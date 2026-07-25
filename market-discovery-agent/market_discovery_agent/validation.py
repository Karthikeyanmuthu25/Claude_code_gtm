"""
Validation — Phase 6.

Unlike every prior phase, this one needs REAL primary data only the
founder can supply: actual notes from customer-discovery interviews they
conducted (ideally using Phase 5's discovery guide, recruiting channels,
and screening criteria). This module does not search or invent evidence —
it reasons over the founder's own interview notes and checks them against
the hypotheses, discovery questions, and success criteria defined earlier
in the pipeline (Phase 1's hypotheses, Phase 5's discovery-question
targets and success_criteria, Phase 4's ICP, Phase 3's synthesis).

Because there's no external fact to ground (the founder's notes ARE the
ground truth here), this runs on OpenAI structured output only — like the
Phase 3 synthesizer, not the Perplexity+OpenAI pipeline.
"""
from typing import List

from llm_utils import call_openai_structured
from models import HypothesisValidation, ValidationOutput
from synthesizer import format_synthesis

RECORD_TOOL = {
    "name": "record_validation",
    "description": "Record the validation assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "overall_verdict": {
                "type": "string",
                "enum": ["Validated", "Partially Validated", "Invalidated", "Inconclusive - need more interviews"],
                "description": "A direct call on what these interviews actually showed, not a hedge.",
            },
            "success_criteria_met": {
                "type": "boolean",
                "description": "Whether the concrete, falsifiable success criteria from Phase 5 (or Phase 1 if Phase 5 wasn't run) were actually met by these interviews.",
            },
            "success_criteria_assessment": {
                "type": "string",
                "description": "Why met/not met, with actual counts from the interviews (e.g. '2 of 7, not the required 3 of 10') — do not round favorably.",
            },
            "hypothesis_validations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "hypothesis_or_question": {"type": "string"},
                        "verdict": {
                            "type": "string",
                            "enum": ["Validated", "Refuted", "Mixed", "Inconclusive"],
                        },
                        "evidence_summary": {
                            "type": "string",
                            "description": "What the interviews actually showed, referencing which interview(s) by label.",
                        },
                        "supporting_interview_count": {
                            "type": "integer",
                            "description": "How many of the interviews showed genuinely supporting signal for this verdict.",
                        },
                    },
                    "required": ["hypothesis_or_question", "verdict", "evidence_summary", "supporting_interview_count"],
                },
                "description": "One assessment per hypothesis/discovery-question that these interviews could plausibly speak to — skip ones no interview touched on rather than forcing a verdict.",
            },
            "notable_patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Recurring themes, phrases, or reactions that showed up across multiple interviews — the closest thing to a real customer's voice, quoted or closely paraphrased where possible.",
            },
            "red_flags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Surprises, objections, or concerning signals that weren't anticipated going in — things that complicate the story, not just confirm it.",
            },
            "summary": {
                "type": "string",
                "description": "3-5 sentence plain-language summary of what was actually learned, written for the founder to act on.",
            },
            "recommended_next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 concrete next actions — e.g. run more interviews on a specific unresolved question, proceed to build, pivot a specific element, or stop.",
            },
        },
        "required": [
            "overall_verdict", "success_criteria_met", "success_criteria_assessment",
            "hypothesis_validations", "notable_patterns", "red_flags", "summary",
            "recommended_next_steps",
        ],
    },
}

SYSTEM_PROMPT = """You are the Validation agent in a market discovery \
pipeline. A founder has just conducted real customer-discovery interviews \
and given you their raw notes. Your job is to hold those notes up against \
the hypotheses and success criteria defined earlier in the pipeline and \
give an honest verdict — you are the last check before the founder \
decides whether to keep building.

Rules:
- Work ONLY from the interview notes provided. Do not assume anything was \
said that isn't in the notes, and do not fill gaps with what you'd expect \
a founder in this situation to say.
- Apply the success criteria EXACTLY as defined (e.g. "at least 3 of 10") \
— count the actual interviews and say plainly if the threshold wasn't met, \
even if the trend looks encouraging. A near-miss is still a miss.
- Distinguish real signal from politeness. Founders being interviewed \
often give encouraging-sounding but noncommittal answers ("that sounds \
useful," "I'd probably try that") — these are NOT validating evidence \
unless backed by a specific past behavior or concrete commitment. Flag \
noncommittal answers as weak signal, not as validation.
- Only assess hypotheses/discovery-questions that the interviews actually \
speak to — do not force a verdict on ones nothing in the notes addresses.
- Actively look for red flags: objections, confusion, disinterest, or \
answers that complicate the founder's story. A validation report with no \
red flags after real interviews is a reason for suspicion, not comfort — \
say so if that's the case.
- Be the most skeptical, most honest voice in this pipeline. Do not \
round "Partially Validated" up to "Validated" to be encouraging.
- Call the tool exactly once with your complete assessment."""


def format_interviews(interviews: List[dict]) -> str:
    lines = [f"---\nINTERVIEW NOTES ({len(interviews)} interview(s))\n---"]
    for i, interview in enumerate(interviews, 1):
        lines.append(f"\n## Interview {i}: {interview['interviewee_label']}")
        lines.append(f"Fits ICP (founder's own judgment): {interview['fits_icp']}")
        lines.append(f"Notes:\n{interview['notes']}")
    return "\n".join(lines)


def _format_discovery_plan(plan: dict) -> str:
    lines = ["---\nCUSTOMER DISCOVERY PLAN (Phase 5)\n---", f"Success criteria: {plan['success_criteria']}\n", "Discovery questions and what they test:"]
    for q in plan["discovery_questions"]:
        lines.append(f"- \"{q['question']}\"\n    Tests: {q['tests']}\n    Validating signal: {q['what_to_listen_for']}")
    return "\n".join(lines)


def _build_user_message(session_data: dict, interviews: List[dict]) -> str:
    phase1 = session_data["phase1_output"]
    lines = [
        f"Problem statement:\n{phase1['problem_statement']}\n",
        "Founder's original hypotheses:",
    ]
    lines += [f"- {h}" for h in phase1["initial_hypotheses"]]

    if "customer_discovery" in session_data:
        lines.append("\n" + _format_discovery_plan(session_data["customer_discovery"]))
    else:
        lines.append(
            "\n(No Phase 5 customer discovery plan exists for this session — "
            f"fall back to the founder's Phase 1 success criteria: "
            + "; ".join(phase1["success_criteria"]) + ")"
        )

    if "icp_discovery" in session_data:
        p = session_data["icp_discovery"]["primary_icp"]
        lines.append(f"\n---\nTARGET ICP (Phase 4)\n---\n{p['segment_name']}: {p['buyer_persona']}")

    if "synthesis" in session_data:
        lines.append("\n" + format_synthesis(session_data["synthesis"]))

    lines.append("\n" + format_interviews(interviews))

    return "\n".join(lines)


def run_validation(session_data: dict, interviews: List[dict]) -> ValidationOutput:
    """Runs Validation to completion against the founder's real interview
    notes. Requires `phase1_output` and at least one interview; Phase 4/5
    context is used if present but not required."""
    user_message = _build_user_message(session_data, interviews)
    result = call_openai_structured(
        system=SYSTEM_PROMPT,
        user_message=user_message,
        tool_name="record_validation",
        input_schema=RECORD_TOOL["input_schema"],
    )
    hypothesis_validations = [HypothesisValidation(**h) for h in result["hypothesis_validations"]]
    return ValidationOutput(
        overall_verdict=result["overall_verdict"],
        success_criteria_met=result["success_criteria_met"],
        success_criteria_assessment=result["success_criteria_assessment"],
        hypothesis_validations=hypothesis_validations,
        notable_patterns=result["notable_patterns"],
        red_flags=result["red_flags"],
        summary=result["summary"],
        recommended_next_steps=result["recommended_next_steps"],
    )
