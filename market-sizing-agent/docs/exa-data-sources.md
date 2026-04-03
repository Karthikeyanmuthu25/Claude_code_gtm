# Exa Search Strategy & Data Sources

## Overview

The `ExaSearchAgent` runs 13 semantic queries across 6 curated source categories using Exa's neural search API. Each query is domain-filtered to ensure high-quality, relevant results.

---

## Data Source Categories

### 1. Industry Reports

**Purpose:** Market size, CAGR, TAM/SAM benchmarks

| Domain | Data type |
|---|---|
| gartner.com | Magic Quadrant, market forecasts |
| forrester.com | Market research, buyer surveys |
| idc.com | Market size statistics, vendor share |
| g2.com | Category data, user reviews volume |
| statista.com | Market statistics, charts |
| grandviewresearch.com | TAM reports by category |
| marketsandmarkets.com | B2B market forecasts |
| mordorintelligence.com | Industry reports |
| businesswire.com | Press releases with market data |
| globenewswire.com | Press releases with market data |

**Queries run:**
```
{space} market size TAM SAM SOM {targetLocation} 2024 2025
{industry} total addressable market forecast growth rate
{space} industry revenue statistics {targetLocation} enterprise
```

---

### 2. Funding & Competitive Data

**Purpose:** VC investment levels, competitor valuations, deal flow

| Domain | Data type |
|---|---|
| crunchbase.com | Funding rounds, company profiles |
| pitchbook.com | Deal data, valuations |
| techcrunch.com | Funding announcements |
| venturebeat.com | AI/tech funding news |

**Queries run:**
```
{space} startup funding rounds 2023 2024 venture capital investment
{space} {targetLocation} series A B funding valuation
```

---

### 3. Buyer / ICP Data

**Purpose:** Buyer pain points, org structure, tech stack

| Domain | Data type |
|---|---|
| linkedin.com | Job postings, company size |
| glassdoor.com | Company culture, headcount |
| builtwith.com | Tech stack data |
| similarweb.com | Traffic and engagement data |
| gartner.com | Buyer survey data |
| forrester.com | Buyer journey research |

**Queries run:**
```
{primaryBuyer} {space} buying decisions budget software {targetLocation}
{primaryBuyer} pain points challenges {space} solutions 2024
```

---

### 4. Competitor Landscape

**Purpose:** Who else is in this space, how they position, reviews

| Domain | Data type |
|---|---|
| producthunt.com | New product launches |
| capterra.com | Software comparisons |
| g2.com | Category leaders, user reviews |
| getapp.com | Software alternatives |
| trustradius.com | B2B software reviews |

**Queries run:**
```
best {space} software tools {targetLocation} alternatives competitors
{space} market share leaders {targetLocation} top companies
```

---

### 5. GTM Benchmarks

**Purpose:** How this market buys, pricing norms, sales cycle length

| Domain | Data type |
|---|---|
| gartner.com | GTM benchmarks |
| forrester.com | Sales process research |
| idc.com | Go-to-market strategies |
| reuters.com | Business news |
| bloomberg.com | Business news |

**Queries run:**
```
{gtmMotion} {space} SaaS benchmark ACV {acvTier} {targetLocation}
SaaS {space} average contract value pricing model {targetLocation}
```

---

### 6. News & Trends

**Purpose:** Tailwinds, regulatory changes, major market events

| Domain | Data type |
|---|---|
| reuters.com | Business / tech news |
| bloomberg.com | Financial news |
| wsj.com | Business news |
| ft.com | Global business news |
| forbes.com | Startup / tech coverage |
| inc.com | SMB / growth coverage |

**Queries run:**
```
{space} market trends disruption 2024 2025 {targetLocation}
{industry} regulatory compliance changes {targetLocation} 2024
```

---

## Query Construction

Queries are dynamically built from user inputs:

```javascript
// Example for inputs:
// space = "AI-powered HR performance management"
// targetLocation = "United States"
// primaryBuyer = "VP of People / CHRO"

"AI-powered HR performance management market size TAM SAM SOM United States 2024 2025"
"VP of People / CHRO pain points challenges AI-powered HR performance management solutions 2024"
```

---

## Exa API Configuration

```javascript
{
  type: "neural",           // Semantic (not keyword) search
  useAutoprompt: true,      // Exa auto-improves queries
  numResults: 5–8,          // Per query, varies by category importance
  includeDomains: [...],    // Domain allowlist per category
  contents: {
    text: { maxCharacters: 800 },
    highlights: { numSentences: 3, highlightsPerUrl: 2 }
  }
}
```

---

## Rate Limiting

Queries are batched in groups of 5 with a 500ms pause between batches to avoid rate limiting.

Total API calls per run: **13 searches**

---

## Evidence Condensation

Before passing results to MarketAnalysisAgent, the `_condenseEvidence()` method:
- Caps each category at 6 results
- Truncates each snippet to 400 characters
- Retains title, URL, highlights, and date

This keeps the analysis prompt within ~4,000 input tokens.
