#!/usr/bin/env python3
"""
Log a real-world send outcome (opened / replied / meeting booked / bounced)
against a generated sequence. This is the missing link that makes
feedback-based optimization possible — without outcome data, nothing in the
system can ever learn what's actually working.

Usage:
  python scripts/log_outcome.py --file output/nurture_x.json --touch day_1 --replied true
  python scripts/log_outcome.py --file output/nurture_x.json --touch li_step_2 --opened true --notes "liked the post-accept line"
  python scripts/log_outcome.py --file output/nurture_x.json --touch day_0 --sent-at 2026-07-20
"""

import argparse
import json
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_bool(value: str):
    if value is None:
        return None
    v = value.strip().lower()
    if v in ("true", "y", "yes", "1"):
        return True
    if v in ("false", "n", "no", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Expected a boolean, got: {value}")


def main():
    parser = argparse.ArgumentParser(description="Log a send outcome against a generated sequence.")
    parser.add_argument("--file", required=True, help="Path to the sequence's .json output file")
    parser.add_argument("--touch", required=True,
                         help="Touch id, e.g. day_0, day_1, day_3, day_5, day_14, day_21, li_step_1..4")
    parser.add_argument("--sent-at", default=None, help="ISO date/time this touch was actually sent")
    parser.add_argument("--opened", type=parse_bool, default=None)
    parser.add_argument("--replied", type=parse_bool, default=None)
    parser.add_argument("--meeting-booked", type=parse_bool, default=None)
    parser.add_argument("--bounced", type=parse_bool, default=None)
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    outcomes = data.setdefault("outcomes", {})
    touch = outcomes.setdefault(args.touch, {
        "sent_at": None, "opened": None, "replied": None,
        "meeting_booked": None, "bounced": None, "notes": None,
    })

    if args.sent_at:
        touch["sent_at"] = args.sent_at
    elif touch.get("sent_at") is None and any(
        v is not None for v in (args.opened, args.replied, args.meeting_booked, args.bounced)
    ):
        touch["sent_at"] = datetime.now(timezone.utc).isoformat()

    if args.opened is not None:
        touch["opened"] = args.opened
    if args.replied is not None:
        touch["replied"] = args.replied
    if args.meeting_booked is not None:
        touch["meeting_booked"] = args.meeting_booked
    if args.bounced is not None:
        touch["bounced"] = args.bounced
    if args.notes is not None:
        touch["notes"] = args.notes

    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated {args.touch} in {args.file}")
    print(f"   {touch}")


if __name__ == "__main__":
    sys.exit(main())
