# Quick Start Guide - AI GTM Content System

Get your first LinkedIn post created in 5 minutes.

## Installation (One-Time Setup)

```bash
# 1. Clone or download the system files
cd ~/Downloads/ai-gtm-content-system

# 2. Run installation
chmod +x install.sh
./install.sh

# 3. Verify
# Open Claude Code and run: /agents
# You should see 4 content agents listed
```

## Your First LinkedIn Post

### Option 1: Use the Full Pipeline (Recommended)

Open Claude Code and run:

```
/content-pipeline "multi-agent collaboration in production"
```

The system will:
1. Ask a few clarifying questions
2. Research the topic (30 seconds)
3. Draft the post (20 seconds)  
4. Review quality (15 seconds)
5. Optimize (10 seconds)
6. Deliver final post (~75 seconds total)

### Option 2: Step-by-Step Manual Control

#### Step 1: Research
```
Use the content-researcher subagent to explore:
"How multi-agent systems improve content quality"
```

**Wait for research output** (key insights, examples, hooks)

#### Step 2: Write
```
Use the content-writer subagent to draft a post using these insights:

[Paste the research output here]

Keep it under 300 words for LinkedIn.
```

**Wait for draft**

#### Step 3: Quality Check
```
Use the content-qa subagent to review:

[Paste the draft here]
```

**If QA says "NEEDS REVISION":**
- Read the feedback
- Use the writer agent again with corrections
- Re-run QA

**If QA says "APPROVED":**
- Proceed to optimization

#### Step 4: Polish
```
Use the content-optimizer subagent to polish:

[Paste QA-approved draft]

Focus on QA suggestions:
[Paste relevant QA feedback]
```

**Final post delivered!**

## Example: Complete Workflow

```
You: /content-pipeline "Why subagents prevent context bloat"

Claude Code: 
Perfect! Creating a LinkedIn post about subagent context management 
for AI GTM Engineering audience.

A few quick questions:
1. Target length: Short (150 words) or Standard (250-300 words)?
2. Technical depth: High (for engineers) or Medium (for PMs/leaders)?

You: Standard length, medium technical depth

Claude Code:
Got it. Running the content pipeline...

═══ Phase 1/4: Research ═══
[Invokes content-researcher subagent]

Research complete! Found compelling angle:
→ Main Insight: Subagents isolate exploration from execution
→ Key Example: 200k token research → 300 token summary
→ Hook Ideas: 3 options identified

═══ Phase 2/4: Writing ═══
[Invokes content-writer subagent]

Draft complete!
→ 287 words (1,432 characters)
→ Hook: "Your AI agent's context window is bleeding tokens..."
→ Structure: Problem → Solution → Example → Takeaway

═══ Phase 3/4: Quality Review ═══
[Invokes content-qa subagent]

QA Verdict: APPROVED ✓
→ Engagement potential: HIGH
→ Hook strength: 9/10
→ Minor polish needed: 2 sentences could be tighter

═══ Phase 4/4: Optimization ═══
[Invokes content-optimizer subagent]

Optimization complete!
→ Final: 274 words (1,398 characters)
→ Readability: avg 17 words/sentence
→ Read time: 38 seconds

✅ FINAL LINKEDIN POST
═════════════════════

Your AI agent's context window is bleeding tokens.

Every web search. Every file it scans. Every exploratory step.
All of it piling up in one conversation until you hit the limit.

This is why production workflows feel fragile.

Subagents solve this elegantly.

Instead of one agent drowning in context, you run specialized 
subagents—each with their own isolated context window.

Here's what changes:

• Research agent explores 50 files → returns 3 key insights
• Main agent receives 300 tokens, not 200k
• Context stays clean for the actual implementation

Real example from our pipeline:
A content research agent processed 15 competitor posts, 
generated 3 pages of analysis, and returned a 4-sentence 
brief to the writing agent.

The writing agent never saw the raw research.
It received exactly what it needed.

This isn't just about saving tokens.
It's about task clarity.

When each agent has one job and its own workspace, the whole 
system becomes more reliable.

Your prompts get simpler.
Your results get more consistent.
Your context window stays healthy.

The best part? You're not building a complex system.
You're just being intentional about who does what.

One focused agent → one clean context → better output.

#AIEngineering #ProductionAI #AgenticWorkflows

═════════════════════
Character count: 1,398
Read time: 38 seconds
Ready to publish! 🚀
```

## Common Use Cases

### Case 1: Weekly Content Creation

```
/content-pipeline "This week's learning about [topic]"
```

### Case 2: Announce a Feature

```
/content-pipeline "Launching multi-subagent support in our product"
```

### Case 3: Share Insights

```
/content-pipeline "3 things I learned debugging agent teams"
```

### Case 4: Technical Deep Dive

```
/content-pipeline "How we reduced context bloat by 85% with subagents"

[In follow-up] Make this more technical, include code examples
```

## Pro Tips

### 1. Better Topics = Better Posts

✅ **Good**: "Why multi-agent systems beat single agents for production"
✅ **Good**: "The hidden cost of context window bloat"
❌ **Too broad**: "AI agents"
❌ **Too narrow**: "Bug fix in line 47"

### 2. Guide the Research

```
/content-pipeline "Agent collaboration patterns"

Focus research on:
- Real production examples
- Performance comparisons
- Common pitfalls
```

### 3. Iterate on QA Feedback

If QA says "NEEDS REVISION":
- Don't ignore the feedback
- The issues are real
- Fix them before optimizing

### 4. Save Your Best Posts

Create a learning library:
```bash
# After a great post
echo "[date] Topic: [topic]" >> ~/claude-posts.log
echo "What worked: [key points]" >> ~/claude-posts.log
```

### 5. A/B Test Hooks

After final post:
```
Use the content-writer to generate 3 alternative hooks 
for this post. Keep everything else the same.
```

## Customization

### Change Subagent Behavior

```bash
# Edit any subagent
code ~/.claude/agents/content-researcher.md

# Changes take effect immediately (no restart)
```

### Adjust Pipeline Steps

```bash
# Modify orchestrator
code ~/.claude/commands/content-pipeline.md
```

### Create Specialized Variants

```bash
# Create short-form version
cp ~/.claude/commands/content-pipeline.md \
   ~/.claude/commands/content-pipeline-short.md

# Then edit to change length targets
```

## Troubleshooting

### "Subagent not found"

```bash
# Reinstall
cd ~/Downloads/ai-gtm-content-system
./install.sh
```

### "QA keeps rejecting"

1. Read the QA feedback carefully
2. Adjust your topic to be more specific
3. Include examples in your initial prompt

### "Posts feel generic"

Add constraints to the pipeline:
```
/content-pipeline "topic"

Requirements:
- Include specific metric/number
- Reference a real example from our product
- End with actionable takeaway
```

## Next Steps

1. **Create 3 posts** - Get comfortable with the workflow
2. **Review QA feedback patterns** - Learn what makes posts better
3. **Customize subagents** - Tune for your style and audience
4. **Build variations** - Create specialized pipelines

## Resources

- **Full documentation**: `README.md`
- **Subagent files**: `~/.claude/agents/`
- **Orchestrator**: `~/.claude/commands/content-pipeline.md`
- **Claude Code docs**: https://docs.claude.com/en/docs/claude-code/overview

---

Ready to create better LinkedIn content? Run `/content-pipeline` and start building! 🚀
