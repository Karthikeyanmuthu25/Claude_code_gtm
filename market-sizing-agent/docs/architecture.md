# Claude Code Sub-Agent Architecture
## Market Sizing Report System

> Production-standard architecture document covering orchestration, sub-agents, tool layer, shared memory, and production safeguards.

---

## 1. System Overview

This system implements the **Claude Code sub-agent pattern**: a top-level orchestrator decomposes a complex user request into discrete tasks, delegates each to a specialised sub-agent with a narrow context, and synthesises results via a shared memory scratchpad.

The specific application is **personalised market sizing**: the user answers 10 questions, the system runs 13 semantic searches via Exa across Crunchbase, Gartner/Forrester/IDC, LinkedIn, and news sources, then generates a structured Markdown + HTML report with embedded Chart.js visualisations.

---

## 2. Architecture Diagram

```
USER LAYER
  CLI (interactive)  OR  JSON batch file
  Fields: website · location · name · email · company
          stage · space · primary buyer · ACV · GTM motion
                              |
                              v
ORCHESTRATOR LAYER
  +----------------------------------------------------------+
  |  Orchestrator Agent                                       |
  |  1. Receives user request (CLI or JSON)                  |
  |  2. Pushes 4 tasks onto task queue                       |
  |  3. Invokes sub-agents in sequence                       |
  |  4. Reads/writes shared ContextManager after each agent  |
  |  5. Runs permission gate before every file write         |
  |  6. Flushes audit log on completion                      |
  +-----------------------------+----------------------------+
                                |
  +------------------+    +----------------------------+
  |  ContextManager  |    |  Task Queue (in-memory)    |
  |  (shared memory) |    |                            |
  |                  |    |  1. collect_inputs         |
  |  inputs       ---|->  |  2. exa_search             |
  |  searchData   ---|->  |  3. market_analysis        |
  |  analysis     ---|->  |  4. report_generation      |
  +------------------+    |  5. render_html_charts     |
                          +----------------------------+
                              |
                              v
SUB-AGENT LAYER
  +----------------+  +----------------+  +----------------+  +----------------+
  |  Input         |  |  Exa           |  |  Market        |  |  Report        |
  |  Collector     |->|  Searcher      |->|  Analyst       |->|  Generator     |
  |                |  |                |  |                |  |                |
  |  Interactive   |  |  13 queries    |  |  TAM/SAM/SOM   |  |  Markdown +    |
  |  CLI prompts   |  |  4 categories  |  |  ICP fit score |  |  chart blocks  |
  |  Validation    |  |  Parallel x5   |  |  GTM fit score |  |  HTML render   |
  |  LLM enrich    |  |  500ms delay   |  |  Risks +       |  |  Chart.js      |
  |  1 LLM call    |  |  0 LLM calls   |  |  tailwinds     |  |  1 LLM call    |
  +----------------+  +----------------+  |  1 LLM call    |  +----------------+
                                          +----------------+
                              |
TOOL LAYER
  +------------+  +--------------+  +-------------+  +------------+
  |  File I/O  |  |  Exa Neural  |  |  Anthropic  |  |  Chart.js  |
  |            |  |  Search API  |  |  Claude API |  |  (CDN)     |
  |  reports/  |  |              |  |             |  |            |
  |  audit-    |  |  Crunchbase  |  |  claude-    |  |  line/bar  |
  |  logs/     |  |  Gartner/    |  |  opus-4-5   |  |  scatter/  |
  |            |  |  Forrester/  |  |             |  |  radar     |
  |            |  |  IDC         |  |  3 calls    |  |            |
  |            |  |  LinkedIn    |  |             |  |            |
  |            |  |  News        |  |             |  |            |
  +------------+  +--------------+  +-------------+  +------------+
                              |
PRODUCTION SAFEGUARD LAYER
  +------------------+  +-------------------+  +--------------------+
  |  Permission Gate |  |  Audit Logger     |  |  Human-in-the-loop |
  |                  |  |                   |  |                    |
  |  Auto-allow:     |  |  Immutable        |  |  Triggered for:    |
  |  FILE_WRITE      |  |  append-only JSON |  |  FILE_DELETE       |
  |  EXA_SEARCH      |  |                   |  |  NETWORK_EXTERNAL  |
  |  CLAUDE_API      |  |  Every event:     |  |                    |
  |                  |  |  timestamp +      |  |  Presents action + |
  |  Deny + confirm: |  |  elapsed time     |  |  context, waits    |
  |  FILE_DELETE     |  |                   |  |  for y/n           |
  |  EXTERNAL_NET    |  |  Flushed to       |  |                    |
  |                  |  |  audit-logs/      |  |                    |
  +------------------+  +-------------------+  +--------------------+
                              |
                    Result / error feedback
                              |
                              v
                    Orchestrator merges results
                    Saves .md + .html to reports/
                    Flushes audit log -> returns to user
```

---

## 3. Sub-Agent Details

### 3.1 InputCollectorAgent

| Property | Value |
|---|---|
| File | `agents/input-collector.js` |
| Claude calls | 1 (input enrichment) |
| Writes to context | `inputs` |
| Output fields | 10 raw + 4 enriched |

**Fields collected:**

| Field | Validation |
|---|---|
| `website` | Must match `https?://` |
| `targetLocation` | Required string |
| `name` | Required string |
| `email` | RFC email format |
| `company` | Required string |
| `stage` | Choice list |
| `space` | Required string |
| `primaryBuyer` | Required string |
| `expectedACV` | Positive number |
| `gtmMotion` | Choice list |

**LLM enrichment adds:** `industry`, `acvTier`, `icp`, `geographyCode`

---

### 3.2 ExaSearchAgent

| Property | Value |
|---|---|
| File | `agents/exa-search.js` |
| API | Exa Neural Search |
| Total queries | 13 |
| Batch size | 5 parallel + 500ms gap |
| Writes to context | `searchData` |

**Search categories:**

| Category | Key domains | Queries |
|---|---|---|
| Industry reports | Gartner, Forrester, IDC, G2, Statista | 3 |
| Funding data | Crunchbase, PitchBook, TechCrunch | 2 |
| Buyer / ICP | LinkedIn, Glassdoor, SimilarWeb | 2 |
| Competitor landscape | G2, Capterra, ProductHunt | 2 |
| GTM benchmarks | Industry reports + news | 2 |
| News & trends | Reuters, Bloomberg, Forbes | 2 |

---

### 3.3 MarketAnalysisAgent

| Property | Value |
|---|---|
| File | `agents/market-analysis.js` |
| Claude calls | 1 |
| Model | `claude-opus-4-5` |
| Max tokens | 8,192 |
| Writes to context | `analysis` |

**SOM stage multipliers:**

| Stage | 3-year SOM % of SAM |
|---|---|
| Pre-seed / Seed | 0.1–0.5% |
| Series A | 0.5–2.0% |
| Series B+ | 2.0–5.0% |

---

### 3.4 ReportGeneratorAgent + ChartRenderer

| Property | Value |
|---|---|
| File | `agents/report-generator.js` + `utils/chart-renderer.js` |
| Claude calls | 1 |
| Output | `.md` file + `.html` file |
| Chart library | Chart.js 4.4.0 via CDN |

**Embedded chart blocks per report:**

| Section | Chart type |
|---|---|
| Market Overview | Line (growth forecast) |
| TAM/SAM/SOM Breakdown | Bar (funnel) |
| 3-Year Revenue Ramp | Bar (ARR targets) |
| Competitive Landscape | Scatter (positioning matrix) |
| GTM Assessment | Radar (6-axis readiness) |

---

## 4. Shared Memory Contract

| Context key | Set by | Read by |
|---|---|---|
| `inputs` | InputCollectorAgent | MarketAnalysisAgent, ReportGeneratorAgent |
| `searchData` | ExaSearchAgent | MarketAnalysisAgent, ReportGeneratorAgent |
| `analysis` | MarketAnalysisAgent | ReportGeneratorAgent |

---

## 5. Permission Gate Policy

| Action | Auto-allow? | Notes |
|---|---|---|
| `FILE_WRITE` | Yes | Path within `reports/` or `audit-logs/` |
| `EXA_SEARCH` | Yes | Always |
| `CLAUDE_API` | Yes | Always |
| `FILE_DELETE` | No | Requires human y/n via stdin |
| `NETWORK_EXTERNAL` | No | Unlisted domains require confirmation |

---

## 6. Token Budget

| Agent call | Input (est.) | Output (est.) |
|---|---|---|
| Input enrichment | ~300 | ~200 |
| Market analysis | ~4,000 | ~2,000 |
| Report generation | ~5,000 | ~3,000 |
| **Total** | **~9,300** | **~5,200** |

---

## 7. Error Handling

| Error scenario | Handling |
|---|---|
| Exa query fails | Log warning, return empty hits, continue |
| Analysis JSON parse fails | Fall back to raw text, log warning |
| Claude API error | Propagate → log → throw → surface to user |
| Permission denied | Throw, log, clean stop |
| Context overflow | `summarise()` truncates to `maxChars` |
| Chart block parse error | Log warning, skip chart, continue |

---

## 8. Running the System

```bash
# Install
npm install

# Set keys
export ANTHROPIC_API_KEY=sk-ant-...
export EXA_API_KEY=your-exa-key

# Interactive mode
npm start

# Batch mode
node orchestrator.js --json sample-input.json

# Render existing .md to HTML
node utils/chart-renderer.js reports/my-report.md
```

---

*Architecture v1.0 — Market Sizing Sub-Agent System*
