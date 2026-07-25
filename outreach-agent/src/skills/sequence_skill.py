"""
Sequence Skill
Constructs the full Claude prompt for the 14-21 Day Nurture Sequence.
Follows the framework: Asset Delivery → Hot Button 1 → Hot Button 2 →
Hot Button 3 → Probing Question → Breakup Email.
Parallel LinkedIn: Connection → Post-accept → Follow-up → Soft close.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.sequence_config import EMAIL_SCHEDULE, LINKEDIN_SCHEDULE, BANNED_PHRASES

BRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "brain.md")


def _load_brain() -> str:
    """Read the accumulated field-knowledge file, if it exists."""
    if not os.path.exists(BRAIN_PATH):
        return ""
    with open(BRAIN_PATH, encoding="utf-8") as f:
        return f.read().strip()


def build_sequence_prompt(inputs: dict, ctx: dict) -> str:
    seq_type = inputs.get("sequence_type", "Both")
    generate_email = seq_type in ["Email", "Both"]
    generate_linkedin = seq_type in ["LinkedIn", "Both"]

    hb = ctx.get("hot_button_map", {})
    hooks_text = "\n".join(f"  - {h}" for h in ctx.get("receiver_hooks", []))
    pain_block = (
        f"  → Hot Button 1: {hb.get('hot_button_1', '')}\n"
        f"  → Hot Button 2: {hb.get('hot_button_2', '')}\n"
        f"  → Hot Button 3: {hb.get('hot_button_3', '')}"
    )

    brain = _load_brain()
    brain_block = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROVEN KNOWLEDGE BASE (field-tested — use what's relevant, ignore what isn't)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{brain}
""" if brain else ""

    prompt = f"""
You are a B2B outreach copywriter specializing in 14-21 day cold-to-warm nurture sequences.

Your task: Generate a complete personalized nurture sequence based on the profiles below.
The sequence follows the Dev Basu / Powered By Search framework that converts 10-20% of cold leads into MQLs.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SENDER PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {inputs.get("sender_name", "")}
Role: {inputs.get("sender_role", "")}
Company: {inputs.get("sender_company", "")}
Summary: {inputs.get("sender_summary", "")}
Credibility anchor: {ctx.get("sender_credibility", "")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECEIVER / TARGET PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {inputs.get("receiver_name", "")}
Role: {inputs.get("receiver_role", "")}
Company: {inputs.get("receiver_company", "")}
Summary: {inputs.get("receiver_summary", "")}

Personalization hooks:
{hooks_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTREACH PARAMETERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: {inputs.get("outreach_goal", "")}
Offer: {inputs.get("offer", "")}
Asset (Day 0): {inputs.get("asset_name", "N/A")}
Tone: {inputs.get("tone", "Friendly and professional")}
Sequence type: {seq_type}

Determine the connection angle yourself from the receiver's actual role, company,
and summary above — do not default to generic SaaS/GTM language ("pipeline",
"MQL", "ICP") unless the receiver's own world genuinely is SaaS/GTM. State the
angle you chose and why in the Outreach Angle section.

ICP Pain Points (Hot Buttons):
{pain_block}
{brain_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NURTURE SEQUENCE FRAMEWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Follow this exact structure and timing:

EMAIL SEQUENCE (6 emails):
  Day 0  — Asset Delivery: Deliver the asset. No pitch. Set expectation.
  Day 1  — Hot Button 1:   Name the #1 pain. Problem-Agitate-Solution. No product push.
  Day 3  — Hot Button 2:   Secondary pain. Compounding effect. Share a "how we solved this" story.
  Day 5  — Hot Button 3:   Third (often overlooked) pain. Connect all 3. Introduce your FRAMEWORK only (not product).
  Day 14 — Probing Question: One honest diagnostic question. Reference prior emails. Zero pressure.
  Day 21 — Breakup Email:  Close the loop. Offer newsletter/resources. Easy out + easy way back in.

LINKEDIN SEQUENCE (parallel, 4 steps):
  Step 1 — Connection Request:  Day 0. 1-2 lines. Personal. Zero pitch.
  Step 2 — Post-accept warm:    Day 1-2. 3-5 lines. One curiosity trigger. Not a pitch.
  Step 3 — Follow-up value:     Day 5-7. 4-6 lines. Reference pain point. Soft resource offer.
  Step 4 — Soft close:          Day 14-21. 2-3 lines. Brief. Graceful. Leave door open.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT WRITING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEVER:
→ Use any of these banned phrases (or close variations): {", ".join(f'"{p}"' for p in BANNED_PHRASES)}
→ Pitch the product in Day 0 or Day 1 emails
→ Write long paragraphs (3 sentences max per paragraph)
→ Be pushy, guilt-trip, or create false urgency

ALWAYS:
→ Open every email with a line about THEIR world, not yours
→ Name specific pain using language they'd use (not corporate speak)
→ Keep LinkedIn messages SHORT — strictly within word limits
→ Use one soft CTA per email (not multiple asks)
→ Day 0 email: deliver value immediately, no pitch at all
→ Day 21 breakup: genuinely warm, no guilt, easy exit
→ Subject lines: specific and curiosity-driven, NOT clickbait
→ Personalize using receiver's role, company stage, and context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIRED OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return output in EXACTLY this structure:

## Outreach Angle

## Personalization Summary

{_email_block(generate_email)}

{_linkedin_block(generate_linkedin)}

## Self-QA Checklist

Answer each honestly, Y/N, after writing the sequence above (not before):
- Connection angle grounded in receiver's actual role/summary (not generic GTM language unless genuinely applicable): Y/N — why
- Day 0 and Day 1 contain zero product pitch: Y/N
- No banned phrase or close variation appears anywhere: Y/N
- Every LinkedIn step is within its word limit: Y/N
- Subject lines are specific and curiosity-driven, not clickbait: Y/N
- Receiver's actual decision-making authority for this offer is clear from the profile (flag below if uncertain): Y/N

## Notes for Human Review

Flag anything a human should verify before sending: uncertain claims, assumptions
about authority/fit, asset/link placeholders, or any Self-QA "N" answers above.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now generate the complete sequence. Be specific, human, and personalized.
"""
    return prompt.strip()


def _email_block(generate: bool) -> str:
    if not generate:
        return ""
    return """## Email Sequence

### Day 0 — Asset Delivery
**Send timing:** Immediately after opt-in or first contact
**Subject:**
**Body:**

---

### Day 1 — Hot Button 1
**Send timing:** 1 day after Day 0
**Subject:**
**Body:**

---

### Day 3 — Hot Button 2
**Send timing:** 3 days after Day 0
**Subject:**
**Body:**

---

### Day 5 — Hot Button 3
**Send timing:** 5 days after Day 0
**Subject:**
**Body:**

---

### Day 14 — Probing Question
**Send timing:** 14 days after Day 0
**Subject:**
**Body:**

---

### Day 21 — Breakup Email
**Send timing:** 21 days after Day 0
**Subject:**
**Body:**"""


def _linkedin_block(generate: bool) -> str:
    if not generate:
        return ""
    return """## LinkedIn Sequence

### Step 1 — Connection Request
**Timing:** Day 0 (send alongside or before first email)
**Message:**

---

### Step 2 — Message After Accepted
**Timing:** Day 1-2 (after connection accepted)
**Message:**

---

### Step 3 — Follow-up with Relevance
**Timing:** Day 5-7
**Message:**

---

### Step 4 — Final Soft Follow-up
**Timing:** Day 14-21
**Message:**"""
