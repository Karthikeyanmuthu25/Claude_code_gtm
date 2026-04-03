# Content QA Agent - Integration Guide

**Quick Start:** 30 seconds to first review  
**Platform:** Claude Code (VS Code extension)  
**Author:** Karthikeyan

---

## 🚀 QUICK START

### Installation
1. Place this folder in `.claude/agents/content-qa/`
2. Restart Claude Code (if running)
3. Test: `@content-qa review this: [paste content]`

### First Review (30 seconds)
```
@content-qa review this LinkedIn post:

AI is changing GTM. Here's what you need to know.

Companies are using AI for lead qualification, email personalization, and more.

Thoughts?
```

**You'll get:** Structured review with score, feedback, and revised version.

---

## 📋 USAGE PATTERNS

### Pattern 1: Simple Review
```
@content-qa review this:

[paste your content]
```

**Returns:** Full review using template.md

---

### Pattern 2: Specific Content Type
```
@content-qa review this email:

Subject: AI qualification system demo
Body: [email content]
```

**Why specify:** Agent adjusts criteria (email vs LinkedIn have different best practices)

---

### Pattern 3: Batch Review
```
@content-qa compare these 3 posts and tell me which is strongest:

Post A: [content]
Post B: [content]
Post C: [content]
```

**Returns:** Individual scores + comparative analysis

---

### Pattern 4: Targeted Feedback
```
@content-qa focus on the hook only:

[paste content]

Is this hook strong enough for AI infrastructure audience?
```

**Returns:** Deep-dive on hook analysis only

---

### Pattern 5: Quick Score (No Full Review)
```
@content-qa quick score:

[paste content]
```

**Returns:** Just the X/10 score with one-sentence reasoning

---

## 🎯 USE CASES

### Use Case 1: Pre-Publish LinkedIn Post
**Workflow:**
1. Draft post in notes app
2. Paste into Claude Code
3. Tag `@content-qa`
4. Review feedback
5. Implement fixes
6. Re-review if score <7
7. Publish when 7+

**Time:** 5-15 minutes depending on score

---

### Use Case 2: Email Campaign Review
**Workflow:**
1. Draft email (subject + body)
2. Tag `@content-qa review this email:`
3. Check subject line (hook) score
4. Check CTA clarity
5. Verify technical accuracy
6. Revise and re-review

**Time:** 10-20 minutes

---

### Use Case 3: Blog Post Polish
**Workflow:**
1. Write draft post
2. Review intro (hook) separately
3. Review full post for flow
4. Check technical claims
5. Strengthen CTA
6. Final review before publish

**Time:** 30-60 minutes

---

### Use Case 4: A/B Test Content
**Workflow:**
```
@content-qa compare these 2 hooks:

Hook A: "Day 23/90: Built AI qualification agent."
Hook B: "I automated lead scoring using RAG. Here's how."

Which is stronger for AI infrastructure audience?
```

**Use:** Test variations before committing

---

### Use Case 5: Learning/Improvement
**Workflow:**
1. Review last 10 posts with agent
2. Identify patterns in weak scores
3. Practice: Rewrite weak elements
4. Compare: Original vs revised scores
5. Iterate: Improve based on feedback

**Goal:** Train yourself to write better first drafts

---

## 🔧 INTEGRATION OPTIONS

### Option 1: Direct in Claude Code (Recommended)
```
# In any file
@content-qa review this: [content]
```

**Pros:** Instant, inline, no context switching

---

### Option 2: Workflow Automation (n8n)
```
Trigger: New post draft saved
  ↓
Node: Call Claude Code agent
  ↓
Node: Parse review JSON
  ↓
Action: If score <7, alert for revision
```

**Pros:** Automatic quality gate

---

### Option 3: Pre-Publish Checklist
```markdown
Before Publishing:
- [ ] @content-qa score ≥7
- [ ] Hook score ≥2/3
- [ ] CTA is clear
- [ ] No technical errors
- [ ] Typo check
```

**Pros:** Forces quality standard

---

## 📊 INTERPRETING RESULTS

### Reading the Score

**9-10/10:** 
- Meaning: Exceptional quality
- Action: Publish immediately
- Confidence: High

**7-8/10:**
- Meaning: Strong, minor issues
- Action: Quick fixes (5-10 min)
- Confidence: Medium-high

**5-6/10:**
- Meaning: Decent bones, needs work
- Action: Restructure (15-30 min)
- Confidence: Medium

**3-4/10:**
- Meaning: Weak, multiple issues
- Action: Major rewrite (1+ hour)
- Confidence: Low

**0-2/10:**
- Meaning: Fundamentally flawed
- Action: Start over with new angle
- Confidence: Very low

---

### Focus on Lowest Score

If overall score is 6/10:
- Hook: 3/3 ✅
- Flow: 2/3 ⚠️
- CTA: 1/2 ⚠️
- Technical: 0/2 ❌

**Priority:** Fix technical accuracy first (biggest gap), then CTA, then flow.

---

### Using Revised Version

**If provided (score <7):**
- Don't copy/paste blindly
- Study the changes
- Understand WHY each change was made
- Apply principles to your own voice
- Use as reference, not replacement

---

## 🎓 LEARNING FROM REVIEWS

### Track Your Patterns

**Create a log:**
```markdown
# My Content QA Log

## Week 1
Post 1: 5/10 (Weak hook, generic CTA)
Post 2: 7/10 (Better hook, still generic CTA)
Post 3: 8/10 (Strong hook, improved CTA)

Pattern: My CTAs are consistently weak
Fix: Study CTA examples in evaluation-criteria.md
```

---

### Common Improvement Paths

**Weak Hook → Strong Hook (2-3 weeks):**
1. Review 10 high-scoring hooks
2. Identify patterns (stats, contrarian, story)
3. Practice: Write 5 hooks per concept
4. Test: Score each, keep best
5. Repeat until consistently 3/3

**Poor Flow → Good Flow (3-4 weeks):**
1. Study PAS/BAB/SIA structures
2. Outline before writing
3. Use formatting (line breaks, bullets)
4. Read aloud (catch awkward transitions)
5. Review flow score trend

**Weak CTA → Strong CTA (1-2 weeks):**
1. Study CTA examples (evaluation-criteria.md)
2. Formula: Action + Reason + Ease
3. Test: "Follow because [specific value]"
4. Avoid: "Thoughts?" and generic asks
5. Track CTA scores

---

## 🔍 ADVANCED USAGE

### Custom Evaluation Criteria

**Modify for your audience:**
```
@content-qa use these additional criteria:

Audience: Series A-C AI infrastructure founders
Criteria: Mentions specific tools (Pinecone, LangChain, etc)
Tone: Technical but accessible

[paste content]
```

---

### Comparative Analysis

**Find what works:**
```
@content-qa analyze my last 5 posts and tell me:
- Which scored highest and why?
- Common patterns in low scorers?
- What should I focus on improving?

Post 1: [content] | Score: 6/10
Post 2: [content] | Score: 8/10
Post 3: [content] | Score: 5/10
Post 4: [content] | Score: 9/10
Post 5: [content] | Score: 7/10
```

---

### Voice Preservation

**If revised versions don't match your voice:**
```
@content-qa the revised version sounds too formal. Can you revise again but keep my casual, builder voice? Use:
- Short sentences
- "I" statements
- Tech specifics
- No corporate speak

Original: [content]
```

---

## ⚙️ CONFIGURATION

### Adjusting Strictness

**Lenient Mode (For Drafts):**
```
@content-qa review this draft (be lenient, focus on big issues):

[content]
```

**Strict Mode (For Final Review):**
```
@content-qa final review (be strict, catch everything):

[content]
```

---

### Content Type Defaults

**LinkedIn (Default):**
- Hook weight: High (LinkedIn = scroll-stopper required)
- Flow: Short paragraphs (2-4 lines)
- CTA: Engagement focused
- Length: 150-300 words ideal

**Email:**
```
@content-qa review this email:
```
- Hook = Subject line (scored separately)
- CTA: Single, clear action
- Flow: Skimmable sections
- Technical: High accuracy (professional context)

**Blog Post:**
```
@content-qa review this blog intro:
```
- Hook = Title + first paragraph
- Flow: Heading structure
- CTA: Multiple acceptable (mid, end)
- Technical: Citations required

---

## 🚨 TROUBLESHOOTING

### Issue: Agent doesn't respond
**Fix:** Ensure agent folder is in `.claude/agents/content-qa/`

### Issue: Review too generic
**Fix:** Provide more context:
```
@content-qa review this LinkedIn post for AI infrastructure builders (technical audience):

[content]
```

### Issue: Score seems harsh
**Response:** Request comparison:
```
Can you show me an example of 9/10 content on this topic?
```

### Issue: Revised version doesn't match voice
**Fix:** Specify voice guidelines:
```
Revise again using: short sentences, casual tone, specific numbers
```

---

## 📈 MEASURING IMPROVEMENT

### Track These Metrics

**Weekly:**
- Average score (target: upward trend)
- Hook score consistency (target: 2.5+/3)
- CTA score consistency (target: 1.5+/2)
- Technical accuracy (target: 2/2 always)

**Monthly:**
- Revision rate (target: decrease)
- First-draft score (target: increase to 7+)
- Publishing confidence (subjective: high)

**Example Tracking:**
```
Week 1: Avg 5.2/10 (4 posts, 3 needed revision)
Week 2: Avg 6.1/10 (5 posts, 2 needed revision)
Week 3: Avg 7.3/10 (5 posts, 1 needed revision)
Week 4: Avg 7.8/10 (6 posts, 0 needed revision)

Progress: 2.6 point improvement in 1 month
```

---

## 🎯 GOALS

### Short-Term (Week 1-4)
- [ ] Review all content before publishing
- [ ] Understand scoring rubric
- [ ] Identify personal weak areas
- [ ] Average score: 6+/10

### Medium-Term (Week 5-8)
- [ ] First drafts consistently 7+/10
- [ ] Hook scores consistently 2.5+/3
- [ ] Rarely need revised versions
- [ ] Average score: 7.5+/10

### Long-Term (Week 9-12)
- [ ] First drafts consistently 8+/10
- [ ] Rarely score below 7
- [ ] Can predict score before review
- [ ] Average score: 8+/10

---

## 💡 TIPS

### Before Writing
1. Read evaluation-criteria.md
2. Study high-scoring examples
3. Choose hook pattern first
4. Outline structure (PAS/BAB/SIA)

### While Writing
1. Keep evaluation criteria open
2. Self-score as you write
3. Check: "Would I stop scrolling for this hook?"
4. Test: "Is my CTA clear and compelling?"

### After Writing
1. Review with agent
2. If <7, implement all fixes
3. Re-review after changes
4. Only publish when 7+

### Over Time
1. Save all reviews (build reference library)
2. Study patterns in your high scorers
3. Avoid patterns in your low scorers
4. Teach others (teaching = deeper learning)

---

## 🔗 RELATED FILES

- **agent-instructions.md** - Agent behavior & rules
- **template.md** - Output format reference
- **evaluation-criteria.md** - Detailed scoring rubric
- **test-cases.md** - Example reviews with scores
- **QUICKSTART.md** - 60-second overview

---

## 📞 SUPPORT

**Issues:**
- Check agent-instructions.md for behavior
- Check evaluation-criteria.md for scoring
- Check test-cases.md for examples

**Questions:**
- "Why did my hook score low?" → See evaluation-criteria.md Hook section
- "What's a strong CTA?" → See evaluation-criteria.md CTA examples
- "How do I improve flow?" → See evaluation-criteria.md Flow patterns

---

**Ready to improve your content quality. Review everything before publishing.** ✅
