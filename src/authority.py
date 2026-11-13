"""Contract V15: Authority wanted level (0..5 stars) and agent spawning (Card F01)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enemies import Creature
    from .run import Run

WANTED_MAX: float = 5.0

AGENT_TYPES: tuple[str, ...] = (
    "agent_streife",
    "agent_sachbearbeiter",
    "agent_drohne",
    "agent_vollstrecker",
    "agent_abteilungsleiter",
)

AGENT_ALIASES: dict[str, str] = {
    "agent_sachbearbeiter": "agent_streife",
}

FORBIDDEN_BLOCKS: tuple[str, ...] = ("sprengkern", "knochenbombe")
AGENT_GOLD: dict[str, int] = {
    "agent_streife": 15,
    "agent_drohne": 5,
    "agent_vollstrecker": 40,
    "agent_abteilungsleiter": 40,
}
BADGE_CHANCE: dict[str, float] = {
    "agent_streife": 0.10,
    "agent_drohne": 0.05,
    "agent_vollstrecker": 0.15,
    "agent_abteilungsleiter": 0.50,
}


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
        old_level = self.level
        new_level = max(0.0, min(WANTED_MAX, old_level + delta))
        if delta > 0 and reason:
            self.crimes.append(reason)
            if len(self.crimes) > 20:
                self.crimes = self.crimes[-20:]
        self.level = new_level
        return not math.isclose(old_level, new_level, abs_tol=1e-5)

    def on_cells_destroyed(self, count: int) -> bool:
        """Increment destroyed cell count (+0.25 per 500 cells)."""
        if count <= 0:
            return False
        self.cells_destroyed_total += count
        self._cells_carry += count
        gained = self._cells_carry // 500
        if gained > 0:
            self._cells_carry %= 500
            return self.add(gained * 0.25, "Sachbeschädigung")
        return False

    def on_workshop(self) -> bool:
        """Decay wanted level by -0.5 upon entering workshop."""
        old_level = self.level
        new_level = max(0.0, old_level - 0.5)
        self.level = new_level
        return not math.isclose(old_level, new_level, abs_tol=1e-5)

    def bribe_cost(self) -> int:
        return 40 + 25 * self.stars

    def agent_count(self) -> int:
        """Return number of authority agents to spawn for current stars:
        0 -> 0, 1 -> 1, 2 -> 2, 3 -> 3, 4 -> 4, 5 -> 6.
        """
        st = self.stars
        if st <= 4:
            return st
        return 6

    def to_data(self) -> dict[str, object]:
        return {
            "level": round(self.level, 4),
            "crimes": list(self.crimes[-20:]),
            "cells_destroyed_total": self.cells_destroyed_total,
            "cells_carry": self._cells_carry,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Wanted:
        if not data:
            return cls()
        return cls(
            level=float(data.get("level", 0.0)),
            crimes=list(data.get("crimes", [])),
            cells_destroyed_total=int(data.get("cells_destroyed_total", 0)),
            _cells_carry=int(data.get("cells_carry", 0)),
        )


def agent_species_for_stars(stars: int) -> list[str]:
    """Return deterministic list of agent species to spawn for given star count (0..5).

    0 -> []
    1 -> [agent_streife]
    2 -> [agent_streife, agent_drohne]
    3 -> [agent_streife, agent_drohne, agent_vollstrecker]
    4 -> [agent_streife, agent_drohne, agent_vollstrecker, agent_abteilungsleiter]
    5 -> [agent_streife, agent_streife, agent_drohne, agent_vollstrecker, agent_vollstrecker, agent_abteilungsleiter]
    """
    st = max(0, min(5, stars))
    if st == 0:
        return []
    if st == 1:
        return ["agent_streife"]
    if st == 2:
        return ["agent_streife", "agent_drohne"]
    if st == 3:
        return ["agent_streife", "agent_drohne", "agent_vollstrecker"]
    if st == 4:
        return [
            "agent_streife",
            "agent_drohne",
            "agent_vollstrecker",
            "agent_abteilungsleiter",
        ]
    return [
        "agent_streife",
        "agent_streife",
        "agent_drohne",
        "agent_vollstrecker",
        "agent_vollstrecker",
        "agent_abteilungsleiter",
    ]


AGENT_MIN_DISTANCE = 200.0  # agents arrive outside the start zone (playtest 2026-11-13)
AGENT_MAX_DISTANCE = 420.0


def spawn_agents(run: Run, count: int | None = None) -> list[Creature]:
    """Spawn authority agents for the wanted level, out of sight of the start but on
    their way to it (AGENT_MIN_DISTANCE..AGENT_MAX_DISTANCE from run.level.spawn)."""
    import random

    from src.enemies import SPECIES

    species_list = agent_species_for_stars(run.wanted.stars)
    if count is not None:
        species_list = species_list[:count]
    if not species_list:
        return []
    spawn = run.level.spawn
    rng = random.Random(run.seed * 61 + run.depth_index * 7 + len(species_list))
    spawned: list[Creature] = []
    for species in species_list:
        spec = SPECIES[species]
        spot = run._open_spot(rng, spawn, min_dist=AGENT_MIN_DISTANCE, max_dist=AGENT_MAX_DISTANCE)
        if spot is None:
            spot = run._open_spot(rng, spawn, min_dist=AGENT_MIN_DISTANCE)
        if spot is None:
            continue  # no room anywhere: the authority sends nobody this time
        c = run.enemies.spawn(species, spot[0] - spec.width // 2, spot[1] - spec.height)
        spawned.append(c)
    return spawned
