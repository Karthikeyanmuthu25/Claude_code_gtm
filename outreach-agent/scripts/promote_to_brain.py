#!/usr/bin/env python3
"""
Promote a proven pattern into knowledge/brain.md so future generations start
from real field experience instead of zero. This is what closes the loop:
generate -> review/send -> measure (log_outcome/analyze_outcomes) -> promote
the pattern that worked -> next generation is grounded in it.

Refuses to promote a sequence with no supporting evidence unless --force is
passed, so the brain stays a record of what's actually working, not a dumping
ground for untested guesses.

Usage:
  python scripts/promote_to_brain.py --file output/nurture_x.json \
      --section "Angle patterns that have worked" \
      --note "Naming the specific compliance/timeline advantage up front worked for facilities buyers."
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "brain.md")


def has_evidence(data: dict) -> bool:
    review_status = data.get("review", {}).get("status")
    if review_status in ("approved", "edited"):
        return True
    for outcome in data.get("outcomes", {}).values():
        if outcome.get("replied") or outcome.get("meeting_booked"):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Append a proven pattern to knowledge/brain.md")
    parser.add_argument("--file", required=True, help="Path to the sequence's .json output file")
    parser.add_argument("--section", required=True,
                         help='Existing "## " heading in knowledge/brain.md to add this note under')
    parser.add_argument("--note", required=True, help="The pattern/learning to record, as a single bullet")
    parser.add_argument("--force", action="store_true",
                         help="Promote even though the sequence has no approved review or logged reply/meeting")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    if not has_evidence(data) and not args.force:
        print(
            "⚠️  Refusing to promote: this sequence has no 'approved'/'edited' review status "
            "and no logged reply/meeting outcome. Run scripts/review.py or scripts/log_outcome.py "
            "first, or pass --force if you're promoting a manually-verified insight."
        )
        return 1

    if not os.path.exists(BRAIN_PATH):
        print(f"❌ {BRAIN_PATH} not found.")
        return 1

    with open(BRAIN_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    heading = f"## {args.section}"
    heading_idx = next((i for i, line in enumerate(lines) if line.strip() == heading), None)
    if heading_idx is None:
        existing = [line.strip() for line in lines if line.startswith("## ")]
        print(f'❌ Section "{heading}" not found in brain.md. Existing sections:')
        for s in existing:
            print(f"   {s}")
        return 1

    next_heading_idx = heading_idx + 1
    while next_heading_idx < len(lines) and not lines[next_heading_idx].startswith("## "):
        next_heading_idx += 1

    # Walk back past trailing blank lines so the bullet lands right after the
    # section's last content line, preserving the blank-line gap before the
    # next heading instead of gluing straight onto it.
    insert_idx = next_heading_idx
    while insert_idx > heading_idx + 1 and lines[insert_idx - 1].strip() == "":
        insert_idx -= 1

    receiver = data.get("inputs", {}).get("receiver_company", "unknown")
    bullet = f"- {args.note} (source: {os.path.basename(args.file)}, {receiver})\n"
    lines.insert(insert_idx, bullet)

    with open(BRAIN_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f'✅ Promoted to brain.md under "{heading}":\n   {bullet.strip()}')


if __name__ == "__main__":
    sys.exit(main())
