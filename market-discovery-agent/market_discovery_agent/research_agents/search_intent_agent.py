"""
Search Intent Agent — Phase 2D of Secondary Research.

Determines whether people are actually SEARCHING for the problem/solution
this idea addresses — search volume, trend direction, autocomplete/People
Also Ask patterns — as opposed to only discovering it via some other
trigger (a referral, a triggering event, an ad). This matters for whether
SEO/content is a viable acquisition channel at all, independent of whether
the problem is real (that's Community/Industry's job).

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid. Note: most
keyword-volume tools (Ahrefs, SEMrush, Google Keyword Planner) sit behind
paid access the model can't reach directly — the research instructions
tell it to search for whatever public signal IS reachable (Google Trends,
AlsoAsked, visible autocomplete/PAA results, vendor blog posts citing
volume data) and say plainly when a claim can't be verified rather than
guessing a number.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Search Intent Agent brief (specific questions
+ rationale, tied to the idea's actual hypotheses) instead of the generic
questions below — the tailored brief is always more useful than the
template.
"""
from typing import List, Optional

from models import ResearchFinding, SearchIntentResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "What search volume and trend data exists for the core terms describing this problem or solution?",
    "Are there autocomplete or People Also Ask patterns showing people searching for this problem?",
    "What is the search intent behind queries for adjacent/existing tools — informational curiosity, or transactional buying intent?",
    "Is there search demand for a category, audit, or free-tool angle this idea could piggyback on for acquisition?",
]

DEFAULT_SOURCES = [
    "Google Trends",
    "AlsoAsked",
    "AnswerThePublic",
    "Google autocomplete / People Also Ask",
    "Ahrefs/SEMrush blog posts citing volume data",
]

RECORD_TOOL = {
    "name": "record_search_intent_research",
    "description": "Record the structured findings of the search intent research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "search_intent_landscape": {
                "type": "string",
                "description": "A short label (under 12 words) naming the specific search terms/queries explored — e.g. 'AI search visibility and GEO tool search terms'. Not a full sentence or summary of findings.",
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {
                            "type": "string",
                            "description": "A direct, sourced answer. If the search didn't turn up a confident answer, say so plainly rather than guessing a volume number.",
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
                "description": "2-3 sentence plain-language summary of whether proactive search demand exists for this problem, and what that implies for acquisition channel choice.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on search intent research alone — is there real, growing search demand, or is this idea entirely dependent on non-search discovery?",
            },
        },
        "required": ["search_intent_landscape", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are determining whether people actually \
SEARCH for the problem or solution a business idea addresses, and must \
answer a specific set of questions with sourced, honest findings.

Rules:
- Most paid keyword-volume tools (Ahrefs, SEMrush, Google Keyword Planner) \
are not directly reachable — search instead for what IS publicly visible: \
Google Trends data, AlsoAsked/AnswerThePublic results, visible autocomplete \
or "People Also Ask" patterns, and vendor/blog posts that cite volume or \
trend numbers (name them as the source, and note they may be \
self-interested).
- Do not answer from memory alone — search demand and trend direction \
change, and your training data may be stale.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a volume number or trend claim.
- Be skeptical, not promotional — your job is to find out whether real, \
proactive search demand exists, not to assume SEO/content will work as an \
acquisition channel just because the problem is real.
- Distinguish clearly between informational search intent (people curious \
about the topic) and transactional/commercial intent (people looking to \
buy or switch tools) where the evidence allows it — this matters for what \
kind of content or channel would actually convert."""


def run_search_intent_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> SearchIntentResearchOutput:
    """Runs the Search Intent Agent to completion. See `_base.run_research_agent`
    for the shared Perplexity-search + OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="search_intent_landscape",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return SearchIntentResearchOutput(
        search_intent_landscape=result["search_intent_landscape"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
