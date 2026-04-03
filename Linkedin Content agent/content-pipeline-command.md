---
description: Generate a polished LinkedIn post through a multi-subagent workflow (Research → Write → QA → Optimize)
argument-hint: "<topic for LinkedIn post>"
---

# AI GTM Content Pipeline

Transform a topic into a publication-ready LinkedIn post using a specialized multi-subagent workflow.

## Workflow Architecture

```
Input: Topic
    ↓
[Research Agent] → Explores ideas, gathers insights
    ↓
[Writing Agent] → Drafts the LinkedIn post
    ↓
[QA Agent] → Reviews clarity and structure
    ↓
[Optimization Agent] → Improves readability and flow
    ↓
Output: Final LinkedIn Post
```

## Mission

Execute a sequential multi-subagent workflow where each agent:
- Operates in its own context window
- Focuses on one specialized responsibility
- Passes curated output to the next agent
- Maintains quality through the pipeline

## Execution Steps

### Step 1: Topic Intake
Receive the topic and confirm understanding.
Ask clarifying questions if needed:
- Target audience specifics?
- Desired post length?
- Key message priority?
- Any examples to include/avoid?

### Step 2: Research Phase
Invoke the **content-researcher** subagent:

```
Use the content-researcher subagent to explore the topic: [TOPIC]

Research focus:
- Find the most compelling angle for AI GTM audience
- Gather 3-5 concrete insights
- Identify relevant examples
- Suggest strong hooks
```

**Wait for research results before proceeding.**

### Step 3: Writing Phase
Invoke the **content-writer** subagent with research output:

```
Use the content-writer subagent to draft a LinkedIn post.

Input from research:
[Paste research brief]

Requirements:
- Follow LinkedIn post structure
- Use conversational but substantive tone
- Keep under 1,500 characters
- Include specific examples from research
```

**Wait for draft before proceeding.**

### Step 4: QA Phase
Invoke the **content-qa** subagent with the draft:

```
Use the content-qa subagent to review this post:

[Paste draft]

Focus areas:
- Hook strength
- Structural flow
- Clarity issues
- Engagement potential
```

**If QA verdict is "REJECTED" or "NEEDS REVISION":**
- Loop back to Writing Phase with QA feedback
- Don't proceed until QA approves

**If QA verdict is "APPROVED":**
- Proceed to optimization

### Step 5: Optimization Phase
Invoke the **content-optimizer** subagent with QA-approved draft:

```
Use the content-optimizer subagent to polish this QA-approved post:

[Paste approved draft]

QA feedback to address:
[Paste QA suggestions]

Focus on:
- Readability enhancement
- Flow optimization
- Impact amplification
```

### Step 6: Final Delivery
Present the final optimized post to the user with:

```
✅ FINAL LINKEDIN POST
==================

[Optimized post]

---
PIPELINE SUMMARY:
Research: [1-line summary of angle found]
Writing: [Character count and hook used]
QA Verdict: [Verdict + key feedback]
Optimization: [Key improvements made]

Ready to publish!

[Optional: Suggest 3-5 relevant hashtags]
```

## Quality Gates

**Gate 1 (After Research):**
- Insights are specific, not generic
- Examples are concrete
- Angle is clear

**Gate 2 (After Writing):**
- Hook is attention-grabbing
- Structure follows best practices
- Value is front-loaded

**Gate 3 (After QA):**
- Must have "APPROVED" verdict
- No critical issues remain
- Engagement potential is Medium or High

**Gate 4 (After Optimization):**
- Readability metrics are met
- Flow is natural
- Character count is optimal

## Error Handling

If a subagent returns unexpected output:
1. Review the output
2. Provide corrective guidance
3. Re-invoke the subagent with clearer instructions

If QA rejects twice:
1. Report to user
2. Suggest rethinking the topic angle
3. Offer to restart from Research phase

## Communication Guidelines

**To User:**
- Keep them informed at each phase
- Show key decisions and outputs
- Ask for approval on major direction changes

**To Subagents:**
- Be specific in prompts
- Include all necessary context
- Reference previous phase outputs clearly

## Success Criteria

The pipeline succeeds when:
- ✅ All four agents execute successfully
- ✅ QA approves the content
- ✅ Final post meets quality standards
- ✅ User is satisfied with output

## Example Execution

```
User: "Create a post about multi-agent workflows"

You:
1. "Got it. Creating a LinkedIn post about multi-agent workflows 
   for AI GTM Engineering audience. Standard length (150-300 words)?"

2. [User confirms]

3. "Phase 1/4: Research..."
   [Invoke content-researcher]

4. "Research complete. Found 3 key insights:
   - [Insight 1]
   - [Insight 2]
   - [Insight 3]
   
   Phase 2/4: Writing..."
   [Invoke content-writer]

5. "Draft complete (287 words). 
   Phase 3/4: Quality review..."
   [Invoke content-qa]

6. "QA approved with minor polish suggestions.
   Phase 4/4: Final optimization..."
   [Invoke content-optimizer]

7. [Present final post with summary]
```

Remember: This is a **sequential pipeline**. Each agent must complete before the next begins. Context flows forward through the chain. Quality gates prevent bad content from advancing.
