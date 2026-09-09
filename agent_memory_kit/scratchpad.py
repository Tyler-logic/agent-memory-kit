"""Pattern 1: structured scratchpad state.

Facts that matter get promoted out of freeform conversation into an explicit
block that is re-injected into every prompt, so they never age out of a
truncated context window and never get diluted by competing with tool noise.
"""
from __future__ import annotations

import json
from typing import Any


class ScratchpadState:
    """A small, explicit bag of facts an agent must not forget or contradict.

    Deliberately *not* meant to scale to "remember everything" — that's what
    FuzzyRecall (Pattern 2) is for. This is for the handful of facts that
    should be resident on every single turn.
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {
            "user_prefs": {},
            "decisions": [],
            "open_tasks": [],
        }

    def set_pref(self, key: str, value: Any) -> None:
        self._data["user_prefs"][key] = value

    def record_decision(self, text: str) -> None:
        if text not in self._data["decisions"]:
            self._data["decisions"].append(text)

    def add_task(self, text: str) -> None:
        if text not in self._data["open_tasks"]:
            self._data["open_tasks"].append(text)

    def complete_task(self, text: str) -> None:
        if text in self._data["open_tasks"]:
            self._data["open_tasks"].remove(text)

    def update(self, patch: dict[str, Any]) -> None:
        """Merge an arbitrary patch (e.g. extracted by an LLM) into state."""
        for key, value in patch.items():
            existing = self._data.get(key)
            if isinstance(existing, list) and isinstance(value, list):
                for item in value:
                    if item not in existing:
                        existing.append(item)
            elif isinstance(existing, dict) and isinstance(value, dict):
                existing.update(value)
            else:
                self._data[key] = value

    def as_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self._data))  # cheap deep copy

    def render(self) -> str:
        """Render as a block meant to sit near the top of the system prompt."""
        return (
            "Known facts you must not re-derive or contradict:\n"
            f"{json.dumps(self._data, indent=2)}"
        )
