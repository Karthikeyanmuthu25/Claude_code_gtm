# Content QA Agent - Test Cases

**Purpose:** Reference examples showing agent in action  
**Use:** Understand expected behavior, calibrate judgment

---

## TEST CASE 1: Excellent LinkedIn Post (9/10)

### Input Content
```
Day 23/90: My RAG system failed in production.

The error: "IndexError: list index out of range"

The cause: Chunking strategy was creating empty chunks.

The fix:
→ Skip chunks <50 tokens
→ Remove whitespace-only chunks
→ Log all skipped chunks for review

Result: Zero errors in 48 hours, 1,247 successful queries.

Tomorrow: Multi-LLM consensus strategies.

Follow if you're building production AI systems. #Day23of90
```

### Expected Output
```markdown
## CONTENT SCORE: 9/10

**Content Type:** LinkedIn post  
**Target Audience:** AI Engineers building production systems  
**Word Count:** 67 words

---

## 🎯 HOOK ANALYSIS (3/3 points)

**Hook Text:** "Day 23/90: My RAG system failed in production."

**Pattern Used:** Story/Progress Update

### Strengths
- Progress indicator (Day 23/90) builds credibility and commitment
- "Failed in production" creates immediate curiosity (what went wrong?)
- Specific and technical (RAG system, not generic "AI")
- Relatable pain point (failures are universal)

### Issues
- None identified

### Recommendation
No changes needed - hook is exceptional. The combination of progress tracking + failure story + technical specificity is perfect for the target audience.

---

## 📊 FLOW ANALYSIS (3/3 points)

**Structure Pattern:** Problem-Agitate-Solution (PAS)

**Content Structure:**
```
Line 1: Hook (failure announced)
Line 3: Problem (specific error)
Line 5: Root cause (chunking issue)
Line 7-11: Solution (3-step fix, scannable format)
Line 13: Proof (48 hours, 1,247 queries)
Line 15: Preview (tomorrow's topic)
Line 17: CTA (follow)
```

### Strengths
- Perfect PAS structure progression
- Code-style formatting (→ bullets) makes technical solution instantly scannable
- Specific metrics provide proof (48 hours, 1,247 queries)
- Each line serves a purpose - zero wasted words
- Short paragraphs (1-2 lines each) maintain pace

### Issues
- None identified

### Recommendation
Flow is excellent. The progression from problem → cause → solution → proof is inevitable and clear. Formatting makes it highly scannable.

---

## 📣 CTA ANALYSIS (2/2 points)

**CTA Text:** "Follow if you're building production AI systems."

**CTA Type:** Engagement (Follow)

### Strengths
- Clear action (Follow)
- Audience targeting (building production AI)
- Relevant preview (tomorrow's topic: Multi-LLM consensus)
- Hashtag adds discoverability (#Day23of90)

### Issues
- None identified

### Recommendation
Strong CTA. Combines clear action with audience targeting and value preview. The "if you're building" qualifier attracts right audience.

---

## ✅ TECHNICAL ACCURACY (2/2 points)

**Technical Claims Made:**
1. "IndexError: list index out of range" - Python error
2. Chunking creates empty chunks
3. Fix: Skip chunks <50 tokens
4. Result: Zero errors in 48 hours

**Accuracy Assessment:**
- ✅ IndexError is correct Python error for this scenario
- ✅ Empty chunks from chunking strategy is realistic issue
- ✅ 50 token threshold is reasonable minimum
- ✅ Logging skipped chunks is best practice
- ✅ 48-hour stability + 1,247 queries is credible proof

### Issues Found
None. All technical claims are accurate and realistic.

---

## 📋 OVERALL ASSESSMENT

### What Works (Top 3 Strengths)
1. **Authentic failure story** - Vulnerability builds trust, shows real production experience
2. **Scannable technical solution** - Code-style formatting makes fix immediately understandable
3. **Specific proof metrics** - 48 hours + 1,247 queries validates the solution worked

### What Needs Work (Critical Issues)
None. This is publication-ready content.

### One-Sentence Summary
Exceptional technical post combining authentic failure story, clean solution presentation, and specific proof metrics - perfect for AI engineering audience.

---

## 🎬 PUBLISHING DECISION

**Recommendation:** ✅ **Publish Immediately** (9/10)

**Time to Publish:** Immediate (check for typos only)

**Why 9/10 (not 10/10):**
Could potentially add:
- Link to code/architecture (if shareable)
- Metric comparison (before vs after chunking fix)
- But these are "nice to have" not "must have"

---

## 📊 SCORE BREAKDOWN SUMMARY

```
╔════════════════════════════════════════╗
║  CONTENT QA SCORECARD                  ║
╠════════════════════════════════════════╣
║  Hook (0-3):              3/3  [███]   ║
║  Flow (0-3):              3/3  [███]   ║
║  CTA (0-2):               2/2  [██]    ║
║  Technical Accuracy (0-2): 2/2  [██]    ║
╠════════════════════════════════════════╣
║  TOTAL SCORE:             9/10         ║
╠════════════════════════════════════════╣
║  Status: PUBLISH IMMEDIATELY ✅        ║
╚════════════════════════════════════════╝
```

---

## 💡 LEARNING NOTES

**What to Remember for Next Time:**
- Failure stories + technical solutions = high engagement
- Code-style formatting (→ bullets) works well for technical content
- Specific metrics (not "it works better") provide proof
- Progress tracking (Day X/Y) builds commitment signal

**Pattern to Repeat:**
Problem (with error) → Cause → Solution (scannable) → Proof (numbers) → Preview
```

---

## TEST CASE 2: Weak Generic Post (2/10)

### Input Content
```
AI is revolutionizing GTM.

More and more companies are using AI for lead qualification, personalization, and analytics.

If you're not using AI yet, you're falling behind.

What do you think?
```

### Expected Output
```markdown
## CONTENT SCORE: 2/10

**Content Type:** LinkedIn post  
**Target Audience:** Unclear (generic business audience?)  
**Word Count:** 31 words

---

## 🎯 HOOK ANALYSIS (0/3 points)

**Hook Text:** "AI is revolutionizing GTM."

**Pattern Used:** Generic statement (not a proven pattern)

### Strengths
- None identified

### Issues
- **Most overused hook on LinkedIn** - Thousands of posts start exactly this way
- Generic to the point of meaningless - could apply to any industry/function
- No curiosity gap created - reader already knows "AI is changing things"
- No specific value promised
- No reason to keep reading (what will I learn that's new?)

### Recommendation
**Complete hook replacement needed.** Options:

**Option A (Specific Result):**
```
I tested 3 AI lead qualification tools. Only 1 hit 90% accuracy. Here's why.
```

**Option B (Contrarian):**
```
Stop paying $800/month for AI GTM tools. I built a $40 alternative.
```

**Option C (Personal Story):**
```
Day 30: My AI qualification system scored its first $50K deal. The setup:
```

---

## 📊 FLOW ANALYSIS (0/3 points)

**Structure Pattern:** None identifiable

**Content Structure:**
```
Line 1: Generic statement
Line 3: Vague generalization  
Line 5: Fear-based claim
Line 7: Weak question
```

### Strengths
- None identified

### Issues
- **No structure** - Three random statements about AI with no connection
- **No problem defined** - What specific GTM challenge does AI solve?
- **No solution presented** - Which AI tools? How to implement?
- **No proof or examples** - No data, no stories, no specifics
- **Wall of text** - No formatting, line breaks, or scannable elements
- Reads like ChatGPT default output (generic, corporate, no personality)

### Recommendation
**Complete restructure needed using PAS (Problem-Agitate-Solution):**

```
Problem: Lead qualification tools use generic scoring rules.
Agitate: This means your sales team wastes time on bad-fit leads.
Solution: I built an AI agent trained on MY exact ICP.
Proof: 91% accuracy vs 73% for generic tools.
How: Pinecone (vector DB) + Claude (reasoning) + MY ICP as training data.
Result: Sales only sees HOT leads now. Zero time wasted.
```

---

## 📣 CTA ANALYSIS (0/2 points)

**CTA Text:** "What do you think?"

**CTA Type:** Soft/Passive (weakest type)

### Strengths
- None identified

### Issues
- **Most overused, laziest CTA on LinkedIn**
- Provides no reason to engage (think about what specifically?)
- Not connected to content (there's no content to discuss)
- Passive voice suggests uncertainty about value
- No audience targeting

### Recommendation
**Replace with targeted CTA:**

```
✅ "Follow if you're building AI GTM systems. Tomorrow: Multi-LLM orchestration."
   - Clear action + audience targeting + value preview

✅ "What's your biggest AI qualification challenge? Comment below."
   - Specific question + engagement ask

✅ "Built a free ICP qualifier. Link in comments 👇"
   - Value offer + clear action
```

---

## ✅ TECHNICAL ACCURACY (2/2 points)

**Technical Claims Made:**
1. "AI is revolutionizing GTM" - Opinion statement
2. "Companies using AI for lead qualification, personalization, analytics" - General trend

**Accuracy Assessment:**
- ✅ No technically false claims
- ✅ Statements are too vague to be wrong
- ⚠️ But also too vague to be useful

### Issues Found
No factual errors, but no actual facts either. All statements are generic truisms.

**Note:** Technically accurate but informationally empty.

---

## 📋 OVERALL ASSESSMENT

### What Works (Top 3 Strengths)
1. No typos or grammatical errors
2. Technically accurate (though vague)
3. [Cannot identify a third strength]

### What Needs Work (Critical Issues)
1. **Generic hook** - Most overused opening on LinkedIn, provides zero curiosity
2. **No structure or flow** - Random statements with no coherent narrative
3. **Weak CTA** - "What do you think?" is the laziest possible engagement ask
4. **No specifics** - No examples, no data, no tools, no proof, no personality
5. **No value** - After reading, audience learned nothing actionable

### One-Sentence Summary
Generic LinkedIn spam with no specific value, no examples, no personality - indistinguishable from thousands of other AI hype posts.

---

## 🎬 PUBLISHING DECISION

**Recommendation:** 🚫 **Start Over** (2/10)

**Time to Publish:** N/A - Do not publish this

**Why 2/10 (not 0/10):**
- No factual errors (2 points for technical accuracy)
- But no value either

**This is worse than unpublishable - it's damaging to your brand.** Generic AI hype posts signal:
- You have nothing unique to say
- You don't actually build with AI (just talk about it)
- You're jumping on trends, not creating value

---

## 🔧 REVISED VERSION

**Completely rewritten with specific value:**

```
I tested 3 AI lead qualification tools for our GTM stack.

Tool 1 (Clay): $800/month, 73% accuracy vs my manual scoring
Tool 2 (Custom RAG): $40/month, 91% accuracy  
Tool 3 (Generic ML): Free, 52% accuracy (worse than random)

The winner: Custom RAG.

Why it works:
→ Trained on MY exact ICP (not generic rules)
→ Retrieves MY criteria from vector DB
→ Claude analyzes with MY business logic

Cost: $40/month vs $800/month (20x cheaper)
Accuracy: 91% vs 73% (25% improvement)

Tomorrow: I'll share the complete architecture.

Follow if you're building AI GTM systems. #Day23of90
```

**Key Changes:**
- Hook: Generic claim → Specific test (3 tools)
- Flow: Random statements → Structured comparison
- Proof: None → Specific metrics ($40 vs $800, 91% vs 73%)
- CTA: "Thoughts?" → Targeted follow with value preview
- Voice: Corporate → Builder (I tested, I built, MY ICP)

**New Score: 8/10**

---

## 📊 SCORE BREAKDOWN SUMMARY

```
╔════════════════════════════════════════╗
║  CONTENT QA SCORECARD                  ║
╠════════════════════════════════════════╣
║  Hook (0-3):              0/3  [░░░]   ║
║  Flow (0-3):              0/3  [░░░]   ║
║  CTA (0-2):               0/2  [░░]    ║
║  Technical Accuracy (0-2): 2/2  [██]    ║
╠════════════════════════════════════════╣
║  TOTAL SCORE:             2/10         ║
╠════════════════════════════════════════╣
║  Status: DO NOT PUBLISH 🚫            ║
╚════════════════════════════════════════╝
```

---

## 💡 LEARNING NOTES

**What NOT to do:**
- Never start with "AI is changing [industry]"
- Never end with "Thoughts?" or "What do you think?"
- Never post generic statements without specific examples
- Never write like ChatGPT (corporate, vague, hype-y)

**What TO do instead:**
- Specific tests, experiments, results
- Concrete numbers, tools, architectures
- Personal experience (I built, I tested, I failed)
- Clear value preview in CTA
```

---

## TEST CASE 3: Good Post Needing Minor Fixes (7/10)

### Input Content
```
Built a RAG system for ICP qualification this week.

The system works by storing your ICP criteria in a vector database. When a new lead comes in, it retrieves relevant criteria and Claude scores them against your requirements.

Much better than generic lead scoring because it uses your specific criteria instead of generic rules.

Built with Pinecone and Claude API. About $0.03 per lead to run.

Let me know if you want to learn more.
```

### Expected Output
```markdown
## CONTENT SCORE: 7/10

**Content Type:** LinkedIn post  
**Target Audience:** AI/GTM builders  
**Word Count:** 67 words

---

## 🎯 HOOK ANALYSIS (2/3 points)

**Hook Text:** "Built a RAG system for ICP qualification this week."

**Pattern Used:** Accomplishment/Build announcement

### Strengths
- Specific technology (RAG system, not just "AI")
- Clear use case (ICP qualification)
- Action-oriented ("Built" shows execution)
- Timeframe provides context (this week)

### Issues
- **No result teased** - What happened after you built it? What did you learn?
- Missing curiosity gap - Why should reader care about YOUR RAG system?
- "This week" is recent but doesn't signal ongoing commitment like "Day X/90"

### Recommendation
**Add result or learning:**

**Option A:**
```
Built a RAG system for ICP qualification. Result: 91% accuracy vs 73% for generic tools.
```

**Option B:**
```
Built a RAG system for ICP qualification. It failed 3 times before working. Here's why.
```

**Option C:**
```
Day 15/90: Built a RAG-powered ICP qualification agent. Scored first lead at 94/100 (HOT).
```

---

## 📊 FLOW ANALYSIS (2/3 points)

**Structure Pattern:** Explanation-based (What it is → How it works → Why it's better)

**Content Structure:**
```
Line 1: Hook (what I built)
Line 3-4: How it works (technical explanation)
Line 6: Benefit (better than generic)
Line 8: Tech stack + cost
Line 10: Soft CTA
```

### Strengths
- Logical progression (what → how → why → specs)
- Technical detail (Pinecone, Claude, cost)
- Clear benefit statement

### Issues
- **Paragraph 2 is wall of text** - Needs line breaks for scannability
- **Technical explanation is dense** - Could use formatting (bullets, arrows)
- **"About $0.03"** is vague - Be exact or provide range
- Missing proof/validation - Did you test it? What were results?

### Recommendation
**Break up paragraph 2 and add formatting:**

```
The system:
→ Stores YOUR ICP criteria in vector DB (Pinecone)
→ Retrieves relevant criteria for each lead
→ Claude scores lead against YOUR requirements

Not generic rules. YOUR exact criteria.

Cost: $0.027-0.031 per lead (Claude + Pinecone)
Accuracy: 91% vs manual scoring (tested on 100 leads)
```

---

## 📣 CTA ANALYSIS (1/2 points)

**CTA Text:** "Let me know if you want to learn more."

**CTA Type:** Soft/Passive

### Strengths
- Invites engagement
- Implies more detail available

### Issues
- **Passive voice** - "Let me know" is weak
- **Vague ask** - Learn more about what specifically?
- **No reason WHY to reach out** - What will they get?
- Not targeted to audience

### Recommendation
**Make CTA active and specific:**

**Option A (Lead gen):**
```
Built a free ICP scorer. Link in comments 👇
```

**Option B (Engagement):**
```
What's your biggest lead qualification challenge? Drop it below.
```

**Option C (Follow):**
```
Follow for the complete build breakdown. Tomorrow: Architecture + code walkthrough.
```

---

## ✅ TECHNICAL ACCURACY (2/2 points)

**Technical Claims Made:**
1. RAG system for ICP qualification
2. Vector database storage (Pinecone)
3. Claude for scoring
4. $0.03 per lead cost

**Accuracy Assessment:**
- ✅ RAG for ICP matching is valid use case
- ✅ Vector DB (Pinecone) correctly used for criteria storage
- ✅ Claude for analysis is appropriate
- ✅ $0.03 per lead is realistic (Claude API ~$0.02 + Pinecone ~$0.01)

### Issues Found
None. Technical approach is sound and costs are accurate.

---

## 📋 OVERALL ASSESSMENT

### What Works (Top 3 Strengths)
1. **Technical credibility** - Specific tech stack (Pinecone, Claude, RAG) shows real implementation
2. **Cost transparency** - Sharing $0.03 per lead cost is valuable for audience
3. **Clear benefit** - "YOUR criteria vs generic rules" is strong differentiator

### What Needs Work (Critical Issues)
1. **Hook needs result** - Add outcome/learning to create curiosity
2. **Flow needs formatting** - Break up paragraph 2 with bullets/arrows for scannability
3. **CTA is passive** - Replace "Let me know" with specific, active ask

### One-Sentence Summary
Strong technical post with good bones, needs 10 minutes of polish to hit 8-9/10.

---

## 🎬 PUBLISHING DECISION

**Recommendation:** ⚠️ **Minor Tweaks Then Publish** (7/10)

**Time to Publish:** 10 minutes (quick fixes)

**Priority Fixes (In Order):**
1. Strengthen hook (add result: "91% accuracy")
2. Add formatting to paragraph 2 (bullets, arrows)
3. Make CTA active ("Want the architecture? Link in comments")

---

## 🔧 REVISED VERSION

```
Built a RAG-powered ICP qualification agent. Result: 91% accuracy vs 73% for generic tools.

How it works:
→ Stores YOUR exact ICP in vector DB (Pinecone)
→ When lead arrives, retrieves YOUR criteria
→ Claude analyzes lead against YOUR requirements
→ Returns score (0-100) + reasoning

Why it's better:
Not generic rules. YOUR specific criteria.

Tech stack: Pinecone + Claude API
Cost: $0.03 per lead (tested on 100 leads)
Accuracy: 91% vs manual scoring

Want the complete architecture? Link in comments 👇

#AIInfrastructure #GTMEngineering
```

**Key Changes:**
- Hook: Added result (91% accuracy)
- Flow: Reformatted with arrows, added test validation
- CTA: Changed from passive "let me know" to active "Link in comments"
- Added: Hashtags for discoverability

**New Score: 8/10**

---

## 📊 SCORE BREAKDOWN SUMMARY

```
╔════════════════════════════════════════╗
║  CONTENT QA SCORECARD                  ║
╠════════════════════════════════════════╣
║  Hook (0-3):              2/3  [██░]   ║
║  Flow (0-3):              2/3  [██░]   ║
║  CTA (0-2):               1/2  [█░]    ║
║  Technical Accuracy (0-2): 2/2  [██]    ║
╠════════════════════════════════════════╣
║  TOTAL SCORE:             7/10         ║
╠════════════════════════════════════════╣
║  Status: MINOR TWEAKS NEEDED ⚠️        ║
╚════════════════════════════════════════╝
```

---

## 💡 LEARNING NOTES

**Pattern Recognition:**
- Posts with results in hook score higher (2/3 vs 3/3)
- Wall of text reduces flow score even if content is good
- Passive CTAs ("let me know") consistently underperform
- Technical accuracy is your strength (keep it up)

**Quick Wins:**
- Always add result to hook (builds curiosity)
- Always format technical explanations (arrows, bullets)
- Always make CTA active and specific
```

---

## TEST CASE 4: Email Subject Line Review

### Input Content
```
Subject: Introducing our new AI qualification system
Body: [Email content...]
```

### Expected Output (Focus on Hook/Subject)
```markdown
## CONTENT SCORE: 4/10 (Subject Line Only)

**Content Type:** Email Subject Line  
**Target Audience:** B2B decision makers (assumed)

---

## 🎯 HOOK ANALYSIS (1/3 points)

**Hook Text:** "Introducing our new AI qualification system"

**Pattern Used:** Announcement

### Strengths
- Clear topic (AI qualification)
- Professional tone

### Issues
- **"Introducing" is weak opener** - Signals sales pitch, not value
- **"Our new"** centers on YOU not reader - reader doesn't care it's new
- **No benefit stated** - Why should they open?
- **No curiosity gap** - No reason to learn more
- Generic - could be any AI announcement email

### Recommendation
**Rewrite focused on reader benefit:**

**Option A (Stat-based):**
```
91% qualification accuracy in 30 seconds (vs 2 hours manual)
```

**Option B (Problem-solution):**
```
Stop wasting sales time on unqualified leads
```

**Option C (Personalized):**
```
[First Name], your lead scoring just got 10x faster
```

**Expected open rate:**
- Current: 12-18% (generic announcement)
- Revised: 25-35% (benefit-focused)
```

---

## SUMMARY OF TEST CASES

### Patterns Observed

**High Scorers (8-10/10):**
- Specific results in hook
- Scannable formatting
- Active, targeted CTAs
- Personal voice (I built, I tested)
- Concrete proof (numbers, metrics)

**Low Scorers (0-4/10):**
- Generic hooks (AI is changing...)
- No structure/flow
- Passive CTAs (Thoughts?)
- No specifics or examples
- Corporate/hype voice

**Mid Scorers (5-7/10):**
- Good bones, needs polish
- Missing one element (result, formatting, CTA)
- 10-30 min fixes get to 8-9/10

---

**Use these examples to calibrate your own content before publishing.**
