# Content QA Agent - Usage Examples

**Copy/paste these commands to try the agent**

---

## 🚀 BASIC USAGE

### Example 1: Review LinkedIn Post
```
@content-qa review this LinkedIn post:

Day 15/90: Built my first RAG system.

Used Pinecone for vector storage and Claude for reasoning. The system qualifies leads by retrieving my ICP criteria and scoring companies.

Cost: About $0.03 per lead.

Let me know if you want to see the architecture.
```

**Expected Output:**
- Score: ~7/10
- Hook: Good (progress + specific tech)
- Flow: Decent (needs formatting)
- CTA: Weak ("let me know" is passive)
- Revised version provided

---

### Example 2: Review Email Subject
```
@content-qa review this email subject line:

"Introducing our new AI-powered lead qualification system"

Target audience: B2B SaaS founders
```

**Expected Output:**
- Score: ~4/10 (subject only)
- Issue: "Introducing" is weak, no benefit stated
- Suggestion: "91% qualification accuracy in 30 seconds (vs 2 hours manual)"

---

### Example 3: Quick Score
```
@content-qa quick score this:

I tested 3 vector databases. Pinecone beat Weaviate by 40ms. Here's the benchmark.

Follow for the complete results tomorrow.
```

**Expected Output:**
```
Score: 8/10

Strong hook (specific test, concrete result), good CTA (preview value). Minor: Could add "why 40ms matters" context.
```

---

## 🔄 COMPARISON USAGE

### Example 4: Compare Two Hooks
```
@content-qa which hook is stronger for AI infrastructure audience:

Hook A: "Built a RAG system this week."
Hook B: "Day 15/90: RAG system scored 94% accuracy. Generic tools hit 73%."

Explain why.
```

**Expected Output:**
```
Hook B is significantly stronger (3/3 vs 2/3).

Why:
- Progress indicator (Day 15/90) builds trust
- Specific metrics (94% vs 73%) create curiosity
- Comparison shows advantage
- "Generic tools" implies your solution is custom/better

Hook A is vague:
- "This week" lacks commitment signal
- No result teased
- No curiosity gap
```

---

### Example 5: Compare Full Posts
```
@content-qa compare these posts and rank them:

Post 1:
AI is changing GTM. Companies use it for lead qualification and personalization. Thoughts?

Post 2:
Built AI qualification agent. Uses RAG to score leads against my ICP. 91% accuracy. Architecture in comments.

Post 3:
Day 23/90: My RAG system failed. The error: empty chunks. The fix: validation before embedding. Result: zero errors in 48 hours.

Which would perform best and why?
```

**Expected Output:**
```
Ranking: Post 3 (9/10) > Post 2 (7/10) > Post 1 (2/10)

Post 3 wins because:
- Authentic failure story (relatable)
- Specific problem + solution
- Proof metrics (48 hours)
- Progress tracking (Day 23/90)

Post 2 is solid but:
- No story element
- Good proof but less engaging

Post 1 fails:
- Generic hook everyone uses
- No specifics
- Weakest CTA ("Thoughts?")
```

---

## 🎯 TARGETED FEEDBACK

### Example 6: Focus on Specific Element
```
@content-qa analyze just the hook:

"I spent 3 months building an AI agent for GTM qualification."

Is this strong enough? If not, what would make it stronger?
```

**Expected Output:**
```
Hook Score: 2/3 (decent but not strong)

What works:
- Timeframe (3 months) shows commitment
- Specific (AI agent for GTM qualification)

What's missing:
- No result teased (what happened after 3 months?)
- No curiosity gap (why should I care?)

Stronger versions:

Option A (Result):
"Spent 3 months building AI qualification agent. Result: 91% accuracy vs 73% for $800/month tools."

Option B (Failure):
"My AI agent took 3 months to build. It failed 5 times. Here's what worked."

Option C (Progress):
"Day 90/90: Shipped my AI qualification agent. 3 months, 5 rewrites, 91% accuracy. The journey:"
```

---

### Example 7: CTA Improvement
```
@content-qa suggest 3 better CTAs for this post:

[Post content about building RAG system]

Current CTA: "Let me know your thoughts."
```

**Expected Output:**
```
Current CTA: 0/2 (very weak)

Better Options:

1. Engagement CTA (Best for authority):
"What's your biggest RAG challenge? Drop it below—I'll analyze your setup."
- Specific question
- Personal value offer
- Encourages detailed responses

2. Conversion CTA (Best for leads):
"Built a free RAG calculator. Estimates cost and accuracy for your use case. Link in comments 👇"
- Clear value
- Specific tool
- Easy action

3. Follow CTA (Best for growth):
"Follow for the complete build breakdown. Tomorrow: Architecture + code walkthrough."
- Preview specific value
- Creates return intent
- Audience targeting implicit
```

---

## 📚 BATCH OPERATIONS

### Example 8: Analyze Content Pattern
```
@content-qa analyze my last 5 LinkedIn posts. Tell me:

1. Common patterns in high scorers vs low scorers
2. My weakest category (hook/flow/CTA)
3. What I should focus on improving

Post 1: [content] - Score: 6/10
Post 2: [content] - Score: 8/10
Post 3: [content] - Score: 5/10
Post 4: [content] - Score: 9/10
Post 5: [content] - Score: 7/10
```

**Expected Output:**
```
PATTERN ANALYSIS:

High Scorers (8-9/10) share:
✓ Specific metrics in hook (Post 2, Post 4)
✓ Progress tracking (Day X/90)
✓ Scannable formatting (bullets, arrows)
✓ Active CTAs with value preview

Low Scorers (5-6/10) suffer from:
❌ Generic hooks (Post 3: "AI is important")
❌ Wall of text (Post 1)
❌ Passive CTAs (Post 3: "Thoughts?")

YOUR WEAKEST CATEGORY: CTAs (Average: 0.8/2)
- You use "Let me know" 3 times
- "Thoughts?" appears twice
- Only Post 4 has strong CTA

IMPROVEMENT FOCUS:

Priority 1: Fix CTAs (Easy wins)
- Never use "Thoughts?" again
- Formula: Action + Reason + Preview
- Example: "Follow for [specific value]. Tomorrow: [topic]"

Priority 2: Strengthen Hooks
- Add result/metric to hook
- Test: "I [action] [metric]. Here's [insight]"

Priority 3: Format Flow
- Break paragraphs (2-4 lines max)
- Use arrows/bullets for lists
- Add line breaks every 2-3 sentences
```

---

## 🔧 ADVANCED USAGE

### Example 9: Custom Scoring Criteria
```
@content-qa review using these additional criteria:

Standard criteria: Hook, Flow, CTA, Technical

Additional for my audience (AI infrastructure founders):
- Mentions specific tools (Pinecone, LangChain, Claude, etc)
- Includes code or architecture
- Shows production experience (not just tutorials)

Content:
[paste content]
```

**Expected Output:**
```
STANDARD SCORE: 7/10
Hook: 2/3
Flow: 3/3
CTA: 1/2
Technical: 2/2

ADDITIONAL CRITERIA FOR AI FOUNDERS:

Tool Specificity: ✅ (Pinecone, Claude mentioned)
Code/Architecture: ⚠️ (Architecture described but no visual/code)
Production Experience: ✅ (48-hour stability metric shows production)

RECOMMENDATION:
Add code snippet or architecture diagram to hit 9/10 for your specific audience.
```

---

### Example 10: Voice Preservation
```
@content-qa the revised version sounds too formal for my style.

Revise again but keep my casual, builder voice:
- Short sentences (10 words max)
- "I" statements (not "one should")
- Tech specifics (tool names, metrics)
- No corporate speak ("leverage", "utilize", etc)

Original: [content]
```

**Expected Output:**
```
REVISED (Casual Builder Voice):

Day 23/90: RAG system crashed.

Error: Empty chunks.
Cause: Bad chunking logic.
Fix: Skip chunks <50 tokens.

Result: Zero crashes. 48 hours stable. 1,247 queries.

Tomorrow: Multi-LLM setup.

Follow if you build AI systems.

[This version]:
✓ Short sentences (8 words average)
✓ "I" voice implied (Day 23 = my journey)
✓ Specific tech (RAG, chunking, tokens)
✓ No corporate jargon
✓ Same 9/10 score, different voice
```

---

## 📧 CONTENT TYPE VARIATIONS

### Example 11: Email Review
```
@content-qa review this email:

Subject: Your lead qualification just got 10x faster

Body:
Hi [First Name],

Most companies waste 2 hours/day on manual lead qualification.

I built an AI system that does it in 30 seconds.

How it works:
- Stores YOUR ICP in vector database
- Retrieves YOUR criteria for each lead
- Claude analyzes and scores (0-100)

Result: Only see qualified leads. Zero time wasted.

Cost: $0.03 per lead (vs 2 hours of salary)

Want a demo? Reply to this email.

[Name]
```

**Expected Output:**
```
EMAIL SCORE: 8/10

Subject Line: 3/3 ✅
- Specific benefit (10x faster)
- Addresses recipient (your)
- Creates urgency (just)

Body Hook: 2/3
- Good problem (2 hours wasted)
- Could be stronger with stat or story

Flow: 3/3 ✅
- Clear structure: Problem → Solution → How → Result → CTA
- Scannable bullets
- Good pacing

CTA: 2/2 ✅
- Clear action (reply)
- Low friction
- Connected to content

RECOMMENDATIONS:
Minor: Strengthen body hook with specific example
"[Company X] spent 2 hours/day qualifying. Now: 30 seconds."

Otherwise excellent. Send as-is or with minor tweak.
```

---

### Example 12: Blog Post Intro
```
@content-qa review this blog post introduction:

Title: "How to Build a Production RAG System in 2026"

Intro:
RAG (Retrieval-Augmented Generation) has become the standard for building AI systems that need access to specific knowledge. But most RAG tutorials show toy examples, not production systems.

In this guide, I'll show you how to build a production-grade RAG system based on 90 days of building AI infrastructure systems.

You'll learn:
- Why most RAG systems fail in production
- The architecture we use for 1M+ queries/month
- Cost optimization strategies (from $800 to $40/month)
- Monitoring and debugging techniques

By the end, you'll have a complete blueprint for production RAG.
```

**Expected Output:**
```
BLOG INTRO SCORE: 7/10

Title: 2/3
✓ Clear topic (RAG production systems)
✓ Timely (2026)
⚠️ Could be more specific: "How We Built a RAG System Handling 1M Queries/Month for $40"

Hook (First Paragraph): 2/3
✓ Identifies problem (toy examples vs production)
✓ Positions value (production focus)
⚠️ Missing credibility signal (your experience)

Flow: 3/3 ✅
- Perfect structure: Problem → Promise → Preview → Outcome
- Scannable bullets (what you'll learn)
- Clear value proposition

CTA: N/A (intro only)

RECOMMENDATIONS:

Strengthen credibility in hook:
"After building 25+ RAG systems over 90 days (and breaking most of them), here's what actually works in production."

Alternative title:
"Production RAG: How We Went from $800/Month to $40/Month at 1M Queries"

Otherwise strong. Good intro for technical blog.
```

---

## 💡 WORKFLOW EXAMPLES

### Example 13: Pre-Publish Checklist
```
# My Publishing Checklist

Before posting to LinkedIn:

1. Run: @content-qa review this: [draft]
2. Check: Score ≥7/10?
3. If no: Implement all fixes
4. Re-run: @content-qa review this: [revised]
5. If yes: Check typos, then publish
6. Log: Track score in Google Sheets

Never publish if score <7.
```

---

### Example 14: A/B Testing Hook
```
# Hook Testing Workflow

For important posts, test 3 hook variations:

@content-qa compare these 3 hooks:

Hook A: "I tested 3 AI tools. Only 1 hit 90% accuracy."
Hook B: "Day 15/90: My AI qualification agent scored 94% vs generic 73%."
Hook C: "Spent $2,400 testing AI tools. Here's the $40 winner."

Rank them for AI infrastructure audience.

[Use highest-scoring hook for final post]
```

---

### Example 15: Weekly Batch Review
```
# Weekly Review Workflow

Every Sunday:

@content-qa analyze my week:

Monday: [post + score]
Tuesday: [post + score]
Wednesday: [post + score]
Thursday: [post + score]
Friday: [post + score]

Tell me:
1. Average score this week
2. Best performer (why it worked)
3. Worst performer (what to avoid)
4. One focus area for next week
```

---

## 🎯 LEARNING EXERCISES

### Exercise 1: Rewrite Challenge
```
@content-qa review this, then I'll try to improve it:

[weak post]

[After getting score]

Here's my revision: [revised post]

Did I improve? Score again and tell me if I correctly addressed the issues.
```

---

### Exercise 2: Pattern Recognition
```
@content-qa show me:

1. An example 9/10 hook using "Specific Result" pattern
2. An example 9/10 hook using "Contrarian Take" pattern
3. An example 9/10 hook using "Progress Update" pattern

For each, explain why it scores high.
```

---

### Exercise 3: Weakness Focus
```
@content-qa my CTAs consistently score low.

Review these 5 CTAs and explain what makes each weak:

1. "Thoughts?"
2. "Let me know what you think"
3. "Follow for more"
4. "Check out my profile"
5. "What do you think about this?"

Then show me 5 strong CTA examples for comparison.
```

---

## 🔍 DEBUGGING EXAMPLES

### Example 16: Disagreement with Score
```
@content-qa you scored my hook 1/3, but I think it's strong.

Hook: "AI is transforming how we do GTM"

Can you:
1. Explain exactly why it scored low
2. Show me a similar hook that scores 3/3
3. Show me what to change

I want to understand, not just accept the score.
```

**Expected Output:**
```
EXPLANATION OF 1/3 SCORE:

Why it's weak:
1. "AI is transforming" = Most overused opening on LinkedIn (thousands use daily)
2. Zero specificity (which AI? what transformation? whose GTM?)
3. No curiosity gap (everyone already knows "AI is changing things")
4. No value promise (what will reader learn?)

Compare to 3/3 hook on same topic:

Your hook (1/3):
"AI is transforming how we do GTM"

3/3 version:
"I replaced our $800/month GTM tool with a $40 AI agent. Same results, 20x cheaper."

Why 3/3 scores high:
✓ Specific (exact costs, specific tool type)
✓ Shocking comparison (20x cheaper)
✓ Concrete value (how to save money)
✓ Curiosity (how did they do it?)

What to change:
- Replace "AI is transforming" with specific result you achieved
- Add numbers/metrics (cost, accuracy, time saved)
- Make it about YOUR experience, not general trends

Does this explanation help you see why generic = low score?
```

---

## 📊 TRACKING EXAMPLES

### Example 17: Monthly Progress Review
```
@content-qa here are my scores from this month:

Week 1: 5.2, 6.1, 4.8, 7.2, 6.5 (Avg: 5.96)
Week 2: 6.3, 7.1, 5.9, 7.8, 6.7 (Avg: 6.76)
Week 3: 7.2, 8.1, 7.5, 6.9, 8.3 (Avg: 7.60)
Week 4: 8.2, 7.9, 8.5, 9.1, 8.0 (Avg: 8.34)

Analysis:
1. Am I improving at good pace?
2. What's working (week 4 vs week 1)?
3. What should I focus on next month?
```

---

**These examples show the full range of agent capabilities.**

**Start with basic usage, progress to advanced patterns as needed.**
