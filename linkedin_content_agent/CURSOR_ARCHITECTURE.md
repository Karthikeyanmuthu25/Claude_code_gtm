# Multi-Subagent Architecture in Cursor

## Overview

Cursor doesn't have native subagent support like Claude Code, but we can achieve the same multi-agent collaboration using:

1. **Cursor Rules** (`.cursorrules` files) - Define agent behaviors
2. **Composer Mode** - Orchestrate multi-step workflows
3. **Context Files** - Pass data between "agents"
4. **Custom Commands** - Automate the pipeline

## Architecture Comparison

### Claude Code (Native Subagents)
```
/content-pipeline → Invokes 4 separate subagents
Each subagent = isolated context window
```

### Cursor (Simulated Subagents)
```
Composer → Executes 4 sequential tasks
Each task = scoped context using .cursorrules
```

## Implementation Strategy

### Strategy 1: Cursor Rules per "Agent" (Recommended)

Create separate `.cursorrules` files for each agent role.

**File Structure:**
```
your-project/
├── .cursorrules/
│   ├── researcher.mdc          # Research agent rules
│   ├── writer.mdc              # Writer agent rules
│   ├── qa.mdc                  # QA agent rules
│   └── optimizer.mdc           # Optimizer agent rules
│
├── agents/
│   ├── research-prompt.md      # Research agent prompt
│   ├── writer-prompt.md        # Writer agent prompt
│   ├── qa-prompt.md            # QA agent prompt
│   └── optimizer-prompt.md     # Optimizer agent prompt
│
└── pipeline/
    ├── 01-research-output.md
    ├── 02-draft-output.md
    ├── 03-qa-output.md
    └── 04-final-output.md
```

### Strategy 2: Composer Workflows (Automation)

Use Cursor's Composer to orchestrate the pipeline.

**Workflow Pattern:**
```
1. User: "Create LinkedIn post about [topic]"
2. Composer executes 4 tasks sequentially:
   - Task 1: Research (uses researcher.mdc rules)
   - Task 2: Write (uses writer.mdc rules)
   - Task 3: QA (uses qa.mdc rules)
   - Task 4: Optimize (uses optimizer.mdc rules)
```

### Strategy 3: Context File Passing

Agents communicate via intermediate files.

**Data Flow:**
```
Research Agent 
  → writes to: pipeline/01-research-output.md
  
Writer Agent 
  → reads: pipeline/01-research-output.md
  → writes to: pipeline/02-draft-output.md
  
QA Agent
  → reads: pipeline/02-draft-output.md
  → writes to: pipeline/03-qa-output.md
  
Optimizer Agent
  → reads: pipeline/02-draft-output.md + pipeline/03-qa-output.md
  → writes to: pipeline/04-final-output.md
```

## Detailed Implementation

### Step 1: Create Agent Rule Files

#### `.cursorrules/researcher.mdc`

```markdown
# Research Agent Rules

You are a specialized RESEARCH AGENT for LinkedIn content.

## Your Role
Explore topics and extract actionable insights.

## Output Format
Always output to: `pipeline/01-research-output.md`

Structure:
```
TOPIC: [topic]
KEY ANGLE: [angle]
CORE INSIGHTS:
1. [insight 1]
2. [insight 2]
3. [insight 3]
EXAMPLES:
- [example 1]
- [example 2]
SUGGESTED HOOKS:
- [hook 1]
- [hook 2]
```

## Constraints
- Research ONLY, don't write the post
- Output 300-500 tokens max
- Focus on specific, actionable insights
- Include concrete examples with numbers

## When Active
Activate when user says:
- "Research [topic]"
- "Phase 1: Research"
- "Explore [topic]"
```

#### `.cursorrules/writer.mdc`

```markdown
# Writer Agent Rules

You are a specialized WRITING AGENT for LinkedIn posts.

## Your Role
Draft engaging LinkedIn posts from research briefs.

## Input Source
Read from: `pipeline/01-research-output.md`

## Output Format
Always output to: `pipeline/02-draft-output.md`

Structure:
```
POST DRAFT:
[complete LinkedIn post]

---
METADATA:
Character count: [X]
Hook used: [hook]
Alternative hooks:
- [alt 1]
- [alt 2]
```

## Constraints
- 150-300 words optimal
- Under 3000 characters (LinkedIn limit)
- Conversational tone
- Include specific examples from research
- Front-load value

## When Active
Activate when user says:
- "Write the post"
- "Phase 2: Writing"
- "Draft from research"
```

#### `.cursorrules/qa.mdc`

```markdown
# QA Agent Rules

You are a specialized QUALITY ASSURANCE AGENT.

## Your Role
Review posts for quality, clarity, and engagement.

## Input Source
Read from: `pipeline/02-draft-output.md`

## Output Format
Always output to: `pipeline/03-qa-output.md`

Structure:
```
QA REVIEW REPORT

VERDICT: [APPROVED / NEEDS REVISION / REJECTED]

HOOK ASSESSMENT: [rating/10]
[analysis]

STRUCTURAL ISSUES:
[issues or "None"]

CLARITY ISSUES:
[issues or "None"]

ENGAGEMENT POTENTIAL: [High/Medium/Low]

REQUIRED CHANGES:
1. [change 1 or "None"]

SUGGESTIONS FOR OPTIMIZER:
- [suggestion 1]
```

## Quality Gates
- APPROVED: Proceed to optimization
- NEEDS REVISION: Return to writer
- REJECTED: Return to research

## When Active
Activate when user says:
- "Review the draft"
- "Phase 3: QA"
- "Quality check"
```

#### `.cursorrules/optimizer.mdc`

```markdown
# Optimizer Agent Rules

You are a specialized OPTIMIZATION AGENT.

## Your Role
Polish QA-approved posts for maximum impact.

## Input Sources
- Draft: `pipeline/02-draft-output.md`
- QA Report: `pipeline/03-qa-output.md`

## Output Format
Always output to: `pipeline/04-final-output.md`

Structure:
```
OPTIMIZED POST:
[polished version]

---
OPTIMIZATION SUMMARY:
Character count: [before] → [after]
Key changes:
• [change 1]
• [change 2]

BEFORE/AFTER:
[examples]

READABILITY METRICS:
- Avg sentence: [X] words
- Read time: [X] seconds
```

## Constraints
- Only optimize APPROVED drafts
- Preserve voice and message
- Focus on readability and flow
- Don't add new content

## When Active
Activate when user says:
- "Optimize the post"
- "Phase 4: Optimization"
- "Polish the approved draft"
```

---

### Step 2: Create Agent Prompt Files

These are fuller instructions that agents can reference.

#### `agents/research-prompt.md`

```markdown
# Research Agent - Full Instructions

[Copy content from content-researcher-instructions.md]

## Cursor-Specific Notes

### Activation
You activate when the user types one of:
- "Research: [topic]"
- "Phase 1: Research"
- "@researcher [topic]"

### Output Location
Always write your research brief to:
`pipeline/01-research-output.md`

### Context Scope
You have access to:
- User's topic/request
- Project files (for context)
- Web search (if enabled)

You do NOT have access to:
- Previous agent outputs (stay focused)
- Full conversation history

### Handoff
After completing research, tell the user:
"Research complete. Ready for Phase 2: Writing."
```

[Repeat for writer-prompt.md, qa-prompt.md, optimizer-prompt.md]

---

### Step 3: Create Pipeline Directory Structure

```bash
# In your project root
mkdir -p pipeline agents .cursorrules

# Create empty pipeline files
touch pipeline/01-research-output.md
touch pipeline/02-draft-output.md
touch pipeline/03-qa-output.md
touch pipeline/04-final-output.md

# Create .gitkeep to track directory
touch pipeline/.gitkeep
```

---

### Step 4: Create Orchestrator Script

#### `orchestrator.sh` (Bash - for Mac/Linux)

```bash
#!/bin/bash

# Multi-Agent Content Pipeline for Cursor
# Usage: ./orchestrator.sh "your topic here"

TOPIC="$1"

if [ -z "$TOPIC" ]; then
    echo "Usage: ./orchestrator.sh \"your topic\""
    exit 1
fi

echo "🚀 Starting Content Pipeline"
echo "Topic: $TOPIC"
echo ""

# Clear previous outputs
rm -f pipeline/*.md
touch pipeline/.gitkeep

# Phase 1: Research
echo "═══ Phase 1/4: Research ═══"
cursor chat "Research: $TOPIC" --rules .cursorrules/researcher.mdc
echo "✓ Research complete"
echo ""

# Phase 2: Writing
echo "═══ Phase 2/4: Writing ═══"
cursor chat "Write the post using pipeline/01-research-output.md" --rules .cursorrules/writer.mdc
echo "✓ Draft complete"
echo ""

# Phase 3: QA
echo "═══ Phase 3/4: QA Review ═══"
cursor chat "Review the draft in pipeline/02-draft-output.md" --rules .cursorrules/qa.mdc
echo "✓ QA complete"
echo ""

# Check QA verdict
if grep -q "VERDICT: APPROVED" pipeline/03-qa-output.md; then
    # Phase 4: Optimization
    echo "═══ Phase 4/4: Optimization ═══"
    cursor chat "Optimize pipeline/02-draft-output.md using feedback from pipeline/03-qa-output.md" --rules .cursorrules/optimizer.mdc
    echo "✓ Optimization complete"
    echo ""
    echo "✅ Pipeline complete! Check pipeline/04-final-output.md"
else
    echo "⚠️  QA did not approve. Check pipeline/03-qa-output.md for feedback."
fi
```

#### `orchestrator.ps1` (PowerShell - for Windows)

```powershell
# Multi-Agent Content Pipeline for Cursor
# Usage: .\orchestrator.ps1 "your topic here"

param([string]$Topic)

if (-not $Topic) {
    Write-Host "Usage: .\orchestrator.ps1 'your topic'"
    exit 1
}

Write-Host "🚀 Starting Content Pipeline"
Write-Host "Topic: $Topic"
Write-Host ""

# Clear previous outputs
Remove-Item pipeline\*.md -ErrorAction SilentlyContinue
New-Item pipeline\.gitkeep -Force | Out-Null

# Phase 1: Research
Write-Host "═══ Phase 1/4: Research ═══"
cursor chat "Research: $Topic" --rules .cursorrules\researcher.mdc
Write-Host "✓ Research complete"
Write-Host ""

# Phase 2: Writing  
Write-Host "═══ Phase 2/4: Writing ═══"
cursor chat "Write the post using pipeline/01-research-output.md" --rules .cursorrules\writer.mdc
Write-Host "✓ Draft complete"
Write-Host ""

# Phase 3: QA
Write-Host "═══ Phase 3/4: QA Review ═══"
cursor chat "Review the draft in pipeline/02-draft-output.md" --rules .cursorrules\qa.mdc
Write-Host "✓ QA complete"
Write-Host ""

# Check QA verdict
$qaContent = Get-Content pipeline\03-qa-output.md -Raw
if ($qaContent -match "VERDICT: APPROVED") {
    # Phase 4: Optimization
    Write-Host "═══ Phase 4/4: Optimization ═══"
    cursor chat "Optimize pipeline/02-draft-output.md using feedback from pipeline/03-qa-output.md" --rules .cursorrules\optimizer.mdc
    Write-Host "✓ Optimization complete"
    Write-Host ""
    Write-Host "✅ Pipeline complete! Check pipeline/04-final-output.md"
} else {
    Write-Host "⚠️  QA did not approve. Check pipeline/03-qa-output.md for feedback."
}
```

---

### Step 5: Manual Workflow (Using Cursor Composer)

If you prefer manual control over scripts:

#### Composer Workflow

1. **Open Cursor Composer** (Cmd/Ctrl + Shift + I)

2. **Phase 1: Research**
   ```
   @researcher Research this topic for a LinkedIn post:
   
   "Multi-agent collaboration in production"
   
   Output to pipeline/01-research-output.md
   ```

3. **Phase 2: Writing**
   ```
   @writer Create a LinkedIn post draft.
   
   Use insights from: pipeline/01-research-output.md
   Output to: pipeline/02-draft-output.md
   ```

4. **Phase 3: QA**
   ```
   @qa Review this draft for quality and engagement.
   
   Draft location: pipeline/02-draft-output.md
   Output to: pipeline/03-qa-output.md
   ```

5. **Phase 4: Optimization** (if QA approved)
   ```
   @optimizer Polish this QA-approved draft.
   
   Draft: pipeline/02-draft-output.md
   QA feedback: pipeline/03-qa-output.md
   Output to: pipeline/04-final-output.md
   ```

---

## Alternative: VSCode Tasks Integration

### `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Content Pipeline: Full",
      "type": "shell",
      "command": "./orchestrator.sh '${input:topic}'",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Content Pipeline: Research Only",
      "type": "shell",
      "command": "cursor chat 'Research: ${input:topic}' --rules .cursorrules/researcher.mdc"
    }
  ],
  "inputs": [
    {
      "id": "topic",
      "type": "promptString",
      "description": "What topic should we research?"
    }
  ]
}
```

Then run: `Cmd/Ctrl + Shift + B` → Select "Content Pipeline: Full"

---

## Cursor-Specific Advantages

### 1. Visual File Context
```
Cursor shows you:
pipeline/
├── 01-research-output.md   ← Can see the research
├── 02-draft-output.md      ← Can see the draft
├── 03-qa-output.md         ← Can see QA feedback
└── 04-final-output.md      ← Can see final result
```

### 2. Easy Manual Intervention
```
If QA rejects:
1. Review pipeline/03-qa-output.md
2. Manually edit pipeline/02-draft-output.md
3. Re-run QA phase
4. Continue to optimization
```

### 3. Composer Multi-Step
```
Composer can execute all 4 phases in one conversation:

User: "Create a LinkedIn post about context isolation"

Composer:
→ Step 1: Research [executes]
→ Step 2: Write [executes]
→ Step 3: QA [executes]
→ Step 4: Optimize [executes]
→ Delivers final post
```

### 4. Git Integration
```
Track changes to:
- Agent rules (.cursorrules/)
- Pipeline outputs (pipeline/)
- Agent prompts (agents/)

Each iteration = commit for review
```

---

## Context Isolation Techniques

### Technique 1: Clear File Instructions

In each agent's rules:
```markdown
## Context Scope

YOU ONLY READ:
- pipeline/01-research-output.md

YOU ONLY WRITE:
- pipeline/02-draft-output.md

DO NOT:
- Reference other pipeline files
- Access previous conversation
- Make assumptions about other agents
```

### Technique 2: Composer Task Boundaries

```
Task 1: Research
- Context: User topic only
- Output: Research file

Task 2: Write
- Context: Research file only
- Output: Draft file

[Tasks are isolated in Composer]
```

### Technique 3: Explicit Context Reset

Between agents, use:
```
@researcher [topic]
[Agent completes]

/clear  # Clear Cursor's context

@writer use pipeline/01-research-output.md
[Next agent starts fresh]
```

---

## Comparison: Claude Code vs Cursor

| Feature | Claude Code | Cursor |
|---------|-------------|--------|
| Native subagents | ✅ Yes | ❌ No (simulated) |
| Context isolation | ✅ Automatic | ⚠️ Manual (.cursorrules) |
| Orchestration | ✅ Built-in commands | ⚠️ Scripts or Composer |
| File passing | ➖ Not needed | ✅ Explicit (clearer) |
| Visual pipeline | ❌ No | ✅ Yes (file tree) |
| Manual intervention | ⚠️ Harder | ✅ Easy (edit files) |
| Setup complexity | ✅ Simple | ⚠️ More setup |

---

## Best Practices for Cursor

### 1. Name Your Pipeline Files Clearly
```
✓ 01-research-output.md
✓ 02-draft-output.md
✗ research.md
✗ output.md
```

### 2. Use Git for Pipeline Tracking
```bash
git add pipeline/
git commit -m "Research phase complete for [topic]"
```

### 3. Create Templates
```
pipeline/templates/
├── research-template.md
├── draft-template.md
├── qa-template.md
└── optimizer-template.md
```

### 4. Document Your Workflow
```
README.md:

## Content Pipeline Usage

1. Research: `cursor chat "@researcher [topic]"`
2. Write: `cursor chat "@writer use research"`
3. QA: `cursor chat "@qa review draft"`
4. Optimize: `cursor chat "@optimizer polish"`

Or run full pipeline: `./orchestrator.sh "topic"`
```

---

## Next Steps

1. ✅ Set up directory structure
2. ✅ Create .cursorrules files
3. ✅ Create orchestrator script
4. ✅ Test with sample topic
5. ✅ Iterate and refine

The key difference: **Cursor uses files for context passing**, which is actually more transparent than Claude Code's hidden subagent communication!

---

**Cursor Architecture**: File-based agent collaboration  
**Advantage**: Visual, traceable, git-friendly  
**Tradeoff**: More manual orchestration needed
