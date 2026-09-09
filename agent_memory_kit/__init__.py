"""agent-memory-kit: three small, dependency-free memory patterns for LLM agents.

Companion library to the AgentCraft article "Why Your AI Agent Forgets Things
Mid-Task". Implements Pattern 1 (scratchpad state), Pattern 2 (fuzzy recall),
and Pattern 3 (pre-compaction checkpointing) as minimal, swappable pieces —
no vector DB, no framework lock-in.
"""

from .scratchpad import ScratchpadState
from .recall import FuzzyRecall
from .checkpoint import CompactionCheckpoint
from .permissions import ActionTier, PermissionBoundary

__all__ = [
    "ScratchpadState",
    "FuzzyRecall",
    "CompactionCheckpoint",
    "ActionTier",
    "PermissionBoundary",
]
__version__ = "0.2.0"
