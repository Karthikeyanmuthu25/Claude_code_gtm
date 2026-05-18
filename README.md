# Claude × GEO Entity Audit Agent

Reverse-engineers AI citation patterns to tell you exactly why competitors
get cited by Perplexity / ChatGPT / Gemini — and what you need to fix.

**Now powered by Exa neural search** — Step 1 is fully automated.

---

## How It Works (4 Steps)

| Step | What Happens | Tool |
|------|-------------|------|
| **Step 1** | Auto-mine pages AI engines cite for your query | **Exa** neural search |
| **Step 2** | Fetch full content (Exa API) + scrape fallback | httpx + BeautifulSoup |
| **Step 3** | Entity gap analysis: gaps, structure, brief | **Claude** Sonnet |
| **Step 4** | Save citability score, track monthly progress | JSON history |

---

## Setup

```bash
# 1. Create folder & virtual env
mkdir geo-entity-audit && cd geo-entity-audit
python3 -m venv venv && source venv/bin/activate

# 2. Install deps
pip install -r requirements.txt

# 3. Add your API keys
cp .env.example .env
nano .env
#  ANTHROPIC_API_KEY=sk-ant-...
#  EXA_API_KEY=...           ← get free at https://exa.ai
```

---

## Run It

**Interactive (guided prompts):**
```bash
python agent.py
```

**Fast CLI:**
```bash
python agent.py \
  -q "best AI SEO tools 2025" \
  -u "https://yoursite.com/page"
```

**With competitor discovery (`find_similar`):**
```bash
python agent.py \
  -q "best AI SEO tools 2025" \
  -u "https://yoursite.com/page" \
  --find-similar
```

**Manual URLs only (no Exa):**
```bash
python agent.py \
  -q "best AI SEO tools 2025" \
  -u "https://yoursite.com/page" \
  --no-exa \
  -c "https://cited1.com,https://cited2.com"
```

**Mix Exa + manual URLs:**
```bash
python agent.py \
  -q "best AI SEO tools 2025" \
  -u "https://yoursite.com/page" \
  -c "https://extra-url.com"
# Exa mines automatically AND adds your manual URL
```

---

## CLI Options

| Flag | Description |
|------|-------------|
| `-q` / `--query` | Target search query |
| `-u` / `--my-url` | Your page URL |
| `-c` / `--cited-urls` | Manual cited URLs (comma-separated, supplements Exa) |
| `-n` / `--exa-results` | Number of Exa results to mine (default: 8) |
| `--find-similar` | Also run Exa find_similar on your URL to find competitors |
| `--no-exa` | Skip Exa, use manual URLs only |

---

## What You Get Per Run

| Output | What It Tells You |
|--------|------------------|
| **Citability Score** | 0–100 vs cited competitors |
| **Entity Gaps** | Named entities missing from your page |
| **Answer Structure** | How cited pages organize (FAQ, tables, schema) |
| **Content Brief** | Prioritized HIGH / MEDIUM / LOW actions |
| **Trust Signals** | Author bio, stats, citations — what's missing |
| **Score History** | Monthly tracking (Step 4) |

Reports saved to `outputs/` as JSON for monthly comparison.

---

## Exa Integration Details

Exa replaces manual Perplexity copy-pasting with:

- **`exa.search_and_contents()`** — neural search returns top cited pages *with* full text and semantic highlights. No scraping needed.
- **`exa.find_similar_and_contents()`** — finds pages structurally similar to yours that are being cited instead. Use `--find-similar` to enable.
- **`use_autoprompt=True`** — Exa rewrites your query for better neural retrieval (closer to how AI engines actually search).
- **Graceful fallback** — if `EXA_API_KEY` is missing or a page has no Exa content, the tool scrapes it with httpx.

Get your free Exa API key at **https://exa.ai**
