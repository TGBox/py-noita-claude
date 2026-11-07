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


def spawn_agents(run: Run, count: int | None = None) -> list[Creature]:
    """Spawn authority agents near run.level.spawn and return spawned Creature instances."""
    from src import materials as mat

    species_list = agent_species_for_stars(run.wanted.stars)
    if count is not None:
        species_list = species_list[:count]

    if not species_list:
        return []

    spawn_x, spawn_y = run.level.spawn
    world = run.world
    id_air = mat.AIR

    spawned: list[Creature] = []
    # Search around spawn with min distance 48 px, max distance 140 px
    for i, spec in enumerate(species_list):
        # Deterministic radial offset
        angle = (i * 2.0 * math.pi) / len(species_list)
        dist = 60.0 + (i % 3) * 25.0
        target_x = spawn_x + dist * math.cos(angle)
        target_y = spawn_y + dist * math.sin(angle)

        # Find nearest air cell around target
        best_pos: tuple[float, float] | None = None
        for r in range(0, 30, 2):
            for d_ang in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
                cand_x = int(target_x + r * math.cos(d_ang))
                cand_y = int(target_y + r * math.sin(d_ang))
                if (
                    0 <= cand_x < world.width
                    and 0 <= cand_y < world.height
                    and world.get(cand_x, cand_y) == id_air
                ):
                    # Check min distance 48, max 140
                    actual_dist = math.hypot(cand_x - spawn_x, cand_y - spawn_y)
                    if 48.0 <= actual_dist <= 140.0:
                        best_pos = (float(cand_x), float(cand_y))
                        break
            if best_pos is not None:
                break

        if best_pos is None:
            best_pos = (spawn_x + 50.0 + i * 10.0, spawn_y)

        c = run.enemies.spawn(spec, best_pos[0], best_pos[1])
        spawned.append(c)

    return spawned

    species_list = agent_species_for_stars(run.wanted.stars)
    if count is not None:
        species_list = species_list[:count]

    if not species_list:
        return []

    spawn_x, spawn_y = run.level.spawn
    world = run.world
    id_air = mat.AIR

    spawned: list[Creature] = []
    # Search around spawn with min distance 48 px, max distance 140 px
    for i, spec in enumerate(species_list):
        # Deterministic radial offset
        angle = (i * 2.0 * math.pi) / len(species_list)
        dist = 60.0 + (i % 3) * 25.0
        target_x = spawn_x + dist * math.cos(angle)
        target_y = spawn_y + dist * math.sin(angle)

        # Find nearest air cell around target
        best_pos: tuple[float, float] | None = None
        for r in range(0, 30, 2):
            for d_ang in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
                cand_x = int(target_x + r * math.cos(d_ang))
                cand_y = int(target_y + r * math.sin(d_ang))
                if (
                    0 <= cand_x < world.width
                    and 0 <= cand_y < world.height
                    and world.get(cand_x, cand_y) == id_air
                ):
                        # Check min distance 48, max 140
                        actual_dist = math.hypot(cand_x - spawn_x, cand_y - spawn_y)
                        if 48.0 <= actual_dist <= 140.0:
                            best_pos = (float(cand_x), float(cand_y))
                            break
            if best_pos is not None:
                break

        if best_pos is None:
            best_pos = (spawn_x + 50.0 + i * 10.0, spawn_y)

        c = run.enemies.spawn(spec, best_pos[0], best_pos[1])
        spawned.append(c)

    return spawned
