"""
Claude × GEO Entity Audit Agent
=================================
Reverse-engineers AI citation patterns in 4 steps:
  Step 1 → Mine live AI citations via Exa (neural search) OR paste URLs manually
  Step 2 → Feed cited URLs into Claude for deep analysis
  Step 3 → Claude outputs entity gaps, answer structure, content brief
  Step 4 → Run monthly, retest citability score
"""

import os
import json
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import anthropic
from exa_py import Exa
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box
import click
from dotenv import load_dotenv

load_dotenv()

console = Console()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

_exa_client = None
def get_exa():
    global _exa_client
    if _exa_client is None:
        key = os.environ.get("EXA_API_KEY", "")
        if key and key != "your_exa_api_key_here":
            _exa_client = Exa(api_key=key)
    return _exa_client

OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# STEP 1 — Exa: Auto-mine AI citation URLs
# ─────────────────────────────────────────────

def exa_mine_citations(query: str, num_results: int = 8) -> list[dict]:
    """
    Use Exa neural search to find pages that AI engines actually cite for a query.
    Returns list of {url, title, highlights, content, published_date}.
    """
    exa = get_exa()
    if not exa:
        return []
    try:
        from exa_py.api import TextContentsOptions, HighlightsContentsOptions
        results = exa.search(
            query,
            type="auto",
            num_results=num_results,
            contents={"text": {"max_characters": 3000}, "highlights": {"num_sentences": 3, "highlights_per_url": 2}},
        )
        mined = []
        for r in results.results:
            mined.append({
                "url": r.url,
                "title": r.title or r.url,
                "highlights": getattr(r, "highlights", []) or [],
                "content": getattr(r, "text", "") or "",
                "published_date": getattr(r, "published_date", None) or "unknown",
                "source": "exa",
            })
        return mined
    except Exception as e:
        console.print(f"[yellow]Warning: Exa search failed: {e}[/yellow]")
        return []


def exa_find_similar(my_url: str, num_results: int = 4) -> list[dict]:
    """
    Use Exa find_similar to discover pages competing with yours.
    These are likely being cited instead of you.
    """
    exa = get_exa()
    if not exa:
        return []
    try:
        results = exa.find_similar(
            my_url,
            num_results=num_results,
            exclude_source_domain=True,
            contents={"text": {"max_characters": 2000}, "highlights": {"num_sentences": 2, "highlights_per_url": 1}},
        )
        similar = []
        for r in results.results:
            similar.append({
                "url": r.url,
                "title": r.title or r.url,
                "highlights": getattr(r, "highlights", []) or [],
                "content": getattr(r, "text", "") or "",
                "published_date": getattr(r, "published_date", None) or "unknown",
                "source": "exa_similar",
            })
        return similar
    except Exception as e:
        console.print(f"[yellow]Warning: Exa find_similar failed: {e}[/yellow]")
        return []


def display_exa_results(results: list[dict], title: str = "Exa Results"):
    table = Table(
        title=f"🔎 {title}",
        box=box.ROUNDED,
        border_style="bright_cyan",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", width=35)
    table.add_column("URL", style="dim cyan", width=42)
    table.add_column("Date", style="dim", width=12)
    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            (r["title"] or "")[:50] + ("…" if len(r["title"] or "") > 50 else ""),
            r["url"][:55] + ("…" if len(r["url"]) > 55 else ""),
            str(r.get("published_date", ""))[:10],
        )
    console.print(table)


# ─────────────────────────────────────────────
# STEP 2 — URL Scraper (fallback / supplement)
# ─────────────────────────────────────────────

async def fetch_page_text(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as hc:
            r = await hc.get(url, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            title = soup.title.string.strip() if soup.title else url
            body = soup.get_text(separator="\n", strip=True)
            body_trimmed = body[:3000] + ("..." if len(body) > 3000 else "")
            return {"url": url, "title": title, "content": body_trimmed, "error": None, "source": "scrape"}
    except Exception as e:
        return {"url": url, "title": url, "content": "", "error": str(e), "source": "scrape"}


async def scrape_all_urls(urls: list[str]) -> list[dict]:
    tasks = [fetch_page_text(u) for u in urls]
    return await asyncio.gather(*tasks)


# ─────────────────────────────────────────────
# STEP 3 — Claude Entity Audit Analysis
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert AI SEO / GEO (Generative Engine Optimization) strategist.
Your job: analyze pages that AI engines cite for a query, then produce a detailed Entity Audit Report.

You must identify:
1. ENTITY GAPS — named entities (people, brands, tools, stats, frameworks, definitions) that appear 
   across the cited pages but are MISSING from the user's own content.
2. ANSWER STRUCTURE — how cited pages organize their answers (headers, schema, FAQ, lists, tables).
3. CONTENT BRIEF — specific actions the user should take to become citeable by AI engines.

Always output valid JSON only. No markdown fences, no preamble. Follow the exact schema provided."""

ANALYSIS_PROMPT_TEMPLATE = """
QUERY: {query}

MY PAGE URL: {my_url}
MY PAGE CONTENT:
{my_content}

CITED PAGES ({n} pages) — sourced via Exa neural search + optional manual URLs:
{cited_pages_block}

Produce a JSON report with EXACTLY this structure:
{{
  "query": "{query}",
  "audit_date": "{today}",
  "citability_score": <integer 0-100, estimate how likely my page is to be cited vs cited pages>,
  "entity_gaps": [
    {{
      "entity": "<entity name>",
      "type": "<person|brand|tool|stat|framework|definition|concept>",
      "appears_in_sources": <count of cited pages that mention it>,
      "missing_from_my_page": true,
      "suggested_addition": "<1-sentence suggestion on how to add this entity>"
    }}
  ],
  "answer_structure": {{
    "patterns_found": ["<pattern 1>", "<pattern 2>"],
    "schema_used": ["<FAQ|HowTo|Article|None>"],
    "avg_word_count_cited": <estimate>,
    "missing_in_my_page": ["<missing structure element 1>", "<missing structure element 2>"]
  }},
  "content_brief": [
    {{
      "priority": "<high|medium|low>",
      "action": "<specific action>",
      "why": "<why this improves AI citability>"
    }}
  ],
  "trust_signals_found": [
    {{
      "signal": "<trust signal>",
      "present_in_n_sources": <count>,
      "present_in_my_page": <true|false>
    }}
  ],
  "recommended_entities_to_add": ["<entity 1>", "<entity 2>", "<entity 3>"]
}}"""


def build_cited_pages_block(pages: list[dict]) -> str:
    blocks = []
    for i, page in enumerate(pages, 1):
        src_label = f"[via {page.get('source', 'scrape')}]"
        if page.get("error"):
            blocks.append(f"[PAGE {i}] {src_label} URL: {page['url']}\nERROR: {page['error']}\n")
        else:
            highlights_text = ""
            if page.get("highlights"):
                highlights_text = "\nHIGHLIGHTS:\n" + "\n".join(
                    f"  • {h}" for h in page["highlights"]
                )
            blocks.append(
                f"[PAGE {i}] {src_label} URL: {page['url']}\n"
                f"TITLE: {page['title']}\n"
                f"PUBLISHED: {page.get('published_date', 'unknown')}"
                f"{highlights_text}\n"
                f"CONTENT:\n{page['content'][:1500]}\n"
            )
    return "\n---\n".join(blocks)


def run_claude_audit(query: str, my_url: str, my_content: str, cited_pages: list[dict]) -> dict:
    cited_block = build_cited_pages_block(cited_pages)
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        query=query,
        my_url=my_url,
        my_content=my_content[:2000],
        cited_pages_block=cited_block,
        n=len(cited_pages),
        today=datetime.today().strftime("%Y-%m-%d"),
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()
    # Attempt to repair truncated JSON by closing open structures
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract valid JSON up to the last complete top-level field
        import re
        match = re.search(r'^\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


# ─────────────────────────────────────────────
# STEP 4 — Citability Score Tracker
# ─────────────────────────────────────────────

def load_history(query_slug: str) -> list[dict]:
    hist_path = OUTPUTS_DIR / f"{query_slug}_history.json"
    if hist_path.exists():
        return json.loads(hist_path.read_text())
    return []


def save_to_history(query_slug: str, report: dict):
    hist_path = OUTPUTS_DIR / f"{query_slug}_history.json"
    history = load_history(query_slug)
    history.append({
        "date": report["audit_date"],
        "citability_score": report["citability_score"],
        "entity_gaps_count": len(report.get("entity_gaps", [])),
    })
    hist_path.write_text(json.dumps(history, indent=2))


def save_report(query_slug: str, report: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = OUTPUTS_DIR / f"{query_slug}_{ts}_audit.json"
    out_path.write_text(json.dumps(report, indent=2))
    return out_path


# ─────────────────────────────────────────────
# RICH DISPLAY LAYER
# ─────────────────────────────────────────────

def display_banner():
    console.print(Panel.fit(
        "[bold orange1]Claude[/bold orange1] × [bold green]GEO[/bold green]  [bold white]Entity Audit Agent[/bold white]\n"
        "[dim]Powered by [bold cyan]Exa[/bold cyan] neural search + [bold orange1]Claude[/bold orange1] entity analysis[/dim]\n"
        "[dim]Reverse-engineer AI citation patterns in 4 steps[/dim]",
        border_style="bright_black",
    ))


def display_score(score: int):
    color = "red" if score < 40 else "yellow" if score < 70 else "green"
    bar = "█" * (score // 5) + "░" * (20 - score // 5)
    console.print(f"\n[bold]Citability Score:[/bold] [{color}]{bar}[/{color}] [bold {color}]{score}/100[/bold {color}]\n")


def display_entity_gaps(gaps: list[dict]):
    if not gaps:
        console.print("[green]✓ No entity gaps found![/green]")
        return
    table = Table(title="🔍 Entity Gaps", box=box.ROUNDED, show_lines=True, border_style="orange1")
    table.add_column("Entity", style="bold cyan", width=20)
    table.add_column("Type", style="dim", width=12)
    table.add_column("In Sources", justify="center", width=10)
    table.add_column("Suggested Addition", width=48)
    for g in gaps[:15]:
        table.add_row(
            g["entity"],
            g["type"],
            str(g["appears_in_sources"]),
            g["suggested_addition"],
        )
    console.print(table)


def display_content_brief(brief: list[dict]):
    table = Table(title="📋 Content Brief", box=box.ROUNDED, show_lines=True, border_style="green")
    table.add_column("Priority", width=8)
    table.add_column("Action", width=40)
    table.add_column("Why It Helps AI Citability", width=40)
    priority_colors = {"high": "red", "medium": "yellow", "low": "dim"}
    for item in brief:
        color = priority_colors.get(item["priority"], "white")
        table.add_row(
            f"[{color}]{item['priority'].upper()}[/{color}]",
            item["action"],
            item["why"],
        )
    console.print(table)


def display_trust_signals(signals: list[dict]):
    table = Table(title="🛡️ Trust Signals", box=box.SIMPLE, border_style="blue")
    table.add_column("Signal", width=30)
    table.add_column("In N Sources", justify="center", width=12)
    table.add_column("On My Page?", justify="center", width=12)
    for s in signals:
        icon = "[green]✓[/green]" if s["present_in_my_page"] else "[red]✗[/red]"
        table.add_row(s["signal"], str(s["present_in_n_sources"]), icon)
    console.print(table)


def display_history(history: list[dict]):
    if not history:
        return
    console.print("\n[bold]📈 Citability Score History[/bold]")
    for h in history[-6:]:
        score = h["citability_score"]
        bar = "█" * (score // 5)
        color = "red" if score < 40 else "yellow" if score < 70 else "green"
        console.print(f"  {h['date']}  [{color}]{bar}[/{color}] {score}")


# ─────────────────────────────────────────────
# MAIN CLI
# ─────────────────────────────────────────────

@click.command()
@click.option("--query", "-q", default=None, help="The search query to audit")
@click.option("--my-url", "-u", default=None, help="Your page URL to analyze")
@click.option("--cited-urls", "-c", default=None, help="Comma-separated manual cited URLs (supplements Exa)")
@click.option("--exa-results", "-n", default=8, type=int, help="Number of Exa results to mine (default: 8)")
@click.option("--no-exa", is_flag=True, help="Skip Exa auto-mining, use manual URLs only")
@click.option("--find-similar", is_flag=True, help="Also run Exa find_similar on your page URL")
def main(query, my_url, cited_urls, exa_results, no_exa, find_similar):
    """
    Claude × GEO Entity Audit — Reverse-engineer AI citation patterns.
    
    \b
    Step 1: Exa auto-mines pages AI engines cite for your query (or paste URLs)
    Step 2: Agent fetches full content via Exa API (no scraping needed!)
    Step 3: Claude returns entity gaps, answer structure, content brief
    Step 4: Track citability score monthly
    
    \b
    Requires in .env:
      ANTHROPIC_API_KEY=...
      EXA_API_KEY=...        (get free key at exa.ai)
    """
    display_banner()

    # ── Collect inputs ──
    if not query:
        query = Prompt.ask("\n[bold cyan]Step 1[/bold cyan] → Enter your target [bold]search query[/bold]")
    if not my_url:
        my_url = Prompt.ask("[bold cyan]       [/bold cyan]   Your page URL [dim](the page you want to get cited)[/dim]")

    all_cited_pages: list[dict] = []

    # ── Step 1a: Exa auto-mining ──
    exa_key = os.environ.get("EXA_API_KEY", "")
    exa_available = bool(exa_key and exa_key != "your_exa_api_key_here")

    if not no_exa:
        if not exa_available:
            console.print("[yellow]⚠ EXA_API_KEY not set — falling back to manual URL input.[/yellow]")
            no_exa = True
        else:
            console.print(f"\n[bold cyan]Step 1[/bold cyan] → [bold]Exa[/bold] mining top {exa_results} AI-cited pages for: [italic]\"{query}\"[/italic]\n")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task("Querying Exa neural search...", total=None)
                mined = exa_mine_citations(query, num_results=exa_results)

            if mined:
                display_exa_results(mined, title=f"Exa: Top pages AI cites for \"{query}\"")
                all_cited_pages.extend(mined)
                console.print(f"[green]✓ Exa mined {len(mined)} cited pages[/green]")
            else:
                console.print("[yellow]No Exa results — will use manual URLs.[/yellow]")

            if find_similar:
                console.print(f"\n[dim]→ Running Exa find_similar for your URL...[/dim]")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                    progress.add_task("Finding similar competing pages...", total=None)
                    similar = exa_find_similar(my_url, num_results=4)
                if similar:
                    display_exa_results(similar, title="Exa: Pages competing with yours")
                    existing_urls = {p["url"] for p in all_cited_pages}
                    for s in similar:
                        if s["url"] not in existing_urls:
                            all_cited_pages.append(s)
                    console.print(f"[green]✓ Added {len(similar)} competitor pages[/green]")

    # ── Step 1b: Manual URLs ──
    if not cited_urls and no_exa:
        console.print("\n[bold cyan]       [/bold cyan]   Paste [bold]cited URLs[/bold] from Perplexity/ChatGPT/Gemini/Claude")
        console.print("       [dim]Separate multiple URLs with commas or new lines.[/dim]")
        console.print("       [dim]Type 'done' on empty line when finished.[/dim]\n")
        url_lines = []
        while True:
            line = Prompt.ask("       URL").strip()
            if line.lower() in ("done", ""):
                break
            url_lines.append(line)
        cited_urls = ",".join(url_lines)

    if cited_urls:
        manual_url_list = [u.strip() for u in cited_urls.replace("\n", ",").split(",") if u.strip()]
        if manual_url_list:
            existing_urls = {p["url"] for p in all_cited_pages}
            new_manual = [
                {"url": u, "title": u, "content": "", "highlights": [], "published_date": "", "source": "manual"}
                for u in manual_url_list if u not in existing_urls
            ]
            if new_manual:
                console.print(f"\n[dim]→ Adding {len(new_manual)} manual URL(s)...[/dim]")
                all_cited_pages.extend(new_manual)

    if not all_cited_pages:
        console.print("[red]No cited URLs found. Provide --cited-urls or set EXA_API_KEY.[/red]")
        return

    console.print(f"\n[dim]→ Query:[/dim] {query}")
    console.print(f"[dim]→ My URL:[/dim] {my_url}")
    console.print(f"[dim]→ Total cited pages:[/dim] {len(all_cited_pages)}\n")

    # ── Step 2: Fetch my page + fill missing content ──
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Step 2 → Fetching your page content...", total=None)
        my_page_data = asyncio.run(fetch_page_text(my_url))
        my_content = my_page_data.get("content", "")

        needs_scrape = [p for p in all_cited_pages if not p.get("content", "").strip()]
        if needs_scrape:
            progress.update(task, description=f"Step 2 → Scraping {len(needs_scrape)} pages (no Exa content)...")
            scraped = asyncio.run(scrape_all_urls([p["url"] for p in needs_scrape]))
            for orig, sp in zip(needs_scrape, scraped):
                orig["content"] = sp.get("content", "")
                orig["error"] = sp.get("error")

    ok = sum(1 for p in all_cited_pages if p.get("content", "").strip())
    console.print(f"[green]✓ Content ready for {ok}/{len(all_cited_pages)} cited pages[/green]")

    # ── Step 3: Claude Entity Audit ──
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("Step 3 → Claude analyzing entity gaps...", total=None)
        try:
            report = run_claude_audit(query, my_url, my_content, all_cited_pages)
        except Exception as e:
            console.print(f"[red]Claude analysis failed: {e}[/red]")
            return

    console.print("[green]✓ Claude entity audit complete[/green]\n")

    # ── Display Results ──
    console.rule("[bold]ENTITY AUDIT REPORT[/bold]")
    display_score(report.get("citability_score", 0))
    display_entity_gaps(report.get("entity_gaps", []))
    console.print()

    ans = report.get("answer_structure", {})
    if ans:
        console.print(Panel(
            f"[bold]Patterns Found:[/bold] {', '.join(ans.get('patterns_found', []))}\n"
            f"[bold]Schema Used:[/bold] {', '.join(ans.get('schema_used', []))}\n"
            f"[bold]Avg Word Count (cited pages):[/bold] {ans.get('avg_word_count_cited', 'N/A')}\n"
            f"[bold]Missing in your page:[/bold] {', '.join(ans.get('missing_in_my_page', []))}",
            title="📐 Answer Structure",
            border_style="cyan",
        ))
        console.print()

    display_content_brief(report.get("content_brief", []))
    console.print()
    display_trust_signals(report.get("trust_signals_found", []))

    recs = report.get("recommended_entities_to_add", [])
    if recs:
        console.print(f"\n[bold]⚡ Top Entities to Add:[/bold] {', '.join(recs)}")

    # ── Step 4: Save + History ──
    query_slug = query.lower().replace(" ", "_")[:40]
    out_path = save_report(query_slug, report)
    save_to_history(query_slug, report)
    display_history(load_history(query_slug))

    console.print(f"\n[dim]Report saved → {out_path}[/dim]")
    console.print(Panel.fit(
        "[bold green]Audit Complete![/bold green]\n"
        "[dim]Step 4: Re-run monthly to track citability improvement.[/dim]\n"
        f"[dim]Run: python agent.py -q \"{query}\" -u \"{my_url}\"[/dim]",
        border_style="green",
    ))


if __name__ == "__main__":
    main()
