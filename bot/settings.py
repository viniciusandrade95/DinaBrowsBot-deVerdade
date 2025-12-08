"""Runtime wiring for pluggable bot components."""
from __future__ import annotations

import os
from pathlib import Path

from bot.state import FileStateStore, InMemoryStateStore, StateStore


def build_state_store() -> StateStore:
    """Choose a StateStore implementation based on environment settings."""
    backend = os.environ.get("STATE_STORE_BACKEND", "file").lower()
    if backend == "memory":
        return InMemoryStateStore()

    base_path = Path(os.environ.get("STATE_STORE_PATH", "data/sessions"))
    return FileStateStore(base_path=base_path)
