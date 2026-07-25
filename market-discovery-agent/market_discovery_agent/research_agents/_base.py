"""
Shared execution engine for secondary-research agents (Industry, Competitor,
Community, Search Intent, Funding, Job Market, Social Intelligence).

Two-step provider pipeline:

  1. PERPLEXITY searches the web and does the actual research. Perplexity's
     sonar models are purpose-built for this — every completion is grounded
     in live search results, with citations returned alongside the answer.
  2. OPENAI (ChatGPT) structures Perplexity's raw research + citations into
     the agent's exact findings JSON schema, using OpenAI's Structured
     Outputs (strict json_schema mode) — grammar-constrained at decode
     time, so the output is GUARANTEED schema-valid with no retry loop
     needed.

Client creation and the strict-schema conversion live in `llm_utils.py`
(shared with `agent.py`'s `discover`/`plan`/`synthesize`, which use OpenAI
structured output directly with no search step).

Every agent module (see industry_agent.py) supplies: default questions/
sources, a `research_instructions` paragraph (what Perplexity should focus
on / be skeptical about), and a RECORD_TOOL dict shaped like {"name",
"description", "input_schema"} — only `name` and `input_schema` are used.

Source credibility: Perplexity returns citations for whatever it searched,
with no guarantee those are reputable — a random blog and a Crunchbase
citation come back looking identical. `_classify_source_tier` tags each
citation's domain into Tier 1/2/3 (a static lookup, not an LLM judgment
call — deterministic and free, at the cost of not covering niche/new
domains, which fall through to Tier 3 by default) before the structuring
step sees them, and `STRUCTURING_SYSTEM_PROMPT` instructs OpenAI to weight
each finding's `confidence` by the tier of the sources backing it, not just
how confident the research text sounds.
"""
import json
from typing import List, Optional
from urllib.parse import urlparse

from llm_utils import get_openai_client, get_perplexity_client, strict_json_schema, OPENAI_MODEL, PERPLEXITY_MODEL

# Verified reference/data platforms, government sources, and major analyst
# firms — the highest-trust tier for market/company facts.
TIER_1_DOMAINS = {
    "g2.com", "capterra.com", "crunchbase.com", "pitchbook.com", "producthunt.com",
    "glassdoor.com", "indeed.com", "linkedin.com", "similarweb.com", "builtwith.com",
    "statista.com", "gartner.com", "forrester.com", "mckinsey.com", "cbinsights.com",
    "owler.com", "sec.gov", "census.gov", "bls.gov",
}

# Reputable trade press / established media — trustworthy but secondary,
# reported-on rather than primary-source data.
TIER_2_DOMAINS = {
    "techcrunch.com", "bloomberg.com", "reuters.com", "wsj.com", "forbes.com",
    "businessinsider.com", "wired.com", "theverge.com", "venturebeat.com", "axios.com",
    "searchengineland.com", "searchenginejournal.com", "moz.com", "hubspot.com",
    "nytimes.com", "ft.com", "cnbc.com", "wikipedia.org",
}


def _classify_source_tier(url: str) -> str:
    """Classifies a citation URL's domain into a credibility tier the
    structuring step can weight confidence by. Falls back to Tier 3 for
    anything unrecognized (blogs, forums, niche/new domains) rather than
    guessing — the point is a cheap, deterministic floor, not perfect
    coverage."""
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return "Tier 3 (unverified/blog/forum/unknown)"
    if domain.startswith("www."):
        domain = domain[4:]
    if not domain:
        return "Tier 3 (unverified/blog/forum/unknown)"
    if domain.endswith(".gov") or any(domain == d or domain.endswith("." + d) for d in TIER_1_DOMAINS):
        return "Tier 1 (verified/reference platform)"
    if any(domain == d or domain.endswith("." + d) for d in TIER_2_DOMAINS):
        return "Tier 2 (reputable media/trade press)"
    return "Tier 3 (unverified/blog/forum/unknown)"


STRUCTURING_SYSTEM_PROMPT = """You are converting raw web-research output \
into a strict structured format. You are NOT doing any research yourself \
— only faithfully reorganizing and extracting what's already in the \
research text below into the required schema.

Rules:
- Every finding's answer, confidence, and sources must come directly from \
the research text — do not add outside knowledge or invent anything not \
present in the text.
- If the research text doesn't confidently answer a question, reflect that \
honestly: write what's actually known (including "no confident answer \
found"), and mark confidence "Low" rather than overstating certainty.
- Extract source names/URLs exactly as they appear in the research text's \
citations — drop the bracketed tier tag itself from the recorded source \
string; it's there to inform your confidence judgment, not to be repeated \
verbatim as part of the source. If no source is given for a specific \
claim, use an empty list for that finding's sources rather than inventing \
one.
- Citations are tagged with a credibility tier: Tier 1 (verified reference/\
data platforms, government sources, major analyst firms), Tier 2 \
(reputable trade press/established media), or Tier 3 (unverified — blogs, \
forums, or unrecognized domains). Weight confidence by tier, not just by \
how confident the text sounds: a finding resting ONLY on Tier 3 sources \
should not be marked "High" — cap it at "Medium" for minor/directional \
claims and "Low" for quantitative or high-stakes claims. When Tier 1/2 and \
Tier 3 sources disagree on the same claim, prefer the Tier 1/2 evidence \
and note the disagreement if it's material.
- Fill every required field in the schema."""


def _search_with_perplexity(research_prompt: str) -> str:
    """Runs the research step. Perplexity grounds every completion in live
    web search automatically — no explicit tool call needed. Citations are
    tagged with a credibility tier (see module docstring) and appended to
    the returned text so the structuring step can weight confidence by
    source quality, not just extract citations verbatim."""
    client = get_perplexity_client()
    response = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[{"role": "user", "content": research_prompt}],
    )
    content = response.choices[0].message.content or ""

    citations = getattr(response, "citations", None)
    if not citations:
        # Some SDK/API versions surface citations per-choice instead of
        # top-level — fall back gracefully rather than erroring.
        citations = getattr(response.choices[0], "citations", None) or []

    if citations:
        tagged = [f"- {c}  [{_classify_source_tier(c)}]" for c in citations]
        content += "\n\nCitations:\n" + "\n".join(tagged)

    return content


def _structure_with_openai(raw_research: str, record_tool: dict, structuring_context: str) -> dict:
    client = get_openai_client()
    schema = strict_json_schema(record_tool["input_schema"])
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": STRUCTURING_SYSTEM_PROMPT + "\n\n" + structuring_context},
            {"role": "user", "content": raw_research},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": record_tool["name"], "schema": schema, "strict": True},
        },
    )
    message = response.choices[0].message
    if getattr(message, "refusal", None):
        raise RuntimeError(f"OpenAI refused to structure the research: {message.refusal}")
    return json.loads(message.content)


def run_research_pipeline(*, record_tool: dict, research_prompt: str, structuring_context: str,
                           extra_context: str = "") -> dict:
    """
    Low-level two-step pipeline: Perplexity searches using `research_prompt`
    verbatim, then OpenAI structures the result into `record_tool`'s schema.
    Use this directly (as competitor_agent.py does) when an agent's prompt
    shape doesn't fit the common problem_statement+hypotheses pattern that
    `run_research_agent` builds. Returns the structured dict.

    `extra_context`, if given, is prepended to what OpenAI sees during
    structuring (but NOT sent to Perplexity) — use this to hand the
    structuring step internal context that doesn't need searching for
    (e.g. earlier phases' findings), while keeping `research_prompt` focused
    on only what actually needs live grounding (as icp_discovery.py does).
    """
    print("  researching with Perplexity...")
    raw_research = _search_with_perplexity(research_prompt)
    content_for_structuring = (
        raw_research if not extra_context
        else extra_context + "\n\n---\nEXTERNAL RESEARCH (from Perplexity, just now)\n---\n" + raw_research
    )
    print("  structuring findings with ChatGPT...")
    return _structure_with_openai(content_for_structuring, record_tool, structuring_context)


def _build_research_prompt(
    problem_statement: str,
    hypotheses: List[str],
    questions: List[str],
    suggested_sources: List[str],
    rationale_by_question: Optional[dict],
    research_instructions: str,
) -> str:
    lines = [research_instructions, "", f"Problem statement:\n{problem_statement}\n"]
    lines.append("Hypotheses this research should help validate or challenge:")
    lines += [f"- {h}" for h in hypotheses]
    lines.append("\nResearch questions to answer:")
    for q in questions:
        rationale = (rationale_by_question or {}).get(q)
        if rationale:
            lines.append(f"- {q}\n    (why this matters: {rationale})")
        else:
            lines.append(f"- {q}")
    lines.append("\nPrioritize these kinds of sources: " + ", ".join(suggested_sources))
    lines.append(
        "\nAnswer each question directly and cite your sources for every claim. "
        "If you can't find a confident answer, say so plainly rather than guessing."
    )
    return "\n".join(lines)


def run_research_agent(
    *,
    record_tool: dict,
    subject_field: str,
    problem_statement: str,
    hypotheses: List[str],
    questions: List[str],
    suggested_sources: List[str],
    research_instructions: str,
    rationale_by_question: Optional[dict] = None,
) -> dict:
    """
    Runs a landscape-level secondary-research agent's full pipeline (see
    module docstring). Returns the structured, schema-valid dict — callers
    wrap it in their own dataclass (e.g. IndustryResearchOutput).
    """
    research_prompt = _build_research_prompt(
        problem_statement, hypotheses, questions, suggested_sources,
        rationale_by_question, research_instructions,
    )
    structuring_context = (
        f"This research is for a business idea's '{subject_field.replace('_', ' ')}' "
        "assessment. The original questions asked were:\n"
        + "\n".join(f"- {q}" for q in questions)
    )
    return run_research_pipeline(
        record_tool=record_tool,
        research_prompt=research_prompt,
        structuring_context=structuring_context,
    )
