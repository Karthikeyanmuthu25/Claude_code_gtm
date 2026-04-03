# ⚡ Quick Start Guide — v2

> Get your first campaign running in under 15 minutes.
> Read this top-to-bottom once. After that, use the prompt-library.md.

---

## Prerequisites

```bash
npm install -g @anthropic-ai/claude-code   # install Claude Code
claude --version                           # must be v2.1.32+
npm update -g @anthropic-ai/claude-code    # upgrade if older
```

Active Claude Pro or Max subscription required.

---

## Step 1 — Enable Agent Teams (2 min)

Open or create `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or add to your shell profile (`~/.bashrc` / `~/.zshrc`):
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## Step 2 — Install the Agents (1 min)

```bash
# From inside the marketing-agent-team/ directory:
cp -r .claude/agents/* ~/.claude/agents/

# Verify all 13 agents installed:
ls ~/.claude/agents/ | wc -l   # should show 13
ls ~/.claude/agents/
```

Expected agents:
```
ab-test-designer.md          marketing-orchestrator.md
audience-analyst.md          performance-analyst.md
blog-writer.md               qa-agent.md
brand-voice-checker.md       seo-optimizer.md
content-calendar-planner.md  social-listener.md
content-strategist.md
email-writer.md
linkedin-writer.md
market-researcher.md
```

---

## Step 3 — Customise Your Brand Voice (5 min — most important step)

Open `docs/brand-voice-guide.md` and fill in:
- **Brand identity** — who you are, your POV, your category
- **Voice dimensions** — rate your tone on each spectrum
- **On-brand examples** — real opening lines that sound like you
- **Banned phrases** — add your specific pet hates
- **Channel notes** — any differences between LinkedIn, email, blog

Then update `CLAUDE.md` — the summary Brand Voice and ICP sections.

> ⚠️ This is the single highest-value setup step. Every agent reads these files.
> Generic brand voice = generic output. Your specific voice = outputs that sound like you.

---

## Step 4 — Fill Your Campaign Brief (3 min)

Open `pipeline/00-campaign-brief.md` and fill in:
- Campaign topic (be specific — not "AI" but "how B2B teams use AI to cut content production time")
- Which deliverables you need (LinkedIn / email / blog — or just one)
- Target ICP segment
- Your CTA and CTA URL
- Success metrics

---

## Step 5 — Run Your First Campaign

```bash
# Start Claude Code from inside marketing-agent-team/ directory
cd marketing-agent-team/
claude
```

**Recommended first run — Express LinkedIn** (lowest token cost, fastest results):
```
Use marketing-orchestrator for an express LinkedIn campaign.
Brief: pipeline/00-campaign-brief.md
Run: audience-analyst + social-listener → linkedin-writer → qa-agent + brand-voice-checker → content-calendar-planner
```

**When you're comfortable — Full Campaign:**
```
Use marketing-orchestrator to run a full campaign from pipeline/00-campaign-brief.md.
Run all teams in sequence. Pause after Research Team for my review.
```

---

## Step 6 — After Your First Campaign

1. **Review outputs** in the `pipeline/` folder
2. **Publish** per the calendar in `pipeline/13-content-calendar.md`
3. **Track performance** for 7–14 days
4. **Run analytics loop**:
   ```
   Use performance-analyst to analyze this data: [paste your metrics]
   Then update pipeline/12-campaign-learnings.md with key findings.
   ```
5. Your second campaign will be smarter because of the learnings log.

---

## 🏁 First-Run Checklist

- [ ] Claude Code v2.1.32+ installed
- [ ] `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set
- [ ] All 13 agents in `~/.claude/agents/`
- [ ] `docs/brand-voice-guide.md` filled with YOUR brand voice
- [ ] `CLAUDE.md` — Brand Voice + ICP sections updated
- [ ] `pipeline/00-campaign-brief.md` filled in
- [ ] Claude Code started from inside `marketing-agent-team/` directory
- [ ] First campaign run complete
- [ ] Outputs reviewed in `pipeline/`

---

## 🚨 Troubleshooting

| Problem | Fix |
|---|---|
| "Agent not found" | Check agents are in `~/.claude/agents/` not a subdirectory |
| Agent not reading pipeline files | Start Claude Code from inside `marketing-agent-team/` directory |
| Out of context / truncated | Run one team at a time, not all 13 in parallel |
| Brand voice check failing everything | Update `docs/brand-voice-guide.md` with YOUR actual brand — don't leave placeholders |
| Agent Teams not working | Run `claude --version` — must be 2.1.32+. Run `npm update -g @anthropic-ai/claude-code` |
| QA stuck in revision loop | After 2 failed revision cycles, the orchestrator will flag for human review — read the QA report yourself and instruct the writer directly |
| Pipeline files not updating | Confirm you're in the correct working directory — agents write relative to where Claude Code was started |

---

## 💡 Pro Tips

**Token management**: Run teams sequentially. Research + Content + Quality = ~35K tokens minimum. Don't run all 13 in parallel unless you're on a high-usage plan.

**Campaign memory**: The `pipeline/12-campaign-learnings.md` file compounds over time. After 3–4 campaigns, the content-strategist will have real patterns to work with. Don't skip updating it.

**Brand voice first**: Spend 10 minutes on `docs/brand-voice-guide.md` before your first run. It's the difference between outputs that sound like you and outputs that sound like every other AI-written B2B content.

**Start narrow**: Use the express LinkedIn workflow for your first 2–3 campaigns. Add email, blog, and full orchestration once you're comfortable reviewing pipeline outputs.

**Iterate the brief**: The `00-campaign-brief.md` template has every field for a reason. The more specific your brief, the less revision loops you'll need.
