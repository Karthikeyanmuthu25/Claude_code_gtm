# B2B Due Diligence Verification Agent

A production-grade autonomous intelligence pipeline for B2B trust verification.

```
◈ Input Validation → ◉ Data Collection → ⊗ Cross-Verification
⚠ Risk Detection → ◆ Trust Scoring → ≡ Evidence Aggregation → ✦ Final Assessment
```

---

## What It Does

Runs a 7-stage intelligence pipeline on any company + decision maker pair and produces:

- **Company trust score** (0–100)
- **Decision maker authenticity score** (0–100)
- **Overall trust score** (0–100)
- **Risk flags** — Red / Yellow / Green classification
- **Cross-verification** — domain, email, LinkedIn, title consistency
- **Final verdict** — `PROCEED` / `CAUTION` / `REJECT` with confidence %
- **Action items** — what to verify manually before proceeding
- **Structured reports** — JSON + Markdown

---

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Set API key

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run

**Interactive mode (guided prompts):**
```bash
python main.py
```

**From a JSON file:**
```bash
python main.py --file examples/acme.json
```

**With Markdown report:**
```bash
python main.py --file examples/acme.json --report md
```

**Inline JSON:**
```bash
python main.py --json '{"company_name":"Acme","company_website":"https://acme.com","decision_maker_name":"Jane Smith","decision_maker_job_title":"CRO","decision_maker_linkedin_url":"https://linkedin.com/in/janesmith","decision_maker_email":"jane@acme.com"}'
```

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

**Required fields:** `company_name`, `decision_maker_name`  
**Recommended:** All others (more fields = higher coverage)

---

## CLI Options

| Flag | Description |
|------|-------------|
| `--file FILE` | Load input from JSON file |
| `--json JSON` | Inline JSON string |
| `--report [json\|md\|both]` | Report format (default: json) |
| `--no-save` | Skip saving reports to disk |
| `--output-dir DIR` | Report output directory (default: reports/) |

---

## Output

### Terminal

Live 7-stage pipeline output with:
- Stage-by-stage findings
- Color-coded risk flags
- Trust score table
- Evidence aggregation
- Final verdict panel with action items

### Reports

Saved to `reports/` directory:
- `{company}_{timestamp}.json` — full structured data
- `{company}_{timestamp}.md` — human-readable Markdown report

---

## 7-Stage Pipeline

| Stage | Layer | What It Does |
|-------|-------|--------------|
| 1 | Input Validation | Format checks, domain alignment, email domain match |
| 2 | Data Collection | Signal extraction from all provided data points |
| 3 | Cross-Verification | Company ↔ decision maker consistency checks |
| 4 | Risk Detection | Red / Yellow / Green flag classification |
| 5 | Trust Scoring | 0–100 scores for company and decision maker |
| 6 | Evidence Aggregation | Supporting vs contradicting signal summary |
| 7 | Final Assessment | PROCEED / CAUTION / REJECT with confidence |

---

## Project Structure

```
b2b-due-diligence-agent/
├── main.py                  # CLI entrypoint
├── requirements.txt
├── README.md
├── examples/
│   ├── acme.json            # Example input
│   └── techflow.json        # Example input
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py      # 7-stage pipeline + Claude integration
│   ├── validator.py         # Input pre-flight validation
│   └── reporter.py          # JSON + Markdown report export
├── reports/                 # Auto-created, stores output reports
└── logs/                    # Auto-created, stores debug logs
```

---

## Verdict Guide

| Verdict | Meaning |
|---------|---------|
| `PROCEED` | Company and decision maker verified. Proceed with business. |
| `CAUTION` | Some signals warrant manual verification before proceeding. |
| `REJECT` | Significant red flags detected. Do not proceed without further investigation. |

---

## Notes

- This agent performs **inference-based** due diligence from provided data. It does not scrape live websites.
- For live scraping, integrate Apify or Exa as additional enrichment layers.
- All reports are stored locally in `reports/`.
- Requires Python 3.9+

---

*B2B Due Diligence Verification Agent v1.0*
