"""
Funding Agent — Phase 2E of Secondary Research.

Assesses investor appetite and funding activity in this idea's space:
how much capital adjacent/competing players have raised recently and at
what stage/valuation, whether any funded player is already targeting this
specific niche, and how much competitive capital could flow in soon. This
calibrates the defensibility/competitive-window hypothesis most ideas make
implicitly ("no well-funded competitor will beat me to this").

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Funding Agent brief (specific questions +
rationale, tied to the idea's actual hypotheses) instead of the generic
questions below — the tailored brief is always more useful than the
template.
"""
from typing import List, Optional

from models import ResearchFinding, FundingResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "How much funding have adjacent or competing companies raised in the last 12-18 months, and at what stage/valuation?",
    "Are any funded players explicitly targeting this same specific niche, based on their roadmap, job postings, or public statements?",
    "What funding or investor interest exists in adjacent categories that could plausibly pivot into this space?",
    "Is there VC thesis content specifically framing this category as investable, and who is writing checks?",
]

DEFAULT_SOURCES = [
    "Crunchbase",
    "PitchBook",
    "Twitter/X VC threads",
    "AngelList/Wellfound",
    "TechCrunch and relevant funding news",
]

RECORD_TOOL = {
    "name": "record_funding_research",
    "description": "Record the structured findings of the funding research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "funding_landscape": {
                "type": "string",
                "description": "A short label (under 12 words) naming the specific competitive/category space whose funding activity was explored — e.g. 'GEO/AEO-tooling funding rounds (Profound, Otterly, Peec)'. Not a full sentence or summary of findings.",
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {
                            "type": "string",
                            "description": "A direct, sourced answer. If the search didn't turn up a confident answer, say so plainly rather than guessing a figure.",
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["High", "Medium", "Low"],
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Source names/URLs that back this answer, from the web search results.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of what this means for the idea's competitive-window/defensibility.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on funding research alone — is the window closing (well-funded players circling this exact niche) or still open?",
            },
        },
        "required": ["funding_landscape", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are researching REAL, CURRENT investor \
appetite and funding activity in a business idea's space, and must answer \
a specific set of questions with sourced, honest findings.

Rules:
- Do not answer from memory alone — funding rounds, valuations, and \
investor focus areas change constantly and your training data may be \
stale by months or years. Search for current information.
- Prefer credible sources: Crunchbase, PitchBook, named VC blog posts or \
threads, and reputable tech/funding press (TechCrunch and similar). Cite \
the source for every claim, including approximate dates for funding events.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a funding amount or valuation.
- Be skeptical, not promotional — your job is to find real signals that a \
well-funded competitor could close this idea's whitespace, not to \
reassure the founder the window is wide open."""


def run_funding_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> FundingResearchOutput:
    """Runs the Funding Agent to completion. See `_base.run_research_agent`
    for the shared Perplexity-search + OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="funding_landscape",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return FundingResearchOutput(
        funding_landscape=result["funding_landscape"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
