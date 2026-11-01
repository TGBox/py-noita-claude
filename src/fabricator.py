"""Contract V20: Spell module fabricator and recipes (Card E06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run

MAX_BUILDS_PER_VISIT: int = 3


@dataclass(frozen=True)
class Recipe:
    block_key: str
    rarity_tier: int
    samples: tuple[tuple[str, int], ...]
    gold: int


def build_cost(block_key: str) -> Recipe:
    """Return the deterministic Recipe for block_key."""
    raise NotImplementedError("Card E06")


class Fabricator:
    def __init__(self) -> None:
        self.builds_this_visit: int = 0

    def reset_visit(self) -> None:
        self.builds_this_visit = 0

    def can_build(
        self,
        block_key: str,
        *,
        unlocked_blueprints: set[str],
        gold: int,
        sample_counts: dict[str, int],
    ) -> tuple[bool, str]:
        """Check whether block_key can be fabricated and return (ok, status_de)."""
        raise NotImplementedError("Card E06")

    def craft(self, run: Run, block_key: str) -> tuple[bool, str]:
        """Consume samples and gold on run, increment builds_this_visit, and return (ok, msg_de)."""
        raise NotImplementedError("Card E06")

