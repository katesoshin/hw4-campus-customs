"""Append-only audit log of agent-loop activity.

Each record is one JSON object on its own line in output/audit_trail.json (JSON Lines), written
in append mode so the file is never wiped between runs. Records capture: time, run id, event,
tool name, short args/result, and stop reason.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from config import HW4_DIR

AUDIT_FILE = HW4_DIR / "output" / "audit_trail.json"


def _short(value, limit: int = 200) -> str:
    """Compact, truncated string form of args/results so the log stays readable."""
    if value is None:
        return ""
    try:
        text = value if isinstance(value, str) else json.dumps(value, default=str)
    except TypeError:
        text = str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def append_audit(
    run_id: str,
    event: str,
    *,
    tool_name: str | None = None,
    args=None,
    result=None,
    stop_reason: str | None = None,
) -> None:
    """Append one audit record (never overwrites existing history)."""
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "event": event,
        "tool_name": tool_name,
        "args": _short(args),
        "result": _short(result),
        "stop_reason": stop_reason,
    }
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
