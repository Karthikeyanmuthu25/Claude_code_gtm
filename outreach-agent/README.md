# 14-21 Day Nurture Sequence Agent

**Converts cold leads into MQLs using the Dev Basu framework · Powered by Claude**

---

## What It Does

You provide two short profile summaries (sender + receiver) and your ICP pain points.

The agent generates a **complete, personalized 14-21 day nurture sequence**:

### Email Sequence (6 emails)
| Day | Type | Purpose |
|-----|------|---------|
| Day 0 | Asset Delivery | Deliver lead asset. No pitch. Set the expectation. |
| Day 1 | Hot Button 1 | Name the #1 pain. Problem-Agitate-Solution. No product push. |
| Day 3 | Hot Button 2 | Secondary pain. Compounding effect. Share a story. |
| Day 5 | Hot Button 3 | Third pain. Connect all 3. Introduce your framework (not product). |
| Day 14 | Probing Question | One honest diagnostic question. Zero pressure. |
| Day 21 | Breakup Email | Close loop. Easy out + easy way back in. |

### LinkedIn Sequence (4 steps, runs in parallel)
| Step | Type | Timing |
|------|------|--------|
| Step 1 | Connection Request | Day 0 — personal, 1-2 lines, zero pitch |
| Step 2 | Post-accept warm message | Day 1-2 — one curiosity trigger |
| Step 3 | Follow-up with relevance | Day 5-7 — reference pain, soft resource offer |
| Step 4 | Final soft follow-up | Day 14-21 — graceful close, leave door open |

---

## Project Structure

```
outreach-agent-v2/
├── main.py                               ← CLI entry point
├── requirements.txt                      ← Only: anthropic
├── sample_input.json                     ← Pre-filled test data
├── README.md
│
├── config/
│   └── sequence_config.py                ← Day schedule, timing rules, banned phrases, spam words
│
├── knowledge/
│   └── brain.md                          ← Living swipe file: proven angles, subject lines,
│                                            objection handling, per-vertical notes. Injected
│                                            into every prompt. Grows via scripts/promote_to_brain.py
│
├── output/                               ← Reports saved here (auto-created).
│                                            Each .json also carries fit_report, lint_report,
│                                            review{}, and outcomes{} — see below.
│
├── scripts/
│   ├── log_outcome.py                    ← Record opens/replies/meetings/bounces per touch
│   ├── review.py                         ← Record human approve/edit/reject + edited text
│   ├── analyze_outcomes.py               ← Aggregate reply rate by touch and by fit score
│   └── promote_to_brain.py               ← Promote an approved/high-reply pattern into brain.md
│
└── src/
    ├── agents/
    │   └── nurture_agent.py              ← Orchestrates: fit gate → personalize → prompt →
    │                                        generate → lint → revise (if needed) → save
    │
    ├── tools/
    │   ├── claude_client.py              ← Anthropic SDK wrapper (generate + revise)
    │   ├── input_collector.py            ← Interactive CLI + JSON loader
    │   └── output_formatter.py           ← Saves .md report + .json data (+ QA/review/outcomes)
    │
    └── skills/
        ├── personalization_skill.py      ← Profile analysis, pain point extraction
        ├── sequence_skill.py             ← Builds full Claude prompt, injects brain.md
        ├── icp_fit_skill.py              ← Pre-generation lead fit score (0-100)
        └── qa_lint_skill.py              ← Post-generation rule-compliance check
```

---

## Setup (3 steps)

### Step 1 — Install Python dependency

```bash
pip install -r requirements.txt
```

### Step 2 — Set your Anthropic API key

```bash
# Mac / Linux
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows Command Prompt
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Get your key at: https://console.anthropic.com

### Step 3 — Run

```bash
# Quick test with sample data
python main.py --input sample_input.json

# Interactive mode (fill details in terminal)
python main.py

# Abort before generating if the lead's ICP fit score is below 60
python main.py --input sample_input.json --min-fit-score 60
```

---

## Input JSON Format

```json
{
  "sender_name": "Your Name",
  "sender_role": "Your Role",
  "sender_company": "Your Company",
  "sender_summary": "2-4 sentences about your background and expertise.",

  "receiver_name": "Target Name",
  "receiver_role": "Their Role",
  "receiver_company": "Their Company",
  "receiver_summary": "2-4 sentences about their role, company stage, and business context.",

  "outreach_goal": "What you want to achieve (e.g. Book a 20-min discovery call)",
  "offer": "What you're offering and why it matters to them.",
  "asset_name": "Name of your lead magnet for Day 0 (or 'N/A')",
  "pain_points": "Pain 1, Pain 2, Pain 3  (comma-separated or one per line)",
  "tone": "e.g. Friendly peer-level, Direct and professional",
  "sequence_type": "Email | LinkedIn | Both"
}
```

---

## Output

Reports saved to `output/` folder:

- `nurture_<receiver>_<company>_<timestamp>.md` — Full sequence (Markdown)
- `nurture_<receiver>_<company>_<timestamp>.json` — Full data including inputs

Open the `.md` file in:
- VS Code (with Markdown Preview)
- Obsidian
- Notion (import)
- markdownlivepreview.com

Every `.md` report now opens with a **Pre-Send QA** table (ICP fit score, lint
status, any unresolved violations/warnings) right under the campaign overview.

---

## What Happens on Every Run

```
1. ICP Fit Gate     → score_fit() scores input completeness/specificity 0-100.
                       Low score = you're about to generate a generic sequence
                       off a thin brief. Doesn't block unless --min-fit-score is set.
2. Personalization  → extract hooks, pain points. (No more keyword-guessed
                       connection angle — the LLM derives that itself from the
                       receiver's actual profile, see knowledge/brain.md →
                       "Known heuristic failure" for why that changed.)
3. Prompt Build     → sequence_config.py rules + knowledge/brain.md's proven
                       patterns are both injected into the prompt.
4. Generate         → single Claude call.
5. Lint             → qa_lint_skill checks banned phrases, spam words, LinkedIn
                       word limits, and the model's own Self-QA answers.
                       Hard violations trigger one automatic revise() pass.
6. Save             → .md + .json, with review{} and outcomes{} skeletons ready
                       to be filled in as the sequence actually gets used.
```

## Closing the Loop — Review, Send, Measure, Learn

The agent generating a good-looking sequence once is not the same as the
system getting better over time. That requires actually recording what
happened and feeding it back in:

```bash
# 1. Human reviews the draft before it goes out
python scripts/review.py --file output/nurture_x.json --status approved --reviewer "Karthikeyan"
# ...or, if you edited the copy before sending, capture the diff:
python scripts/review.py --file output/nurture_x.json --status edited \
    --reviewer "Karthikeyan" --edited-text-file output/nurture_x_edited.md

# 2. After sending, log what actually happened per touch
python scripts/log_outcome.py --file output/nurture_x.json --touch day_1 --replied true

# 3. Periodically, see what's working across every sequence you've sent
python scripts/analyze_outcomes.py

# 4. Promote a confirmed winning pattern into the shared knowledge base
python scripts/promote_to_brain.py --file output/nurture_x.json \
    --section "Angle patterns that have worked" \
    --note "Naming the specific compliance/timeline edge up front worked for facilities buyers."
```

`knowledge/brain.md` is what every future prompt reads from — this is the
mechanism that turns individual sends into compounding institutional
knowledge instead of one-off documents nobody re-reads.

---

## Framework Source

Sequence structure adapted from **Dev Basu / Powered By Search**:
*"14-21 Day Nurture Sequence to Convert 10-20% of Cold Leads Into MQLs"*

Key principles:
- Day 0: Pure value delivery. Zero pitch.
- Days 1-5: Pain-first. Education before solution.
- Day 14: Honest conversation starter.
- Day 21: Graceful exit. Always leave door open.

---

## Tips for Best Results

1. **Write real, specific receiver summaries** — generic profiles = generic output.
   A thin summary now also tanks your ICP Fit Score (check the Pre-Send QA table).
2. **Use their actual language** for pain points (copy from LinkedIn/G2 reviews/Slack)
3. **The asset name matters** — a specific asset beats "N/A" for Day 0 personalization
4. **Review the Self-QA Checklist and Notes for Human Review** before sending anything,
   then record your decision with `scripts/review.py` so it's tracked, not just read
5. Use `sequence_type: "Email"` if you only need the email track
6. **Log outcomes after you send** (`scripts/log_outcome.py`) — the system can only
   get smarter than the first draft if real replies/meetings get fed back in
7. **Update `knowledge/brain.md`** as you learn what's working per vertical —
   it's read into every prompt going forward

---

## License

MIT — Use freely for your outreach campaigns.
