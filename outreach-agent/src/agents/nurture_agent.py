"""
14-21 Day Nurture Sequence Agent
Orchestrates the full pipeline:
  Input → Personalization Analysis → Prompt Build → Claude → Markdown Report
"""

from src.tools.claude_client import ClaudeClient
from src.tools.output_formatter import format_and_save
from src.skills.personalization_skill import build_personalization_context
from src.skills.sequence_skill import build_sequence_prompt


class NurtureSequenceAgent:
    def __init__(self, model: str = "claude-opus-4-5"):
        self.client = ClaudeClient(model=model)

    def run(self, inputs: dict) -> dict:
        print("\n  🔍  Step 1/4 — Analyzing profiles...")
        ctx = build_personalization_context(inputs)
        self._print_analysis(ctx)

        print("  ✍️   Step 2/4 — Building sequence prompt...")
        prompt = build_sequence_prompt(inputs, ctx)

        print("  🤖  Step 3/4 — Generating sequence via Claude...\n")
        raw_output = self.client.generate(prompt)

        print("  📄  Step 4/4 — Saving report...")
        result = format_and_save(raw_output, inputs)

        return result

    def _print_analysis(self, ctx: dict):
        hb = ctx.get("hot_button_map", {})
        print(f"\n  Connection angle: {ctx.get('connection_angle', '')}")
        print(f"  Hot Button 1: {hb.get('hot_button_1', '')}")
        print(f"  Hot Button 2: {hb.get('hot_button_2', '')}")
        print(f"  Hot Button 3: {hb.get('hot_button_3', '')}\n")
