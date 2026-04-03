# 🎯 Marketing Agent Team for Claude Code — v2

> **Architecture**: 1 Orchestrator → 5 Layers → 13 Specialized Agents  
> **Requires**: Claude Code v2.1.32+ · Agent Teams enabled  
> **Start here**: `docs/quick-start.md`

---

## What This Is

A complete multi-agent marketing system built on Claude Code Agent Teams.

13 specialist agents work in coordinated sequence — each doing one job, handing off to the next, with quality gates, revision loops, and campaign memory that compounds across every run.

Built on the Day 14 foundation (linkedin-writer + qa-agent), expanded into a full production-grade marketing stack.

---

## File Structure

```
marketing-agent-team/
│
├── CLAUDE.md                          ← System config (read by all agents) — CUSTOMISE THIS
│
├── .claude/agents/                    ← All 13 agent definitions
│   ├── marketing-orchestrator.md      ← Lead agent (entry point)
│   │
│   ├── content-strategist.md          ← Strategy Layer
│   │
│   ├── market-researcher.md           ← Research Team
│   ├── audience-analyst.md
│   ├── social-listener.md
│   │
│   ├── linkedin-writer.md             ← Content Team
│   ├── email-writer.md
│   ├── blog-writer.md
│   │
│   ├── qa-agent.md                    ← Quality Team
│   ├── seo-optimizer.md
│   ├── brand-voice-checker.md
│   │
│   ├── performance-analyst.md         ← Analytics + Planning
│   ├── ab-test-designer.md
│   └── content-calendar-planner.md
│
├── pipeline/                          ← All agent outputs flow here
│   ├── 00-campaign-brief.md           ← YOU fill this in first
│   ├── 00b-content-strategy.md        ← content-strategist output
│   ├── 01-market-research.md          ← market-researcher output
│   ├── 02-audience-insights.md        ← audience-analyst output
│   ├── 03-social-signals.md           ← social-listener output
│   ├── 04-linkedin-draft.md           ← linkedin-writer output
│   ├── 05-email-draft.md              ← email-writer output
│   ├── 06-blog-draft.md               ← blog-writer output
│   ├── 07-qa-report.md                ← qa-agent output
│   ├── 08-seo-report.md               ← seo-optimizer output
│   ├── 09-brand-check.md              ← brand-voice-checker output
│   ├── 10-performance-report.md       ← performance-analyst output
│   ├── 11-ab-variants.md              ← ab-test-designer output
│   ├── 12-campaign-learnings.md       ← Campaign memory — NEVER DELETE
│   └── 13-content-calendar.md         ← content-calendar-planner output
│
└── docs/
    ├── brand-voice-guide.md           ← CUSTOMISE THIS — your brand voice bible
    ├── quick-start.md                 ← Setup and first run guide
    ├── agent-reference.md             ← Full agent capability reference
    └── prompt-library.md              ← Copy-paste prompts for every use case
```

---

## Quick Setup

```bash
# 1. Enable Agent Teams
echo '{"env":{"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"}}' > ~/.claude/settings.json

# 2. Install agents
cp -r .claude/agents/* ~/.claude/agents/

# 3. Customise brand voice
# Edit docs/brand-voice-guide.md and CLAUDE.md

# 4. Fill in your brief
# Edit pipeline/00-campaign-brief.md

# 5. Run
cd marketing-agent-team/
claude
```

Then in the session:
```
Use marketing-orchestrator for an express LinkedIn campaign from pipeline/00-campaign-brief.md.
Run: audience-analyst + social-listener → linkedin-writer → qa-agent + brand-voice-checker → content-calendar-planner
```

---

## What's New in v2

| Feature | v1 | v2 |
|---|---|---|
| Agents | 11 | 13 |
| Strategy layer | ❌ | ✅ content-strategist |
| Campaign memory | ❌ | ✅ pipeline/12-campaign-learnings.md |
| Revision loops | ❌ | ✅ QA fail → fix → re-review |
| Publish scheduling | ❌ | ✅ content-calendar-planner |
| Brand voice guide | Generic placeholder | ✅ Dedicated docs/brand-voice-guide.md |
| Agent descriptions | Long narrative | ✅ Short, trigger-keyword-dense |
| SEO signals | 2022 standards | ✅ 2025: AI Overviews, E-E-A-T, schema |
| Forward routing | ❌ | ✅ Each quality agent routes to next step |
| Fallback logic | ❌ | ✅ All research agents have search fallbacks |

---

## Token Cost Reference

| Workflow | Agents | Est. Tokens |
|---|---|---|
| Full campaign | All 13 | 50,000–100,000 |
| Express LinkedIn | 5 agents | 8,000–18,000 |
| Research only | 3 agents | 8,000–15,000 |
| Quality pass | 3 agents | 6,000–12,000 |
| Analytics loop | 2 agents | 4,000–8,000 |

---

## Resources

- Claude Code docs: https://docs.anthropic.com/en/docs/claude-code
- Agent Teams feature: https://code.claude.com/docs/en/agent-teams
- Version check: `claude --version` (need 2.1.32+)
