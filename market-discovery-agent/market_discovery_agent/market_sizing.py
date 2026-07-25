"""
Market Sizing — Phase 4b (TAM / SAM / SOM).

Runs after ICP Discovery, not before: SAM only means something once we
know the ICP's actual firmographic/industry/technographic filters to
narrow TAM down with, and SOM only means something once we know who the
named competitors are (from Phase 2B) and how confident the Phase 3
synthesis was in the opportunity overall. All three are optional context
(this phase still runs off Phase 1 alone if nothing else has been run),
but the estimate gets meaningfully sharper with each one present.

Like ICP Discovery, this benefits from live grounding — published market-
size figures and company-count/industry statistics are real-world facts,
not something to reason out from training data alone — so it runs the
same two-step pipeline as the 7 secondary-research agents:

  1. PERPLEXITY searches for EXTERNAL grounding only: published market-size
     estimates for the category (or the closest adjacent/parent category,
     since niche categories are often not sized on their own), and company-
     count/firmographic distribution data relevant to the ICP's segment.
     It does NOT re-derive anything already established internally.
  2. OPENAI structures the final TAM/SAM/SOM using BOTH that fresh external
     grounding AND everything already known internally (problem statement,
     ICP firmographics/qualified-account filters, Phase 3 synthesis
     verdict, secondary-research findings — including competitor pricing
     already gathered, so Perplexity isn't wastefully asked to re-research
     it) via `run_research_pipeline`'s `extra_context` parameter.

Every dollar figure is required to be a RANGE, not false precision, and
each estimate must state whether it's top-down (from a published report)
or bottom-up (company-count x average deal size) reasoning — niche/
emerging categories frequently have no clean published number (see the
Funding Agent's "no confident answer found" pattern), so a transparent
bottom-up estimate the founder can sanity-check is treated as equally
valid to a top-down one, just lower confidence when unconfirmed.
"""
from typing import List, Optional

from models import MarketSizeEstimate, MarketSizingOutput
from research_agents._base import run_research_pipeline
from synthesizer import format_secondary_research, format_synthesis

DEFAULT_QUESTIONS = [
    "What is the published market size (annual revenue) for the closest parent/adjacent software category (e.g., SEO software, martech, digital marketing analytics)?",
    "Are there any published market-size or analyst estimates specifically for this exact emerging category? If not, say so plainly rather than guessing.",
    "Roughly how many companies exist globally (or in the most relevant region) in the target industry/segment, broken down by company-size band if possible?",
    "What customer counts or market penetration are reported by comparable/adjacent SaaS categories at a similar maturity stage, as a reference point for a realistic obtainable share?",
]

DEFAULT_SOURCES = [
    "Analyst market-size reports (Gartner, Forrester, IDC, Statista)",
    "Industry association or trade-press market-size figures",
    "Government/census company-count and industry statistics",
    "Comparable SaaS category market-size benchmarks (e.g. published SEO/martech software market size)",
]

MARKET_SIZE_ESTIMATE_SCHEMA = {
    "type": "object",
    "properties": {
        "value_usd": {
            "type": "string",
            "description": "The estimated market size in USD, as a RANGE (e.g. '$450M-$600M annually') — never false precision.",
        },
        "timeframe": {
            "type": "string",
            "description": "What the figure represents, e.g. 'current annual market size' for TAM/SAM, or '3-year obtainable revenue' for SOM.",
        },
        "methodology": {
            "type": "string",
            "description": "Whether this is top-down (from a published market-size report/estimate) or bottom-up (company-count x average deal size reasoning), and exactly how it was derived.",
        },
        "key_assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The specific assumptions behind this number (e.g. company count used, average deal size, capture rate) so it can be sanity-checked or updated later.",
        },
        "confidence": {
            "type": "string",
            "enum": ["High", "Medium", "Low"],
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["value_usd", "timeframe", "methodology", "key_assumptions", "confidence", "sources"],
}

RECORD_TOOL = {
    "name": "record_market_sizing",
    "description": "Record the TAM/SAM/SOM market sizing estimate.",
    "input_schema": {
        "type": "object",
        "properties": {
            "tam": MARKET_SIZE_ESTIMATE_SCHEMA,
            "sam": MARKET_SIZE_ESTIMATE_SCHEMA,
            "sam_narrowing_criteria": {
                "type": "string",
                "description": "Exactly which ICP firmographic/industry/technographic filters were applied to narrow TAM down to SAM. If no ICP Discovery has been run yet, say so and narrow using the problem statement's implied segment instead.",
            },
            "som": MARKET_SIZE_ESTIMATE_SCHEMA,
            "som_capture_rationale": {
                "type": "string",
                "description": "Why this capture rate/timeframe is realistic given the named competitors' scale/funding (if known) and the Phase 3 synthesis's overall confidence — not an arbitrary percentage. An early-stage entrant against funded, established competitors should get a conservative capture rate unless there's a specific reason to expect otherwise.",
            },
            "overall_confidence": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "Overall confidence in this TAM/SAM/SOM given available evidence — Low if it rests mostly on bottom-up reasoning with no published figures found.",
            },
            "summary": {
                "type": "string",
                "description": "3-5 sentence plain-language summary of the market opportunity size, written for the founder to act on.",
            },
        },
        "required": [
            "tam", "sam", "sam_narrowing_criteria", "som",
            "som_capture_rationale", "overall_confidence", "summary",
        ],
    },
}

STRUCTURING_INSTRUCTIONS = """You are the Market Sizing agent in a market \
discovery pipeline. Your job is to size TAM (Total Addressable Market), \
SAM (Serviceable Addressable Market), and SOM (Serviceable Obtainable \
Market) — concretely and honestly, not with a confident-sounding but \
made-up number.

You'll be given: (1) the business's problem statement, (2) if available, \
the ICP Discovery output (firmographics, industry, technographics, and the \
qualified-account spec's filters), (3) if available, a Phase 3 synthesis \
with a go/no-go verdict, (4) if available, findings from up to 7 \
secondary-research agents (including competitor pricing already gathered — \
do not ask Perplexity to re-research pricing you already have), and (5) \
fresh external research on published market-size figures and company-count \
statistics, just gathered via web search.

Rules:
- TAM is the total size of the broadest addressable market for this \
category (or its closest adjacent/parent category if the category itself \
is too new to have a published figure — say which you used).
- SAM MUST be a genuine subset of TAM, narrowed using the ICP's actual \
firmographic/industry/technographic filters from Phase 4 — not a vague \
percentage haircut. State exactly which filters did the narrowing in \
sam_narrowing_criteria. If no ICP Discovery has been run, narrow using the \
segment implied by the problem statement instead, and say so.
- SOM MUST be a realistic, time-bound slice of SAM — grounded in the named \
competitors' scale/funding (if known from Phase 2B) and the synthesis's \
overall confidence (if one exists). An early-stage, unfunded entrant \
facing well-funded, established competitors should get a conservative \
capture rate (usually low single-digit percent of SAM within the stated \
timeframe) unless there's a specific, stated reason to expect more.
- EVERY value_usd must be a range, never a single false-precise number.
- EVERY estimate must state its methodology plainly: top-down (a real \
published estimate — cite it) or bottom-up (state the company-count and \
average-deal-size assumptions used to derive it). If no published figure \
exists for a level, say so and use bottom-up reasoning instead of \
inventing a top-down-sounding number.
- If the evidence base is thin (no ICP, no synthesis, no published market \
data found), say so plainly and mark overall_confidence "Low" rather than \
presenting a guess with false confidence.
- Call the tool exactly once with your complete TAM/SAM/SOM."""


def _build_research_prompt(problem_statement: str, icp_industry: Optional[str],
                            questions: List[str], suggested_sources: List[str]) -> str:
    lines = [
        "You are researching EXTERNAL, real-world market-size and company-"
        "count data for a business idea — NOT the idea's internal "
        "validation (that's handled separately). Focus only on published "
        "figures and statistics: market size for this category or its "
        "closest adjacent/parent category, and company-count/firmographic "
        "distribution data for the relevant industry/segment.",
        "",
        f"Problem statement (for category context):\n{problem_statement}\n",
    ]
    if icp_industry:
        lines.append(f"Target industry/segment to size company counts for: {icp_industry}\n")
    lines.append("Questions to answer:")
    lines += [f"- {q}" for q in questions]
    lines.append("\nPrioritize these kinds of sources: " + ", ".join(suggested_sources))
    lines.append(
        "\nAnswer each question directly and cite your sources. If no published "
        "figure exists, say so plainly rather than guessing at one."
    )
    return "\n".join(lines)


def run_market_sizing(
    session_data: dict,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
) -> MarketSizingOutput:
    """Runs Market Sizing (TAM/SAM/SOM) to completion for one session's
    data. Requires `phase1_output`; ICP Discovery, Phase 3 synthesis, and
    secondary-research findings are all used as context if present, but
    none is required — SAM/SOM are simply less precisely narrowed without
    ICP Discovery having been run first."""
    phase1 = session_data["phase1_output"]
    questions = questions or DEFAULT_QUESTIONS
    suggested_sources = suggested_sources or DEFAULT_SOURCES

    icp = session_data.get("icp_discovery")
    icp_industry = icp["primary_icp"]["industry"] if icp else None

    research_prompt = _build_research_prompt(
        phase1["problem_statement"], icp_industry, questions, suggested_sources,
    )

    context_parts = [f"Problem statement:\n{phase1['problem_statement']}\n"]

    if icp:
        p = icp["primary_icp"]
        spec = icp["qualified_account_spec"]
        context_parts.append(
            "\n---\nICP DISCOVERY (Phase 4)\n---\n"
            f"Primary ICP: {p['segment_name']}\n"
            f"Market: {p['market']}\n"
            f"Industry: {p['industry']}\n"
            f"Firmographics: {p['firmographics']}\n"
            f"Technographics: {p['technographics']}\n"
            f"Qualified-account firmographic filters: {spec['firmographic_filters']}\n"
            f"Qualified-account technographic filters: {spec['technographic_filters']}\n"
            f"Minimum fit score to pursue: {spec['minimum_fit_score']}/100"
        )
    else:
        context_parts.append(
            "\n(No Phase 4 ICP Discovery has been run yet for this session — "
            "narrow SAM using the segment implied by the problem statement instead.)"
        )

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

    return MarketSizingOutput(
        tam=MarketSizeEstimate(**result["tam"]),
        sam=MarketSizeEstimate(**result["sam"]),
        sam_narrowing_criteria=result["sam_narrowing_criteria"],
        som=MarketSizeEstimate(**result["som"]),
        som_capture_rationale=result["som_capture_rationale"],
        overall_confidence=result["overall_confidence"],
        summary=result["summary"],
    )
