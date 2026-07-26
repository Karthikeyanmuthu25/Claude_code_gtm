"""
Lookalike Account Agent — Phase 4d.

Takes the Target Account Agent's verified `target_accounts.accounts` as a
seed set and discovers MORE real, LinkedIn-verified companies that
resemble them. Requires `target_accounts` (and transitively `icp_discovery`,
since target-accounts requires it) to already exist in session_data.

Same three-stage pipeline as target_account_agent.py — PERPLEXITY+OPENAI
discovery, EXA+APIFY verification, OPENAI scoring against the ICP's
scoring_rubric — reusing that module's `discover_and_verify_candidates`
orchestrator (multi-round, top-up-until-`count` discovery/verification)
and `_score_verified_candidates` unchanged. Lookalikes still need to be
genuinely qualified accounts (same rubric, same location check), just
discovered via a different signal: the discovery prompt asks Perplexity
for companies similar to the already-verified seed accounts' real profiles
(industry, size, description), instead of matching the ICP spec's raw
filters directly.

Already-seen company names — both the seed accounts themselves and
anything the prior target-accounts run dropped as unverified — seed the
orchestrator's exclusion set from round 1 onward (via
`initial_excluded_names`), so a top-up round doesn't just re-surface the
same seeds or already-rejected names.
"""
from typing import List, Optional

import target_account_agent as taa
from models import TargetAccount, TargetAccountListOutput

LOOKALIKE_DISCOVERY_STRUCTURING_CONTEXT = (
    "This research is identifying real LOOKALIKE candidate companies — "
    "similar to a set of already-verified example accounts given in the "
    "prompt. Only extract companies actually named in the research text "
    "below — do not invent any, and do not re-list any of the example "
    "accounts themselves. Leave linkedin_url as an empty string for any "
    "company whose exact LinkedIn URL isn't confidently stated in the "
    "text, rather than guessing or constructing one."
)


def _build_lookalike_discovery_prompt(
    seed_accounts: List[dict],
    spec: dict,
    target_location: str,
    exclude_names: List[str],
    buffer_count: int,
) -> str:
    seed_lines = [
        f"- {a['company_name']} — {a['industry']}, {a['employee_count']} employees. {a['fit_score_rationale']}"
        for a in seed_accounts
    ]
    lines = [
        "You are identifying REAL, SPECIFIC, NAMED companies (not made-up "
        "or example companies) that are LOOKALIKES of the example accounts "
        "below — similar in industry, company size, business model, and "
        "buying signals. Do NOT just re-list the example accounts "
        "themselves. For each new company, name it exactly. If you know "
        "its exact public LinkedIn company-page URL, state it explicitly; "
        "if you are not confident of the exact URL, say so rather than "
        "guessing or constructing one.",
        "",
        "EXAMPLE ACCOUNTS TO FIND LOOKALIKES OF (already verified, real):",
        *seed_lines,
        "",
        f"Firmographic filters (for context — lookalikes should still roughly fit): {spec['firmographic_filters']}",
        f"Technographic filters: {spec['technographic_filters']}",
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
            "\nDo NOT suggest any of the following companies — already considered in a "
            "prior pass: " + ", ".join(exclude_names)
        )
    lines.append(f"\nIdentify at least {buffer_count} distinct real lookalike companies matching the above.")
    lines.append("For each, briefly explain what makes it a lookalike of the example accounts, citing your sources.")
    return "\n".join(lines)


def run_lookalike_account_discovery(
    session_data: dict,
    target_location: Optional[str] = None,
    count: int = 5,
) -> TargetAccountListOutput:
    """Runs the Lookalike Account Agent to completion. Requires
    `target_accounts` to already exist in `session_data` with at least one
    verified account (raises RuntimeError otherwise) — that's the seed set
    lookalikes are discovered from. Scores against the same ICP
    scoring_rubric/qualified_account_spec target_account_agent uses.

    `target_location` overrides whatever's on the prior target-accounts
    run / `founder_input.target_location`, in that order."""
    if "target_accounts" not in session_data:
        raise RuntimeError(
            "Lookalike Account Agent requires Target Account Agent to have "
            "been run first — it uses its verified accounts as the seed "
            "set to find similar companies. Run `target-accounts` before "
            "`lookalike-accounts`."
        )
    if "icp_discovery" not in session_data:
        raise RuntimeError(
            "Lookalike Account Agent requires ICP Discovery to have been "
            "run first — it scores candidates against Phase 4's scoring "
            "rubric and qualified-account spec, same as Target Account Agent."
        )

    ta = session_data["target_accounts"]
    seed_accounts = ta.get("accounts") or []
    if not seed_accounts:
        raise RuntimeError(
            "Lookalike Account Agent requires at least one verified target "
            "account to use as a seed, but the prior target-accounts run "
            "produced none. Re-run `target-accounts` (or widen its filters/"
            "location) first."
        )

    icp = session_data["icp_discovery"]
    spec = icp["qualified_account_spec"]
    rubric = icp["scoring_rubric"]

    resolved_location = (
        target_location
        or ta.get("target_location")
        or session_data.get("founder_input", {}).get("target_location")
        or ""
    )

    base_exclude_names = [a["company_name"] for a in seed_accounts]
    for u in ta.get("unverified_candidates", []):
        # unverified_candidates entries are formatted as "Name (reason...)".
        base_exclude_names.append(u.split(" (")[0].strip())

    def build_prompt(buffer_count: int, round_exclude_names: List[str]) -> str:
        # round_exclude_names already includes base_exclude_names, since
        # discover_and_verify_candidates seeds its exclusion set with them.
        return _build_lookalike_discovery_prompt(
            seed_accounts, spec, resolved_location, round_exclude_names, buffer_count,
        )

    verified, unverified_names = taa.discover_and_verify_candidates(
        build_prompt, LOOKALIKE_DISCOVERY_STRUCTURING_CONTEXT, resolved_location, count,
        initial_excluded_names=base_exclude_names,
    )

    if not verified:
        return TargetAccountListOutput(
            target_location=resolved_location,
            accounts=[],
            unverified_candidates=unverified_names,
            summary=(
                "No lookalike candidate companies could be verified via a real "
                "LinkedIn scrape. Try again, or widen the target-account filters / location."
            ),
        )

    print("  scoring verified lookalike candidates against the ICP rubric...")
    scoring_result = taa._score_verified_candidates(verified, spec, rubric, resolved_location, count)

    accounts = [TargetAccount(**a) for a in scoring_result["ranked_accounts"][:count]]
    all_unverified = unverified_names + scoring_result.get("location_mismatches", [])
    return TargetAccountListOutput(
        target_location=resolved_location,
        accounts=accounts,
        unverified_candidates=all_unverified,
        summary=scoring_result["summary"],
    )
