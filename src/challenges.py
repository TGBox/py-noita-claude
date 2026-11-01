"""Contract V13: Optional shrine challenges (Cards D13, D14)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class ChallengeSpec:
    key: str
    name: str
    description: str
    reward_gold: int
    reward_samples: int = 2
    reward_perk: bool = False
    time_limit: float = 0.0


@dataclass
class Challenge:
    spec: ChallengeSpec
    active: bool = False
    completed: bool = False
    failed: bool = False
    reward_paid: bool = False
    progress: int = 0
    elapsed: float = 0.0

    def activate(self) -> None:
        """Activate this challenge at the shrine."""
        raise NotImplementedError("Card D13")

    def on_event(self, name: str, data: dict[str, object], run: Run) -> None:
        """React to gameplay events emitted on Run."""
        raise NotImplementedError("Card D13")

    def tick(self, dt: float, run: Run) -> None:
        """Advance time-based challenge progress and check limits."""
        raise NotImplementedError("Card D13")

    def pay_reward(self, run: Run) -> None:
        """Grant reward_gold, reward_samples, and optional perk once upon completion."""
        raise NotImplementedError("Card D13")

    def to_data(self) -> dict[str, object]:
        """Serialize challenge state."""
        raise NotImplementedError("Card D13")

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Challenge | None:
        """Restore Challenge from serialized dict."""
        raise NotImplementedError("Card D13")


CHALLENGES: dict[str, ChallengeSpec] = {}


def pick_challenge(universe_key: str, depth: int, rng: random.Random) -> Challenge:
    """Pick a deterministic Challenge instance for universe_key and depth."""
    raise NotImplementedError("Card D13")

