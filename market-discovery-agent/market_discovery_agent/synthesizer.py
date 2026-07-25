"""
Research Synthesizer — Phase 3.

Reads whatever secondary-research findings exist for a session (Industry,
Competitor, Community, Search Intent, Funding, Job Market, Social
Intelligence — however many of the 7 have actually been run; none are
required) plus Phase 1's problem statement, hypotheses, and success
criteria, and synthesizes them into ONE opportunity assessment: which
hypotheses are actually supported or refuted by the combined evidence, an
overall opportunity score and go/no-go recommendation, key strengths and
risks, and what's still unresolved — the things only primary research
(real customer/design-partner conversations) can answer, not more
secondary research.

Unlike the 7 secondary-research agents, this step does no web search of
its own — it reasons over evidence they already gathered. So it calls
OpenAI directly via `llm_utils.call_openai_structured` (strict Structured
Outputs, single call, no retry loop needed) rather than going through the
Perplexity+OpenAI search pipeline in `research_agents/_base.py`.
"""
from typing import List

from llm_utils import call_openai_structured
from models import HypothesisAssessment, SynthesisOutput

# Maps each possible session-state key (written by agent.py's cmd_* handlers)
# to (display label, shape). "landscape" = the Industry/Community/etc shape
# (subject + findings + summary + opportunity_signal). "competitor" = the
# Competitor Agent's per-item list shape. Add new secondary-research agents
# here so the synthesizer picks them up automatically once built.
AGENT_DISPLAY = {
    "industry_research": ("Industry Agent", "landscape"),
    "community_research": ("Community Agent", "landscape"),
    "search_intent_research": ("Search Intent Agent", "landscape"),
    "funding_research": ("Funding Agent", "landscape"),
    "job_market_research": ("Job Market Agent", "landscape"),
    "social_intelligence_research": ("Social Intelligence Agent", "landscape"),
    "competitor_research": ("Competitor Agent", "competitor"),
}

RECORD_TOOL = {
    "name": "record_synthesis",
    "description": "Record the synthesized opportunity assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "opportunity_score": {
                "type": "integer",
                "description": "0-100 overall opportunity score, synthesizing all available research. Not an average of individual agents' signals — weigh what's actually load-bearing for the idea's core premise.",
            },
            "recommendation": {
                "type": "string",
                "enum": ["Pursue", "Pursue with caution", "Pivot needed", "Do not pursue"],
                "description": "A direct go/no-go call, not a hedge.",
            },
            "executive_summary": {
                "type": "string",
                "description": "3-5 sentence plain-language synthesis of the overall opportunity, written for the founder to act on.",
            },
            "hypothesis_assessments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "hypothesis": {"type": "string"},
                        "verdict": {
                            "type": "string",
                            "enum": ["Supported", "Refuted", "Mixed", "Untested"],
                        },
                        "evidence_summary": {
                            "type": "string",
                            "description": "What the combined research actually shows for this specific hypothesis, referencing which agent(s) the evidence came from.",
                        },
                        "supporting_agents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Which secondary-research agents' findings this assessment draws on. Empty list if verdict is 'Untested'.",
                        },
                    },
                    "required": ["hypothesis", "verdict", "evidence_summary", "supporting_agents"],
                },
                "description": "One assessment per hypothesis from Phase 1 — every hypothesis must be assessed, even if the verdict is 'Untested' because no agent's research actually addressed it.",
            },
            "key_strengths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The strongest, most evidence-backed points in favor of this idea.",
            },
            "key_risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The most serious evidence-backed threats to this idea, ranked by how load-bearing they are.",
            },
            "critical_open_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Things no amount of secondary research can resolve — only primary research (real customer/design-partner conversations) can answer these.",
            },
            "recommended_next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete, specific next actions for the founder, ordered by priority.",
            },
        },
        "required": [
            "opportunity_score", "recommendation", "executive_summary",
            "hypothesis_assessments", "key_strengths", "key_risks",
            "critical_open_questions", "recommended_next_steps",
        ],
    },
}

SYSTEM_PROMPT = """You are the Research Synthesizer in a market discovery \
pipeline — the last analytical step before a founder decides whether to \
keep pursuing an idea. You do not do any new research; you reason \
critically over research that's already been gathered by up to 7 \
specialized secondary-research agents (Industry, Competitor, Community, \
Search Intent, Funding, Job Market, Social Intelligence).

Rules:
- Cross-reference agents against each other. If Community found no organic \
evidence of a problem but Industry found strong buyer-behavior data, say \
so explicitly — don't let a single agent's finding stand in for the whole \
picture, and call out contradictions between agents when they exist.
- Weight evidence by confidence. A "High confidence" finding backed by \
named sources should carry more weight than a "Low confidence" one, even \
if they point the same direction. Say plainly when the overall picture \
rests on thin evidence.
- Assess EVERY hypothesis from Phase 1, even ones no agent's research \
actually addressed — mark those "Untested" honestly rather than stretching \
an unrelated finding to cover it.
- The opportunity_score and recommendation must reflect what's actually \
load-bearing for the idea, not a simple average of the individual agents' \
signals. One fatal, well-evidenced risk (e.g. the core causal mechanism has \
zero support) should be able to drag the score down even if other signals \
are positive.
- Be the most skeptical, most honest voice in this pipeline. Your job is \
to tell the founder the truth even if it's not what they want to hear — do \
not soften a "Do not pursue" call into "Pursue with caution" to be polite.
- Distinguish clearly between what secondary research CAN settle and what \
only primary research (real conversations with real prospective customers) \
can settle — list the latter explicitly as critical_open_questions rather \
than guessing at an answer.
- If few or no secondary-research agents have been run yet, say so plainly \
in the executive_summary and mark every hypothesis "Untested" rather than \
inventing evidence that doesn't exist — a low-information synthesis is \
still useful if it's honest about being low-information.
- Call the tool exactly once with your complete synthesis."""


def format_finding(f: dict) -> str:
    sources = ", ".join(f.get("sources", [])) or "(no sources)"
    return f"- Q: {f['question']}\n  A: {f['answer']}\n  Confidence: {f['confidence']}\n  Sources: {sources}"


def format_landscape_agent(label: str, data: dict) -> str:
    subject = next(
        (v for k, v in data.items() if k.endswith("_name") or k.endswith("_landscape")),
        "",
    )
    lines = [
        f"### {label}",
        f"Subject: {subject}",
        f"Opportunity signal: {data.get('opportunity_signal', 'n/a')}",
        "",
    ]
    lines += [format_finding(f) for f in data.get("findings", [])]
    lines.append(f"\nSummary: {data.get('summary', '')}")
    return "\n".join(lines)


def format_competitor_agent(competitors: List[dict]) -> str:
    lines = [f"### Competitor Agent ({len(competitors)} competitor(s) researched)"]
    for c in competitors:
        lines.append(f"\n**{c['company_name']}** ({c.get('website_url', 'website unknown')})")
        lines.append(f"Summary: {c['summary']}")
        lines += [format_finding(f) for f in c.get("findings", [])]
    return "\n".join(lines)


def format_secondary_research(session_data: dict, none_found_message: str) -> str:
    """Renders whatever secondary-research agents exist in `session_data`
    as one text block — shared by the synthesizer's own prompt and by
    later phases (e.g. icp_discovery.py) that need the same evidence base
    as context. `none_found_message` is shown when no agent has been run."""
    lines = ["---\nSECONDARY RESEARCH FINDINGS\n---"]
    agents_present = [k for k in AGENT_DISPLAY if k in session_data]

    if not agents_present:
        lines.append(f"\n({none_found_message})")
    else:
        for key in agents_present:
            label, kind = AGENT_DISPLAY[key]
            data = session_data[key]
            if kind == "competitor":
                lines.append("\n" + format_competitor_agent(data))
            else:
                lines.append("\n" + format_landscape_agent(label, data))

    return "\n".join(lines)


def format_synthesis(synthesis: dict) -> str:
    """Renders a saved Phase 3 synthesis (if one exists) as a text block —
    shared with later phases that should build on its verdict rather than
    re-deriving it from raw findings."""
    lines = [
        "---\nRESEARCH SYNTHESIS (Phase 3)\n---",
        f"Recommendation: {synthesis['recommendation']}  (opportunity score: {synthesis['opportunity_score']}/100)",
        f"\n{synthesis['executive_summary']}\n",
        "Hypothesis verdicts:",
    ]
    for h in synthesis["hypothesis_assessments"]:
        lines.append(f"- [{h['verdict']}] {h['hypothesis']}\n    {h['evidence_summary']}")
    if synthesis.get("key_risks"):
        lines.append("\nKey risks:")
        lines += [f"- {r}" for r in synthesis["key_risks"]]
    return "\n".join(lines)


def _build_user_message(session_data: dict) -> str:
    phase1 = session_data["phase1_output"]
    lines = [
        f"Problem statement:\n{phase1['problem_statement']}\n",
        "Hypotheses to assess (assess EVERY one, even if untested):",
    ]
    lines += [f"- {h}" for h in phase1["initial_hypotheses"]]
    lines.append("\nSuccess criteria the founder defined (context only, not to be assessed individually):")
    lines += [f"- {s}" for s in phase1["success_criteria"]]
    lines.append("\n\n" + format_secondary_research(
        session_data, none_found_message="No secondary-research agents have been run yet for this session — synthesize from Phase 1 alone."
    ))
    return "\n".join(lines)


def run_synthesis(session_data: dict) -> SynthesisOutput:
    """Runs the Research Synthesizer to completion for one session's data."""
    user_message = _build_user_message(session_data)
    result = call_openai_structured(
        system=SYSTEM_PROMPT,
        user_message=user_message,
        tool_name="record_synthesis",
        input_schema=RECORD_TOOL["input_schema"],
    )
    assessments = [HypothesisAssessment(**h) for h in result["hypothesis_assessments"]]
    return SynthesisOutput(
        opportunity_score=result["opportunity_score"],
        recommendation=result["recommendation"],
        executive_summary=result["executive_summary"],
        hypothesis_assessments=assessments,
        key_strengths=result["key_strengths"],
        key_risks=result["key_risks"],
        critical_open_questions=result["critical_open_questions"],
        recommended_next_steps=result["recommended_next_steps"],
    )
