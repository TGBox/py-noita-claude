"""Contract V17: Authority Headquarters 3-stage finale and Ober-Cloita (Cards F09, F10)."""

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


def can_enter_headquarters(run: Run) -> bool:
    """Return True if player has >= 3 badges or >= 4 wanted stars."""
    raise NotImplementedError("Card F09")


def generate_headquarters_arena(world: World) -> tuple[int, int]:
    """Build the 320x200 Headquarters arena in world and return player spawn (x, y)."""
    raise NotImplementedError("Card F09")


class HeadquartersController:
    def __init__(self) -> None:
        self.stage_index: int = 0
        self.completed: bool = False

    def spawn_stage(self, run: Run) -> None:
        """Spawn enemies/boss for current HQ_STAGES[self.stage_index]."""
        raise NotImplementedError("Card F09")

    def update(self, dt: float, run: Run) -> None:
        """Advance Headquarters stage when all stage enemies are defeated."""
        raise NotImplementedError("Card F09")

