"""
QA Lint Skill
Post-generation compliance check against config.sequence_config rules.
Hard violations trigger one revision pass (see ClaudeClient.revise); warnings
are surfaced to the human reviewer but don't block a send on their own.
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.sequence_config import BANNED_PHRASES, SPAM_TRIGGER_WORDS, LINKEDIN_SCHEDULE


def lint(raw_output: str) -> dict:
    lower = raw_output.lower()

    violations = [
        f'Banned phrase found: "{phrase}"'
        for phrase in BANNED_PHRASES
        if phrase in lower
    ]
    violations.extend(_check_linkedin_word_limits(raw_output))

    warnings = [
        f'Spam-trigger word "{word}" appears {lower.count(word)}x'
        for word in SPAM_TRIGGER_WORDS
        if word in lower
    ]
    warnings.extend(_check_self_qa_flags(raw_output))

    return {
        "violations": violations,
        "warnings": warnings,
        "passed": len(violations) == 0,
    }


def _check_linkedin_word_limits(raw_output: str) -> list:
    """Flag LinkedIn steps that blow past their configured word limit by >30%."""
    issues = []
    parts = re.split(r"###\s+Step\s+(\d+)\s+—", raw_output)
    for i in range(1, len(parts), 2):
        step_num = parts[i]
        block = parts[i + 1] if i + 1 < len(parts) else ""
        schedule = LINKEDIN_SCHEDULE.get(f"step_{step_num}")
        if not schedule:
            continue
        msg_match = re.search(r"\*\*Message:\*\*\s*(.+?)(?:\n---|\Z)", block, re.DOTALL)
        if not msg_match:
            continue
        word_count = len(msg_match.group(1).strip().split())
        limit = schedule["max_words"]
        if word_count > limit * 1.3:
            issues.append(
                f"LinkedIn Step {step_num} is {word_count} words, over the {limit}-word limit"
            )
    return issues


def _check_self_qa_flags(raw_output: str) -> list:
    """Surface any 'N' answers the model gave itself in the Self-QA Checklist."""
    issues = []
    qa_match = re.search(r"## Self-QA Checklist(.+?)(?:\n##|\Z)", raw_output, re.DOTALL)
    if not qa_match:
        issues.append("Self-QA Checklist section missing from output")
        return issues
    for line in qa_match.group(1).splitlines():
        if re.search(r":\s*N\b", line):
            issues.append(f"Self-QA flagged: {line.strip('- ').strip()}")
    return issues
