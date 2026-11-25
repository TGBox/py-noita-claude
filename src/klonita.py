"""Contract V21: Klonita, the companion (Cards F12, F13, F16, F17).

She floats behind the player, cannot die (she is knocked out for five seconds instead),
helps with four small assists, points at secrets, fetches loot, calms peaceful
creatures and has one quirk per universe. ``Run`` calls ``update`` every frame and
``on_trigger`` for the five auto triggers; everything she says goes through ``run.say``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.klonita_lines import line_for

if TYPE_CHECKING:
    from .loot import Pickup
    from .run import Run

KLONITA_STATES: tuple[str, ...] = (
    "dismissed",
    "follow",
    "assist",
    "quirk",
    "knocked",
)

HELPERS: tuple[str, ...] = ("point", "carry", "hug")
QUIRKS: tuple[str, ...] = (
    "shiny_poke",
    "loud_sneeze",
    "sample_nibble",
    "tip_trader",
    "feed_creature",
    "warn_enemy",
)
QUIRK_CHANCE_PER_S = 0.02
POINT_RADIUS = 240.0
CARRY_MIN_RISE = 40.0
HUG_RADIUS = 80.0

AUTO_TRIGGERS: tuple[str, ...] = (
    "enter_universe",
    "player_low_hp",
    "boss_spawn",
    "wanted_high",
    "event_start",
)

KNOCKED_TIME = 5.0
FOLLOW_OFFSET = (-18.0, -10.0)  # behind and above the player
FOLLOW_RESPONSE = 4.0  # 1/s, how fast she closes the gap
TELEPORT_DISTANCE = 220.0
ASSIST_TIME = 0.4  # how long the "assist"/"quirk" pose is held
COOLDOWNS: dict[str, float] = {
    "shield": 18.0, "snack": 45.0, "spark": 4.5, "cleanse": 22.0, "point": 60.0, "carry": 30.0,
}  # fmt: skip
SHIELD_RADIUS = 28.0
SNACK_BELOW = 0.35
SNACK_HEAL = 15.0
SPARK_RANGE = 90.0
SPARK_DAMAGE = 6.0
POINT_TIME = 3.0
CARRY_REACH_X = 200.0
HUG_CALM = 0.5
PEACEFUL = ("peaceful", "passive", "territorial", "neutral")
POKE_RADIUS = 40.0
SNEEZE_RADIUS = 90.0
NIBBLE_MIN_SAMPLES = 5
NIBBLE_GOLD = 15
TIP_RADIUS = 60.0
FEED_RADIUS = 24.0
FEED_SHARE = 0.20
WARN_RADIUS = 120.0

_TRIGGER_TOPICS = {
    "enter_universe": "enter_universe",
    "player_low_hp": "player_low_hp",
    "boss_spawn": "boss_spawn",
    "wanted_high": "wanted_high",
    "event_start": "event_warn",
}


def _rng(run: Any) -> random.Random:
    """Her own random stream, so her chatter never shifts the world's generation."""
    return getattr(run, "klonita_rng", None) or run.rng


def _dist(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(ax - bx, ay - by)


@dataclass
class Klonita:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    hp: float = 60.0
    max_hp: float = 60.0
    state: str = "follow"
    knocked_timer: float = 0.0
    quirk_used_in_universe: bool = False
    cooldowns: dict[str, float] = field(
        default_factory=lambda: {
            "shield": 0.0,
            "snack": 0.0,
            "spark": 0.0,
            "cleanse": 0.0,
            "point": 0.0,
            "carry": 0.0,
        }
    )
    facing: int = 1
    pointing: tuple[float, float] | None = None
    point_timer: float = 0.0
    pose_timer: float = 0.0  # how long "assist"/"quirk" is still shown
    converted: float = 0.0  # the Good One's conversion (F19): on her side, harmless
    _quirk_clock: float = 0.0

    # ------------------------------------------------------------ state machine

    def toggle(self) -> str:
        """[K]: switch between 'dismissed' and 'follow' (not while knocked)."""
        if self.state == "knocked":
            return self.state
        self.state = "follow" if self.state == "dismissed" else "dismissed"
        return self.state

    def on_trigger(self, trigger: str, run: Run) -> str | None:
        """One of AUTO_TRIGGERS: she comes back to 'follow' and says something fitting."""
        if trigger not in AUTO_TRIGGERS:
            return None
        if self.state in ("dismissed", "assist", "quirk"):
            self.state = "follow"
        topic = _TRIGGER_TOPICS[trigger]
        universe = getattr(run, "universe_key", "")
        if trigger == "enter_universe":
            topic = f"enter_{universe}" if _rng(run).random() < 0.5 else "enter_universe"
        elif trigger == "event_start":
            topic = f"event_warn_{universe}"
        return line_for(topic, _rng(run))

    def take_damage(self, amount: float) -> bool:
        """She never dies: at 0 hp she is knocked out for KNOCKED_TIME seconds."""
        if self.state == "knocked" or amount <= 0:
            return False
        self.hp = max(0.0, self.hp - amount)
        if self.hp > 0:
            return False
        self.state = "knocked"
        self.knocked_timer = KNOCKED_TIME
        self.pointing = None
        return True

    @property
    def active(self) -> bool:
        return self.state not in ("dismissed", "knocked")

    # ------------------------------------------------------------------ update

    def update(self, dt: float, run: Run) -> None:
        """Movement, cooldowns, assists, helpers and (rarely) a quirk."""
        for key in self.cooldowns:
            self.cooldowns[key] = max(0.0, self.cooldowns[key] - dt)
        if self.converted > 0:
            self.converted = max(0.0, self.converted - dt)
        if self.state == "knocked":
            self.knocked_timer -= dt
            self.vx = self.vy = 0.0
            if self.knocked_timer <= 0.0:
                self.knocked_timer = 0.0
                self.hp = self.max_hp
                self.state = "follow"
                self._say(run, "klonita_up")
            return
        if self.state == "dismissed":
            return
        if self.pose_timer > 0:
            self.pose_timer -= dt
            if self.pose_timer <= 0 and self.state in ("assist", "quirk"):
                self.state = "follow"
        if getattr(run, "in_workshop", False):  # on the couch: no following, no assists
            self._quirk_roll(dt, run)
            return
        self._follow(dt, run)
        if self.point_timer > 0:
            self.point_timer -= dt
            if self.point_timer <= 0:
                self.pointing = None
        if self.converted > 0:
            return  # on the Good One's side: she watches, harmlessly
        if self._assist(run):
            return
        self._helpers(run)
        self._quirk_roll(dt, run)

    def _follow(self, dt: float, run: Run) -> None:
        player = run.player
        if player.dead and self.state != "knocked":
            return
        facing = getattr(player, "facing", 1) or 1
        tx = player.x + player.width / 2 + FOLLOW_OFFSET[0] * facing
        ty = player.y + FOLLOW_OFFSET[1]
        if self.pointing is not None and self.point_timer > 0:
            tx, ty = self.x, self.y  # she stands still while pointing
        if _dist(self.x, self.y, tx, ty) > TELEPORT_DISTANCE:
            self.x, self.y = tx, ty
            self.vx = self.vy = 0.0
            return
        follow = min(1.0, FOLLOW_RESPONSE * dt)
        bob = math.sin(getattr(run, "time_in_depth", 0.0) * 3.0) * 2.0
        self.vx = (tx - self.x) * FOLLOW_RESPONSE
        self.vy = (ty + bob - self.y) * FOLLOW_RESPONSE
        self.x += (tx - self.x) * follow
        self.y += (ty + bob - self.y) * follow
        if abs(tx - self.x) > 1.0:
            self.facing = 1 if tx > self.x else -1

    # ------------------------------------------------------- the four assists

    def _assist(self, run: Run) -> bool:
        player = run.player
        body = player.body
        px, py = body.center
        if self.cooldowns["shield"] <= 0:
            for p in run.projectiles.items:
                if p.alive and p.team != body.team and _dist(p.x, p.y, px, py) < SHIELD_RADIUS:
                    p.alive = False
                    run.events.append("blast_small")
                    return self._did("shield", run, "shield", quiet=True)
        if (
            self.cooldowns["snack"] <= 0
            and body.max_hp > 0
            and body.hp / body.max_hp < SNACK_BELOW
            and run.boss_script is None
        ):
            body.hp = min(body.max_hp, body.hp + SNACK_HEAL)
            run.events.append("heal")
            return self._did("snack", run, "snack")
        if self.cooldowns["cleanse"] <= 0 and (
            getattr(player, "burning", 0.0) > 0
            or getattr(player, "frozen", 0.0) > 0
            or getattr(body, "stamped_bad", 0.0) > 0
        ):
            if getattr(player, "burning", 0.0) > 0:
                player.burning = 0.0
            if getattr(player, "frozen", 0.0) > 0:
                player.frozen = 0.0
            body.stamped_bad = 0.0
            return self._did("cleanse", run, "cleanse", quiet=True)
        if self.cooldowns["spark"] <= 0:
            foe = self._nearest(run, SPARK_RANGE, hostile=True)
            if foe is not None:
                self._spark(run, foe)
                return self._did("spark", run, "", quiet=True)
        return False

    def _spark(self, run: Run, foe: Any) -> None:
        from src.body import PLAYER_TEAM
        from src.projectiles import build
        from src.spells import CATALOG
        from src.wand import Shot

        fx, fy = foe.center
        angle = math.atan2(fy - self.y, fx - self.x)
        spark = build(Shot(CATALOG["funke"]), self.x, self.y, angle, PLAYER_TEAM)
        spark.damage = SPARK_DAMAGE
        spark.blast = 0
        spark.splash = 0
        run.projectiles.items.append(spark)
        run.events.append("cast")

    def _did(self, key: str, run: Run, topic: str, *, quiet: bool = False) -> bool:
        self.cooldowns[key] = COOLDOWNS[key]
        self.state = "assist"
        self.pose_timer = ASSIST_TIME
        if topic and not quiet:
            self._say(run, topic)
        return True

    # ------------------------------------------------------- the bible helpers

    def _helpers(self, run: Run) -> None:
        if self.cooldowns["point"] <= 0:
            self.helper_point(run)
        if self.cooldowns["carry"] <= 0:
            self.helper_carry(run)
        self.helper_hug(run)

    def helper_point(self, run: Run) -> tuple[float, float] | None:
        """Point at a secret or a life capsule / heart / memory shard within POINT_RADIUS."""
        if self.cooldowns["point"] > 0:
            return None
        targets: list[tuple[float, float]] = []
        secret = getattr(run.level, "secret", None)
        if secret is not None:
            targets.append((float(secret[0]), float(secret[1])))
        for item in run.pickups:
            if getattr(item, "kind", "") in ("life_capsule", "heart", "memory_shard"):
                targets.append((float(item.x), float(item.y)))
        near = [t for t in targets if _dist(self.x, self.y, *t) <= POINT_RADIUS]
        if not near:
            return None
        target = min(near, key=lambda t: _dist(self.x, self.y, *t))
        self.pointing = target
        self.point_timer = POINT_TIME
        self.cooldowns["point"] = COOLDOWNS["point"]
        self.facing = 1 if target[0] >= self.x else -1
        run.emit("klonita_point", x=target[0], y=target[1])
        self._say(run, "point_secret")
        return target

    def helper_carry(self, run: Run) -> Pickup | None:
        """Fetch a pickup lying high above the player and drop it at her feet."""
        if self.cooldowns["carry"] > 0:
            return None
        player = run.player
        px, py = float(player.x), float(player.y)
        for item in run.pickups:
            if getattr(item, "kind", "") == "portal" or getattr(item, "portal", False):
                continue
            if py - item.y > CARRY_MIN_RISE and abs(item.x - px) < CARRY_REACH_X:
                item.x, item.y = px, py
                self.cooldowns["carry"] = COOLDOWNS["carry"]
                self.state = "assist"
                self.pose_timer = ASSIST_TIME
                self._say(run, "helper_carry")
                return item
        return None

    def helper_hug(self, run: Run) -> int:
        """Calm every peaceful creature within HUG_RADIUS; returns how many."""
        count = 0
        for creature in run.enemies.creatures:
            if creature.dead or creature.spec.stance not in PEACEFUL:
                continue
            cx, cy = creature.center
            if _dist(self.x, self.y, cx, cy) <= HUG_RADIUS:
                creature.calmed = max(getattr(creature, "calmed", 0.0), HUG_CALM)
                count += 1
        return count

    # ---------------------------------------------------------------- quirks

    def _quirk_roll(self, dt: float, run: Run) -> None:
        if self.quirk_used_in_universe:
            return
        self._quirk_clock += dt
        if self._quirk_clock < 1.0:
            return
        self._quirk_clock = 0.0
        for kind in QUIRKS:
            if self._quirk_possible(kind, run) and _rng(run).random() < QUIRK_CHANCE_PER_S:
                self.trigger_quirk(kind, run)
                return

    def _nearest(self, run: Run, radius: float, *, hostile: bool | None = None,
                 stances: tuple[str, ...] | None = None, prop: bool = False,
                 asleep: bool = False) -> Any:
        best, best_d = None, radius
        for creature in run.enemies.creatures:
            if creature.dead:
                continue
            spec = creature.spec
            if prop:
                if not (spec.prop and spec.blast):
                    continue
            elif spec.prop:
                continue
            if hostile is True and spec.stance != "hostile":
                continue
            if stances is not None and spec.stance not in stances:
                continue
            if asleep and not (getattr(creature, "dormant", False) or creature.state == "sleep"):
                continue
            cx, cy = creature.center
            d = _dist(self.x, self.y, cx, cy)
            if d < best_d:
                best, best_d = creature, d
        return best

    def _quirk_possible(self, kind: str, run: Run) -> bool:
        if kind == "shiny_poke":
            return self._nearest(run, POKE_RADIUS, prop=True) is not None
        if kind == "loud_sneeze":
            return self._nearest(run, SNEEZE_RADIUS, asleep=True) is not None
        if kind == "sample_nibble":
            return sum(c for _, c in self._samples(run)) >= NIBBLE_MIN_SAMPLES
        if kind == "tip_trader":
            layout = getattr(run, "workshop_layout", None)
            if not (run.in_workshop and layout is not None and run.traders and run.gold >= 5):
                return False
            return any(_dist(self.x, self.y, sx, sy) < TIP_RADIUS for sx, sy in layout.trader_slots)
        if kind == "feed_creature":
            return self._nearest(run, FEED_RADIUS, stances=PEACEFUL) is not None
        if kind == "warn_enemy":
            return self._nearest(run, WARN_RADIUS, hostile=True) is not None
        return False

    @staticmethod
    def _samples(run: Run) -> list[tuple[str, int]]:
        return [slot for slot in run.inventory.samples if slot]

    def trigger_quirk(self, kind: str, run: Run) -> bool:
        """Play quirk ``kind`` now; all quirks together fire at most once per universe."""
        if self.quirk_used_in_universe or kind not in QUIRKS or not self.active:
            return False
        if not self._quirk_possible(kind, run):
            return False
        if kind == "shiny_poke":
            prop = self._nearest(run, POKE_RADIUS, prop=True)
            prop.hurt(prop.hp, "Klonita")
        elif kind == "loud_sneeze":
            run.emit("noise", x=self.x, y=self.y, radius=SNEEZE_RADIUS)
        elif kind == "sample_nibble":
            self._nibble(run)
        elif kind == "tip_trader":
            tip = min(run.gold, _rng(run).randint(5, 15))
            run.gold -= tip
        elif kind == "feed_creature":
            pet = self._nearest(run, FEED_RADIUS, stances=PEACEFUL)
            pet.hp = min(pet.max_hp, pet.hp + pet.max_hp * FEED_SHARE)
        elif kind == "warn_enemy":
            foe = self._nearest(run, WARN_RADIUS, hostile=True)
            foe.dodge_charges = getattr(foe, "dodge_charges", 0) + 1
        self.quirk_used_in_universe = True
        self.state = "quirk"
        self.pose_timer = ASSIST_TIME
        topic = f"quirk_{kind}" if kind in ("tip_trader", "feed_creature", "warn_enemy") else kind
        self._say(run, topic)
        return True

    def _nibble(self, run: Run) -> None:
        """Eat one tier-1 sample (any sample if none is tier 1) and drop 15 gold."""
        from src.loot import Pickup
        from src.samples import SAMPLES

        slots = run.inventory.samples
        choice = None
        for i, slot in enumerate(slots):
            if slot and SAMPLES.get(slot[0]) is not None and SAMPLES[slot[0]].tier == 1:
                choice = i
                break
        if choice is None:
            choice = next(i for i, slot in enumerate(slots) if slot)
        key, count = slots[choice]
        slots[choice] = (key, count - 1) if count > 1 else None
        run.pickups.append(Pickup(self.x, self.y + 8, kind="gold", amount=NIBBLE_GOLD))

    # ------------------------------------------------------------------ misc

    def _say(self, run: Run, topic: str) -> None:
        say = getattr(run, "say", None)
        if say is not None:
            say("Klonita", line_for(topic, _rng(run)), self.x, self.y - 10)

    def new_universe(self) -> None:
        """Called when a universe is entered: one quirk again, nothing pointed at."""
        self.quirk_used_in_universe = False
        self.pointing = None
        self.point_timer = 0.0
        self._quirk_clock = 0.0

    def to_data(self) -> dict[str, object]:
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "hp": round(self.hp, 2),
            "max_hp": round(self.max_hp, 2),
            "state": self.state,
            "knocked_timer": round(self.knocked_timer, 3),
            "quirk_used_in_universe": self.quirk_used_in_universe,
            "cooldowns": dict(self.cooldowns),
            "facing": self.facing,
            "pointing": list(self.pointing) if self.pointing else None,
            "point_timer": round(self.point_timer, 3),
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Klonita:
        if not data:
            return cls()
        pointing = data.get("pointing")
        k = cls(
            x=float(data.get("x", 0.0)),  # type: ignore[arg-type]
            y=float(data.get("y", 0.0)),  # type: ignore[arg-type]
            hp=float(data.get("hp", 60.0)),  # type: ignore[arg-type]
            max_hp=float(data.get("max_hp", 60.0)),  # type: ignore[arg-type]
            state=str(data.get("state", "follow")),
            knocked_timer=float(data.get("knocked_timer", 0.0)),  # type: ignore[arg-type]
            quirk_used_in_universe=bool(data.get("quirk_used_in_universe", False)),
            facing=int(data.get("facing", 1)),  # type: ignore[arg-type]
            pointing=(float(pointing[0]), float(pointing[1])) if isinstance(pointing, (list, tuple)) and len(pointing) == 2 else None,  # type: ignore[index]
            point_timer=float(data.get("point_timer", 0.0)),  # type: ignore[arg-type]
        )
        cooldowns = data.get("cooldowns")
        if isinstance(cooldowns, dict):
            for key in k.cooldowns:
                k.cooldowns[key] = float(cooldowns.get(key, 0.0))  # type: ignore[arg-type]
        if k.state not in KLONITA_STATES:
            k.state = "follow"
        return k
