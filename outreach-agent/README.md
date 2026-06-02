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
│   └── sequence_config.py                ← Day schedule, timing rules, writing guidelines
│
├── output/                               ← Reports saved here (auto-created)
│
└── src/
    ├── agents/
    │   └── nurture_agent.py              ← Main orchestration agent
    │
    ├── tools/
    │   ├── claude_client.py              ← Anthropic SDK wrapper
    │   ├── input_collector.py            ← Interactive CLI + JSON loader
    │   └── output_formatter.py           ← Saves .md report + .json data
    │
    └── skills/
        ├── personalization_skill.py      ← Profile analysis, pain point extraction
        └── sequence_skill.py             ← Builds full Claude prompt
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

1. **Write real, specific receiver summaries** — generic profiles = generic output
2. **Use their actual language** for pain points (copy from LinkedIn/G2 reviews/Slack)
3. **The asset name matters** — a specific asset beats "N/A" for Day 0 personalization
4. **Review Notes for Human Review section** before sending anything
5. Use `sequence_type: "Email"` if you only need the email track

---

## License

MIT — Use freely for your outreach campaigns.
