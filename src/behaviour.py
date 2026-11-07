"""Contract V1: Creature special abilities and behaviour helpers (Cards A12, A13)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src import materials as mat
from src.loot import Pickup

if TYPE_CHECKING:
    from .enemies import Creature
    from .player import Player
    from .projectiles import Projectile
    from .world import World

PIERCING_FORMS: frozenset[str] = frozenset({"beam", "lance", "laser", "lightning", "chain", "saw"})

GRAZE_MATERIAL: dict[str, str] = {
    "rostkaefer": "rust",
    "zottenwurm": "flesh",
    "aktenfresser": "paper",
    "marzipanschwein": "dough",
    "blattlaus": "zucker",
}

REFLECT_RADIUS = 24.0
STEAL_RADIUS = 16.0
GRAZE_DROP_GOLD: dict[str, int] = {"marzipanschwein": 2, "blattlaus": 1}  # byproduct of grazing

SPLIT_SIZES: tuple[tuple[float, float], ...] = (
    (1.0, 1.0),
    (0.7, 0.55),
    (0.5, 0.30),
)


@dataclass(frozen=True)
class Ability:
    kind: str
    param: str = ""
    param_float: float = 0.0


@dataclass
class BehaviourContext:
    dt: float
    world: World
    player: Player
    creatures: list[Creature]
    projectiles: list[Projectile]
    pickups: list[Pickup] = field(default_factory=list)
    grudges: set[tuple[str, str]] = field(default_factory=set)
    on_beat: bool = True
    rng: random.Random = field(default_factory=random.Random)
    out_events: list[tuple[str, dict[str, object]]] = field(default_factory=list)


def handle_split_on_death(
    creature: Creature,
    ability: Ability,
    out_events: list[tuple[str, dict[str, object]]],
) -> None:
    """Emit a 'split' event if creature.generation < 2."""
    if creature.generation >= 2:
        return
    species = ability.param or creature.spec.key
    out_events.append(
        (
            "split",
            {
                "species": species,
                "x": float(creature.center[0]),
                "y": float(creature.center[1]),
                "generation": creature.generation,
            },
        )
    )


def handle_morph_check(creature: Creature, ability: Ability) -> bool:
    """Trigger a one-time morph when HP ratio drops below ability.param_float."""
    if creature.morphed or creature.max_hp <= 0:
        return False
    if creature.hp / creature.max_hp >= ability.param_float:
        return False
    creature.morphed = True
    return True


def handle_reflect_projectiles(
    creature: Creature,
    projectiles: list[Projectile],
    out_events: list[tuple[str, dict[str, object]]],
) -> int:
    """Reflect nearby non-piercing projectiles and return count reflected."""
    cx, cy = creature.center
    reflected = 0
    for proj in projectiles:
        form = proj.form if isinstance(proj.form, str) else getattr(proj.form, "key", "")
        if form in PIERCING_FORMS or id(creature) in proj.hit_ids:
            continue
        if proj.owner_species and proj.owner_species == creature.spec.key:
            continue
        if math.hypot(proj.x - cx, proj.y - cy) > REFLECT_RADIUS:
            continue
        proj.vx = -proj.vx
        proj.vy = -proj.vy
        proj.from_player = True
        proj.hit_ids.add(id(creature))
        reflected += 1
        out_events.append(
            ("reflect", {"species": creature.spec.key, "x": float(proj.x), "y": float(proj.y)})
        )
    return reflected


def handle_steal_pickup(
    creature: Creature,
    pickups: list[Pickup],
    out_events: list[tuple[str, dict[str, object]]],
) -> bool:
    """Pick up a nearby gold/sample pickup into creature.carrying."""
    if creature.carrying:
        return False
    cx, cy = creature.center
    best: Pickup | None = None
    best_distance = STEAL_RADIUS
    for item in pickups:
        if item.kind not in ("gold", "sample"):
            continue
        distance = math.hypot(item.x - cx, item.y - cy)
        if distance <= best_distance:
            best, best_distance = item, distance
    if best is None:
        return False
    pickups.remove(best)
    creature.carrying = best.kind
    out_events.append(("steal", {"item_key": best.item_key or best.kind, "value": best.amount}))
    return True


def handle_eat_material(
    creature: Creature,
    material_name: str,
    world: World,
    pickups: list[Pickup],
) -> bool:
    """Consume an adjacent matching material cell, heal, and optionally drop a byproduct."""
    material_id = mat.MAT_ID.get(material_name)
    if material_id is None:
        return False
    for cy in range(creature.y - 1, creature.y + creature.height + 1):
        for cx in range(creature.x - 1, creature.x + creature.width + 1):
            if world.get(cx, cy) != material_id:
                continue
            world.set(cx, cy, mat.AIR, force=True)
            creature.hp = min(creature.max_hp, creature.hp + max(2.0, creature.max_hp * 0.2))
            gold = GRAZE_DROP_GOLD.get(creature.spec.key, 0)
            if gold:
                pickups.append(Pickup(float(cx), float(cy), kind="gold", amount=gold))
            return True
    return False


def handle_aura(
    creature: Creature,
    ability: Ability,
    player: Player,
    creatures: list[Creature],
    dt: float = 0.016,
) -> None:
    """Apply aura status effects within ability.param_float radius."""
    raise NotImplementedError("Card A13")


def handle_teleport(
    creature: Creature,
    world: World,
    rng: random.Random,
) -> bool:
    """Teleport creature to a free air cell 40..110 px away."""
    raise NotImplementedError("Card A13")


def handle_summon(
    creature: Creature,
    ability: Ability,
    out_events: list[tuple[str, dict[str, object]]],
) -> None:
    """Emit a 'summon' event for ability.param with count int(max(1, ability.param_float))."""
    raise NotImplementedError("Card A13")


def handle_kamikaze(
    creature: Creature,
    ability: Ability,
    player: Player,
    world: World,
    out_events: list[tuple[str, dict[str, object]]],
) -> bool:
    """Detonate if player is within ability.param_float (or 16 px) and set HP to 0."""
    raise NotImplementedError("Card A13")


def handle_burrow(
    creature: Creature,
    target_pos: tuple[float, float],
    world: World,
    dt: float,
) -> None:
    """Move creature through sand/dirt/flesh/dough towards target_pos."""
    raise NotImplementedError("Card A13")


def apply_chorus_buff(creature: Creature, creatures: list[Creature]) -> float:
    """Return damage multiplier (1.5 if >= 3 'moenchsfisch' within 90 px, else 1.0)."""
    raise NotImplementedError("Card A13")


def tick_abilities(creature: Creature, ctx: BehaviourContext) -> None:
    """Dispatch all abilities on creature.spec.abilities for the current tick."""
    raise NotImplementedError("Card A13")
