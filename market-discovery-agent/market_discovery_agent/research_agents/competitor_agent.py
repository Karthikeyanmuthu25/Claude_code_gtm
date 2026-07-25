"""
Competitor Agent — Phase 2B of Secondary Research.

Input for this agent is deliberately minimal: a list of competitors'
PUBLIC LinkedIn company-page URLs (not personal profiles, and nothing
requiring a login). From there, the agent:

  1. Scrapes the LinkedIn company page itself via an Apify actor
     (`automation-lab/linkedin-company-scraper` by default — override with
     `APIFY_LINKEDIN_COMPANY_ACTOR`) to get ground-truth structured fields
     (name, description, employee count, industry, website) without ever
     logging in — the actor only reads what's already public.
  2. Fetches the actual page text (not just search snippets) for the
     LinkedIn URL and, once known, the company's own website via Exa's
     `get_contents`.
  3. Runs Perplexity search — now steered by the known company
     name/website from step 1 when available — to pivot to the
     substantive research: the company's own website, G2, Capterra,
     Product Hunt, Crunchbase.
  4. Answers the five core competitor questions: existing solution,
     positioning, pricing, customers, weaknesses.

Apify and Exa are both best-effort enrichment: if their API keys aren't
set, or a call fails, that step is skipped (logged, not raised) and the
pipeline falls back to Perplexity search alone, exactly as it worked
before either was added.

Uses the shared Perplexity (search) + OpenAI (structuring) pipeline in
`_base.py`. Its prompt shape (anchored on a LinkedIn URL, no hypotheses)
doesn't fit the common problem_statement+hypotheses pattern the other 6
agents use, so it calls `_base.run_research_pipeline` directly with its
own hand-built research prompt rather than `_base.run_research_agent`.
"""
from typing import List, Optional
from urllib.parse import urlparse

from models import ResearchFinding, CompetitorResearchOutput
from research_agents._base import run_research_pipeline, _classify_source_tier
from llm_utils import get_exa_client, scrape_linkedin_company, APIFY_LINKEDIN_COMPANY_ACTOR

EXA_MAX_CHARS_PER_PAGE = 4000


def _domain_of(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def _scrape_linkedin_with_apify(linkedin_url: str) -> Optional[dict]:
    """Thin wrapper around `llm_utils.scrape_linkedin_company` that adds
    the "scraping..." progress message — the actual Apify call (and its
    graceful degrade-on-failure behavior) is shared with
    `target_account_agent.py` to avoid duplicating that logic."""
    print(f"  scraping LinkedIn company page with Apify ({APIFY_LINKEDIN_COMPANY_ACTOR})...")
    return scrape_linkedin_company(linkedin_url)


def _fetch_pages_with_exa(urls: List[str]) -> dict:
    """Fetches real page text (not search snippets) for known URLs via Exa.
    Returns {url: text}, skipping any URL Exa couldn't fetch. Best-effort —
    missing key or a failed call just returns {}."""
    urls = [u for u in dict.fromkeys(urls) if u]  # dedupe, drop falsy
    if not urls:
        return {}
    try:
        client = get_exa_client()
    except RuntimeError as e:
        print(f"  (skipping Exa page fetch: {e})")
        return {}
    try:
        print(f"  fetching page content with Exa for {len(urls)} URL(s)...")
        response = client.get_contents(urls, text=True)
        return {
            r.url: (r.text or "")[:EXA_MAX_CHARS_PER_PAGE]
            for r in response.results
        }
    except Exception as e:
        print(f"  (Exa page fetch failed, continuing without it: {e})")
        return {}

CORE_QUESTIONS = [
    "What is their existing solution — what does the product actually do?",
    "How do they position themselves (category, tagline, core value prop)?",
    "What is their pricing model and roughly what do they charge?",
    "Who are their customers (segment, company size, notable named customers)?",
    "What are their weaknesses — gaps, complaints, or things reviewers criticize?",
]

RECORD_TOOL = {
    "name": "record_competitor_research",
    "description": "Record the structured research findings for one competitor.",
    "input_schema": {
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "The company's real name, identified from their LinkedIn page or website.",
            },
            "website_url": {
                "type": "string",
                "description": "The company's official website, if found. Empty string if not found.",
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {
                            "type": "string",
                            "description": "A direct, sourced answer. If you couldn't find a confident answer, say so plainly rather than guessing.",
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["High", "Medium", "Low"],
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Source names/URLs from the web search results that back this answer.",
                        },
                    },
                    "required": ["question", "answer", "confidence", "sources"],
                },
            },
            "summary": {
                "type": "string",
                "description": "2-3 sentence plain-language summary of this competitor and how much of a threat/reference point they are.",
            },
        },
        "required": ["company_name", "website_url", "findings", "summary"],
    },
}

RESEARCH_INSTRUCTIONS = """You are given a competitor's PUBLIC LinkedIn \
company-page URL as your starting point — nothing else.

Process:
1. Search using the LinkedIn URL (and the company name if given) to \
identify who this company actually is. LinkedIn company pages are public \
and searchable — you'll typically find the company name, a short \
description, industry, and often their website in public search results \
and snippets. Do NOT attempt to log into LinkedIn, access private profile \
data, or scrape anything behind an authentication wall — work only from \
what's publicly discoverable through search.
2. Once you know the company name and (ideally) their website, pivot to \
researching them properly using public sources: their own website, G2, \
Capterra, Product Hunt, and Crunchbase. This is where the substantive \
answers come from, not the LinkedIn page itself.
3. Answer the five competitor questions with sourced, honest findings. If \
pricing or customer information isn't public, say so plainly rather than \
guessing a number.
4. Be genuinely critical when researching weaknesses — pull from real \
G2/Capterra review complaints where available, not generic hedging."""


def _build_research_prompt(
    linkedin_url: str,
    known_name: Optional[str],
    known_website: Optional[str],
    problem_statement: str,
    questions: List[str],
    suggested_sources: List[str],
) -> str:
    lines = [RESEARCH_INSTRUCTIONS, "", f"Competitor LinkedIn company page: {linkedin_url}"]
    if known_name:
        lines.append(f"Known name (already confirmed via LinkedIn scrape): {known_name}")
    if known_website:
        lines.append(f"Known website (already confirmed via LinkedIn scrape): {known_website}")
    if known_name or known_website:
        lines.append(
            "The name/website above are already confirmed — skip re-identifying the "
            "company and go straight to researching them on public sources."
        )
    lines.append(f"\nOur problem statement, for context on what to compare against:\n{problem_statement}")
    lines.append("\nQuestions to answer about this competitor:")
    lines += [f"- {q}" for q in questions]
    lines.append("\nPrioritize these kinds of sources: " + ", ".join(suggested_sources))
    return "\n".join(lines)


def _build_extra_context(apify_data: Optional[dict], exa_pages: dict) -> str:
    """Formats Apify's structured LinkedIn fields and Exa's fetched page
    text into context for the OpenAI structuring step (never sent to
    Perplexity — see `run_research_pipeline`'s `extra_context` param).
    Tags each source with a credibility tier, same as Perplexity's
    citations (see `_base._classify_source_tier`) — Apify's LinkedIn scrape
    is always Tier 1 (first-party), and the competitor's own website is
    labeled first-party too (authoritative for their own claims, not for
    independent criticism), rather than falling through to Tier 3 just
    because it isn't a recognized third-party reference platform.
    Returns "" if neither source produced anything."""
    sections = []
    known_website_domain = None
    if apify_data:
        fields = [
            ("Name", apify_data.get("name")),
            ("Description", apify_data.get("description")),
            ("Industry", apify_data.get("industry")),
            ("Company size", apify_data.get("companySize")),
            ("Employee count", apify_data.get("employeeCount")),
            ("Founded", apify_data.get("foundedYear")),
            ("Headquarters", apify_data.get("headquarters")),
            ("Website", apify_data.get("website")),
            ("Specialties", apify_data.get("specialties")),
        ]
        present = [f"- {label}: {value}" for label, value in fields if value]
        if present:
            sections.append(
                "GROUND-TRUTH DATA FROM LINKEDIN (scraped via Apify)  "
                "[Tier 1 (first-party — direct LinkedIn scrape)]:\n"
                + "\n".join(present)
            )
        if apify_data.get("website"):
            known_website_domain = _domain_of(apify_data["website"])

    for url, text in exa_pages.items():
        if not text:
            continue
        if known_website_domain and _domain_of(url) == known_website_domain:
            tier_label = "Tier 1 (first-party — company's own site; authoritative for their own claims, not for independent criticism)"
        else:
            tier_label = _classify_source_tier(url)
        sections.append(f"PAGE CONTENT FETCHED VIA EXA — {url}  [{tier_label}]:\n{text}")

    return "\n\n".join(sections)


def run_competitor_research(
    linkedin_url: str,
    problem_statement: str,
    known_name: Optional[str] = None,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
) -> CompetitorResearchOutput:
    """Runs the Competitor Agent to completion for ONE competitor: Apify
    scrapes the LinkedIn page for ground-truth fields, Exa fetches real
    page text for the LinkedIn URL (and the website once known), then
    Perplexity + OpenAI run as in `_base.run_research_pipeline` — with the
    Apify/Exa data folded in as `extra_context` for the structuring step."""
    apify_data = _scrape_linkedin_with_apify(linkedin_url)
    known_website = (apify_data or {}).get("website") or None
    if apify_data and apify_data.get("name"):
        known_name = apify_data["name"]

    exa_urls = [linkedin_url] + ([known_website] if known_website else [])
    exa_pages = _fetch_pages_with_exa(exa_urls)

    research_prompt = _build_research_prompt(
        linkedin_url,
        known_name,
        known_website,
        problem_statement,
        questions or CORE_QUESTIONS,
        suggested_sources or ["Company website", "G2", "Capterra", "Product Hunt", "Crunchbase"],
    )
    structuring_context = (
        f"This research is about ONE competitor, starting point LinkedIn URL: {linkedin_url}. "
        "Original questions asked:\n" + "\n".join(f"- {q}" for q in (questions or CORE_QUESTIONS))
    )
    result = run_research_pipeline(
        record_tool=RECORD_TOOL,
        research_prompt=research_prompt,
        structuring_context=structuring_context,
        extra_context=_build_extra_context(apify_data, exa_pages),
    )
    findings = [ResearchFinding(**f) for f in result["findings"]]
    return CompetitorResearchOutput(
        linkedin_url=linkedin_url,
        company_name=result["company_name"],
        website_url=known_website or result.get("website_url", ""),
        findings=findings,
        summary=result["summary"],
    )


def run_competitor_batch(
    competitor_inputs: List[dict],
    problem_statement: str,
    questions: Optional[List[str]] = None,
    suggested_sources: Optional[List[str]] = None,
    on_result=None,
) -> List[CompetitorResearchOutput]:
    """
    Runs the Competitor Agent for a list of {"linkedin_url": ..., "known_name": ...}
    dicts, one at a time. `on_result` is an optional callback(result) invoked
    after each competitor completes — useful for streaming progress to the
    terminal or saving incrementally so a crash mid-batch doesn't lose
    everything already researched.
    """
    results = []
    for c in competitor_inputs:
        result = run_competitor_research(
            linkedin_url=c["linkedin_url"],
            problem_statement=problem_statement,
            known_name=c.get("known_name"),
            questions=questions,
            suggested_sources=suggested_sources,
        )
        results.append(result)
        if on_result:
            on_result(result)
    return results
