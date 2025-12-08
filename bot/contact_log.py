"""Simple contact logging for inbound WhatsApp numbers."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONTACT_LOG_PATH = Path("data/contact_log.json")


def load_contact_log(log_path: Path | str = DEFAULT_CONTACT_LOG_PATH) -> List[Dict[str, Any]]:
    """Load the contact log from disk, returning an empty list if missing or invalid."""

    path = Path(log_path)
    if not path.exists():
        return []

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        logger.warning("Invalid contact log at %s: %s", path, exc)
        return []


def _format_timestamp(now: Optional[datetime] = None) -> str:
    timestamp = now or datetime.utcnow()
    return timestamp.isoformat()


def log_contact_number(
    number: str,
    *,
    log_path: Path | str = DEFAULT_CONTACT_LOG_PATH,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Append or update an entry for a contact number, returning the full log."""

    if not number:
        return []

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    entries = load_contact_log(path)
    timestamp = _format_timestamp(now)

    for entry in entries:
        if entry.get("number") == number:
            entry["last_seen"] = timestamp
            entry["count"] = entry.get("count", 1) + 1
            break
    else:
        entries.append(
            {
                "number": number,
                "first_seen": timestamp,
                "last_seen": timestamp,
                "count": 1,
            }
        )

    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
    return entries
