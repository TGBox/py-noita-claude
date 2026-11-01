"""Contract V16: Multi-phase boss scripts and arena hazards (Cards F03..F06)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enemies import Creature
    from ..run import Run


@dataclass(frozen=True)
class BossPhase:
    index: int
    hp_threshold: float
    name_de: str
    line_de: str
    attack_interval_scale: float = 1.0
    speed_scale: float = 1.0
    summon_species: str = ""
    summon_count: int = 0
    arena_hazard: str = ""


class BossScript:
    boss_key: str = ""
    title_de: str = ""
    phases: tuple[BossPhase, ...] = ()

    def __init__(self, boss: Creature) -> None:
        self.boss: Creature = boss
        self.phase: int = 0
        self.phase_timer: float = 0.0
        self.invuln_timer: float = 0.0
        self.hazard_timer: float = 0.0

    def update(self, dt: float, run: Run) -> None:
        """Check phase HP thresholds, tick invuln_timer, and execute tick_phase."""
        raise NotImplementedError("Card F03")

    def phase_change(self, new_phase: int, run: Run) -> None:
        """Transition into new_phase with 1.0s invulnerability, summons, and boss_line."""
        raise NotImplementedError("Card F03")

    def tick_phase(self, dt: float, run: Run) -> None:
        """Execute phase-specific attacks and arena hazards."""
        raise NotImplementedError("Card F03")

    def on_death(self, run: Run) -> None:
        """Handle boss defeat rewards and portal unlock."""
        raise NotImplementedError("Card F03")


def apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run) -> None:
    """Apply periodic arena hazard effect during a boss fight."""
    raise NotImplementedError("Card F03")


def make_boss_script(boss: Creature) -> BossScript | None:
    """Return the matching BossScript instance for boss.species, or None."""
    raise NotImplementedError("Cards F03..F06")

