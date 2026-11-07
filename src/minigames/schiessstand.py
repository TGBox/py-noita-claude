"""Contract V20: the shooting range minigame (Card E09)."""

from __future__ import annotations

from dataclasses import dataclass

from . import Minigame


@dataclass
class ShootingTarget:
    x: float
    y: float
    kind: str
    visible_time: float
    hit: bool = False


class SchiessstandMinigame(Minigame):
    key: str = "schiessstand"
    title_de: str = "Schießstand"
    stake: int = 20
    time_limit: float = 30.0

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed=seed)
        self.targets: list[ShootingTarget] = []
        self.score: int = 0
