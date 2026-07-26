"""
Target Account Agent — Phase 4c.

The terminal step of the 9-step ICP framework: turns ICP Discovery's
`qualified_account_spec` and `scoring_rubric` from criteria into an actual
ranked list of real, LinkedIn-verified candidate companies. Requires ICP
Discovery to have been run first — there's no scoring rubric to score
against otherwise. Market Sizing (TAM/SAM/SOM) is optional context, used
to sanity-check that the target location/segment is worth prioritizing.

Three-stage pipeline, deliberately keeping "find candidates" and "verify
they're real" and "score them" as separate steps rather than trusting one
model call to do all three (an LLM asked to both name real companies AND
score them in one pass tends to invent plausible-sounding details for
whichever it's less sure of):

  1. PERPLEXITY + OPENAI (discovery) — `research_agents._base.run_research_pipeline`
     searches for real, named companies matching the qualified-account
     spec's firmographic/technographic/buying-signal filters within the
     target location, and structures them into a candidate list. Perplexity
     is explicitly told to leave `linkedin_url` blank rather than guess one
     it isn't confident about.
  2. EXA + APIFY (verification) — Perplexity is often too conservative to
     state an exact LinkedIn slug even for well-known companies, so any
     candidate missing a `linkedin_url` first gets one filled in via an Exa
     search (`_find_linkedin_url_with_exa`) before being scraped via
     `llm_utils.scrape_linkedin_company` (the same actor
     `competitor_agent.py` uses). A candidate that still has no URL, or
     whose URL fails to scrape, is dropped into `unverified_candidates`
     rather than presented as a real recommendation — this is the
     integrity check that keeps the final list honest.

     Since Exa's lookup is a generic web search, not a guaranteed entity
     match, the scraped page's own `name` field is then sanity-checked
     against the candidate name via `_names_plausibly_match` — a mismatch
     (Exa found a different, similarly-named company) is dropped rather
     than silently presented as the intended company.

     Location fit (if a target_location was given) is then checked
     DETERMINISTICALLY against the real `headquarters` field via
     `_country_alpha2_from_headquarters`, using `pycountry`'s static ISO
     3166-1/3166-2 data — no network call, no LLM judgment. This replaced
     an earlier design where an LLM did this check as part of scoring: it
     once hallucinated that "Pune, Maharashtra" wasn't in India. A
     confident mismatch is dropped right here; only candidates whose
     headquarters string doesn't resolve to any known country/subdivision
     (rare) fall through to the scoring step's best-effort judgment.
  3. OPENAI (scoring, no search) — `llm_utils.call_openai_structured` scores
     only the VERIFIED (and location-confirmed) candidates against the
     ICP's scoring rubric, using their real Apify data as evidence, and
     ranks the top N.

A thin candidate pool (discover more than you need) absorbs candidates
that fail verification in step 2 — asking for exactly `count` up front
would mean any verification failure shrinks the final list below what was
asked for. On top of that buffer, `discover_and_verify_candidates` will
run MULTIPLE discovery rounds (up to `DISCOVERY_MAX_ROUNDS`) if the first
round's buffer still doesn't yield `count` verified candidates — each
extra round excludes every company name already seen (verified or not) so
it doesn't just re-surface the same rejects. This is still best-effort,
not an absolute guarantee: a narrow enough ICP/location combination can
have fewer than `count` real, LinkedIn-verified qualifying companies to
find, in which case the run honestly returns fewer, with the shortfall
visible in `unverified_candidates`.
"""
import difflib
import unicodedata
from typing import List, Optional

import pycountry

from models import TargetAccount, TargetAccountListOutput
from research_agents._base import run_research_pipeline
from llm_utils import call_openai_structured, scrape_linkedin_company, get_exa_client

_SUBDIVISION_INDEX = None  # lazy-built {diacritic-stripped lowercase state/province name: alpha_2 country code}
_COUNTRY_EXACT_INDEX = None  # lazy-built {diacritic-stripped lowercase name/code: alpha_2 country code}


def _strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _subdivision_index() -> dict:
    """Lazily builds a {state/province name -> country alpha_2} index from
    ALL of pycountry's subdivisions, stripped of diacritics — pycountry's
    official ISO romanizations (e.g. "Mahārāshtra", "Karnātaka") don't
    match the plain-ASCII spellings real-world data like LinkedIn actually
    uses ("Maharashtra", "Karnataka")."""
    global _SUBDIVISION_INDEX
    if _SUBDIVISION_INDEX is None:
        _SUBDIVISION_INDEX = {
            _strip_diacritics(s.name).lower(): s.country_code
            for s in pycountry.subdivisions
        }
    return _SUBDIVISION_INDEX


def _country_exact_index() -> dict:
    """Lazily builds a {name/official_name/common_name/alpha_2/alpha_3 ->
    alpha_2} index for EXACT (non-fuzzy) country lookups."""
    global _COUNTRY_EXACT_INDEX
    if _COUNTRY_EXACT_INDEX is None:
        index = {}
        for c in pycountry.countries:
            for attr in ("name", "official_name", "common_name", "alpha_2", "alpha_3"):
                value = getattr(c, attr, None)
                if value:
                    index[_strip_diacritics(value).lower()] = c.alpha_2
        _COUNTRY_EXACT_INDEX = index
    return _COUNTRY_EXACT_INDEX


def _country_alpha2_from_headquarters(headquarters: str) -> Optional[str]:
    """Resolves the ISO alpha-2 country for a LinkedIn `headquarters`
    string like "Pune, Maharashtra" using EXACT (non-fuzzy) matching only,
    checked token by token against known states/provinces then country
    names — deliberately does NOT use fuzzy country matching here, since a
    headquarters string's city token could occasionally fuzzy-match an
    unrelated country by coincidence (observed live: pycountry's fuzzy
    search matches the lone token "London" to "United Kingdom" — correct
    in that case, but not a risk worth taking on arbitrary city names).
    Returns None if no token resolves."""
    if not headquarters:
        return None
    subdivision_index = _subdivision_index()
    country_index = _country_exact_index()
    for token in [t.strip() for t in headquarters.split(",") if t.strip()]:
        key = _strip_diacritics(token).lower()
        if key in subdivision_index:
            return subdivision_index[key]
        if key in country_index:
            return country_index[key]
    return None


def _country_alpha2_from_target_location(target_location: str) -> Optional[str]:
    """Resolves the ISO alpha-2 country for a user-typed target_location
    (e.g. "India", "USA", "UK", "United States"). Fuzzy matching is
    appropriate here — unlike a headquarters string, this is always
    meant to name a country or a common alias/abbreviation of one, not an
    arbitrary city, so the false-positive risk that rules out fuzzy
    matching for headquarters doesn't apply."""
    if not target_location:
        return None
    key = _strip_diacritics(target_location).lower()
    country_index = _country_exact_index()
    if key in country_index:
        return country_index[key]
    try:
        matches = pycountry.countries.search_fuzzy(target_location)
    except LookupError:
        matches = []
    return matches[0].alpha_2 if matches else None


def _location_check(headquarters: str, target_location: str) -> Optional[bool]:
    """Deterministically checks whether `headquarters` is in
    `target_location`. Returns True/False when both sides resolve to a
    known country; returns None when either side can't be resolved (an
    unrecognized headquarters format, or a target_location that isn't a
    country/alias pycountry knows) — callers should treat None as "can't
    confirm, don't hard-drop" rather than as a match or mismatch."""
    hq_country = _country_alpha2_from_headquarters(headquarters)
    target_country = _country_alpha2_from_target_location(target_location)
    if hq_country is None or target_country is None:
        return None
    return hq_country == target_country

DISCOVERY_BUFFER_MULTIPLIER = 5  # discover 5x the requested count: some won't have a confident LinkedIn URL, some will fail to scrape, and (when a location filter is set) some will scrape fine but turn out headquartered elsewhere
DISCOVERY_MAX_ROUNDS = 3  # cap on extra discovery rounds discover_and_verify_candidates will run to try to reach `count` verified candidates

DISCOVERY_RECORD_TOOL = {
    "name": "record_candidate_companies",
    "description": "Record real, named candidate companies identified by web research as potential qualified accounts.",
    "input_schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "The real, specific company name — not a category, example, or placeholder.",
                        },
                        "linkedin_url": {
                            "type": "string",
                            "description": "The company's public LinkedIn company-page URL, ONLY if confidently identified from the research text. Empty string if not confidently found — do not guess or construct a URL.",
                        },
                        "website_url": {
                            "type": "string",
                            "description": "The company's official website, if found in the research text. Empty string if not found.",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "Why this company plausibly matches the target firmographic/technographic/buying-signal filters, referencing the research text.",
                        },
                    },
                    "required": ["company_name", "linkedin_url", "website_url", "rationale"],
                },
                "description": "Real, named candidate companies actually mentioned in the research text — do not invent any not present in the text.",
            },
        },
        "required": ["candidates"],
    },
}

DISCOVERY_STRUCTURING_CONTEXT = (
    "This research is identifying real candidate companies for a qualified-"
    "account list. Only extract companies actually named in the research "
    "text below — do not invent any. Leave linkedin_url as an empty string "
    "for any company whose exact LinkedIn URL isn't confidently stated in "
    "the text, rather than guessing or constructing one."
)

SCORING_SYSTEM_PROMPT = """You are scoring VERIFIED candidate companies \
against an ICP's scoring rubric and qualified-account spec, to produce a \
ranked target-account list. You are NOT doing any research yourself — \
only scoring what's already been verified via a real LinkedIn scrape, \
provided below.

Rules:
- The "Target location" given in the user message is AUTHORITATIVE for \
this run and OVERRIDES any different geography mentioned inside the \
qualified-account spec's firmographic_filters text itself — that text was \
often written during an earlier ICP research pass and may name a different \
region (e.g. it might say "North America or Europe" while Target location \
here says "India"). When they conflict, always check against Target \
location, never against a region named only in firmographic_filters.
- Every candidate below has ALREADY had its headquarters deterministically \
checked against the target location before reaching you (see each \
candidate's "Location check" line) — a candidate marked "confirmed" is \
settled; do NOT re-litigate or second-guess it. Only candidates marked \
"could not be automatically confirmed" need YOUR judgment: use your own \
knowledge of world geography on the raw headquarters string given, and if \
you determine it is genuinely NOT in the target location, EXCLUDE it from \
ranked_accounts and list it in `location_mismatches` instead, with its \
real headquarters string.
- Score each remaining candidate honestly against the rubric's weighted \
criteria, using its verified LinkedIn data (employee count, industry, \
description, etc.) and the discovery rationale given. Do not inflate a \
score to justify inclusion — a candidate that's a weak fit should get a \
low score, even if that means it falls below the qualified-account spec's \
minimum fit score.
- key_matching_signals must cite concrete evidence from the verified data \
(e.g. "708 employees on LinkedIn", "industry: Software Development") — \
not vague restatements like "seems like a good fit."
- Only include candidates actually provided below — do not invent any \
company not listed.
- Rank ranked_accounts highest fit_score first.
- Only the top N candidates by fit_score (N is stated in the user message) \
will actually be kept in the final deliverable — write `summary` to \
describe ONLY those top N, not every candidate you scored, even though \
you should still return every eligible candidate you scored in \
ranked_accounts.
- Fill every required field in the schema."""

SCORING_RECORD_SCHEMA = {
    "type": "object",
    "properties": {
        "ranked_accounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "linkedin_url": {"type": "string"},
                    "website_url": {"type": "string"},
                    "industry": {"type": "string"},
                    "employee_count": {
                        "type": "string",
                        "description": "As reported by the verified LinkedIn data — a string since it's often a range or approximation.",
                    },
                    "fit_score": {
                        "type": "integer",
                        "description": "0-100, scored honestly against the provided scoring rubric.",
                    },
                    "fit_score_rationale": {"type": "string"},
                    "key_matching_signals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Concrete evidence from the verified data, not vague restatements.",
                    },
                },
                "required": [
                    "company_name", "linkedin_url", "website_url", "industry",
                    "employee_count", "fit_score", "fit_score_rationale", "key_matching_signals",
                ],
            },
            "description": "Candidates that are genuinely headquartered in the target location (if one was specified), ranked highest fit_score first.",
        },
        "location_mismatches": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Candidates excluded because their real headquarters isn't genuinely in the target location, formatted as 'Company Name (headquartered in X, not target location Y)'. Empty list if no target location was specified or all candidates matched.",
        },
        "summary": {
            "type": "string",
            "description": "2-4 sentence plain-language summary of the resulting target-account list and how strong a fit it is overall.",
        },
    },
    "required": ["ranked_accounts", "location_mismatches", "summary"],
}


def _build_discovery_prompt(
    spec: dict, target_location: str, buffer_count: int, exclude_names: Optional[List[str]] = None,
) -> str:
    lines = [
        "You are identifying REAL, SPECIFIC, NAMED companies (not made-up "
        "or example companies) that plausibly match the target-account "
        "filters below. For each company, name it exactly. If you know its "
        "exact public LinkedIn company-page URL, state it explicitly; if "
        "you are not confident of the exact URL, say so rather than "
        "guessing or constructing one.",
        "",
        f"Firmographic filters: {spec['firmographic_filters']}",
        f"Technographic filters: {spec['technographic_filters']}",
        f"Buying-signal filters to prioritize when evident: {spec['buying_signal_filters']}",
    ]
    if target_location:
        lines.append(
            f"Target location: companies HEADQUARTERED IN / BASED IN {target_location} "
            f"— not global/multinational companies that merely have some operations, "
            f"offices, or sales presence there. Every candidate's actual home base must "
            f"be {target_location}."
        )
    else:
        lines.append("Target location: not specified — consider any region.")
    if exclude_names:
        lines.append(
            "\nDo NOT suggest any of these companies again — already considered in a "
            "prior pass: " + ", ".join(exclude_names)
        )
    lines.append(f"\nIdentify at least {buffer_count} distinct real companies matching the above.")
    lines.append("For each, briefly explain why it matches, citing your sources.")
    return "\n".join(lines)


def _find_linkedin_url_with_exa(company_name: str) -> Optional[str]:
    """Looks up a company's LinkedIn company-page URL via Exa search, for
    candidates Perplexity named but wasn't confident enough to state a
    URL for. Best-effort: missing key, no matching result, or a failed
    call all just return None so the caller drops the candidate rather
    than guessing a URL itself."""
    try:
        client = get_exa_client()
    except RuntimeError as e:
        print(f"  (skipping Exa LinkedIn lookup: {e})")
        return None
    try:
        response = client.search(f"{company_name} official LinkedIn company page", num_results=5)
        for r in response.results:
            if "linkedin.com/company/" in r.url:
                return r.url
        return None
    except Exception as e:
        print(f"  (Exa LinkedIn lookup failed for {company_name}: {e})")
        return None


def _names_plausibly_match(candidate_name: str, scraped_name: str) -> bool:
    """Sanity-checks that the LinkedIn page Apify actually scraped is for
    the company Perplexity/Exa intended, not a different, similarly-named
    company that Exa's search returned by mistake (Exa's LinkedIn lookup
    is a generic web search, not a guaranteed-correct entity match). Uses
    substring containment plus a loose similarity ratio rather than exact
    match, since LinkedIn names commonly differ in suffix/legal form
    (e.g. "Tata Motors" vs "Tata Motors Limited")."""
    if not scraped_name:
        return False
    a = candidate_name.strip().lower()
    b = scraped_name.strip().lower()
    if a in b or b in a:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.6


def _verify_candidate(c: dict, resolved_location: str) -> tuple:
    """Runs one candidate through the Exa-lookup + Apify-scrape + name-match
    + deterministic-location-check pipeline. Returns
    (verified_entry_or_None, unverified_reason_or_None) — exactly one of
    the pair is non-None. Shared by both `discover_and_verify_candidates`
    (target accounts) and the Lookalike Account Agent, which reuses it as
    `target_account_agent._verify_candidate`."""
    if not c.get("linkedin_url"):
        print(f"  looking up LinkedIn URL for {c['company_name']} via Exa...")
        found_url = _find_linkedin_url_with_exa(c["company_name"])
        if not found_url:
            return None, f"{c['company_name']} (no LinkedIn URL found via research or Exa lookup)"
        c["linkedin_url"] = found_url
    print(f"  verifying {c['company_name']} via Apify LinkedIn scrape...")
    apify_data = scrape_linkedin_company(c["linkedin_url"])
    if not apify_data:
        return None, f"{c['company_name']} (LinkedIn scrape failed)"
    scraped_name = apify_data.get("name", "")
    if not _names_plausibly_match(c["company_name"], scraped_name):
        return None, (
            f"{c['company_name']} (scraped LinkedIn page is for '{scraped_name}', not a "
            f"confident name match — likely the wrong company's URL, dropped)"
        )
    if resolved_location:
        location_result = _location_check(apify_data.get("headquarters", ""), resolved_location)
        if location_result is False:
            hq = apify_data.get("headquarters") or "unknown"
            return None, (
                f"{c['company_name']} (headquartered in '{hq}', not '{resolved_location}' — "
                f"dropped for location mismatch, confirmed deterministically)"
            )
        # True (confirmed) or None (couldn't resolve, deferred to the
        # scoring step's best-effort judgment) both proceed.
    return {"candidate": c, "apify_data": apify_data}, None


def discover_and_verify_candidates(
    build_prompt_fn, structuring_context: str, resolved_location: str, count: int,
    max_rounds: int = DISCOVERY_MAX_ROUNDS, initial_excluded_names: Optional[List[str]] = None,
) -> tuple:
    """Runs discovery+verification in rounds until `count` candidates are
    verified or `max_rounds` is exhausted. `build_prompt_fn(buffer_count,
    exclude_names)` builds the Perplexity research prompt for one round —
    target_account_agent and lookalike_account_agent each supply their own
    (different discovery framing, same verification). Every company name
    seen in any round (verified or not) is excluded from later rounds so a
    top-up round doesn't just re-surface the same rejects.

    `initial_excluded_names`, if given, seeds the exclusion set before round
    1 — used by the Lookalike Account Agent to keep its seed accounts (and
    anything the prior target-accounts run already rejected) out of its own
    results, not just names this call itself discovers.

    Returns (verified, unverified_names) — `verified` is a list of
    {"candidate", "apify_data"} dicts ready for `_score_verified_candidates`."""
    verified: List[dict] = []
    unverified_names: List[str] = []
    excluded_lower = {n.strip().lower() for n in (initial_excluded_names or [])}

    for round_num in range(1, max_rounds + 1):
        remaining = count - len(verified)
        if remaining <= 0:
            break
        buffer_count = remaining * DISCOVERY_BUFFER_MULTIPLIER
        prompt = build_prompt_fn(buffer_count, sorted(excluded_lower))
        if round_num > 1:
            print(f"  discovering more candidate companies with Perplexity (round {round_num}, need {remaining} more)...")
        else:
            print("  discovering candidate companies with Perplexity...")
        discovery_result = run_research_pipeline(
            record_tool=DISCOVERY_RECORD_TOOL,
            research_prompt=prompt,
            structuring_context=structuring_context,
        )
        candidates = [
            c for c in discovery_result["candidates"]
            if c["company_name"].strip().lower() not in excluded_lower
        ]
        if not candidates:
            break  # nothing new came back — further rounds won't help either

        for c in candidates:
            excluded_lower.add(c["company_name"].strip().lower())
            entry, reason = _verify_candidate(c, resolved_location)
            if entry:
                verified.append(entry)
            else:
                unverified_names.append(reason)

    return verified, unverified_names


def _format_verified_candidate(candidate: dict, apify_data: dict, target_location: str) -> str:
    fields = [
        ("Name (per LinkedIn)", apify_data.get("name")),
        ("Description", apify_data.get("description")),
        ("Industry", apify_data.get("industry")),
        ("Company size", apify_data.get("companySize")),
        ("Employee count", apify_data.get("employeeCount")),
        ("Headquarters", apify_data.get("headquarters")),
        ("Website", apify_data.get("website")),
        ("Specialties", apify_data.get("specialties")),
    ]
    present = "\n".join(f"  {label}: {value}" for label, value in fields if value)

    if not target_location:
        location_line = "Location check: no target location specified for this run."
    else:
        headquarters = apify_data.get("headquarters", "")
        result = _location_check(headquarters, target_location)
        if result is True:
            location_line = f"Location check: confirmed in {target_location} (deterministic, via headquarters '{headquarters}')."
        else:
            # False shouldn't reach here (dropped upstream) — only None does.
            location_line = (
                f"Location check: could not be automatically confirmed against "
                f"'{target_location}' (raw headquarters: '{headquarters or 'unknown'}') "
                f"— use your own geography judgment."
            )

    return (
        f"Candidate: {candidate['company_name']}\n"
        f"LinkedIn: {candidate['linkedin_url']}\n"
        f"Discovery rationale: {candidate['rationale']}\n"
        f"{location_line}\n"
        f"Verified LinkedIn data (Tier 1, first-party, scraped via Apify):\n{present}"
    )


def _score_verified_candidates(verified: List[dict], spec: dict, rubric: List[dict], target_location: str, count: int) -> dict:
    rubric_lines = [f"- {c['criterion']} (weight: {c['weight']}) — {c['how_to_score']}" for c in rubric]
    candidate_blocks = [_format_verified_candidate(v["candidate"], v["apify_data"], target_location) for v in verified]

    user_message = (
        f"Target location: {target_location or 'not specified'}\n"
        f"N (top candidates that will actually be kept): {count}\n\n"
        "QUALIFIED ACCOUNT SPEC:\n"
        f"Firmographic filters: {spec['firmographic_filters']}\n"
        f"Technographic filters: {spec['technographic_filters']}\n"
        f"Buyer titles: {', '.join(spec['buyer_titles'])}\n"
        f"Buying-signal filters: {spec['buying_signal_filters']}\n"
        f"Minimum fit score to pursue: {spec['minimum_fit_score']}\n\n"
        "SCORING RUBRIC:\n" + "\n".join(rubric_lines) + "\n\n"
        "VERIFIED CANDIDATES:\n\n" + "\n\n".join(candidate_blocks)
    )

    return call_openai_structured(
        system=SCORING_SYSTEM_PROMPT,
        user_message=user_message,
        tool_name="record_target_account_scoring",
        input_schema=SCORING_RECORD_SCHEMA,
    )


def run_target_account_discovery(
    session_data: dict,
    target_location: Optional[str] = None,
    count: int = 5,
) -> TargetAccountListOutput:
    """Runs the Target Account Agent to completion. Requires
    `icp_discovery` to already exist in `session_data` (raises RuntimeError
    otherwise) — everything else (Market Sizing, secondary research) is
    unused directly by this phase; it scores strictly against the ICP's
    own scoring_rubric and qualified_account_spec.

    `target_location` overrides whatever's on `founder_input.target_location`
    for this run; if neither is set, discovery proceeds with no location
    filter."""
    if "icp_discovery" not in session_data:
        raise RuntimeError(
            "Target Account Agent requires ICP Discovery to have been run "
            "first — it scores candidates against Phase 4's scoring rubric "
            "and qualified-account spec. Run `icp` before `target-accounts`."
        )

    icp = session_data["icp_discovery"]
    spec = icp["qualified_account_spec"]
    rubric = icp["scoring_rubric"]

    resolved_location = target_location or session_data.get("founder_input", {}).get("target_location") or ""

    def build_prompt(buffer_count: int, exclude_names: List[str]) -> str:
        return _build_discovery_prompt(spec, resolved_location, buffer_count, exclude_names)

    verified, unverified_names = discover_and_verify_candidates(
        build_prompt, DISCOVERY_STRUCTURING_CONTEXT, resolved_location, count,
    )

    if not verified:
        return TargetAccountListOutput(
            target_location=resolved_location,
            accounts=[],
            unverified_candidates=unverified_names,
            summary=(
                "No candidate companies could be verified via a real LinkedIn "
                "scrape. Try again, or widen the target-account filters / location."
            ),
        )

    print("  scoring verified candidates against the ICP rubric...")
    scoring_result = _score_verified_candidates(verified, spec, rubric, resolved_location, count)

    accounts = [TargetAccount(**a) for a in scoring_result["ranked_accounts"][:count]]
    all_unverified = unverified_names + scoring_result.get("location_mismatches", [])
    return TargetAccountListOutput(
        target_location=resolved_location,
        accounts=accounts,
        unverified_candidates=all_unverified,
        summary=scoring_result["summary"],
    )
