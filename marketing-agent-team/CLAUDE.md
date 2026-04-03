# 🎯 MARKETING AGENT TEAM — System Configuration

> Built on Claude Code Agent Teams  
> Architecture: 1 Orchestrator → 5 Layers → 13 Specialized Agents  
> Requires: Claude Code v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## 🏗️ Agent Team Architecture

```
MARKETING ORCHESTRATOR (Lead Agent — entry point for all multi-agent runs)
│
├── 🧭 STRATEGY LAYER (run first on full campaigns)
│   └── content-strategist       → topic/angle/funnel/format decisions
│
├── 🔍 RESEARCH TEAM (run second)
│   ├── market-researcher        → trends, competitor signals, data
│   ├── audience-analyst         → ICP insights, pain points, exact language
│   └── social-listener          → what's performing in the LinkedIn feed
│
├── ✍️ CONTENT TEAM (run third)
│   ├── linkedin-writer          → LinkedIn posts (2–3 variants)
│   ├── email-writer             → cold outreach / nurture sequences
│   └── blog-writer              → long-form SEO content
│
├── 🧪 QUALITY TEAM (run fourth — has revision loop back to Content)
│   ├── qa-agent                 → grammar, clarity, accuracy, structure
│   ├── seo-optimizer            → keywords, meta, E-E-A-T (blog only)
│   └── brand-voice-checker      → tone consistency across all channels
│
└── 📊 ANALYTICS + PLANNING (run post-quality or post-publish)
    ├── performance-analyst      → what content is working and why
    ├── ab-test-designer         → headline/CTA/hook variants
    └── content-calendar-planner → publish schedule with dates/times/actions
```

---

## 📁 Pipeline File Map

```
pipeline/
├── 00-campaign-brief.md       ← YOU fill this in first (always)
├── 00b-content-strategy.md    ← content-strategist writes here
├── 01-market-research.md      ← market-researcher writes here
├── 02-audience-insights.md    ← audience-analyst writes here
├── 03-social-signals.md       ← social-listener writes here
├── 04-linkedin-draft.md       ← linkedin-writer writes here
├── 05-email-draft.md          ← email-writer writes here
├── 06-blog-draft.md           ← blog-writer writes here
├── 07-qa-report.md            ← qa-agent writes here
├── 08-seo-report.md           ← seo-optimizer writes here
├── 09-brand-check.md          ← brand-voice-checker writes here
├── 10-performance-report.md   ← performance-analyst writes here
├── 11-ab-variants.md          ← ab-test-designer writes here
├── 12-campaign-learnings.md   ← orchestrator updates after every run ← NEVER DELETE
└── 13-content-calendar.md     ← content-calendar-planner writes here
```

---

## 🔄 Standard Workflows

```
FULL CAMPAIGN:
  1. Fill pipeline/00-campaign-brief.md
  2. content-strategist    → pipeline/00b-content-strategy.md
  3. Research Team         → pipeline/01, 02, 03
  4. Content Team          → pipeline/04, 05, 06
  5. Quality Team          → pipeline/07, 08, 09
     └── [revision loop if QA fails → back to Content → re-run QA]
  6. Analytics Team        → pipeline/11 (ab-test-designer)
  7. content-calendar-planner → pipeline/13
  8. Publish per calendar
  9. Post-publish: performance-analyst → pipeline/10
 10. Orchestrator updates  → pipeline/12-campaign-learnings.md

EXPRESS (LinkedIn only):
  Fill brief → audience-analyst + social-listener
  → linkedin-writer → qa-agent + brand-voice-checker
  → content-calendar-planner

POST-CAMPAIGN (analytics loop):
  Paste performance data into brief → performance-analyst
  → ab-test-designer → update pipeline/12
```

---

## ⚙️ Setup

### Enable Agent Teams
Add to `~/.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Install Agents
```bash
cp -r .claude/agents/* ~/.claude/agents/
claude --version  # must be v2.1.32+
```

---

## 🧠 Shared Context — Fill These In

> All agents read this section. The more specific you are, the better every output.
> Detailed brand voice lives in `docs/brand-voice-guide.md` — update that file first.

### Brand Voice (Summary)
- **Tone**: [Your tone — e.g., Conversational, confident, practitioner-first]
- **Style**: [Your style — e.g., Short sentences. Real examples. No fluff.]
- **Avoid**: [What you never say — e.g., Jargon, passive voice, corporate speak]
- **Full guide**: See `docs/brand-voice-guide.md`

### Ideal Customer Profile (ICP)
- **Primary**: [e.g., B2B SaaS Founders, 30–100 employees, Series A/B]
- **Secondary**: [e.g., Marketing Leaders at SMBs scaling content ops]
- **Core pain**: [e.g., No time to create content, inconsistent brand voice]
- **Core goal**: [e.g., Thought leadership + pipeline from content]

### Content Pillars
1. [Pillar 1 — e.g., AI-powered marketing workflows]
2. [Pillar 2 — e.g., B2B content strategy & GTM]
3. [Pillar 3 — e.g., Founder brand building on LinkedIn]
4. [Pillar 4 — e.g., Marketing automation & efficiency]

### Product / Offer
- **Product name**: [Your product name]
- **One-line description**: [What it does]
- **Primary CTA**: [e.g., Book a free strategy call / Start free trial / Download playbook]
- **CTA URL**: [URL]

---

## ⚠️ System-Wide Rules

1. **File ownership**: Each agent owns its pipeline file(s) — no agent overwrites another's output
2. **Read before write**: Always read the brief + all upstream pipeline files before generating
3. **Revision loop**: If QA fails → content agent fixes flagged items only → QA re-runs → max 2 cycles before human escalation
4. **Quality gate**: Nothing gets scheduled until qa-agent (07) + brand-voice-checker (09) both PASS
5. **Memory**: `pipeline/12-campaign-learnings.md` is updated after every run — never delete it
6. **Token awareness**: Run teams sequentially on tight budgets — Research Team alone = 8K–15K tokens

---

## 📊 Token Cost Reference

| Workflow | Agents Active | Est. Tokens |
|---|---|---|
| Full campaign (all 13 agents) | All | 50,000–100,000 |
| Express LinkedIn | 5 agents | 8,000–18,000 |
| Research only | 3 agents | 8,000–15,000 |
| Content only | 3 agents | 10,000–22,000 |
| Quality pass | 3 agents | 6,000–12,000 |
| Single post (fast) | 2 agents | 3,000–6,000 |
| Post-campaign analytics | 2 agents | 4,000–8,000 |

> 💡 Start with the Express workflow. Run full campaigns once you're comfortable with the system.
