"""Pattern 2: retrieval on demand for facts too numerous to keep resident.

Deliberately starts crude (difflib fuzzy matching over a flat JSONL file, zero
infra, zero cost) rather than reaching for a vector database on day one.
Swap in real embeddings later by replacing `_score` — the public interface
(`remember` / `recall`) doesn't need to change.
"""
from __future__ import annotations

import difflib
import json
import os
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class FuzzyRecall:
    path: str = "memory.jsonl"
    scorer: Callable[[str, str], float] = field(default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.scorer is None:
            self.scorer = self._default_scorer

    @staticmethod
    def _default_scorer(query: str, candidate: str) -> float:
        return difflib.SequenceMatcher(None, query.lower(), candidate.lower()).ratio()

    def remember(self, text: str, **metadata) -> None:
        record = {"text": text, **metadata}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def recall(self, query: str, top_k: int = 3) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            facts = [json.loads(line) for line in f if line.strip()]
        scored = sorted(
            facts, key=lambda fact: self.scorer(query, fact["text"]), reverse=True
        )
        return scored[:top_k]

    def clear(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)
