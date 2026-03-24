# Cursor Multi-Agent Pipeline - Quick Reference

## 🚀 Quick Commands

| Phase | Command | Output File |
|-------|---------|-------------|
| Research | `@researcher [topic]` | `pipeline/01-research-output.md` |
| Writing | `@writer` | `pipeline/02-draft-output.md` |
| QA Review | `@qa` | `pipeline/03-qa-output.md` |
| Optimization | `@optimizer` | `pipeline/04-final-output.md` |

## 📊 Pipeline Workflow

```
┌─────────────────────────────────────────────────────────┐
│  YOU: "Create post about multi-agent workflows"         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  @researcher            │
        │  Explores topic         │
        │  ↓                      │
        │  01-research-output.md  │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  @writer                │
        │  Drafts post            │
        │  ↓                      │
        │  02-draft-output.md     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │  @qa                    │
        │  Reviews quality        │
        │  ↓                      │
        │  03-qa-output.md        │
        └────────────┬────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    APPROVED              NEEDS REVISION
          │                     │
          │                     └──► Loop to @writer
          │
        ┌─▼──────────────────────┐
        │  @optimizer             │
        │  Final polish           │
        │  ↓                      │
        │  04-final-output.md     │
        └─────────────────────────┘
                     │
                     ▼
           📄 Ready to Publish!
```

## 💡 Usage Patterns

### Pattern 1: Full Manual Control

```
Step 1: @researcher context isolation patterns
[Wait, review output]

Step 2: @writer
[Wait, review draft]

Step 3: @qa
[Check verdict]

Step 4 (if approved): @optimizer
[Get final post]
```

### Pattern 2: Composer Automation

```
Open Composer (Cmd/Ctrl + Shift + I)

Prompt:
"Create a LinkedIn post about [topic] using the 
multi-agent pipeline. Run all 4 phases: research, 
write, QA, and optimize."

[Composer executes all phases]
```

### Pattern 3: With Manual Intervention

```
@researcher [topic]
@writer
@qa
[QA says "NEEDS REVISION"]

→ Edit pipeline/02-draft-output.md manually
→ @qa again
[QA says "APPROVED"]

@optimizer
```

## 🎯 Agent Responsibilities

| Agent | Reads | Writes | Purpose |
|-------|-------|--------|---------|
| **Researcher** | User input | `01-research-output.md` | Explore & extract insights |
| **Writer** | `01-research-output.md` | `02-draft-output.md` | Draft engaging post |
| **QA** | `02-draft-output.md` | `03-qa-output.md` | Review & approve/reject |
| **Optimizer** | `02 & 03` | `04-final-output.md` | Polish approved draft |

## ✅ Quality Gates

### Gate 1: Research Complete
- ✓ 3-5 insights identified
- ✓ Concrete examples present
- ✓ Clear angle found

### Gate 2: Draft Complete
- ✓ Hook is present
- ✓ Structure follows pattern
- ✓ Examples included

### Gate 3: QA Approval ⚠️ CRITICAL
- ✓ Verdict = "APPROVED"
- ✓ Hook rated 8+/10
- ✓ Engagement potential ≥ Medium

### Gate 4: Optimization Complete
- ✓ Readability improved
- ✓ Character count optimal
- ✓ Flow enhanced

## 📁 File Structure

```
your-project/
├── .cursorrules/
│   ├── researcher.mdc    ← Agent behavior rules
│   ├── writer.mdc
│   ├── qa.mdc
│   └── optimizer.mdc
│
└── pipeline/
    ├── 01-research-output.md    ← Agent outputs
    ├── 02-draft-output.md
    ├── 03-qa-output.md
    └── 04-final-output.md
```

## 🔧 Common Tasks

### Start a New Post
```bash
# Clear previous pipeline
rm pipeline/*.md
touch pipeline/.gitkeep

# Start fresh
@researcher [your topic]
```

### Re-run a Phase
```bash
# If QA rejects, fix and re-run
# 1. Edit pipeline/02-draft-output.md
# 2. Run QA again
@qa
```

### Check Current Status
```bash
# View file tree in Cursor
# See which pipeline files exist
ls -la pipeline/

# Or just look in Cursor's sidebar
```

### Debug a Phase
```bash
# Each agent only reads specific files:

@researcher → Reads: User input only
@writer → Reads: 01-research-output.md
@qa → Reads: 02-draft-output.md
@optimizer → Reads: 02 & 03
```

## 🚨 Troubleshooting

### Agent Doesn't Respond
```
Check:
1. Is .cursorrules/[agent].mdc present?
2. Did you use @ mention? (@researcher, @writer, etc.)
3. Is the rule file properly formatted?
```

### Wrong Output File
```
Check:
- Each agent MUST write to its specific pipeline file
- Researcher → 01-research-output.md
- Writer → 02-draft-output.md
- QA → 03-qa-output.md
- Optimizer → 04-final-output.md
```

### QA Keeps Rejecting
```
Solutions:
1. Review QA feedback in 03-qa-output.md
2. Common issues:
   - Hook too weak
   - No concrete examples
   - Generic content
3. Fix in 02-draft-output.md
4. Re-run @qa
```

### Pipeline State Confusion
```
Reset:
# Clear all pipeline files
rm pipeline/*.md
touch pipeline/.gitkeep

# Start fresh from research
@researcher [topic]
```

## 💪 Pro Tips

### Tip 1: Track with Git
```bash
git add pipeline/
git commit -m "Research phase: [topic]"

# Track each phase
# Easy to rollback if needed
```

### Tip 2: Use Templates
```bash
# Copy templates before starting
cp pipeline/templates/* pipeline/

# Then agents fill in the structure
```

### Tip 3: Manual Tweaks
```
QA approved but you want changes?

1. Edit 04-final-output.md directly
2. Keep the pipeline file as-is
3. Your manual edit = final version
```

### Tip 4: Batch Processing
```
# Create multiple topics in sequence

@researcher topic 1
@writer
@qa
@optimizer

# Save 04-final-output.md as final-topic-1.md

# Then repeat for topic 2
rm pipeline/*.md
@researcher topic 2
...
```

## 📊 Metrics to Watch

After each pipeline run, check:

- **Character count**: Should be 1,200-1,500 optimal
- **Read time**: Should be 30-45 seconds
- **Hook strength**: QA rates 8+/10
- **Engagement potential**: High or Medium
- **Iterations**: Ideally QA approves on first pass

## 🎓 Learning Curve

**Day 1**: Run full pipeline manually
- Understand each agent's role
- See how files pass data

**Day 2**: Start customizing rules
- Adjust .cursorrules/*.mdc for your style
- Tune quality gates

**Day 3**: Use Composer automation
- Let it run end-to-end
- Intervene only when needed

**Day 4+**: Production use
- Create real content
- Track what works
- Iterate on agent rules

---

## 🚀 One-Liner Usage

```
@researcher [topic] → @writer → @qa → @optimizer → Done!
```

---

**Remember**: Each agent focuses on ONE thing. The power is in the collaboration!
