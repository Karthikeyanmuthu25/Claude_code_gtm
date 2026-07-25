"""
Nurture Sequence Configuration
Based on the 14-21 Day framework to convert cold leads into MQLs.

SEQUENCE STRUCTURE:
  Day 0  → Asset Delivery     (Deliver what they asked for. No pitch.)
  Day 1  → Hot Button 1       (Most pressing pain point)
  Day 3  → Hot Button 2       (Secondary pain that keeps them stuck)
  Day 5  → Hot Button 3       (Hidden/overlooked third pain. Introduce framework.)
  Day 14 → Probing Question   (Simple honest question. Invite conversation.)
  Day 21 → Breakup Email      (Close loop. Offer easy way back in.)

LINKEDIN SEQUENCE (parallel, 4-step):
  Step 1 → Connection Request  (1-2 lines, personal, zero pitch)
  Step 2 → Post-accept warm    (After connected — one curiosity trigger)
  Step 3 → Follow-up value     (Reference pain point 1 or 2)
  Step 4 → Soft close          (Brief, graceful, leave door open)
"""

# Day schedule for email sequence
EMAIL_SCHEDULE = {
    "day_0": {
        "label": "Asset Delivery",
        "purpose": "Deliver what they requested. Avoid fluff.",
        "subject_pattern": "Here's your [Asset Name]",
        "strategy": [
            "Deliver what they asked for immediately",
            "No sales pitch in this email",
            "Set expectation for follow-up",
        ],
        "tone": "Helpful, immediate, zero pitch",
    },
    "day_1": {
        "label": "Hot Button 1",
        "purpose": "Speak directly to the most pressing pain point.",
        "subject_pattern": "The #1 reason [ICP] can't [achieve outcome]",
        "strategy": [
            "Name the observable pain (not your solution yet)",
            "Use Problem-Agitate-Solution framework",
            "Include relevant case study or statistic",
        ],
        "tone": "Empathetic, insightful, no solution push yet",
    },
    "day_3": {
        "label": "Hot Button 2",
        "purpose": "Follow up with the second pain point that keeps them stuck.",
        "subject_pattern": "Why [pain point #2] is costing you [outcome]",
        "strategy": [
            "Address the secondary pain point",
            "Show the compounding effect of inaction",
            "Share a 'how we solved this' story",
        ],
        "tone": "Story-driven, relatable, still not pitching hard",
    },
    "day_5": {
        "label": "Hot Button 3",
        "purpose": "Hit the third. By this point, they're paying attention.",
        "subject_pattern": "The hidden cost of [pain point #3]",
        "strategy": [
            "Address the third pain point (often overlooked)",
            "Connect all three pains to show systemic issue",
            "Introduce your framework/methodology (not product yet)",
        ],
        "tone": "Educational, connecting-dots, light framework intro",
    },
    "day_14": {
        "label": "Probing Question",
        "purpose": "Ask a simple, honest question that invites a conversation.",
        "subject_pattern": "Quick question about [their situation]",
        "strategy": [
            "Reference the pain points mentioned in previous emails",
            "Ask a clear diagnostic question",
            "Make it easy to reply and show genuine curiosity (no sales pressure)",
        ],
        "tone": "Human, curious, conversational, zero pressure",
    },
    "day_21": {
        "label": "Breakup Email",
        "purpose": "If there's no response, close the loop and move them to long-term nurture.",
        "subject_pattern": "Closing the loop",
        "strategy": [
            "Offer to stay in touch differently (newsletter, resources)",
            "Give them an easy out OR easy way back in",
            "Leave door open for future",
        ],
        "tone": "Graceful, brief, no guilt, genuinely warm",
    },
}

# LinkedIn sequence steps
LINKEDIN_SCHEDULE = {
    "step_1": {
        "label": "Connection Request",
        "timing": "Day 0 — send before or alongside first email",
        "purpose": "Get connected. Zero pitch.",
        "rules": [
            "1-2 lines maximum",
            "Reference something real about their work",
            "No mention of product or offer",
            "Personal, not templated-sounding",
        ],
        "max_words": 40,
    },
    "step_2": {
        "label": "Message After Accepted",
        "timing": "Day 1-2 — after they accept",
        "purpose": "Warm opener. One curiosity trigger.",
        "rules": [
            "3-5 lines maximum",
            "Reference their specific role or company",
            "One question or observation — not a pitch",
            "Natural and human",
        ],
        "max_words": 80,
    },
    "step_3": {
        "label": "Follow-up with Relevance",
        "timing": "Day 5-7",
        "purpose": "Add context. Reference a pain point from the email thread.",
        "rules": [
            "Share one specific insight or stat relevant to their situation",
            "Reference the email sequence or a pain point briefly",
            "Soft offer to share framework or resource",
            "4-6 lines max",
        ],
        "max_words": 100,
    },
    "step_4": {
        "label": "Final Soft Follow-up",
        "timing": "Day 14-21",
        "purpose": "Brief, graceful close. Leave door open.",
        "rules": [
            "2-3 lines maximum",
            "No guilt or pressure",
            "Easy yes or easy pass",
            "Leave door open genuinely",
        ],
        "max_words": 60,
    },
}

# Phrases the model is instructed never to use. Shared source of truth between
# the prompt (sequence_skill.py) and the post-generation lint (qa_lint_skill.py)
# so the rule is actually enforced, not just requested.
BANNED_PHRASES = [
    "i hope this finds you well",
    "i hope this email finds you well",
    "i've been following your journey",
    "i have been following your journey",
    "your company is doing amazing work",
    "your company is doing great work",
    "just circling back",
    "just checking in",
    "touching base",
    "reaching out because",
    "hope you're doing well",
    "hope all is well",
]

# Common cold-email spam/deliverability triggers. Flagged as warnings (not
# auto-blocked) since some are context-dependent — a human should confirm.
SPAM_TRIGGER_WORDS = [
    "free", "guarantee", "guaranteed", "act now", "limited time",
    "click here", "risk-free", "no obligation", "100% free",
    "no cost", "cash bonus", "act immediately", "urgent", "winner",
    "congratulations", "special promotion", "as seen on",
]
