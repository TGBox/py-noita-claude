"""Contract V20: Schiessstand target-shooting minigame (Card E09)."""

from __future__ import annotations

from dataclasses import dataclass

from . import Minigame


@dataclass
class ShootingTarget:
    x: float
    y: float
    vx: float = 20.0
    hit: bool = False
    is_authority_dummy: bool = False


class SchiessstandMinigame(Minigame):
    key: str = "schiessstand"
    title_de: str = "Schießstand"
    time_limit: float = 15.0

    def __init__(self, seed: int = 0) -> None:
        super().__init__(seed=seed)
        self.targets: list[ShootingTarget] = []

