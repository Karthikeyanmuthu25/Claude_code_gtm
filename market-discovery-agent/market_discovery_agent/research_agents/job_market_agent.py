"""
Job Market Agent — Phase 2F of Secondary Research.

Uses hiring signals to detect whether competitors or adjacent players are
already staffing up to build toward this idea's specific niche, ahead of
any public launch. Job postings are a leading indicator of roadmap
direction — often visible months before a feature or pivot is announced —
so this corroborates or disconfirms the same defensibility hypothesis the
Funding and Competitor agents test from other angles.

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Job Market Agent brief (specific questions +
rationale, tied to the idea's actual hypotheses) instead of the generic
questions below — the tailored brief is always more useful than the
template.
"""
from typing import List, Optional

from models import ResearchFinding, JobMarketResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "Are competitors or adjacent companies currently hiring for roles that signal they're building toward this same niche?",
    "What roles are the most relevant funded/adjacent players hiring for, and does any posting reference this idea's specific angle?",
    "Are there specialized roles (e.g. data science/ML/research) at any company suggesting proprietary methodology being built at scale in this space?",
]

DEFAULT_SOURCES = [
    "LinkedIn Jobs",
    "AngelList/Wellfound",
    "Company careers pages",
    "levels.fyi",
    "Job aggregator sites",
]

RECORD_TOOL = {
    "name": "record_job_market_research",
    "description": "Record the structured findings of the job market research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "job_market_landscape": {
                "type": "string",
                "description": "A short label (under 12 words) naming the companies whose hiring/job postings were explored — e.g. 'Taplio, Profound, and Otterly job postings'. Not a full sentence or summary of findings.",
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {
                            "type": "string",
                            "description": "A direct, sourced answer. If the search didn't turn up a confident answer, say so plainly rather than guessing.",
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["High", "Medium", "Low"],
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Source names/URLs (ideally specific job postings) that back this answer, from the web search results.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of what hiring signals imply for this idea's competitive-window/defensibility.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on job market research alone — are competitors visibly staffing up for this exact niche, or not?",
            },
        },
        "required": ["job_market_landscape", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are researching REAL, CURRENT hiring \
signals — job postings, roles, and headcount growth — for companies \
relevant to a business idea's space, and must answer a specific set of \
questions with sourced, honest findings.

Rules:
- Do not answer from memory alone — hiring activity changes constantly \
and your training data may be stale. Search for current postings.
- Prefer credible sources: LinkedIn Jobs, AngelList/Wellfound, company \
careers pages, and job aggregator sites. Quote the actual role title and, \
where possible, snippets from the posting itself — not a vague paraphrase.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a role or posting.
- Be skeptical, not promotional — your job is to find real evidence that a \
competitor is staffing toward this exact niche, not to reassure the \
founder no one is building it."""


def run_job_market_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> JobMarketResearchOutput:
    """Runs the Job Market Agent to completion. See `_base.run_research_agent`
    for the shared Perplexity-search + OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="job_market_landscape",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return JobMarketResearchOutput(
        job_market_landscape=result["job_market_landscape"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
