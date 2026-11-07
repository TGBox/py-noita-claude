"""Contract V13: Optional shrine challenges (Cards D13, D14)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class ChallengeSpec:
    key: str
    name: str
    description: str
    reward_gold: int
    reward_samples: int = 2
    reward_perk: bool = False
    time_limit: float = 0.0


CHALLENGES: dict[str, ChallengeSpec] = {
    "pacifist": ChallengeSpec(
        "pacifist",
        "Pazifist",
        "Schließe das Universum ab, ohne Kreaturen zu töten.",
        reward_gold=80,
        reward_samples=2,
    ),
    "no_gold": ChallengeSpec(
        "no_gold",
        "Goldabstinenz",
        "Sammle kein Gold ein.",
        reward_gold=60,
        reward_samples=2,
    ),
    "speed_run": ChallengeSpec(
        "speed_run",
        "Tempolauf",
        "Erreiche den Ausgang in unter 60 Sekunden.",
        reward_gold=100,
        reward_samples=2,
        time_limit=60.0,
    ),
    "no_damage": ChallengeSpec(
        "no_damage",
        "Makellos",
        "Erleide keinen Schaden bis zum Verlassen.",
        reward_gold=120,
        reward_samples=3,
        reward_perk=True,
    ),
    "kill_streak": ChallengeSpec(
        "kill_streak",
        "Blutrausch",
        "Besiege 10 Kreaturen in schneller Folge.",
        reward_gold=75,
        reward_samples=2,
    ),
    "dry_feet": ChallengeSpec(
        "dry_feet",
        "Trockene Füße",
        "Berühre keine Flüssigkeiten.",
        reward_gold=70,
        reward_samples=2,
    ),
}


@dataclass
class Challenge:
    spec: ChallengeSpec
    active: bool = False
    completed: bool = False
    failed: bool = False
    reward_paid: bool = False
    progress: int = 0
    elapsed: float = 0.0

    def activate(self) -> None:
        """Activate this challenge at the shrine."""
        self.active = True
        self.completed = False
        self.failed = False
        self.reward_paid = False
        self.progress = 0
        self.elapsed = 0.0

    def on_event(self, name: str, data: dict[str, object], run: Run) -> None:
        """React to gameplay events emitted on Run."""
        if not self.active or self.failed or self.completed:
            return
        key = self.spec.key
        if key == "pacifist":
            if name == "kill" and data.get("killer") == "player":
                self.failed = True
            elif name == "leave_universe":
                self.completed = True
        elif key == "no_gold":
            if name in ("gold", "pickup") and (name == "gold" or data.get("kind") == "gold"):
                self.failed = True
            elif name == "leave_universe":
                self.completed = True
        elif key == "no_damage":
            if name == "hurt_player":
                self.failed = True
            elif name == "leave_universe":
                self.completed = True
        elif key == "speed_run":
            if name == "leave_universe":
                if self.spec.time_limit <= 0.0 or self.elapsed <= self.spec.time_limit:
                    self.completed = True
                else:
                    self.failed = True
        elif key == "dry_feet":
            if name == "wet":
                self.failed = True
            elif name == "leave_universe":
                self.completed = True
        elif key == "kill_streak":
            if name == "kill":
                self.progress += 1
                if self.progress >= 10:
                    self.completed = True
            elif name == "leave_universe":
                if self.progress >= 10:
                    self.completed = True
                else:
                    self.failed = True

    def tick(self, dt: float, run: Run) -> None:
        """Advance time-based challenge progress and check limits."""
        if not self.active or self.failed or self.completed:
            return
        self.elapsed += dt
        if self.spec.key == "speed_run" and self.spec.time_limit > 0.0:
            if self.elapsed > self.spec.time_limit:
                self.failed = True

    def pay_reward(self, run: Run) -> None:
        """Grant reward_gold, reward_samples, and optional perk once upon completion."""
        if not self.completed or self.reward_paid:
            return
        self.reward_paid = True
        if self.spec.reward_gold > 0:
            run.gold += self.spec.reward_gold
            run.emit("gold", amount=self.spec.reward_gold, source="challenge_reward")
        if self.spec.reward_samples > 0:
            sample_key = getattr(run.universe, "sample_key", "probe_gallenstein")
            run.inventory.add_sample(sample_key, self.spec.reward_samples)
            run.emit("sample", key=sample_key, count=self.spec.reward_samples)

    def to_data(self) -> dict[str, object]:
        """Serialize challenge state."""
        return {
            "key": self.spec.key,
            "active": self.active,
            "completed": self.completed,
            "failed": self.failed,
            "reward_paid": self.reward_paid,
            "progress": self.progress,
            "elapsed": self.elapsed,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Challenge | None:
        """Restore Challenge from serialized dict."""
        if not data:
            return None
        key = str(data.get("key", ""))
        spec = CHALLENGES.get(key)
        if spec is None:
            return None
        return cls(
            spec=spec,
            active=bool(data.get("active", False)),
            completed=bool(data.get("completed", False)),
            failed=bool(data.get("failed", False)),
            reward_paid=bool(data.get("reward_paid", False)),
            progress=int(data.get("progress", 0)),
            elapsed=float(data.get("elapsed", 0.0)),
        )


def pick_challenge(universe_key: str, depth: int, rng: random.Random) -> Challenge:
    """Pick a deterministic Challenge instance for universe_key and depth."""
    keys = list(CHALLENGES.keys())
    selected_key = keys[(depth + abs(hash(universe_key))) % len(keys)]
    return Challenge(spec=CHALLENGES[selected_key])


@dataclass(frozen=True)
class QuestSpec:
    """Universe challenge given by a native (Contract V13b)."""

    key: str
    universe: str
    giver: str
    text_de: str
    goal: int
    reward: tuple[str, int]


@dataclass
class Quest:
    spec: QuestSpec
    accepted: bool = False
    progress: int = 0
    done: bool = False
    failed: bool = False
    reward_paid: bool = False

    def accept(self, run: Run) -> None:
        raise NotImplementedError("Card D22")

    def on_event(self, name: str, data: dict[str, object], run: Run) -> None:
        raise NotImplementedError("Card D22")

    def tick(self, dt: float, run: Run) -> None:
        raise NotImplementedError("Card D22")

    def turn_in(self, run: Run) -> bool:
        raise NotImplementedError("Card D22")

    def to_data(self) -> dict[str, object]:
        raise NotImplementedError("Card D22")

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Quest | None:
        raise NotImplementedError("Card D22")


QUESTS: dict[str, QuestSpec] = {}


def quest_for(universe_key: str) -> Quest:
    """Return a fresh Quest for the universe (Card D22)."""
    raise NotImplementedError("Card D22")
