"""File-backed StateStore implementation for development use."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from .base import SessionState, StateStore

logger = logging.getLogger(__name__)


class FileStateStore(StateStore):
    """Persist session state as JSON files under a base directory."""

    def __init__(self, base_path: Path | str = Path("data/sessions")):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _session_path(self, tenant_id: str, session_id: str) -> Path:
        safe_tenant = tenant_id.replace("/", "_")
        safe_session = session_id.replace("/", "_")
        filename = f"{safe_tenant}__{safe_session}.json"
        return self.base_path / filename

    def get_session(self, tenant_id: str, session_id: str) -> SessionState:
        path = self._session_path(tenant_id, session_id)
        if not path.exists():
            return SessionState(tenant_id=tenant_id, user_id=session_id)

        try:
            data: Dict[str, Any] = json.loads(path.read_text())
            return SessionState.from_dict(data)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to read session file %s: %s", path, exc)
            return SessionState(tenant_id=tenant_id, user_id=session_id)

    def save_session(self, state: SessionState) -> None:
        path = self._session_path(state.tenant_id, state.user_id)
        path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))

    def delete_session(self, tenant_id: str, session_id: str) -> None:
        path = self._session_path(tenant_id, session_id)
        if path.exists():
            try:
                path.unlink()
            except OSError as exc:  # pragma: no cover - defensive
                logger.exception("Failed to delete session file %s: %s", path, exc)

    def append_event(self, tenant_id: str, session_id: str, event: Dict[str, Any]) -> None:
        session = self.get_session(tenant_id, session_id)
        events = session.context.setdefault("events", [])
        events.append(event)
        session.touch()
        self.save_session(session)
