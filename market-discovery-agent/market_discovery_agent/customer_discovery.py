"""
Customer Discovery — Phase 5.

Turns the ICP (Phase 4) and whatever's still open or unresolved from
Phase 3's synthesis into an ACTIONABLE plan for talking to real
prospective customers: a tailored interview guide where every question is
tied to a specific hypothesis or open question it's meant to test, named
recruiting channels to actually find design partners matching the ICP, a
short outreach message template, screening criteria, and concrete,
falsifiable success criteria for the round of interviews.

Like ICP Discovery, this benefits from live grounding: effective
customer-discovery interview technique and realistic recruiting-channel
norms are things easy to get generically wrong without checking, so it
runs the same two-step pipeline:

  1. PERPLEXITY searches for EXTERNAL grounding only — interview technique
     that avoids false-positive validation (e.g. the "Mom Test" pitfall of
     hypothetical questions), and recruiting channels/norms for this
     specific buyer segment, beyond whatever the Community Agent already
     surfaced.
  2. OPENAI structures the final plan using that fresh grounding PLUS
     everything already known internally: the ICP (if Phase 4 has run),
     the synthesis verdict and open questions (if Phase 3 has run), and
     secondary-research findings (if any exist) — via
     `research_agents._base.run_research_pipeline`'s `extra_context`.

Works with a partial pipeline: ICP Discovery and the synthesis are both
optional context, not requirements — only Phase 1's problem statement and
hypotheses are required. Without them, questions are designed around the
founder's raw hypotheses instead, and the summary says so honestly.
"""
from typing import List, Optional

from models import DiscoveryQuestion, RecruitingChannel, CustomerDiscoveryOutput
from research_agents._base import run_research_pipeline
from synthesizer import format_secondary_research, format_synthesis

DEFAULT_QUESTIONS = [
    "What customer-discovery interview techniques or question framing most reliably surface honest signal — not polite false-positives — from busy early-stage founders?",
    "Beyond generic startup communities, what specific channels, communities, or newsletters would reach this exact buyer segment?",
    "What response rates, message length, and framing are typical for successful cold outreach recruiting unpaid design partners/interview participants in B2B SaaS?",
    "What are common pitfalls that lead a customer-discovery process to produce false-positive validation, and how does interview design avoid them?",
]

DEFAULT_SOURCES = [
    "Lean Startup / customer development methodology (Steve Blank, Rob Fitzpatrick's 'The Mom Test')",
    "Indie Hackers / founder community discussions on design-partner recruiting",
    "Cold outreach response-rate benchmarks for B2B SaaS",
    "Niche community directories for the target buyer segment",
]

RECORD_TOOL = {
    "name": "record_customer_discovery",
    "description": "Record the customer discovery plan.",
    "input_schema": {
        "type": "object",
        "properties": {
            "discovery_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "tests": {
                            "type": "string",
                            "description": "The specific hypothesis or open question (from Phase 1/3/4) this question is designed to validate or refute.",
                        },
                        "what_to_listen_for": {
                            "type": "string",
                            "description": "The concrete signal in their answer that would count as validating vs. refuting — not a vague 'positive response'.",
                        },
                    },
                    "required": ["question", "tests", "what_to_listen_for"],
                },
                "description": "5-8 interview questions, each tied to a specific hypothesis/open question.",
            },
            "recruiting_channels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "A specific, named place — a named subreddit, Slack community, newsletter, or directory. Not vague ('social media').",
                        },
                        "why_this_channel": {"type": "string"},
                        "evidence": {
                            "type": "string",
                            "description": "What supports this channel actually reaching the ICP — external research and/or prior secondary-research findings (e.g. Community Agent).",
                        },
                    },
                    "required": ["channel", "why_this_channel", "evidence"],
                },
                "description": "3-6 specific, named recruiting channels.",
            },
            "outreach_message_template": {
                "type": "string",
                "description": "A short (3-5 sentence) outreach message: leads with a specific observation relevant to the ICP's pain (not a generic pitch), makes a low-friction ask (a short call, not a sales pitch).",
            },
            "screening_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 criteria to quickly tell, from a short reply, whether someone actually matches the ICP before scheduling a call.",
            },
            "success_criteria": {
                "type": "string",
                "description": "Concrete and falsifiable criteria for the round of interviews (e.g. 'at least X of Y interviewed founders independently describe [specific pain] unprompted') — tied to the actual open questions/hypotheses.",
            },
            "summary": {
                "type": "string",
                "description": "2-4 sentence plain-language summary of the discovery plan and what it's designed to settle.",
            },
            "recommended_next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete, ordered next actions to execute this plan.",
            },
        },
        "required": [
            "discovery_questions", "recruiting_channels", "outreach_message_template",
            "screening_criteria", "success_criteria", "summary", "recommended_next_steps",
        ],
    },
}

STRUCTURING_INSTRUCTIONS = """You are the Customer Discovery agent in a \
market discovery pipeline. Your job is to turn the ICP and the still-open \
hypotheses into an actionable plan for talking to REAL prospective \
customers.

You'll be given: (1) the problem statement and hypotheses, (2) the ICP \
Discovery output if available (primary ICP + anti-ICP), (3) the Phase 3 \
synthesis verdict and open questions if available, (4) secondary-research \
findings (especially the Community Agent, if run) for channel context, \
and (5) fresh external research on interview technique and \
recruiting-channel norms.

Rules:
- Every discovery_question must be tied to a SPECIFIC hypothesis or open \
question from Phase 1/3/4 — don't write generic questions like "tell me \
about your business" that don't test anything specific.
- Favor questions that surface PAST behavior ("tell me about the last \
time X happened") over hypothetical ones ("would you use a tool that..."). \
Hypothetical questions produce false-positive validation — this is the \
well-known "Mom Test" pitfall (people are polite about hypotheticals) — \
design around it explicitly.
- Recruiting channels must be specific and actionable (a named subreddit, \
a named Slack community, a named newsletter) — not vague ("social media", \
"startup communities").
- If Community Agent findings already named specific channels, build on \
and extend them rather than repeating the same ones with different wording.
- The outreach_message_template should be short (3-5 sentences), lead \
with a SPECIFIC observation relevant to the ICP's pain (not a generic \
pitch), and make a low-friction ask (a 15-20 minute call, not a sales \
pitch).
- screening_criteria should let the founder quickly tell, from a short \
reply, whether someone actually matches the ICP before scheduling a call.
- success_criteria must be concrete and falsifiable (a specific fraction \
or count, e.g. "at least 3 of 10 interviewed founders independently \
describe X unprompted") — tie it back to the actual open questions/\
hypotheses, echoing the founder's own Phase 1 success criteria where \
relevant.
- If little or no ICP/synthesis/secondary-research context exists yet, \
say so plainly in the summary and design discovery_questions around the \
founder's raw hypotheses instead — still produce a usable guide, just be \
honest that it rests on less validation than ideal.
- Call the tool exactly once with your complete plan."""


def _build_research_prompt(
    problem_statement: str,
    icp_hint: Optional[str],
    known_channels_hint: Optional[str],
    questions: List[str],
    suggested_sources: List[str],
) -> str:
    lines = [
        "You are researching EXTERNAL best practices for customer-discovery "
        "interviews and design-partner recruiting — NOT the business idea's "
        "internal validation (that's handled separately). Focus on real "
        "interview-technique and recruiting-channel research.",
        "",
        f"Problem statement (for context only):\n{problem_statement}\n",
    ]
    if icp_hint:
        lines.append(f"Target buyer segment (for channel-relevance context only): {icp_hint}\n")
    if known_channels_hint:
        lines.append(
            "Channels already identified by prior research (find ADDITIONAL ones, "
            f"don't just repeat these): {known_channels_hint}\n"
        )
    lines.append("Questions to answer:")
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
        f"Firmographics: {p['firmographics']}",
        f"Buyer persona: {p['buyer_persona']}",
        f"Pain points: {p['pain_points']}",
        f"Buying signals: {p['buying_signals']}",
        f"\nExclusion criteria (do not target): {icp['exclusion_criteria']}",
    ]
    return "\n".join(lines)


def run_customer_discovery(
    session_data: dict,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
) -> CustomerDiscoveryOutput:
    """Runs Customer Discovery to completion for one session's data.
    Requires `phase1_output`; ICP Discovery, Phase 3 synthesis, and
    secondary-research findings are used as context if present, but none
    is required."""
    phase1 = session_data["phase1_output"]
    questions = questions or DEFAULT_QUESTIONS
    suggested_sources = suggested_sources or DEFAULT_SOURCES

    icp_hint = None
    if "icp_discovery" in session_data:
        p = session_data["icp_discovery"]["primary_icp"]
        icp_hint = f"{p['segment_name']} — {p['buyer_persona']}"

    known_channels_hint = None
    if "community_research" in session_data:
        known_channels_hint = session_data["community_research"].get("community_landscape")

    research_prompt = _build_research_prompt(
        phase1["problem_statement"], icp_hint, known_channels_hint, questions, suggested_sources,
    )

    context_parts = [
        f"Problem statement:\n{phase1['problem_statement']}\n",
        "Founder's hypotheses:",
    ]
    context_parts += [f"- {h}" for h in phase1["initial_hypotheses"]]

    if "icp_discovery" in session_data:
        context_parts.append("\n" + _format_icp(session_data["icp_discovery"]))
    else:
        context_parts.append(
            "\n(No Phase 4 ICP Discovery has been run yet for this session — "
            "design questions around the founder's raw hypotheses instead.)"
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

    discovery_questions = [DiscoveryQuestion(**q) for q in result["discovery_questions"]]
    recruiting_channels = [RecruitingChannel(**c) for c in result["recruiting_channels"]]
    return CustomerDiscoveryOutput(
        discovery_questions=discovery_questions,
        recruiting_channels=recruiting_channels,
        outreach_message_template=result["outreach_message_template"],
        screening_criteria=result["screening_criteria"],
        success_criteria=result["success_criteria"],
        summary=result["summary"],
        recommended_next_steps=result["recommended_next_steps"],
    )
