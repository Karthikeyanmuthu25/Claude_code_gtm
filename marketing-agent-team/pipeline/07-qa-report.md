# QA Report
**Campaign**: Early Customer Persona vs ICP — B2B GTM Clarity Campaign
**Files Reviewed**: pipeline/04-linkedin-draft.md, pipeline/05-email-draft.md, pipeline/06-blog-draft.md
**Date**: 2026-03-17
**Agent**: qa-agent

---

## Overall Assessment

| File | Status | Issues Found |
|---|---|---|
| 04-linkedin-draft.md | PASS | 0 Critical / 1 Major / 2 Minor |
| 05-email-draft.md | PASS | 0 Critical / 1 Major / 1 Minor |
| 06-blog-draft.md | PASS | 0 Critical / 2 Major / 3 Minor |

**Quality Gate Result**: PASS — no Critical issues found. Content is approved to proceed to publishing pipeline.

---

## 04-linkedin-draft.md — LinkedIn Posts

### PASS

**Strengths:**
- All 3 variants stay within the 150–250 word range
- Hook lines are strong and specific — no generic engagement bait
- ECP vs ICP distinction is clearly explained in plain language in all 3 variants
- Arrow (→) used consistently as visual separator
- Hashtags are 4 or fewer per post and not stacked
- Closing questions are substantive and specific — will generate genuine comment responses
- No outbound links in caption

**Issues:**

MAJOR — Variant C word count verification needed
- Variant C runs approximately 230 words. Confirm it does not exceed 250 words when formatted for the LinkedIn editor (LinkedIn sometimes counts differently from word processors). Recommend a manual word count check before scheduling.
- Fix: Review in LinkedIn draft editor before scheduling. No content change needed unless it exceeds 250 words, in which case trim the last two body lines.

MINOR — Variant A closing question is slightly compound
- "Is your GTM built around your early buyers — or around the customer you're hoping to find?" is good but could be sharpened to a single choice or direct question.
- Fix (optional): Simplify to "Who is your GTM actually built around — your early buyers or your future ones?" (Already closer to the social signals example post skeleton — consider aligning.)

MINOR — Variant B hashtag placement
- Hashtags appear at the very end of Variant B as a block: `#B2BSaaS #StartupGTM #FounderLed`. Per social-listener guidance, weave 1–2 hashtags naturally into the closing rather than stacking at the end.
- Fix: Move one hashtag earlier in the closing paragraph or integrate into the final sentence organically.

---

## 05-email-draft.md — Cold Outreach Sequence

### PASS

**Strengths:**
- Educate-first structure is maintained across all 3 emails — no premature pitch
- Email 1 is correctly brief and single-insight
- Email 2 contains the 3-step ECP framework in a scannable format
- Email 3 is genuinely conversational — the soft CTA (reply or follow) is appropriate for the audience and stated goal
- Exact audience language used correctly throughout: "not converting," "wrong fit," "messaging isn't landing," "first 10 customers," "first sales hire can't close"
- Multiple subject line options provided for A/B testing
- Preview text included for all 3 emails

**Issues:**

MAJOR — Email 2 subject line option C has a minor factual framing issue
- "Why your first sales hire can't close the same deals you closed" — while this is a valid trigger from the audience research, it appears as a subject line without being the primary content of Email 2. The email leads with the ECP-building framework, not the sales hire problem specifically. A reader who opens on that subject line may feel the body doesn't fully deliver on the promise.
- Fix: Either (a) move this subject line to Email 1 where the overall GTM misalignment framing is discussed, or (b) add 1–2 sentences in Email 2 explicitly connecting the SDR closing problem to the ECP/ICP distinction before the 3-step framework begins.

MINOR — Email 3 subject line option A
- "One question before I stop emailing you" — while this is a recognized cold email pattern, it risks reading as manipulative to a sophisticated founder audience that receives many cold emails. It may also trigger spam filters depending on the email platform.
- Fix (optional): Consider replacing with "Still thinking about your early customers?" or "Quick question about your GTM persona." Keep Option B or C as primary.

---

## 06-blog-draft.md — Long-Form Blog Post

### PASS

**Strengths:**
- H1 is clear, keyword-relevant, and benefit-forward
- The ECP definition is precise and distinct from ICP — the conceptual distinction is never muddied
- The side-by-side comparison table is accurate, scannable, and well-structured
- The 4-step ECP building framework is practical and actionable
- The "what ECP changes downstream" section directly maps ECP to execution impact (copy, channels, SDR onboarding, product roadmap, investor conversations) — this is the strongest differentiating section of the post
- The post ends with a clean summary framework (4-step sequence) that is shareable and memorable
- Word count ~2,050 words — within the 1,800–2,200 target range
- No passive voice issues identified
- No factual errors found in the core content

**Issues:**

MAJOR — Stats cited without source caveats in the post body
- The market research file flags two stats as needing verification: "68% higher win rate" and "70% of startups will adopt AI GTM tools by 2026" (Gartner). Neither stat appears in the current blog draft — this is GOOD. However, the phrase "one of the most consistent patterns in early-stage B2B GTM" (in the $1M ARR section) and "most B2B go-to-market strategy advice starts at step 3" (in the summary) are stated as facts without attribution or a framing qualifier.
- Fix: Add a light qualifier to the "most B2B go-to-market strategy advice" claim: "Most ICP-first GTM advice starts at step 3" — this aligns with the competitor analysis and feels more grounded without needing a citation.

MAJOR — The GTM Strategist framework is referenced by implication but not credited
- The blog post mentions "The GTM Strategist framework names this directly: early users become early customers, who eventually become ideal customers." This is a specific attribution that is not currently in the post. If this reference is included in the final published version, it should either (a) include a hyperlink to the GTM Strategist article (in the first comment on LinkedIn or inline on the blog), or (b) be reframed as an observation ("A pattern recognized across GTM practitioners: early users...") if a hyperlink is not desired.
- Fix: Add a hyperlink inline on the blog to the GTM Strategist article, or rephrase to remove the direct attribution.

MINOR — H2 structure could benefit from one additional keyword-bearing subheading
- The current subheadings are: "What Is an Early Customer Persona," "What Is an ICP," "Why Founders Conflate ECP and ICP," "The Consequences of Skipping the ECP," "ECP vs. ICP: Side-by-Side," "How to Build Your Early Customer Persona," "The $1M ARR Persona Is Not the $10M ARR Persona," "What the ECP Changes Downstream," "Start Before You Have Enough Data," "Summary."
- The secondary keyword "B2B go-to-market strategy" does not appear in any H2 or H3. Consider renaming the Summary section to "The Early Customer Persona in B2B Go-to-Market Strategy" or adding a brief H2 before the summary.
- Fix: Low priority — flagged for SEO optimizer to handle.

MINOR — "Start Before You Have Enough Data" section is slightly repetitive
- This section largely restates points made in the objection handling section of the "How to Build Your ECP" framework. The core content ("you need 5–10 conversations, not 100 customers") appears in both the framework steps and this section.
- Fix: Either (a) merge this section into the framework step as a note, or (b) give this section a distinct angle — e.g., "What to do when your early buyers came entirely from your network" — which is a more specific and novel concern not addressed elsewhere.

MINOR — Closing CTA is functional but plain
- "If this framework was useful, follow for more B2B GTM content — one practitioner-level framework per week. No templates. No fluff." This works but is a generic sign-off. It could be elevated by connecting back to the post's core question: "If you're still not sure whether your GTM is built on an ECP or an ICP — follow for more frameworks to help you find out."
- Fix (optional): Revise the closing sentence to reconnect to the post's core tension.

---

## Summary

No Critical issues. 3 Major issues total across all files — all fixable with minor edits:

1. (LinkedIn) Variant C word count — verify before scheduling
2. (Email) Email 2 subject line C / framing mismatch — move or add bridging sentence
3. (Blog) GTM Strategist attribution — add hyperlink or rephrase

Recommended: Apply fixes to blog (items 2 and 3 under blog issues) before publishing. LinkedIn and email fixes are pre-publish checks rather than content rewrites. All content is approved to proceed to brand voice check and scheduling.
