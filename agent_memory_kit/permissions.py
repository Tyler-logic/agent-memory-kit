"""Permission-boundary pattern for autonomous agents.

Classifies actions by reversibility and enforces the classification in code
the model doesn't control — not as a prompt instruction it can forget under
context pressure. Companion to the AgentCraft article "How to Stop an
Autonomous Agent From Doing Something Destructive".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class ActionTier(Enum):
    AUTONOMOUS = "autonomous"  # reversible, low-consequence — just do it
    CONFIRM = "confirm"        # real consequence, but recoverable — ask first
    BLOCKED = "blocked"        # irreversible or high-consequence — never autonomous


@dataclass
class PermissionBoundary:
    """Enforces action tiers around a set of tool implementations.

    Unknown actions default to CONFIRM, not AUTONOMOUS — a new tool added
    later without an explicit classification should never silently inherit
    the least restrictive tier.
    """

    tiers: dict[str, ActionTier] = field(default_factory=dict)
    implementations: dict[str, Callable[..., Any]] = field(default_factory=dict)
    default_tier: ActionTier = ActionTier.CONFIRM

    def register(
        self, name: str, tier: ActionTier, implementation: Callable[..., Any]
    ) -> None:
        self.tiers[name] = tier
        self.implementations[name] = implementation

    def tier_for(self, name: str) -> ActionTier:
        return self.tiers.get(name, self.default_tier)

    def execute(
        self,
        name: str,
        arguments: Optional[dict] = None,
        get_human_approval: Optional[Callable[[str, dict], bool]] = None,
    ) -> str:
        arguments = arguments or {}
        tier = self.tier_for(name)

        if tier is ActionTier.BLOCKED:
            return f"Action '{name}' is blocked and cannot be executed autonomously."

        if tier is ActionTier.CONFIRM:
            if get_human_approval is None:
                return (
                    f"Action '{name}' requires approval but no approval "
                    "mechanism was provided. Not executed."
                )
            if not get_human_approval(name, arguments):
                return f"Action '{name}' was not approved. Continuing without it."

        impl = self.implementations.get(name)
        if impl is None:
            return f"Action '{name}' has no registered implementation."
        return impl(**arguments)

    def collect_pending_confirmations(
        self, planned_actions: list[tuple[str, dict]]
    ) -> list[tuple[str, dict]]:
        """Filter a batch of planned actions down to the ones needing approval,
        so a caller can present one batched review instead of many individual
        prompts."""
        return [
            (name, args)
            for name, args in planned_actions
            if self.tier_for(name) is ActionTier.CONFIRM
        ]
