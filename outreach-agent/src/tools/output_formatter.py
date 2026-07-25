"""
Output Formatter
Saves the generated nurture sequence to a rich Markdown report
and a JSON data file.
"""

import os
import json
import re
from datetime import datetime


OUTPUT_DIR = "output"


def _sanitize(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name.lower().strip())


def _ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _base_name(inputs: dict) -> str:
    receiver = _sanitize(inputs.get("receiver_name", "receiver"))
    company = _sanitize(inputs.get("receiver_company", "company"))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"nurture_{receiver}_{company}_{ts}"


def format_and_save(raw_output: str, inputs: dict, fit_report: dict = None, lint_report: dict = None) -> dict:
    _ensure_dir()
    base = _base_name(inputs)
    fit_report = fit_report or {}
    lint_report = lint_report or {}

    md_content = _build_markdown(raw_output, inputs, fit_report, lint_report)
    md_path = os.path.join(OUTPUT_DIR, f"{base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    json_data = {
        "generated_at": datetime.now().isoformat(),
        "inputs": inputs,
        "sequence_type": inputs.get("sequence_type", "Both"),
        "output_file": md_path,
        "raw_output": raw_output,
        "fit_report": fit_report,
        "lint_report": lint_report,
        # Filled in later by scripts/review.py — makes human review a tracked
        # gate instead of freeform notes, and captures edits as a diffable
        # signal against raw_output.
        "review": {
            "status": "draft",  # draft | approved | edited | rejected
            "reviewer": None,
            "reviewed_at": None,
            "edited_text": None,
            "notes": None,
        },
        # Filled in later by scripts/log_outcome.py — this is what makes
        # feedback-based optimization possible at all. Without this, nothing
        # in the system ever learns from a real send.
        "outcomes": _init_outcomes(inputs),
    }
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    _print_terminal(raw_output, md_path, json_path)

    return {"markdown_path": md_path, "json_path": json_path, "raw_output": raw_output}


def _init_outcomes(inputs: dict) -> dict:
    seq_type = inputs.get("sequence_type", "Both")
    touches = {}
    if seq_type in ("Email", "Both"):
        for day in ("day_0", "day_1", "day_3", "day_5", "day_14", "day_21"):
            touches[day] = _blank_outcome()
    if seq_type in ("LinkedIn", "Both"):
        for step in ("li_step_1", "li_step_2", "li_step_3", "li_step_4"):
            touches[step] = _blank_outcome()
    return touches


def _blank_outcome() -> dict:
    return {
        "sent_at": None,
        "opened": None,
        "replied": None,
        "meeting_booked": None,
        "bounced": None,
        "notes": None,
    }


def _build_markdown(raw_output: str, inputs: dict, fit_report: dict = None, lint_report: dict = None) -> str:
    now = datetime.now().strftime("%B %d, %Y %H:%M")
    seq_type = inputs.get("sequence_type", "Both")
    fit_report = fit_report or {}
    lint_report = lint_report or {}

    # Sequence timeline label
    if seq_type == "Email":
        timeline = "6-Email nurture (Day 0 → Day 21)"
    elif seq_type == "LinkedIn":
        timeline = "4-Step LinkedIn nurture"
    else:
        timeline = "6-Email + 4-Step LinkedIn nurture (Day 0 → Day 21)"

    header = f"""# 14-21 Day Nurture Sequence Report

**Generated:** {now}

---

## Campaign Overview

| Field | Value |
|-------|-------|
| **Sender** | {inputs.get("sender_name", "")} — {inputs.get("sender_role", "")} @ {inputs.get("sender_company", "")} |
| **Receiver** | {inputs.get("receiver_name", "")} — {inputs.get("receiver_role", "")} @ {inputs.get("receiver_company", "")} |
| **Outreach Goal** | {inputs.get("outreach_goal", "")} |
| **Tone** | {inputs.get("tone", "")} |
| **Sequence** | {timeline} |
| **Asset (Day 0)** | {inputs.get("asset_name", "N/A")} |

---

## Pre-Send QA

| Check | Result |
|-------|--------|
| **ICP Fit Score** | {fit_report.get("score", "n/a")}/100 |
| **Fit Notes** | {"; ".join(fit_report.get("reasons", [])) or "n/a"} |
| **Lint Status** | {"✅ Passed" if lint_report.get("passed") else f"⚠️ {len(lint_report.get('violations', []))} unresolved issue(s)"} |
| **Lint Violations** | {"; ".join(lint_report.get("violations", [])) or "None"} |
| **Lint Warnings** | {"; ".join(lint_report.get("warnings", [])) or "None"} |

Review status, reviewer, and send outcomes are tracked in the companion `.json`
file (`review` / `outcomes` keys) — update them with `scripts/review.py` and
`scripts/log_outcome.py`, not by hand.

---

## Nurture Timeline

```
Day 0  → Asset Delivery       Send lead asset. Zero pitch.
Day 1  → Hot Button 1         Most pressing pain point
Day 3  → Hot Button 2         Secondary pain + story
Day 5  → Hot Button 3         Third pain + introduce framework
Day 14 → Probing Question     One honest diagnostic question
Day 21 → Breakup Email        Close loop. Leave door open.

LinkedIn (parallel):
Step 1 → Connection Request   (Day 0)
Step 2 → Post-accept warm     (Day 1-2)
Step 3 → Follow-up value      (Day 5-7)
Step 4 → Soft close           (Day 14-21)
```

---

{raw_output}

---

*Generated by the 14-21 Day Nurture Sequence Agent · Powered by Claude*
"""
    return header


def _print_terminal(raw_output: str, md_path: str, json_path: str):
    print("\n" + "═" * 58)
    print("  ✅ NURTURE SEQUENCE GENERATED")
    print("═" * 58)
    print(raw_output)
    print("\n" + "═" * 58)
    print(f"  📄 Markdown → {md_path}")
    print(f"  📦 JSON     → {json_path}")
    print("═" * 58 + "\n")
