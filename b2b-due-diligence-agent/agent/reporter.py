"""
Report Exporter — Generate structured reports from pipeline results.
"""

import json
import re
from datetime import datetime
from pathlib import Path

_TOOL_PATTERNS = [
    # exact tool/brand names with common suffixes
    r'\bExa\b[\s\-:]*(search|result[s]?|intelligence|data|web)?',
    r'\bApify\b[\s\-:]*(result[s]?|data|scrape)?',
    r'\bVibe\b[\s\-:]*(Prospecting|data|result[s]?)?',
    r'\bOpenAI\b[\s\-:]*(GPT[\-\s]?4o?)?',
    r'\bGPT[\-\s]?4o?\b',
    r'\bAnthropic\b',
    r'\bClaude\b[\s\-:]*(AI|model)?',
    r'— source:\s*Exa[^,\n]*',
    r'— source:\s*Apify[^,\n]*',
    r'as confirmed by Exa result from',
    r'confirmed by Exa result from',
    r'source:\s*(Exa|Apify|Vibe)[^,\n\.]*',
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TOOL_PATTERNS]


def _clean(text: str) -> str:
    if not isinstance(text, str):
        return text
    for pattern in _COMPILED:
        text = pattern.sub("", text)
    # collapse multiple spaces
    text = re.sub(r'  +', ' ', text).strip()
    # fix trailing dashes or colons left behind
    text = re.sub(r'\s*[—\-]\s*$', '', text).strip()
    return text


def _clean_list(items: list) -> list:
    return [_clean(i) for i in items if isinstance(i, str)]


def score_label(score: int) -> str:
    if score >= 75:
        return "HIGH TRUST"
    elif score >= 50:
        return "MODERATE"
    return "LOW TRUST"


def risk_tier(score: int) -> str:
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    return "High Risk"


def export_json(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = input_data.get("company_name", "unknown").lower().replace(" ", "_")[:20]
    path = f"{output_dir}/{slug}_{ts}.json"
    full = {
        "input": input_data,
        "analysis": result,
        "generated_at": datetime.now().isoformat(),
        "report_version": "3.0",
    }
    with open(path, "w") as f:
        json.dump(full, f, indent=2)
    return path


def export_markdown(input_data: dict, result: dict, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = input_data.get("company_name", "unknown").lower().replace(" ", "_")[:20]
    path = f"{output_dir}/{slug}_{ts}.md"

    sr = result.get("stage_results", {})
    fa = sr.get("final_assessment", {})
    ts_data = sr.get("trust_scoring", {})
    rd = sr.get("risk_detection", {})
    ea = sr.get("evidence_aggregation", {})
    cv = sr.get("cross_verification", {})

    rec = fa.get("recommendation", "CAUTION")
    cs = ts_data.get("company_score", 0)
    ds = ts_data.get("decision_maker_score", 0)
    os_ = ts_data.get("overall_score", 0)

    company = input_data.get("company_name", "—")
    dm_name = input_data.get("decision_maker_name", "—")
    dm_title = input_data.get("decision_maker_job_title", "—")
    now = datetime.now().strftime("%B %d, %Y")

    rec_display = {"PROCEED": "✅ PROCEED", "CAUTION": "⚠️ PROCEED WITH CAUTION", "REJECT": "🚫 DO NOT PROCEED"}.get(rec, rec)

    lines = [
        f"# B2B Due Diligence — Executive Intelligence Report",
        f"## {company}",
        "",
        f"> **Prepared:** {now}  ",
        f"> **Classification:** Confidential — Internal Use Only  ",
        f"> **Scope:** Full-Spectrum Verification (7-Stage Analysis)  ",
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
        f"| {company} (Organization) | {cs} / 100 | {risk_tier(cs)} |",
        f"| {dm_name} (Individual) | {ds} / 100 | {risk_tier(ds)} |",
        f"| **Combined Assessment** | **{os_} / 100** | **{risk_tier(os_)}** |",
        "",
        "> Scores are derived from multi-source verification across digital presence, professional records, and cross-referenced intelligence.",
        "",
        "---",
        "",
        "## 4. Risk Assessment",
        "",
        "### Critical Risk Indicators",
        "",
    ]

    red_flags = _clean_list(rd.get("red_flags", []))
    if red_flags:
        for f_ in red_flags:
            lines.append(f"- 🔴 {f_}")
    else:
        lines.append("- No critical risk indicators identified.")

    lines += [
        "",
        "### Areas Requiring Attention",
        "",
    ]
    yellow_flags = _clean_list(rd.get("yellow_flags", []))
    if yellow_flags:
        for f_ in yellow_flags:
            lines.append(f"- 🟡 {f_}")
    else:
        lines.append("- No significant concerns flagged.")

    lines += [
        "",
        "### Positive Indicators",
        "",
    ]
    green_signals = _clean_list(rd.get("green_signals", []))
    if green_signals:
        for f_ in green_signals:
            lines.append(f"- 🟢 {f_}")
    else:
        lines.append("- No strong positive signals identified.")

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
    if matches:
        for m in matches:
            lines.append(f"- ✓ {m}")
    else:
        lines.append("- No verified matches recorded.")

    lines += [
        "",
        "### Discrepancies & Inconsistencies",
        "",
    ]
    mismatches = _clean_list(cv.get("mismatches", []))
    if mismatches:
        for m in mismatches:
            lines.append(f"- ✕ {m}")
    else:
        lines.append("- No discrepancies detected.")

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
    if supporting:
        for e in supporting:
            lines.append(f"- {e}")
    else:
        lines.append("- Insufficient corroborating evidence available.")

    lines += [
        "",
        "### Contradicting Intelligence",
        "",
    ]
    contradicting = _clean_list(ea.get("contradicting_signals", []))
    if contradicting:
        for e in contradicting:
            lines.append(f"- {e}")
    else:
        lines.append("- No contradicting intelligence found.")

    lines += [
        "",
        "### Contextual Observations",
        "",
    ]
    neutral = _clean_list(ea.get("neutral_observations", []))
    if neutral:
        for e in neutral:
            lines.append(f"- {e}")
    else:
        lines.append("- No additional observations.")

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
        "This report is generated through an automated multi-stage intelligence pipeline combining "
        "publicly available data, digital footprint analysis, professional network verification, "
        "and cross-referenced business intelligence. All findings should be reviewed by a qualified "
        "analyst before making final business decisions.",
        "",
        "> **Confidentiality Notice:** This document contains proprietary intelligence compiled exclusively "
        "for internal due diligence purposes. Unauthorized distribution is prohibited.",
        "",
        f"*Report Reference: {slug.upper()}_{ts} | Prepared {now}*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path
