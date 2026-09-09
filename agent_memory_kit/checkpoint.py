"""Pattern 3: explicit checkpointing before a framework compacts/summarizes
old context.

Turns compaction from a lossy black box into a controlled handoff: an
extraction pass pulls anything load-bearing into ScratchpadState *before* the
raw turns get summarized or dropped.
"""
from __future__ import annotations

from typing import Callable

from .scratchpad import ScratchpadState


class CompactionCheckpoint:
    def __init__(
        self,
        state: ScratchpadState,
        extractor: Callable[[list[dict]], dict],
    ) -> None:
        """
        Args:
            state: the ScratchpadState to receive extracted facts.
            extractor: a callable (typically a cheap LLM call) that takes the
                conversation history about to be compacted and returns a
                patch dict of {"user_prefs": ..., "decisions": [...], ...}.
        """
        self.state = state
        self.extractor = extractor

    def before_compaction(self, conversation_history: list[dict]) -> dict:
        """Run extraction and merge the result into state. Returns the patch
        that was applied, so callers can log/inspect it."""
        patch = self.extractor(conversation_history)
        self.state.update(patch)
        return patch
