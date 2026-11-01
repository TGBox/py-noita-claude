"""Universe rules (work package T4, bible chapter 02 "Regelbibliothek").

Every universe has one main rule. A rule is data (key + parameters per rank) plus the
hooks the run calls: material values when a world is built, gravity and bounces for
bodies and projectiles, a damage factor for casts and a per-frame update.

The six MVP rules and their rank scaling:

=====================  ==========================  ==========  ============================
rule                   rank 1                      rank 2      rank 3
=====================  ==========================  ==========  ============================
``rule_living_walls``  flesh regrows 1 cell/s per  twice that  three times
                       100 edge cells
``rule_paperwork``     flammability x1.5           x2          x3
``rule_bounce``        +2 bounces                  +3          +4, enemy shots bounce too
``rule_tiny``          gravity 50 %                45 %        40 %
``rule_beat``          beat 0.5 s, +25 % damage    0.4 s       0.33 s, +30 %
``rule_flooded``       breath 15 s                 11 s        8 s
=====================  ==========================  ==========  ============================
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

from src import materials as mat
from src.materials import AIR, KIND, LIQUID

if TYPE_CHECKING:
    from src.run import Run

NAMES_DE = {
    "rule_living_walls": "Alles lebt",
    "rule_paperwork": "Papierkrieg",
    "rule_bounce": "Gummiwelt",
    "rule_tiny": "Winzig",
    "rule_beat": "Bass",
    "rule_flooded": "Geflutet",
}
DESCRIPTIONS_DE = {
    "rule_living_walls": "Fleisch wächst in Löcher nach.",
    "rule_paperwork": "Papier brennt schneller und weiter.",
    "rule_bounce": "Geschosse prallen öfter ab.",
    "rule_tiny": "Schwerkraft wirkt schwächer.",
    "rule_beat": "Auf dem Beat gefeuert trifft härter.",
    "rule_flooded": "Unter Wasser wird die Luft knapp.",
}

RANK_PARAMS: dict[str, tuple[dict[str, Any], ...]] = {
    "rule_living_walls": ({"regrow": 1.0}, {"regrow": 2.0}, {"regrow": 3.0}),
    "rule_paperwork": ({"flammability": 1.5}, {"flammability": 2.0}, {"flammability": 3.0}),
    "rule_bounce": (
        {"bounces": 2, "enemy_bounces": 0},
        {"bounces": 3, "enemy_bounces": 0},
        {"bounces": 4, "enemy_bounces": 2},
    ),
    "rule_tiny": ({"gravity": 0.5}, {"gravity": 0.45}, {"gravity": 0.4}),
    "rule_beat": (
        {"period": 0.5, "bonus": 0.25},
        {"period": 0.4, "bonus": 0.25},
        {"period": 0.33, "bonus": 0.30},
    ),
    "rule_flooded": ({"breath": 15.0}, {"breath": 11.0}, {"breath": 8.0}),
}
RULE_KEYS: tuple[str, ...] = tuple(RANK_PARAMS)

BEAT_WINDOW = 0.08  # seconds before/after a beat that still count as "on the beat"
REGROW_PER_EDGE = 1 / 100  # living walls: cells per second per edge cell (rank 1)
REGROW_KEEP_OUT = 14  # no regrowth this close to the player (never wall them in)
DROWN_DPS = 10.0
BREATH_REFILL = 3.0  # seconds of breath regained per second in the air


@dataclass
class Rule:
    """The active rule of a universe at one rank (1-3). ``key`` "" means no rule."""

    key: str = ""
    rank: int = 1
    params: dict[str, Any] = field(default_factory=dict)
    beat_time: float = 0.0  # rule_beat: seconds since the last beat
    beats: int = 0
    breath: float = 0.0  # rule_flooded: seconds of air left
    _regrow_budget: float = 0.0

    @classmethod
    def make(cls, key: str, rank: int = 1) -> Rule:
        if not key:
            return cls()
        if key not in RANK_PARAMS:
            raise ValueError(f"unknown rule {key}")
        rank = max(1, min(3, rank))
        rule = cls(key, rank, dict(RANK_PARAMS[key][rank - 1]))
        rule.breath = rule.max_breath
        return rule

    @property
    def name_de(self) -> str:
        return NAMES_DE.get(self.key, "Keine Regel")

    # ------------------------------------------------------------ world building

    def material_set(self, base: mat.MaterialSet) -> mat.MaterialSet:
        """The universe's material set as this rule changes it (registered by key)."""
        factor = self.params.get("flammability", 1.0)
        if factor == 1.0:
            return base
        changed = []
        for material in base.resolved():
            if material.kind == mat.SOLID and material.flammability > 0:
                material = replace(
                    material, flammability=min(1.0, material.flammability * factor)
                )
            changed.append(material)
        derived = mat.MaterialSet(
            f"{base.key}+{self.key}{self.rank}", tuple(changed), base.aliases, base.reactions
        )
        mat.DERIVED.setdefault(derived.key, derived)
        return mat.DERIVED[derived.key]

    # ------------------------------------------------------------ physics hooks

    @property
    def gravity_scale(self) -> float:
        return float(self.params.get("gravity", 1.0))

    def bounce_bonus(self, enemy: bool) -> int:
        return int(self.params.get("enemy_bounces" if enemy else "bounces", 0))

    @property
    def max_breath(self) -> float:
        return float(self.params.get("breath", 0.0))

    @property
    def on_beat(self) -> bool:
        period = self.params.get("period")
        if not period:
            return False
        return self.beat_time <= BEAT_WINDOW or self.beat_time >= period - BEAT_WINDOW

    def cast_factor(self) -> float:
        """Damage factor for a cast right now (rule_beat rewards casting on the beat)."""
        return 1.0 + self.params.get("bonus", 0.0) if self.on_beat else 1.0

    def light_factor(self) -> float:
        """Brightness pulse (rule_beat: bright on the beat, fading until the next)."""
        period = self.params.get("period")
        if not period:
            return 1.0
        return 1.0 + 0.35 * max(0.0, 1.0 - self.beat_time / period) ** 3

    # ------------------------------------------------------------ per frame

    def update(self, run: Run, dt: float, area: tuple[int, int, int, int] | None) -> None:
        if self.key == "rule_beat":
            self._beat(run, dt)
        elif self.key == "rule_flooded":
            self._breathe(run, dt)
        elif self.key == "rule_living_walls":
            self._regrow(run, dt, area)

    def _beat(self, run: Run, dt: float) -> None:
        period = self.params["period"]
        self.beat_time += dt
        while self.beat_time >= period:
            self.beat_time -= period
            self.beats += 1
            run.events.append("beat")

    def _breathe(self, run: Run, dt: float) -> None:
        player = run.player
        if player.dead:
            return
        head = run.world.get(int(player.center[0]), player.y + 1)
        if KIND[head] == LIQUID:
            self.breath = max(0.0, self.breath - dt)
            if self.breath <= 0:
                player.hurt(DROWN_DPS * dt, "Ertrunken")
        else:
            self.breath = min(self.max_breath, self.breath + BREATH_REFILL * dt)

    def _regrow(self, run: Run, dt: float, area: tuple[int, int, int, int] | None) -> None:
        """Air next to flesh turns into flesh again (holes slowly close).

        Random cells of the simulated area are sampled; ``REGROW_PER_EDGE`` cells per
        second and edge cell grow back on average, ``regrow`` times that per rank.
        """
        if not mat.has("flesh"):
            return
        world = run.world
        x0, y0, x1, y1 = area or (0, 0, world.width, world.height)
        x0, y0 = max(2, x0), max(2, y0)
        x1, y1 = min(world.width - 2, x1), min(world.height - 2, y1)
        if x1 <= x0 or y1 <= y0:
            return
        cells = (x1 - x0) * (y1 - y0)
        self._regrow_budget += self.params["regrow"] * REGROW_PER_EDGE * cells * dt
        samples, self._regrow_budget = int(self._regrow_budget), self._regrow_budget % 1
        flesh = mat.id_of("flesh")
        px, py = run.player.center
        rng = world.rng
        for _ in range(samples):
            x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
            if world.get(x, y) != AIR:
                continue
            if abs(x - px) < REGROW_KEEP_OUT and abs(y - py) < REGROW_KEEP_OUT:
                continue
            around = (world.get(x - 1, y), world.get(x + 1, y), world.get(x, y - 1), world.get(x, y + 1))
            if sum(1 for cell in around if cell == flesh) >= 2:
                world.set_cell(x, y, flesh)


def describe_de(rule: Rule) -> str:
    """Short line for the HUD (``DESCRIPTIONS_DE`` holds the explanation)."""
    if not rule.key:
        return ""
    return f"Regel: {rule.name_de} · Rang {rule.rank}"

