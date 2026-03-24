# Content Pipeline Orchestrator - Command Instructions

## Command Identity

**Name**: content-pipeline  
**Version**: 1.0  
**Type**: Multi-agent orchestrator command  
**Purpose**: Coordinate 4 subagents to create LinkedIn posts

## Command Synopsis

```
/content-pipeline "<topic>"

Example:
/content-pipeline "multi-agent collaboration in production"
```

## System Architecture

```
┌─────────────────────────────────────────────────┐
│           ORCHESTRATOR (This Command)            │
│  Coordinates execution, enforces quality gates   │
└───────────┬─────────────────────────────────────┘
            │
            ├→ Phase 1: Research
            │  └─ Invoke: content-researcher
            │     Output: Research brief (300-500 tokens)
            │
            ├→ Phase 2: Writing  
            │  └─ Invoke: content-writer
            │     Output: Post draft + metadata
            │
            ├→ Phase 3: Quality Assurance ⚠️ GATE
            │  └─ Invoke: content-qa-agent
            │     Output: QA verdict + feedback
            │     Decision:
            │       • APPROVED → Continue to Phase 4
            │       • NEEDS REVISION → Loop to Phase 2
            │       • REJECTED → Loop to Phase 1
            │
            └→ Phase 4: Optimization
               └─ Invoke: content-optimizer
                  Output: Final polished post
```

## Execution Workflow

### Phase 0: Initialization

**Input**: Topic from user

**Actions**:
1. Parse topic
2. Ask clarifying questions (if needed):
   - Target length? (short/standard/long)
   - Technical depth? (high/medium/low)
   - Specific requirements?
3. Prepare execution context

**Output**: Confirmed parameters

---

### Phase 1: Research

**Objective**: Explore topic and gather insights

**Invocation**:
```
Use the content-researcher subagent to explore this topic:

Topic: [USER_TOPIC]

Optional focus:
[Any specific angles or constraints from initialization]
```

**Wait Condition**: Research brief received

**Quality Check**:
- ✓ Key angle identified?
- ✓ 3-5 insights present?
- ✓ Examples are concrete?

**On Failure**: Request clarification or narrower topic

**Output to Next Phase**: Research brief

---

### Phase 2: Writing

**Objective**: Draft the LinkedIn post

**Invocation**:
```
Use the content-writer subagent to draft a LinkedIn post.

Input from research:
[PASTE COMPLETE RESEARCH BRIEF]

Requirements:
- Length: [from initialization]
- Technical depth: [from initialization]
- Include examples from research
- Follow LinkedIn post structure
```

**Wait Condition**: Draft received

**Quality Check**:
- ✓ Draft is complete?
- ✓ Character count provided?
- ✓ Hook is present?
- ✓ Examples included?

**On Failure**: Re-invoke with specific guidance

**Output to Next Phase**: Post draft + metadata

---

### Phase 3: Quality Assurance (CRITICAL GATE)

**Objective**: Review and approve/reject draft

**Invocation**:
```
Use the content-qa-agent subagent to review this draft:

[PASTE COMPLETE DRAFT]

Review for:
- Hook strength
- Structural clarity
- Engagement potential
- Overall quality
```

**Wait Condition**: QA verdict received

**Quality Gate Logic**:
```
IF verdict = "APPROVED":
    → Proceed to Phase 4 (Optimization)
    
ELSE IF verdict = "NEEDS REVISION":
    → Extract QA feedback
    → Return to Phase 2 with corrections
    → Iteration counter++
    → If iterations > 2: escalate to user
    
ELSE IF verdict = "REJECTED":
    → Extract QA feedback
    → Return to Phase 1 with new angle
    → Escalate to user for confirmation
```

**Critical Note**: 
This phase uses the existing `content-qa-agent` with its full evaluation framework. No modifications to the QA agent are required.

**Output to Next Phase**: 
- QA-approved draft
- QA suggestions for optimization

---

### Phase 4: Optimization

**Objective**: Polish the QA-approved draft

**Invocation**:
```
Use the content-optimizer subagent to polish this QA-approved post:

DRAFT:
[PASTE QA-APPROVED DRAFT]

QA SUGGESTIONS:
[PASTE RELEVANT QA FEEDBACK]

Focus on:
- Readability enhancement
- Flow optimization  
- Impact amplification
```

**Wait Condition**: Final optimized post received

**Quality Check**:
- ✓ Optimization summary provided?
- ✓ Readability metrics included?
- ✓ Character count acceptable?

**Output to User**: Final post with complete summary

---

### Phase 5: Delivery

**Objective**: Present final post to user

**Delivery Format**:
```
✅ FINAL LINKEDIN POST
═══════════════════

[OPTIMIZED POST TEXT]

═══════════════════

📊 PIPELINE SUMMARY

Research Phase:
• Angle: [key angle found]
• Insights: [count] core insights identified
• Examples: [count] concrete examples

Writing Phase:
• Draft length: [word count] words ([character count] chars)
• Hook: "[hook used]"
• Alternative hooks: [count] provided

QA Phase:
• Verdict: [APPROVED/NEEDS REVISION/REJECTED]
• Engagement potential: [rating]
• Key feedback: [1-2 most important points]
• Iterations: [number if > 1]

Optimization Phase:
• Character change: [before] → [after]
• Key improvements: [top 2-3 changes]
• Read time: [seconds]

Ready to publish! 🚀

[Optional: Suggest 3-5 relevant hashtags]
```

---

## Error Handling

### Subagent Invocation Failure

**Symptoms**: Subagent doesn't respond or returns error

**Actions**:
1. Report specific failure to user
2. Suggest manual invocation for debugging
3. Offer to restart from that phase

**Example**:
```
⚠️ Research phase failed to complete.

Error: content-researcher did not return expected format

Options:
1. Retry with more specific topic
2. Manually invoke: "Use content-researcher to explore [topic]"
3. Skip to writing with your own brief
```

---

### QA Loop Exceeds Limit

**Trigger**: QA rejects draft 2+ times

**Actions**:
1. Present QA feedback to user
2. Ask for guidance:
   - Change topic angle?
   - Provide example post?
   - Override and proceed?

**Example**:
```
⚠️ QA has rejected the draft twice.

Feedback patterns:
- Hook lacks specificity
- Examples are too generic
- No clear takeaway

Recommendation: Change topic angle or provide example post

Continue anyway? [Y/N]
```

---

### Phase Timeout

**Trigger**: Subagent takes unusually long

**Actions**:
1. Inform user of delay
2. Suggest checking subagent directly
3. Offer to restart phase

---

## Quality Gates Summary

### Gate 1: Research Quality (Soft)
- Check: Insights are specific
- Fail action: Request topic refinement

### Gate 2: Draft Completeness (Soft)  
- Check: All required elements present
- Fail action: Re-invoke writer

### Gate 3: QA Approval (HARD)
- Check: Verdict = APPROVED
- Fail action: Loop or escalate
- **This is the critical gate**

### Gate 4: Optimization Verification (Soft)
- Check: Metrics improved
- Fail action: Rare, usually acceptable as-is

---

## User Interaction Guidelines

### When to Ask User

**ASK** when:
- Topic is too broad (initialization)
- QA rejects 2+ times (escalation)
- Multiple angles viable (disambiguation)
- Character limit concerns (length)

**DON'T ASK** when:
- Normal pipeline execution
- Minor quality iterations
- Standard parameter decisions

### Communication Style

**To User**:
- Concise status updates
- Clear phase indicators (1/4, 2/4, etc.)
- Show key decisions
- Celebrate completion

**To Subagents**:
- Complete context every time
- Specific instructions
- Clear format expectations
- All necessary data

---

## Success Criteria

Pipeline succeeds when:
- ✅ All 4 phases execute
- ✅ QA approves the content  
- ✅ Final post meets quality standards
- ✅ User is satisfied

---

## Integration with Existing QA Agent

### Critical Notes

1. **No QA Agent Modifications Required**
   - Use existing content-qa-agent as-is
   - Leverage existing evaluation-criteria.md
   - Respect existing verdict format

2. **QA Agent is the Authority**
   - Its verdict is final for the pipeline
   - APPROVED = proceed
   - NEEDS REVISION = loop to writer
   - REJECTED = loop to research

3. **Pass Complete Drafts**
   - QA agent expects full post draft
   - Include all metadata from writer
   - Don't summarize or truncate

4. **Respect QA Output Format**
   - Use whatever format QA agent returns
   - Extract verdict from structured output
   - Pass optimization suggestions forward

---

## Example Full Execution

### User Input
```
/content-pipeline "Why subagents prevent context bloat"
```

### Orchestrator Execution
```
Initializing content pipeline...

Target: LinkedIn post about subagent context management
Length: Standard (250-300 words)
Audience: AI GTM Engineering

═══ Phase 1/4: Research ═══

[Invokes content-researcher]
✓ Research complete (32s)

Key findings:
• Angle: Context isolation as reliability strategy
• Insights: 3 identified (context bloat, isolation pattern, error reduction)
• Examples: 2 concrete scenarios provided

═══ Phase 2/4: Writing ═══

[Invokes content-writer with research brief]
✓ Draft complete (24s)

Draft stats:
• Length: 287 words (1,432 characters)
• Hook: "Your AI agent's context window is bleeding tokens..."
• Structure: Problem → Solution → Example → Takeaway

═══ Phase 3/4: Quality Review ═══

[Invokes content-qa-agent with draft]
✓ QA review complete (18s)

QA Verdict: APPROVED ✓
• Hook strength: 9/10
• Engagement potential: HIGH
• Structural quality: Excellent
• Minor polish recommended: 2 areas flagged

[Pipeline proceeds to optimization]

═══ Phase 4/4: Optimization ═══

[Invokes content-optimizer with QA-approved draft + feedback]
✓ Optimization complete (12s)

Final stats:
• Length: 274 words (1,398 characters)
• Avg sentence: 17 words
• Read time: 38 seconds

✅ FINAL LINKEDIN POST
═══════════════════

[Final optimized post displayed]

═══════════════════

Total pipeline time: 86 seconds
Quality gate status: APPROVED on first pass
Ready to publish! 🚀
```

---

## Maintenance & Updates

### Version History
- v1.0 (2026-03-15): Initial orchestrator

### Dependencies
- content-researcher v1.0+
- content-writer v1.0+
- content-qa-agent (existing, any version)
- content-optimizer v1.0+

### Future Enhancements
- Parallel research exploration
- A/B testing variants
- Engagement prediction
- Automated publishing

---

**Status**: Production ready  
**QA Integration**: Compatible with existing content-qa-agent  
**Modification Required**: None to existing agents
