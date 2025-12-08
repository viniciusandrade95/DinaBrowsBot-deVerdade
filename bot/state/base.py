"""State store interfaces and session models."""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Protocol


@dataclass
class SessionState:
    tenant_id: str
    user_id: str
    flow: str = "IDLE"
    step: str = "NONE"
    context: Dict[str, Any] = field(default_factory=dict)
    last_updated: float = field(default_factory=lambda: time.time())

    def touch(self) -> None:
        """Update last_updated to current time."""
        self.last_updated = time.time()

    def reset(self) -> None:
        """Clear conversational context to start a fresh workflow."""
        self.flow = "IDLE"
        self.step = "NONE"
        self.context = {}
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        return cls(
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id", ""),
            flow=data.get("flow", "IDLE"),
            step=data.get("step", "NONE"),
            context=data.get("context") or {},
            last_updated=data.get("last_updated") or time.time(),
        )


class StateStore(Protocol):
    """Abstract interface for loading and persisting session state."""

    def get_session(self, tenant_id: str, session_id: str) -> SessionState:
        """Return session state for a tenant and session; create default if missing."""

    def save_session(self, state: SessionState) -> None:
        """Persist the full session state."""

    def delete_session(self, tenant_id: str, session_id: str) -> None:
        """Delete a session if it exists without raising if it does not."""

    def append_event(self, tenant_id: str, session_id: str, event: Dict[str, Any]) -> None:
        """Append an event to the session history; base implementations may be simple."""
