"""
Community Agent — Phase 2C of Secondary Research.

Finds direct, unprompted evidence in founder/user communities (Reddit,
Indie Hackers, Slack/Discord, Hacker News, LinkedIn posts/comments) of
whether the problem this idea addresses actually surfaces organically —
in people's own words, not the founder's framing of it.

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Community Agent brief (specific questions +
rationale, tied to the idea's actual hypotheses) instead of the generic
questions below — the tailored brief is always more useful than the
template.
"""
from typing import List, Optional

from models import ResearchFinding, CommunityResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "Are there threads/posts in relevant communities where people describe this exact problem unprompted?",
    "How do people describe the problem in their own words — do they use the founder's framing/vocabulary, or something different?",
    "What complaints or requests exist about adjacent/existing tools regarding the specific gap this idea claims to fill?",
    "Is there evidence people are already discussing or working around this problem informally (workarounds, DIY solutions, manual processes)?",
]

DEFAULT_SOURCES = [
    "Reddit (relevant subreddits)",
    "Indie Hackers",
    "Hacker News",
    "LinkedIn posts/comments",
    "Relevant Slack/Discord communities",
]

RECORD_TOOL = {
    "name": "record_community_research",
    "description": "Record the structured findings of the community research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "community_landscape": {
                "type": "string",
                "description": "A short label (under 12 words) naming the specific communities/channels explored — e.g. 'Reddit r/SaaS and Indie Hackers threads on AI visibility'. Not a full sentence or summary of findings.",
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
                            "description": "Source names/URLs (specific threads/posts where possible) that back this answer, from the web search results.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of what this means for the business idea's felt-urgency claim.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on community research alone — does the problem organically surface in the wild, or only in the founder's own framing?",
            },
        },
        "required": ["community_landscape", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are finding REAL, CURRENT evidence — in \
people's own words — of whether the problem a business idea addresses \
actually surfaces organically in founder/user communities.

Rules:
- Search for real threads, posts, and discussions. Do not answer from \
memory alone — community sentiment changes and your training data may be \
stale or may not reflect what's actually being discussed right now.
- Prefer specific, quotable evidence: named threads, subreddits, posts, or \
comments — not vague impressions. Cite the source (ideally a URL) for \
every claim.
- Distinguish sharply between (a) people independently describing this \
problem unprompted, in their own words, and (b) vendor/marketing content \
that merely asserts the problem exists. The former is real evidence; the \
latter is not — call this out explicitly when you see it.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a quote or thread.
- Be skeptical, not promotional — your job is to find the truth about \
whether this problem is actually felt, not to make the business idea look \
validated."""


def run_community_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> CommunityResearchOutput:
    """Runs the Community Agent to completion. See `_base.run_research_agent`
    for the shared Perplexity-search + OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="community_landscape",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return CommunityResearchOutput(
        community_landscape=result["community_landscape"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
