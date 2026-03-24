# AI GTM Content System - Multi-Subagent LinkedIn Pipeline

A production-ready multi-subagent workflow for creating high-quality LinkedIn posts using Claude Code.

## Architecture Overview

```
Input: Topic → AI GTM Engineering
         ↓
    Main Agent (Orchestrator)
         ↓
┌────────────────────────────────────┐
│  Research Subagent                 │
│  → Explores ideas and insights     │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│  Writing Subagent                  │
│  → Drafts the LinkedIn post        │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│  Content QA Subagent               │
│  → Reviews clarity and structure   │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│  Optimization Subagent             │
│  → Improves readability and flow   │
└────────────────┬───────────────────┘
                 ↓
         Final LinkedIn Post
```

## What This System Does

✅ **Clear Separation of Concerns**: Each subagent has one focused responsibility
✅ **Quality Gates**: QA agent prevents bad content from advancing  
✅ **Context Isolation**: Each subagent works in its own context window
✅ **Sequential Workflow**: Structured pipeline ensures consistent quality
✅ **Production-Ready**: Built for real content creation, not demos

## Installation

### Prerequisites

- **Claude Code** installed and configured ([Install Guide](https://docs.claude.com/en/docs/claude-code/overview))
- **Node.js** 20+ required for Claude Code
- Active Claude subscription (Pro, Team, or Enterprise)

### Option 1: Automatic Installation (Recommended)

```bash
# Clone the repository
git clone <your-repo-url> ai-gtm-content-system
cd ai-gtm-content-system

# Run installation script
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

```bash
# 1. Create Claude Code directories if they don't exist
mkdir -p ~/.claude/agents
mkdir -p ~/.claude/commands

# 2. Copy subagent definitions
cp research-agent.md ~/.claude/agents/content-researcher.md
cp writer-agent.md ~/.claude/agents/content-writer.md
cp qa-agent.md ~/.claude/agents/content-qa.md
cp optimizer-agent.md ~/.claude/agents/content-optimizer.md

# 3. Copy orchestrator command
cp content-pipeline-command.md ~/.claude/commands/content-pipeline.md

# 4. Verify installation
ls ~/.claude/agents/    # Should show 4 agent files
ls ~/.claude/commands/  # Should show content-pipeline.md
```

### Verification

Open Claude Code and run:

```bash
/agents
```

You should see:
- `content-researcher`
- `content-writer`
- `content-qa`
- `content-optimizer`

## Usage

### Quick Start

In Claude Code, use the orchestrator command:

```
/content-pipeline "multi-subagent collaboration"
```

The system will:
1. Ask clarifying questions
2. Research the topic
3. Draft the post
4. Review quality
5. Optimize readability
6. Deliver final post

### Manual Subagent Invocation

You can also invoke subagents individually:

**Research Phase:**
```
Use the content-researcher subagent to explore: 
"How multi-agent systems improve content quality"
```

**Writing Phase:**
```
Use the content-writer subagent to draft a post about:
[paste research insights]
```

**QA Phase:**
```
Use the content-qa subagent to review:
[paste draft]
```

**Optimization Phase:**
```
Use the content-optimizer subagent to polish:
[paste QA-approved draft]
```

### Example Workflow

```
User: /content-pipeline "agentic workflows in production"

Claude Code:
→ Phase 1/4: Research
  [Invokes content-researcher]
  Research found: 3 key insights about production workflows
  
→ Phase 2/4: Writing
  [Invokes content-writer]
  Draft complete (312 words, 1,487 characters)
  
→ Phase 3/4: Quality Review
  [Invokes content-qa]
  QA Verdict: APPROVED (High engagement potential)
  
→ Phase 4/4: Optimization
  [Invokes content-optimizer]
  Final post: 287 words, 1,398 characters
  
✅ Final LinkedIn post ready for publication!
```

## Subagent Details

### 1. Research Subagent (`content-researcher`)

**Purpose**: Explore topics and gather insights

**Tools**: Read, Grep, Bash

**Model**: Sonnet

**Outputs**:
- Key angle for the topic
- 3-5 core insights
- Supporting examples
- Suggested hooks

### 2. Writing Subagent (`content-writer`)

**Purpose**: Draft engaging LinkedIn posts

**Tools**: Read, Write, Edit

**Model**: Sonnet

**Outputs**:
- Complete post draft
- Character count
- Hook alternatives
- Writing notes

### 3. QA Subagent (`content-qa`)

**Purpose**: Review clarity and structure

**Tools**: Read

**Model**: Sonnet

**Outputs**:
- QA verdict (Approved/Needs Revision/Rejected)
- Structural issues
- Clarity issues
- Specific fixes needed

### 4. Optimization Subagent (`content-optimizer`)

**Purpose**: Polish readability and flow

**Tools**: Read, Edit

**Model**: Sonnet

**Outputs**:
- Optimized final post
- Before/after samples
- Readability metrics

## Customization

### Modify Subagent Behavior

Edit the agent files in `~/.claude/agents/`:

```bash
# Open an agent for editing
code ~/.claude/agents/content-researcher.md
```

Key customization areas:
- **System prompt**: Adjust tone, focus areas, output format
- **Tools**: Add/remove tool access
- **Model**: Switch between Sonnet/Opus/Haiku

### Adjust Orchestrator

Edit the command file:

```bash
code ~/.claude/commands/content-pipeline.md
```

Customization options:
- Quality gate criteria
- Phase ordering
- Error handling
- Output format

### Create Variations

You can create specialized versions:

```bash
# Short-form content variant
cp content-pipeline.md ~/.claude/commands/content-pipeline-short.md

# Technical deep-dive variant  
cp content-pipeline.md ~/.claude/commands/content-pipeline-technical.md
```

## Advanced Usage

### Parallel Research (Experimental)

For complex topics, research multiple angles in parallel:

```
Research this topic from three angles in parallel:
1. Use content-researcher for technical perspective
2. Use content-researcher for business perspective  
3. Use content-researcher for user perspective

Then synthesize findings.
```

### Custom Quality Gates

Add stricter requirements in the orchestrator:

```markdown
**Gate 3 (After QA):**
- Engagement potential must be HIGH
- Character count under 1,200
- At least 2 specific examples
```

### A/B Testing

Generate multiple variations:

```
/content-pipeline "topic"
[Complete workflow]

Now use content-writer to create 2 alternative hooks 
for the final post.
```

## Best Practices

### 1. Topic Selection
✅ Specific over broad ("multi-agent content pipelines" vs "AI")
✅ Angle-rich topics work best
✅ Include context in your prompt

### 2. Quality Control
✅ Review QA feedback before proceeding
✅ Don't skip quality gates
✅ Iterate on "NEEDS REVISION" verdicts

### 3. Context Management
✅ Each subagent gets fresh context
✅ Main agent synthesizes results
✅ Don't overload subagent prompts

### 4. Production Use
✅ Test workflow with sample topics first
✅ Review final output before publishing
✅ Track what topics/angles perform best

## Troubleshooting

### Subagent Not Found

```bash
# Verify installation
ls ~/.claude/agents/

# Reinstall if needed
cp *-agent.md ~/.claude/agents/
```

### QA Keeps Rejecting

- Check if topic is too broad
- Ensure research phase provided specific insights
- Review QA feedback for patterns
- Try a different angle

### Character Count Too High

- Adjust writing subagent prompt for brevity
- Increase optimization focus on word economy
- Set explicit length target upfront

### Low Engagement Verdict

- Strengthen the hook in writing phase
- Add more specific examples
- Ensure clear takeaway

## Performance Tips

### Speed Optimization

- Use Sonnet for all subagents (fast, capable)
- Keep research focused (3 insights vs 10)
- Limit QA iteration cycles (max 2)

### Quality Optimization

- Use Opus for research on complex topics
- Add examples to subagent prompts
- Extend QA checklist for your use case

### Token Management

- Each subagent has isolated context
- Main agent only receives summaries
- Total tokens = sum of subagent outputs (minimal)

## System Architecture

### Why Multi-Subagent?

**Context Isolation**: Research exploration doesn't bloat writing context
**Specialization**: Each agent is expert in one domain
**Reproducibility**: Same pipeline, consistent quality
**Modularity**: Swap/upgrade individual agents

### Design Decisions

**Sequential not Parallel**: Quality gates require order
**QA as Gate-Keeper**: Prevents bad content from optimization
**Orchestrator Pattern**: Main agent coordinates, doesn't execute
**Tool Restrictions**: Each agent has minimal tool access needed

## Contributing

Improvements welcome! Key areas:

- New subagents for different content types
- Alternative quality metrics
- Performance optimizations
- Integration with publishing tools

## License

MIT License - Use freely in your content workflows

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Subagent Best Practices](https://code.claude.com/docs/en/sub-agents)
- [LinkedIn Content Guide](https://business.linkedin.com/marketing-solutions/blog/content-marketing/2024/best-practices-for-linkedin-posts)

## Support

Issues? Questions? Feedback?

- Open an issue on GitHub
- Review subagent logs in Claude Code
- Check the troubleshooting section above

---

**Built for Day 14 of AI GTM Engineering journey**

From concept to production-ready multi-agent collaboration system. 🚀
