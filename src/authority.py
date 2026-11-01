"""Contract V15: Authority wanted level (0..5 stars) and agent spawning (Card F01)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enemies import Creature
    from .run import Run

WANTED_MAX: float = 5.0

AGENT_TYPES: tuple[str, ...] = (
    "agent_sachbearbeiter",
    "agent_vollstrecker",
    "agent_abteilungsleiter",
)


@dataclass
class Wanted:
    level: float = 0.0
    crimes: list[str] = field(default_factory=list)
    cells_destroyed_total: int = 0
    _cells_carry: int = 0

    @property
    def stars(self) -> int:
        return max(0, min(5, int(self.level)))

    def add(self, delta: float, reason: str) -> bool:
        """Adjust wanted level by delta (clamped 0..5) and record reason."""
        raise NotImplementedError("Card F01")

    def on_cells_destroyed(self, count: int) -> bool:
        """Increment destroyed cell count (+0.25 per 500 cells)."""
        raise NotImplementedError("Card F01")

    def on_workshop(self) -> bool:
        """Decay wanted level by -0.5 upon entering workshop."""
        raise NotImplementedError("Card F01")

    def bribe_cost(self) -> int:
        return 40 + 25 * self.stars

    def agent_count(self) -> int:
        """Return number of authority agents to spawn for current stars."""
        raise NotImplementedError("Card F01")

    def to_data(self) -> dict[str, object]:
        return {
            "level": round(self.level, 4),
            "crimes": list(self.crimes[-20:]),
            "cells_destroyed_total": self.cells_destroyed_total,
            "cells_carry": self._cells_carry,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Wanted:
        raise NotImplementedError("Card F01")


def agent_species_for_stars(stars: int) -> list[str]:
    """Return deterministic list of agent species to spawn for given star count (0..5)."""
    raise NotImplementedError("Card F01")


def spawn_agents(run: Run, count: int | None = None) -> list[Creature]:
    """Spawn authority agents near run.level.spawn and return spawned Creature instances."""
    raise NotImplementedError("Card F01")

