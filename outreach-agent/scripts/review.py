#!/usr/bin/env python3
"""
Record a human review decision against a generated sequence — turns "Notes
for Human Review" from freeform text into a tracked gate with a real status
and (optionally) the edited-as-sent text, so human corrections become a
diffable signal instead of being thrown away.

Usage:
  python scripts/review.py --file output/nurture_x.json --status approved --reviewer Karthikeyan
  python scripts/review.py --file output/nurture_x.json --status edited --reviewer Karthikeyan \
      --edited-text-file output/nurture_x_edited.md --notes "tightened Day 1 opener"
  python scripts/review.py --file output/nurture_x.json --status rejected --notes "wrong angle, regenerate"
"""

import argparse
import json
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description="Record a human review decision.")
    parser.add_argument("--file", required=True, help="Path to the sequence's .json output file")
    parser.add_argument("--status", required=True, choices=["approved", "edited", "rejected"])
    parser.add_argument("--reviewer", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--edited-text-file", default=None,
                         help="Path to a file containing the final, human-edited sequence text "
                              "(required/typical when --status edited)")
    args = parser.parse_args()

    if args.status == "edited" and not args.edited_text_file:
        parser.error("--status edited should be paired with --edited-text-file so the edit is captured as a diff")

    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    review = data.setdefault("review", {})
    review["status"] = args.status
    review["reviewer"] = args.reviewer
    review["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    review["notes"] = args.notes

    if args.edited_text_file:
        with open(args.edited_text_file, encoding="utf-8") as f:
            review["edited_text"] = f.read()

    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Review recorded: {args.status} on {args.file}")
    if args.status == "edited":
        print("   Edited text captured — this diff is exactly what scripts/promote_to_brain.py "
              "should learn from.")


if __name__ == "__main__":
    sys.exit(main())
