"""
Lightweight local session persistence.

Each run of the agent (per business idea) gets one JSON file under
./sessions/. This lets you run `init`, then `discover`, then `plan`
as separate terminal commands — each phase reads what the previous
phase wrote, so you're never forced through the whole pipeline in
one sitting.
"""
import json
import os
import re
from datetime import datetime, timezone

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")


def _slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len] or "session"


def session_path(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def new_session_id(product_idea: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{_slugify(product_idea)}"


def load(session_id: str) -> dict:
    path = session_path(session_id)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No session found at {path}. Run `init` first, or pass "
            f"the correct --session <id>."
        )
    with open(path, "r") as f:
        return json.load(f)


def save(session_id: str, data: dict) -> None:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    data["_updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(session_path(session_id), "w") as f:
        json.dump(data, f, indent=2)


def latest_session_id() -> str:
    """Convenience for `--session latest` — grabs the most recently updated session."""
    if not os.path.isdir(SESSIONS_DIR):
        raise FileNotFoundError("No sessions directory yet — run `init` first.")
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No sessions found — run `init` first.")
    files.sort(key=lambda f: os.path.getmtime(session_path(f[:-5])), reverse=True)
    return files[0][:-5]
