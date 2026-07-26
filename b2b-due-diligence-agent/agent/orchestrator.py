"""
B2B Due Diligence Verification Agent — Production Orchestrator v5.0

Stage 1 — Input Validation      → LLM (pure logic, hard-fail on errors)
Stage 2 — Data Collection       → Web Scraper + Neural Search + Google Search
Stage 3 — Cross-Verification    → Neural Search + LLM
Stage 4 — Risk Detection        → Neural Search + Web Scraper + LLM
Stage 5 — Trust Scoring         → Neural Search + LLM (sub-score breakdown)
Stage 6 — Evidence Aggregation  → Neural Search + LLM
Stage 7 — Final Assessment      → LLM (pure synthesis, no new data)

Production features:
- Per-LLM-call retry with exponential backoff
- Per-stage error isolation — pipeline continues on partial failure
- Score bounds validation post-LLM with weighted formula enforcement
- Hard verdict override rules — LLM arithmetic cannot override policy
- Input sanitisation — control chars, length limits, injection blocking
- Full cost + token tracking per LLM call and tool call
- Centralised logging to file + console
- Stage callback for real-time UI progress
"""

import copy
import json
import os
import re
import sys
import io as _io
import time
from datetime import datetime
from typing import Callable, Optional

import anthropic as _anthropic
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from agent.tools import ExaSearch, ApifyScraper
from agent.config import (
    LLM_PROVIDER, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE,
    LLM_RETRY_ATTEMPTS, LLM_RETRY_BACKOFF, LLM_FALLBACK_ENABLED,
    ANTHROPIC_MODEL, OPENAI_MODEL,
    TRUNCATE_CHARS_DEFAULT, TRUNCATE_CHARS_S7,
    COMPANY_SCORE_WEIGHT, DM_SCORE_WEIGHT,
    PROCEED_MIN_SCORE, REJECT_MAX_SCORE, PROCEED_MIN_CONF,
)
from agent.logger import get_logger
from agent.cost_tracker import CostTracker
from agent.langfuse_tracer import LangfuseTracer

logger = get_logger("orchestrator")


class _LLMState:
    """Tracks which provider/model is currently active for this pipeline run.
    Mutated in place when _llm() falls back, so every later stage call
    picks up the switch automatically."""
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model


def _model_for(provider: str) -> str:
    return ANTHROPIC_MODEL if provider == "anthropic" else OPENAI_MODEL


def _other_provider(provider: str) -> str:
    return "openai" if provider == "anthropic" else "anthropic"


# ── Console ───────────────────────────────────────────────────────────────────

def _make_console() -> Console:
    if "streamlit" in sys.modules:
        return Console(file=_io.StringIO(), highlight=False)
    return Console(legacy_windows=False)

console = _make_console()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _domain_from(website: str) -> str:
    return website.replace("https://", "").replace("http://", "").split("/")[0].strip()


def _truncate(data: dict, max_chars: int = 6000) -> str:
    """Smart truncation that trims lists before doing a hard cut."""
    def _trim_lists(obj, max_items=3):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, list) and len(v) > max_items:
                    obj[k] = v[:max_items] + [f"... ({len(v)-max_items} more)"]
                elif isinstance(v, (dict, list)):
                    _trim_lists(v)
        elif isinstance(obj, list):
            for item in obj:
                _trim_lists(item)

    trimmed = copy.deepcopy(data)
    raw = json.dumps(trimmed, indent=2, default=str)
    if len(raw) <= max_chars:
        return raw
    _trim_lists(trimmed)
    raw = json.dumps(trimmed, indent=2, default=str)
    if len(raw) <= max_chars:
        return raw
    return raw[:max_chars] + "\n... [hard truncated]"


def _stage(label: str, status: str = "running", detail: str = ""):
    icons = {
        "running": "[yellow]>>>[/yellow]",
        "done":    "[bright_green]OK [/bright_green]",
        "skip":    "[dim]---[/dim]",
        "fail":    "[red]ERR[/red]",
    }
    detail_str = f"  ({detail})" if detail else ""
    console.print(f"  {icons.get(status, '   ')} {label}{detail_str}")


def _sanitise_input(data: dict) -> dict:
    """Strip control chars, enforce field length limits, block prompt injection."""
    MAX_LENGTHS = {
        "company_name": 200,
        "company_website": 500,
        "company_location": 200,
        "decision_maker_name": 200,
        "decision_maker_job_title": 200,
        "decision_maker_linkedin_url": 500,
        "decision_maker_email": 200,
    }
    INJECTION_PATTERNS = [
        "ignore all previous", "ignore prior", "disregard",
        "system prompt", "jailbreak", "forget your instructions",
    ]
    clean = {}
    for k, v in data.items():
        if isinstance(v, str):
            v = v.strip()
            v = v[:MAX_LENGTHS.get(k, 300)]
            v = re.sub(r"[\x00-\x1f\x7f]", "", v)
            v_lower = v.lower()
            for pattern in INJECTION_PATTERNS:
                if pattern in v_lower:
                    v = "[REDACTED — policy violation]"
                    break
        clean[k] = v
    return clean


def _validate_scores(s5: dict) -> dict:
    for key in ("company_score", "decision_maker_score", "overall_score"):
        try:
            s5[key] = max(0, min(100, float(s5.get(key, 0))))
        except (TypeError, ValueError):
            s5[key] = 0
    cs = s5.get("company_score", 0)
    dm = s5.get("decision_maker_score", 0)
    s5["overall_score"] = round(
        (cs * COMPANY_SCORE_WEIGHT) + (dm * DM_SCORE_WEIGHT), 1
    )
    return s5


def _enforce_verdict_rules(s7: dict, s4: dict, s5: dict) -> dict:
    """Override LLM verdict if it violates hard decision rules."""
    score     = float(s5.get("overall_score", 0))
    red_flags = s4.get("red_flags", [])
    yellows   = s4.get("yellow_flags", [])
    original  = s7.get("recommendation", "CAUTION")
    override  = None

    if red_flags or score < REJECT_MAX_SCORE:
        if original != "REJECT":
            override = f"Forced REJECT: red_flags={len(red_flags)} score={score}"
            s7["recommendation"] = "REJECT"
    elif score < PROCEED_MIN_SCORE or yellows:
        if original == "PROCEED":
            override = f"Forced CAUTION: score={score} yellow_flags={len(yellows)}"
            s7["recommendation"] = "CAUTION"

    if override:
        s7["_rule_override"] = override
        logger.warning(f"Verdict override | {override} | original={original}")

    return s7


def _default(stage: str) -> dict:
    """Safe fallback result when a stage fails."""
    defaults = {
        "s3": {"matches": [], "mismatches": [], "unverifiable": ["Cross-verification unavailable — data gap"]},
        "s4": {"red_flags": [], "yellow_flags": ["Risk analysis unavailable — treat as unverified"], "green_signals": []},
        "s5": {"company_score": 0, "company_score_rationale": "Scoring failed", "company_sub_scores": {},
               "decision_maker_score": 0, "decision_maker_score_rationale": "Scoring failed", "dm_sub_scores": {},
               "overall_score": 0},
        "s6": {"supporting_evidence": [], "contradicting_signals": [], "neutral_observations": ["Evidence aggregation unavailable"]},
        "s7": {"recommendation": "CAUTION", "confidence": "LOW", "confidence_percentage": 0,
               "primary_reason": "Pipeline completed with errors — manual review required",
               "action_items": ["Conduct manual due diligence", "Re-run agent with complete data"],
               "summary": "Analysis could not be fully completed. Manual review is required."},
    }
    return defaults.get(stage, {})


# ── Stage system prompts ──────────────────────────────────────────────────────

_TOOL_NAME_RULE = """
CRITICAL OUTPUT RULE: Never mention tool names, data vendor names, or AI
provider names in your output. Do not write "Exa", "Apify", "OpenAI",
"GPT-4o", "Claude", "Anthropic", "neural search", "web scraping tool",
"LLM", or any internal system name. Write as a human analyst: use "web
search results", "company website", "professional profile", "online
records", "public sources", "search results", "intelligence gathered".
Every finding must read as if a human researcher discovered it.
"""

_S1_SYSTEM = """You are a strict input validator for a B2B due diligence pipeline.
Perform pure logic checks — no external lookups needed.

Validate:
- company_name: non-empty string
- company_website: valid http/https URL, proper domain structure
- company_location: non-empty string
- decision_maker_name: non-empty, looks like a real full name (first + last name)
- decision_maker_job_title: non-empty string
- decision_maker_linkedin_url: must contain linkedin.com/in/
- decision_maker_email: OPTIONAL field. If present, must be valid email format;
  flag if domain differs from company website domain. If missing or empty,
  this is NOT an error — add a warning only, never an error.

Only company_name and decision_maker_name are strictly required. All other
fields, if missing or empty, should produce a warning (not an error).

Return ONLY valid JSON:
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "field_checks": {
    "company_name": "ok",
    "company_website": "ok",
    "company_location": "ok",
    "decision_maker_name": "ok",
    "decision_maker_job_title": "ok",
    "decision_maker_linkedin_url": "ok",
    "decision_maker_email": "ok"
  }
}"""

_S3_SYSTEM = """You are a cross-verification specialist for B2B due diligence.
You receive input data plus web intelligence results.

Cross-check all provided fields against what was found online:
- Company name vs domain vs web search results
- Email domain vs website domain alignment
- Decision maker name — does web intelligence confirm this person at this company?
- Job title — is this title confirmed at this company?
- Location — is the region mentioned consistently?

Return ONLY valid JSON:
{
  "matches": ["specific verified fact with source URL"],
  "mismatches": ["specific mismatch with detail"],
  "unverifiable": ["field that could not be confirmed"]
}
""" + _TOOL_NAME_RULE

_S4_SYSTEM = """You are a risk detection specialist for B2B due diligence.
You receive web intelligence, website content, and professional profile data.

Classify all signals:
- red_flags: fraud, scam, legal actions, fake profiles, domain spoofing, suspicious patterns
- yellow_flags: limited data, inconsistencies, recently registered domain, no verifiable history, unverified claims
- green_signals: established brand, professional website, verified presence, consistent identity, good reputation

For each flag, describe the observation clearly without referencing data source tool names.
Use plain language like "company website", "web search results", "professional profile", "online presence".

Return ONLY valid JSON:
{
  "red_flags": ["clear description of risk"],
  "yellow_flags": ["clear description of concern"],
  "green_signals": ["clear description of positive signal"]
}
""" + _TOOL_NAME_RULE

_S5_SYSTEM = """You are a trust scoring specialist for B2B due diligence.
You receive web intelligence data plus all prior stage outputs.

Score company (0–100) and decision maker (0–100) with sub-score breakdown for auditability.

Company sub-scores (each 0–100):
- domain_credibility: domain age signals, SSL, infrastructure quality
- web_presence_depth: brand recognition, search result depth, consistency
- news_and_reputation: press coverage, awards, partnerships, public mentions
- identity_consistency: name/domain/location consistency across all sources

Decision maker sub-scores (each 0–100):
- profile_verification: confirmed name + role at this company in web results
- linkedin_data_quality: profile completeness and professional depth
- email_domain_alignment: email domain matches company website domain
- public_professional_presence: public credibility, mentions, career history

Company score = average of company sub-scores
DM score = average of DM sub-scores
overall_score = (company_score * 0.6) + (decision_maker_score * 0.4)

Return ONLY valid JSON:
{
  "company_score": 0,
  "company_score_rationale": "2-3 sentence rationale citing specific findings",
  "company_sub_scores": {
    "domain_credibility": 0,
    "web_presence_depth": 0,
    "news_and_reputation": 0,
    "identity_consistency": 0
  },
  "decision_maker_score": 0,
  "decision_maker_score_rationale": "2-3 sentence rationale citing specific findings",
  "dm_sub_scores": {
    "profile_verification": 0,
    "linkedin_data_quality": 0,
    "email_domain_alignment": 0,
    "public_professional_presence": 0
  },
  "overall_score": 0
}
""" + _TOOL_NAME_RULE

_S6_SYSTEM = """You are an evidence aggregation specialist for B2B due diligence.
You receive web search results plus all prior stage outputs.

Synthesise findings into three lists. Write each item as a clear, factual observation.
Do NOT mention data tool names — write as if you found this information through research.

- supporting_evidence: concrete positive signals with source URLs where available
- contradicting_signals: anything undermining trust or contradicting provided information
- neutral_observations: factual context that is neither positive nor negative

Return ONLY valid JSON:
{
  "supporting_evidence": ["factual observation — source: URL if available"],
  "contradicting_signals": [],
  "neutral_observations": ["factual observation"]
}
""" + _TOOL_NAME_RULE

_S7_SYSTEM = """You are the final assessment specialist for B2B due diligence.
You receive complete outputs from all prior stages. No new data — pure synthesis.

Decision rules:
- PROCEED: overall_score >= 70 AND no red flags AND confidence >= 75%
- CAUTION: overall_score 40–69 OR yellow flags present OR data gaps
- REJECT: overall_score < 40 OR any red flags present

Confidence calibration:
- HIGH (>=80%): strong data coverage, consistent signals across all sources
- MEDIUM (50–79%): moderate data, some gaps or inconsistencies
- LOW (<50%): significant data gaps, conflicting signals, or failed stages

Return ONLY valid JSON:
{
  "recommendation": "PROCEED",
  "confidence": "HIGH",
  "confidence_percentage": 85,
  "primary_reason": "one clear sentence explaining the verdict",
  "action_items": ["specific actionable next step 1", "specific actionable next step 2"],
  "summary": "4–5 sentence executive paragraph synthesising all findings, risks, and opportunities."
}
""" + _TOOL_NAME_RULE


# ── LLM with retry + cost tracking ───────────────────────────────────────────

def _llm(clients: dict, llm_state: _LLMState, system: str, user: str, label: str, stage: str,
         cost_tracker: CostTracker, telemetry: dict = None, trace=None,
         _is_fallback_attempt: bool = False) -> dict:
    """LLM call with retry, exponential backoff, cost tracking, and telemetry.

    Supports Anthropic and OpenAI. If every retry against the active provider
    (`llm_state.provider`) fails and LLM_FALLBACK_ENABLED is set, automatically
    retries once on the other provider (if its key is configured) and — on
    success — permanently switches `llm_state` so later stages use it too.
    """
    provider = llm_state.provider
    model    = llm_state.model
    client   = clients.get(provider)

    raw = ""
    start = time.time()
    last_error = None
    generation = (
        trace.generation(name=label, model=model, input=user, metadata={"stage": stage, "provider": provider})
        if trace is not None else None
    )

    for attempt in range(LLM_RETRY_ATTEMPTS):
        try:
            if provider == "anthropic":
                resp = client.messages.create(
                    model=model,
                    max_tokens=LLM_MAX_TOKENS,
                    temperature=LLM_TEMPERATURE,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                raw   = resp.content[0].text.strip()
                prompt_tokens     = resp.usage.input_tokens if resp.usage else 0
                completion_tokens = resp.usage.output_tokens if resp.usage else 0
                model_used        = resp.model
            else:
                resp = client.chat.completions.create(
                    model=model,
                    max_tokens=LLM_MAX_TOKENS,
                    temperature=LLM_TEMPERATURE,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                )
                raw   = resp.choices[0].message.content.strip()
                prompt_tokens     = resp.usage.prompt_tokens if resp.usage else 0
                completion_tokens = resp.usage.completion_tokens if resp.usage else 0
                model_used        = resp.model

            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)

            duration = time.time() - start

            cost_tracker.record_llm(
                label=label,
                stage=stage,
                model=model_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                duration_s=duration,
                attempt=attempt + 1,
                status="success",
            )

            logger.debug(
                f"LLM OK | {label} | provider={provider} | tokens={prompt_tokens}+{completion_tokens} "
                f"| attempt={attempt+1} | {round(duration,2)}s"
            )

            if telemetry is not None:
                telemetry["total_tokens"] += (prompt_tokens + completion_tokens)
                telemetry["llm_calls"].append({
                    "label": label, "attempts": attempt + 1,
                    "duration_s": round(duration, 2),
                    "status": "success",
                    "tokens": prompt_tokens + completion_tokens,
                    "provider": provider,
                })
                if attempt > 0:
                    telemetry["retry_count"] += attempt

            if generation is not None:
                generation.end(
                    output=result,
                    usage={"input": prompt_tokens, "output": completion_tokens, "unit": "TOKENS"},
                )

            return result

        except json.JSONDecodeError as exc:
            os.makedirs("logs", exist_ok=True)
            with open("logs/last_raw_response.txt", "w", encoding="utf-8") as f:
                f.write(raw)
            last_error = RuntimeError(f"{label} — invalid JSON: {exc} | Preview: {raw[:200]}")
            logger.warning(f"LLM JSON parse failed | {label} | attempt={attempt+1} | {str(exc)[:100]}")

        except Exception as exc:
            last_error = exc
            logger.warning(f"LLM API error | {label} | provider={provider} | attempt={attempt+1} | {str(exc)[:100]}")

        if attempt < LLM_RETRY_ATTEMPTS - 1:
            time.sleep(LLM_RETRY_BACKOFF ** attempt)

    cost_tracker.record_llm(
        label=label,
        stage=stage,
        model=model,
        prompt_tokens=0,
        completion_tokens=0,
        duration_s=round(time.time() - start, 2),
        attempt=LLM_RETRY_ATTEMPTS,
        status="failed",
        error=str(last_error)[:300],
    )
    logger.error(f"LLM FAILED after {LLM_RETRY_ATTEMPTS} attempts | provider={provider} | {label} | {str(last_error)[:200]}")

    if generation is not None:
        generation.end(output=None, level="ERROR", status_message=str(last_error)[:300])

    # ── Automatic provider fallback ──────────────────────────────────────────
    fallback_provider = _other_provider(provider)
    if not _is_fallback_attempt and LLM_FALLBACK_ENABLED and clients.get(fallback_provider) is not None:
        logger.warning(f"Provider fallback engaged | {label} | {provider} -> {fallback_provider}")
        if telemetry is not None:
            telemetry.setdefault("provider_fallbacks", []).append({
                "label": label, "from": provider, "to": fallback_provider,
                "reason": str(last_error)[:200],
            })
        llm_state.provider = fallback_provider
        llm_state.model    = _model_for(fallback_provider)
        return _llm(clients, llm_state, system, user, label, stage, cost_tracker,
                    telemetry=telemetry, trace=trace, _is_fallback_attempt=True)

    if telemetry is not None:
        telemetry["llm_calls"].append({
            "label": label, "attempts": LLM_RETRY_ATTEMPTS,
            "duration_s": round(time.time() - start, 2),
            "status": "failed", "error": str(last_error)[:200],
            "provider": provider,
        })
        telemetry["errors"].append(f"{label}: {str(last_error)[:200]}")

    raise last_error


def _stage_run(label: str, fn, stage_key: str, telemetry: dict, default_key: str = None):
    """Run a stage function with error isolation, timing, and telemetry."""
    start = time.time()
    try:
        result = fn()
        telemetry["stages"][stage_key] = {
            "status": "success",
            "duration_s": round(time.time() - start, 2),
        }
        return result
    except Exception as exc:
        err = str(exc)[:300]
        telemetry["stages"][stage_key] = {
            "status": "failed",
            "duration_s": round(time.time() - start, 2),
            "error": err,
        }
        telemetry["errors"].append(f"{stage_key}: {err}")
        _stage(label, "fail", err[:80])
        logger.error(f"Stage {stage_key} FAILED | error={err}")
        return _default(default_key) if default_key else {}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def _check_keys() -> dict:
    """Validate required API keys at startup. Requires at least one of
    ANTHROPIC_API_KEY / OPENAI_API_KEY — the other is optional and, when
    present, enables automatic mid-run fallback if the primary provider fails."""
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key    = os.environ.get("OPENAI_API_KEY", "")
    primary_key   = anthropic_key if LLM_PROVIDER == "anthropic" else openai_key
    fallback_key  = openai_key if LLM_PROVIDER == "anthropic" else anthropic_key

    if not primary_key and not fallback_key:
        console.print("\n[red]  No LLM API key set — cannot run pipeline.[/red]")
        console.print("[dim]  Add ANTHROPIC_API_KEY or OPENAI_API_KEY to your .env file.[/dim]\n")
        sys.exit(1)

    if not primary_key:
        primary_name, fallback_name = (
            ("ANTHROPIC_API_KEY", "OPENAI_API_KEY") if LLM_PROVIDER == "anthropic"
            else ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
        )
        console.print(
            f"[yellow]  Warning: {primary_name} not set — starting on the fallback "
            f"provider ({fallback_name}) instead[/yellow]"
        )
    elif fallback_key and not LLM_FALLBACK_ENABLED:
        pass
    elif not fallback_key:
        console.print("[dim]  No fallback LLM key configured — a primary-provider outage will fail the run.[/dim]")

    missing_optional = []
    for key, label in [("EXA_API_KEY", "Web Search"), ("APIFY_API_KEY", "Web Scraping")]:
        if not os.environ.get(key, ""):
            missing_optional.append(f"{label} ({key})")
    if missing_optional:
        console.print(f"[yellow]  Warning: optional keys not set — reduced coverage: {', '.join(missing_optional)}[/yellow]")

    return {
        "anthropic": anthropic_key,
        "openai":    openai_key,
        "exa":       os.environ.get("EXA_API_KEY", ""),
        "apify":     os.environ.get("APIFY_API_KEY", ""),
    }


def run_pipeline(
    input_data: dict,
    api_key: str,
    save_report: bool = True,
    stage_callback: Callable[[int], None] = None,
) -> Optional[dict]:
    """Run the full 7-stage due diligence pipeline with cost tracking."""

    # ── Sanitise input first ──────────────────────────────────────────────────
    input_data = _sanitise_input(input_data)

    keys  = _check_keys()
    exa   = ExaSearch(keys["exa"])       if keys["exa"]   else None
    apify = ApifyScraper(keys["apify"])  if keys["apify"] else None

    # Build both provider clients (whichever keys are present) so _llm() can
    # fall back mid-run without needing to re-authenticate. Ignores the raw
    # `api_key` argument — callers (main.py, app.py) may pass either
    # ANTHROPIC_API_KEY or OPENAI_API_KEY regardless of LLM_PROVIDER, and the
    # keys resolved by _check_keys() are the authoritative source.
    clients = {
        "anthropic": _anthropic.Anthropic(api_key=keys["anthropic"]) if keys["anthropic"] else None,
        "openai":    OpenAI(api_key=keys["openai"]) if keys["openai"] else None,
    }
    initial_provider = LLM_PROVIDER if clients.get(LLM_PROVIDER) is not None else _other_provider(LLM_PROVIDER)
    llm_state = _LLMState(initial_provider, _model_for(initial_provider))

    company = input_data.get("company_name", "Unknown")
    website = input_data.get("company_website", "")
    domain  = _domain_from(website) if website else ""
    person  = input_data.get("decision_maker_name", "")
    title   = input_data.get("decision_maker_job_title", "")
    linkedin = input_data.get("decision_maker_linkedin_url", "")

    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug    = re.sub(r"[^\w\-]", "_", company.lower()).strip("_")[:20]
    run_id  = f"{slug.upper()}_{ts}"

    cost_tracker = CostTracker(run_id=run_id)

    tracer = LangfuseTracer()
    trace = tracer.trace(
        name="b2b-due-diligence",
        id=run_id,
        input=input_data,
        metadata={"company": company, "llm_model": llm_state.model, "llm_provider": llm_state.provider},
    )

    logger.info(f"Pipeline started | run_id={run_id} | company={company}")

    # ── Telemetry init ────────────────────────────────────────────────────────
    telemetry = {
        "run_id":          run_id,
        "pipeline_start":  time.time(),
        "pipeline_end":    None,
        "total_duration_s": None,
        "stages":          {},
        "llm_calls":       [],
        "data_coverage":   {
            "web_company_intel":  0,
            "web_person_intel":   0,
            "web_domain_check":   0,
            "web_risk_signals":   0,
            "web_evidence":       0,
            "profile_scrape":     0,
            "website_crawl":      0,
            "google_search":      0,
        },
        "retry_count":   0,
        "total_tokens":  0,
        "errors":        [],
        "data_sources":  {
            "web_search":   bool(exa),
            "web_scraping": bool(apify),
            "google_search": bool(apify),
            "llm_analysis": True,
        },
    }

    enrichment = {}

    # ── Banner ────────────────────────────────────────────────────────────────
    console.print()
    console.print(Panel.fit(
        "[bold white]B2B DUE DILIGENCE VERIFICATION AGENT[/bold white]\n"
        "[dim]7-Stage Autonomous Intelligence Pipeline  v5.0[/dim]",
        border_style="dim white", padding=(1, 4),
    ))
    console.print()
    console.print(f"  Target  : [bold]{company}[/bold]  {website}")
    console.print(f"  Contact : {person}  |  {title}")
    console.print(f"  Run ID  : [dim]{run_id}[/dim]")
    console.print()
    console.print("-" * 60)

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 1 — Input Validation
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(1)
    logger.debug(f"Stage 1 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 1[/bold] — Input Validation")
    _stage("Validating fields, URL patterns, email-domain alignment", "running")
    s1_start = time.time()

    s1 = _llm(clients, llm_state, _S1_SYSTEM,
               f"Validate:\n{json.dumps(input_data, indent=2)}", "Stage 1 — Validation",
               "stage_1", cost_tracker, telemetry, trace=trace)

    telemetry["stages"]["stage_1"] = {
        "status": "success" if not s1.get("errors") else "failed",
        "duration_s": round(time.time() - s1_start, 2),
        "warnings": s1.get("warnings", []),
    }

    if s1.get("errors"):
        _stage("Field validation", "fail", " | ".join(s1["errors"]))
        raise ValueError(f"Stage 1 validation failed: {'; '.join(s1['errors'])}")

    _stage("Field validation", "done",
           "all fields valid" if not s1.get("warnings") else f"{len(s1.get('warnings', []))} warning(s)")
    logger.debug(f"Stage 1 done | duration={round(time.time()-s1_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 2 — Data Collection
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(2)
    logger.debug(f"Stage 2 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 2[/bold] — Data Collection")
    s2_start = time.time()
    s2_errors = []

    # Professional profile scrape
    if apify and linkedin:
        _stage("Professional profile scrape", "running")
        _t = time.time()
        apify_li = apify.scrape_linkedin_profile(linkedin)
        ok = apify_li.get("status") == "success"
        cnt = len(apify_li.get("items", []))
        telemetry["data_coverage"]["profile_scrape"] = cnt
        cost_tracker.record_tool(
            tool="apify", method="scrape_linkedin_profile", stage="stage_2",
            input_summary=f"LinkedIn: {linkedin[:80]}",
            results_count=cnt, duration_s=time.time() - _t,
            status="success" if ok else "failed",
            error=apify_li.get("error", "")[:200] if not ok else None,
        )
        logger.debug(f"Tool call | tool=apify | method=scrape_linkedin_profile | input={linkedin[:60]}")
        _stage("Professional profile scrape", "done" if ok else "fail",
               f"{cnt} items" if ok else apify_li.get("error", "")[:80])
        if not ok:
            s2_errors.append("profile_scrape")
        enrichment.setdefault("apify", {})["linkedin_profile"] = apify_li
    elif apify:
        cost_tracker.record_tool(tool="apify", method="scrape_linkedin_profile",
            stage="stage_2", input_summary="skipped — no LinkedIn URL", status="skipped")
    else:
        cost_tracker.record_tool(tool="apify", method="scrape_linkedin_profile",
            stage="stage_2", input_summary="skipped — no API key", status="skipped")

    # Company website crawl
    if apify and website:
        _stage("Company website crawl", "running")
        _t = time.time()
        apify_web = apify.scrape_website(website)
        ok = apify_web.get("status") == "success"
        cnt = len(apify_web.get("items", []))
        telemetry["data_coverage"]["website_crawl"] = cnt
        cost_tracker.record_tool(
            tool="apify", method="scrape_website", stage="stage_2",
            input_summary=f"website: {website[:80]}",
            results_count=cnt, duration_s=time.time() - _t,
            status="success" if ok else "failed",
            error=apify_web.get("error", "")[:200] if not ok else None,
        )
        logger.debug(f"Tool call | tool=apify | method=scrape_website | input={website[:60]}")
        _stage("Company website crawl", "done" if ok else "fail",
               f"{cnt} pages" if ok else apify_web.get("error", "")[:80])
        if not ok:
            s2_errors.append("website_crawl")
        enrichment.setdefault("apify", {})["website"] = apify_web
    elif apify:
        cost_tracker.record_tool(tool="apify", method="scrape_website",
            stage="stage_2", input_summary="skipped — no website", status="skipped")

    # Google search
    if apify and company:
        _stage("Google search — company background", "running")
        _t = time.time()
        try:
            google_res = apify.google_search(
                f'"{company}" review reputation background site:linkedin.com OR site:crunchbase.com OR news',
            )
            ok = google_res.get("status") == "success"
            cnt = len(google_res.get("items", []))
            telemetry["data_coverage"]["google_search"] = cnt
            cost_tracker.record_tool(
                tool="apify", method="google_search", stage="stage_2",
                input_summary=f"company={company}",
                results_count=cnt, duration_s=time.time() - _t,
                status="success" if ok else "failed",
                error=google_res.get("error", "")[:200] if not ok else None,
            )
            logger.debug(f"Tool call | tool=apify | method=google_search | input={company[:60]}")
            _stage("Google search — company background", "done" if ok else "fail",
                   f"{cnt} results" if ok else google_res.get("error", "")[:60])
            enrichment.setdefault("apify", {})["google_search"] = google_res
        except Exception as e:
            cost_tracker.record_tool(tool="apify", method="google_search",
                stage="stage_2", input_summary=f"company={company}",
                duration_s=time.time() - _t, status="failed", error=str(e)[:200])
            _stage("Google search — company background", "fail", str(e)[:60])
            s2_errors.append("google_search")

    if not apify:
        _stage("Web scraping + Google search", "skip", "no scraping key configured")

    # Exa — company intelligence
    if exa:
        _stage("Web intelligence — company", "running")
        _t = time.time()
        exa_co = exa.search_company_intel(company, domain or None)
        cnt = len(exa_co.get("results", []))
        telemetry["data_coverage"]["web_company_intel"] = cnt
        cost_tracker.record_tool(
            tool="exa", method="search_company_intel", stage="stage_2",
            input_summary=f"company={company} domain={domain}",
            results_count=cnt, duration_s=time.time() - _t,
            status="success" if "error" not in exa_co else "failed",
            error=exa_co.get("error", "")[:200] if "error" in exa_co else None,
        )
        logger.debug(f"Tool call | tool=exa | method=search_company_intel | input={company[:60]}")
        _stage("Web intelligence — company", "done" if "error" not in exa_co else "fail",
               f"{cnt} results")

        _stage("Web intelligence — decision maker", "running")
        _t = time.time()
        exa_pe = exa.search_person_intel(person, company=company, title=title)
        cnt = len(exa_pe.get("results", []))
        telemetry["data_coverage"]["web_person_intel"] = cnt
        cost_tracker.record_tool(
            tool="exa", method="search_person_intel", stage="stage_2",
            input_summary=f"person={person} company={company}",
            results_count=cnt, duration_s=time.time() - _t,
            status="success" if "error" not in exa_pe else "failed",
            error=exa_pe.get("error", "")[:200] if "error" in exa_pe else None,
        )
        logger.debug(f"Tool call | tool=exa | method=search_person_intel | input={person[:60]}")
        _stage("Web intelligence — decision maker", "done" if "error" not in exa_pe else "fail",
               f"{cnt} results")

        _stage("Domain verification", "running")
        _t = time.time()
        exa_dom = exa.verify_domain(domain) if domain else {}
        cnt = len(exa_dom.get("results", []))
        telemetry["data_coverage"]["web_domain_check"] = cnt
        if domain:
            cost_tracker.record_tool(
                tool="exa", method="verify_domain", stage="stage_2",
                input_summary=f"domain={domain}",
                results_count=cnt, duration_s=time.time() - _t,
                status="success" if "error" not in exa_dom else "failed",
                error=exa_dom.get("error", "")[:200] if "error" in exa_dom else None,
            )
        _stage("Domain verification", "done" if domain else "skip",
               f"{cnt} results" if domain else "no domain")

        enrichment["exa"] = {
            "company_intel": exa_co,
            "person_intel":  exa_pe,
            "domain_check":  exa_dom,
        }
    else:
        _stage("Neural web search", "skip", "no search key configured")
        cost_tracker.record_tool(tool="exa", method="search_company_intel",
            stage="stage_2", input_summary="skipped — no API key", status="skipped")
        cost_tracker.record_tool(tool="exa", method="search_person_intel",
            stage="stage_2", input_summary="skipped — no API key", status="skipped")

    telemetry["stages"]["stage_2"] = {
        "status": "partial" if s2_errors else "success",
        "duration_s": round(time.time() - s2_start, 2),
        "failed_sources": s2_errors,
        "data_coverage": dict(telemetry["data_coverage"]),
    }

    s2 = {
        "company_signals_count": telemetry["data_coverage"]["web_company_intel"],
        "person_signals_count":  telemetry["data_coverage"]["web_person_intel"],
        "website_pages_crawled": telemetry["data_coverage"]["website_crawl"],
        "profile_scraped":       telemetry["data_coverage"]["profile_scrape"],
        "google_results":        telemetry["data_coverage"]["google_search"],
        "sources_active": {
            "exa":   bool(exa),
            "apify": bool(apify),
        },
        "stage_errors": s2_errors,
    }

    logger.debug(f"Stage 2 done | duration={round(time.time()-s2_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 3 — Cross-Verification
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(3)
    logger.debug(f"Stage 3 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 3[/bold] — Cross-Verification")
    _stage("Cross-checking identity against web intelligence", "running")

    s3_ctx = {
        "web_company_intel": enrichment.get("exa", {}).get("company_intel", {}),
        "web_person_intel":  enrichment.get("exa", {}).get("person_intel", {}),
        "web_domain_check":  enrichment.get("exa", {}).get("domain_check", {}),
        "google_results":    enrichment.get("apify", {}).get("google_search", {}),
    }

    def _run_s3():
        return _llm(clients, llm_state, _S3_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nWEB INTELLIGENCE:\n{_truncate(s3_ctx)}",
                    "Stage 3 — Cross-Verification", "stage_3", cost_tracker, telemetry, trace=trace)

    s3_start = time.time()
    s3 = _stage_run("Cross-verification", _run_s3, "stage_3", telemetry, "s3")
    _stage("Cross-verification", "done",
           f"{len(s3.get('matches',[]))} matches, {len(s3.get('mismatches',[]))} mismatches")
    logger.debug(f"Stage 3 done | duration={round(time.time()-s3_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 4 — Risk Detection
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(4)
    logger.debug(f"Stage 4 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 4[/bold] — Risk Detection")

    if exa:
        _stage("Web risk signal search", "running")
        _t = time.time()
        try:
            exa_risk = exa.search_risk_signals(company, person)
            enrichment["exa"]["risk_signals"] = exa_risk
            cnt = len(exa_risk.get("results", []))
            telemetry["data_coverage"]["web_risk_signals"] = cnt
            cost_tracker.record_tool(
                tool="exa", method="search_risk_signals", stage="stage_4",
                input_summary=f"company={company} person={person}",
                results_count=cnt, duration_s=time.time() - _t,
                status="success" if "error" not in exa_risk else "failed",
                error=exa_risk.get("error", "")[:200] if "error" in exa_risk else None,
            )
            logger.debug(f"Tool call | tool=exa | method=search_risk_signals | input={company[:60]}")
            _stage("Web risk signal search", "done" if "error" not in exa_risk else "fail",
                   f"{cnt} results")
        except Exception as e:
            cost_tracker.record_tool(tool="exa", method="search_risk_signals",
                stage="stage_4", input_summary=f"company={company}",
                duration_s=time.time() - _t, status="failed", error=str(e)[:200])
            _stage("Web risk signal search", "fail", str(e)[:60])

    _stage("Risk classification", "running")

    s4_ctx = {
        "risk_signals":    enrichment.get("exa", {}).get("risk_signals", {}),
        "company_intel":   enrichment.get("exa", {}).get("company_intel", {}),
        "website_content": enrichment.get("apify", {}).get("website", {}),
        "profile_content": enrichment.get("apify", {}).get("linkedin_profile", {}),
        "google_results":  enrichment.get("apify", {}).get("google_search", {}),
    }

    def _run_s4():
        return _llm(clients, llm_state, _S4_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE DATA:\n{_truncate(s4_ctx)}",
                    "Stage 4 — Risk Detection", "stage_4", cost_tracker, telemetry, trace=trace)

    s4_start = time.time()
    s4 = _stage_run("Risk classification", _run_s4, "stage_4", telemetry, "s4")
    _stage("Risk classification", "done",
           f"{len(s4.get('red_flags',[]))} red  {len(s4.get('yellow_flags',[]))} yellow  {len(s4.get('green_signals',[]))} green")
    logger.debug(f"Stage 4 done | duration={round(time.time()-s4_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 5 — Trust Scoring
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(5)
    logger.debug(f"Stage 5 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 5[/bold] — Trust Scoring")
    _stage("Generating scored trust assessment with sub-score breakdown", "running")

    s5_ctx = {
        "company_intel":   enrichment.get("exa", {}).get("company_intel", {}),
        "person_intel":    enrichment.get("exa", {}).get("person_intel", {}),
        "website_content": enrichment.get("apify", {}).get("website", {}),
        "profile_content": enrichment.get("apify", {}).get("linkedin_profile", {}),
        "google_results":  enrichment.get("apify", {}).get("google_search", {}),
        "cross_verification": s3,
        "risk_detection":     s4,
    }

    def _run_s5():
        raw = _llm(clients, llm_state, _S5_SYSTEM,
                   f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE + PRIOR STAGES:\n{_truncate(s5_ctx)}",
                   "Stage 5 — Trust Scoring", "stage_5", cost_tracker, telemetry, trace=trace)
        return _validate_scores(raw)

    s5_start = time.time()
    s5 = _stage_run("Trust scoring", _run_s5, "stage_5", telemetry, "s5")
    co, dm, ov = s5.get("company_score", 0), s5.get("decision_maker_score", 0), s5.get("overall_score", 0)
    _stage("Trust scoring", "done", f"company {co}/100  ·  DM {dm}/100  ·  overall {ov}/100")
    logger.debug(f"Stage 5 done | duration={round(time.time()-s5_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 6 — Evidence Aggregation
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(6)
    logger.debug(f"Stage 6 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 6[/bold] — Evidence Aggregation")

    if exa:
        _stage("Evidence & corroboration search", "running")
        _t = time.time()
        try:
            exa_ev = exa.search_evidence(company, domain or None)
            enrichment["exa"]["evidence_search"] = exa_ev
            cnt = len(exa_ev.get("results", []))
            telemetry["data_coverage"]["web_evidence"] = cnt
            cost_tracker.record_tool(
                tool="exa", method="search_evidence", stage="stage_6",
                input_summary=f"company={company} domain={domain}",
                results_count=cnt, duration_s=time.time() - _t,
                status="success" if "error" not in exa_ev else "failed",
                error=exa_ev.get("error", "")[:200] if "error" in exa_ev else None,
            )
            logger.debug(f"Tool call | tool=exa | method=search_evidence | input={company[:60]}")
            _stage("Evidence & corroboration search", "done" if "error" not in exa_ev else "fail",
                   f"{cnt} results")
        except Exception as e:
            cost_tracker.record_tool(tool="exa", method="search_evidence",
                stage="stage_6", input_summary=f"company={company}",
                duration_s=time.time() - _t, status="failed", error=str(e)[:200])
            _stage("Evidence & corroboration search", "fail", str(e)[:60])

    _stage("Evidence aggregation and synthesis", "running")

    s6_ctx = {
        "evidence_search": enrichment.get("exa", {}).get("evidence_search", {}),
        "company_intel":   enrichment.get("exa", {}).get("company_intel", {}),
        "person_intel":    enrichment.get("exa", {}).get("person_intel", {}),
        "google_results":  enrichment.get("apify", {}).get("google_search", {}),
        "cross_verification": s3,
        "risk_detection":     s4,
        "trust_scoring":      s5,
    }

    def _run_s6():
        return _llm(clients, llm_state, _S6_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE + PRIOR STAGES:\n{_truncate(s6_ctx)}",
                    "Stage 6 — Evidence Aggregation", "stage_6", cost_tracker, telemetry, trace=trace)

    s6_start = time.time()
    s6 = _stage_run("Evidence aggregation", _run_s6, "stage_6", telemetry, "s6")
    _stage("Evidence aggregation", "done",
           f"{len(s6.get('supporting_evidence',[]))} supporting  ·  {len(s6.get('contradicting_signals',[]))} contradicting")
    logger.debug(f"Stage 6 done | duration={round(time.time()-s6_start,2)}s")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 7 — Final Assessment
    # ──────────────────────────────────────────────────────────────────────────
    if stage_callback:
        stage_callback(7)
    logger.debug(f"Stage 7 starting | run_id={run_id}")
    console.print()
    console.print("  [bold]STAGE 7[/bold] — Final Assessment")
    _stage("Synthesising all stages — PROCEED / CAUTION / REJECT", "running")

    s7_ctx = {
        "stage_1_validation":    s1,
        "stage_3_cross_verify":  s3,
        "stage_4_risk":          s4,
        "stage_5_trust_scores":  s5,
        "stage_6_evidence":      s6,
        "pipeline_errors":       telemetry["errors"],
    }

    def _run_s7():
        return _llm(clients, llm_state, _S7_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nALL STAGE OUTPUTS:\n{_truncate(s7_ctx, TRUNCATE_CHARS_S7)}",
                    "Stage 7 — Final Assessment", "stage_7", cost_tracker, telemetry, trace=trace)

    s7_start = time.time()
    s7 = _stage_run("Final assessment", _run_s7, "stage_7", telemetry, "s7")

    # Enforce hard verdict rules
    s7 = _enforce_verdict_rules(s7, s4, s5)

    rec = s7.get("recommendation", "CAUTION")
    col = {"PROCEED": "bright_green", "CAUTION": "yellow", "REJECT": "red"}.get(rec, "white")
    _stage(f"Final verdict — [{col}]{rec}[/{col}]", "done",
           f"{s7.get('confidence','?')}  {s7.get('confidence_percentage',0)}%")
    logger.debug(f"Stage 7 done | duration={round(time.time()-s7_start,2)}s")

    # ── Finalise telemetry ────────────────────────────────────────────────────
    telemetry["pipeline_end"]      = time.time()
    telemetry["total_duration_s"]  = round(telemetry["pipeline_end"] - telemetry["pipeline_start"], 2)
    telemetry["total_llm_calls"]   = len(telemetry["llm_calls"])
    telemetry["stages_succeeded"]  = sum(1 for s in telemetry["stages"].values() if s.get("status") == "success")
    telemetry["stages_failed"]     = sum(1 for s in telemetry["stages"].values() if s.get("status") == "failed")

    logger.info(
        f"Pipeline complete | run_id={run_id} | verdict={rec} "
        f"| duration={telemetry['total_duration_s']}s "
        f"| tokens={telemetry['total_tokens']}"
    )

    # ── Assemble result ───────────────────────────────────────────────────────
    result = {
        "run_id": run_id,
        "stage_results": {
            "input_validation":     s1,
            "data_collection":      s2,
            "cross_verification":   s3,
            "risk_detection":       s4,
            "trust_scoring":        s5,
            "evidence_aggregation": s6,
            "final_assessment":     s7,
        },
        "telemetry": telemetry,
        "cost_tracking": cost_tracker.summary(),
        "metadata": {
            "agent_version":    "5.0",
            "llm_model":        llm_state.model,
            "llm_provider":     llm_state.provider,
            "llm_fell_back":    bool(telemetry.get("provider_fallbacks")),
            "stages_completed": len(telemetry["stages"]),
            "analysis_depth":   "FULL",
            "data_sources":     telemetry["data_sources"],
        },
    }

    # ── Print verdict ─────────────────────────────────────────────────────────
    console.print()
    console.print("-" * 60)
    console.print()
    console.print(f"  VERDICT     : [{col}]{rec}[/{col}]")
    console.print(f"  Confidence  : {s7.get('confidence','?')} ({s7.get('confidence_percentage',0)}%)")
    console.print(f"  Trust Score : {ov}/100  (Company: {co}/100  |  Contact: {dm}/100)")
    console.print(f"  Duration    : {telemetry['total_duration_s']}s  |  LLM Calls: {telemetry['total_llm_calls']}  |  Tokens: {telemetry['total_tokens']}")
    console.print(f"  Cost        : ${cost_tracker.total_cost:.5f} USD  (LLM: ${cost_tracker.total_llm_cost:.5f}  Tools: ${cost_tracker.total_tool_cost:.5f})")
    if telemetry["errors"]:
        console.print(f"  [yellow]  Errors: {len(telemetry['errors'])} stage(s) had issues — see monitor report[/yellow]")
    console.print()

    trace.update(output={"recommendation": rec, "overall_score": ov})
    tracer.flush()

    return result
