"""In-memory StateStore for development and tests."""
from __future__ import annotations

from typing import Dict

from .base import SessionState, StateStore


class InMemoryStateStore(StateStore):
    def __init__(self):
        self._store: Dict[str, SessionState] = {}

    def _key(self, tenant_id: str, session_id: str) -> str:
        return f"{tenant_id}:{session_id}"

    def get_session(self, tenant_id: str, session_id: str) -> SessionState:
        key = self._key(tenant_id, session_id)
        if key not in self._store:
            self._store[key] = SessionState(tenant_id=tenant_id, user_id=session_id)
        return self._store[key]

    def save_session(self, state: SessionState) -> None:
        key = self._key(state.tenant_id, state.user_id)
        self._store[key] = state

    def delete_session(self, tenant_id: str, session_id: str) -> None:
        self._store.pop(self._key(tenant_id, session_id), None)

    def append_event(self, tenant_id: str, session_id: str, event: dict) -> None:
        session = self.get_session(tenant_id, session_id)
        session.context.setdefault("events", []).append(event)
        session.touch()
        self.save_session(session)
