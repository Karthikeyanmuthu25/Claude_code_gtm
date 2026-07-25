"""
14-21 Day Nurture Sequence Agent
Orchestrates the full pipeline:
  Input → Personalization Analysis → Prompt Build → Claude → Markdown Report
"""

from src.tools.claude_client import ClaudeClient
from src.tools.output_formatter import format_and_save
from src.skills.personalization_skill import build_personalization_context
from src.skills.sequence_skill import build_sequence_prompt
from src.skills.qa_lint_skill import lint
from src.skills.icp_fit_skill import score_fit

MAX_REVISION_ATTEMPTS = 1


class NurtureSequenceAgent:
    def __init__(self, model: str = "claude-opus-4-5"):
        self.client = ClaudeClient(model=model)

    def run(self, inputs: dict, min_fit_score: int = 0) -> dict:
        print("\n  🎯  Step 1/5 — Scoring ICP fit...")
        fit = score_fit(inputs)
        self._print_fit(fit)
        if fit["score"] < min_fit_score:
            raise ValueError(
                f"Fit score {fit['score']} is below --min-fit-score {min_fit_score}. "
                f"Reasons: {'; '.join(fit['reasons'])}"
            )

        print("  🔍  Step 2/5 — Analyzing profiles...")
        ctx = build_personalization_context(inputs)
        self._print_analysis(ctx)

        print("  ✍️   Step 3/5 — Building sequence prompt...")
        prompt = build_sequence_prompt(inputs, ctx)

        print("  🤖  Step 4/5 — Generating sequence via Claude...\n")
        raw_output = self.client.generate(prompt)
        lint_report = lint(raw_output)

        attempts = 0
        while not lint_report["passed"] and attempts < MAX_REVISION_ATTEMPTS:
            attempts += 1
            print(f"  🛠️   Lint found {len(lint_report['violations'])} issue(s) — revising (attempt {attempts})...")
            raw_output = self.client.revise(prompt, raw_output, lint_report["violations"])
            lint_report = lint(raw_output)

        if lint_report["passed"]:
            print("  ✅  Lint passed.")
        else:
            print(f"  ⚠️   {len(lint_report['violations'])} issue(s) unresolved after revision — flagged for human review.")

        print("  📄  Step 5/5 — Saving report...")
        result = format_and_save(raw_output, inputs, fit_report=fit, lint_report=lint_report)

        return result

    def _print_fit(self, fit: dict):
        print(f"\n  Fit score: {fit['score']}/100")
        for reason in fit["reasons"]:
            print(f"    - {reason}")

    def _print_analysis(self, ctx: dict):
        hb = ctx.get("hot_button_map", {})
        print(f"  Hot Button 1: {hb.get('hot_button_1', '')}")
        print(f"  Hot Button 2: {hb.get('hot_button_2', '')}")
        print(f"  Hot Button 3: {hb.get('hot_button_3', '')}\n")
