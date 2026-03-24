# System Architecture - AI GTM Content System

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                │
│                   "Create a LinkedIn post                        │
│              about multi-agent collaboration"                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MAIN AGENT (Orchestrator)                      │
│                  /content-pipeline command                       │
│                                                                   │
│  Responsibilities:                                                │
│  • Parse user request                                            │
│  • Coordinate subagent execution                                 │
│  • Enforce quality gates                                         │
│  • Synthesize final output                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Sequential Pipeline
                           ▼
        ┌──────────────────────────────────────────┐
        │         PHASE 1: RESEARCH                │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │   content-researcher subagent      │ │
        │  │                                    │ │
        │  │  Context: Fresh 200k tokens       │ │
        │  │  Tools: Read, Grep, Bash          │ │
        │  │  Model: Sonnet                    │ │
        │  │                                    │ │
        │  │  Input: Topic                     │ │
        │  │  Output: Research Brief           │ │
        │  │   • Key angle                     │ │
        │  │   • 3-5 insights                  │ │
        │  │   • Examples                      │ │
        │  │   • Hook suggestions              │ │
        │  └────────────────────────────────────┘ │
        └──────────────────┬───────────────────────┘
                           │ Research Brief
                           ▼
        ┌──────────────────────────────────────────┐
        │         PHASE 2: WRITING                 │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │   content-writer subagent          │ │
        │  │                                    │ │
        │  │  Context: Fresh 200k tokens       │ │
        │  │  Tools: Read, Write, Edit         │ │
        │  │  Model: Sonnet                    │ │
        │  │                                    │ │
        │  │  Input: Research Brief            │ │
        │  │  Output: Post Draft               │ │
        │  │   • Complete post                 │ │
        │  │   • Character count               │ │
        │  │   • Hook alternatives             │ │
        │  │   • Writing notes                 │ │
        │  └────────────────────────────────────┘ │
        └──────────────────┬───────────────────────┘
                           │ Post Draft
                           ▼
        ┌──────────────────────────────────────────┐
        │         PHASE 3: QUALITY ASSURANCE       │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │   content-qa subagent              │ │
        │  │                                    │ │
        │  │  Context: Fresh 200k tokens       │ │
        │  │  Tools: Read                      │ │
        │  │  Model: Sonnet                    │ │
        │  │                                    │ │
        │  │  Input: Post Draft                │ │
        │  │  Output: QA Report                │ │
        │  │   • Verdict (Approve/Revise/Reject)│ │
        │  │   • Structural issues             │ │
        │  │   • Clarity issues                │ │
        │  │   • Specific fixes                │ │
        │  └────────────────────────────────────┘ │
        └──────────────────┬───────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
        APPROVED│              │NEEDS REVISION
                │              └──────┐
                ▼                     │
        ┌──────────────────────────┐ │
        │  PHASE 4: OPTIMIZATION   │ │
        │                          │ │
        │  ┌──────────────────────┐│ │
        │  │content-optimizer     ││ │
        │  │                      ││ │
        │  │ Context: Fresh 200k  ││ │
        │  │ Tools: Read, Edit    ││ │
        │  │ Model: Sonnet        ││ │
        │  │                      ││ │
        │  │ Input: QA-approved   ││ │
        │  │ Output: Final Post   ││ │
        │  │  • Polished version  ││ │
        │  │  • Optimizations     ││ │
        │  │  • Metrics           ││ │
        │  └──────────────────────┘│ │
        └──────────────┬───────────┘ │
                       │             │
                       ▼             │
              ┌──────────────┐      │
              │ FINAL OUTPUT │      │
              └──────────────┘      │
                                    │
                Loop back to ───────┘
                Writing Phase


```

## Component Breakdown

### Main Agent (Orchestrator)

**File**: `~/.claude/commands/content-pipeline.md`

**Responsibilities**:
- User interaction and clarification
- Sequential workflow coordination
- Quality gate enforcement
- Result synthesis
- Error handling

**Context Management**:
- Receives only summaries from subagents
- Never executes research/writing/QA/optimization itself
- Maintains conversation history with user
- Typical context usage: 10-20k tokens

---

### Subagent 1: Research

**File**: `~/.claude/agents/content-researcher.md`

**Purpose**: Explore topics and extract insights

**Inputs**:
- Topic from main agent
- Optional focus areas
- Target audience context

**Processing**:
- Breaks down topic into themes
- Identifies compelling angles
- Finds real-world examples
- Generates hook suggestions

**Outputs**:
- Structured research brief (~500 tokens)
- Key insights (3-5 points)
- Supporting examples
- Suggested hooks

**Context Isolation**:
- Can explore 100+ documents
- All exploration stays in subagent context
- Main agent gets clean brief, not raw research

---

### Subagent 2: Writing

**File**: `~/.claude/agents/content-writer.md`

**Purpose**: Draft engaging LinkedIn posts

**Inputs**:
- Research brief from Research subagent
- Style preferences
- Length target

**Processing**:
- Applies LinkedIn post structure
- Weaves insights into narrative
- Creates scannable format
- Includes specific examples

**Outputs**:
- Complete post draft
- Character count and metadata
- Alternative hook options
- Writing notes for QA

**Context Isolation**:
- Never sees raw research data
- Works from curated brief only
- Can iterate on drafts without bloating main context

---

### Subagent 3: QA

**File**: `~/.claude/agents/content-qa.md`

**Purpose**: Review quality and enforce standards

**Inputs**:
- Post draft from Writing subagent
- Quality criteria

**Processing**:
- Structural review (hook, flow, conclusion)
- Clarity review (readability, ambiguity)
- Engagement review (scroll-stop potential)

**Outputs**:
- QA verdict (APPROVED / NEEDS REVISION / REJECTED)
- Specific issues found
- Required fixes
- Suggestions for optimization

**Quality Gates**:
- REJECTED → Restart from Research
- NEEDS REVISION → Loop to Writing
- APPROVED → Proceed to Optimization

**Context Isolation**:
- Focused only on quality assessment
- No writing or optimization attempted
- Clean separation of concerns

---

### Subagent 4: Optimization

**File**: `~/.claude/agents/content-optimizer.md`

**Purpose**: Polish readability and impact

**Inputs**:
- QA-approved draft
- QA suggestions for improvement

**Processing**:
- Word-level optimization (economy, power words)
- Sentence-level optimization (rhythm, active voice)
- Paragraph-level optimization (flow, coherence)
- Final polish pass

**Outputs**:
- Final polished post
- Before/after samples
- Readability metrics
- Character count comparison

**Context Isolation**:
- Works only on approved content
- No structural changes
- Preserves author's voice while enhancing clarity

---

## Data Flow

```
Topic → [Research] → Brief → [Write] → Draft → [QA] → Report → [Optimize] → Final
         ↑200k ctx          ↑200k ctx        ↑200k ctx         ↑200k ctx
         │                  │                │                 │
         │                  │                │                 │
         └──────────────────┴────────────────┴─────────────────┘
                All isolated, fresh context windows
```

## Context Management Strategy

### Problem: Single-Agent Context Bloat

```
Single Agent Approach:
┌──────────────────────────────────────┐
│ Main Agent Context (200k limit)      │
│                                      │
│ [Research exploration: 150k tokens]  │
│ [Planning: 20k tokens]               │
│ [Writing attempts: 25k tokens]       │
│ [Revisions: 15k tokens]              │
│ = 210k tokens → OVERFLOW             │
└──────────────────────────────────────┘
```

### Solution: Multi-Subagent Context Isolation

```
Multi-Agent Approach:
┌──────────────────────────────────────┐
│ Main Agent Context                   │
│                                      │
│ [User conversation: 5k tokens]       │
│ [Research brief: 500 tokens]         │
│ [Draft metadata: 300 tokens]         │
│ [QA report: 400 tokens]              │
│ [Final post: 1.4k tokens]            │
│ = 7.6k tokens → 96% free             │
└──────────────────────────────────────┘

Research Subagent: 150k tokens (isolated)
Writing Subagent: 25k tokens (isolated)
QA Subagent: 15k tokens (isolated)
Optimization Subagent: 10k tokens (isolated)

Total work: 200k tokens
Main context used: 7.6k tokens
Efficiency: 26x improvement
```

## Quality Gates

### Gate 1: Research Quality

**Check**: After Research phase
**Criteria**:
- ✓ Insights are specific, not generic
- ✓ Examples are concrete
- ✓ Angle is clear and compelling

**Action on Fail**: 
- Request more specific topic
- Or restart Research with better constraints

---

### Gate 2: Draft Quality

**Check**: After Writing phase (before QA)
**Criteria**:
- ✓ Hook grabs attention
- ✓ Structure follows best practices
- ✓ Value is front-loaded
- ✓ Character count acceptable

**Action on Fail**:
- Rarely needed (QA is the main gate)

---

### Gate 3: QA Approval (CRITICAL)

**Check**: After QA phase
**Criteria**:
- ✓ Verdict = "APPROVED"
- ✓ No critical issues
- ✓ Engagement potential ≥ Medium

**Action on Fail**:
- NEEDS REVISION → Loop to Writing with feedback
- REJECTED → Loop to Research or change topic

---

### Gate 4: Final Polish

**Check**: After Optimization
**Criteria**:
- ✓ Readability metrics met
- ✓ Character count optimal
- ✓ Natural flow maintained

**Action on Fail**:
- Rare (optimization doesn't change structure)

---

## System Properties

### Modularity
Each subagent is independent and replaceable:
- Swap Research agent for different research methodology
- Upgrade QA agent with stricter criteria
- Replace Optimizer with brand-specific polish

### Reproducibility
Same topic → Same pipeline → Consistent quality:
- No "prompt magic" needed
- Process is codified in subagents
- Quality is enforced by gates

### Scalability
Can extend to more subagents:
- Add Image Generation subagent
- Add Hashtag Research subagent
- Add Engagement Prediction subagent

### Reliability
Quality gates prevent bad outputs:
- QA must approve before optimization
- Each phase has specific success criteria
- Pipeline fails gracefully with clear error messages

---

## File Organization

```
~/.claude/
├── agents/
│   ├── content-researcher.md    # Subagent 1: Research
│   ├── content-writer.md        # Subagent 2: Writing
│   ├── content-qa.md            # Subagent 3: QA
│   └── content-optimizer.md     # Subagent 4: Optimization
│
└── commands/
    └── content-pipeline.md      # Main orchestrator
```

## Execution Model

**Sequential, not Parallel**: Quality gates require order
**Synchronous, not Async**: Each phase completes before next begins
**Stateless Subagents**: Each runs independently with fresh context
**Stateful Orchestrator**: Main agent tracks progress and results

---

This architecture enables:
- ✅ Clean separation of responsibilities
- ✅ Context window sustainability
- ✅ Predictable quality output
- ✅ Easy modification and extension
- ✅ Production-ready reliability

The system behaves less like one AI tool and more like a small,
collaborating team—exactly as intended.
