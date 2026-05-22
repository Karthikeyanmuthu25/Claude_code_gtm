"""
B2B Due Diligence Verification Agent — Core Orchestrator v3.0

Stage 1 — Input Validation      → OpenAI GPT-4o (pure logic)
Stage 2 — Data Collection       → Apify + Exa
Stage 3 — Cross-Verification    → Exa + OpenAI GPT-4o
Stage 4 — Risk Detection        → Exa + Apify + OpenAI GPT-4o
Stage 5 — Trust Scoring         → Exa + OpenAI GPT-4o
Stage 6 — Evidence Aggregation  → Exa + OpenAI GPT-4o
Stage 7 — Final Assessment      → OpenAI GPT-4o (pure synthesis)
"""

import json
import os
import sys
import io as _io
from typing import Optional
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from .tools import ExaSearch, ApifyScraper


def _make_console() -> Console:
    if "streamlit" in sys.modules:
        return Console(file=_io.StringIO(), highlight=False)
    return Console(legacy_windows=False)


console = _make_console()


def _domain_from(website: str) -> str:
    return website.replace("https://", "").replace("http://", "").split("/")[0].strip()


def _truncate(data: dict, max_chars: int = 6000) -> str:
    raw = json.dumps(data, indent=2, default=str)
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n... [truncated]"
    return raw


def _stage(label: str, status: str = "running", detail: str = ""):
    icons = {
        "running": "[yellow]>>>[/yellow]",
        "done":    "[bright_green]OK [/bright_green]",
        "skip":    "[dim]---[/dim]",
        "fail":    "[red]ERR[/red]",
    }
    icon = icons.get(status, "   ")
    detail_str = f"  ({detail})" if detail else ""
    console.print(f"  {icon} {label}{detail_str}")


def _llm(client: OpenAI, system: str, user: str, label: str) -> dict:
    """Single GPT-4o call returning parsed JSON."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        raw   = resp.choices[0].message.content.strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        os.makedirs("logs", exist_ok=True)
        with open("logs/last_raw_response.txt", "w", encoding="utf-8") as f:
            f.write(raw)
        raise RuntimeError(f"{label} returned invalid JSON: {exc}\nPreview: {raw[:300]}") from exc


# ── Stage system prompts ──────────────────────────────────────────────────────

_S1_SYSTEM = """You are a strict input validator for a B2B due diligence pipeline.
Perform pure logic checks — no external lookups needed.

Validate:
- company_name: non-empty string
- company_website: valid http/https URL, proper domain structure
- company_location: non-empty string
- decision_maker_name: non-empty, looks like a real full name
- decision_maker_job_title: non-empty string
- decision_maker_linkedin_url: must contain linkedin.com/in/
- decision_maker_email: valid email format; flag if domain differs from company website domain
- URL patterns: no typos, no localhost, no IP addresses

Return ONLY valid JSON, no prose:
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
You receive input data provided by the user plus Exa web intelligence results.

Cross-check all provided fields against what Exa found:
- Company name vs domain vs Exa search results
- Email domain vs website domain alignment
- Decision maker name — does Exa confirm this person exists at this company?
- Job title — does Exa confirm this title at this company?
- Location — is the UAE/region mentioned consistently?
- Are there any mismatches between what was claimed and what was found online?

Cite which Exa result confirmed or contradicted each point.

Return ONLY valid JSON:
{
  "matches": ["description citing Exa source"],
  "mismatches": ["mismatch with source"],
  "unverifiable": ["field that could not be confirmed online"]
}"""

_S4_SYSTEM = """You are a risk detection specialist for B2B due diligence.
You receive Exa risk/reputation search results and Apify scraped website + LinkedIn content.

Classify all signals:
- red_flags: fraud, scam, legal actions, fake profiles, domain spoofing, suspicious registration patterns
- yellow_flags: limited data, inconsistencies, recently registered domain, no verifiable history
- green_signals: established brand, professional website, verified online presence, consistent identity

Cover: domain credibility, news/reputation, fraud mentions, website authenticity, profile consistency.
Cite specific sources for each flag.

Return ONLY valid JSON:
{
  "red_flags": [],
  "yellow_flags": ["flag — source: ..."],
  "green_signals": ["signal — source: ..."]
}"""

_S5_SYSTEM = """You are a trust scoring specialist for B2B due diligence.
You receive Exa web intelligence data plus all prior stage outputs (cross-verification, risk detection).
There is no Vibe Prospecting data — base scoring entirely on Exa results, Apify scrapes, and stage outputs.

Score company (0–100) and decision maker (0–100):

Company scoring factors:
- Domain age signals, SSL, professional infrastructure (from Apify)
- Brand recognition and web presence depth (from Exa)
- News coverage, partnerships, awards
- Consistency of identity across web sources
- Red/yellow/green flag balance from Stage 4

Decision maker scoring factors:
- Confirmation of name + role at this company from Exa
- LinkedIn profile existence and data quality (from Apify)
- Email domain match with company website
- Public presence and professional credibility (Exa results)
- Cross-verification match rate from Stage 3

overall_score = (company_score * 0.6) + (decision_maker_score * 0.4)

Return ONLY valid JSON:
{
  "company_score": 0,
  "company_score_rationale": "specific rationale citing Exa/Apify findings",
  "decision_maker_score": 0,
  "decision_maker_score_rationale": "specific rationale citing Exa/Apify findings",
  "overall_score": 0
}"""

_S6_SYSTEM = """You are an evidence aggregation specialist for B2B due diligence.
You receive Exa evidence search results plus all prior stage outputs.

Synthesise findings into three lists:
- supporting_evidence: concrete positive signals (cite URLs/sources where found)
- contradicting_signals: anything undermining trust or contradicting provided info
- neutral_observations: factual observations that are neither positive nor negative

Be specific — reference actual content found by Exa or Apify.

Return ONLY valid JSON:
{
  "supporting_evidence": ["evidence — source: ..."],
  "contradicting_signals": [],
  "neutral_observations": ["observation"]
}"""

_S7_SYSTEM = """You are the final assessment specialist for B2B due diligence.
You receive complete outputs from all prior stages (1–6). No new data — pure synthesis.

Rules:
- PROCEED: overall_score >= 70 AND no red flags AND confidence >= 75%
- CAUTION: overall_score 40–69 OR yellow flags present OR data gaps
- REJECT: overall_score < 40 OR any red flags present

Confidence:
- HIGH: >= 80% — strong data coverage, consistent signals
- MEDIUM: 50–79% — moderate data, some gaps
- LOW: < 50% — significant data gaps or conflicting signals

Return ONLY valid JSON:
{
  "recommendation": "PROCEED",
  "confidence": "HIGH",
  "confidence_percentage": 85,
  "primary_reason": "one-sentence core reason",
  "action_items": ["concrete next step 1", "concrete next step 2"],
  "summary": "3–5 sentence paragraph synthesising all findings."
}"""


def run_pipeline(input_data: dict, api_key: str, save_report: bool = True) -> Optional[dict]:
    """Run the full 7-stage due diligence pipeline — Apify + Exa + OpenAI GPT-4o."""

    exa_key   = os.environ.get("EXA_API_KEY", "")
    apify_key = os.environ.get("APIFY_API_KEY", "")

    exa   = ExaSearch(exa_key)       if exa_key   else None
    apify = ApifyScraper(apify_key)  if apify_key else None

    client   = OpenAI(api_key=api_key)
    company  = input_data.get("company_name", "Unknown")
    website  = input_data.get("company_website", "")
    domain   = _domain_from(website) if website else ""
    person   = input_data.get("decision_maker_name", "")
    title    = input_data.get("decision_maker_job_title", "")
    linkedin = input_data.get("decision_maker_linkedin_url", "")

    console.print()
    console.print(Panel.fit(
        "[bold white]B2B DUE DILIGENCE VERIFICATION AGENT[/bold white]\n"
        "[dim]7-Stage Autonomous Intelligence Pipeline[/dim]\n"
        "[dim]Apify  |  Exa Search  |  OpenAI GPT-4o[/dim]",
        border_style="dim white", padding=(1, 4),
    ))
    console.print()
    console.print(f"  Target : [bold]{company}[/bold]  {website}")
    console.print(f"  Person : {person}  |  {title}")
    console.print()
    console.print("-" * 60)

    enrichment = {}

    # ── STAGE 1 — Input Validation (GPT-4o) ──────────────────────────────────
    console.print()
    console.print("  [bold]STAGE 1[/bold] — Input Validation  [dim][OpenAI GPT-4o][/dim]")
    _stage("GPT-4o: validating fields, URL patterns, email-domain alignment", "running")

    s1 = _llm(client, _S1_SYSTEM,
              f"Validate these input fields:\n{json.dumps(input_data, indent=2)}", "Stage 1")

    if s1.get("errors"):
        _stage("GPT-4o: field validation", "fail", " | ".join(s1["errors"]))
        raise ValueError(f"Stage 1 validation failed: {'; '.join(s1['errors'])}")

    detail = "all fields valid"
    if s1.get("warnings"):
        detail = f"{len(s1['warnings'])} warning(s): {s1['warnings'][0][:60]}"
    _stage("GPT-4o: field validation", "done", detail)

    # ── STAGE 2 — Data Collection (Apify + Exa) ───────────────────────────────
    console.print()
    console.print("  [bold]STAGE 2[/bold] — Data Collection  [dim][Apify + Exa][/dim]")

    # Apify: LinkedIn profile scrape
    if apify and linkedin:
        _stage("Apify: LinkedIn profile scrape", "running")
        apify_li = apify.scrape_linkedin_profile(linkedin)
        enrichment.setdefault("apify", {})["linkedin_profile"] = apify_li
        ok = apify_li.get("status") == "success"
        _stage("Apify: LinkedIn profile scrape",
               "done" if ok else "fail",
               f"{len(apify_li.get('items', []))} items" if ok else apify_li.get("error", "")[:80])
    elif not apify:
        _stage("Apify scraping", "skip", "no APIFY_API_KEY")

    # Apify: company website crawl
    if apify and website:
        _stage("Apify: company website crawl", "running")
        apify_web = apify.scrape_website(website, max_pages=4)
        enrichment.setdefault("apify", {})["website"] = apify_web
        ok = apify_web.get("status") == "success"
        _stage("Apify: company website crawl",
               "done" if ok else "fail",
               f"{len(apify_web.get('items', []))} pages" if ok else apify_web.get("error", "")[:80])

    # Exa: company + person + domain intelligence
    if exa:
        _stage("Exa: company intelligence search", "running")
        exa_co = exa.search_company_intel(company, domain or None)
        _stage("Exa: company intelligence search",
               "done" if "error" not in exa_co else "fail",
               f"{len(exa_co.get('results', []))} results")

        _stage("Exa: person intelligence search", "running")
        exa_pe = exa.search_person_intel(person, company=company, title=title)
        _stage("Exa: person intelligence search",
               "done" if "error" not in exa_pe else "fail",
               f"{len(exa_pe.get('results', []))} results")

        _stage("Exa: domain verification", "running")
        exa_dom = exa.verify_domain(domain) if domain else {}
        _stage("Exa: domain verification",
               "done" if domain else "skip",
               f"{len(exa_dom.get('results', []))} results" if domain else "no domain")

        enrichment["exa"] = {
            "company_intel": exa_co,
            "person_intel":  exa_pe,
            "domain_check":  exa_dom,
        }
    else:
        _stage("Exa Search", "skip", "no EXA_API_KEY")

    # ── STAGE 3 — Cross-Verification (Exa + GPT-4o) ───────────────────────────
    console.print()
    console.print("  [bold]STAGE 3[/bold] — Cross-Verification  [dim][Exa + OpenAI GPT-4o][/dim]")
    _stage("GPT-4o: cross-checking identity against Exa web intelligence", "running")

    s3_ctx = {
        "exa_company_intel": enrichment.get("exa", {}).get("company_intel", {}),
        "exa_person_intel":  enrichment.get("exa", {}).get("person_intel", {}),
        "exa_domain_check":  enrichment.get("exa", {}).get("domain_check", {}),
    }
    s3 = _llm(client, _S3_SYSTEM,
              f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nEXA DATA:\n{_truncate(s3_ctx)}", "Stage 3")
    _stage("GPT-4o: cross-verification", "done",
           f"{len(s3.get('matches',[]))} matches, {len(s3.get('mismatches',[]))} mismatches")

    # ── STAGE 4 — Risk Detection (Exa + Apify + GPT-4o) ──────────────────────
    console.print()
    console.print("  [bold]STAGE 4[/bold] — Risk Detection  [dim][Exa + Apify + OpenAI GPT-4o][/dim]")

    if exa:
        _stage("Exa: risk signal search", "running")
        exa_risk = exa.search_risk_signals(company, person)
        enrichment["exa"]["risk_signals"] = exa_risk
        _stage("Exa: risk signal search",
               "done" if "error" not in exa_risk else "fail",
               f"{len(exa_risk.get('results', []))} results")

    _stage("GPT-4o: classifying risk flags from Exa + Apify data", "running")
    s4_ctx = {
        "exa_risk_signals":  enrichment.get("exa", {}).get("risk_signals", {}),
        "exa_company_intel": enrichment.get("exa", {}).get("company_intel", {}),
        "apify_website":     enrichment.get("apify", {}).get("website", {}),
        "apify_linkedin":    enrichment.get("apify", {}).get("linkedin_profile", {}),
    }
    s4 = _llm(client, _S4_SYSTEM,
              f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nEXA + APIFY DATA:\n{_truncate(s4_ctx)}", "Stage 4")
    _stage("GPT-4o: risk classification", "done",
           f"{len(s4.get('red_flags',[]))} red  {len(s4.get('yellow_flags',[]))} yellow  {len(s4.get('green_signals',[]))} green")

    # ── STAGE 5 — Trust Scoring (Exa + GPT-4o) ───────────────────────────────
    console.print()
    console.print("  [bold]STAGE 5[/bold] — Trust Scoring  [dim][Exa + OpenAI GPT-4o][/dim]")
    _stage("GPT-4o: scoring company + decision maker via Exa intelligence", "running")

    s5_ctx = {
        "exa_company_intel": enrichment.get("exa", {}).get("company_intel", {}),
        "exa_person_intel":  enrichment.get("exa", {}).get("person_intel", {}),
        "apify_website":     enrichment.get("apify", {}).get("website", {}),
        "apify_linkedin":    enrichment.get("apify", {}).get("linkedin_profile", {}),
        "cross_verification": s3,
        "risk_detection":     s4,
    }
    s5 = _llm(client, _S5_SYSTEM,
              f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nEXA + APIFY + PRIOR STAGES:\n{_truncate(s5_ctx)}", "Stage 5")
    co  = s5.get("company_score", 0)
    dm  = s5.get("decision_maker_score", 0)
    ov  = s5.get("overall_score", 0)
    _stage("GPT-4o: trust scoring", "done",
           f"company {co}/100  ·  DM {dm}/100  ·  overall {ov}/100")

    # ── STAGE 6 — Evidence Aggregation (Exa + GPT-4o) ────────────────────────
    console.print()
    console.print("  [bold]STAGE 6[/bold] — Evidence Aggregation  [dim][Exa + OpenAI GPT-4o][/dim]")

    if exa:
        _stage("Exa: evidence search", "running")
        exa_ev = exa.search_evidence(company, domain or None)
        enrichment["exa"]["evidence_search"] = exa_ev
        _stage("Exa: evidence search",
               "done" if "error" not in exa_ev else "fail",
               f"{len(exa_ev.get('results', []))} results")

    _stage("GPT-4o: aggregating supporting vs contradicting evidence", "running")
    s6_ctx = {
        "exa_evidence":      enrichment.get("exa", {}).get("evidence_search", {}),
        "exa_company_intel": enrichment.get("exa", {}).get("company_intel", {}),
        "exa_person_intel":  enrichment.get("exa", {}).get("person_intel", {}),
        "cross_verification": s3,
        "risk_detection":     s4,
        "trust_scoring":      s5,
    }
    s6 = _llm(client, _S6_SYSTEM,
              f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nEXA + PRIOR STAGES:\n{_truncate(s6_ctx)}", "Stage 6")
    _stage("GPT-4o: evidence aggregation", "done",
           f"{len(s6.get('supporting_evidence',[]))} supporting  ·  {len(s6.get('contradicting_signals',[]))} contradicting")

    # ── STAGE 7 — Final Assessment (GPT-4o only) ─────────────────────────────
    console.print()
    console.print("  [bold]STAGE 7[/bold] — Final Assessment  [dim][OpenAI GPT-4o][/dim]")
    _stage("GPT-4o: synthesising all stages -- PROCEED / CAUTION / REJECT", "running")

    s7_ctx = {
        "stage_1_validation":   s1,
        "stage_3_cross_verify": s3,
        "stage_4_risk":         s4,
        "stage_5_trust_scores": s5,
        "stage_6_evidence":     s6,
    }
    s7 = _llm(client, _S7_SYSTEM,
              f"INPUT DATA:\n{json.dumps(input_data, indent=2)}\n\nALL STAGE OUTPUTS:\n{_truncate(s7_ctx, max_chars=7000)}", "Stage 7")

    rec = s7.get("recommendation", "CAUTION")
    col = {"PROCEED": "bright_green", "CAUTION": "yellow", "REJECT": "red"}.get(rec, "white")
    _stage(f"GPT-4o: final verdict -- [{col}]{rec}[/{col}]", "done",
           f"{s7.get('confidence','?')}  {s7.get('confidence_percentage',0)}%")

    # ── Assemble result ───────────────────────────────────────────────────────
    result = {
        "stage_results": {
            "input_validation":     s1,
            "cross_verification":   s3,
            "risk_detection":       s4,
            "trust_scoring":        s5,
            "evidence_aggregation": s6,
            "final_assessment":     s7,
        },
        "metadata": {
            "agent_version":     "3.0",
            "llm":               "openai/gpt-4o",
            "stages_completed":  7,
            "analysis_depth":    "FULL",
            "data_sources_used": [
                k for k, v in {
                    "apify_scraping": bool(apify),
                    "exa_search":     bool(exa),
                }.items() if v
            ],
        },
    }

    # ── Print verdict ─────────────────────────────────────────────────────────
    console.print()
    console.print("-" * 60)
    console.print()
    console.print(f"  VERDICT : [{col}]{rec}[/{col}]")
    console.print(f"  Confidence : {s7.get('confidence','?')} ({s7.get('confidence_percentage',0)}%)")
    console.print(f"  Trust Score : {ov}/100")
    console.print(f"  Company : {co}/100   Decision Maker : {dm}/100")
    console.print()

    # ── Save JSON report ──────────────────────────────────────────────────────
    if save_report:
        from datetime import datetime
        os.makedirs("reports", exist_ok=True)
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug   = company.lower().replace(" ", "_")[:25]
        json_path = f"reports/{slug}_{ts_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "input":        input_data,
                "enrichment":   enrichment,
                "analysis":     result,
                "generated_at": datetime.now().isoformat(),
            }, f, indent=2, default=str)
        console.print(f"  JSON  --> {json_path}")

    return result
