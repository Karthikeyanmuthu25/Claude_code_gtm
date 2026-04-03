# A/B Test Variants
**Campaign**: Early Customer Persona vs ICP — B2B GTM Clarity Campaign
**Files Reviewed**: pipeline/04-linkedin-draft.md, pipeline/05-email-draft.md
**Date**: 2026-03-17
**Agent**: ab-test-designer

---

## Overview

This document defines the A/B test structure for LinkedIn hooks and email subject lines. All variants are ready for implementation. Testing recommendations include hypothesis, success metric, and decision criteria for each test.

---

## TEST 1 — LinkedIn Hook Variants

**What we're testing**: Which hook type drives the highest comment rate (Depth Score proxy) for this topic and audience.

**Hypothesis**: The Mistake Hook (Variant A) will outperform the other two hooks on comment rate because it names a specific failure state that founders self-identify with, triggering both "that's me" and "actually, you're wrong" responses. The Stakes/ARR Hook (Variant C) will generate the highest reshare rate due to its financial anchoring.

**Primary metric**: Comment count within 48 hours of posting
**Secondary metric**: Reshare rate within 48 hours
**Decision threshold**: 30%+ difference in comment rate = clear winner; <30% = run both in rotation for 2 more weeks

### Hook A — Mistake Hook (Variant A)
"Most founders build their GTM for a customer who doesn't exist yet."

**Prediction**: Highest comment rate. Strong self-identification trigger. Most accessible to problem-unaware founders.
**Risk**: Can read as slightly generic if the second line doesn't immediately agitate — monitor comment quality, not just quantity.

### Hook B — Contrarian Reframe (Variant B)
"Your ICP isn't the problem. Building a full GTM motion before you know your Early Customer Persona is."

**Prediction**: Highest save rate. This hook stops scroll for founders who are ICP-familiar and think they've solved it — creates productive cognitive dissonance. Lower comment rate than A, higher save rate.
**Risk**: May not resonate with problem-unaware founders (those who don't yet have an ICP). Best for an audience that's already engaged with the topic.

### Hook C — Stakes/ARR Hook (Variant C)
"The persona that gets you to $1M ARR will stall you at $3M."

**Prediction**: Highest reshare rate and tag-a-cofounder behavior. The ARR milestones make the stakes personal and specific. Founders who have crossed $1M will tag co-founders and sales hires.
**Risk**: Smaller addressable audience — requires the reader to be close to or past $1M ARR to feel the urgency. May underperform on absolute impressions vs. Variant A.

### Recommended Test Schedule
- Week 1: Publish Variant A (Tuesday, 8am) — benchmark engagement
- Week 2: Publish Variant C (Tuesday, 8am) — compare ARR hook vs. mistake hook
- Week 3: Publish Variant B (Wednesday, 8am) — final comparison, different day to control for weekday effects
- Winner: Highest comment rate in first 48 hours wins the right to be used as the evergreen version of this content

---

## TEST 2 — Email Subject Line Variants

**What we're testing**: Which subject line pattern achieves the highest open rate for cold outreach to B2B SaaS Founders.

**Hypothesis**: Subject lines that reference a specific, recognizable failure state will outperform subject lines that promise a framework or tease curiosity — because this audience is inundated with "here's how to do X" subject lines and has developed strong filter habits against them.

**Primary metric**: Open rate (target: >35%)
**Secondary metric**: Reply rate (target: >6%)
**Decision threshold**: 5+ percentage points difference in open rate = winner. If under 5pp, use click-to-reply rate as tiebreaker.

### Email 1 Subject Line Test

**Test A vs. B vs. C** (3-way split, equal send volume per variant):

| Variant | Subject Line | Hypothesis |
|---|---|---|
| A | Your first 10 customers vs. your ICP | Direct contrast, no fluff — speaks to founders who already think about the distinction |
| B | Why your outbound isn't converting (it's not the copy) | Pain-state opener with a pattern-interrupt. Reframes a common attribution error. Predicted highest open rate. |
| C | The GTM mistake hiding inside your ICP doc | Curiosity gap + possessive framing ("your ICP doc") — personal and specific |

**Recommended primary**: Variant B — "Why your outbound isn't converting (it's not the copy)"
**Rationale**: Directly names the most acute pain (outbound not converting) and immediately introduces a counterintuitive element (it's not the copy). Forces the open. Matches the exact language founders use ("not converting").

**Backup**: Variant C if Variant B underperforms — the curiosity gap is a reliable fallback for the ICP-familiar segment.

### Email 2 Subject Line Test

**Test A vs. B** (2-way split):

| Variant | Subject Line | Hypothesis |
|---|---|---|
| A | How to build an Early Customer Persona (3-step method) | Framework promise — will attract founders actively searching for a solution |
| B | The $1M ARR persona vs. the $10M ARR persona | Stakes/outcome framing — mirrors the LinkedIn Variant C hook; predicted to perform better with founders already past early traction |

**Recommended primary**: Variant B for founders at $500K–$2M ARR. Variant A for founders pre-revenue to $500K ARR.
**Segmentation note**: If list can be segmented by company stage/ARR, send B to further-along founders and A to earlier-stage. If not, default to Variant A — broader relevance.

### Email 3 Subject Line Test

**Test A vs. B** (2-way split):

| Variant | Subject Line | Hypothesis |
|---|---|---|
| A | One question before I stop emailing you | Classic cold email close — recognized pattern, but risks feeling manipulative to sophisticated founders. QA has already flagged this. |
| B | Still figuring out your early customer? (quick question) | Softer, more genuine — lower pressure, higher quality reply rate even if open rate is lower |

**Recommended primary**: Variant B — "Still figuring out your early customer? (quick question)"
**Rationale**: Aligns with the conversational brand voice. Variant A is a recognized pattern that some founders will filter on sight. Variant B's parenthetical "(quick question)" signals brevity and reduces friction.

---

## TEST 3 — LinkedIn Closing CTA Variant (Secondary Test)

**What we're testing**: Whether a direct question about their specific situation outperforms a general reflection prompt for comment rate.

**Variant X (current)**: "Is your GTM built around your early buyers — or around the customer you're hoping to find?"
**Variant Y (alternative)**: "When did you last look at who actually closed your first 10 deals — and what they had in common?"

**Hypothesis**: Variant Y will outperform on comment depth (longer, more specific responses) because it asks a concrete action question, not a philosophical one. Variant X will win on comment volume.

**Recommendation**: Use Variant X for Variant A (Mistake Hook) on first publish. If comment depth is low, switch to Variant Y on the second post.

---

## Implementation Notes

- All LinkedIn A/B tests should be run on the same account, staggered 7 days apart
- Email subject line tests require a minimum of 100 sends per variant for statistical significance — confirm list size before splitting
- Track opens, replies, and LinkedIn comments in a shared tracking sheet — tag each entry with the variant label (A, B, C)
- At campaign close, pass results to performance-analyst and update pipeline/12-campaign-learnings.md with winning patterns
