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
        "connection_angle": _infer_connection_angle(inputs),
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


def _infer_connection_angle(inputs: dict) -> str:
    sender_role = inputs.get("sender_role", "").lower()
    receiver_role = inputs.get("receiver_role", "").lower()
    offer = inputs.get("offer", "").lower()

    if any(w in offer for w in ["ai", "automation", "agent", "intelligence"]):
        if any(w in receiver_role for w in ["founder", "ceo", "cto", "head"]):
            return (
                "AI-efficiency angle — position around intelligence uplift "
                "and time reclaimed for founder-level thinking"
            )
    if any(w in sender_role for w in ["gtm", "growth", "sales"]):
        return (
            "peer GTM angle — sender brings tactical, hands-on GTM engineering "
            "credibility that mirrors the receiver's growth challenges"
        )
    if any(w in offer for w in ["lead", "icp", "pipeline", "prospect"]):
        return (
            "pipeline quality angle — position around better qualified leads "
            "and reduced time-to-MQL"
        )
    return (
        "value-first angle — lead with insight and education before any product mention"
    )
