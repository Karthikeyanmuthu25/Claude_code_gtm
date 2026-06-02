#!/usr/bin/env python3
"""
14-21 Day Nurture Sequence Agent
CLI Entry Point

Usage:
  python main.py                           # Interactive mode
  python main.py --input sample_input.json # Load from JSON
  python main.py --input input.json --model claude-opus-4-5
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.nurture_agent import NurtureSequenceAgent
from src.tools.input_collector import collect_inputs


def parse_args():
    parser = argparse.ArgumentParser(
        description="14-21 Day Nurture Sequence Agent — Powered by Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --input sample_input.json
  python main.py --input sample_input.json --model claude-opus-4-5
        """
    )
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Path to JSON input file")
    parser.add_argument("--model", "-m", type=str, default="claude-opus-4-5",
                        help="Claude model (default: claude-opus-4-5)")
    return parser.parse_args()


def main():
    print("\n" + "═" * 58)
    print("  14-21 DAY NURTURE SEQUENCE AGENT")
    print("  Converts Cold Leads → MQLs · Powered by Claude")
    print("═" * 58)

    args = parse_args()

    try:
        inputs = collect_inputs(json_path=args.input)
        agent = NurtureSequenceAgent(model=args.model)
        result = agent.run(inputs)

        print("✅ Done!")
        print(f"   Markdown report → {result['markdown_path']}")
        print(f"   JSON data       → {result['json_path']}\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled.\n")
        sys.exit(0)
    except EnvironmentError as e:
        print(f"\n{e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
