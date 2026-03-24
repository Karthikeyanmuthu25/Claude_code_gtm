# LinkedIn Content Agent - Multi-Subagent System

**Complete multi-agent collaboration system for creating high-quality LinkedIn posts**

Version: 1.0  
Date: March 2026  
Platform: Cursor IDE / Claude Code

---

## 📦 What's Inside This Package

This is a **production-ready multi-subagent content creation system** that transforms a topic into a polished LinkedIn post through 4 specialized AI agents working together.

### File Structure

```
LINKEDIN-CONTENT-AGENT/
├── .cursorrules/            ← Cursor agent rules (for @ mentions)
│   ├── researcher.mdc       
│   ├── writer.mdc
│   ├── qa.mdc
│   └── optimizer.mdc
│
├── pipeline/                ← Agent communication files
│   ├── 01-research-output.md
│   ├── 02-draft-output.md
│   ├── 03-qa-output.md
│   └── 04-final-output.md
│
├── Sub_agents/              ← Detailed agent instructions
│   ├── research-agent.md
│   ├── writer-agent.md
│   ├── qa-agent.md
│   └── optimizer-agent.md
│
├── ARCHITECTURE.md          ← System design deep-dive
├── CURSOR_ARCHITECTURE.md   ← Cursor-specific implementation
├── CURSOR_QUICK_REFERENCE.md ← Cheat sheet
├── EXAMPLES.md              ← Real output samples
├── QUICKSTART.md            ← Get started in 5 minutes
├── README.md                ← This file
├── content-pipeline-command.md ← Orchestrator logic
└── install.sh               ← Setup script
```

---

## 🚀 Quick Start

### For Cursor IDE (Recommended)

**Step 1: Extract & Navigate**
```bash
# Extract this package
unzip linkedin-content-agent.zip
cd LINKEDIN-CONTENT-AGENT

# Or if using tar.gz:
tar -xzf linkedin-content-agent.tar.gz
cd LINKEDIN-CONTENT-AGENT
```

**Step 2: Open in Cursor**
```bash
# Open the folder in Cursor
cursor .

# Or drag the folder to Cursor
```

**Step 3: Test the Agents**
```
Open Cursor Chat (Cmd/Ctrl + L)

Type: @researcher multi-agent collaboration

Expected: Agent responds and creates pipeline/01-research-output.md
```

**Step 4: Run Full Pipeline**
```
@researcher [your topic]
@writer
@qa
@optimizer

Result: Final post in pipeline/04-final-output.md
```

### For Claude Code

**Step 1: Run Installation Script**
```bash
chmod +x install.sh
./install.sh
```

**Step 2: Test**
```bash
# In Claude Code terminal
/content-pipeline "your topic here"
```

---

## 📖 Documentation Guide

**Start here:**
1. **QUICKSTART.md** - Get up and running in 5 minutes
2. **CURSOR_QUICK_REFERENCE.md** - Daily usage cheat sheet

**Go deeper:**
3. **ARCHITECTURE.md** - Understand the system design
4. **CURSOR_ARCHITECTURE.md** - Cursor-specific details
5. **EXAMPLES.md** - See real output samples

**Reference:**
6. **Sub_agents/*.md** - Detailed agent instructions
7. **content-pipeline-command.md** - Orchestrator logic

---

## 🎯 How It Works

### The 4-Agent Pipeline

```
Input: "multi-agent collaboration in production"
    ↓
┌─────────────────────────────────┐
│  RESEARCH AGENT                 │
│  Explores topic & finds insights│
│  Output: Research brief         │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  WRITER AGENT                   │
│  Drafts engaging post           │
│  Output: Complete draft         │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  QA AGENT (Quality Gate)        │
│  Reviews & approves/rejects     │
│  Output: QA verdict + feedback  │
└──────────────┬──────────────────┘
               ↓
       [If APPROVED]
               ↓
┌─────────────────────────────────┐
│  OPTIMIZER AGENT                │
│  Polishes for readability       │
│  Output: Final LinkedIn post    │
└─────────────────────────────────┘
```

### Key Features

✅ **Context Isolation** - Each agent operates in its own context window  
✅ **Quality Gates** - QA agent prevents bad content from advancing  
✅ **Sequential Pipeline** - Clear workflow: Research → Write → QA → Optimize  
✅ **Visible Data Flow** - All intermediate outputs saved as files  
✅ **Production Ready** - Built for real content creation  
✅ **Modular Design** - Easy to customize or extend  

---

## 💡 Usage Patterns

### Pattern 1: Cursor @ Mentions (Manual Control)

```
@researcher context isolation patterns
[Review output in pipeline/01-research-output.md]

@writer
[Review draft in pipeline/02-draft-output.md]

@qa
[Check verdict in pipeline/03-qa-output.md]

@optimizer
[Get final post in pipeline/04-final-output.md]
```

### Pattern 2: Cursor Composer (Automated)

```
Open Composer (Cmd/Ctrl + Shift + I)

Prompt:
"Create a LinkedIn post about [topic] using the 
multi-agent pipeline. Run all 4 phases."

[Composer executes everything automatically]
```

### Pattern 3: Claude Code Command

```
/content-pipeline "your topic here"

[Runs all 4 agents sequentially]
```

---

## 🔧 Customization

### Modify Agent Behavior

**For Cursor:**
```bash
# Edit agent rules
code .cursorrules/researcher.mdc
code .cursorrules/writer.mdc
code .cursorrules/qa.mdc
code .cursorrules/optimizer.mdc
```

**For Claude Code:**
```bash
# Edit agent instructions
code Sub_agents/research-agent.md
# Then reinstall with install.sh
```

### Adjust Quality Standards

Edit `.cursorrules/qa.mdc` (or `Sub_agents/qa-agent.md` for Claude Code):

```markdown
## Quality Gates

**APPROVED:**
- Hook strength: 9+/10  ← Raise the bar
- Engagement: High only ← More strict
```

### Change Output Format

Edit `.cursorrules/writer.mdc`:

```markdown
## LinkedIn Post Structure

Use this pattern:
[Your custom structure here]
```

---

## 📊 Example Output

**Input Topic:** "Why subagents prevent context bloat"

**Final Output (pipeline/04-final-output.md):**
```
Your AI agent is drowning in context.

Every search, file, and experimental step piling up in one 
conversation until you hit the limit.

This breaks production workflows.

[... full post continues ...]

One focused agent. One clean context. Better output.

---
Character count: 1,187
Read time: 34 seconds
```

See **EXAMPLES.md** for complete sample outputs from all 4 agents.

---

## 🚨 Troubleshooting

### Cursor: @ Mentions Don't Work

**Check:**
1. Is `.cursorrules/` directory present?
2. Are files named correctly? (`researcher.mdc` not `research-agent.md`)
3. Are you in the right project folder?

**Fix:**
```bash
ls -la .cursorrules/
# Should show: researcher.mdc, writer.mdc, qa.mdc, optimizer.mdc
```

### Pipeline Files Not Created

**Check:**
1. Does `pipeline/` directory exist?
2. Do agents have write permissions?

**Fix:**
```bash
mkdir -p pipeline
touch pipeline/01-research-output.md
touch pipeline/02-draft-output.md
touch pipeline/03-qa-output.md
touch pipeline/04-final-output.md
```

### QA Keeps Rejecting

**This is expected!** QA is the quality gate.

**Solutions:**
1. Review feedback in `pipeline/03-qa-output.md`
2. Common issues: weak hook, no examples, generic content
3. Fix in `pipeline/02-draft-output.md`
4. Re-run `@qa`

---

## 🎓 Learning Path

**Day 1:** Understand the system
- Read QUICKSTART.md
- Run the pipeline manually
- Observe each agent's output

**Day 2:** Daily usage
- Use CURSOR_QUICK_REFERENCE.md as cheat sheet
- Create 2-3 posts
- Note what works

**Day 3:** Customization
- Adjust agent rules for your style
- Tweak quality gates
- Add your own patterns

**Day 4+:** Production
- Integrate into content workflow
- Track performance
- Iterate based on results

---

## 📈 System Benefits

### vs Single AI Agent

**Before (Single Agent):**
- Context bloats with exploration
- Inconsistent quality
- Hard to iterate
- Manual quality checks

**After (Multi-Agent):**
- Context stays clean (isolation)
- Consistent quality (gates)
- Easy iteration (file-based)
- Automated quality (QA agent)

### Real Metrics

Based on Day 13-14 exploration:

- **Context efficiency:** 26x improvement (200k exploration → 7.6k main context)
- **Quality consistency:** QA gate ensures standards
- **Iteration speed:** 60% faster with automated pipeline
- **Output quality:** Higher engagement (specific examples, clear hooks)

---

## 🛠️ Technical Details

### Cursor Implementation

- **Agent Rules:** `.cursorrules/*.mdc` files
- **Communication:** File-based via `pipeline/` directory
- **Context:** Each agent gets fresh context per invocation
- **Orchestration:** Manual (@mentions) or automated (Composer)

### Claude Code Implementation

- **Subagents:** Native subagent support
- **Communication:** Hidden internal passing
- **Context:** Automatic isolation
- **Orchestration:** `/content-pipeline` command

### File Formats

- `.mdc` - Cursor agent rules (markdown compatible)
- `.md` - Documentation and pipeline outputs
- `.sh` - Installation/setup scripts

---

## 🤝 Contributing

This is a modular system. Contributions welcome:

- New agent types (image generation, hashtag research)
- Improved quality metrics
- Platform-specific templates (Twitter, blog posts)
- Integration with publishing tools

---

## 📝 License

MIT License - Use freely in your content workflows

---

## 🆘 Support

**Issues?**
1. Check QUICKSTART.md
2. Review CURSOR_QUICK_REFERENCE.md  
3. See troubleshooting section above

**Questions?**
- Review ARCHITECTURE.md for system design
- Check EXAMPLES.md for output samples

---

## 🎉 Next Steps

1. **Test the pipeline** - Run through all 4 agents
2. **Create real content** - Use it for your next post
3. **Customize** - Adjust agents to your voice
4. **Track results** - Note what performs well
5. **Iterate** - Improve based on learnings

---

**Built for Day 13-14 of AI GTM Engineering exploration**

Transform topics into LinkedIn posts through specialized agent collaboration. 🚀

---

## Version History

- **v1.0** (March 2026) - Initial release
  - 4 specialized agents
  - Cursor + Claude Code support
  - Production-ready pipeline
  - Complete documentation
