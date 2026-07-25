"""
Shared low-level helpers for calling OpenAI, Perplexity, Exa, and Apify.

The pipeline's core is OpenAI + Perplexity — no Anthropic. Two kinds of
calls happen across the project:

  1. Search-grounded research (Perplexity) — used by the 7 secondary-
     research agents via `research_agents/_base.py`'s two-step pipeline.
  2. Structured-output-only calls, no search needed (OpenAI) — used both
     by that same pipeline's structuring step, AND directly by `agent.py`'s
     `discover`/`plan`/`synthesize` commands, which only need to reason
     over text already in hand (a founder's raw input, or research findings
     already gathered) and record it in a strict schema.

OpenAI's Structured Outputs (`strict` json_schema mode) are grammar-
constrained at decode time, so the result is GUARANTEED to match the
schema — no malformed-output retry loop is needed for either use case.

Two more providers support the Competitor Agent specifically, where a
concrete LinkedIn URL is already in hand and generic web search is a weak
tool for it:

  3. Exa (`get_exa_client`) — fetches the actual readable text of a known
     URL (the competitor's LinkedIn page, their own site) rather than
     search snippets. Used by `research_agents/competitor_agent.py`.
  4. Apify (`get_apify_client`, `scrape_linkedin_company`) — runs a hosted
     actor that scrapes public LinkedIn company pages into structured
     fields (name, employee count, industry, website, ...) without logging
     in. Used by `competitor_agent.py` as ground-truth context alongside
     Exa/Perplexity, and by `target_account_agent.py` to verify candidate
     companies before they're presented as real recommendations.

If Anthropic is ever reintroduced, it should slot in here as an
alternative provider rather than being wired back into every caller
individually.
"""
import json
import os
from typing import Optional

OPENAI_MODEL = os.environ.get("MARKET_DISCOVERY_STRUCTURE_MODEL", "gpt-4o")
PERPLEXITY_MODEL = os.environ.get("MARKET_DISCOVERY_SEARCH_MODEL", "sonar-pro")
APIFY_LINKEDIN_COMPANY_ACTOR = os.environ.get(
    "APIFY_LINKEDIN_COMPANY_ACTOR", "automation-lab/linkedin-company-scraper"
)


def get_openai_client():
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set — export it or add it to .env.")
    return OpenAI(api_key=api_key)


def get_perplexity_client():
    from openai import OpenAI
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY is not set — export it or add it to .env.")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


def get_exa_client():
    from exa_py import Exa
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise RuntimeError("EXA_API_KEY is not set — export it or add it to .env.")
    return Exa(api_key=api_key)


def get_apify_client():
    from apify_client import ApifyClient
    api_key = os.environ.get("APIFY_API_KEY")
    if not api_key:
        raise RuntimeError("APIFY_API_KEY is not set — export it or add it to .env.")
    return ApifyClient(api_key)


def scrape_linkedin_company(linkedin_url: str) -> Optional[dict]:
    """Runs the Apify LinkedIn company-page actor for one URL. Returns the
    first (only) result item, or None if the key is missing, the actor
    finds nothing, or the call fails for any reason — this is best-effort
    ground truth/verification, not a hard dependency. Shared by
    `competitor_agent.py` (enrichment) and `target_account_agent.py`
    (verification — a candidate that fails to scrape here is dropped, not
    presented as a real recommendation)."""
    try:
        client = get_apify_client()
    except RuntimeError as e:
        print(f"  (skipping Apify LinkedIn scrape: {e})")
        return None
    try:
        run = client.actor(APIFY_LINKEDIN_COMPANY_ACTOR).call(
            run_input={"companyUrls": [linkedin_url], "maxCompanies": 1}
        )
        items = client.dataset(run.default_dataset_id).list_items().items
        return items[0] if items else None
    except Exception as e:
        print(f"  (Apify LinkedIn scrape failed for {linkedin_url}: {e})")
        return None


def strict_json_schema(input_schema: dict) -> dict:
    """Converts a {"type": "object", "properties": {...}} schema into an
    OpenAI Structured Outputs strict-mode schema: every object needs
    `required` listing ALL its properties and `additionalProperties: false`,
    recursively (strict mode does not support optional properties)."""
    schema = json.loads(json.dumps(input_schema))  # deep copy, drop references

    def _make_strict(node):
        if not isinstance(node, dict):
            return
        if node.get("type") == "object" and "properties" in node:
            node["required"] = list(node["properties"].keys())
            node["additionalProperties"] = False
            for v in node["properties"].values():
                _make_strict(v)
        elif node.get("type") == "array" and "items" in node:
            _make_strict(node["items"])

    _make_strict(schema)
    return schema


def call_openai_structured(*, system: str, user_message: str, tool_name: str,
                            input_schema: dict, model: str = None) -> dict:
    """
    Single-call structured output via OpenAI Structured Outputs (strict
    json_schema mode). Use this for any no-search, reason-over-text-in-hand
    task (Phase 1 synthesis, research planning, research synthesis) — for
    search-grounded research, use `research_agents/_base.py` instead.
    """
    client = get_openai_client()
    schema = strict_json_schema(input_schema)
    response = client.chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": tool_name, "schema": schema, "strict": True},
        },
    )
    message = response.choices[0].message
    if getattr(message, "refusal", None):
        raise RuntimeError(f"OpenAI refused to produce structured output: {message.refusal}")
    return json.loads(message.content)
