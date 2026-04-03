
# 📚 Prompt Library v2 — Copy-Paste Commands

> All prompts for use inside a Claude Code session.
> Replace [BRACKETS] with your specifics.
> Start Claude Code from inside the `marketing-agent-team/` directory.

---

## 🚀 Orchestrator Prompts

### Full Campaign (all teams)
```
Use marketing-orchestrator to run a full content campaign.
Brief: pipeline/00-campaign-brief.md
Run all teams in sequence: Strategy → Research → Content → Quality → Analytics → Calendar
Pause for my approval after Research Team before continuing to Content.
```

### Full Campaign (no pauses)
```
Use marketing-orchestrator to run a full campaign from pipeline/00-campaign-brief.md.
Run all teams end-to-end. Notify me only if QA fails or human review is needed.
```

### Express LinkedIn (fast)
```
Use marketing-orchestrator for an express LinkedIn campaign on [TOPIC].
Run: audience-analyst + social-listener → linkedin-writer → qa-agent + brand-voice-checker → content-calendar-planner
Skip market-researcher, email, and blog agents.
```

---

## 🧭 Strategy Prompts

### Content Strategy Plan
```
Use content-strategist to build a strategy plan for pipeline/00-campaign-brief.md.
Read pipeline/12-campaign-learnings.md if it has entries.
Output: which content to create, which angle to own, distribution plan.
Save to pipeline/00b-content-strategy.md
```

### Pillar Content Audit
```
Use content-strategist to audit our current content pillar coverage.
Context: [paste a list of recent posts/topics]
Output: which pillars are underserved, what to create next, which funnel stage is weak.
```

---

## 🔍 Research Prompts

### Full Research Suite
```
Use market-researcher, audience-analyst, and social-listener to research [TOPIC].
Target ICP: [ICP description]
Save outputs to pipeline/01, 02, 03.
```

### Competitive Intelligence Only
```
Use market-researcher to research competitor activity on [TOPIC].
Focus on: what are they saying, what angles they're using, what they're missing.
Save to pipeline/01-market-research.md
```

### ICP Language Mining
```
Use audience-analyst to map pain points and exact language for [ROLE] at [COMPANY TYPE].
Context from: pipeline/01-market-research.md (if available)
Focus on: the words they actually use, their fears, their buying triggers.
Save to pipeline/02-audience-insights.md
```

### LinkedIn Format Intelligence
```
Use social-listener to find what content formats are performing for [TOPIC] on LinkedIn right now.
Output: top formats, best hook patterns, topic saturation level, gaps to fill.
Save to pipeline/03-social-signals.md
```

---

## ✍️ Content Prompts

### LinkedIn Posts (with research)
```
Use linkedin-writer to write 3 LinkedIn post variants on [TOPIC].
Read: pipeline/01-market-research.md, pipeline/02-audience-insights.md, pipeline/03-social-signals.md
Goal: [awareness / engagement / lead gen]
CTA: [specific CTA]
Save to pipeline/04-linkedin-draft.md
```

### LinkedIn Post (fast, no research)
```
Use linkedin-writer to write a [FORMAT] LinkedIn post about [TOPIC].
Format: [list / story / contrarian / data-led / short insight]
Target ICP: [description]
CTA: [CTA]
Save to pipeline/04-linkedin-draft.md
```

### LinkedIn Post — Revision
```
Use linkedin-writer to revise pipeline/04-linkedin-draft.md.
QA issues to fix: pipeline/07-qa-report.md
Brand issues to fix: pipeline/09-brand-check.md
Fix ONLY the flagged sections. Do not rewrite passing sections.
Log all changes at the bottom of the file.
```

### Cold Email Sequence (3 emails)
```
Use email-writer to write a 3-email cold outreach sequence.
Target: [ROLE] at [COMPANY TYPE]
Goal: [e.g., book a 20-min discovery call]
Value prop: [one sentence]
Read audience context from: pipeline/02-audience-insights.md
Save to pipeline/05-email-draft.md
```

### Nurture Email Sequence (5 emails)
```
Use email-writer to write a 5-email nurture sequence for [STAGE] leads.
Content pillars to cover: [list 3–5 topics — one per email]
Final email CTA: [specific CTA]
Read context from: pipeline/02-audience-insights.md
Save to pipeline/05-email-draft.md
```

### Blog Post
```
Use blog-writer to write a [WORD COUNT]-word blog post.
Target keyword: [keyword]
Search intent: [informational / commercial / transactional]
Target reader: [ICP description]
Angle: [specific angle from content strategy or your own]
Read research from: pipeline/01-market-research.md, pipeline/02-audience-insights.md
Save to pipeline/06-blog-draft.md
```

### Blog Post — Revision
```
Use blog-writer to revise pipeline/06-blog-draft.md.
QA issues: pipeline/07-qa-report.md
SEO issues: pipeline/08-seo-report.md
Fix ONLY the flagged items. Log changes at bottom of file.
```

---

## 🧪 Quality Prompts

### Full Quality Pass (all three agents)
```
Use qa-agent, brand-voice-checker, and seo-optimizer to review all content.
Files to review: pipeline/04-linkedin-draft.md, pipeline/05-email-draft.md, pipeline/06-blog-draft.md
Save reports to pipeline/07, 08, 09.
```

### QA Only (no SEO, no brand)
```
Use qa-agent to review [pipeline/04 / pipeline/05 / pipeline/06].
Check: grammar, clarity, factual accuracy, structural completeness, CTA presence.
Save to pipeline/07-qa-report.md
```

### Brand Voice Audit
```
Use brand-voice-checker to audit pipeline/04-linkedin-draft.md and pipeline/05-email-draft.md.
Cross-check against docs/brand-voice-guide.md.
Flag all off-brand language with specific rewrite suggestions.
Save to pipeline/09-brand-check.md
```

### SEO Optimization
```
Use seo-optimizer to optimize pipeline/06-blog-draft.md.
Primary keyword: [keyword]
Check for: 2025 SEO signals, AI Overview optimization, E-E-A-T, schema opportunities.
Save to pipeline/08-seo-report.md
```

---

## 📊 Analytics Prompts

### Post-Campaign Analysis
```
Use performance-analyst to analyze content performance.
Campaign: [campaign name]
Performance data:
[PASTE YOUR DATA HERE — LinkedIn metrics, email stats, blog analytics]
Read campaign context from: pipeline/00-campaign-brief.md
Save to pipeline/10-performance-report.md
```

### A/B Test Design
```
Use ab-test-designer to design A/B tests for pipeline/04 and pipeline/05.
Priority: email subject lines first, LinkedIn hooks second, CTAs third.
Read performance patterns from: pipeline/10-performance-report.md (if available)
Save to pipeline/11-ab-variants.md
```

### Post-Campaign Full Loop
```
Use performance-analyst to analyze this data: [PASTE DATA]
Then use ab-test-designer to design tests for the next campaign.
Then update pipeline/12-campaign-learnings.md with key findings.
```

---

## 🗓️ Calendar Prompts

### Build Publish Calendar
```
Use content-calendar-planner to build a publishing schedule for this campaign.
Approved content: [list which files passed QA]
Calendar window: [start date] to [end date]
Channels: LinkedIn + Email [+ Blog if applicable]
Save to pipeline/13-content-calendar.md
```

### Express Calendar (LinkedIn only)
```
Use content-calendar-planner to schedule pipeline/04-linkedin-draft.md.
2-week window starting [date].
Include: post dates/times, variant sequence, A/B test instructions, engagement protocol.
Save to pipeline/13-content-calendar.md
```

---

## 🔄 Advanced Workflow Prompts

### Full Campaign with Learnings Integration
```
Use marketing-orchestrator to run a campaign.
Brief: pipeline/00-campaign-brief.md
IMPORTANT: Read pipeline/12-campaign-learnings.md first.
Apply any "do not repeat" patterns and double down on proven playbooks.
Run full sequence. Update learnings file on completion.
```

### Content Repurposing
```
Use linkedin-writer and email-writer to repurpose pipeline/06-blog-draft.md.
LinkedIn: extract 2 angles from the post, write as standalone posts (not just teasers)
Email: write 1 nurture email that educates on the topic + links to full post
Then run qa-agent + brand-voice-checker on both new outputs.
```

### Quarterly Pillar Audit
```
Use content-strategist to audit our content pillar balance.
Past content (last 90 days): [paste titles or topics]
Output: which pillars are over/under-served, which funnel stages are weak,
which topics have worked, which to avoid. Recommend Q[X] content priorities.
```

### Competitor Response Post
```
Use market-researcher to analyze: [competitor content URL or paste content]
Then use linkedin-writer to write our differentiated POV on the same topic.
Rules: do NOT mention the competitor by name. Lead with our angle, not theirs.
Run qa-agent + brand-voice-checker before finalizing.
```
