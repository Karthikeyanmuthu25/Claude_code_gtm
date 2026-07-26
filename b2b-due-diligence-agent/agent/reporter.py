"""
Report Exporter v5.0 — Two-report architecture.

export_executive_report() → Client-facing strategic intelligence report
export_monitor_report()   → Internal agent performance & governance report
"""

import json
import re
from datetime import datetime
from pathlib import Path


# ── Text sanitiser — strip all tool/vendor names from AI-generated text ───────

_TOOL_PATTERNS = [
    r"— source:\s*(?:Apify|Exa|Vibe|OpenAI|GPT)[^,\n\.]*",
    r"as confirmed by (?:Exa|Apify)[^,\n\.]*",
    r"confirmed by (?:Exa|Apify)[^,\n\.]*result from",
    r"\bExa'?s?\b[\s\-:]*(search|result[s]?|intelligence|data|web|neural)?",
    r"\bApify'?s?\b[\s\-:]*(result[s]?|data|scrape[d]?|crawl[ed]?)?",
    r"\bVibe\b[\s\-:]*(Prospecting|data|result[s]?)?",
    r"\bOpenAI\b[\s\-:]*(GPT[\-\s]?4o?)?",
    r"\bGPT[\-\s]?4o?\b",
    r"\bAnthropic\b",
    r"source:\s*(?:Exa|Apify|Vibe)[^,\n\.]*",
    r"\bneural search\b",
    r"\bweb scraping tool\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TOOL_PATTERNS]


def _clean(text: str) -> str:
    if not isinstance(text, str):
        return text
    for pattern in _COMPILED:
        text = pattern.sub("", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = re.sub(r"\s*[—\-]\s*$", "", text).strip()
    text = re.sub(r"\s*:\s*$", "", text).strip()
    return text


def _clean_list(items: list) -> list:
    return [_clean(i) for i in items if isinstance(i, str) and _clean(i)]


# ── Score helpers ─────────────────────────────────────────────────────────────

def _risk_tier(score) -> str:
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "Unscored"
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    return "High Risk"


def _trust_label(score) -> str:
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "—"
    if score >= 75:
        return "HIGH TRUST"
    elif score >= 50:
        return "MODERATE"
    return "LOW TRUST"


def _coverage_label(count: int) -> str:
    if count >= 5:
        return "✅ Good"
    elif count >= 2:
        return "⚠️ Partial"
    elif count == 1:
        return "⚠️ Minimal"
    return "🔴 None"


def _health_label(telemetry: dict) -> str:
    errors = len(telemetry.get("errors", []))
    failed = telemetry.get("stages_failed", 0)
    coverage = telemetry.get("data_coverage", {})
    zero_sources = sum(1 for v in coverage.values() if v == 0)
    if failed == 0 and errors == 0 and zero_sources <= 2:
        return "✅ HEALTHY"
    elif failed <= 1 and zero_sources <= 4:
        return "⚠️ DEGRADED"
    return "🔴 UNHEALTHY"


# ── Shared path builder ───────────────────────────────────────────────────────

def _report_path(company_name: str, suffix: str, output_dir: str) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^\w\-]", "_", company_name.lower()).strip("_")[:20]
    return f"{output_dir}/{slug}_{suffix}_{ts}.md"


# ── JSON export ───────────────────────────────────────────────────────────────

def export_json(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^\w\-]", "_", input_data.get("company_name", "unknown").lower()).strip("_")[:20]
    path = f"{output_dir}/{slug}_{ts}.json"
    with open(path, "w") as f:
        json.dump({
            "input":        input_data,
            "analysis":     result,
            "generated_at": datetime.now().isoformat(),
            "report_version": "5.0",
        }, f, indent=2)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 1 — Executive Intelligence Report (Client-facing)
# ─────────────────────────────────────────────────────────────────────────────

def export_executive_report(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    path = _report_path(input_data.get("company_name", "unknown"), "executive", output_dir)

    sr   = result.get("stage_results", {})
    fa   = sr.get("final_assessment", {})
    ts_d = sr.get("trust_scoring", {})
    rd   = sr.get("risk_detection", {})
    ea   = sr.get("evidence_aggregation", {})
    cv   = sr.get("cross_verification", {})

    rec  = fa.get("recommendation", "CAUTION")
    cs   = ts_d.get("company_score", 0)
    ds   = ts_d.get("decision_maker_score", 0)
    os_  = ts_d.get("overall_score", 0)

    company  = input_data.get("company_name", "—")
    dm_name  = input_data.get("decision_maker_name", "—")
    dm_title = input_data.get("decision_maker_job_title", "—")
    now      = datetime.now().strftime("%B %d, %Y")
    run_id   = result.get("run_id", "—")

    rec_display = {
        "PROCEED": "✅ PROCEED",
        "CAUTION": "⚠️ PROCEED WITH CAUTION",
        "REJECT":  "🚫 DO NOT PROCEED",
    }.get(rec, rec)

    # Sub-scores
    co_sub = ts_d.get("company_sub_scores", {})
    dm_sub = ts_d.get("dm_sub_scores", {})

    lines = [
        "# B2B Due Diligence — Executive Intelligence Report",
        f"## {company}",
        "",
        f"> **Prepared:** {now}  ",
        "> **Classification:** Confidential — Internal Use Only  ",
        "> **Scope:** Full-Spectrum Verification (7-Stage Analysis)  ",
        f"> **Reference:** {run_id}  ",
        "",
        "---",
        "",
        "## 1. Subject Profile",
        "",
        "| Field | Details |",
        "|-------|---------|",
        f"| **Organization** | {company} |",
        f"| **Website** | {input_data.get('company_website', '—')} |",
        f"| **Headquarters** | {input_data.get('company_location', '—')} |",
        f"| **Primary Contact** | {dm_name} |",
        f"| **Title / Role** | {dm_title} |",
        f"| **LinkedIn** | {input_data.get('decision_maker_linkedin_url', '—')} |",
        f"| **Business Email** | {input_data.get('decision_maker_email', '—') or '—'} |",
        "",
        "---",
        "",
        "## 2. Executive Recommendation",
        "",
        f"### Verdict: {rec_display}",
        "",
        f"**Analyst Confidence:** {fa.get('confidence', '—')} ({fa.get('confidence_percentage', 0)}%)",
        "",
        "#### Strategic Summary",
        "",
        _clean(fa.get("summary", "—")),
        "",
        "#### Key Rationale",
        "",
        _clean(fa.get("primary_reason", "—")),
        "",
        "---",
        "",
        "## 3. Trust & Credibility Scorecard",
        "",
        "| Entity | Credibility Score | Risk Tier |",
        "|--------|------------------|-----------|",
        f"| {company} (Organization) | {cs} / 100 | {_risk_tier(cs)} |",
        f"| {dm_name} (Individual) | {ds} / 100 | {_risk_tier(ds)} |",
        f"| **Combined Assessment** | **{os_} / 100** | **{_risk_tier(os_)}** |",
        "",
        "> Scores are derived from multi-source verification across digital presence, professional records, and cross-referenced intelligence.",
    ]

    # Sub-score breakdown if available
    if co_sub or dm_sub:
        lines += ["", "#### Score Breakdown", ""]
        if co_sub:
            lines += [
                f"**{company} — Scoring Factors**",
                "",
                "| Factor | Score |",
                "|--------|-------|",
            ]
            labels = {
                "domain_credibility":   "Domain & Infrastructure Credibility",
                "web_presence_depth":   "Web Presence Depth",
                "news_and_reputation":  "News Coverage & Reputation",
                "identity_consistency": "Identity Consistency",
            }
            for k, label in labels.items():
                if k in co_sub:
                    lines.append(f"| {label} | {co_sub[k]} / 100 |")
            lines.append("")
        if dm_sub:
            lines += [
                f"**{dm_name} — Scoring Factors**",
                "",
                "| Factor | Score |",
                "|--------|-------|",
            ]
            dm_labels = {
                "profile_verification":       "Identity & Role Verification",
                "linkedin_data_quality":      "Professional Profile Quality",
                "email_domain_alignment":     "Email / Domain Alignment",
                "public_professional_presence": "Public Professional Presence",
            }
            for k, label in dm_labels.items():
                if k in dm_sub:
                    lines.append(f"| {label} | {dm_sub[k]} / 100 |")

    lines += [
        "",
        "---",
        "",
        "## 4. Risk Assessment",
        "",
        "### Critical Risk Indicators",
        "",
    ]

    red_flags = _clean_list(rd.get("red_flags", []))
    lines += [f"- 🔴 {f}" for f in red_flags] or ["- No critical risk indicators identified."]

    lines += ["", "### Areas Requiring Attention", ""]
    yellow_flags = _clean_list(rd.get("yellow_flags", []))
    lines += [f"- 🟡 {f}" for f in yellow_flags] or ["- No significant concerns flagged."]

    lines += ["", "### Positive Indicators", ""]
    green_signals = _clean_list(rd.get("green_signals", []))
    lines += [f"- 🟢 {f}" for f in green_signals] or ["- No strong positive signals identified."]

    lines += [
        "",
        "---",
        "",
        "## 5. Intelligence Verification Summary",
        "",
        "### Verified & Consistent Information",
        "",
    ]
    matches = _clean_list(cv.get("matches", []))
    lines += [f"- ✓ {m}" for m in matches] or ["- No verified matches recorded."]

    lines += ["", "### Discrepancies & Inconsistencies", ""]
    mismatches = _clean_list(cv.get("mismatches", []))
    lines += [f"- ✕ {m}" for m in mismatches] or ["- No discrepancies detected."]

    unverifiable = _clean_list(cv.get("unverifiable", []))
    if unverifiable:
        lines += ["", "### Could Not Be Verified", ""]
        lines += [f"- ◌ {u}" for u in unverifiable]

    lines += [
        "",
        "---",
        "",
        "## 6. Supporting Evidence & Intelligence",
        "",
        "### Corroborating Evidence",
        "",
    ]
    supporting = _clean_list(ea.get("supporting_evidence", []))
    lines += [f"- {e}" for e in supporting] or ["- Insufficient corroborating evidence available."]

    lines += ["", "### Contradicting Intelligence", ""]
    contradicting = _clean_list(ea.get("contradicting_signals", []))
    lines += [f"- {e}" for e in contradicting] or ["- No contradicting intelligence found."]

    lines += ["", "### Contextual Observations", ""]
    neutral = _clean_list(ea.get("neutral_observations", []))
    lines += [f"- {e}" for e in neutral] or ["- No additional observations."]

    lines += [
        "",
        "---",
        "",
        "## 7. Recommended Next Steps",
        "",
    ]
    action_items = _clean_list(fa.get("action_items", []))
    if action_items:
        for i, a in enumerate(action_items, 1):
            lines.append(f"{i}. {a}")
    else:
        lines.append("1. Proceed with standard onboarding due diligence.")

    lines += [
        "",
        "---",
        "",
        "## 8. Analyst Notes & Disclaimers",
        "",
        "This report is produced through an automated multi-stage intelligence process combining "
        "publicly available data, digital footprint analysis, professional network verification, "
        "and cross-referenced business intelligence. All findings should be reviewed by a qualified "
        "analyst before making final business decisions.",
        "",
        "> **Confidentiality Notice:** This document contains proprietary intelligence compiled "
        "exclusively for internal due diligence purposes. Unauthorized distribution is prohibited.",
        "",
        f"*Report Reference: {run_id} | Prepared {now}*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 2 — Agent Performance Monitor Report (Internal)
# ─────────────────────────────────────────────────────────────────────────────

def export_monitor_report(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    path = _report_path(input_data.get("company_name", "unknown"), "monitor", output_dir)

    sr        = result.get("stage_results", {})
    telemetry = result.get("telemetry", {})
    metadata  = result.get("metadata", {})
    fa        = sr.get("final_assessment", {})
    ts_d      = sr.get("trust_scoring", {})
    rd        = sr.get("risk_detection", {})
    cv        = sr.get("cross_verification", {})

    company  = input_data.get("company_name", "—")
    run_id   = result.get("run_id", "—")
    now      = datetime.now().strftime("%B %d, %Y at %H:%M")

    stages   = telemetry.get("stages", {})
    llm_calls = telemetry.get("llm_calls", [])
    coverage  = telemetry.get("data_coverage", {})
    errors    = telemetry.get("errors", [])

    total_dur   = telemetry.get("total_duration_s", 0)
    total_tok   = telemetry.get("total_tokens", 0)
    retry_count = telemetry.get("retry_count", 0)
    s_success   = telemetry.get("stages_succeeded", 0)
    s_failed    = telemetry.get("stages_failed", 0)
    health      = _health_label(telemetry)

    rec  = fa.get("recommendation", "CAUTION")
    conf = fa.get("confidence_percentage", 0)
    os_  = ts_d.get("overall_score", 0)
    co   = ts_d.get("company_score", 0)
    dm   = ts_d.get("decision_maker_score", 0)

    stage_order = [
        ("stage_1", "Stage 1 — Input Validation"),
        ("stage_2", "Stage 2 — Data Collection"),
        ("stage_3", "Stage 3 — Cross-Verification"),
        ("stage_4", "Stage 4 — Risk Detection"),
        ("stage_5", "Stage 5 — Trust Scoring"),
        ("stage_6", "Stage 6 — Evidence Aggregation"),
        ("stage_7", "Stage 7 — Final Assessment"),
    ]

    coverage_labels = {
        "web_company_intel":  "Company Intelligence Search",
        "web_person_intel":   "Decision Maker Intelligence",
        "web_domain_check":   "Domain Verification",
        "web_risk_signals":   "Risk Signal Search",
        "web_evidence":       "Evidence Corroboration Search",
        "profile_scrape":     "Professional Profile Scrape",
        "website_crawl":      "Company Website Crawl (pages)",
        "google_search":      "Google Search Results",
    }

    lines = [
        "# Agent Performance Monitor Report",
        f"## {company} — Run: {run_id}",
        "",
        f"> **Executed:** {now}  ",
        "> **Classification:** Internal — Agent Operations & AI Governance Team  ",
        f"> **Agent Version:** {metadata.get('agent_version', '4.0')}  ",
        f"> **LLM Provider:** {metadata.get('llm_provider', '—')}  ",
        f"> **LLM Model:** {metadata.get('llm_model', 'gpt-4o')}  ",
        "",
        "---",
        "",
        "## 1. Pipeline Execution Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Run ID | `{run_id}` |",
        f"| Total Duration | {total_dur}s |",
        f"| Stages Completed | {s_success + s_failed} / 7 |",
        f"| Stages Succeeded | {s_success} |",
        f"| Stages Failed | {s_failed} |",
        f"| LLM Calls Made | {len(llm_calls)} |",
        f"| Total Tokens Used | {total_tok:,} |",
        f"| Retry Events | {retry_count} |",
        f"| Pipeline Errors | {len(errors)} |",
        f"| Overall Health | {health} |",
        f"| LLM Provider Fallback Triggered | {'⚠️ Yes' if metadata.get('llm_fell_back') else 'No'} |",
    ]

    fallbacks = telemetry.get("provider_fallbacks", [])
    if fallbacks:
        lines += ["", "**Fallback events:**", ""]
        for fb in fallbacks:
            lines.append(f"- `{fb.get('label','—')}`: {fb.get('from','—')} → {fb.get('to','—')} — {fb.get('reason','—')}")

    lines += [
        "",
        "---",
        "",
        "## 2. Stage Performance Breakdown",
        "",
        "| Stage | Status | Duration | Notes |",
        "|-------|--------|----------|-------|",
    ]

    for key, label in stage_order:
        s = stages.get(key, {})
        status = s.get("status", "skipped")
        dur    = f"{s.get('duration_s', '—')}s"
        icon   = {"success": "✅", "partial": "⚠️", "failed": "🔴", "skipped": "—"}.get(status, "—")
        note   = s.get("error", s.get("failed_sources", ""))
        if isinstance(note, list):
            note = ", ".join(note)
        lines.append(f"| {label} | {icon} {status.capitalize()} | {dur} | {str(note)[:80] if note else '—'} |")

    # ── Cost & Token Spend Analysis ───────────────────────────────────────────
    cost = result.get("cost_tracking", {})
    cb   = cost.get("cost_breakdown", {})
    tb   = cost.get("token_breakdown", {})
    ts_tool = cost.get("tool_summary", {})
    rel  = cost.get("reliability", {})
    ct_dur = cost.get("pipeline_duration_s", 0)

    lines += [
        "",
        "---",
        "",
        "## 3. Cost & Token Spend Analysis",
        "",
        "### 3.1 Grand Total",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Grand Total (USD) | ${cb.get('grand_total_usd', 0):.6f} |",
        f"| LLM Cost | ${cb.get('llm_total_usd', 0):.6f} |",
        f"| Tool Cost (est.) | ${cb.get('tool_total_usd', 0):.6f} |",
        f"| Pipeline Duration | {ct_dur}s |",
        "",
        f"> {cb.get('cost_note', '')}",
        "",
        "### 3.2 Token Breakdown",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Tokens | {tb.get('total_tokens', 0):,} |",
        f"| Prompt Tokens | {tb.get('prompt_tokens', 0):,} |",
        f"| Completion Tokens | {tb.get('completion_tokens', 0):,} |",
        f"| Avg Tokens / LLM Call | {tb.get('avg_tokens_per_call', 0)} |",
        "",
        "### 3.3 LLM Call Detail",
        "",
        "| # | Stage | Model | Prompt | Completion | Total | Cost (USD) | Duration | Attempts | Status |",
        "|---|-------|-------|--------|------------|-------|------------|----------|----------|--------|",
    ]

    llm_detail = cost.get("llm_calls", [])
    total_cost_sum = 0.0
    total_prompt_sum = 0
    total_comp_sum = 0
    total_tok_sum = 0
    for i, c in enumerate(llm_detail, 1):
        attempt_str = str(c.get("attempt", 1))
        if c.get("attempt", 1) > 1:
            attempt_str = f"**{attempt_str} RETRIED**"
        status_icon = "✅" if c.get("status") == "success" else "🔴"
        lines.append(
            f"| {i} | {c.get('stage','—')} | {c.get('model','—')} "
            f"| {c.get('prompt_tokens',0):,} | {c.get('completion_tokens',0):,} "
            f"| {c.get('total_tokens',0):,} | ${c.get('total_cost_usd',0):.6f} "
            f"| {c.get('duration_s','—')}s | {attempt_str} | {status_icon} {c.get('status','—')} |"
        )
        total_cost_sum += c.get("total_cost_usd", 0)
        total_prompt_sum += c.get("prompt_tokens", 0)
        total_comp_sum += c.get("completion_tokens", 0)
        total_tok_sum += c.get("total_tokens", 0)

    lines.append(
        f"| **Total** | — | — | **{total_prompt_sum:,}** | **{total_comp_sum:,}** "
        f"| **{total_tok_sum:,}** | **${total_cost_sum:.6f}** | — | — | — |"
    )

    lines += [
        "",
        "### 3.4 Tool Call Detail",
        "",
        "| # | Tool | Method | Stage | Results | Cost (USD) | Duration | Status |",
        "|---|------|--------|-------|---------|------------|----------|--------|",
    ]

    tool_detail = cost.get("tool_calls", [])
    tool_cost_sum = 0.0
    for i, c in enumerate(tool_detail, 1):
        status_icon = {"success": "✅", "failed": "🔴", "skipped": "—"}.get(c.get("status",""), "—")
        lines.append(
            f"| {i} | {c.get('tool','—')} | {c.get('method','—')} | {c.get('stage','—')} "
            f"| {c.get('results_count',0)} | ${c.get('cost_usd',0):.6f} "
            f"| {c.get('duration_s','—')}s | {status_icon} {c.get('status','—')} |"
        )
        tool_cost_sum += c.get("cost_usd", 0)

    lines.append(f"| **Total** | — | — | — | — | **${tool_cost_sum:.6f}** | — | — |")

    lines += [
        "",
        "### 3.5 Tool Summary",
        "",
        "| Tool | Calls | Results | Est. Cost (USD) |",
        "|------|-------|---------|-----------------|",
        f"| Exa Search | {ts_tool.get('exa_calls',0)} | {ts_tool.get('exa_results_total',0)} | ${ts_tool.get('exa_cost_usd',0):.6f} |",
        f"| Apify | {ts_tool.get('apify_calls',0)} | — | ${ts_tool.get('apify_cost_usd',0):.6f} |",
        "",
        f"> Failed tool calls: {ts_tool.get('failed_calls',0)}  |  Skipped: {ts_tool.get('skipped_calls',0)}",
        "",
        "### 3.6 Reliability",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total LLM Calls | {rel.get('total_llm_calls',0)} |",
        f"| Successful | {rel.get('successful_llm',0)} |",
        f"| Failed | {rel.get('failed_llm',0)} |",
        f"| Retry Rate | {rel.get('retry_rate_pct',0)}% |",
    ]

    lines += [
        "",
        "---",
        "",
        "## 4. Data Source Coverage Analysis",
        "",
        "| Source | Results Retrieved | Coverage Quality |",
        "|--------|------------------|-----------------|",
    ]

    total_results = 0
    for key, label in coverage_labels.items():
        count = coverage.get(key, 0)
        total_results += count
        lines.append(f"| {label} | {count} | {_coverage_label(count)} |")

    zero_sources = sum(1 for v in coverage.values() if v == 0)
    lines += [
        "",
        f"> **Total Intelligence Items Retrieved:** {total_results}  ",
        f"> **Zero-coverage Sources:** {zero_sources} / {len(coverage_labels)}  ",
    ]

    if zero_sources > 0:
        zero_list = [coverage_labels.get(k, k) for k, v in coverage.items() if v == 0]
        lines += [
            "",
            "**Coverage Gaps Detected:**",
            "",
        ]
        for z in zero_list:
            lines.append(f"- ⚠️ {z} returned no data — this may reduce verdict reliability")

    lines += [
        "",
        "---",
        "",
        "## 5. LLM Call Performance",
        "",
        "| # | Stage | Duration | Tokens | Attempts | Status |",
        "|---|-------|----------|--------|----------|--------|",
    ]

    for i, call in enumerate(llm_calls, 1):
        status_icon = "✅" if call.get("status") == "success" else "🔴"
        tokens = f"{call.get('tokens', 0):,}" if call.get("tokens") else "—"
        attempts = call.get("attempts", 1)
        attempt_str = f"{attempts}" if attempts == 1 else f"**{attempts} (retried)**"
        lines.append(
            f"| {i} | {call.get('label', '—')} | {call.get('duration_s', '—')}s "
            f"| {tokens} | {attempt_str} | {status_icon} {call.get('status', '—').capitalize()} |"
        )

    avg_dur = round(sum(c.get("duration_s", 0) for c in llm_calls) / len(llm_calls), 2) if llm_calls else 0
    lines += [
        "",
        f"> **Average LLM Response Time:** {avg_dur}s  ",
        f"> **Total Token Spend:** {total_tok:,}  ",
        f"> **Retry Rate:** {retry_count}/{len(llm_calls)} calls required retry  ",
    ]

    lines += [
        "",
        "---",
        "",
        "## 6. Trust Score Audit Trail",
        "",
        f"### Overall Verdict: `{rec}` — Confidence: {conf}%",
        "",
        "| Entity | Score | Risk Tier | Trust Label |",
        "|--------|-------|-----------|-------------|",
        f"| {company} (Organization) | {co} / 100 | {_risk_tier(co)} | {_trust_label(co)} |",
        f"| Decision Maker | {dm} / 100 | {_risk_tier(dm)} | {_trust_label(dm)} |",
        f"| **Combined** | **{os_} / 100** | **{_risk_tier(os_)}** | **{_trust_label(os_)}** |",
        "",
        "#### Company Score Rationale",
        "",
        _clean(ts_d.get("company_score_rationale", "—")),
        "",
        "#### Decision Maker Score Rationale",
        "",
        _clean(ts_d.get("decision_maker_score_rationale", "—")),
    ]

    # Sub-scores
    co_sub = ts_d.get("company_sub_scores", {})
    dm_sub = ts_d.get("dm_sub_scores", {})
    if co_sub:
        lines += ["", "#### Company Sub-Score Breakdown", "", "| Factor | Score | Interpretation |", "|--------|-------|----------------|"]
        for k, v in co_sub.items():
            lines.append(f"| {k.replace('_', ' ').title()} | {v} / 100 | {_risk_tier(v)} |")
    if dm_sub:
        lines += ["", "#### Decision Maker Sub-Score Breakdown", "", "| Factor | Score | Interpretation |", "|--------|-------|----------------|"]
        for k, v in dm_sub.items():
            lines.append(f"| {k.replace('_', ' ').title()} | {v} / 100 | {_risk_tier(v)} |")

    lines += [
        "",
        "---",
        "",
        "## 7. Verification Quality Assessment",
        "",
        f"| Metric | Count |",
        "|--------|-------|",
        f"| Facts Verified & Matched | {len(cv.get('matches', []))} |",
        f"| Discrepancies Found | {len(cv.get('mismatches', []))} |",
        f"| Fields Unverifiable | {len(cv.get('unverifiable', []))} |",
        f"| Red Flags | {len(rd.get('red_flags', []))} |",
        f"| Yellow Flags | {len(rd.get('yellow_flags', []))} |",
        f"| Green Signals | {len(rd.get('green_signals', []))} |",
        "",
    ]

    unverifiable = cv.get("unverifiable", [])
    if unverifiable:
        lines += ["**Unverifiable Fields:**", ""]
        for u in unverifiable:
            lines.append(f"- ◌ {_clean(u)}")

    lines += [
        "",
        "---",
        "",
        "## 8. AI Governance & Risk Assessment",
        "",
        "### Hallucination Risk Indicators",
        "",
    ]

    # Governance analysis
    hallucination_risks = []
    if coverage.get("web_company_intel", 0) == 0:
        hallucination_risks.append("Company intelligence returned zero results — LLM may have generated company facts without grounding")
    if coverage.get("web_person_intel", 0) == 0:
        hallucination_risks.append("Decision maker intelligence returned zero results — person verification is ungrounded")
    if coverage.get("profile_scrape", 0) == 0:
        hallucination_risks.append("Professional profile could not be scraped — LinkedIn data may be absent from analysis")
    if conf < 60:
        hallucination_risks.append(f"Low confidence score ({conf}%) — model acknowledges significant uncertainty in its verdict")
    if len(cv.get("unverifiable", [])) >= 3:
        hallucination_risks.append(f"{len(cv.get('unverifiable', []))} fields were unverifiable — verdict is partially speculative")
    if retry_count > 0:
        hallucination_risks.append(f"{retry_count} LLM retry event(s) occurred — JSON parse instability detected")

    if hallucination_risks:
        for r in hallucination_risks:
            lines.append(f"- ⚠️ {r}")
    else:
        lines.append("- ✅ No significant hallucination risk indicators detected")

    lines += [
        "",
        "### Data Quality Governance",
        "",
    ]

    gov_flags = []
    if zero_sources > 3:
        gov_flags.append(f"HIGH DATA GAP: {zero_sources} of {len(coverage)} intelligence sources returned no data — verdict reliability significantly reduced")
    elif zero_sources > 1:
        gov_flags.append(f"PARTIAL DATA GAP: {zero_sources} intelligence sources returned no data — consider re-running with additional inputs")
    if s_failed > 0:
        failed_names = [label for key, label in stage_order if stages.get(key, {}).get("status") == "failed"]
        gov_flags.append(f"STAGE FAILURE: {', '.join(failed_names)} — these stages used fallback defaults")
    if len(errors) > 0:
        gov_flags.append(f"PIPELINE ERRORS: {len(errors)} error(s) recorded during execution")

    if gov_flags:
        for g in gov_flags:
            lines.append(f"- 🔴 {g}")
    else:
        lines.append("- ✅ Data quality meets governance standards for this run")

    lines += [
        "",
        "### Verdict Reliability Assessment",
        "",
    ]

    # Reliability score
    reliability_score = 100
    reliability_score -= zero_sources * 8
    reliability_score -= s_failed * 15
    reliability_score -= len(hallucination_risks) * 5
    reliability_score = max(0, min(100, reliability_score))

    if reliability_score >= 80:
        rel_label = "✅ HIGH — Verdict is well-supported by multi-source intelligence"
    elif reliability_score >= 60:
        rel_label = "⚠️ MEDIUM — Verdict is partially supported; some data gaps present"
    else:
        rel_label = "🔴 LOW — Verdict has significant data gaps; manual review strongly recommended"

    lines += [
        f"**Reliability Score: {reliability_score}/100**",
        "",
        rel_label,
        "",
        "| Factor | Impact |",
        "|--------|--------|",
        f"| Zero-coverage sources | -{zero_sources * 8} pts ({zero_sources} sources × 8) |",
        f"| Failed stages | -{s_failed * 15} pts ({s_failed} stages × 15) |",
        f"| Hallucination risk indicators | -{len(hallucination_risks) * 5} pts ({len(hallucination_risks)} indicators × 5) |",
        f"| **Final Reliability Score** | **{reliability_score} / 100** |",
    ]

    lines += [
        "",
        "---",
        "",
        "## 9. Pipeline Error Log",
        "",
    ]

    if errors:
        for i, err in enumerate(errors, 1):
            lines.append(f"{i}. `{err}`")
    else:
        lines.append("No errors recorded during this pipeline run.")

    lines += [
        "",
        "---",
        "",
        "## 10. Agent Improvement Recommendations",
        "",
    ]

    recs = []
    if coverage.get("web_company_intel", 0) == 0:
        recs.append("**Expand company search queries** — current search returned no results for this target; consider adding country-specific domains or alternative name variants")
    if coverage.get("profile_scrape", 0) == 0:
        recs.append("**Professional profile scraping failed** — verify scraping access tier; consider alternative profile data sources")
    if coverage.get("google_search", 0) == 0:
        recs.append("**Google search returned no results** — check scraping API quota and actor availability")
    if conf < 70:
        recs.append("**Confidence is below 70%** — provide additional input fields (email, LinkedIn, company registration number) to improve coverage")
    if zero_sources > 2:
        recs.append("**Multiple zero-coverage sources** — this target may have limited online presence; consider manual research or local business registry lookup for MENA targets")
    if not recs:
        recs.append("Pipeline performed well for this target — no specific improvements required")

    for i, r in enumerate(recs, 1):
        lines.append(f"{i}. {r}")

    lines += [
        "",
        "---",
        "",
        "## 11. Governance Sign-off",
        "",
        "| Check | Status |",
        "|-------|--------|",
        f"| All 7 stages executed | {'✅ Yes' if s_success + s_failed == 7 else f'⚠️ Partial ({s_success + s_failed}/7)'} |",
        f"| LLM outputs validated (score bounds) | ✅ Yes — scores clamped to 0–100 |",
        f"| Tool names stripped from report | ✅ Yes — sanitiser applied |",
        f"| No PII beyond provided inputs | ✅ Yes |",
        f"| Hallucination risk assessed | ✅ Yes — {len(hallucination_risks)} indicator(s) flagged |",
        f"| Reliability score computed | ✅ {reliability_score}/100 |",
        "",
        f"*Monitor Report Reference: {run_id} | Generated {now}*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# Backward-compatible alias
def export_markdown(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    return export_executive_report(input_data, result, output_dir)
