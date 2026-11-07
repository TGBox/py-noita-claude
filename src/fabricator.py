"""Contract V20: the fabricator builds modules from blueprints (Card E06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run

MAX_BUILDS_PER_VISIT: int = 3
TIER2_SAMPLES: tuple[str, ...] = ("probe_knochen", "probe_aether", "probe_schatten")
TIER3_SAMPLES: tuple[str, ...] = ("probe_gold", "probe_kern")


@dataclass(frozen=True)
class Recipe:
    block_key: str
    rarity_tier: int
    universe_samples: int
    universe: str | None
    special_samples: tuple[str, ...]
    blueprint_shards: int
    gold: int


def build_cost(block_key: str, stage: int = 1) -> Recipe:
    raise NotImplementedError("Card E06")


class Fabricator:
    def __init__(self) -> None:
        self.builds_this_visit: int = 0

    def reset_visit(self) -> None:
        self.builds_this_visit = 0

    def can_build(self, run: Run, block_key: str) -> tuple[bool, str]:
        raise NotImplementedError("Card E06")

    def craft(self, run: Run, block_key: str) -> tuple[bool, str]:
        raise NotImplementedError("Card E06")
