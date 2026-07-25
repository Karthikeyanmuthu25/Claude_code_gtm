# Outbound Brain

Living knowledge store for the nurture agent. This is **field-tested pattern
memory**, not framework structure (structure lives in `config/sequence_config.py`).
The prompt builder (`src/skills/sequence_skill.py`) injects the relevant parts of
this file into every generation so the model works from real experience instead
of starting cold each time.

Entries get added here two ways:
- `scripts/promote_to_brain.py` — promote a human-approved or high-reply sequence
- Manually, when you notice a pattern worth keeping

Keep entries short and reusable. Delete entries that stop working — this file
should reflect what's working *now*, not an archive of everything ever sent.

---

## Angle patterns that have worked

- **"Embedded operator, not advisor" angle** — for ops/COO-type offers, position
  the sender as someone who does the work alongside the team, not someone who
  delivers a deck and leaves. Landed well for fractional-COO-style offers into
  Head of Asset Management / GM roles (real estate, franchise ops).
- **Structural-tension framing** — name the specific gap between the receiver's
  accountability and their authority/tooling (e.g. "full accountability for
  network outcomes without full authority over the franchisees"). Works when the
  receiver is a senior operator managing something that scaled past its original
  process design.
- **Regional/practical-advantage angle** — for physical-product/manufacturing
  offers into hospitality or facilities buyers, lead with a concrete logistics or
  compliance edge (e.g. GCC-based manufacturing = faster turnaround + easier
  brand-standard compliance for a luxury hotel group) rather than product specs.

## Subject lines that tested well (by pattern, not literal reuse)

- Day 0: `"[Specific asset/framework name] for [receiver's specific situation]"`
  — beats generic "Here's your [asset]". Naming the situation, not just the
  asset, increases relevance signal in the subject line itself.
- Day 1: naming the mechanism of the pain, not the pain itself —
  `"The reporting lag problem at scale"` outperforms `"Are you struggling with
  reporting?"` in tone (diagnostic, not interrogative).
- Day 14: `"Quick question, [Name]"` — plain, low-effort-looking subject lines
  get opened more at the probing-question stage than clever ones.

## Objection-handling notes

- **"We already have a PM/vendor for this"** — don't argue against the existing
  relationship. Reframe around the coordination/reporting layer *above* the
  existing vendor, not replacing it.
- **No response after Day 5** — do not add a second reason to reply in the Day 14
  email. One honest question outperforms stacking more value props.
- **Recipient is clearly not the decision-maker** — flag for human review before
  Day 1 sends; do not let the sequence run assuming buying authority the profile
  doesn't support.

## Per-vertical notes

### Real estate / franchise operations
Buyers here (GM, Head of Asset/Portfolio Management) respond to language about
scaling infrastructure vs. scaling headcount. Avoid marketing/SaaS vocabulary
("pipeline", "MQL", "ICP") entirely — it reads as obviously mismatched to their
world and undermines credibility in the first line. See BMC Investments and
RE/MAX outputs for reference tone.

### Hospitality / F&B equipment & fit-out
Buyers (Director of F&B, procurement) respond to brand-standard-compliance
framing and delivery-timeline confidence more than price or product range.
Regional manufacturing proximity is a real differentiator worth leading with.

---

## Known heuristic failure — do not repeat

The old rule-based `_infer_connection_angle()` keyword matcher guessed a
"pipeline quality / time-to-MQL" angle for a real-estate asset-management buyer
(BMC Investments) purely because the offer text contained GTM-flavored words.
The model had to catch and override this itself in the Notes for Human Review.
**Lesson:** never assert a connection angle from keyword matching on the offer
text alone — derive it from the receiver's actual role/summary, and treat
generic SaaS/GTM vocabulary as a signal to *avoid*, not match on, for
non-SaaS buyers.
