"""
Langfuse observability wrapper.
Enabled when LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY are set in env.
Falls back to silent no-ops when disabled or the package is missing.
"""

import os

from agent.logger import get_logger

logger = get_logger("langfuse")


class _NullObs:
    """Silent stand-in returned when Langfuse is disabled."""
    def generation(self, **kw): return self
    def span(self, **kw):       return self
    def end(self, **kw):        pass
    def update(self, **kw):     pass


class LangfuseTracer:
    """
    Thin, failure-safe wrapper around the Langfuse Python SDK.
    Creates a single client instance per pipeline run.
    All methods degrade gracefully to no-ops if Langfuse is not configured.
    """

    def __init__(self):
        self._lf = None
        pk = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
        sk = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
        if not (pk and sk):
            return
        try:
            from langfuse import Langfuse          # noqa: PLC0415
            self._lf = Langfuse(
                public_key=pk,
                secret_key=sk,
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            )
            logger.info("Langfuse tracing enabled")
        except Exception as exc:
            logger.warning(f"Langfuse init failed — tracing disabled: {exc}")

    @property
    def enabled(self) -> bool:
        return self._lf is not None

    def trace(self, **kwargs) -> object:
        if self._lf:
            try:
                return self._lf.trace(**kwargs)
            except Exception as exc:
                logger.debug(f"Langfuse trace() error: {exc}")
        return _NullObs()

    def flush(self):
        if self._lf:
            try:
                self._lf.flush()
            except Exception as exc:
                logger.debug(f"Langfuse flush() error: {exc}")
