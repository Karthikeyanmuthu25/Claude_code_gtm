"""
B2B Due Diligence Verification Agent — Production Orchestrator v4.0

Stage 1 — Input Validation      → LLM (pure logic, hard-fail on errors)
Stage 2 — Data Collection       → Web Scraper + Neural Search + Google Search
Stage 3 — Cross-Verification    → Neural Search + LLM
Stage 4 — Risk Detection        → Neural Search + Web Scraper + LLM
Stage 5 — Trust Scoring         → Neural Search + LLM (sub-score breakdown)
Stage 6 — Evidence Aggregation  → Neural Search + LLM
Stage 7 — Final Assessment      → LLM (pure synthesis, no new data)

Production features:
- Per-LLM-call retry with exponential backoff (3 attempts)
- Per-stage error isolation — pipeline continues on partial failure
- Score bounds validation post-LLM
- Google Search integrated in Stage 2
- Full telemetry collection for monitor report
- Startup key validation with actionable error messages
"""

import json
import os
import sys
import io as _io
import time
from datetime import datetime
from typing import Optional
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from .tools import ExaSearch, ApifyScraper


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
    raw = json.dumps(data, indent=2, default=str)
    return raw[:max_chars] + "\n... [truncated]" if len(raw) > max_chars else raw


def _stage(label: str, status: str = "running", detail: str = ""):
    icons = {
        "running": "[yellow]>>>[/yellow]",
        "done":    "[bright_green]OK [/bright_green]",
        "skip":    "[dim]---[/dim]",
        "fail":    "[red]ERR[/red]",
    }
    detail_str = f"  ({detail})" if detail else ""
    console.print(f"  {icons.get(status, '   ')} {label}{detail_str}")


def _validate_scores(s5: dict) -> dict:
    """Clamp all score fields to 0–100."""
    for key in ("company_score", "decision_maker_score", "overall_score"):
        try:
            s5[key] = max(0, min(100, float(s5.get(key, 0))))
        except (TypeError, ValueError):
            s5[key] = 0
    return s5


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


# ── LLM with retry + telemetry ────────────────────────────────────────────────

def _llm(client: OpenAI, system: str, user: str, label: str, telemetry: dict = None) -> dict:
    """GPT-4o call with 3-attempt retry, exponential backoff, and telemetry tracking."""
    raw = ""
    start = time.time()
    last_error = None

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2500,
                temperature=0,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            raw   = resp.choices[0].message.content.strip()
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)

            if telemetry is not None:
                tokens = resp.usage.total_tokens if resp.usage else 0
                telemetry["llm_calls"].append({
                    "label": label, "attempts": attempt + 1,
                    "duration_s": round(time.time() - start, 2),
                    "status": "success", "tokens": tokens,
                })
                telemetry["total_tokens"] += tokens
                if attempt > 0:
                    telemetry["retry_count"] += attempt
            return result

        except json.JSONDecodeError as exc:
            os.makedirs("logs", exist_ok=True)
            with open("logs/last_raw_response.txt", "w", encoding="utf-8") as f:
                f.write(raw)
            last_error = RuntimeError(f"{label} — invalid JSON: {exc} | Preview: {raw[:200]}")
        except Exception as exc:
            last_error = exc

        if attempt < 2:
            time.sleep(2 ** attempt)

    if telemetry is not None:
        telemetry["llm_calls"].append({
            "label": label, "attempts": 3,
            "duration_s": round(time.time() - start, 2),
            "status": "failed", "error": str(last_error)[:200],
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
        return _default(default_key) if default_key else {}


# ── Stage system prompts ──────────────────────────────────────────────────────

_S1_SYSTEM = """You are a strict input validator for a B2B due diligence pipeline.
Perform pure logic checks — no external lookups needed.

Validate:
- company_name: non-empty string
- company_website: valid http/https URL, proper domain structure
- company_location: non-empty string
- decision_maker_name: non-empty, looks like a real full name (first + last name)
- decision_maker_job_title: non-empty string
- decision_maker_linkedin_url: must contain linkedin.com/in/
- decision_maker_email: valid email format; flag if domain differs from company website domain

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
}"""

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
}"""

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
}"""

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
}"""

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
}"""


# ── Main pipeline ─────────────────────────────────────────────────────────────

def _check_keys() -> dict:
    """Validate required API keys at startup. Returns {key_name: value}."""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        console.print("\n[red]  OPENAI_API_KEY not set — cannot run pipeline.[/red]")
        console.print("[dim]  Add it to your .env file: OPENAI_API_KEY=sk-...[/dim]\n")
        sys.exit(1)

    missing_optional = []
    for key, label in [("EXA_API_KEY", "Web Search"), ("APIFY_API_KEY", "Web Scraping")]:
        if not os.environ.get(key, ""):
            missing_optional.append(f"{label} ({key})")
    if missing_optional:
        console.print(f"[yellow]  Warning: optional keys not set — reduced coverage: {', '.join(missing_optional)}[/yellow]")

    return {
        "openai": openai_key,
        "exa":    os.environ.get("EXA_API_KEY", ""),
        "apify":  os.environ.get("APIFY_API_KEY", ""),
    }


def run_pipeline(input_data: dict, api_key: str, save_report: bool = True) -> Optional[dict]:
    """Run the full 7-stage due diligence pipeline with telemetry."""

    keys  = _check_keys()
    exa   = ExaSearch(keys["exa"])       if keys["exa"]   else None
    apify = ApifyScraper(keys["apify"])  if keys["apify"] else None

    client  = OpenAI(api_key=api_key)
    company = input_data.get("company_name", "Unknown")
    website = input_data.get("company_website", "")
    domain  = _domain_from(website) if website else ""
    person  = input_data.get("decision_maker_name", "")
    title   = input_data.get("decision_maker_job_title", "")
    linkedin = input_data.get("decision_maker_linkedin_url", "")

    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug    = company.lower().replace(" ", "_")[:20]
    run_id  = f"{slug.upper()}_{ts}"

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
        "[dim]7-Stage Autonomous Intelligence Pipeline  v4.0[/dim]",
        border_style="dim white", padding=(1, 4),
    ))
    console.print()
    console.print(f"  Target  : [bold]{company}[/bold]  {website}")
    console.print(f"  Contact : {person}  |  {title}")
    console.print(f"  Run ID  : [dim]{run_id}[/dim]")
    console.print()
    console.print("-" * 60)

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 1 — Input Validation (hard-fail)
    # ──────────────────────────────────────────────────────────────────────────
    console.print()
    console.print("  [bold]STAGE 1[/bold] — Input Validation")
    _stage("Validating fields, URL patterns, email-domain alignment", "running")
    s1_start = time.time()

    s1 = _llm(client, _S1_SYSTEM,
               f"Validate:\n{json.dumps(input_data, indent=2)}", "Stage 1 — Validation",
               telemetry)

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

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 2 — Data Collection (isolated per source)
    # ──────────────────────────────────────────────────────────────────────────
    console.print()
    console.print("  [bold]STAGE 2[/bold] — Data Collection")
    s2_start = time.time()
    s2_errors = []

    # Professional profile scrape
    if apify and linkedin:
        _stage("Professional profile scrape", "running")
        apify_li = apify.scrape_linkedin_profile(linkedin)
        enrichment.setdefault("apify", {})["linkedin_profile"] = apify_li
        ok = apify_li.get("status") == "success"
        cnt = len(apify_li.get("items", []))
        telemetry["data_coverage"]["profile_scrape"] = cnt
        _stage("Professional profile scrape", "done" if ok else "fail",
               f"{cnt} items" if ok else apify_li.get("error", "")[:80])
        if not ok:
            s2_errors.append("profile_scrape")

    # Company website crawl
    if apify and website:
        _stage("Company website crawl", "running")
        apify_web = apify.scrape_website(website, max_pages=5)
        enrichment.setdefault("apify", {})["website"] = apify_web
        ok = apify_web.get("status") == "success"
        cnt = len(apify_web.get("items", []))
        telemetry["data_coverage"]["website_crawl"] = cnt
        _stage("Company website crawl", "done" if ok else "fail",
               f"{cnt} pages" if ok else apify_web.get("error", "")[:80])
        if not ok:
            s2_errors.append("website_crawl")

    # Google search
    if apify and company:
        _stage("Google search — company background", "running")
        try:
            google_res = apify.google_search(
                f'"{company}" review reputation background site:linkedin.com OR site:crunchbase.com OR news',
                max_results=8,
            )
            enrichment.setdefault("apify", {})["google_search"] = google_res
            ok = google_res.get("status") == "success"
            cnt = len(google_res.get("items", []))
            telemetry["data_coverage"]["google_search"] = cnt
            _stage("Google search — company background", "done" if ok else "fail",
                   f"{cnt} results" if ok else google_res.get("error", "")[:60])
        except Exception as e:
            _stage("Google search — company background", "fail", str(e)[:60])
            s2_errors.append("google_search")

    if not apify:
        _stage("Web scraping + Google search", "skip", "no scraping key configured")

    # Neural search — company intelligence
    if exa:
        _stage("Web intelligence — company", "running")
        exa_co = exa.search_company_intel(company, domain or None)
        cnt = len(exa_co.get("results", []))
        telemetry["data_coverage"]["web_company_intel"] = cnt
        _stage("Web intelligence — company", "done" if "error" not in exa_co else "fail",
               f"{cnt} results")

        _stage("Web intelligence — decision maker", "running")
        exa_pe = exa.search_person_intel(person, company=company, title=title)
        cnt = len(exa_pe.get("results", []))
        telemetry["data_coverage"]["web_person_intel"] = cnt
        _stage("Web intelligence — decision maker", "done" if "error" not in exa_pe else "fail",
               f"{cnt} results")

        _stage("Domain verification", "running")
        exa_dom = exa.verify_domain(domain) if domain else {}
        cnt = len(exa_dom.get("results", []))
        telemetry["data_coverage"]["web_domain_check"] = cnt
        _stage("Domain verification", "done" if domain else "skip",
               f"{cnt} results" if domain else "no domain")

        enrichment["exa"] = {
            "company_intel": exa_co,
            "person_intel":  exa_pe,
            "domain_check":  exa_dom,
        }
    else:
        _stage("Neural web search", "skip", "no search key configured")

    telemetry["stages"]["stage_2"] = {
        "status": "partial" if s2_errors else "success",
        "duration_s": round(time.time() - s2_start, 2),
        "failed_sources": s2_errors,
        "data_coverage": dict(telemetry["data_coverage"]),
    }

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 3 — Cross-Verification
    # ──────────────────────────────────────────────────────────────────────────
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
        return _llm(client, _S3_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nWEB INTELLIGENCE:\n{_truncate(s3_ctx)}",
                    "Stage 3 — Cross-Verification", telemetry)

    s3 = _stage_run("Cross-verification", _run_s3, "stage_3", telemetry, "s3")
    _stage("Cross-verification", "done",
           f"{len(s3.get('matches',[]))} matches, {len(s3.get('mismatches',[]))} mismatches")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 4 — Risk Detection
    # ──────────────────────────────────────────────────────────────────────────
    console.print()
    console.print("  [bold]STAGE 4[/bold] — Risk Detection")

    if exa:
        _stage("Web risk signal search", "running")
        try:
            exa_risk = exa.search_risk_signals(company, person)
            enrichment["exa"]["risk_signals"] = exa_risk
            cnt = len(exa_risk.get("results", []))
            telemetry["data_coverage"]["web_risk_signals"] = cnt
            _stage("Web risk signal search", "done" if "error" not in exa_risk else "fail",
                   f"{cnt} results")
        except Exception as e:
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
        return _llm(client, _S4_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE DATA:\n{_truncate(s4_ctx)}",
                    "Stage 4 — Risk Detection", telemetry)

    s4 = _stage_run("Risk classification", _run_s4, "stage_4", telemetry, "s4")
    _stage("Risk classification", "done",
           f"{len(s4.get('red_flags',[]))} red  {len(s4.get('yellow_flags',[]))} yellow  {len(s4.get('green_signals',[]))} green")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 5 — Trust Scoring (with sub-scores)
    # ──────────────────────────────────────────────────────────────────────────
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
        raw = _llm(client, _S5_SYSTEM,
                   f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE + PRIOR STAGES:\n{_truncate(s5_ctx)}",
                   "Stage 5 — Trust Scoring", telemetry)
        return _validate_scores(raw)

    s5 = _stage_run("Trust scoring", _run_s5, "stage_5", telemetry, "s5")
    co, dm, ov = s5.get("company_score", 0), s5.get("decision_maker_score", 0), s5.get("overall_score", 0)
    _stage("Trust scoring", "done", f"company {co}/100  ·  DM {dm}/100  ·  overall {ov}/100")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 6 — Evidence Aggregation
    # ──────────────────────────────────────────────────────────────────────────
    console.print()
    console.print("  [bold]STAGE 6[/bold] — Evidence Aggregation")

    if exa:
        _stage("Evidence & corroboration search", "running")
        try:
            exa_ev = exa.search_evidence(company, domain or None)
            enrichment["exa"]["evidence_search"] = exa_ev
            cnt = len(exa_ev.get("results", []))
            telemetry["data_coverage"]["web_evidence"] = cnt
            _stage("Evidence & corroboration search", "done" if "error" not in exa_ev else "fail",
                   f"{cnt} results")
        except Exception as e:
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
        return _llm(client, _S6_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nINTELLIGENCE + PRIOR STAGES:\n{_truncate(s6_ctx)}",
                    "Stage 6 — Evidence Aggregation", telemetry)

    s6 = _stage_run("Evidence aggregation", _run_s6, "stage_6", telemetry, "s6")
    _stage("Evidence aggregation", "done",
           f"{len(s6.get('supporting_evidence',[]))} supporting  ·  {len(s6.get('contradicting_signals',[]))} contradicting")

    # ──────────────────────────────────────────────────────────────────────────
    # STAGE 7 — Final Assessment
    # ──────────────────────────────────────────────────────────────────────────
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
        return _llm(client, _S7_SYSTEM,
                    f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nALL STAGE OUTPUTS:\n{_truncate(s7_ctx, 7000)}",
                    "Stage 7 — Final Assessment", telemetry)

    s7 = _stage_run("Final assessment", _run_s7, "stage_7", telemetry, "s7")

    rec = s7.get("recommendation", "CAUTION")
    col = {"PROCEED": "bright_green", "CAUTION": "yellow", "REJECT": "red"}.get(rec, "white")
    _stage(f"Final verdict — [{col}]{rec}[/{col}]", "done",
           f"{s7.get('confidence','?')}  {s7.get('confidence_percentage',0)}%")

    # ── Finalise telemetry ────────────────────────────────────────────────────
    telemetry["pipeline_end"]      = time.time()
    telemetry["total_duration_s"]  = round(telemetry["pipeline_end"] - telemetry["pipeline_start"], 2)
    telemetry["total_llm_calls"]   = len(telemetry["llm_calls"])
    telemetry["stages_succeeded"]  = sum(1 for s in telemetry["stages"].values() if s.get("status") == "success")
    telemetry["stages_failed"]     = sum(1 for s in telemetry["stages"].values() if s.get("status") == "failed")

    # ── Assemble result ───────────────────────────────────────────────────────
    result = {
        "run_id": run_id,
        "stage_results": {
            "input_validation":     s1,
            "cross_verification":   s3,
            "risk_detection":       s4,
            "trust_scoring":        s5,
            "evidence_aggregation": s6,
            "final_assessment":     s7,
        },
        "telemetry": telemetry,
        "metadata": {
            "agent_version":    "4.0",
            "llm_model":        "gpt-4o",
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
    if telemetry["errors"]:
        console.print(f"  [yellow]  Errors: {len(telemetry['errors'])} stage(s) had issues — see monitor report[/yellow]")
    console.print()

    # ── Save JSON ─────────────────────────────────────────────────────────────
    if save_report:
        os.makedirs("reports", exist_ok=True)
        json_path = f"reports/{slug}_{ts}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "input":        input_data,
                "enrichment":   enrichment,
                "analysis":     result,
                "generated_at": datetime.now().isoformat(),
            }, f, indent=2, default=str)
        console.print(f"  JSON        --> {json_path}")

    return result
