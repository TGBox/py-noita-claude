"""Contract V20: workshop minigame base class and result type (Cards E07..E09)."""

from __future__ import annotations

from dataclasses import dataclass

from ..world import World

MINIGAME_WORLD_SIZE: tuple[int, int] = (160, 120)

# Boosts for the next universe (bible 07): flux charge +20 %, damage +10 %, speed +10 %.
NEXT_BOOST_KEYS: tuple[str, ...] = ("flux", "damage", "speed")


@dataclass
class MinigameResult:
    completed: bool
    won: bool
    reward_gold: int = 0
    reward_sample: str = ""
    next_boost: str = ""
    message_de: str = ""


class Minigame:
    key: str = ""
    title_de: str = ""
    stake: int = 0
    time_limit: float = 15.0

    def __init__(self, seed: int = 0) -> None:
        self.seed: int = seed
        self.elapsed: float = 0.0
        self.finished: bool = False
        self.result: MinigameResult | None = None
        self.world: World = World(*MINIGAME_WORLD_SIZE)

    def step(
        self,
        dt: float,
        action: str | None = None,
        cursor: tuple[int, int] = (80, 60),
    ) -> MinigameResult | None:
        """Advance the minigame by dt; return the result once it is finished."""
        raise NotImplementedError("Card E07")
