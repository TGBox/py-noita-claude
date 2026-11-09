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
        if self.finished:
            return self.result

        self.elapsed += dt
        if action is not None:
            self.on_action(action, cursor)

        # Step physics world
        self.world.step()
        self.tick(dt)

        # Check win/loss
        if not self.finished:
            if self.check_win():
                self.finish(won=True)
            elif self.elapsed >= self.time_limit:
                self.finish(won=False)

        return self.result

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        pass

    def tick(self, dt: float) -> None:
        pass

    def check_win(self) -> bool:
        return False

    def finish(self, won: bool) -> None:
        self.finished = True
        if won:
            self.result = self.make_win_result()
        else:
            self.result = MinigameResult(completed=True, won=False, message_de="Zeit abgelaufen!")

    def make_win_result(self) -> MinigameResult:
        return MinigameResult(
            completed=True, won=True, reward_gold=self.stake * 2, message_de="Geschafft!"
        )

        self.elapsed += dt
        if action is not None:
            self.on_action(action, cursor)

        # Step physics world
        self.world.step()
        self.tick(dt)

        # Check win/loss
        if not self.finished:
            if self.check_win():
                self.finish(won=True)
            elif self.elapsed >= self.time_limit:
                self.finish(won=False)

        return self.result

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        pass

    def tick(self, dt: float) -> None:
        pass

    def check_win(self) -> bool:
        return False

    def finish(self, won: bool) -> None:
        self.finished = True
        if won:
            self.result = self.make_win_result()
        else:
            self.result = MinigameResult(completed=True, won=False, message_de="Zeit abgelaufen!")

    def make_win_result(self) -> MinigameResult:
        return MinigameResult(completed=True, won=True, reward_gold=self.stake * 2, message_de="Geschafft!")
