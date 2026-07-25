"""
Social Intelligence Agent — Phase 2G of Secondary Research (the last of
the 7).

Captures real-time, organic social conversation about this idea's problem:
how frequently and in what tone the target audience posts about it, and how
similar content/hook formats (scorecards, audits, low-score reveals,
before/after comparisons) actually perform when shared — engagement,
virality, skepticism — as opposed to assumed. This is closely related to
the Community Agent (which looks at forums/communities) but focused
specifically on public social platforms and share/virality behavior, which
matters for any idea whose growth loop depends on organic sharing.

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py` so answers are grounded in real, current sources, not the
model's training data, and always come back schema-valid.

If a `research_plan` already exists in the session (from `agent.py plan`),
this agent uses ITS tailored Social Intelligence Agent brief (specific
questions + rationale, tied to the idea's actual hypotheses) instead of the
generic questions below — the tailored brief is always more useful than
the template.
"""
from typing import List, Optional

from models import ResearchFinding, SocialIntelligenceResearchOutput
from research_agents._base import run_research_agent

DEFAULT_QUESTIONS = [
    "How frequently and in what tone does the target audience post on social platforms (LinkedIn, Twitter/X) about this exact problem?",
    "When people share content in a similar format to what this idea would produce (scorecards, audits, comparisons), what engagement/share patterns do those posts get?",
    "What sentiment exists around the core hook or framing this idea would use — do people react with anxiety/action, or dismissiveness ('vanity metric')?",
    "Are there any viral posts or threads specifically about this problem, and what follow-on engagement (comments, shares, quote-posts) did they get?",
]

DEFAULT_SOURCES = [
    "LinkedIn post search",
    "Twitter/X search",
    "BuzzSumo",
    "Brand24/Mention-style tools if accessible manually",
]

RECORD_TOOL = {
    "name": "record_social_intelligence_research",
    "description": "Record the structured findings of the social intelligence research.",
    "input_schema": {
        "type": "object",
        "properties": {
            "social_intelligence_landscape": {
                "type": "string",
                "description": "A short label (under 12 words) naming the platforms/conversations explored — e.g. 'LinkedIn and X posts on AI-citation loss'. Not a full sentence or summary of findings.",
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
                            "description": "Source names/URLs (ideally specific posts/threads) that back this answer, from the web search results.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of what organic social signal implies for this idea's felt-urgency and virality assumptions.",
            },
            "opportunity_signal": {
                "type": "string",
                "enum": ["Strong", "Moderate", "Weak", "Unclear"],
                "description": "Overall signal strength for this idea based on social intelligence research alone — does this problem/content format organically surface and spread, or is that assumed rather than evidenced?",
            },
        },
        "required": ["social_intelligence_landscape", "findings", "summary", "opportunity_signal"],
    },
}

RESEARCH_INSTRUCTIONS = """You are finding REAL, CURRENT evidence of \
organic social conversation and sharing behavior related to a business \
idea's problem, and must answer a specific set of questions with sourced, \
honest findings.

Rules:
- Search for real posts, threads, and engagement patterns. Do not answer \
from memory alone — social conversation and virality patterns change \
constantly and your training data may be stale or may not reflect what's \
actually being posted right now.
- Prefer specific, quotable evidence: named posts, threads, or accounts — \
not vague impressions of "people talk about this a lot." Cite the source \
(ideally a URL) for every claim.
- Distinguish sharply between (a) organic, unprompted posts from real \
people, and (b) vendor/marketing content designed to look organic. The \
former is real evidence; call out the latter explicitly when you see it.
- If you cannot find a confident answer, say so explicitly rather than \
fabricating a post, engagement number, or trend.
- Be skeptical, not promotional — your job is to find the truth about \
whether this content format/problem actually gets attention and shares, \
not to assume virality because the idea sounds shareable."""


def run_social_intelligence_research(
    problem_statement: str,
    hypotheses: List[str],
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    rationale_by_question: Optional[dict] = None,
) -> SocialIntelligenceResearchOutput:
    """Runs the Social Intelligence Agent to completion. See
    `_base.run_research_agent` for the shared Perplexity-search +
    OpenAI-structuring pipeline."""
    result = run_research_agent(
        record_tool=RECORD_TOOL,
        subject_field="social_intelligence_landscape",
        problem_statement=problem_statement,
        hypotheses=hypotheses,
        questions=questions or DEFAULT_QUESTIONS,
        suggested_sources=suggested_sources or DEFAULT_SOURCES,
        research_instructions=RESEARCH_INSTRUCTIONS,
        rationale_by_question=rationale_by_question,
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return SocialIntelligenceResearchOutput(
        social_intelligence_landscape=result["social_intelligence_landscape"],
        findings=findings,
        summary=result["summary"],
        opportunity_signal=result["opportunity_signal"],
    )
