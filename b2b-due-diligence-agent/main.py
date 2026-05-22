#!/usr/bin/env python3
"""
B2B Due Diligence Verification Agent
=====================================
Run from terminal — always saves a Markdown report to reports/

Usage:
  python main.py                          # Interactive input
  python main.py --file input.json        # Load from JSON file
  python main.py --json '{"company_name":"Acme",...}'
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from agent.orchestrator import run_pipeline
from agent.validator import validate_input
from agent.reporter import export_executive_report, export_monitor_report

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

load_dotenv()

console = Console(legacy_windows=False)


def get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        console.print()
        console.print("[red]  OPENAI_API_KEY not set.[/red]")
        console.print("[dim]  Add it to your .env file: OPENAI_API_KEY=sk-...[/dim]")
        console.print()
        sys.exit(1)
    return key


def interactive_input() -> dict:
    console.print()
    console.print(Panel.fit(
        "[bold]MANUAL INPUT MODE[/bold]\n"
        "[dim]Enter target company and decision maker details.[/dim]\n"
        "[dim]Press Enter to skip optional fields.[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    data = {}

    console.print("[bold]-- COMPANY --[/bold]")
    data["company_name"]     = Prompt.ask("  Company Name [red]*[/red]").strip()
    data["company_website"]  = Prompt.ask("  Website", default="").strip()
    data["company_location"] = Prompt.ask("  Location", default="").strip()
    console.print()

    console.print("[bold]-- DECISION MAKER --[/bold]")
    data["decision_maker_name"]         = Prompt.ask("  Full Name [red]*[/red]").strip()
    data["decision_maker_job_title"]    = Prompt.ask("  Job Title", default="").strip()
    data["decision_maker_linkedin_url"] = Prompt.ask("  LinkedIn URL", default="").strip()
    data["decision_maker_email"]        = Prompt.ask("  Email", default="").strip()
    console.print()

    return data


def main():
    parser = argparse.ArgumentParser(
        description="B2B Due Diligence Verification Agent — 7-Stage Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --file examples/acme.json
  python main.py --json '{"company_name":"Acme","decision_maker_name":"Jane"}'
        """,
    )
    parser.add_argument("--file", "-f", help="Path to JSON input file")
    parser.add_argument("--json", "-j", help="Inline JSON string")
    parser.add_argument("--output-dir", default="reports", help="Report output directory (default: reports)")
    parser.add_argument("--no-save", action="store_true", help="Skip saving reports")
    args = parser.parse_args()

    api_key = get_api_key()

    # ── Load input ────────────────────────────────────────────────────────────
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                data = json.load(f)
            console.print(f"[dim]  Loaded from {args.file}[/dim]")
        except FileNotFoundError:
            console.print(f"[red]  File not found: {args.file}[/red]")
            sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[red]  Invalid JSON in {args.file}: {e}[/red]")
            sys.exit(1)

    elif args.json:
        try:
            data = json.loads(args.json)
        except json.JSONDecodeError as e:
            console.print(f"[red]  Invalid JSON: {e}[/red]")
            sys.exit(1)

    else:
        data = interactive_input()

    # ── Validate ──────────────────────────────────────────────────────────────
    is_valid, errors, warnings = validate_input(data)

    if errors:
        console.print()
        for e in errors:
            console.print(f"  [red]  {e}[/red]")
        console.print()
        sys.exit(1)

    if warnings:
        console.print()
        for w in warnings:
            console.print(f"  [yellow]  Warning: {w}[/yellow]")
        console.print()

    # ── Run pipeline ──────────────────────────────────────────────────────────
    try:
        result = run_pipeline(
            input_data=data,
            api_key=api_key,
            save_report=not args.no_save,
        )
    except Exception as exc:
        console.print(f"\n[red]  Pipeline failed: {exc}[/red]\n")
        sys.exit(1)

    if result is None:
        sys.exit(1)

    # ── Save both reports ─────────────────────────────────────────────────────
    if not args.no_save:
        exec_path    = export_executive_report(data, result, output_dir=args.output_dir)
        monitor_path = export_monitor_report(data, result, output_dir=args.output_dir)
        console.print(f"  Executive    --> {exec_path}")
        console.print(f"  Monitor      --> {monitor_path}")
        console.print()

    # ── Final line ────────────────────────────────────────────────────────────
    fa  = result.get("stage_results", {}).get("final_assessment", {})
    rec = fa.get("recommendation", "CAUTION")
    col = {"PROCEED": "bright_green", "CAUTION": "yellow", "REJECT": "red"}.get(rec, "white")
    console.print(f"  [bold {col}]Analysis complete -- {rec}[/bold {col}]")
    console.print()


if __name__ == "__main__":
    main()
