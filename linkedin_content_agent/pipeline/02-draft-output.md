# Phase 2: Writer Draft Output
**Topic**: Day 14 — Building multi-agent collaboration systems
**Date**: 2026-03-15

---

POST DRAFT:

I built a 4-agent AI system. The hardest part had nothing to do with AI.

Day 14 of building in public — and today's system exposed something most multi-agent tutorials quietly skip over.

The pipeline: 4 specialized agents (researcher → writer → QA → optimizer) working sequentially to produce LinkedIn content. Each agent hands off to the next via a structured file. Simple concept. Surprisingly hard to get right.

Here's what actually makes it work:

**Context isolation is a feature, not a bug.**
Each agent receives only what it needs. The writer never sees raw research noise. The optimizer never second-guesses the QA verdict. Narrow context produces sharper output — not dumber agents. The researcher outputs a 300–500 token brief. That constraint is intentional design.

**File handoffs beat API chaining.**
research_brief.txt → draft.txt → qa_feedback.txt → final.txt

Every stage is inspectable, replayable, debuggable. Black-box pipelines fail silently. File-based pipelines fail loudly — and that's exactly what you want in production.

**Quality gates separate demos from real systems.**
The QA agent evaluates against a rubric: hook strength, insight depth, CTA clarity. It can reject a draft and force a rewrite loop. Without a hard gate, you're just chaining prompts. A real gate changes the system's reliability profile entirely.

Four agents with one job each compound their strengths. One monolithic prompt with 10 instructions fights itself.

The teams shipping reliable agentic systems aren't using fancier models.
They're using better orchestration patterns.

What's your current approach to agent handoffs?

---
METADATA:
Character count: 1,247
Word count: 228
Estimated read time: 55 seconds
Hook used: "I built a 4-agent AI system. The hardest part had nothing to do with AI."

NOTES FOR QA:
- Chose Pattern 1 (Problem-Solution-Result)
- Bold section headers for scannability
- File chain used as concrete visual anchor
- Closing question to drive comments
- No emojis — practitioner tone
- Day 14 placed line 2 to preserve opener strength
