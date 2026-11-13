"""Contract V13: Optional shrine challenges (Cards D13, D14)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src import materials as mat
from src.flask import CAPACITY as FLASK_CAPACITY
from src.flask import Flask
from src.loot import Pickup
from src.spells import blocks_of_tier

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
    _cow: Any = field(default=None, repr=False, compare=False)  # Glibbria: the escorted cow
    _cow_wet: float = field(default=0.0, repr=False, compare=False)
    _feed_timer: float = field(default=0.0, repr=False, compare=False)

    @property
    def closed(self) -> bool:
        """Nothing changes any more after failing or after the reward was paid."""
        return self.failed or self.reward_paid

    def accept(self, run: Run) -> None:
        if self.accepted:
            return
        self.accepted = True
        if self.spec.universe == "glibbria":
            x, y = _giver_spot(self, run)
            self._cow = run.enemies.spawn("glibberkuh", x + 14, y - 12)
            self._cow.stance = "passive"
        run.emit("quest_accepted", key=self.spec.key)

    def _fail(self, run: Run) -> None:
        if not self.closed:
            self.failed = True
            run.emit("quest_done", key=self.spec.key, success=False)

    def _advance(self, amount: int = 1) -> None:
        self.progress = min(self.spec.goal, self.progress + amount)
        self.done = self.progress >= self.spec.goal

    def on_event(self, name: str, data: dict[str, object], run: Run) -> None:
        if not self.accepted or self.closed:
            return
        universe = self.spec.universe
        if universe == "aktenhalde":
            if name == "form_stamped":
                self._advance()
            elif name == "event_start" and data.get("key") == "pruefung" and not self.done:
                self._fail(run)  # the audit came before the forms were stamped
        elif universe == "glibbria":
            if name == "kill" and data.get("species") == "glibberkuh":
                self._fail(run)
        elif universe == "kruemelreich":
            if name == "aphid_fed":
                self._advance()
        elif universe == "sporenklub":
            if name == "jump" and not self.done:
                if data.get("on_beat"):
                    self._advance()
                else:
                    self.progress = 0  # off the beat: start the dance again
        elif universe == "abtei":
            if name == "bell_rung":
                self._advance()
            elif name == "creature_woke" and data.get("species") == "kirchenkrake":
                self._fail(run)

    def tick(self, dt: float, run: Run) -> None:
        if not self.accepted or self.closed:
            return
        universe = self.spec.universe
        if universe == "fleischwelt":
            self.progress = min(self.spec.goal, run.inventory.sample_count("probe_gallenstein"))
            self.done = self.progress >= self.spec.goal
        elif universe == "glibbria":
            self._tick_cow(dt, run)
        elif universe == "kruemelreich" and not self.done:
            self._feed_timer += dt
            if self._feed_timer >= 1.0:  # at most once per second
                self._feed_timer = 0.0
                self._tick_aphids(run)

    def _tick_cow(self, dt: float, run: Run) -> None:
        """The cow follows the player (closer than 120 px), dissolves after 3 s in syrup and
        arrives within 24 px of ``Level.quest_target``."""
        cow, target = self._cow, getattr(run.level, "quest_target", None)
        if cow is None or cow.dead or self.done:
            return
        cx, cy = cow.center
        px, _py = run.player.center
        if 20 < abs(px - cx) and math.dist(run.player.center, cow.center) < COW_FOLLOW_RANGE:
            cow.facing = 1 if px > cx else -1
            cow._move_x(run.world, cow.facing * cow.spec.speed * dt)
        feet = run.world.get(int(cx), int(cow.y + cow.height - 1))
        self._cow_wet = self._cow_wet + dt if mat.KEYS[feet] == "brausesirup" else 0.0
        if self._cow_wet >= COW_SYRUP_TIME:
            cow.hp = 0.0  # the run reports the death as "kill": the quest fails there
            return
        if target is not None and math.dist(cow.center, target) <= QUEST_TARGET_RADIUS:
            self._advance()

    def _tick_aphids(self, run: Run) -> None:
        """Aphids eat the sugar poured next to them; an ant warrior that sees you ends it."""
        sugar = mat.MAT_ID.get("zucker")
        world = run.world
        for creature in run.enemies.creatures:
            if creature.dead:
                continue
            if creature.species == "ameisenkrieger":
                if creature.can_see(world, *run.player.center, creature.spec.sight):
                    self._fail(run)
                    return
            elif creature.species == "blattlaus" and sugar is not None:
                cx, cy = (int(v) for v in creature.center)
                reach = APHID_REACH
                cells = [
                    (x, y)
                    for y in range(cy - reach, cy + reach + 1)
                    for x in range(cx - reach, cx + reach + 1)
                    if world.get(x, y) == sugar
                ]
                for x, y in cells:
                    world.set_cell(x, y, mat.AIR, force=True)
                if cells:
                    run.emit("aphid_fed", x=float(cx), y=float(cy), cells=len(cells))

    def turn_in(self, run: Run) -> bool:
        if not self.accepted or self.closed or self.progress < self.spec.goal:
            return False
        universe = self.spec.universe
        if universe == "fleischwelt" and not run.inventory.take_samples({"probe_gallenstein": 3}):
            return False  # the stones are gone again: the quest stays open
        kind, amount = self.spec.reward
        x, y = _giver_spot(self, run)
        if kind == "gold":
            run.gold += amount
        elif kind == "reroll":
            run.inventory.rerolls += amount
        elif kind == "samples":
            run.inventory.add_sample(run.universe.sample_key, amount)
        elif kind == "neonsaft_gold":
            run.gold += amount
            run.pickups.append(Pickup(x, y - 4, flask=Flask("neonsaft", FLASK_CAPACITY)))
        elif kind == "module_tier":
            run.pickups.append(Pickup(x, y - 4, block=run.rng.choice(blocks_of_tier(amount))))
        else:  # "life_capsule"
            run.pickups.append(Pickup(x, y - 4, kind="life_capsule"))
        self.reward_paid = self.done = True
        run.emit("quest_done", key=self.spec.key, success=True)
        return True

    def to_data(self) -> dict[str, object]:
        return {
            "key": self.spec.key,
            "accepted": self.accepted,
            "progress": self.progress,
            "done": self.done,
            "failed": self.failed,
            "reward_paid": self.reward_paid,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Quest | None:
        spec = QUESTS.get(str(data.get("key", ""))) if data else None
        if spec is None:
            return None
        return cls(
            spec,
            accepted=bool(data.get("accepted")),
            progress=int(data.get("progress", 0)),  # type: ignore[call-overload]
            done=bool(data.get("done")),
            failed=bool(data.get("failed")),
            reward_paid=bool(data.get("reward_paid")),
        )


def _giver_spot(quest: Quest, run: Run) -> tuple[float, float]:
    """Where the quest giver stands (the creature if it lives, else its place, else you)."""
    for creature in run.enemies.creatures:
        if creature.giver and not creature.dead and creature.species == quest.spec.giver:
            return creature.center
    spot = getattr(run.level, "quest_giver", None)
    return (float(spot[0]), float(spot[1])) if spot else run.player.center


COW_FOLLOW_RANGE = 120.0  # px: the Glibberkuh follows the player inside this distance
COW_SYRUP_TIME = 3.0  # seconds in Brausesirup until the cow dissolves
QUEST_TARGET_RADIUS = 24.0
APHID_REACH = 20  # px around an aphid where it eats sugar

QUESTS: dict[str, QuestSpec] = {
    spec.key: spec
    for spec in (
        QuestSpec(
            "challenge_fleischwelt", "fleischwelt", "fleischmade",
            "Bring mir 3 Gallensteine, ich sammle sie.", 3, ("life_capsule", 1),
        ),
        QuestSpec(
            "challenge_aktenhalde", "aktenhalde", "stempler",
            "Stempel 5 Formulare ab, bevor die Prüfung kommt.", 5, ("gold", 150),
        ),
        QuestSpec(
            "challenge_glibbria", "glibbria", "huepfling",
            "Bring meine Kuh heil über den Sirupsee.", 1, ("module_tier", 3),
        ),
        QuestSpec(
            "challenge_kruemelreich", "kruemelreich", "blattlaus",
            "Füttere die Blattläuse, ohne dass die Ameisen dich sehen.", 3, ("samples", 2),
        ),
        QuestSpec(
            "challenge_sporenklub", "sporenklub", "leuchtmotte",
            "Tanz mit mir! Fünf Sprünge, genau auf dem Beat.", 5, ("neonsaft_gold", 80),
        ),
        QuestSpec(
            "challenge_abtei", "abtei", "moenchsfisch",
            "Läute die Glocke dreimal, ohne den Kraken zu wecken.", 3, ("reroll", 1),
        ),
    )
}  # fmt: skip


def quest_for(universe_key: str) -> Quest:
    """Return a fresh Quest for the universe (Card D22)."""
    return Quest(QUESTS[f"challenge_{universe_key}"])
