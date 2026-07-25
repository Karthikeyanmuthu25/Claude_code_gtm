"""
Personalization Skill
Analyzes sender and receiver profiles to extract:
- Outreach angle
- ICP pain point hooks
- Sender credibility anchors
- Connection points to seed the sequence prompt
"""

import re
from typing import List


def build_personalization_context(inputs: dict) -> dict:
    pain_points = _parse_pain_points(inputs.get("pain_points", ""))
    return {
        "sender_credibility": _extract_sender_credibility(inputs),
        "receiver_hooks": _extract_receiver_hooks(inputs),
        "pain_point_list": pain_points,
        "hot_button_map": _map_hot_buttons(pain_points, inputs),
        "sequence_type": inputs.get("sequence_type", "Both"),
    }


def _parse_pain_points(raw: str) -> List[str]:
    """Extract up to 3 pain points from free-text input."""
    if not raw:
        return [
            "Manual, time-consuming GTM research process",
            "Inability to identify high-intent leads at speed",
            "No systematic ICP scoring or signal tracking",
        ]
    # Try comma split first, then newline
    if "," in raw:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in raw.splitlines() if p.strip()]
    # Pad to 3 if fewer provided
    defaults = [
        "manual research overhead",
        "slow lead qualification",
        "missed timing on buyer signals",
    ]
    while len(parts) < 3:
        parts.append(defaults[len(parts)])
    return parts[:3]


def _extract_sender_credibility(inputs: dict) -> str:
    role = inputs.get("sender_role", "")
    company = inputs.get("sender_company", "")
    summary = inputs.get("sender_summary", "")
    return f"{role} at {company}. {summary}".strip()


def _extract_receiver_hooks(inputs: dict) -> List[str]:
    hooks = []
    role = inputs.get("receiver_role", "")
    company = inputs.get("receiver_company", "")
    summary = inputs.get("receiver_summary", "")
    if role:
        hooks.append(f"Role: {role}")
    if company:
        hooks.append(f"Company: {company}")
    if summary:
        hooks.append(f"Context: {summary}")
    return hooks


def _map_hot_buttons(pain_points: List[str], inputs: dict) -> dict:
    """Map each pain point to the email day it anchors."""
    return {
        "hot_button_1": pain_points[0],
        "hot_button_2": pain_points[1],
        "hot_button_3": pain_points[2],
    }


# NOTE: this used to contain _infer_connection_angle(), a keyword-matching
# guesser that picked a connection angle from words in the offer text (e.g.
# "lead"/"pipeline" → "pipeline quality / time-to-MQL" angle). It once guessed
# that angle for a real-estate asset-management buyer, which was simply wrong,
# and the LLM had to notice and override it in the human-review notes. Keyword
# matching on the offer has no idea who the receiver actually is — it injects
# noise, not signal. The connection angle is now derived by the LLM directly
# from receiver_hooks/receiver_summary at generation time (see
# sequence_skill.py), which is the only place enough real context exists to
# get it right. See knowledge/brain.md → "Known heuristic failure" for detail.
