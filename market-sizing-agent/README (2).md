# Market Sizing Sub-Agent System

> AI-powered, personalised market sizing reports using Claude Code sub-agents and Exa semantic search.

---

## Overview

This system uses a **Claude Code sub-agent architecture** to collect inputs from a user, run semantic searches across curated data sources via Exa, analyse the results with Claude, and generate a personalised market sizing report in Markdown.

```
User / CLI
    │
    ▼
┌─────────────────────────────────────────────┐
│            Orchestrator Agent               │
│  Plans tasks · routes agents · merges       │
│  results · manages context window           │
└─────┬──────┬──────┬──────┬──────────────────┘
      │      │      │      │
      ▼      ▼      ▼      ▼
  Input   Exa    Market  Report
Collector Search Analysis Generator
 Agent   Agent   Agent    Agent
      │      │      │      │
      └──────┴──────┴──────┘
                 │
        Shared Memory / Scratchpad
         (summaries · search data
          analysis · file index)
                 │
         ┌───────┴────────┐
         │  Tool Layer    │
         │ File I/O       │
         │ Exa API        │
         │ Claude API     │
         └───────┬────────┘
                 │
    ┌────────────┴───────────────┐
    │    Production Safeguards   │
    │  Permission Gate           │
    │  Audit Logger              │
    │  Retry / Fallback          │
    │  Human-in-the-loop         │
    └────────────────────────────┘
```

---

## Quick Start

### 1. Install dependencies

```bash
cd market-sizing-agent
npm install
```

### 2. Set environment variables

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export EXA_API_KEY=your-exa-key-here
```

### 3. Run interactively

```bash
npm start
```

### 4. Run in batch mode (JSON input)

```bash
npm run batch sample-input.json
```

### 5. Run demo (no API keys needed for structure test)

```bash
npm run demo
```

---

## Input Fields

The system collects the following fields interactively (or via JSON):

| Field | Description | Example |
|---|---|---|
| `website` | Company website URL | `https://acme.com` |
| `targetLocation` | Target market geography | `United States` |
| `name` | Requestor's full name | `Priya Krishnan` |
| `email` | Requestor's email | `priya@acme.com` |
| `company` | Company name | `Acme Corp` |
| `stage` | Funding stage | `Series A` |
| `space` | Product / market category | `AI-powered HR software` |
| `primaryBuyer` | Primary buyer persona | `VP of People / CHRO` |
| `expectedACV` | Expected ACV in USD | `45000` |
| `gtmMotion` | Primary GTM motion | `Sales-led` |

---

## Architecture Deep Dive

See [`docs/architecture.md`](docs/architecture.md) for the full architecture documentation.

---

## Output

Reports are saved to `./reports/` as Markdown files named:

```
{company-slug}-market-sizing-{timestamp}.md
```

The report includes:
- Executive Summary
- TAM / SAM / SOM with methodology
- Competitive Landscape
- ICP Analysis with fit score
- GTM Motion Assessment
- Key Tailwinds and Risks
- Strategic Recommendations
- Data Sources

---

## Project Structure

```
market-sizing-agent/
├── orchestrator.js              # Main entry point + orchestration logic
├── demo.js                      # Demo with hardcoded inputs
├── package.json
│
├── agents/
│   ├── input-collector.js       # Sub-agent: interactive input collection + enrichment
│   ├── exa-search.js            # Sub-agent: semantic search via Exa API
│   ├── market-analysis.js       # Sub-agent: Claude market sizing analysis
│   └── report-generator.js      # Sub-agent: Markdown report generation
│
├── prompts/
│   ├── market-analysis.js       # System prompt for market analysis
│   └── report-generator.js      # System prompt for report generation
│
├── utils/
│   ├── audit-logger.js          # Immutable audit trail
│   ├── context-manager.js       # Shared scratchpad between agents
│   └── permission-gate.js       # Allow/deny policy for all tool calls
│
├── docs/
│   ├── architecture.md          # Full architecture documentation
│   ├── exa-data-sources.md      # Exa search strategy + data sources
│   └── report-schema.md         # Output report schema
│
└── reports/                     # Generated reports (auto-created)
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Yes | Your Anthropic API key |
| `EXA_API_KEY` | ✅ Yes | Your Exa API key |

---

## License

MIT
