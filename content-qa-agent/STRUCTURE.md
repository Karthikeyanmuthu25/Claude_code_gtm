# Content QA Agent - File Structure

**Understanding how the agent is organized**

---

## 📁 Directory Structure

```
.claude/agents/content-qa/
├── agent-instructions.md      [8,500 words] - Agent behavior & rules
├── template.md                [1,800 words] - Output format
├── evaluation-criteria.md     [12,000 words] - Detailed scoring rubric
├── test-cases.md              [8,000 words] - Example reviews
├── INTEGRATION.md             [5,000 words] - Usage guide
├── QUICKSTART.md              [600 words] - 30-second start
├── README.md                  [3,000 words] - Overview
├── STRUCTURE.md               [This file] - File organization
└── sample.md                  [2,000 words] - Usage examples
```

**Total Documentation:** ~41,000 words of guidance

---

## 📄 File Purposes

### Core Agent Files

#### `agent-instructions.md` ⭐ Core Logic
**Purpose:** Defines how the agent thinks and behaves  
**Contains:**
- Role & identity
- Evaluation framework (Hook, Flow, CTA, Technical)
- Scoring rubric (0-10 scale)
- Response protocol
- Special cases (LinkedIn vs email vs blog)

**Who reads this:**
- Claude (to understand how to review)
- Advanced users (to understand agent logic)

**When to read:**
- If you want to modify agent behavior
- If you disagree with a score (understand reasoning)

---

#### `template.md` ⭐ Output Structure
**Purpose:** Defines exact format of every review  
**Contains:**
- Section headers
- Required fields
- Score breakdown format
- Revised version template

**Who reads this:**
- Claude (to format responses correctly)
- Users (to understand what to expect)

**When to read:**
- If review format seems inconsistent
- If you want to customize output format

---

#### `evaluation-criteria.md` ⭐⭐⭐ Must Read
**Purpose:** Detailed scoring rubric with examples  
**Contains:**
- Hook patterns (6 types with examples)
- Flow structures (PAS, BAB, SIA)
- CTA types (Engagement, Conversion, Discussion)
- Technical accuracy checks
- Red flags for each category

**Who reads this:**
- Everyone (most important file)
- Users learning to write better
- Agent (for scoring decisions)

**When to read:**
- Before writing content (know what scores high)
- After getting a low score (understand why)
- Daily (study high-performing patterns)

**Time investment:** 30 minutes to read thoroughly  
**ROI:** Immediate improvement in content quality

---

### User Documentation

#### `README.md` ⭐ Start Here
**Purpose:** Overview and quick reference  
**Contains:**
- What the agent does
- How to use it
- Success metrics
- Quality standards

**Who reads this:**
- First-time users
- Anyone needing quick reference

**When to read:**
- First time using agent
- Refresher on usage

---

#### `QUICKSTART.md` ⚡ 30 Seconds
**Purpose:** Get started immediately  
**Contains:**
- Installation (1 step)
- First review (copy/paste command)
- Quick fixes for common issues

**Who reads this:**
- Impatient users
- Users who want results fast

**When to read:**
- Literally right now (takes 30 seconds)

---

#### `INTEGRATION.md` ⭐ Advanced Usage
**Purpose:** Workflows, automation, tracking  
**Contains:**
- Usage patterns (8 types)
- Integration options (n8n, automation)
- Learning frameworks
- Improvement tracking

**Who reads this:**
- Power users
- Users integrating into workflows
- Users serious about improvement

**When to read:**
- After first week of usage
- When ready to systemize
- Building automation systems

---

#### `test-cases.md` ⭐ Examples Library
**Purpose:** Real reviews showing agent in action  
**Contains:**
- Test Case 1: Excellent post (9/10) with full review
- Test Case 2: Weak post (2/10) with full review
- Test Case 3: Good post (7/10) needing minor fixes
- Test Case 4: Email subject line review

**Who reads this:**
- Users calibrating expectations
- Users learning scoring patterns
- Users who learn by example

**When to read:**
- After getting first review (calibrate)
- When confused about a score
- Weekly (study high-scoring patterns)

---

#### `STRUCTURE.md` (This File)
**Purpose:** Explain file organization  
**Contains:**
- File purposes
- Reading order
- Reading priority

**Who reads this:**
- Users overwhelmed by documentation
- Users wanting systematic approach

**When to read:**
- When unsure which file to read
- Planning your learning path

---

#### `sample.md` 📝 Practical Examples
**Purpose:** Show real usage scenarios  
**Contains:**
- Copy/paste commands
- Expected outputs
- Common workflows

**Who reads this:**
- Users who learn by doing
- Users needing templates

**When to read:**
- Wanting to try specific use cases
- Building custom workflows

---

## 🎯 Recommended Reading Order

### Path 1: Fast Start (15 minutes)
**Goal:** Get first review immediately

1. **QUICKSTART.md** (2 min) - Installation + first command
2. **README.md** (5 min) - Skim "Understanding Scores" section
3. **sample.md** (3 min) - Copy a usage pattern
4. **Try it:** Run first review (5 min)

**Next:** Come back to Path 2 after first review

---

### Path 2: Deep Learning (2 hours)
**Goal:** Master the system

1. **README.md** (15 min) - Full read
2. **evaluation-criteria.md** (45 min) - Study all sections
3. **test-cases.md** (30 min) - Read all 4 test cases
4. **INTEGRATION.md** (20 min) - Learn workflows
5. **Practice:** Review 5-10 of your past posts (10 min)

**Next:** Daily usage + weekly pattern study

---

### Path 3: Power User (Ongoing)
**Goal:** Systematic improvement

**Week 1:**
- Read evaluation-criteria.md completely
- Review all past content (last 20 posts)
- Identify your weakest category (Hook/Flow/CTA)

**Week 2-4:**
- Study weakest category daily (5 min/day)
- Write 5+ variations before publishing
- Track scores (Google Sheets)

**Week 5+:**
- Review evaluation-criteria.md weekly (spot-check)
- Contribute new patterns you discover
- Help others improve

---

## 🔍 Which File to Read When

### Before Writing Content
**Read:** `evaluation-criteria.md`  
**Section:** Hook Patterns + Your weak area  
**Time:** 5 minutes  
**Why:** Prime your brain with high-performing patterns

---

### After Getting Low Score
**Read:** `evaluation-criteria.md`  
**Section:** Specific category that scored low  
**Time:** 10 minutes  
**Why:** Understand exactly what makes that element strong

---

### Building Workflow Automation
**Read:** `INTEGRATION.md`  
**Section:** "Integration Options" + "Advanced Usage"  
**Time:** 20 minutes  
**Why:** See n8n, automation, tracking patterns

---

### Disagreeing with Score
**Read:** `test-cases.md`  
**Section:** Find similar content type  
**Time:** 10 minutes  
**Why:** Calibrate expectations, see agent consistency

---

### Want to Customize Agent
**Read:** `agent-instructions.md`  
**Section:** "Evaluation Framework" + "Response Protocol"  
**Time:** 30 minutes  
**Why:** Understand decision-making logic

---

### Feeling Overwhelmed
**Read:** `QUICKSTART.md` ONLY  
**Section:** All of it (very short)  
**Time:** 2 minutes  
**Why:** Just get started, learn as you go

---

## 📊 File Dependency Map

```
QUICKSTART.md
    ↓
README.md
    ↓
    ├─→ evaluation-criteria.md (most important)
    │       ↓
    │   test-cases.md (see it in action)
    │       ↓
    │   INTEGRATION.md (advanced usage)
    │
    └─→ sample.md (copy/paste examples)

Supporting:
- agent-instructions.md (how agent thinks)
- template.md (output format reference)
- STRUCTURE.md (this file - navigation)
```

---

## 💡 Learning Tracks

### Track 1: Minimum Viable Usage
**Goal:** Review content before publishing

**Must Read:**
1. QUICKSTART.md
2. README.md (skim)

**Skip:**
- Everything else initially
- Come back when you hit issues

**Time:** 10 minutes  
**Outcome:** Can review content, understand scores

---

### Track 2: Quality Improvement
**Goal:** Write better first drafts

**Must Read:**
1. evaluation-criteria.md (full read)
2. test-cases.md (study patterns)
3. INTEGRATION.md (tracking section)

**Practice:**
- Review 10 past posts
- Identify patterns in your weak scores
- Rewrite weak elements

**Time:** 2 hours initial + 5 min/day  
**Outcome:** First drafts consistently 7+/10

---

### Track 3: Content Mastery
**Goal:** Agent rarely finds issues

**Must Read:**
- Everything (all files)
- Re-read evaluation-criteria.md weekly

**Practice:**
- Daily: Study one hook pattern
- Weekly: Review all your content
- Monthly: Analyze improvement trends

**Time:** 3 hours initial + 10 min/day  
**Outcome:** Consistently 8+/10, internalized standards

---

## 📈 File Updates

**This agent is versioned:**

Current Version: **1.0** (March 11, 2026)

**When files will be updated:**
- New hook patterns discovered → evaluation-criteria.md
- New use cases emerge → INTEGRATION.md, sample.md
- User feedback → All files (continuous improvement)

**How to check for updates:**
- Version number in README.md
- Last updated date in each file

---

## 🎯 Priority Reading List

**If you only read 3 files:**

1. **QUICKSTART.md** - Get started (2 min)
2. **evaluation-criteria.md** - Learn patterns (30 min)
3. **test-cases.md** - See examples (20 min)

**Total time:** 52 minutes  
**ROI:** Immediate content quality improvement

---

**If you only read 1 file:**

**evaluation-criteria.md**

It contains everything you need to write high-scoring content.

---

## 🧭 Navigation Tips

### Lost in Documentation?
**Start here:** QUICKSTART.md → Just use it first

### Want to Understand Scores?
**Go here:** evaluation-criteria.md → Study scoring rubric

### Need Specific Example?
**Go here:** test-cases.md → Find similar content

### Building Automation?
**Go here:** INTEGRATION.md → See workflow patterns

### Want to Modify Agent?
**Go here:** agent-instructions.md → Understand logic

---

**Remember:**

You don't need to read everything to get value.

Start with QUICKSTART.md.  
Use the agent.  
Come back to documentation when you need specific guidance.

**Learning by doing > Reading everything first.**

---

**Questions about structure?**
- Too much documentation? Start with QUICKSTART.md only
- Not enough detail? Read evaluation-criteria.md
- Want examples? Read test-cases.md
- Need workflows? Read INTEGRATION.md

**The documentation serves you. Use what's helpful. Skip the rest.**
