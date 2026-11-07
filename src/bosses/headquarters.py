"""Contract V17: the authority headquarters and the Ober-Cloita (Cards F09, F10)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..run import Run
    from ..world import World

HQ_STAGES: tuple[str, ...] = (
    "anhoerung",
    "boese_ichs",
    "ober_cloita",
)
COUNCIL_SIZE = 5
OBER_CLOITA_HP = 6000


def can_enter_headquarters(run: Run) -> bool:
    """6 memory shards, 3 badges or 4 wanted stars (bible 02)."""
    raise NotImplementedError("Card F09")


def generate_headquarters_arena(world: World) -> tuple[int, int]:
    """Build the 960x360 file hall in world and return the player spawn."""
    raise NotImplementedError("Card F09")


class HeadquartersController:
    def __init__(self) -> None:
        self.stage_index: int = 0
        self.completed: bool = False

    def spawn_stage(self, run: Run) -> None:
        """Spawn the enemies of HQ_STAGES[self.stage_index]."""
        raise NotImplementedError("Card F09")

    def update(self, dt: float, run: Run) -> None:
        """Advance to the next stage once the current one is cleared."""
        raise NotImplementedError("Card F09")
