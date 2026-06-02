"""
Claude API Client
Handles all communication with the Anthropic Claude API.
"""

import os
import anthropic
from typing import Optional


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
        system_prompt = system or (
            "You are an expert B2B outreach copywriter and GTM strategist. "
            "You craft hyper-personalized, human-sounding outreach sequences "
            "that convert cold leads into warm MQLs. "
            "You never write generic, templated, or pushy messages. "
            "Every sequence you write is grounded in the receiver's real business context, "
            "follows a deliberate nurture arc, and respects the reader's time. "
            "Always return output in the exact structured format requested."
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
