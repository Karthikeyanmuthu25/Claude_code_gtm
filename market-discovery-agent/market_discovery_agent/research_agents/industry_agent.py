"""
Industry Agent — Phase 2A of Secondary Research.

Answers the five core industry questions for this specific business idea:
  - Which industry has this problem?
  - Market size
  - Growth rate
  - Regulations
  - Technology trends

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Industry Agent brief (specific questions +
rationale, tied to the idea's actual hypotheses) instead of the generic
five questions — the tailored brief is always more useful than the
template.
"""
from typing import List, Optional

from models import ResearchFinding, IndustryResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "Which industry actually has this problem, and how would you segment it?",
    "What is the market size for this industry/segment?",
    "What is the growth rate, and is it accelerating or slowing?",
    "What regulations affect this industry, and are they tightening or loosening?",
    "What technology trends are reshaping how this industry buys or works?",
]

DEFAULT_SOURCES = [
    "Gartner",
    "McKinsey",
    "CB Insights",
    "Statista",
    "Government reports",
    "Industry associations",
]

RECORD_TOOL = {
    "name": "record_industry_research",
    "description": "Record the structured findings of the industry research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "industry_name": {
                "type": "string",
                "description": "The specific industry/segment this idea actually serves — be precise, not a broad category.",
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
                            "description": "Source names/URLs that back this answer, from the research.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of what this means for the business idea.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on industry research alone.",
            },
        },
        "required": ["industry_name", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are researching the REAL, CURRENT state of \
an industry for a business idea, and must answer a specific set of \
questions with sourced, honest findings.

Rules:
- Do not answer from memory alone for anything time-sensitive (market \
size, growth rate, regulatory status, funding, trends) — search for \
current information and cite it.
- Prefer credible sources: analyst firms (Gartner, McKinsey, CB Insights), \
Statista, government/regulatory reports, and named industry associations. \
Cite the source for every claim.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a number or guessing.
- Be skeptical, not promotional — your job is to find the truth about this \
industry, not to make the business idea look good."""


def run_industry_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> IndustryResearchOutput:
    """Runs the Industry Agent to completion. See `_base.run_research_agent`
    for the shared Perplexity-search + OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="industry_name",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return IndustryResearchOutput(
        industry_name=result["industry_name"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
