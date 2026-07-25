"""
ICP Discovery — Phase 4.

The first phase that reasons about WHO to sell to, not just whether the
idea is viable. Follows a 9-step ICP framework end to end:

    Market -> Industry -> Company (Firmographics) -> Technology Stack
    (Technographics) -> Buyer Persona -> Pain Points -> Buying Signals
    -> Exclusion Criteria -> ICP Scoring & Prioritization
    -> Qualified Account Spec

Steps 1-7 are per-segment (`ICPProfile`, one for `primary_icp` and 0-2 for
`secondary_icps`). Steps 8-9 apply across all segments at once, so they
live on `ICPDiscoveryOutput` instead: `exclusion_criteria` (who NOT to
target), `scoring_rubric` (weighted, checkable criteria), and
`qualified_account_spec` (Step 9's terminal deliverable) — a concrete
enough filter spec that a founder can paste directly into Clay, Apollo, or
LinkedIn Sales Navigator to manually build the real qualified-account list.
This pipeline does not call those APIs itself.

Unlike Phase 3's synthesizer (pure reasoning, no search), ICP Discovery
genuinely benefits from live grounding: firmographic/technographic/buyer
norms for a given price point and category are real-world facts, easy to
get wrong from training data alone. So it runs a two-step pipeline like
the 7 secondary-research agents:

  1. PERPLEXITY searches for EXTERNAL grounding only — typical buyer
     roles/budget-authority, typical tech stacks, buying triggers, and
     price-sensitivity norms for this kind of product/category. It does
     NOT re-derive anything already established internally (that would
     waste a search on facts already in hand).
  2. OPENAI structures the final ICP using BOTH that fresh external
     grounding AND everything already known internally: the problem
     statement, the founder's own hypotheses, the Phase 3 synthesis
     verdict (if one exists), and the secondary-research agents' findings
     (if any have been run) — via `research_agents._base.run_research_pipeline`'s
     `extra_context` parameter, which reaches OpenAI's structuring step
     without being sent to Perplexity's search step.

Works with a partial pipeline: Phase 3 synthesis and the 7 secondary-
research agents are all optional context, not requirements — only
Phase 1's problem statement and hypotheses are required.
"""
from typing import List, Optional

from models import ICPProfile, ICPDiscoveryOutput, ScoringCriterion, QualifiedAccountSpec
from research_agents._base import run_research_pipeline
from synthesizer import format_secondary_research, format_synthesis

DEFAULT_QUESTIONS = [
    "What company stage/size/industry segment is most likely to feel this problem acutely AND have budget to solve it?",
    "What job titles/roles typically hold both the pain and the budget authority to buy a solution like this?",
    "What tools/platforms (CRM, sales engagement, data stack, etc.) do companies in this segment typically already have in place, and what does that signal about fit — a gap this product fills, or a competing tool already occupying the budget?",
    "What triggers or workflow moments typically prompt a purchase decision for tools solving this kind of problem?",
    "What price sensitivity or budget norms exist for tools at this price point in this segment?",
    "Are there recognizable sub-segments (by company stage, vertical, or buyer role) that show meaningfully different fit for this kind of solution?",
]

DEFAULT_SOURCES = [
    "G2/Capterra buyer-persona data for comparable tools",
    "Crunchbase/company-size distributions for comparable customers",
    "Vendor case studies naming their actual customer segment",
    "LinkedIn job postings/titles at companies buying comparable tools",
    "Pricing-page tiering of comparable tools (signals budget norms)",
    "BuiltWith/Wappalyzer-style tech-stack data or job postings mentioning specific tools (signals technographic fit)",
]

ICP_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "segment_name": {
            "type": "string",
            "description": "A short label (under 12 words) naming this segment precisely — e.g. 'Seed-to-Series A B2B SaaS founder-led marketers'. Not a full sentence.",
        },
        "market": {
            "type": "string",
            "description": "The broader market/category this segment buys within (e.g. 'B2B sales engagement software') — TAM context, not the specific vertical.",
        },
        "industry": {
            "type": "string",
            "description": "The specific industry vertical(s) this segment belongs to (e.g. 'B2B SaaS', 'Healthcare IT', 'Fintech'). Be specific, not 'technology'.",
        },
        "firmographics": {
            "type": "string",
            "description": "Company stage, size range, and geography that define this segment.",
        },
        "technographics": {
            "type": "string",
            "description": "Tools/platforms this segment typically already has in place (CRM, sales engagement, data stack, etc.), and what that signals about fit — a gap this product fills, or a competing tool already occupying the budget.",
        },
        "buyer_persona": {
            "type": "string",
            "description": "The actual buyer's role/title, seniority, and whether they personally hold both the pain and the budget authority (or need to go through someone else).",
        },
        "pain_points": {
            "type": "string",
            "description": "The pain in THEIR words (not the founder's framing) — distinct from the trigger event that makes them act on it.",
        },
        "buying_signals": {
            "type": "string",
            "description": "The specific event/moment that triggers a buying decision, plus budget/willingness-to-pay norms for this segment at this price point — grounded in external research where possible, marked speculative where not.",
        },
        "evidence": {
            "type": "string",
            "description": "What research (external grounding AND/OR internal Phase 1-3 findings) actually supports this segment being viable. Reference which source it came from.",
        },
        "confidence": {
            "type": "string",
            "enum": ["High", "Medium", "Low"],
        },
        "fit_score": {
            "type": "integer",
            "description": "0-100 score for how well this segment fits/prioritizes against the scoring rubric recorded alongside it. Higher = stronger, more evidence-backed fit.",
        },
        "fit_score_rationale": {
            "type": "string",
            "description": "Which scoring-rubric criteria drove this score, and why — reference the rubric's criteria by name.",
        },
    },
    "required": [
        "segment_name", "market", "industry", "firmographics", "technographics",
        "buyer_persona", "pain_points", "buying_signals", "evidence", "confidence",
        "fit_score", "fit_score_rationale",
    ],
}

RECORD_TOOL = {
    "name": "record_icp_discovery",
    "description": "Record the discovered Ideal Customer Profile, its scoring rubric, and the qualified-account spec.",
    "input_schema": {
        "type": "object",
        "properties": {
            "primary_icp": ICP_PROFILE_SCHEMA,
            "secondary_icps": {
                "type": "array",
                "items": ICP_PROFILE_SCHEMA,
                "description": "0-2 other genuinely viable segments, ONLY if evidence actually supports them as distinct from the primary ICP. Empty list if there's really just one clear segment — don't invent secondary segments to fill space.",
            },
            "exclusion_criteria": {
                "type": "string",
                "description": "The clearest disqualifying characteristics — who looks superficially similar to the ICP but should NOT be targeted, and why (wrong stage, no budget authority, pain too weak, wrong tech stack, etc).",
            },
            "scoring_rubric": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion": {
                            "type": "string",
                            "description": "A specific, checkable criterion, e.g. 'Company has 20-200 employees', 'Uses a competing tool today', 'Posted a relevant job in the last 90 days'.",
                        },
                        "weight": {
                            "type": "integer",
                            "description": "0-100 — how much this criterion should count toward a candidate account's total score. All criteria across the rubric should sum to roughly 100.",
                        },
                        "how_to_score": {
                            "type": "string",
                            "description": "Concretely how to check/award this criterion for a real candidate account — what to look up, and where.",
                        },
                    },
                    "required": ["criterion", "weight", "how_to_score"],
                },
                "description": "4-8 weighted, checkable criteria a founder can use to score real candidate accounts pulled into a tool like Clay or Apollo — concrete enough to apply by hand, not vague heuristics. Weights should sum to roughly 100.",
            },
            "qualified_account_spec": {
                "type": "object",
                "properties": {
                    "firmographic_filters": {
                        "type": "string",
                        "description": "Concrete firmographic filters to search/filter by (industry, size range, stage, geography) — phrased so they map directly onto Clay/Apollo/LinkedIn Sales Navigator filter fields.",
                    },
                    "technographic_filters": {
                        "type": "string",
                        "description": "Concrete technographic filters/signals to search for (tools/platforms in use) that indicate fit.",
                    },
                    "buyer_titles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific job titles to search for as the buyer-persona contact within a qualified account.",
                    },
                    "buying_signal_filters": {
                        "type": "string",
                        "description": "Concrete, searchable buying-signal filters (e.g. funding events, headcount growth, specific job postings, tech adoption) to prioritize accounts showing active intent.",
                    },
                    "minimum_fit_score": {
                        "type": "integer",
                        "description": "Only pursue accounts scoring at/above this threshold (0-100) on the scoring rubric above.",
                    },
                },
                "required": [
                    "firmographic_filters", "technographic_filters", "buyer_titles",
                    "buying_signal_filters", "minimum_fit_score",
                ],
                "description": "A ready-to-use spec for manually building a qualified-account list in Clay/Apollo/Sales Navigator — this pipeline does not call those tools itself.",
            },
            "summary": {
                "type": "string",
                "description": "3-5 sentence plain-language summary of who this idea should actually sell to, written for the founder to act on.",
            },
            "icp_confidence": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "Overall confidence in this ICP given available evidence — Low if it rests mostly on the founder's assumptions rather than external grounding or secondary research.",
            },
            "recommended_validation_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete next actions to validate or refine this ICP through real conversations with prospective customers matching the profile — not more secondary research.",
            },
        },
        "required": [
            "primary_icp", "secondary_icps", "exclusion_criteria", "scoring_rubric",
            "qualified_account_spec", "summary", "icp_confidence", "recommended_validation_steps",
        ],
    },
}

STRUCTURING_INSTRUCTIONS = """You are the ICP Discovery agent in a market \
discovery pipeline, following a 9-step framework: Market -> Industry -> \
Firmographics -> Technographics -> Buyer Persona -> Pain Points -> Buying \
Signals -> Exclusion Criteria -> ICP Scoring & Prioritization, ending in a \
Qualified Account spec. Your job is to define a concrete, actionable Ideal \
Customer Profile — not a vague persona sketch.

You'll be given: (1) the business's problem statement and hypotheses, \
(2) if available, a Phase 3 research synthesis with a go/no-go verdict \
and per-hypothesis assessments, (3) if available, findings from up to 7 \
secondary-research agents, and (4) fresh external research on buyer/\
segment/tech-stack norms for this category, just gathered via web search.

Rules:
- Ground the ICP in evidence wherever it exists — prefer what the \
external research or secondary-research agents actually found over the \
founder's own untested assumptions. If a synthesis exists and refuted or \
marked a hypothesis about the customer as "Untested," reflect that \
honestly in confidence levels rather than ignoring it.
- Be specific. "Early-stage B2B SaaS founders" is not specific enough — \
say what stage, what size, what they've already tried, who exactly holds \
the budget, what tools they already run.
- The buyer persona must distinguish between who FEELS the pain and who \
holds BUDGET AUTHORITY — for many B2B products these are different \
people, and conflating them produces an ICP that can't actually convert.
- Pain points and buying signals are DIFFERENT fields: pain_points is the \
ongoing frustration in the buyer's own words; buying_signals is the \
specific event/moment/intent signal (plus budget norms) that turns that \
frustration into an active purchase decision right now.
- Define exclusion_criteria explicitly and specifically — this is often \
more useful to a founder than the ICP itself, since it prevents wasted \
effort on superficially-similar-but-wrong-fit prospects.
- The scoring_rubric must be concrete and checkable — a founder should be \
able to look at a real company/contact and award points for each \
criterion without guessing. Weights should sum to roughly 100.
- Each profile's fit_score is that segment's own score against the \
rubric — use it to justify why primary_icp outranks any secondary_icps, \
not just as a decoration.
- qualified_account_spec is the terminal deliverable: phrase every field \
so it could be pasted directly into Clay's or Apollo's free-tier search/\
filter UI or LinkedIn Sales Navigator — concrete filter values, not \
prose description of the ICP restated.
- Only include secondary_icps if evidence genuinely supports a second \
distinct segment — an empty list is a valid, honest answer.
- If the overall evidence base is thin (little/no secondary research, no \
synthesis, mostly founder assumption), say so plainly and mark \
icp_confidence "Low" rather than presenting a guess with false confidence.
- Call the tool exactly once with your complete ICP."""


def _build_research_prompt(problem_statement: str, questions: List[str], suggested_sources: List[str]) -> str:
    lines = [
        "You are researching EXTERNAL, real-world buyer/segment/tech-stack "
        "benchmarks for a business idea — NOT the idea's internal validation "
        "(that's handled separately). Focus only on facts about how buyers in "
        "this general category behave: typical company profile, typical tech "
        "stack, typical buyer role/budget authority, typical buying triggers, "
        "and typical price sensitivity — grounded in comparable/adjacent "
        "products, not this specific idea.",
        "",
        f"Problem statement (for category context only):\n{problem_statement}\n",
        "Questions to answer:",
    ]
    lines += [f"- {q}" for q in questions]
    lines.append("\nPrioritize these kinds of sources: " + ", ".join(suggested_sources))
    lines.append(
        "\nAnswer each question directly and cite your sources. If you can't find "
        "a confident answer, say so plainly rather than guessing."
    )
    return "\n".join(lines)


def run_icp_discovery(
    session_data: dict,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
) -> ICPDiscoveryOutput:
    """Runs ICP Discovery to completion for one session's data. Requires
    `phase1_output`; Phase 3 synthesis and secondary-research findings are
    used as context if present, but neither is required."""
    phase1 = session_data["phase1_output"]
    questions = questions or DEFAULT_QUESTIONS
    suggested_sources = suggested_sources or DEFAULT_SOURCES

    research_prompt = _build_research_prompt(phase1["problem_statement"], questions, suggested_sources)

    context_parts = [
        f"Problem statement:\n{phase1['problem_statement']}\n",
        "Founder's hypotheses:",
    ]
    context_parts += [f"- {h}" for h in phase1["initial_hypotheses"]]

    if "synthesis" in session_data:
        context_parts.append("\n" + format_synthesis(session_data["synthesis"]))
    else:
        context_parts.append("\n(No Phase 3 synthesis has been run yet for this session.)")

    context_parts.append("\n" + format_secondary_research(
        session_data,
        none_found_message="No secondary-research agents have been run yet for this session.",
    ))
    extra_context = "\n".join(context_parts)

    result = run_research_pipeline(
        record_tool=RECORD_TOOL,
        research_prompt=research_prompt,
        structuring_context=STRUCTURING_INSTRUCTIONS,
        extra_context=extra_context,
    )

    primary_icp = ICPProfile(**result["primary_icp"])
    secondary_icps = [ICPProfile(**s) for s in result["secondary_icps"]]
    scoring_rubric = [ScoringCriterion(**c) for c in result["scoring_rubric"]]
    qualified_account_spec = QualifiedAccountSpec(**result["qualified_account_spec"])
    return ICPDiscoveryOutput(
        primary_icp=primary_icp,
        secondary_icps=secondary_icps,
        exclusion_criteria=result["exclusion_criteria"],
        scoring_rubric=scoring_rubric,
        qualified_account_spec=qualified_account_spec,
        summary=result["summary"],
        icp_confidence=result["icp_confidence"],
        recommended_validation_steps=result["recommended_validation_steps"],
    )
