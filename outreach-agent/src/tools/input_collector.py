"""
Input Collector
Collects sender/receiver profiles and outreach parameters
from the terminal (interactive) or a JSON file.
"""

import json
import sys
import os
from typing import Optional


def prompt_single(label: str, hint: str = "") -> str:
    print(f"\n  📝 {label}")
    if hint:
        print(f"     ({hint})")
    return input("     → ").strip()


def prompt_multiline(label: str, hint: str = "") -> str:
    print(f"\n  📝 {label}")
    if hint:
        print(f"     ({hint})")
    print("     Enter text. Press Enter twice to finish:")
    lines = []
    while True:
        line = input("     ")
        if line == "" and lines:
            break
        lines.append(line)
    return " ".join(lines).strip()


def validate_sequence_type(value: str) -> str:
    v = value.strip().lower()
    if "email" in v and "linkedin" not in v:
        return "Email"
    elif "linkedin" in v and "email" not in v:
        return "LinkedIn"
    else:
        return "Both"


def collect_inputs(json_path: Optional[str] = None) -> dict:
    if json_path:
        if not os.path.exists(json_path):
            print(f"❌ File not found: {json_path}")
            sys.exit(1)
        with open(json_path) as f:
            data = json.load(f)
        print(f"\n✅ Inputs loaded from: {json_path}")
        _print_summary(data)
        return data

    print("\n" + "═" * 58)
    print("  14-21 DAY NURTURE SEQUENCE AGENT")
    print("  Powered by Claude · Converts Cold Leads into MQLs")
    print("═" * 58)

    data = {}

    print("\n\n── SENDER PROFILE ──────────────────────────────────────")
    data["sender_name"] = prompt_single("Your Name", "e.g. Karthikeyan R")
    data["sender_role"] = prompt_single("Your Role", "e.g. AI GTM Engineer")
    data["sender_company"] = prompt_single("Your Company", "e.g. e-ideaCS")
    data["sender_summary"] = prompt_multiline(
        "Your Profile Summary",
        "2-4 sentences: background, expertise, what you do"
    )

    print("\n── RECEIVER / TARGET PROFILE ───────────────────────────")
    data["receiver_name"] = prompt_single("Receiver Name", "e.g. Arjun Menon")
    data["receiver_role"] = prompt_single("Receiver Role", "e.g. Co-founder & CEO")
    data["receiver_company"] = prompt_single("Receiver Company", "e.g. GrowthPilot AI")
    data["receiver_summary"] = prompt_multiline(
        "Receiver Profile Summary",
        "2-4 sentences: their role, company stage, focus area, recent context"
    )

    print("\n── OUTREACH DETAILS ─────────────────────────────────────")
    data["outreach_goal"] = prompt_single(
        "Outreach Goal",
        "e.g. Book a 20-min discovery call"
    )
    data["offer"] = prompt_multiline(
        "Your Offer / Service",
        "What are you offering? Key benefits? Who is it for?"
    )
    data["asset_name"] = prompt_single(
        "Lead Asset Name (for Day 0)",
        "e.g. 'GTM Intelligence Playbook', 'ICP Scoring Template', or 'N/A' if no asset"
    )
    data["pain_points"] = prompt_multiline(
        "Top 3 Pain Points of your ICP",
        "List 3 pains separated by commas or new lines. These drive Hot Button emails."
    )
    data["tone"] = prompt_single(
        "Preferred Tone",
        "e.g. Friendly peer-level, Direct and concise, Warm consultant"
    )
    seq_raw = prompt_single("Sequence Type", "Email / LinkedIn / Both")
    data["sequence_type"] = validate_sequence_type(seq_raw)

    print("\n\n✅ All inputs collected.\n")
    return data


def _print_summary(data: dict):
    print("\n── LOADED INPUTS ────────────────────────────────────────")
    fields = [
        ("sender_name", "Sender"),
        ("sender_role", "Sender Role"),
        ("receiver_name", "Receiver"),
        ("receiver_role", "Receiver Role"),
        ("receiver_company", "Receiver Company"),
        ("outreach_goal", "Goal"),
        ("tone", "Tone"),
        ("sequence_type", "Sequence Type"),
    ]
    for key, label in fields:
        val = data.get(key, "N/A")
        print(f"  {label}: {val}")
    print("─" * 58)
