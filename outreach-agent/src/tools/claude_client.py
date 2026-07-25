"""
Claude API Client
Handles all communication with the Anthropic Claude API.
"""

import os
import anthropic
from typing import List, Optional

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert B2B outreach copywriter and GTM strategist. "
    "You craft hyper-personalized, human-sounding outreach sequences "
    "that convert cold leads into warm MQLs. "
    "You never write generic, templated, or pushy messages. "
    "Every sequence you write is grounded in the receiver's real business context, "
    "follows a deliberate nurture arc, and respects the reader's time. "
    "Always return output in the exact structured format requested."
)


class ClaudeClient:
    def __init__(self, model: str = "claude-opus-4-5"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "❌ ANTHROPIC_API_KEY not set.\n"
                "Run: export ANTHROPIC_API_KEY=your_key_here"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 8096,
    ) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or DEFAULT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def revise(
        self,
        original_prompt: str,
        previous_output: str,
        issues: List[str],
        system: Optional[str] = None,
        max_tokens: int = 8096,
    ) -> str:
        """One critique-and-fix pass: send back the specific rule violations
        qa_lint_skill found and ask for a full corrected rewrite."""
        revision_instruction = (
            "The sequence you just generated has these specific compliance issues:\n"
            + "\n".join(f"- {issue}" for issue in issues)
            + "\n\nRewrite the FULL sequence fixing only these issues. Keep everything "
            "else that wasn't flagged as-is. Return the complete sequence in the exact "
            "same format as before."
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or DEFAULT_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": original_prompt},
                {"role": "assistant", "content": previous_output},
                {"role": "user", "content": revision_instruction},
            ],
        )
        return message.content[0].text
