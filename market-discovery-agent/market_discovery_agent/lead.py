"""
Lead — owns the project's output convention and is the single place every
phase/subagent (Business Understanding, Research Plan, Industry Agent,
Competitor Agent, Community Agent, ...) reports its deliverable through.

THE RULE (do not duplicate this elsewhere — call save_output instead):
  All human/machine-readable output lives under `output/`, nowhere else.
  Each phase/agent gets its own subfolder, named by its slug, and writes
  a matching pair of files named after the session ID:

      output/<agent-slug>/<session_id>.md    (human-readable report)
      output/<agent-slug>/<session_id>.json  (same data, machine-readable)

  Example: the Industry Agent's report for session <id> lands at
      output/industry-research/<id>.md
      output/industry-research/<id>.json

`sessions/<session_id>.json` is separate and untouched by this module —
that file is internal pipeline state (each phase reads what the previous
phase wrote there). `output/` is the deliverable copy, organized for a
human (or a downstream tool) to read one agent's work at a time.

When you build a new subagent, add its name -> slug mapping to AGENT_SLUGS
below, then call save_output(...) at the end of its command handler. Don't
invent a new folder-naming scheme per agent.
"""
import json
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Canonical slug per phase/agent so every writer lands in the same place.
# Add new secondary-research agents here as they're built.
AGENT_SLUGS = {
    "Business Understanding": "business-understanding",
    "Research Plan": "research-plan",
    "Industry Agent": "industry-research",
    "Competitor Agent": "competitor-research",
    "Community Agent": "community-research",
    "Search Intent Agent": "search-intent-research",
    "Funding Agent": "funding-research",
    "Job Market Agent": "job-market-research",
    "Social Intelligence Agent": "social-intelligence-research",
    "Research Synthesizer": "research-synthesis",
    "ICP Discovery Agent": "icp-discovery",
    "Market Sizing Agent": "market-sizing",
    "Target Account Agent": "target-accounts",
    "Lookalike Account Agent": "lookalike-accounts",
    "Customer Discovery Agent": "customer-discovery",
    "Validation Agent": "validation",
    "GTM Recommendation Agent": "gtm-recommendation",
}


def slug_for(agent_name: str) -> str:
    """Canonical slug for an agent/phase name — falls back to a slugified
    version of the name itself so an unregistered agent still works
    (but prefer registering it in AGENT_SLUGS)."""
    return AGENT_SLUGS.get(agent_name) or re.sub(r"[^a-z0-9]+", "-", agent_name.lower()).strip("-")


def save_output(agent_name: str, session_id: str, title: str, markdown_body: str, data: dict) -> tuple:
    """
    Writes one agent's deliverable to output/<agent-slug>/<session_id>.{md,json}.

    `markdown_body` is the report content (no top-level title needed — this
    function adds a title heading + session ID header for you).
    `data` is the raw structured data, dumped as-is to the .json sibling.

    Returns (md_path, json_path).
    """
    slug = slug_for(agent_name)
    folder = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)

    md_path = os.path.join(folder, f"{session_id}.md")
    json_path = os.path.join(folder, f"{session_id}.json")

    header = f"# {title}\n\nSession ID: `{session_id}`\n\n---\n\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(header + markdown_body.strip() + "\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return md_path, json_path


# --------------------------------------------------------------------------
# Markdown renderers — one per phase/agent shape. Kept here (not in agent.py
# or the individual research_agents modules) so every writer produces
# consistently-formatted reports.
# --------------------------------------------------------------------------

def render_business_understanding_md(founder_input: dict, phase1: dict) -> str:
    lines = ["## Founder Input", ""]
    lines.append(f"**Product idea:**\n{founder_input['product_idea']}\n")
    lines.append(f"**Vision:**\n{founder_input['vision']}\n")
    lines.append("**Features:**")
    lines += [f"- {f}" for f in founder_input["features"]]
    lines.append("")
    lines.append("**Assumptions:**")
    lines += [f"- {a}" for a in founder_input["assumptions"]]
    lines.append("")
    lines.append(f"**Founder knowledge:**\n{founder_input['founder_knowledge']}")
    lines.append("\n## Phase 1 Output\n")
    lines.append("### Problem Statement\n")
    lines.append(phase1["problem_statement"])
    lines.append("\n### Initial Hypotheses\n")
    lines += [f"{i}. {h}" for i, h in enumerate(phase1["initial_hypotheses"], 1)]
    lines.append("\n### Success Criteria\n")
    lines += [f"{i}. {s}" for i, s in enumerate(phase1["success_criteria"], 1)]
    return "\n".join(lines)


def render_research_plan_md(plan: dict) -> str:
    lines = ["## Priority Order", ""]
    lines += [f"{i}. {name}" for i, name in enumerate(plan["priority_order"], 1)]

    for brief in plan["agent_briefs"]:
        lines.append(f"\n## {brief['agent_name']}\n")
        lines.append(f"**Objective:** {brief['objective']}\n")
        lines.append("**Questions:**")
        for q in brief["questions"]:
            lines.append(f"- {q['question']}")
            lines.append(f"  *Why:* {q['rationale']}")
        lines.append("\n**Suggested sources:** " + ", ".join(brief["suggested_sources"]))

    if plan.get("open_questions_for_founder"):
        lines.append("\n## Open Questions Only the Founder Can Answer\n")
        lines += [f"- {q}" for q in plan["open_questions_for_founder"]]

    return "\n".join(lines)


def render_research_findings_md(agent_label: str, subject_name: str, findings: list,
                                 summary: str, opportunity_signal: str,
                                 objective: str = None) -> str:
    """Generic renderer for any secondary-research agent whose output is
    shaped like IndustryResearchOutput: a subject name, a list of
    {question, answer, confidence, sources} findings, a summary, and an
    opportunity signal. Reuse this for Competitor/Community/etc agents
    that share the same shape rather than writing a new renderer."""
    lines = [f"## {agent_label}: {subject_name}", ""]
    if objective:
        lines.append(f"**Objective:** {objective}\n")

    lines.append("### Findings\n")
    for f in findings:
        lines.append(f"**Q: {f['question']}**\n")
        lines.append(f"{f['answer']}\n")
        lines.append(f"- Confidence: {f['confidence']}")
        sources = ", ".join(f["sources"]) if f["sources"] else "(none found)"
        lines.append(f"- Sources: {sources}\n")

    lines.append(f"### Summary\n\n{summary}\n")
    lines.append(f"**Opportunity signal:** {opportunity_signal}")
    return "\n".join(lines)


def render_competitor_research_md(competitors: list) -> str:
    """Renders one Competitor Agent report covering ALL competitors
    researched in this run (each competitor is researched individually via
    run_competitor_research, but they're reported together as one deliverable
    per session, per the output convention)."""
    lines = [f"Competitors researched: {len(competitors)}\n"]
    for c in competitors:
        lines.append(f"## {c['company_name']}\n")
        lines.append(f"- LinkedIn: {c['linkedin_url']}")
        lines.append(f"- Website: {c['website_url'] or '(not found)'}\n")
        lines.append("### Findings\n")
        for f in c["findings"]:
            lines.append(f"**Q: {f['question']}**\n")
            lines.append(f"{f['answer']}\n")
            lines.append(f"- Confidence: {f['confidence']}")
            sources = ", ".join(f["sources"]) if f["sources"] else "(none found)"
            lines.append(f"- Sources: {sources}\n")
        lines.append(f"### Summary\n\n{c['summary']}\n")
    return "\n".join(lines)


def render_synthesis_md(synthesis: dict) -> str:
    lines = [
        f"## Recommendation: {synthesis['recommendation']}",
        f"**Opportunity score:** {synthesis['opportunity_score']}/100\n",
        f"{synthesis['executive_summary']}\n",
        "## Hypothesis Assessments\n",
    ]
    for h in synthesis["hypothesis_assessments"]:
        lines.append(f"**[{h['verdict']}]** {h['hypothesis']}\n")
        lines.append(f"{h['evidence_summary']}\n")
        agents = ", ".join(h["supporting_agents"]) if h["supporting_agents"] else "(none)"
        lines.append(f"*Evidence from: {agents}*\n")

    lines.append("## Key Strengths\n")
    lines += [f"- {s}" for s in synthesis["key_strengths"]]

    lines.append("\n## Key Risks\n")
    lines += [f"- {r}" for r in synthesis["key_risks"]]

    lines.append("\n## Critical Open Questions (primary research needed)\n")
    lines += [f"- {q}" for q in synthesis["critical_open_questions"]]

    lines.append("\n## Recommended Next Steps\n")
    lines += [f"{i}. {s}" for i, s in enumerate(synthesis["recommended_next_steps"], 1)]

    return "\n".join(lines)


def _render_icp_profile_md(profile: dict) -> str:
    lines = [
        f"### {profile['segment_name']}  *(confidence: {profile['confidence']}, fit score: {profile['fit_score']}/100)*\n",
        f"**Market:** {profile['market']}\n",
        f"**Industry:** {profile['industry']}\n",
        f"**Firmographics:** {profile['firmographics']}\n",
        f"**Technographics:** {profile['technographics']}\n",
        f"**Buyer persona:** {profile['buyer_persona']}\n",
        f"**Pain points:** {profile['pain_points']}\n",
        f"**Buying signals:** {profile['buying_signals']}\n",
        f"**Evidence:** {profile['evidence']}\n",
        f"**Fit score rationale:** {profile['fit_score_rationale']}",
    ]
    return "\n".join(lines)


def render_icp_discovery_md(icp: dict) -> str:
    lines = [
        f"## Overall ICP Confidence: {icp['icp_confidence']}\n",
        f"{icp['summary']}\n",
        "## Primary ICP\n",
        _render_icp_profile_md(icp["primary_icp"]),
    ]

    if icp["secondary_icps"]:
        lines.append("\n## Secondary ICPs\n")
        for profile in icp["secondary_icps"]:
            lines.append(_render_icp_profile_md(profile) + "\n")

    lines.append("\n## Exclusion Criteria — Who NOT to Target\n")
    lines.append(icp["exclusion_criteria"])

    lines.append("\n## ICP Scoring Rubric\n")
    for c in icp["scoring_rubric"]:
        lines.append(f"- **{c['criterion']}** (weight: {c['weight']}) — {c['how_to_score']}")

    spec = icp["qualified_account_spec"]
    lines.append("\n## Qualified Account Spec — paste into Clay / Apollo / Sales Navigator\n")
    lines.append(f"**Firmographic filters:** {spec['firmographic_filters']}\n")
    lines.append(f"**Technographic filters:** {spec['technographic_filters']}\n")
    lines.append(f"**Buyer titles to search:** {', '.join(spec['buyer_titles'])}\n")
    lines.append(f"**Buying-signal filters:** {spec['buying_signal_filters']}\n")
    lines.append(f"**Minimum fit score to pursue:** {spec['minimum_fit_score']}/100")

    lines.append("\n\n## Recommended Validation Steps\n")
    lines += [f"{i}. {s}" for i, s in enumerate(icp["recommended_validation_steps"], 1)]

    return "\n".join(lines)


def _render_market_size_estimate_md(label: str, estimate: dict) -> str:
    lines = [
        f"### {label}: {estimate['value_usd']}  *(confidence: {estimate['confidence']})*\n",
        f"**Timeframe:** {estimate['timeframe']}\n",
        f"**Methodology:** {estimate['methodology']}\n",
        "**Key assumptions:**",
    ]
    lines += [f"- {a}" for a in estimate["key_assumptions"]]
    if estimate["sources"]:
        lines.append("\n**Sources:** " + ", ".join(estimate["sources"]))
    return "\n".join(lines)


def render_market_sizing_md(sizing: dict) -> str:
    lines = [
        f"## Overall Confidence: {sizing['overall_confidence']}\n",
        f"{sizing['summary']}\n",
        _render_market_size_estimate_md("TAM", sizing["tam"]),
        "",
        _render_market_size_estimate_md("SAM", sizing["sam"]),
        f"\n**How SAM was narrowed from TAM:** {sizing['sam_narrowing_criteria']}\n",
        _render_market_size_estimate_md("SOM", sizing["som"]),
        f"\n**Why this capture rate is realistic:** {sizing['som_capture_rationale']}",
    ]
    return "\n".join(lines)


def render_target_accounts_md(result: dict) -> str:
    lines = [
        f"**Target location:** {result['target_location'] or '(none set)'}\n",
        f"{result['summary']}\n",
    ]

    if result["accounts"]:
        lines.append("## Target Accounts\n")
        for a in result["accounts"]:
            lines.append(f"### {a['company_name']}  *(fit score: {a['fit_score']}/100)*\n")
            lines.append(f"**LinkedIn:** {a['linkedin_url']}\n")
            lines.append(f"**Website:** {a['website_url']}\n")
            lines.append(f"**Industry:** {a['industry']}  |  **Employees:** {a['employee_count']}\n")
            lines.append(f"**Why it qualifies:** {a['fit_score_rationale']}\n")
            lines.append("**Key matching signals:**")
            lines += [f"- {s}" for s in a["key_matching_signals"]]
            lines.append("")
    else:
        lines.append("## Target Accounts\n\nNone could be verified via a real LinkedIn scrape this run.\n")

    if result["unverified_candidates"]:
        lines.append("## Unverified Candidates (dropped, not recommended)\n")
        lines += [f"- {name}" for name in result["unverified_candidates"]]

    return "\n".join(lines)


def render_customer_discovery_md(plan: dict) -> str:
    lines = [f"{plan['summary']}\n", "## Discovery Questions\n"]
    for q in plan["discovery_questions"]:
        lines.append(f"**Q: {q['question']}**\n")
        lines.append(f"- Tests: {q['tests']}")
        lines.append(f"- Listen for: {q['what_to_listen_for']}\n")

    lines.append("## Recruiting Channels\n")
    for c in plan["recruiting_channels"]:
        lines.append(f"**{c['channel']}**\n")
        lines.append(f"- Why: {c['why_this_channel']}")
        lines.append(f"- Evidence: {c['evidence']}\n")

    lines.append("## Outreach Message Template\n")
    lines.append(f"> {plan['outreach_message_template']}\n")

    lines.append("## Screening Criteria\n")
    lines += [f"- {s}" for s in plan["screening_criteria"]]

    lines.append("\n## Success Criteria\n")
    lines.append(plan["success_criteria"])

    lines.append("\n## Recommended Next Steps\n")
    lines += [f"{i}. {s}" for i, s in enumerate(plan["recommended_next_steps"], 1)]

    return "\n".join(lines)


def render_validation_md(validation: dict, interviews: list) -> str:
    met = "Yes" if validation["success_criteria_met"] else "No"
    lines = [
        f"## Verdict: {validation['overall_verdict']}",
        f"**Success criteria met:** {met}\n",
        f"{validation['success_criteria_assessment']}\n",
        f"{validation['summary']}\n",
        "## Hypothesis Validations\n",
    ]
    for h in validation["hypothesis_validations"]:
        lines.append(f"**[{h['verdict']}]** {h['hypothesis_or_question']}\n")
        lines.append(f"{h['evidence_summary']}\n")
        lines.append(f"*Supporting interviews: {h['supporting_interview_count']}*\n")

    lines.append("## Notable Patterns\n")
    lines += [f"- {p}" for p in validation["notable_patterns"]]

    lines.append("\n## Red Flags\n")
    lines += [f"- {r}" for r in validation["red_flags"]] if validation["red_flags"] else ["(none noted)"]

    lines.append("\n## Recommended Next Steps\n")
    lines += [f"{i}. {s}" for i, s in enumerate(validation["recommended_next_steps"], 1)]

    lines.append(f"\n## Interviews Analyzed ({len(interviews)})\n")
    for i, interview in enumerate(interviews, 1):
        lines.append(f"### Interview {i}: {interview['interviewee_label']}\n")
        lines.append(f"Fits ICP: {interview['fits_icp']}\n")
        lines.append(f"Notes:\n{interview['notes']}\n")

    return "\n".join(lines)


def render_gtm_recommendation_md(gtm: dict) -> str:
    lines = [
        f"## Primary Motion: {gtm['primary_motion']}  *(confidence: {gtm['confidence']})*\n",
        f"{gtm['summary']}\n",
        "## Positioning Statement\n",
        f"> {gtm['positioning_statement']}\n",
        "## Messaging Pillars\n",
    ]
    lines += [f"- {m}" for m in gtm["messaging_pillars"]]

    lines.append("\n## Primary Channels\n")
    for c in gtm["primary_channels"]:
        lines.append(f"### {c['channel']}\n")
        lines.append(f"- Why: {c['why_this_channel']}")
        lines.append(f"- Evidence: {c['evidence']}")
        lines.append("- First actions:")
        lines += [f"  {i}. {a}" for i, a in enumerate(c["first_actions"], 1)]
        lines.append("")

    lines.append("## Pricing & Packaging\n")
    lines.append(gtm["pricing_and_packaging"])

    lines.append("\n## Launch Sequence\n")
    lines += [f"{i}. {s}" for i, s in enumerate(gtm["launch_sequence"], 1)]

    lines.append("\n## Metrics to Track\n")
    lines += [f"- {m}" for m in gtm["metrics_to_track"]]

    lines.append("\n## Key Risks\n")
    lines += [f"- {r}" for r in gtm["key_risks"]]

    lines.append("\n## Recommended Next Steps\n")
    lines += [f"{i}. {s}" for i, s in enumerate(gtm["recommended_next_steps"], 1)]

    return "\n".join(lines)
