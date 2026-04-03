---
name: linkedin-gtm-post
description: Use this skill when writing LinkedIn posts, content, captions, thought-leadership articles, or any professional social content for AI GTM Engineer positioning. Trigger on "write a LinkedIn post", "create LinkedIn content", "draft post for [day/topic]", "write eKigai product post", or "create newsletter edition". Optimized for Karthikeyan's 9-post weekly strategy (7 daily educational + 2 eKigai product posts) + 2 newsletters.
---

# LinkedIn GTM Post Production System

## Quick Reference Card

**When to use this skill:**
- Writing any of the 9 weekly LinkedIn posts
- Creating newsletter editions (Production GTM or AI Product Marketer)
- Drafting thought-leadership articles
- Any professional content for LinkedIn

**What this skill does:**
- Analyzes post intent (which of 9 post types)
- Loads appropriate tone guide and format template
- Generates post with correct structure, hooks, CTAs
- Outputs in requested format (short/long/carousel)
- Ensures brand consistency across all content

---

## Layer 1: Capture Intent

**Step 1: Identify post type from user request**

Ask the user (if not specified):
1. **Which post type?**
   - Monday: GTM Engineering Execution
   - Tuesday AM: Product Marketing Strategy
   - Tuesday PM: eKigai Product (Building)
   - Wednesday: GTM Engineering Execution
   - Thursday AM: LinkedIn Foundation
   - Thursday PM: eKigai Product (User Story)
   - Friday: Claude/Agentic Evaluation
   - Saturday: Product Development
   - Sunday: Weekly Showcase + Analytics
   - Newsletter: Production GTM (LinkedIn)
   - Newsletter: AI Product Marketer (Substack)

2. **What's the specific topic?** (e.g., "ICP scoring framework", "funding signal detection")

3. **What's the goal?**
   - Educational (teach framework)
   - Social proof (show results)
   - Product promotion (drive eKigai users)
   - Newsletter (deep-dive content)

4. **Any specific format?**
   - Short text post (200-300 words)
   - Long-form post (400-600 words)
   - Carousel (request number of slides)
   - Article (newsletter format)

**Step 2: Determine audience & tone**

Based on post type, automatically select:
- **Target audience:** GTM engineers, Product marketers, Founders, Technical builders
- **Tone:** Technical authority, Strategic consultant, Build-in-public, Thought leader
- **Voice:** First-person (educational posts), "We" (eKigai posts), "I work with" (client work)

---

## Layer 2: Load Reference Materials

**Step 3: Read appropriate tone guide**

→ Read `/references/tone-guide.md` for voice matching
→ Identifies: B2B vs thought-leader vs founder voice
→ Matches to post type (technical, strategic, product, reflective)

**Step 4: Read post format template**

→ Read `/references/post-formats.md` for structure
→ Loads template for specific post type (Monday execution, Tuesday PM eKigai, etc.)
→ Gets hook patterns, body structure, CTA formats

**Step 5: Load examples (if needed)**

→ Read `/references/examples.md` for high-performing post patterns
→ Analyzes structure, hook quality, engagement triggers
→ Adapts patterns to user's specific topic

---

## Layer 3: Draft the Post

**Step 6: Write the hook (first 1-2 lines)**

**Hook principles:**
- Start with relatable pain point or surprising stat
- Address ICP directly (AI-native founders, GTM engineers, Product marketers)
- Pattern interrupt (avoid generic openings)
- Under 20 words for maximum impact

**Hook types by post:**
- **Educational posts:** Problem statement ("Most founders waste 15 hrs/week on X")
- **eKigai posts:** Relatable pain + solution preview ("Sarah was drowning in manual ICP scoring. Here's what changed:")
- **Framework posts:** Contrarian insight ("ICP scoring isn't about company size. It's about signals.")
- **Weekly showcase:** Data-driven opener ("This week: 3 clients, 27 hours saved, here's how:")

**Step 7: Write the body**

**Structure by post type:**

**Monday/Wednesday (GTM Execution):**
```
Hook: [Problem client faced]

What we shipped:
→ [System 1]
→ [System 2]
→ [System 3]

[Deep-dive on one implementation with screenshot/diagram]

Results:
→ [Metric before] → [Metric after]
→ [Time/cost saved]

Stack: [Tools used]

Lesson learned: [One key insight]
```

**Tuesday AM (Product Marketing):**
```
Hook: [Common PM mistake]

Here's the framework we use:

[Framework name]

Step 1: [Action]
Step 2: [Action]
Step 3: [Action]

Example in action:
[Client scenario]

Before: [Problem metric]
After: [Improved metric]

Why this works: [Strategic insight]

Template: [Link to download]
```

**Tuesday PM (eKigai Building):**
```
Building eKigai: [Feature name]

Hook: [Founder pain point eKigai solves]

The challenge:
[Product development challenge]

How we're solving it:
→ [GTM engineering approach]
→ [Framework/system built]
→ [Technical implementation]

Why this matters:
[Business impact for founders]

What we learned:
[Key insight from building]

---

eKigai is AI-native business intelligence for B2B SaaS founders.

Testing with 50+ early users. Want early access? → [link]

#BuildingInPublic #eKigai
```

**Thursday PM (eKigai User Story):**
```
eKigai User Story: [Founder name]

Hook: [Relatable founder pain]

Meet [Founder], [Title] at [Company]:

Before eKigai:
→ [Manual process]
→ [Time spent]
→ [Pain point]

After eKigai (Week X):
→ [Automated process]
→ [Time saved]
→ [Business result]

[Founder quote about impact]

---

eKigai is AI-native business intelligence.

Book a demo: [calendar link]

#eKigai #CustomerStory
```

**Friday (Claude/Evaluation):**
```
Hook: [AI quality issue]

Built evaluation framework:

Test criteria:
→ [Metric 1]: [How measured]
→ [Metric 2]: [How measured]

Implementation:
[Code snippet or workflow]

Results:
→ Baseline: [Before]
→ After evaluation: [After]
→ Improvement: [%]

Key lesson: [Insight about AI evaluation]
```

**Sunday (Weekly Showcase):**
```
Weekly Showcase: [Week's theme]

This week's focus: [GTM area]

What we shipped:
→ [System 1] — [Result]
→ [System 2] — [Result]
→ [System 3] — [Result]

Key metrics:
→ [Metric 1]: [Before] → [After]
→ [Metric 2]: [Before] → [After]

Biggest lesson: [One key insight]

📬 Full breakdown in this week's newsletter: [Link]
```

**Step 8: Add CTA (Call-to-Action)**

**CTA rules by post type:**

**Educational posts (Mon/Tue/Wed/Thu/Fri):**
- Soft CTA: "Template in comments" or "DM '[keyword]' for framework"
- Newsletter CTA: "Full methodology in this week's newsletter"
- Engagement CTA: "What's your approach to [topic]?"

**eKigai posts (Tue PM / Thu PM):**
- Month 1: "Join the waitlist → [link]"
- Month 2: "Book a 20-min demo → [calendar]"
- Month 3: "Lock in founder pricing → [link]"

**Weekly showcase (Sunday):**
- Newsletter CTA: "📬 Full breakdown in Production GTM newsletter"
- Subscribe CTA: "Subscribe here: [link]"

**Step 9: Add formatting**

**Formatting rules:**
- Use arrows (→) for lists, not bullets
- Line breaks between sections (not walls of text)
- Bold key numbers or results
- Emojis: Sparingly (1-2 max, only for section headers)
- Hashtags: 3-5 relevant tags at end

**Visual structure:**
```
[Hook - 1-2 lines]

[Blank line]

[Body section 1]
→ Point
→ Point

[Blank line]

[Body section 2 with data/results]

[Blank line]

[Lesson learned or key insight]

[Blank line]

---

[CTA if eKigai post]

[Hashtags]
```

---

## Layer 4: Variants (Optional)

**Step 10: Generate variants if requested**

**Short version (200-300 words):**
- Hook + 1 key point + CTA
- For quick insights or hot takes

**Long version (400-600 words):**
- Full template structure
- Deep-dive with examples and data

**Carousel version:**
- Slide 1: Hook + problem statement
- Slides 2-8: Framework steps or key points (1 per slide)
- Slide 9: Results or case study
- Slide 10: CTA + next steps

---

## Layer 5: Output Format

**Step 11: Format for publishing**

**Text post format:**
```
[Post content with formatting]

[Hashtags: #GTMEngineering #RevOps #ProductMarketing #AIforGTM #eKigai]

---

Character count: [X]
Estimated reading time: [Y] seconds
Target audience: [Audience type]
Best time to post: [Day] [Time] IST
```

**Newsletter format (Production GTM or AI Product Marketer):**
- Include full newsletter template structure
- Add section dividers (━━━━━━)
- Email subject line
- Preview text
- Lead magnet CTA

**Carousel format:**
- Text for each slide
- Design notes (background color, text size)
- Visual hierarchy guidance

---

## Quality Checklist (Always Run)

Before outputting, verify:

✅ **Hook quality:**
- [ ] Addresses specific pain point
- [ ] Under 20 words
- [ ] Relevant to ICP
- [ ] Pattern interrupt (not generic)

✅ **Body structure:**
- [ ] Clear framework or story arc
- [ ] Specific examples (not vague)
- [ ] Data/metrics included (before → after)
- [ ] Actionable takeaway

✅ **Voice consistency:**
- [ ] Matches post type (technical vs strategic vs product)
- [ ] First-person for educational, "We" for eKigai
- [ ] No jargon without explanation
- [ ] Authentic (not salesy for eKigai posts)

✅ **CTA appropriateness:**
- [ ] Matches post goal (educational vs product)
- [ ] Not too pushy (70% education, 20% context, 10% CTA for eKigai)
- [ ] Clear next step

✅ **Formatting:**
- [ ] Line breaks for readability
- [ ] Arrows (→) for lists
- [ ] Bold for key metrics
- [ ] 3-5 hashtags only

✅ **Length:**
- [ ] Short: 200-300 words
- [ ] Long: 400-600 words
- [ ] Newsletter: 1,200-1,800 words (LinkedIn) or 2,000-3,000 (Substack)

✅ **Brand consistency:**
- [ ] Matches Karthikeyan's positioning (AI GTM Engineer at e-ideaCS)
- [ ] Mentions eKigai appropriately (only in Tue/Thu PM posts)
- [ ] References client work (not solo building)
- [ ] Includes newsletter CTA where relevant

---

## Special Instructions by Post Type

### Monday/Wednesday (GTM Execution Showcase)

**Focus:** Show real client work with results
**Tone:** Professional, data-driven, technical
**Key elements:**
- Client context (company size, stage) - sanitized
- Technical stack used (Clay, n8n, HubSpot, Claude)
- Before/after metrics (time saved, accuracy improved)
- One key lesson learned

**Avoid:**
- Generic "we built a system" (be specific)
- Overpromising results
- Revealing client names without permission

---

### Tuesday AM (Product Marketing Strategy)

**Focus:** Strategic framework for product marketers
**Tone:** Consultant, strategic, framework-oriented
**Key elements:**
- Framework with clear steps
- Real-world application example
- Common mistakes to avoid
- Template download CTA

**Avoid:**
- Too theoretical (need practical application)
- No examples (frameworks need context)
- Forgetting the "why this works" section

---

### Tuesday PM (Building eKigai)

**Focus:** Product development insights using GTM engineering
**Tone:** Build-in-public, technical, founder-to-founder
**Key elements:**
- Specific feature or decision
- GTM engineering approach used
- Technical implementation details
- What you learned building it
- Soft eKigai CTA (waitlist/demo)

**Critical rules:**
- 70% educational (the learning)
- 20% product context (eKigai as case study)
- 10% soft CTA (invitation, not pressure)
- NEVER say "eKigai is the best" or "limited time"
- ALWAYS lead with insight, not product

---

### Thursday AM (LinkedIn Foundation)

**Focus:** LinkedIn strategy and personal branding
**Tone:** Practitioner, tactical, results-oriented
**Key elements:**
- Specific LinkedIn tactic tested
- Before/after results
- Framework or approach
- Why it worked (algorithm insight)

**Avoid:**
- Generic LinkedIn advice
- No data/results
- Overly promotional

---

### Thursday PM (eKigai User Story)

**Focus:** Social proof from real eKigai users
**Tone:** Storytelling, relatable, founder-to-founder
**Key elements:**
- Founder name + company (with permission)
- Before state (manual pain)
- After state (automated result)
- Specific metrics (time saved, accuracy improved)
- Founder quote (authentic, not scripted)
- Demo booking CTA

**Critical rules:**
- Real users only (never fabricate)
- Get permission before posting
- Use real metrics (not inflated)
- Quote must sound authentic
- Lead with relatable pain, not product

---

### Friday (Claude/Agentic Evaluation)

**Focus:** AI quality, evaluation, Claude-specific implementations
**Tone:** Technical, practitioner, quality-focused
**Key elements:**
- AI quality problem identified
- Evaluation framework built
- Technical implementation (code snippets okay)
- Results (hallucination reduction, accuracy improvement)
- Key lesson about AI evaluation

**Avoid:**
- Generic AI hype
- No technical depth
- Missing evaluation metrics

---

### Saturday (Product Development)

**Focus:** Product decisions, build vs buy, roadmap choices
**Tone:** Thoughtful, strategic, transparent
**Key elements:**
- Product decision or challenge
- Options considered
- Trade-offs analyzed
- Decision made + reasoning
- Timeline or next steps

**Avoid:**
- Promoting eKigai (this is about development, not marketing)
- Being vague about trade-offs
- No clear decision/recommendation

---

### Sunday (Weekly Showcase + Analytics)

**Focus:** Week's results, metrics, learnings
**Tone:** Reflective, data-driven, teaching
**Key elements:**
- Week's theme or focus area
- What was shipped (3 items)
- Key metrics (2-3 before/after)
- Biggest lesson learned
- Newsletter CTA

**Avoid:**
- Bragging without teaching
- Metrics without context
- No lesson or takeaway

---

### Newsletter: Production GTM (LinkedIn)

**Focus:** Technical GTM engineering deep-dive
**Tone:** Engineer-to-engineer, practical, code-heavy
**Structure:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Production GTM — Edition [X]
[Topic Title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 Hey [First Name],

[Hook: Technical problem]

🏗️ THE ARCHITECTURE
[System design]

⚙️ THE IMPLEMENTATION
[Step-by-step with code]

📊 THE RESULTS
[Before/after metrics]

💡 KEY LESSONS
[Technical insights]

🔧 GRAB THE TEMPLATE
[Lead magnet download]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

See you next Sunday.
— Karthikeyan
```

**Length:** 1,200-1,800 words

---

### Newsletter: The AI Product Marketer (Substack)

**Focus:** Strategic product marketing frameworks
**Tone:** Consultant-to-client, strategic, framework-heavy
**Structure:**
```
[Topic Title]

By Karthikeyan Muthu · [Date] · 8 min read

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Hook: Strategic challenge]

THE FRAMEWORK
[3-layer methodology with diagrams]

REAL-WORLD APPLICATION
[Client case study]

COMMON MISTAKES TO AVOID
[3 mistakes + better approaches]

YOUR ACTION PLAN
[Week-by-week implementation]

DOWNLOAD THE TEMPLATE
[Framework download]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thanks for reading The AI Product Marketer.

Next week: [Preview]

— Karthikeyan
```

**Length:** 2,000-3,000 words

---

## Hashtag Strategy

**Always use 3-5 hashtags max** (LinkedIn algorithm penalizes 6+)

**By post type:**

**Monday/Wednesday (GTM Execution):**
`#GTMEngineering #RevOps #MarketingAutomation #ClayHQ #n8n`

**Tuesday AM (Product Marketing):**
`#ProductMarketing #GTMStrategy #ICPStrategy #Positioning #B2BMarketing`

**Tuesday PM (eKigai Building):**
`#BuildingInPublic #eKigai #AIforGTM #StartupGTM #FounderLed`

**Thursday AM (LinkedIn Strategy):**
`#LinkedInStrategy #PersonalBranding #ContentMarketing #ThoughtLeadership`

**Thursday PM (eKigai User Story):**
`#eKigai #CustomerStory #StartupSuccess #AIAutomation #GTMResults`

**Friday (Claude/Evaluation):**
`#ClaudeAI #AgenticAI #AIEvaluation #PromptEngineering #AIQuality`

**Saturday (Product Development):**
`#ProductDevelopment #BuildInPublic #ProductStrategy #StartupJourney`

**Sunday (Weekly Showcase):**
`#GTMResults #WeeklyReview #DataDriven #GTMEngineering #RevOps`

---

## Common Mistakes to Avoid

❌ **Don't:**
- Start with "I'm excited to share..." (overused)
- Use generic hooks ("In today's business landscape...")
- Forget metrics/data in execution posts
- Make eKigai posts too salesy (violates 70-20-10 rule)
- Use more than 5 hashtags
- Wall of text (need line breaks)
- Generic CTAs ("Let me know in comments")
- Fabricate user stories or metrics

✅ **Do:**
- Lead with specific pain point
- Include real metrics (before → after)
- Use authentic voice (not corporate)
- Show work (screenshots, diagrams, code snippets)
- Give away frameworks freely
- Make eKigai posts educational first
- Keep CTAs specific and soft
- Get permission before sharing user stories

---

## Publishing Checklist

Before scheduling the post:

**Content quality:**
- [ ] Hook tested (would I stop scrolling for this?)
- [ ] Body delivers on hook promise
- [ ] Specific examples included (not vague)
- [ ] Data/metrics included where relevant
- [ ] One clear takeaway or lesson
- [ ] CTA matches post type and goal

**Technical requirements:**
- [ ] Character count appropriate (200-600 words)
- [ ] Line breaks for readability
- [ ] Formatting consistent (arrows, bold, spacing)
- [ ] Hashtags: 3-5 only
- [ ] No typos or grammar errors

**Brand alignment:**
- [ ] Matches Karthikeyan's voice (AI GTM Engineer at e-ideaCS)
- [ ] Positioning correct (team member, not solo founder)
- [ ] eKigai mentioned appropriately (only Tue/Thu PM)
- [ ] Newsletter CTA included (where relevant)
- [ ] Client work sanitized (no client names without permission)

**Strategic alignment:**
- [ ] Supports ICP (AI-native B2B SaaS founders)
- [ ] Builds authority in GTM engineering
- [ ] Demonstrates frameworks in practice
- [ ] Drives specific action (waitlist, newsletter, demo, engagement)

---

## When to Skip This Skill

**Don't use this skill for:**
- Personal posts (family, travel, life updates)
- Company announcements (from e-ideaCS official account)
- Job posts or hiring content
- Quick comments or replies to others' posts
- Direct messages or private communication

**Use this skill for:**
- All 9 weekly LinkedIn posts (educational + eKigai)
- Both newsletter editions (Production GTM + AI Product Marketer)
- Long-form thought-leadership articles
- Any professional content building GTM engineering authority

---

## Final Output Template

When complete, output in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 LINKEDIN POST DRAFT
Post Type: [Monday GTM Execution / Tuesday PM eKigai / etc.]
Topic: [Specific topic]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[FULL POST CONTENT WITH FORMATTING]

[HASHTAGS]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 POST METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Character count: [X]
Word count: [Y]
Estimated read time: [Z] seconds
Target audience: [Audience]
Best posting time: [Day] [Time] IST
Post goal: [Educational / Social proof / Product promotion / Newsletter]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ QUALITY CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hook quality: [✓ / Needs work]
Specific examples: [✓ / Needs work]
Data/metrics included: [✓ / N/A]
Clear takeaway: [✓ / Needs work]
CTA appropriate: [✓ / Needs work]
Formatting correct: [✓ / Needs work]
Brand aligned: [✓ / Needs work]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 OPTIMIZATION SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Any specific suggestions for improvement]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**Ready to create LinkedIn content that builds authority, drives users, and positions you for promotion.**

**Next step:** Tell me which post type you want to write, the specific topic, and I'll draft it for you.
