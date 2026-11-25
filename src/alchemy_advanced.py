"""Advanced Alchemy Engine, Distilling Cauldron, and Pressurized Flasks (Phase I01-I03)."""

from __future__ import annotations

import math
import random
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field

from src import materials as mat
from src.body import Body
from src.flask import CAPACITY, Flask
from src.materials import AIR, BEDROCK, KIND, SOLID
from src.world import World

BREW_TIME = 5.0
PRESSURE_BLAST_RADIUS = 60
SCHUTZTONIKUM_SHIELD = 40.0
SCHUTZTONIKUM_FLUX_TIME = 25.0
SCHUTZTONIKUM_PERK_HEAL = 20.0
ALCHEMIST_HEAL_PERKS = frozenset({"blutsauger", "alchemie_magen"})


@dataclass(frozen=True)
class SecretAlchemyRecipes:
    """Two deterministic 3-ingredient recipes generated per run seed."""

    schutztonikum_zutaten: tuple[str, str, str]
    midas_schmelze_zutaten: tuple[str, str, str]


class SecretAlchemyEngine:
    """Deterministic seed alchemy constrained strictly to the active 11+10 palette."""

    @staticmethod
    def recipes_for_seed(seed: int, active_keys: Sequence[str] | None = None) -> SecretAlchemyRecipes:
        keys = active_keys if active_keys is not None else mat.KEYS
        pool = [k for k in keys if k not in ("air", "bedrock")]
        if len(pool) < 3:
            raise ValueError("need at least 3 non-air/bedrock materials in active set")
        rng = random.Random(seed ^ 0xA1C4E3)
        tonic = tuple(rng.sample(pool, 3))
        midas = tuple(rng.sample(pool, 3))
        if len(pool) >= 6:
            remaining = [k for k in pool if k not in tonic]
            midas = tuple(rng.sample(remaining, 3))
        return SecretAlchemyRecipes(tonic, midas)  # type: ignore[arg-type]

    @staticmethod
    def check_world_reaction(
        world: World, cx: int, cy: int, recipes: SecretAlchemyRecipes
    ) -> str | None:
        """Check 3x3 neighborhood at (cx, cy) for secret 3-ingredient reactions."""
        found_keys: set[str] = set()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                cid = world.get(cx + dx, cy + dy)
                key = mat.key_of(cid)
                if key:
                    found_keys.add(key)

        if all(k in found_keys for k in recipes.schutztonikum_zutaten):
            if "schutztonikum" in mat.MAT_ID and world.get(cx, cy) != BEDROCK:
                world.set_cell(cx, cy, mat.MAT_ID["schutztonikum"])
            return "schutztonikum"

        if all(k in found_keys for k in recipes.midas_schmelze_zutaten):
            gold_id = mat.MAT_ID.get("gold_vein")
            if gold_id is not None:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        cell = world.get(nx, ny)
                        if cell != BEDROCK and KIND[cell] == SOLID:
                            world.set_cell(nx, ny, gold_id)
            return "gold_vein"

        return None

    @staticmethod
    def drink_schutztonikum(body: Body, perks: Collection[str] = ()) -> dict[str, float]:
        """Grant shield + flux boost; never heal HP unless blutsauger/alchemie_magen active."""
        body.shield_hp += SCHUTZTONIKUM_SHIELD
        body.flux_boost_time = max(getattr(body, "flux_boost_time", 0.0), SCHUTZTONIKUM_FLUX_TIME)
        healed = 0.0
        if any(p in perks for p in ALCHEMIST_HEAL_PERKS):
            before = body.hp
            body.hp = min(body.max_hp, body.hp + SCHUTZTONIKUM_PERK_HEAL)
            healed = body.hp - before
        return {
            "shield": SCHUTZTONIKUM_SHIELD,
            "flux_time": SCHUTZTONIKUM_FLUX_TIME,
            "healed": healed,
        }


@dataclass
class Cauldron:
    """Distilling copper cauldron (ws_kessel) taking up to 3 flask funnels of 300 capacity."""

    capacity_per_funnel: int = CAPACITY
    funnels: list[tuple[str, int]] = field(default_factory=list)
    brewing: bool = False
    brew_timer: float = 0.0
    last_result: str | None = None

    def add_from_flask(self, flask: Flask, amount: int = 30) -> bool:
        """Pour up to ``amount`` cells from flask into an open funnel (max 3 funnels)."""
        if flask.empty or flask.key is None or len(self.funnels) >= 3:
            return False
        pour = min(flask.amount, amount, self.capacity_per_funnel)
        if pour <= 0:
            return False
        self.funnels.append((flask.key, pour))
        flask._drain(pour)
        return True

    def add_reagent(self, key: str, amount: int = 30) -> bool:
        """Direct helper to add one reagent funnel up to capacity 300."""
        if not key or len(self.funnels) >= 3 or amount <= 0:
            return False
        self.funnels.append((key, min(amount, self.capacity_per_funnel)))
        return True

    def ignite(self) -> bool:
        """Start 5-second boiling when heated from below with fire."""
        if not self.funnels or self.brewing:
            return False
        self.brewing = True
        self.brew_timer = BREW_TIME
        self.last_result = None
        return True

    def update(
        self,
        dt: float,
        recipes: SecretAlchemyRecipes,
        world: World | None = None,
        cx: int = 0,
        cy: int = 0,
    ) -> str | None:
        """Advance boiling; returns brewed output key on completion."""
        if not self.brewing:
            return None
        self.brew_timer -= dt
        if self.brew_timer > 0.0:
            return None
        self.brewing = False
        self.brew_timer = 0.0
        ingredients = {key for key, _amt in self.funnels}
        self.funnels.clear()

        if set(recipes.schutztonikum_zutaten).issubset(ingredients):
            self.last_result = "schutztonikum"
        elif set(recipes.midas_schmelze_zutaten).issubset(ingredients):
            self.last_result = "gold_vein"
        else:
            self.last_result = "smoke_fail"
            if world is not None:
                smoke_id = mat.MAT_ID.get("smoke", mat.SMOKE)
                for dy in range(-3, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if world.get(nx, ny) == AIR:
                            world.set_cell(nx, ny, smoke_id)
        return self.last_result


@dataclass(frozen=True)
class CauldronRoom:
    """Secret alchemy laboratory chamber spawned from rank 2 upward (I02)."""

    x0: int
    y0: int
    x1: int
    y1: int
    cauldron_pos: tuple[int, int]
    cauldron: Cauldron


def generate_cauldron_room(
    world: World, rank: int, rng: random.Random
) -> CauldronRoom | None:
    """Generate a secret cauldron room in rank >= 2 universes; None in rank 1."""
    if rank < 2 or world.width < 80 or world.height < 60:
        return None
    w, h = 28, 18
    x0 = rng.randint(12, max(12, world.width - w - 12))
    y0 = rng.randint(12, max(12, world.height - h - 12))
    x1, y1 = x0 + w, y0 + h
    wall = mat.MAT_ID.get("rock", mat.ROCK)
    fire_id = mat.MAT_ID.get("fire", mat.FIRE)
    world.fill_rect(x0, y0, x1, y1, wall)
    world.fill_rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, AIR)
    cx, cy = (x0 + x1) // 2, y1 - 4
    world.fill_rect(cx - 2, cy + 1, cx + 3, cy + 2, fire_id)
    return CauldronRoom(x0, y0, x1, y1, (cx, cy), Cauldron())


def shatter_pressurized_flask(
    world: World, x: float, y: float, flask: Flask, bodies: Sequence[Body] = ()
) -> int:
    """Burst a pressurized flask into a 60 px aerosol shockwave (I03). Returns hit bodies."""
    if not flask.is_pressurized:
        return 0
    cx, cy = int(x), int(y)
    world.explode(cx, cy, max(4, PRESSURE_BLAST_RADIUS // 4))
    if not flask.empty:
        world.splash(cx, cy, min(20, PRESSURE_BLAST_RADIUS // 3), flask.material)
    hits = 0
    for body in bodies:
        if not body.dead and math.hypot(body.center[0] - cx, body.center[1] - cy) <= PRESSURE_BLAST_RADIUS:
            body.hurt(18.0, "Überdruck-Phiole")
            hits += 1
    flask.material, flask.amount = None, 0
    flask.pressure = 0.0
    flask.reagents.clear()
    return hits
