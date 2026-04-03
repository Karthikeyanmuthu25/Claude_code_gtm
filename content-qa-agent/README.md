# Content QA Agent

**Never publish weak content again.**

Expert content reviewer for AI Infrastructure, GTM Engineering, and technical content.  
Built for Claude Code by Karthikeyan (AI GTM Engineer).

---

## 🎯 What This Agent Does

Reviews your content (LinkedIn posts, emails, blogs) and provides:
- **Objective scoring** (0-10 scale)
- **Specific feedback** (not generic "this is good")
- **Actionable fixes** (exact changes to make)
- **Revised version** (if score <7/10)

**Goal:** Ensure every piece of content you publish scores 7+/10.

---

## 🚀 Quick Start

### Installation
```bash
# Place this folder at:
.claude/agents/content-qa/
```

### First Review (30 seconds)
```
@content-qa review this:

[paste your draft content]
```

### Get Structured Feedback
- Score: 7/10
- Hook: 2/3 (needs stronger opening)
- Flow: 3/3 (perfect structure)
- CTA: 1/2 (make it more specific)
- Technical: 2/2 (accurate)

**Plus:** Revised version showing exactly how to improve.

---

## 📋 What Gets Scored

### 1. Hook (0-3 points)
**Question:** Does it stop scrolling?

**Good:** "I tested 3 AI tools. Only 1 hit 90% accuracy."  
**Bad:** "AI is changing GTM."

---

### 2. Flow (0-3 points)
**Question:** Does it progress logically?

**Good:** Problem → Solution → Proof → CTA  
**Bad:** Random thoughts with no structure

---

### 3. CTA (0-2 points)
**Question:** Is the ask clear and compelling?

**Good:** "Follow for complete build breakdown. Tomorrow: Architecture."  
**Bad:** "Thoughts?"

---

### 4. Technical Accuracy (0-2 points)
**Question:** Are claims correct?

**Good:** "RAG reduces hallucinations by grounding in context"  
**Bad:** "RAG eliminates hallucinations"

---

## 💡 Why This Matters

**Your LinkedIn is your portfolio.**

One generic post ("AI is changing GTM...") signals:
- ❌ You don't actually build with AI
- ❌ You're jumping on trends
- ❌ You have nothing unique to say

One specific post ("Built RAG system, 91% accuracy, here's how") signals:
- ✅ You build production systems
- ✅ You have real experience
- ✅ You share actual value

**This agent enforces quality standards.**

---

## 📊 Understanding Scores

### 9-10/10: Exceptional ⭐⭐⭐
**Meaning:** Publication-ready, high-impact content  
**Action:** Publish immediately (typo check only)  
**Example:** Specific result + proof + clear structure + strong CTA

---

### 7-8/10: Strong ⭐⭐
**Meaning:** Good content with 1-2 fixable issues  
**Action:** Quick fixes (5-10 minutes), then publish  
**Example:** Great hook but weak CTA, or good content with poor formatting

---

### 5-6/10: Decent ⭐
**Meaning:** Solid foundation but needs work  
**Action:** Restructure (15-30 minutes), then re-review  
**Example:** Valuable content buried in poor structure

---

### 3-4/10: Weak
**Meaning:** Multiple critical issues  
**Action:** Major rewrite (1+ hour)  
**Example:** Generic hook + no structure + vague CTA

---

### 0-2/10: Poor
**Meaning:** Fundamentally flawed  
**Action:** Start over with new approach  
**Example:** "AI is changing GTM. Thoughts?"

---

## 📁 File Structure

```
content-qa/
├── agent-instructions.md      ← Agent behavior & rules
├── template.md                ← Output format (what you receive)
├── evaluation-criteria.md     ← Detailed scoring rubric ⭐ READ THIS
├── test-cases.md             ← Example reviews with scores
├── INTEGRATION.md            ← How to use, workflows, tips
├── QUICKSTART.md             ← 30-second start guide
├── README.md                 ← This file
├── STRUCTURE.md              ← File organization explained
└── sample.md                 ← Example usage demonstrations
```

**Start with:** `evaluation-criteria.md` (learn scoring patterns)  
**Then try:** Test cases in `test-cases.md`  
**Then use:** `@content-qa review this: [your draft]`

---

## 🎓 How to Improve Over Time

### Week 1: Learn the System
- Read `evaluation-criteria.md` (full scoring rubric)
- Review all `test-cases.md` examples
- Run 5+ reviews to understand scores
- **Goal:** Average score 6+/10

### Week 2-4: Fix Weak Areas
- Identify your lowest-scoring category (hook/flow/CTA)
- Study examples in `evaluation-criteria.md`
- Practice that element specifically
- **Goal:** First drafts consistently 7+/10

### Week 5-8: Mastery
- Self-score before using agent
- Agent confirms your judgment
- Rarely need revised versions
- **Goal:** Consistently 8+/10, agent rarely needed

**Track progress in Google Sheets:**
```
Week 1: Avg 5.2/10 (4 posts, 3 revised)
Week 2: Avg 6.1/10 (5 posts, 2 revised)
Week 3: Avg 7.3/10 (5 posts, 1 revised)
Week 4: Avg 7.8/10 (6 posts, 0 revised)
```

---

## 🔧 Common Usage Patterns

### Pre-Publish Review (Most Common)
```
@content-qa review this LinkedIn post:

[paste draft]
```

**Returns:** Full review with score + fixes

---

### Compare Versions
```
@content-qa which hook is stronger:

A: "Day 23/90: Built AI agent"
B: "I automated lead scoring using RAG"
```

**Returns:** Comparison with recommendation

---

### Quick Score (No Full Review)
```
@content-qa quick score:

[paste content]
```

**Returns:** X/10 with one-sentence reason

---

### Batch Review
```
@content-qa review my last 5 posts:

Post 1: [content]
Post 2: [content]
...

Tell me patterns in high vs low scorers.
```

**Returns:** Comparative analysis + improvement recommendations

---

## 💡 Pro Tips

### Before Writing
1. Choose hook pattern (see `evaluation-criteria.md`)
2. Outline structure (PAS / BAB / SIA)
3. Know your CTA before writing

### While Writing
1. Self-score as you go
2. Check: "Would I stop scrolling?"
3. Format for scannability (line breaks, bullets)

### After Writing
1. Review with agent
2. If <7: Implement all fixes
3. Re-review after changes
4. Only publish when 7+

---

## 🎯 Quality Standards

**Your publishing rules:**

✅ **Publish if:**
- Score ≥7/10
- No technical errors
- Hook creates curiosity
- CTA is clear
- You'd engage with this content yourself

❌ **Don't publish if:**
- Score <7/10
- Generic hook ("AI is changing...")
- No structure
- Weak CTA ("Thoughts?")
- You're just filling content calendar

**Remember:** One great post > Five mediocre posts

---

## 📚 Full Documentation

### For Quick Reference
- **QUICKSTART.md** - 30-second guide
- **sample.md** - Usage examples

### For Learning
- **evaluation-criteria.md** ⭐ Detailed scoring rubric with examples
- **test-cases.md** - Real reviews (9/10, 7/10, 2/10 examples)

### For Advanced Use
- **INTEGRATION.md** - Workflows, automation, tracking
- **agent-instructions.md** - How agent thinks (technical)
- **template.md** - Output format reference

---

## 🐛 Troubleshooting

### Agent doesn't respond
**Fix:** Ensure folder is at `.claude/agents/content-qa/`

### Review seems too harsh
**Remember:** Agent enforces professional standards  
**Check:** `test-cases.md` - calibrate expectations

### Want different voice in revised version
**Tell agent:** "Revise using casual/technical/formal tone"

### Disagree with score
**Ask agent:** "Show me 9/10 example on this topic for comparison"

---

## 🎬 Examples

### Example 1: Excellent Post (9/10)
```
✅ Hook: "Day 23/90: My RAG system failed in production."
✅ Flow: Problem → Cause → Solution → Proof
✅ CTA: "Follow if you're building production AI"
✅ Technical: All accurate
```

### Example 2: Weak Post (2/10)
```
❌ Hook: "AI is revolutionizing GTM"
❌ Flow: Random statements, no structure
❌ CTA: "Thoughts?"
❌ Technical: Too vague to verify
```

**See `test-cases.md` for full reviews of both.**

---

## 📈 Success Metrics

### Short-Term (Week 1-4)
- [ ] Review all content before publishing
- [ ] Understand scoring system
- [ ] Average score: 6+/10
- [ ] Zero posts <5/10 published

### Medium-Term (Week 5-8)
- [ ] First drafts consistently 7+/10
- [ ] Rarely need revised versions
- [ ] Can predict score before review
- [ ] Average score: 7.5+/10

### Long-Term (Week 9-12)
- [ ] First drafts consistently 8+/10
- [ ] Agent mostly confirms your judgment
- [ ] Teaching others to write better
- [ ] Average score: 8+/10

---

## 🚨 Important Reminders

**This agent is strict by design.**

It will tell you when your content is weak.  
It will call out generic hooks.  
It will flag lazy CTAs.

**This is good.**

Your LinkedIn is your professional brand.  
Generic AI hype posts hurt your credibility.  
Every post should prove you actually build things.

**Use this agent as your quality filter.**

Never publish anything that scores <7/10.

---

## 🤝 Contributing

**Found an issue?**
- Check `agent-instructions.md` for behavior rules
- Check `evaluation-criteria.md` for scoring logic
- Check `test-cases.md` for calibration

**Want to improve it?**
- Suggest new hook patterns
- Add more test cases
- Improve evaluation criteria

---

## 📞 Support

**Questions:**
- Read `evaluation-criteria.md` first (most answers there)
- Check `test-cases.md` for examples
- Review `INTEGRATION.md` for advanced usage

**Common Questions:**
- "Why did my hook score low?" → See evaluation-criteria.md Hook section
- "What's a good CTA?" → See evaluation-criteria.md CTA examples  
- "How do I improve flow?" → See evaluation-criteria.md Flow patterns
- "Is this score accurate?" → Compare to test-cases.md examples

---

## 🎯 Your Content Quality Commitment

**Starting today:**

✅ I will review all content before publishing  
✅ I will not publish anything scoring <7/10  
✅ I will implement all suggested fixes  
✅ I will track my improvement over time  
✅ I will build authority through quality, not quantity

**Because:**
- One great post > Five mediocre posts
- Your LinkedIn is your portfolio
- Quality compounds, quantity doesn't

---

**Ready to never publish weak content again.**

**Start:** `@content-qa review this: [paste your draft]`

---

**Version:** 1.0  
**Last Updated:** March 11, 2026  
**Author:** Karthikeyan (AI GTM Engineer)  
**License:** Personal use
