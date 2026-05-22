"""
Tool connectivity test — Apify, Exa, OpenAI GPT-4o
"""

import os
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console(legacy_windows=False)

SAMPLE_COMPANY  = "Nando's UAE"
SAMPLE_DOMAIN   = "nandos.ae"
SAMPLE_WEBSITE  = "https://www.nandos.ae/"
SAMPLE_PERSON   = "George Kunnappally"
SAMPLE_LINKEDIN = "https://www.linkedin.com/in/georgekunnappally/"
SAMPLE_EMAIL    = "george@nandos.ae"

results = {}


def section(title: str):
    console.print()
    console.print(Panel.fit(f"[bold]{title}[/bold]", border_style="cyan", padding=(0, 2)))
    console.print()

def ok(msg, detail=""):
    console.print(f"  [bright_green]PASS[/bright_green]  {msg}" + (f"  [dim]{detail}[/dim]" if detail else ""))

def fail(msg, detail=""):
    console.print(f"  [red]FAIL[/red]  {msg}" + (f"  [dim]{detail}[/dim]" if detail else ""))

def warn(msg, detail=""):
    console.print(f"  [yellow]WARN[/yellow]  {msg}" + (f"  [dim]{detail}[/dim]" if detail else ""))


# ── 1. APIFY ──────────────────────────────────────────────────────────────────
section("1 · Apify Scraping")

apify_key = os.environ.get("APIFY_API_KEY", "")
if not apify_key:
    fail("APIFY_API_KEY not set in .env")
    results["apify"] = "NO KEY"
else:
    ok("APIFY_API_KEY found", apify_key[:12] + "...")
    from agent.tools.apify import ApifyScraper
    apify = ApifyScraper(apify_key)

    console.print("  [dim]Testing website crawl (nandos.ae, 2 pages)...[/dim]")
    web = apify.scrape_website(SAMPLE_WEBSITE, max_pages=2)
    if web.get("status") == "success":
        pages = len(web.get("items", []))
        ok("Website crawl", f"{pages} pages scraped")
        if pages > 0:
            item  = web["items"][0]
            title = item.get("metadata", {}).get("title", item.get("title", ""))[:70]
            console.print(f"       [dim]Page title: {title}[/dim]")
        results["apify_web"] = "OK"
    else:
        fail("Website crawl", web.get("error", "unknown error")[:100])
        results["apify_web"] = "FAIL"

    console.print("  [dim]Testing LinkedIn profile scrape (georgekunnappally)...[/dim]")
    li = apify.scrape_linkedin_profile(SAMPLE_LINKEDIN)
    if li.get("status") == "success":
        items = li.get("items", [])
        ok("LinkedIn scrape", f"{len(items)} item(s) returned")
        if items:
            p    = items[0]
            name = p.get("fullName", p.get("name", "—"))
            hdl  = p.get("headline", p.get("title", ""))[:60]
            console.print(f"       [dim]Name: {name}  |  {hdl}[/dim]")
        results["apify_linkedin"] = "OK"
    else:
        fail("LinkedIn scrape", li.get("error", "unknown error")[:100])
        results["apify_linkedin"] = "FAIL"

    results["apify"] = "OK" if results.get("apify_web") == "OK" else "FAIL"


# ── 2. EXA SEARCH ─────────────────────────────────────────────────────────────
section("2 · Exa Search")

exa_key = os.environ.get("EXA_API_KEY", "")
if not exa_key:
    fail("EXA_API_KEY not set in .env")
    results["exa"] = "NO KEY"
else:
    ok("EXA_API_KEY found", exa_key[:8] + "...")
    from agent.tools.exa import ExaSearch
    exa = ExaSearch(exa_key)

    tests = [
        ("Company Intel",   lambda: exa.search_company_intel(SAMPLE_COMPANY, SAMPLE_DOMAIN), "exa_company"),
        ("Person Intel",    lambda: exa.search_person_intel(SAMPLE_PERSON, company=SAMPLE_COMPANY, title="Managing Director"), "exa_person"),
        ("Domain Verify",   lambda: exa.verify_domain(SAMPLE_DOMAIN), "exa_domain"),
        ("Risk Signals",    lambda: exa.search_risk_signals(SAMPLE_COMPANY, SAMPLE_PERSON), "exa_risk"),
        ("Evidence Search", lambda: exa.search_evidence(SAMPLE_COMPANY, SAMPLE_DOMAIN), "exa_evidence"),
    ]

    for label, fn, key in tests:
        console.print(f"  [dim]Testing {label.lower()}...[/dim]")
        r = fn()
        if "error" in r:
            fail(label, r["error"][:100])
            results[key] = "FAIL"
        else:
            n   = len(r.get("results", []))
            top = r["results"][0].get("title", "") if r.get("results") else ""
            ok(label, f"{n} results" + (f"  |  top: {top[:50]}" if top else ""))
            results[key] = "OK"

    exa_tests = [results.get(k) for k in ["exa_company","exa_person","exa_domain","exa_risk","exa_evidence"]]
    results["exa"] = "OK" if all(v == "OK" for v in exa_tests) else "PARTIAL"


# ── 3. OPENAI GPT-4o ──────────────────────────────────────────────────────────
section("3 · OpenAI GPT-4o")

oai_key = os.environ.get("OPENAI_API_KEY", "")
if not oai_key:
    fail("OPENAI_API_KEY not set in .env")
    results["openai"] = "NO KEY"
elif oai_key.startswith("sk-ant-"):
    fail("OPENAI_API_KEY contains an Anthropic key (sk-ant-...)",
         "Get a real key at https://platform.openai.com/account/api-keys")
    results["openai"] = "WRONG KEY"
else:
    ok("OPENAI_API_KEY found", oai_key[:12] + "...")
    from openai import OpenAI
    client = OpenAI(api_key=oai_key)

    console.print("  [dim]Testing GPT-4o completion...[/dim]")
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=60,
            temperature=0,
            messages=[
                {"role": "system", "content": 'Reply with exactly: {"status":"ok","model":"gpt-4o"}'},
                {"role": "user",   "content": "ping"},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        ok("GPT-4o completion", f"model={resp.model}  ·  tokens={resp.usage.total_tokens}")
        console.print(f"       [dim]Response: {raw[:80]}[/dim]")
        results["openai_completion"] = "OK"
    except Exception as e:
        fail("GPT-4o completion", str(e)[:120])
        results["openai_completion"] = "FAIL"

    console.print("  [dim]Testing GPT-4o JSON mode (used by all 5 pipeline stages)...[/dim]")
    try:
        resp2 = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=80,
            temperature=0,
            messages=[
                {"role": "system", "content": 'Return only valid JSON: {"test":"passed","tool":"gpt-4o"}'},
                {"role": "user",   "content": "test json mode"},
            ],
        )
        raw2   = resp2.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        parsed = json.loads(raw2)
        ok("GPT-4o JSON mode", f"parsed cleanly -- {parsed}")
        results["openai_json"] = "OK"
    except Exception as e:
        fail("GPT-4o JSON mode", str(e)[:120])
        results["openai_json"] = "FAIL"

    results["openai"] = "OK" if results.get("openai_completion") == "OK" else "FAIL"


# ── SUMMARY TABLE ─────────────────────────────────────────────────────────────
console.print()
console.print(Panel.fit("[bold]TOOL TEST SUMMARY[/bold]", border_style="white", padding=(0, 2)))
console.print()

table = Table(show_header=True, header_style="bold dim", border_style="dim", box=None)
table.add_column("Tool",     style="bold", width=20)
table.add_column("Sub-test", width=26)
table.add_column("Status",   width=10)
table.add_column("Notes",    style="dim", width=36)

SC = {
    "OK":       "[bright_green]OK[/bright_green]",
    "PARTIAL":  "[yellow]PARTIAL[/yellow]",
    "FAIL":     "[red]FAIL[/red]",
    "NO KEY":   "[red]NO KEY[/red]",
    "WRONG KEY":"[red]WRONG KEY[/red]",
}

def row(tool, sub, key, note=""):
    s = results.get(key, "—")
    table.add_row(tool, sub, SC.get(s, s), note)

row("Apify",          "Website Crawl",   "apify_web",          "nandos.ae")
row("",               "LinkedIn Scrape", "apify_linkedin",     "georgekunnappally")
row("Exa Search",     "Company Intel",   "exa_company",        "")
row("",               "Person Intel",    "exa_person",         "George Kunnappally")
row("",               "Domain Verify",   "exa_domain",         "nandos.ae")
row("",               "Risk Signals",    "exa_risk",           "")
row("",               "Evidence Search", "exa_evidence",       "")
row("OpenAI GPT-4o",  "Completion",      "openai_completion",  "gpt-4o")
row("",               "JSON Mode",       "openai_json",        "pipeline mode")

console.print(table)
console.print()

if results.get("openai") in ("NO KEY","WRONG KEY","FAIL"):
    console.print("  [red bold]Pipeline blocked — OpenAI GPT-4o key required.[/red bold]")
elif all(results.get(k) in ("OK","PARTIAL") for k in ["apify","exa","openai"]):
    console.print("  [bright_green bold]All tools operational — pipeline ready.[/bright_green bold]")
else:
    console.print("  [yellow bold]Some tools unavailable — check keys above.[/yellow bold]")
console.print()
