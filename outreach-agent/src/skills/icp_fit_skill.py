"""
ICP Fit Skill
Pre-generation gate: scores whether this lead has enough real signal to justify
spending a full 6-email + 4-LinkedIn sequence on them. This is a heuristic on
input *completeness and specificity* (there's no external enrichment data
here) — it catches "we're about to generate a generic sequence because the
brief is thin" before burning tokens on it, not "this is/isn't a good company."
"""

from typing import Dict, List, Tuple

_GENERIC_PHRASES = [
    "n/a", "tbd", "unknown", "not sure", "generic company", "test",
]

_DEFAULT_PAIN_POINTS = {
    "manual, time-consuming gtm research process",
    "inability to identify high-intent leads at speed",
    "no systematic icp scoring or signal tracking",
}


def score_fit(inputs: Dict) -> Dict:
    score = 100
    reasons: List[str] = []

    score, reasons = _check_summary(inputs, score, reasons)
    score, reasons = _check_pain_points(inputs, score, reasons)
    score, reasons = _check_field(inputs, "receiver_role", 10, score, reasons)
    score, reasons = _check_field(inputs, "receiver_company", 10, score, reasons)
    score, reasons = _check_field(inputs, "outreach_goal", 10, score, reasons)
    score, reasons = _check_offer(inputs, score, reasons)

    asset = inputs.get("asset_name", "").strip().lower()
    if not asset or asset in _GENERIC_PHRASES:
        score -= 5
        reasons.append("No Day-0 asset — weakens the zero-pitch opener (-5)")

    score = max(0, min(100, score))
    if not reasons:
        reasons.append("Strong signal across all fields")
    return {"score": score, "reasons": reasons}


def _check_field(inputs: Dict, key: str, penalty: int, score: int, reasons: List[str]) -> Tuple[int, List[str]]:
    val = inputs.get(key, "").strip().lower()
    if not val or val in _GENERIC_PHRASES:
        score -= penalty
        reasons.append(f"Missing or placeholder '{key}' (-{penalty})")
    return score, reasons


def _check_summary(inputs: Dict, score: int, reasons: List[str]) -> Tuple[int, List[str]]:
    summary = inputs.get("receiver_summary", "").strip()
    word_count = len(summary.split())
    if not summary:
        score -= 30
        reasons.append("Missing receiver_summary — generation will default to generic angle (-30)")
    elif word_count < 15:
        score -= 15
        reasons.append(f"receiver_summary is thin ({word_count} words) — generic output risk (-15)")
    return score, reasons


def _check_pain_points(inputs: Dict, score: int, reasons: List[str]) -> Tuple[int, List[str]]:
    raw = inputs.get("pain_points", "").strip().lower()
    if not raw:
        score -= 20
        reasons.append("No pain_points supplied — Hot Button emails will use generic defaults (-20)")
        return score, reasons
    parts = {p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()}
    if parts <= _DEFAULT_PAIN_POINTS:
        score -= 20
        reasons.append("pain_points match the generic fallback set, not this lead's real pains (-20)")
    return score, reasons


def _check_offer(inputs: Dict, score: int, reasons: List[str]) -> Tuple[int, List[str]]:
    offer = inputs.get("offer", "").strip()
    if not offer:
        score -= 10
        reasons.append("Missing offer (-10)")
    elif len(offer.split()) < 8:
        score -= 5
        reasons.append("offer is very short — may lack enough detail to personalize (-5)")
    return score, reasons
