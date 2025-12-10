from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ConversationState:
    flow: str = "idle"
    step: str = "inicio"
    data: Dict[str, Any] = field(default_factory=dict)


class ConversationStorage:
    def __init__(self):
        self._store: Dict[str, ConversationState] = {}

    def get(self, key: str) -> ConversationState:
        if key not in self._store:
            self._store[key] = ConversationState()
        return self._store[key]

    def save(self, key: str, state: ConversationState) -> None:
        self._store[key] = state
