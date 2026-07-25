#!/usr/bin/env python3
"""
Aggregate logged outcomes (scripts/log_outcome.py) across every generated
sequence to surface what's actually working — reply rate by touch, and reply
rate by ICP fit score bucket. This is the "surface patterns back into the
brain" half of the feedback loop; scripts/promote_to_brain.py is the other
half (writing a confirmed pattern into knowledge/brain.md).

Usage:
  python scripts/analyze_outcomes.py
  python scripts/analyze_outcomes.py --output-dir output
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict


def fit_bucket(score) -> str:
    if score is None:
        return "unknown"
    if score >= 80:
        return "80-100 (strong fit)"
    if score >= 60:
        return "60-79 (moderate fit)"
    return "0-59 (weak fit)"


def main():
    parser = argparse.ArgumentParser(description="Aggregate outcome data across all generated sequences.")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.output_dir, "*.json")))
    if not files:
        print(f"No output files found in {args.output_dir}")
        return

    touch_stats = defaultdict(lambda: {"sent": 0, "opened": 0, "replied": 0, "meeting_booked": 0, "bounced": 0})
    bucket_stats = defaultdict(lambda: {"sequences": 0, "got_reply": 0})
    sequences_with_any_outcome = 0

    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        outcomes = data.get("outcomes", {})
        fit_score = data.get("fit_report", {}).get("score")
        sequence_had_any_logged = False
        sequence_got_reply = False

        for touch_id, o in outcomes.items():
            if o.get("sent_at") is None and all(
                o.get(k) is None for k in ("opened", "replied", "meeting_booked", "bounced")
            ):
                continue
            sequence_had_any_logged = True
            stats = touch_stats[touch_id]
            stats["sent"] += 1
            if o.get("opened"):
                stats["opened"] += 1
            if o.get("replied"):
                stats["replied"] += 1
                sequence_got_reply = True
            if o.get("meeting_booked"):
                stats["meeting_booked"] += 1
            if o.get("bounced"):
                stats["bounced"] += 1

        if sequence_had_any_logged:
            sequences_with_any_outcome += 1
            bucket = fit_bucket(fit_score)
            bucket_stats[bucket]["sequences"] += 1
            if sequence_got_reply:
                bucket_stats[bucket]["got_reply"] += 1

    print(f"Sequences generated: {len(files)}")
    print(f"Sequences with at least one logged outcome: {sequences_with_any_outcome}")

    if sequences_with_any_outcome == 0:
        print("\nNo outcome data yet. Log sends with scripts/log_outcome.py, then re-run this.")
        return

    print("\nReply rate by touch:")
    for touch_id in sorted(touch_stats):
        s = touch_stats[touch_id]
        rate = f"{s['replied'] / s['sent']:.0%}" if s["sent"] else "n/a"
        print(f"  {touch_id:10s}  sent={s['sent']:3d}  opened={s['opened']:3d}  "
              f"replied={s['replied']:3d} ({rate})  meetings={s['meeting_booked']:3d}  bounced={s['bounced']:3d}")

    print("\nReply rate by ICP fit score bucket:")
    for bucket in sorted(bucket_stats):
        s = bucket_stats[bucket]
        rate = f"{s['got_reply'] / s['sequences']:.0%}" if s["sequences"] else "n/a"
        print(f"  {bucket:22s}  sequences={s['sequences']:3d}  got_reply={s['got_reply']:3d} ({rate})")

    print("\nHigh-reply touches/buckets are candidates for scripts/promote_to_brain.py.")


if __name__ == "__main__":
    sys.exit(main())
