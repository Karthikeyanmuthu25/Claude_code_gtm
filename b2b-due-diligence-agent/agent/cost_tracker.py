"""
Real-time cost and token tracking for every tool call in the pipeline.
Tracks: OpenAI LLM calls, Apify actor runs, Exa search calls.
Produces a full cost breakdown per run.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import time

# ── LLM pricing (USD per 1K tokens), by model prefix — update when prices change ──
# Matched by longest-prefix so dated snapshots (e.g. "claude-sonnet-4-5-20250929")
# resolve to their family's rate without needing an entry per snapshot.
MODEL_PRICING_PER_1K = {
    # Anthropic — Claude
    "claude-opus-4":     (0.015, 0.075),
    "claude-sonnet-4-6": (0.003, 0.015),
    "claude-sonnet-4":   (0.003, 0.015),
    "claude-haiku-4-5":  (0.001, 0.005),
    "claude-3-5-sonnet": (0.003, 0.015),
    "claude-3-5-haiku":  (0.0008, 0.004),
    "claude-3-opus":     (0.015, 0.075),
    # OpenAI
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o":      (0.005, 0.015),
}
DEFAULT_LLM_INPUT_COST_PER_1K  = 0.005
DEFAULT_LLM_OUTPUT_COST_PER_1K = 0.015


def _price_for_model(model: str) -> tuple[float, float]:
    """Longest-prefix match against MODEL_PRICING_PER_1K; falls back to the default rate."""
    best_match, best_len = None, -1
    for prefix, rates in MODEL_PRICING_PER_1K.items():
        if model.startswith(prefix) and len(prefix) > best_len:
            best_match, best_len = rates, len(prefix)
    return best_match or (DEFAULT_LLM_INPUT_COST_PER_1K, DEFAULT_LLM_OUTPUT_COST_PER_1K)

# ── Exa pricing (approximate — $0.001 per search result) ──────────────────
EXA_COST_PER_RESULT = 0.001

# ── Apify pricing (approximate — $0.004 per 1000 events) ──────────────────
APIFY_COST_PER_ACTOR_RUN = 0.01    # rough estimate per run


@dataclass
class LLMCall:
    label: str
    stage: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    duration_s: float
    attempt: int
    status: str   # success | failed | retried
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


@dataclass
class ToolCall:
    tool: str           # exa | apify | vibe
    method: str         # search_company_intel | scrape_website | etc.
    stage: str
    input_summary: str  # brief description of what was queried
    results_count: int
    cost_usd: float
    duration_s: float
    status: str         # success | failed | skipped
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


class CostTracker:
    """
    Tracks every LLM call and tool call with full cost breakdown.
    Call .summary() at end of pipeline for the complete cost report.
    """

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.started_at = datetime.now().isoformat()
        self.llm_calls: list[LLMCall] = []
        self.tool_calls: list[ToolCall] = []
        self._pipeline_start = time.time()

    # ── LLM tracking ──────────────────────────────────────────────────────

    def record_llm(
        self,
        label: str,
        stage: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_s: float,
        attempt: int = 1,
        status: str = "success",
        error: str = None,
    ) -> LLMCall:
        total_tokens = prompt_tokens + completion_tokens
        input_rate, output_rate = _price_for_model(model)
        input_cost   = (prompt_tokens / 1000) * input_rate
        output_cost  = (completion_tokens / 1000) * output_rate
        total_cost   = input_cost + output_cost

        call = LLMCall(
            label=label,
            stage=stage,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            input_cost_usd=round(input_cost, 6),
            output_cost_usd=round(output_cost, 6),
            total_cost_usd=round(total_cost, 6),
            duration_s=round(duration_s, 2),
            attempt=attempt,
            status=status,
            error=error,
        )
        self.llm_calls.append(call)
        return call

    # ── Tool tracking ──────────────────────────────────────────────────────

    def record_tool(
        self,
        tool: str,
        method: str,
        stage: str,
        input_summary: str,
        results_count: int = 0,
        duration_s: float = 0.0,
        status: str = "success",
        error: str = None,
    ) -> ToolCall:
        if tool == "exa":
            cost = results_count * EXA_COST_PER_RESULT
        elif tool == "apify":
            cost = APIFY_COST_PER_ACTOR_RUN if status == "success" else 0.0
        else:
            cost = 0.0

        call = ToolCall(
            tool=tool,
            method=method,
            stage=stage,
            input_summary=input_summary[:200],
            results_count=results_count,
            cost_usd=round(cost, 6),
            duration_s=round(duration_s, 2),
            status=status,
            error=error,
        )
        self.tool_calls.append(call)
        return call

    # ── Aggregates ────────────────────────────────────────────────────────

    @property
    def total_llm_cost(self) -> float:
        return round(sum(c.total_cost_usd for c in self.llm_calls), 6)

    @property
    def total_tool_cost(self) -> float:
        return round(sum(c.cost_usd for c in self.tool_calls), 6)

    @property
    def total_cost(self) -> float:
        return round(self.total_llm_cost + self.total_tool_cost, 6)

    @property
    def total_tokens(self) -> int:
        return sum(c.total_tokens for c in self.llm_calls)

    @property
    def total_prompt_tokens(self) -> int:
        return sum(c.prompt_tokens for c in self.llm_calls)

    @property
    def total_completion_tokens(self) -> int:
        return sum(c.completion_tokens for c in self.llm_calls)

    @property
    def total_retries(self) -> int:
        return sum(1 for c in self.llm_calls if c.attempt > 1)

    @property
    def pipeline_duration_s(self) -> float:
        return round(time.time() - self._pipeline_start, 2)

    # ── Full summary dict ─────────────────────────────────────────────────

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "pipeline_duration_s": self.pipeline_duration_s,

            "cost_breakdown": {
                "llm_total_usd":       self.total_llm_cost,
                "tool_total_usd":      self.total_tool_cost,
                "grand_total_usd":     self.total_cost,
                "currency":            "USD",
                "cost_note": (
                    "LLM costs are priced per-model (see MODEL_PRICING_PER_1K); unrecognised "
                    "models fall back to $5/1M input, $15/1M output. Tool costs are estimates. "
                    "Check provider dashboards for exact billing."
                ),
            },

            "token_breakdown": {
                "total_tokens":       self.total_tokens,
                "prompt_tokens":      self.total_prompt_tokens,
                "completion_tokens":  self.total_completion_tokens,
                "avg_tokens_per_call": round(
                    self.total_tokens / len(self.llm_calls), 0
                ) if self.llm_calls else 0,
            },

            "llm_calls": [
                {
                    "label":             c.label,
                    "stage":             c.stage,
                    "model":             c.model,
                    "prompt_tokens":     c.prompt_tokens,
                    "completion_tokens": c.completion_tokens,
                    "total_tokens":      c.total_tokens,
                    "input_cost_usd":    c.input_cost_usd,
                    "output_cost_usd":   c.output_cost_usd,
                    "total_cost_usd":    c.total_cost_usd,
                    "duration_s":        c.duration_s,
                    "attempt":           c.attempt,
                    "status":            c.status,
                    "timestamp":         c.timestamp,
                    "error":             c.error,
                }
                for c in self.llm_calls
            ],

            "tool_calls": [
                {
                    "tool":          c.tool,
                    "method":        c.method,
                    "stage":         c.stage,
                    "input_summary": c.input_summary,
                    "results_count": c.results_count,
                    "cost_usd":      c.cost_usd,
                    "duration_s":    c.duration_s,
                    "status":        c.status,
                    "timestamp":     c.timestamp,
                    "error":         c.error,
                }
                for c in self.tool_calls
            ],

            "tool_summary": {
                "exa_calls":         sum(1 for c in self.tool_calls if c.tool == "exa"),
                "exa_results_total": sum(c.results_count for c in self.tool_calls if c.tool == "exa"),
                "exa_cost_usd":      round(sum(c.cost_usd for c in self.tool_calls if c.tool == "exa"), 6),
                "apify_calls":       sum(1 for c in self.tool_calls if c.tool == "apify"),
                "apify_cost_usd":    round(sum(c.cost_usd for c in self.tool_calls if c.tool == "apify"), 6),
                "failed_calls":      sum(1 for c in self.tool_calls if c.status == "failed"),
                "skipped_calls":     sum(1 for c in self.tool_calls if c.status == "skipped"),
            },

            "reliability": {
                "total_llm_calls":     len(self.llm_calls),
                "successful_llm":      sum(1 for c in self.llm_calls if c.status == "success"),
                "failed_llm":          sum(1 for c in self.llm_calls if c.status == "failed"),
                "total_retries":       self.total_retries,
                "retry_rate_pct":      round(
                    self.total_retries / len(self.llm_calls) * 100, 1
                ) if self.llm_calls else 0,
            },
        }
