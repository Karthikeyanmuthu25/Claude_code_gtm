import os

# ── LLM ──────────────────────────────────────────────────
# Per-provider default models — used for both the primary provider and
# whichever provider the automatic fallback switches to mid-run.
ANTHROPIC_MODEL    = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENAI_MODEL       = os.getenv("OPENAI_MODEL", "gpt-4o")

LLM_PROVIDER       = os.getenv("LLM_PROVIDER", "openai")   # "anthropic" | "openai" — primary provider
LLM_MODEL          = os.getenv("LLM_MODEL", OPENAI_MODEL if LLM_PROVIDER == "openai" else ANTHROPIC_MODEL)
LLM_MAX_TOKENS     = int(os.getenv("LLM_MAX_TOKENS", "2500"))
LLM_TEMPERATURE    = float(os.getenv("LLM_TEMPERATURE", "0"))
LLM_RETRY_ATTEMPTS = int(os.getenv("LLM_RETRY_ATTEMPTS", "3"))
LLM_RETRY_BACKOFF  = float(os.getenv("LLM_RETRY_BACKOFF", "2.0"))

# If the primary provider fails after exhausting retries (auth, billing,
# rate-limit, or any other error), automatically retry the same call on the
# other provider — as long as its API key is configured. Once a fallback
# succeeds, the pipeline stays on that provider for the rest of the run.
LLM_FALLBACK_ENABLED = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"

# ── Apify actor IDs ───────────────────────────────────────
APIFY_ACTOR_LINKEDIN = os.getenv("APIFY_ACTOR_LINKEDIN", "dev_fusion~Linkedin-Profile-Scraper")
APIFY_ACTOR_WEBSITE  = os.getenv("APIFY_ACTOR_WEBSITE",  "apify~website-content-crawler")
APIFY_ACTOR_GOOGLE   = os.getenv("APIFY_ACTOR_GOOGLE",   "apify~google-search-scraper")
APIFY_TIMEOUT_S      = int(os.getenv("APIFY_TIMEOUT_S",  "120"))
APIFY_WEBSITE_PAGES  = int(os.getenv("APIFY_WEBSITE_PAGES", "5"))
APIFY_GOOGLE_RESULTS = int(os.getenv("APIFY_GOOGLE_RESULTS", "8"))

# ── Exa ───────────────────────────────────────────────────
EXA_TIMEOUT_S        = int(os.getenv("EXA_TIMEOUT_S", "30"))
EXA_MAX_CHARS        = int(os.getenv("EXA_MAX_CHARS", "1000"))

# ── Pipeline ──────────────────────────────────────────────
TRUNCATE_CHARS_DEFAULT = int(os.getenv("TRUNCATE_CHARS", "6000"))
TRUNCATE_CHARS_S7      = int(os.getenv("TRUNCATE_CHARS_S7", "7000"))
REPORT_OUTPUT_DIR      = os.getenv("REPORT_OUTPUT_DIR", "reports")
LOG_DIR                = os.getenv("LOG_DIR", "logs")

# ── Scoring weights ───────────────────────────────────────
COMPANY_SCORE_WEIGHT = float(os.getenv("COMPANY_SCORE_WEIGHT", "0.6"))
DM_SCORE_WEIGHT      = float(os.getenv("DM_SCORE_WEIGHT", "0.4"))

# ── Verdict thresholds ────────────────────────────────────
PROCEED_MIN_SCORE    = int(os.getenv("PROCEED_MIN_SCORE", "70"))
REJECT_MAX_SCORE     = int(os.getenv("REJECT_MAX_SCORE", "40"))
PROCEED_MIN_CONF     = int(os.getenv("PROCEED_MIN_CONF", "75"))
