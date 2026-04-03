# Content Calendar
**Campaign**: Early Customer Persona vs ICP — B2B GTM Clarity Campaign
**Schedule start**: 2026-03-18
**Schedule end**: 2026-03-31 (2-week window)
**Quality gate**: All content files passed QA (07), SEO (08), and Brand Voice (09)
**Date**: 2026-03-17
**Agent**: content-calendar-planner

---

## Campaign Publish Timeline

| Date | Day | Time | Channel | Asset | Variant | Actions Required |
|---|---|---|---|---|---|---|
| 2026-03-18 | Wed | 8:00am local | Email | Email 1 — The Reframe | Subject line Variant B: "Why your outbound isn't converting (it's not the copy)" | Load into email platform, personalize [First name] field, set preview text |
| 2026-03-18 | Wed | 9:00am local | Blog | Blog post live | — | Publish to site with SEO slug `/early-customer-persona-vs-icp-b2b-gtm`, add author bio, add Article schema, add 2–3 outbound citations |
| 2026-03-19 | Thu | 8:00am local | LinkedIn | LinkedIn Variant A | Mistake Hook: "Most founders build their GTM for a customer who doesn't exist yet." | Post, then immediately drop blog link in first comment; author available to reply to comments 8–10am |
| 2026-03-22 | Sun | — | Email | Email 2 — The Framework | Subject line Variant B: "The $1M ARR persona vs. the $10M ARR persona" | Auto-trigger 4 days after Email 1 send |
| 2026-03-25 | Wed | 8:00am local | LinkedIn | LinkedIn Variant C | Stakes/ARR Hook: "The persona that gets you to $1M ARR will stall you at $3M." | Post, drop blog link in first comment; author replies to comments 8–10am |
| 2026-03-27 | Fri | — | Email | Email 3 — The Soft CTA | Subject line Variant B: "Still figuring out your early customer? (quick question)" | Auto-trigger 5 days after Email 2 send |
| 2026-03-31 | Tue | 8:00am local | LinkedIn | LinkedIn Variant B | Contrarian Reframe: "Your ICP isn't the problem." | Post, drop blog link in first comment; author replies to comments 8–10am |

---

## Channel Notes

### Blog
- Publish date: 2026-03-18 (Wednesday)
- Publish before LinkedIn post goes live on 2026-03-19 so the link is live when dropped in first comment
- Pre-publish checklist:
  - [ ] Add exact phrase "early customer persona B2B GTM" in first 100 words (SEO fix #1)
  - [ ] Add H3 labels for Steps 1–4 in the ECP building section (SEO fix #4)
  - [ ] Rename Summary H2 to include "B2B go-to-market strategy" (SEO fix #3)
  - [ ] Add author bio to the published page
  - [ ] Add Article schema markup
  - [ ] Add 2–3 contextual outbound citations (GTM Strategist, First Round Review)
  - [ ] Confirm comparison table renders as HTML table, not markdown block
  - [ ] Add attribution or hyperlink for GTM Strategist framework reference (QA fix)
- Post-publish: Submit URL to Google Search Console for indexing

### LinkedIn — All Posts
- Do NOT include the blog link in the caption
- Drop blog link in the first comment immediately after posting
- Author must be available to reply to comments in the first 2 hours after each post
- After posting, seed the comment thread with a follow-up question from the author within 30 minutes
- Hashtag check: confirm hashtags are woven naturally (not stacked at bottom) before scheduling
- Variant C word count: verify in LinkedIn draft editor before scheduling (QA note)

### LinkedIn — Variant A (2026-03-19)
- Lead post for the campaign — first signal on what format resonates
- Track: comment count at 24h, saves at 24h, reshare count
- If comment count exceeds 20 within 48h: reshare the post in the campaign Slack or newsletter mention

### LinkedIn — Variant C (2026-03-25)
- Staggered 6 days after Variant A
- Primary metric to watch: reshare rate and co-founder tags in comments
- If Variant A significantly outperformed on comments, add a callback to it in Variant C's first comment ("Following up on the post from last week on ECP vs ICP — this one goes deeper on the ARR transition...")

### LinkedIn — Variant B (2026-03-31)
- Final variant, 6 days after Variant C
- Wednesday post — different day from the previous two to control for day-of-week effects
- If either Variant A or C has a clear winner at this point, use the learnings to optimize Variant B's comment engagement strategy before posting

### Email Sequence
- Email 1: Send Wednesday 2026-03-18 at 8:00am — aligns with blog publish day and LinkedIn campaign launch
- Email 2: Auto-trigger 4 days after Email 1 (Sunday 2026-03-22) — keeps momentum without over-sending on weekdays
- Email 3: Auto-trigger 5 days after Email 2 (Friday 2026-03-27)
- Personalization fields: [First name] — confirm all records in the send list have first name populated
- Subject line A/B split: Run the subject line tests documented in pipeline/11-ab-variants.md if list size permits (100+ per variant)
- Link placement: Blog URL goes in Email 2 body only (not Email 1 — Email 1 is single insight, no links except LinkedIn profile)

---

## Week-by-Week View

### Week 1 (2026-03-18 to 2026-03-24)
| Date | Action |
|---|---|
| 2026-03-18 Wed | Blog live + Email 1 sent |
| 2026-03-19 Thu | LinkedIn Variant A posted |
| 2026-03-22 Sun | Email 2 auto-sent |
| 2026-03-22 Sun | Review LinkedIn Variant A performance — record comment count, saves, reshares |

### Week 2 (2026-03-25 to 2026-03-31)
| Date | Action |
|---|---|
| 2026-03-25 Wed | LinkedIn Variant C posted |
| 2026-03-27 Fri | Email 3 auto-sent |
| 2026-03-28 Sat | Record email sequence metrics — open rate, reply rate per email |
| 2026-03-31 Tue | LinkedIn Variant B posted |
| 2026-03-31 Tue | Campaign window closes — collect all metrics for performance-analyst |

---

## Post-Campaign Actions (after 2026-03-31)

- Pull LinkedIn analytics: impressions, comments, saves, reshares per variant
- Pull email analytics: open rate, click rate, reply rate per email and per subject line variant
- Pull blog analytics: sessions, avg. time on page, scroll depth, keyword ranking position
- Pass all data to performance-analyst → pipeline/10-performance-report.md
- Pass winning patterns to ab-test-designer for next campaign
- Update pipeline/12-campaign-learnings.md with what worked

---

## Link Placement Notes

| Asset | Blog link placement |
|---|---|
| LinkedIn Variant A, B, C | First comment only — never in caption |
| Email 1 | No blog link — LinkedIn profile URL only |
| Email 2 | Blog URL inline in body (after the 3-step framework) |
| Email 3 | LinkedIn profile URL — no blog link |

---

## Deadline Check

| Deliverable | Status | Publish date | Deadline |
|---|---|---|---|
| Blog post | Ready — apply 4 SEO pre-publish fixes | 2026-03-18 | 2026-03-24 (brief deadline) |
| LinkedIn Variant A | Ready — verify word count on Variant C | 2026-03-19 | 2026-03-24 |
| LinkedIn Variant C | Ready | 2026-03-25 | Post-deadline but within campaign window |
| LinkedIn Variant B | Ready | 2026-03-31 | Post-deadline but within campaign window |
| Email sequence | Ready — confirm send list and personalization | 2026-03-18 | 2026-03-24 |

All content is publish-ready by the 2026-03-24 brief deadline. Variants C and B are scheduled post-deadline for the A/B test stagger — this is intentional and does not violate the brief.
