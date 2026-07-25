# Early-Stage Market Discovery Agent

A terminal CLI implementing the first slice of the Early-Stage Market
Discovery workflow:

```
Business Idea -> Problem Discovery -> Market Discovery -> ICP Discovery
-> Customer Discovery -> Validation -> GTM Recommendation
```

This build covers:

- **Phase 1 — Business Understanding**: collect the founder's raw input
  (product idea, vision, features, assumptions, founder knowledge) and
  synthesize it into a sharp problem statement, testable hypotheses, and
  concrete success criteria.
- **Research Planner**: turns Phase 1's output into a tailored brief for
  each of the 7 secondary-research agents (Industry, Competitor, Community,
  Search Intent, Funding, Job Market, Social Intelligence) — including a
  priority order, since not every idea needs all 7 run with equal weight.
- **Secondary-research agents** (Phase 2, all 7 built): each uses a
  two-step Perplexity (search) + OpenAI (structuring) pipeline to answer
  its tailored brief from the research plan with sourced, confidence-rated
  findings — see "Providers" below.
  - **Industry, Community, Search Intent, Funding, Job Market, Social
    Intelligence Agents** — landscape-level: answer a brief's questions
    about the idea as a whole. Share one execution engine
    (`research_agents/_base.py`) and one CLI command pattern
    (`agent._run_landscape_agent_command`), so each is a ~150-line module
    (brief-specific questions, tool schema, system prompt) plus a 6-line
    `cmd_*` wrapper.
  - **Competitor Agent** — per-item: given a competitor's public LinkedIn
    company-page URL, researches that one company (product, positioning,
    pricing, customers, weaknesses). Takes a list of URLs and runs them as
    a batch; no `opportunity_signal` per-competitor since that's a
    landscape-level judgment made across all of them together.

- **Research Synthesizer** (Phase 3): reads whatever secondary-research
  findings exist for a session (not all 7 required) plus Phase 1's
  hypotheses, and rolls them into one opportunity assessment — a 0-100
  score, a direct go/no-go recommendation, a verdict per hypothesis
  (Supported/Refuted/Mixed/Untested with evidence), key strengths/risks,
  and which open questions only primary research (real customer
  conversations) can still resolve. Does no search of its own — pure
  OpenAI structured-output reasoning over evidence already gathered.
- **ICP Discovery** (Phase 4): the first phase that reasons about WHO to
  sell to, not just whether the idea is viable. Follows a 9-step ICP
  framework end to end — Market -> Industry -> Firmographics ->
  Technographics -> Buyer Persona (distinguishing who feels the pain from
  who holds budget authority) -> Pain Points -> Buying Signals ->
  Exclusion Criteria -> ICP Scoring & Prioritization — and produces a
  primary ICP (plus 0-2 secondary segments if evidence supports them), a
  weighted scoring rubric, and a **Qualified Account Spec**: concrete
  firmographic/technographic/buying-signal filters and buyer titles phrased
  to paste directly into Clay's or Apollo's free-tier search UI or
  LinkedIn Sales Navigator. This pipeline does not call Clay/Apollo APIs
  itself — it hands off the spec for building the real account list by
  hand. Unlike the synthesizer, this phase DOES search: Perplexity grounds
  real-world buyer/segment/tech-stack norms for the category, while
  OpenAI's structuring step combines that with everything already known
  internally (hypotheses, the Phase 3 synthesis verdict, secondary-research
  findings) via `run_research_pipeline`'s `extra_context` parameter —
  external grounding and internal context stay separate so Perplexity isn't
  wastefully asked to "search" for facts already in the session.
- **Market Sizing** (Phase 4b, runs after ICP Discovery): sizes **TAM /
  SAM / SOM**. SAM is a genuine subset of TAM, narrowed using the ICP's
  actual firmographic/industry/technographic filters (not a generic
  percentage haircut); SOM is a realistic, time-bound slice of SAM grounded
  in the named competitors' scale/funding (Phase 2B) and the Phase 3
  synthesis's confidence — a conservative capture rate for an early-stage
  entrant facing funded, established competitors, unless there's a specific
  reason to expect more. Every dollar figure is a range, never false
  precision, and each estimate states its methodology plainly: top-down
  (a real published estimate, cited) or bottom-up (company-count x average
  deal size) — niche/emerging categories frequently have no clean published
  number, so bottom-up reasoning is treated as equally valid, just lower
  confidence when unconfirmed. Same two-step pattern as ICP Discovery:
  Perplexity grounds published market-size/company-count data, OpenAI
  structures that plus everything already known (ICP, synthesis,
  secondary-research findings, including competitor pricing already
  gathered) via `extra_context`.
- **Customer Discovery** (Phase 5): turns the ICP and whatever's still
  open from Phase 3 into an actionable plan for talking to real prospects
  — an interview guide where every question is tied to a specific
  hypothesis/open question it tests (favoring past-behavior questions over
  hypotheticals, to avoid the "Mom Test" false-positive-validation
  pitfall), named recruiting channels, a short outreach message template,
  screening criteria, and concrete falsifiable success criteria for the
  round of interviews. Same two-step pattern as ICP Discovery: Perplexity
  grounds interview-technique and recruiting-channel norms, OpenAI
  structures that plus everything already known (ICP, synthesis,
  secondary research) via `extra_context`.
- **Validation** (Phase 6): the first phase that reasons over REAL primary
  data instead of research — the founder's own notes from customer-
  discovery interviews (ideally conducted using Phase 5's guide). Holds
  those notes up against Phase 1's hypotheses and Phase 5's (or Phase 1's)
  success criteria and gives a direct verdict per hypothesis, whether the
  success criteria were actually met (counted exactly, no rounding up),
  notable patterns, and red flags — deliberately skeptical of noncommittal
  "that sounds useful" answers that aren't real validating signal. No
  search, no invented evidence — pure OpenAI structured reasoning over the
  founder's notes, like the Phase 3 synthesizer.
- **GTM Recommendation** (Phase 7, final phase): turns everything learned
  in Phases 1-6 into ONE concrete go-to-market plan rather than a menu of
  options — a primary motion (not a hedge across several), a positioning
  statement and messaging pillars, 2-4 specific named channels each with
  first actions, pricing/packaging, an ordered launch sequence, concrete
  metrics to track, and key risks. Same two-step pattern as ICP/Customer
  Discovery: Perplexity grounds channel-effectiveness, pricing, and
  launch-playbook norms for the category, OpenAI structures that plus
  everything already known — critically, Phase 6's validation results
  (real interview evidence) if they exist, since that's the strongest
  signal in the whole pipeline and outweighs assumption-based context from
  earlier phases. If validation hasn't been run yet, the plan is
  explicitly scoped down to a narrower validation-first motion instead of
  a full launch plan.

All 7 phases of the workflow are now built.

## Folder structure

```
market-discovery-agent/
├── README.md
├── requirements.txt
├── .gitignore
└── market_discovery_agent/
    ├── agent.py           # CLI entrypoint
    ├── models.py          # dataclasses for every phase's input/output
    ├── state.py           # local JSON session persistence (internal pipeline state)
    ├── lead.py            # owns the output/ convention — every agent writes through this
    ├── llm_utils.py        # shared OpenAI/Perplexity client creation + strict-schema conversion
    ├── synthesizer.py      # Phase 3 — Research Synthesizer
    ├── icp_discovery.py    # Phase 4 — ICP Discovery
    ├── market_sizing.py    # Phase 4b — Market Sizing (TAM / SAM / SOM)
    ├── customer_discovery.py # Phase 5 — Customer Discovery
    ├── validation.py       # Phase 6 — Validation (real interview notes)
    ├── gtm.py              # Phase 7 — GTM Recommendation (final phase)
    ├── research_agents/   # one module per secondary-research agent (industry_agent.py, ...)
    │                      # + _base.py, the shared Perplexity+OpenAI execution engine
    ├── sessions/          # created automatically — one JSON file per idea (pipeline state)
    └── output/            # created automatically — human/machine-readable deliverables
        ├── business-understanding/<session_id>.md + .json
        ├── research-plan/<session_id>.md + .json
        ├── industry-research/<session_id>.md + .json
        └── <agent-slug>/<session_id>.md + .json   # one subfolder per agent, see lead.py
```

## Output convention

**Rule: every phase/agent's deliverable lives under `output/<agent-slug>/`, never loose at the top level, and always as a matching `.md` + `.json` pair named after the session ID.**

This is enforced in one place — `lead.py` — not duplicated per command. `lead.py`:
- owns `AGENT_SLUGS`, the canonical folder name for each phase/agent (add new agents here)
- exposes `save_output(agent_name, session_id, title, markdown_body, data)` — call this at the end of any command/agent that produces a deliverable
- provides shared markdown renderers (`render_business_understanding_md`, `render_research_plan_md`, `render_research_findings_md`) so reports look consistent across agents

`sessions/<session_id>.json` is separate — it's internal pipeline state each phase reads from, untouched by `lead.py`. `output/` is the readable copy for humans (or downstream tooling) to open one agent's work at a time, e.g. `output/industry-research/<session_id>.md`.

When building a new secondary-research agent, don't write its own output-saving logic — register its slug in `lead.AGENT_SLUGS`, reuse `render_research_findings_md` if its output shape matches `IndustryResearchOutput` (subject name + findings + summary + opportunity signal), and call `lead.save_output(...)` at the end of its `cmd_*` handler in `agent.py`.

## Providers

The core pipeline runs on **OpenAI + Perplexity — no Anthropic** (it can
be reintroduced later as an alternative if needed, but nothing in the
codebase depends on it today). Two kinds of calls happen, split by what
each provider is actually built for:

- **Perplexity (search)** — the actual web-grounded research for all 7
  landscape secondary-research agents plus the Competitor Agent. `sonar-pro`
  grounds every completion in live search results, with citations returned
  alongside the answer.
- **OpenAI (structuring)** — everything that needs to record structured
  output, whether or not search was involved: the 7 agents' findings
  (after Perplexity researches them), and the no-search reasoning steps
  (`discover`, `plan`, `synthesize`) that only need to structure text
  already in hand. Uses OpenAI's Structured Outputs (`strict` json_schema
  mode), which is grammar-constrained at decode time — the output is
  guaranteed schema-valid, so no malformed-output retry loop is needed
  anywhere in the pipeline.

**Source credibility filtering.** Perplexity returns citations for
whatever it searched, with no guarantee those are reputable — a random
blog and a Crunchbase citation come back looking identical. Before the
structuring step sees them, `research_agents/_base.py`'s
`_classify_source_tier` tags every citation's domain into a tier (a static
lookup, not an LLM judgment call — deterministic and free, at the cost of
not covering niche/new domains, which fall through to Tier 3 by default):

- **Tier 1** — verified reference/data platforms (G2, Capterra, Crunchbase,
  PitchBook, Glassdoor, LinkedIn, BuiltWith, ...), government sources, major
  analyst firms (Gartner, Forrester, McKinsey, CB Insights).
- **Tier 2** — reputable trade press/established media (TechCrunch,
  Bloomberg, Reuters, WSJ, Wikipedia, ...).
- **Tier 3** — everything else: blogs, forums, or unrecognized domains.

`STRUCTURING_SYSTEM_PROMPT` instructs OpenAI to weight each finding's
`confidence` by tier, not just by how confident the research text sounds —
a finding resting only on Tier 3 sources gets capped at "Medium" (or "Low"
for quantitative/high-stakes claims), and Tier 1/2 evidence wins when
sources disagree. This applies to all 7 secondary-research agents, ICP
Discovery, and the Competitor Agent's Perplexity step; the Competitor
Agent's Apify/Exa context (see below) is tagged the same way, with Apify's
LinkedIn scrape always Tier 1 and the competitor's own website labeled
first-party (authoritative for their own claims, not for independent
criticism) rather than falling through to Tier 3.

Both call shapes are centralized in `llm_utils.py` (client creation +
strict-schema conversion), shared by `agent.py` directly (for
discover/plan/synthesize) and by `research_agents/_base.py` (for the
search pipeline).

The **Competitor Agent** additionally uses two enrichment providers, both
best-effort (skipped with a printed notice, not a hard failure, if the key
is missing or the call fails):

- **Apify (`get_apify_client`)** — runs a hosted actor
  (`automation-lab/linkedin-company-scraper` by default, override with
  `APIFY_LINKEDIN_COMPANY_ACTOR`) that scrapes the competitor's public
  LinkedIn company page into structured fields — name, description,
  industry, employee count, website — without logging in. This becomes
  ground-truth context for OpenAI's structuring step and also steers the
  Perplexity search prompt (no need to re-identify a company already
  confirmed).
- **Exa (`get_exa_client`)** — fetches the actual readable text of the
  LinkedIn URL and, once known, the competitor's own website via
  `get_contents`, instead of relying on Perplexity's search snippets for
  pages we already have the URL for.

## Setup

```bash
cd market-discovery-agent
pip install -r requirements.txt
export OPENAI_API_KEY=sk-your-key-here              # structuring — every command that hits an LLM
export PERPLEXITY_API_KEY=pplx-your-key-here        # search step, all research agents
export EXA_API_KEY=your-exa-key-here                # optional — Competitor Agent page-content fetch
export APIFY_API_KEY=apify_api_your-key-here        # optional — Competitor Agent LinkedIn scrape
```

Optional — override either model, or the Apify actor:
```bash
export MARKET_DISCOVERY_STRUCTURE_MODEL=gpt-4o             # OpenAI structuring step (also used by discover/plan/synthesize)
export MARKET_DISCOVERY_SEARCH_MODEL=sonar-pro              # Perplexity search step
export APIFY_LINKEDIN_COMPANY_ACTOR=automation-lab/linkedin-company-scraper  # Competitor Agent's LinkedIn scraper actor
```

## Usage

Run everything from inside `market_discovery_agent/`. Each phase is a
separate command so you can stop and pick back up later. Sessions are
saved as JSON under `market_discovery_agent/sessions/`.

```bash
cd market_discovery_agent

# 1. Collect your raw input (interactive prompts, no API call yet)
python agent.py init
# -> prints a session ID, e.g. 20260721-103948-ai-tool-that-helps-founders

# 2. Synthesize problem statement / hypotheses / success criteria
python agent.py discover --session 20260721-103948-ai-tool-that-helps-founders
# or just:
python agent.py discover --session latest

# 3. Build the research plan (tailored briefs for each secondary agent)
python agent.py plan --session latest

# 4. Run the secondary-research agents (any order; each reads its brief
#    from the research plan saved in step 3)
python agent.py industry --session latest
python agent.py community --session latest
python agent.py search-intent --session latest
python agent.py funding --session latest
python agent.py job-market --session latest
python agent.py social-intelligence --session latest

# Competitor Agent is per-competitor — prompts interactively for public
# LinkedIn company-page URLs (one per line, blank line to finish)
python agent.py competitor --session latest

# 5. Synthesize whatever secondary research you've run into one opportunity
#    score + go/no-go recommendation (works with a partial set of agents too)
python agent.py synthesize --session latest

# 6. Discover the Ideal Customer Profile — grounds buyer/segment norms via
#    Perplexity, combines with everything known from steps 2-5
python agent.py icp --session latest

# 6b. Size TAM / SAM / SOM — run after `icp` so SAM is narrowed by real
#     firmographic/technographic filters, not a generic percentage
python agent.py market-sizing --session latest

# 7. Build a customer discovery plan — interview guide, recruiting
#    channels, outreach template, success criteria
python agent.py customer-discovery --session latest

# 8. Validate against REAL customer-discovery interviews you conducted —
#    prompts you to enter interview notes, then checks them against your
#    hypotheses and success criteria
python agent.py validate --session latest

# 9. Build the GTM recommendation — motion, positioning, channel mix,
#    pricing/packaging, launch sequence, and metrics to track
python agent.py gtm --session latest
```

## Why it's structured this way

- **One JSON session per idea, not an in-memory pipeline.** You can run
  `init` today and `discover` tomorrow without losing anything.
- **Structured output, not free-text parsing.** `discover` and `plan` use
  OpenAI's Structured Outputs to force a response matching a defined JSON
  schema, so the output is always parseable — no regex-scraping a
  paragraph for a problem statement.
- **The planner doesn't run research — it plans it.** Keeping planning
  and execution as separate phases means you can review and edit the
  brief before burning API calls (or real work) on 7 research agents.

## Status

All 7 phases of the workflow (Business Understanding through GTM
Recommendation) are built.
