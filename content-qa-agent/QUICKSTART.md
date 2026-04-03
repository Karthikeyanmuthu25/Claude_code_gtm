# Content QA Agent - Quick Start

**⏱️ Get your first review in 30 seconds**

---

## ⚡ 30-SECOND START

### 1. Add to Claude Code
Place this folder at: `.claude/agents/content-qa/`

### 2. Test It
```
@content-qa review this:

AI is changing GTM. Thoughts?
```

### 3. Get Review
You'll receive:
- Score (X/10)
- What's strong
- What needs work
- Revised version (if <7/10)

**Done.** ✅

---

## 🎯 COMMON USAGE

### Before Publishing LinkedIn Post
```
@content-qa review this:

[paste your draft post]
```

### Compare Two Versions
```
@content-qa which is better:

Version A: [content]
Version B: [content]
```

### Focus on Specific Element
```
@content-qa rate just the hook:

[paste hook line]
```

---

## 📊 UNDERSTANDING SCORES

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Exceptional | Publish now |
| 7-8 | Strong | 5-10 min fixes |
| 5-6 | Decent | 15-30 min revision |
| 3-4 | Weak | 1+ hour rewrite |
| 0-2 | Poor | Start over |

---

## 🔧 QUICK FIXES

### If Hook Score Low (0-1/3)
**Problem:** Generic opening like "AI is changing..."

**Fix:** Use proven pattern:
```
❌ AI is revolutionizing GTM
✅ I tested 3 AI tools. Only 1 hit 90% accuracy.
```

---

### If Flow Score Low (0-1/3)
**Problem:** Wall of text, no structure

**Fix:** Add line breaks and formatting:
```
❌ The system works by storing your ICP in a database and then retrieving it when needed and scoring leads.

✅ The system:
→ Stores YOUR ICP in vector DB
→ Retrieves when lead arrives
→ Scores against YOUR criteria
```

---

### If CTA Score Low (0-1/2)
**Problem:** Weak ask like "Thoughts?"

**Fix:** Be specific and active:
```
❌ What do you think?
✅ Follow for the complete build breakdown. Tomorrow: Architecture + code.
```

---

## 📚 FULL DOCUMENTATION

- **agent-instructions.md** - How agent works
- **template.md** - Output format reference
- **evaluation-criteria.md** - Detailed scoring rubric (READ THIS!)
- **test-cases.md** - Example reviews with scores
- **INTEGRATION.md** - Advanced usage & workflows

---

## 💡 PRO TIPS

### Before Writing
1. Check evaluation-criteria.md for hook patterns
2. Choose structure (PAS, BAB, SIA)
3. Plan your CTA first

### While Writing
1. Self-score as you write
2. Ask: "Would I stop scrolling for this?"
3. Keep formatting scannable

### After Writing
1. Review with agent
2. Fix anything <7/10
3. Re-review
4. Publish when 7+

---

## 🎯 GOALS

**Week 1:** Understand scoring, average 6+/10  
**Week 4:** First drafts 7+/10  
**Week 8:** Consistently 8+/10

---

## ⚠️ REMEMBER

**Always review before publishing.**

Your LinkedIn posts represent your expertise.  
One generic post can undo weeks of authority building.

Every piece should score 7+.  
No exceptions.

---

**Ready to improve your content.**  
**Start with:** `@content-qa review this: [paste draft]`
