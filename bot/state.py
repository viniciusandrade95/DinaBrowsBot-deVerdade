# bot/state.py
from dataclasses import dataclass
from typing import Dict, Any
import time


@dataclass
class SessionState:
    tenant_id: str
    user_id: str
    flow: str = "IDLE"
    step: str = "NONE"
    context: Dict[str, Any] = None
    last_updated: float = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.last_updated is None:
            self.last_updated = time.time()


class StateStore:
    """Abstract session state store (e.g. Redis/DB)."""

    def load_state(self, tenant_id: str, user_id: str) -> SessionState:
        raise NotImplementedError

    def save_state(self, state: SessionState) -> None:
        raise NotImplementedError


class InMemoryStateStore(StateStore):
    """Non-production, just for dev/tests."""

    def __init__(self):
        self._store: Dict[str, SessionState] = {}

    def _key(self, tenant_id: str, user_id: str) -> str:
        return f"{tenant_id}:{user_id}"

    def load_state(self, tenant_id: str, user_id: str) -> SessionState:
        key = self._key(tenant_id, user_id)
        if key not in self._store:
            self._store[key] = SessionState(tenant_id=tenant_id, user_id=user_id)
        return self._store[key]

    def save_state(self, state: SessionState) -> None:
        key = self._key(state.tenant_id, state.user_id)
        self._store[key] = state
