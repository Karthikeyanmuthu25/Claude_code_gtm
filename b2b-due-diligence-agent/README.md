# B2B Due Diligence Verification Agent — v5.0

A 7-stage autonomous intelligence pipeline that verifies B2B leads and decision makers using web intelligence, professional profile scraping, and GPT-4o analysis.

---

## Quick Start

### 1. Set up environment

```bash
cp .env.example .env
# Edit .env and add your real API keys
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Check connectivity

```bash
python test_tools.py
```

### 4. Run analysis

**CLI mode (recommended for batch):**
```bash
python main.py
python main.py --file examples/acme.json
python main.py --json '{"company_name":"Acme","decision_maker_name":"Jane Smith"}'
```

**Streamlit UI:**
```bash
streamlit run app.py
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys. **Never commit `.env` to git.**

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | GPT-4o for all LLM stages |
| `APIFY_API_KEY` | Optional | LinkedIn scraping, website crawl, Google search |
| `EXA_API_KEY` | Optional | Neural web search for company/person intel |

Without Apify and Exa keys the pipeline still runs using GPT-4o only, but with reduced data coverage.

### Optional config overrides (via `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `gpt-4o` | OpenAI model |
| `LLM_MAX_TOKENS` | `2500` | Max tokens per LLM call |
| `LLM_RETRY_ATTEMPTS` | `3` | Retry attempts per LLM call |
| `APIFY_TIMEOUT_S` | `120` | Apify actor run timeout |
| `APIFY_WEBSITE_PAGES` | `5` | Max website pages to crawl |
| `APIFY_GOOGLE_RESULTS` | `8` | Google search results per query |
| `TRUNCATE_CHARS` | `6000` | Max chars per stage context |
| `REPORT_OUTPUT_DIR` | `reports` | Report output directory |
| `LOG_DIR` | `logs` | Log file directory |
| `COMPANY_SCORE_WEIGHT` | `0.6` | Company score weight in overall |
| `DM_SCORE_WEIGHT` | `0.4` | Decision maker score weight |
| `PROCEED_MIN_SCORE` | `70` | Minimum score for PROCEED |
| `REJECT_MAX_SCORE` | `40` | Maximum score before REJECT |

---

## 7-Stage Pipeline

| Stage | Name | Tools |
|-------|------|-------|
| 1 | Input Validation | GPT-4o |
| 2 | Data Collection | Apify (LinkedIn, website, Google) + Exa (web search) |
| 3 | Cross-Verification | Exa + GPT-4o |
| 4 | Risk Detection | Exa + Apify + GPT-4o |
| 5 | Trust Scoring | Exa + GPT-4o |
| 6 | Evidence Aggregation | Exa + GPT-4o |
| 7 | Final Assessment | GPT-4o |

**Verdicts:** `PROCEED` · `CAUTION` · `REJECT`

Hard verdict rules are enforced post-LLM — any red flag forces REJECT regardless of LLM output.

---

## Reports

Each run produces two Markdown reports in `reports/`:

- **Executive report** (`*_executive_*.md`) — Client-facing strategic intelligence. No tool names, written as a human analyst.
- **Monitor report** (`*_monitor_*.md`) — Internal agent performance. Includes stage timing, LLM call detail, cost breakdown, data coverage, hallucination risk assessment.

JSON output via `--file` or download in the UI includes a `cost_tracking` section with:
- `cost_breakdown` — LLM cost, tool cost, grand total (USD)
- `token_breakdown` — prompt, completion, total tokens
- `llm_calls` — per-call detail with cost, duration, attempt count
- `tool_calls` — per-tool-call detail with cost and status
- `tool_summary` — Exa and Apify call aggregates
- `reliability` — LLM success rate, retry rate

---

## Input Format

```json
{
  "company_name": "Acme SaaS Inc.",
  "company_website": "https://acmesaas.com",
  "company_location": "San Francisco, CA, USA",
  "decision_maker_name": "Jane Smith",
  "decision_maker_job_title": "Chief Revenue Officer",
  "decision_maker_linkedin_url": "https://linkedin.com/in/janesmith",
  "decision_maker_email": "jane@acmesaas.com"
}
```

See `examples/` for sample inputs.

---

## Security

- `.env` is gitignored — never committed
- Input is sanitised: control chars stripped, length-limited, prompt injection blocked
- All report text is sanitised to remove tool vendor names before output
- Logs written to `logs/agent_YYYYMMDD.log` (DEBUG level file, WARNING only to console)
