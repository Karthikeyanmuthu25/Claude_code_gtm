"""
GTM Recommendation — Phase 7 (final phase).

Turns everything learned across the pipeline into a concrete go-to-market
plan: which motion to run, sharpened positioning, a specific channel mix,
pricing/packaging, an ordered launch sequence, and the metrics that would
actually tell the founder it's working.

Like ICP Discovery and Customer Discovery, this benefits from live
grounding: channel-effectiveness norms, pricing/packaging benchmarks, and
launch-playbook patterns for a given category are real-world facts, easy
to get wrong from training data alone. So it runs the same two-step
pipeline:

  1. PERPLEXITY searches for EXTERNAL grounding only — which GTM motions
     and channels actually work for comparable products/categories, pricing
     and packaging norms at this price point/segment, and founder-led
     launch-playbook patterns (e.g. audit/free-tool lead magnets,
     community-led launches). It does NOT re-derive anything already
     established internally.
  2. OPENAI structures the final plan using BOTH that fresh external
     grounding AND everything already known internally: the problem
     statement and hypotheses, the Phase 3 synthesis verdict, the Phase 4
     ICP, secondary-research findings (especially Competitor pricing/
     channels and Community-named channels), the Phase 5 customer
     discovery plan, and — the strongest signal available, if it
     exists — the Phase 6 validation results from real interviews.

Works with a partial pipeline: only Phase 1's problem statement and
hypotheses are required. Everything else (synthesis, ICP, secondary
research, customer discovery, validation) sharpens the plan if present
but isn't required — the summary says plainly how much of this rests on
real evidence versus category-level grounding alone.
"""
from typing import List, Optional

from models import GTMChannelRecommendation, GTMRecommendationOutput
from research_agents._base import run_research_pipeline
from synthesizer import format_secondary_research, format_synthesis
from validation import format_interviews

DEFAULT_QUESTIONS = [
    "Which GTM motions (content-led, community-led, outbound, paid, partnerships, product-led/free-tool-led) actually work best for products at this price point and buyer segment?",
    "What pricing and packaging models (per-seat, flat monthly, usage-based, audit-then-subscribe) are typical for comparable tools, and what conversion benchmarks exist for free-to-paid funnels in this category?",
    "What launch-playbook patterns (free audits/scorecards, founder-led LinkedIn/content, communities, cold outreach) have worked for early-stage products targeting a similar buyer, and what results have they reported?",
    "What messaging and positioning angles have resonated for comparable products, and which have fallen flat or been dismissed as vanity/gimmick?",
]

DEFAULT_SOURCES = [
    "Case studies/blog posts from comparable early-stage products' launches",
    "Pricing pages and public packaging of comparable tools",
    "Indie Hackers / founder community launch retrospectives",
    "GTM/marketing newsletters and playbooks for this category",
    "Producthunt launches and their reported traction for comparable tools",
]

CHANNEL_SCHEMA = {
    "type": "object",
    "properties": {
        "channel": {
            "type": "string",
            "description": "A specific, named channel/motion instantiation — e.g. 'Founder LinkedIn posts + free AI-visibility audit lead magnet', not a generic category like 'content marketing'.",
        },
        "why_this_channel": {"type": "string"},
        "evidence": {
            "type": "string",
            "description": "What supports this channel actually working for THIS ICP/category — external research and/or internal findings (Community Agent, Customer Discovery, Validation).",
        },
        "first_actions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "2-4 concrete, specific actions to kick this channel off in the next 2 weeks.",
        },
    },
    "required": ["channel", "why_this_channel", "evidence", "first_actions"],
}

RECORD_TOOL = {
    "name": "record_gtm_recommendation",
    "description": "Record the go-to-market recommendation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "primary_motion": {
                "type": "string",
                "description": "A short label (under 15 words) for the single GTM motion to lead with, e.g. 'Content-led founder brand with a free-audit lead magnet'. Pick one primary motion — don't hedge across all of them.",
            },
            "positioning_statement": {
                "type": "string",
                "description": "A sharp 1-2 sentence positioning statement — for WHO, what category, what makes it different — written to be used verbatim in outbound/landing copy, not restated market-speak.",
            },
            "messaging_pillars": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 core messages to hit repeatedly across every channel, each grounded in something evidence actually supports (a validated pain, a proven differentiator).",
            },
            "primary_channels": {
                "type": "array",
                "items": CHANNEL_SCHEMA,
                "description": "2-4 specific, named channels/motions that make up the launch mix — ranked by priority.",
            },
            "pricing_and_packaging": {
                "type": "string",
                "description": "A concrete pricing/packaging recommendation (price point, tiering, free-to-paid mechanic if any), grounded in external benchmarks and whatever willingness-to-pay evidence exists internally (ICP, Customer Discovery, Validation).",
            },
            "launch_sequence": {
                "type": "array",
                "items": {"type": "string"},
                "description": "5-9 ordered, concrete steps spanning roughly the first 30/60/90 days — not vague phases, actual actions in order.",
            },
            "metrics_to_track": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete, measurable metrics that would tell the founder this GTM plan is working (e.g. specific conversion rates, response rates, activation counts) — tied to the success criteria defined earlier in the pipeline where relevant.",
            },
            "key_risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The most serious risks to this specific GTM plan succeeding (channel saturation, message fatigue, a red flag from Validation, a competitive threat from secondary research) — not generic startup risks.",
            },
            "confidence": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "Overall confidence in this plan given available evidence — Low if it rests mostly on category-level grounding rather than this idea's own validation/ICP/customer-discovery evidence.",
            },
            "summary": {
                "type": "string",
                "description": "3-5 sentence plain-language summary of the GTM plan and why this motion over the alternatives, written for the founder to act on.",
            },
            "recommended_next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete, immediate next actions to start executing this plan.",
            },
        },
        "required": [
            "primary_motion", "positioning_statement", "messaging_pillars",
            "primary_channels", "pricing_and_packaging", "launch_sequence",
            "metrics_to_track", "key_risks", "confidence", "summary",
            "recommended_next_steps",
        ],
    },
}

STRUCTURING_INSTRUCTIONS = """You are the GTM Recommendation agent — the \
final phase in a market discovery pipeline. Your job is to turn everything \
learned in earlier phases into ONE concrete go-to-market plan, not a menu \
of options.

You'll be given: (1) the problem statement and hypotheses, (2) the Phase 3 \
synthesis verdict if available, (3) the Phase 4 ICP (primary segment + \
anti-ICP) if available, (4) secondary-research findings if available \
(especially Competitor pricing/channels and Community-named channels), \
(5) the Phase 5 customer discovery plan if available, (6) the Phase 6 \
validation results from REAL interviews if available — this is the \
strongest signal in the whole pipeline when it exists, and (7) fresh \
external research on channel effectiveness, pricing norms, and launch \
playbooks for this category.

Rules:
- Recommend ONE primary motion, not a hedge across several. A founder \
executing three motions at once with no real resourcing to do any of them \
well is a worse plan than one motion executed properly.
- Weight evidence by how real it is: real Phase 6 validation evidence (if \
present) outweighs Phase 4/5 assumptions, which outweigh category-level \
external grounding alone. Say so explicitly when the plan leans on the \
weaker end of that evidence.
- If Validation (Phase 6) surfaced red flags or an "Invalidated"/\
"Partially Validated" verdict, the GTM plan must account for that — do not \
propose a full-scale launch plan for an idea that hasn't actually cleared \
validation; recommend narrower/cheaper validation-first moves instead.
- Positioning and messaging must be specific to what's actually evidenced \
(a validated pain, a proven differentiator, a real anti-ICP) — not generic \
market-speak that could describe any competitor.
- Channels must be specific, named instantiations (a concrete lead magnet, \
a named community, a specific content format) — never a generic category \
like "content marketing" or "social media" with no further detail.
- Pricing/packaging must engage with actual willingness-to-pay evidence if \
it exists (ICP, Customer Discovery, Validation) rather than only external \
benchmarks.
- metrics_to_track must be concrete and measurable — actual rates/counts, \
not vague goals like "grow awareness."
- If little internal evidence exists yet (no synthesis, ICP, customer \
discovery, or validation), say so plainly in the summary, mark confidence \
"Low", and recommend a narrower validation-first GTM motion (e.g. a small \
manual pilot) rather than a full launch plan.
- Call the tool exactly once with your complete recommendation."""


def _build_research_prompt(problem_statement: str, questions: List[str], suggested_sources: List[str]) -> str:
    lines = [
        "You are researching EXTERNAL, real-world GTM benchmarks for a "
        "business idea — NOT the idea's internal validation (that's "
        "handled separately). Focus on facts about how comparable products "
        "actually go to market: which motions/channels work, typical "
        "pricing/packaging, and launch-playbook patterns — grounded in "
        "comparable/adjacent products, not this specific idea.",
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


def _format_icp(icp: dict) -> str:
    p = icp["primary_icp"]
    lines = [
        "---\nICP DISCOVERY (Phase 4)\n---",
        f"Primary ICP: {p['segment_name']} (confidence: {p['confidence']}, fit score: {p['fit_score']}/100)",
        f"Buyer persona: {p['buyer_persona']}",
        f"Pain points: {p['pain_points']}",
        f"Buying signals: {p['buying_signals']}",
        f"\nExclusion criteria (do not target): {icp['exclusion_criteria']}",
    ]
    return "\n".join(lines)


def _format_customer_discovery(plan: dict) -> str:
    lines = [
        "---\nCUSTOMER DISCOVERY PLAN (Phase 5)\n---",
        f"Success criteria: {plan['success_criteria']}",
        "\nRecruiting channels already identified:",
    ]
    lines += [f"- {c['channel']}: {c['why_this_channel']}" for c in plan["recruiting_channels"]]
    return "\n".join(lines)


def _format_validation(validation: dict, interviews: Optional[List[dict]]) -> str:
    lines = [
        "---\nVALIDATION RESULTS (Phase 6 — REAL interview evidence, strongest signal available)\n---",
        f"Overall verdict: {validation['overall_verdict']}",
        f"Success criteria met: {'Yes' if validation['success_criteria_met'] else 'No'} — {validation['success_criteria_assessment']}",
        f"\n{validation['summary']}",
    ]
    if validation.get("red_flags"):
        lines.append("\nRed flags:")
        lines += [f"- {r}" for r in validation["red_flags"]]
    if validation.get("notable_patterns"):
        lines.append("\nNotable patterns (real customer voice):")
        lines += [f"- {p}" for p in validation["notable_patterns"]]
    if interviews:
        lines.append("\n" + format_interviews(interviews))
    return "\n".join(lines)


def run_gtm_recommendation(
    session_data: dict,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
) -> GTMRecommendationOutput:
    """Runs GTM Recommendation to completion for one session's data.
    Requires `phase1_output`; Phase 3-6 outputs are used as context if
    present, but none is required."""
    phase1 = session_data["phase1_output"]
    questions = questions or DEFAULT_QUESTIONS
    suggested_sources = suggested_sources or DEFAULT_SOURCES

    research_prompt = _build_research_prompt(phase1["problem_statement"], questions, suggested_sources)

    context_parts = [
        f"Problem statement:\n{phase1['problem_statement']}\n",
        "Founder's hypotheses:",
    ]
    context_parts += [f"- {h}" for h in phase1["initial_hypotheses"]]
    context_parts.append("\nFounder's success criteria:")
    context_parts += [f"- {s}" for s in phase1["success_criteria"]]

    if "synthesis" in session_data:
        context_parts.append("\n" + format_synthesis(session_data["synthesis"]))
    else:
        context_parts.append("\n(No Phase 3 synthesis has been run yet for this session.)")

    if "icp_discovery" in session_data:
        context_parts.append("\n" + _format_icp(session_data["icp_discovery"]))
    else:
        context_parts.append("\n(No Phase 4 ICP Discovery has been run yet for this session.)")

    context_parts.append("\n" + format_secondary_research(
        session_data,
        none_found_message="No secondary-research agents have been run yet for this session.",
    ))

    if "customer_discovery" in session_data:
        context_parts.append("\n" + _format_customer_discovery(session_data["customer_discovery"]))
    else:
        context_parts.append("\n(No Phase 5 customer discovery plan has been run yet for this session.)")

    if "validation" in session_data:
        context_parts.append("\n" + _format_validation(
            session_data["validation"], session_data.get("interview_notes"),
        ))
    else:
        context_parts.append(
            "\n(No Phase 6 validation has been run yet for this session — no real "
            "customer interview evidence exists. Recommend a narrower, "
            "validation-first GTM motion rather than a full launch plan, and say "
            "so plainly.)"
        )

    extra_context = "\n".join(context_parts)

    result = run_research_pipeline(
        record_tool=RECORD_TOOL,
        research_prompt=research_prompt,
        structuring_context=STRUCTURING_INSTRUCTIONS,
        extra_context=extra_context,
    )

    primary_channels = [GTMChannelRecommendation(**c) for c in result["primary_channels"]]
    return GTMRecommendationOutput(
        primary_motion=result["primary_motion"],
        positioning_statement=result["positioning_statement"],
        messaging_pillars=result["messaging_pillars"],
        primary_channels=primary_channels,
        pricing_and_packaging=result["pricing_and_packaging"],
        launch_sequence=result["launch_sequence"],
        metrics_to_track=result["metrics_to_track"],
        key_risks=result["key_risks"],
        confidence=result["confidence"],
        summary=result["summary"],
        recommended_next_steps=result["recommended_next_steps"],
    )
