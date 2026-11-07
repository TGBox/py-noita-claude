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
AURA_HOLD = 1.0
TELEPORT_MIN = 40.0
TELEPORT_MAX = 110.0
TELEPORT_ATTEMPTS = 24
TELEPORT_INTERVAL = 4.0
SUMMON_INTERVAL = 8.0
KAMIKAZE_RANGE = 16.0
KAMIKAZE_BLAST = 6
KAMIKAZE_DAMAGE = 15.0
BURROW_SPEED = 20.0
BURROW_MATERIALS = ("sand", "dirt", "flesh", "dough")
CHORUS_RADIUS = 90.0
CHORUS_FAR_RADIUS = 180.0
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
    radius = ability.param_float or 40.0
    cx, cy = creature.center
    status = ability.param
    if status == "heal_allies":
        for other in creatures:
            if other is creature or other.dead or other.species != creature.species:
                continue
            if math.hypot(other.center[0] - cx, other.center[1] - cy) <= radius:
                other.hp = min(other.max_hp, other.hp + 5.0 * dt)
        return
    target = player.body
    px, py = target.center
    if math.hypot(px - cx, py - cy) > radius:
        return
    hold = AURA_HOLD
    if status == "slow":
        target.chilled = max(target.chilled, hold)
        target.sticky = max(target.sticky, hold)
    elif status == "poison":
        target.poisoned = max(target.poisoned, hold)
    elif status == "stamp_tax":
        target.stamped_bad = max(target.stamped_bad, hold)
    elif status == "shock":
        target.charged = max(target.charged, hold)


def handle_teleport(
    creature: Creature,
    world: World,
    rng: random.Random,
) -> bool:
    """Teleport creature to a free air cell 40..110 px away."""
    for _ in range(TELEPORT_ATTEMPTS):
        angle = rng.uniform(0.0, math.tau)
        distance = rng.uniform(TELEPORT_MIN, TELEPORT_MAX)
        nx = int(creature.x + math.cos(angle) * distance)
        ny = int(creature.y + math.sin(angle) * distance)
        if nx < 1 or ny < 1 or nx + creature.width >= world.width:
            continue
        if ny + creature.height >= world.height:
            continue
        if creature.blocked(world, nx, ny):
            continue
        creature.x, creature.y = nx, ny
        creature.vx = creature.vy = 0.0
        return True
    return False


def handle_summon(
    creature: Creature,
    ability: Ability,
    out_events: list[tuple[str, dict[str, object]]],
) -> None:
    """Emit a 'summon' event for ability.param with count int(max(1, ability.param_float))."""
    cx, cy = creature.center
    out_events.append(
        (
            "summon",
            {
                "species": creature.spec.key,
                "target_species": ability.param,
                "x": float(cx),
                "y": float(cy),
                "count": int(max(1, ability.param_float)),
            },
        )
    )


def handle_kamikaze(
    creature: Creature,
    ability: Ability,
    player: Player,
    world: World,
    out_events: list[tuple[str, dict[str, object]]],
) -> bool:
    """Detonate if player is within ability.param_float (or 16 px) and set HP to 0."""
    cx, cy = creature.center
    px, py = player.body.center
    trigger = ability.param_float if ability.param_float > 0 else KAMIKAZE_RANGE
    if math.hypot(px - cx, py - cy) > trigger:
        return False
    destroyed = world.explode(int(cx), int(cy), KAMIKAZE_BLAST)
    if math.hypot(px - cx, py - cy) <= KAMIKAZE_BLAST + 4:
        player.body.hurt(KAMIKAZE_DAMAGE, "Explosion")
    creature.hp = 0.0
    out_events.append(("noise", {"x": float(cx), "y": float(cy), "radius": 80.0}))
    if destroyed > 0:
        out_events.append(("cells_destroyed", {"count": destroyed, "gold_vein_cells": 0}))
    return True


def handle_burrow(
    creature: Creature,
    target_pos: tuple[float, float],
    world: World,
    dt: float,
) -> None:
    """Move creature through sand/dirt/flesh/dough towards target_pos."""
    acc = getattr(creature, "_burrow_acc", 0.0) + BURROW_SPEED * dt
    steps = int(acc)
    creature._burrow_acc = acc - steps  # type: ignore[attr-defined]
    diggable = {mat.MAT_ID[k] for k in BURROW_MATERIALS if k in mat.MAT_ID}
    for _ in range(steps):
        cx, cy = creature.center
        dx, dy = target_pos[0] - cx, target_pos[1] - cy
        if abs(dx) < 1 and abs(dy) < 1:
            return
        sx = (dx > 0) - (dx < 0) if abs(dx) >= abs(dy) else 0
        sy = (dy > 0) - (dy < 0) if abs(dy) > abs(dx) else 0
        nx, ny = creature.x + sx, creature.y + sy
        cells = [
            (x, y) for y in range(ny, ny + creature.height) for x in range(nx, nx + creature.width)
        ]
        if any(
            world.get(x, y) not in diggable
            and mat.KIND[world.get(x, y)] not in (mat.EMPTY, mat.GAS)
            for x, y in cells
        ):
            return
        for x, y in cells:
            if world.get(x, y) in diggable:
                world.set(x, y, mat.AIR, force=True)
        creature.x, creature.y = nx, ny


def apply_chorus_buff(creature: Creature, creatures: list[Creature]) -> float:
    """Return damage multiplier (1.5 if >= 3 'moenchsfisch' within 90 px, else 1.0)."""
    if creature.species != "moenchsfisch":
        return 1.0
    cx, cy = creature.center

    def count_within(radius: float) -> int:
        return sum(
            1
            for other in creatures
            if other.species == "moenchsfisch"
            and not other.dead
            and math.hypot(other.center[0] - cx, other.center[1] - cy) <= radius
        )

    if count_within(CHORUS_RADIUS) >= 3:
        return 1.5
    if count_within(CHORUS_FAR_RADIUS) >= 3:
        return 1.25
    return 1.0


def tick_abilities(creature: Creature, ctx: BehaviourContext) -> None:
    """Dispatch all abilities on creature.spec.abilities for the current tick."""
    cooldowns: dict[str, float] = creature.__dict__.setdefault("_ability_cd", {})
    for kind in list(cooldowns):
        cooldowns[kind] = max(0.0, cooldowns[kind] - ctx.dt)

    def ready(ability: Ability, interval: float) -> bool:
        if cooldowns.get(ability.kind, 0.0) > 0.0:
            return False
        cooldowns[ability.kind] = interval
        return True

    for ability in getattr(creature.spec, "abilities", ()):
        kind = ability.kind
        if kind == "eat_material" or kind == "graze":
            handle_eat_material(creature, ability.param, ctx.world, ctx.pickups)
        elif kind == "steal":
            handle_steal_pickup(creature, ctx.pickups, ctx.out_events)
        elif kind == "reflect":
            handle_reflect_projectiles(creature, ctx.projectiles, ctx.out_events)
        elif kind == "aura":
            handle_aura(creature, ability, ctx.player, ctx.creatures, ctx.dt)
        elif kind == "summon" and ready(ability, SUMMON_INTERVAL):
            handle_summon(creature, ability, ctx.out_events)
        elif kind == "teleport" and ready(ability, TELEPORT_INTERVAL):
            handle_teleport(creature, ctx.world, ctx.rng)
        elif kind == "kamikaze":
            handle_kamikaze(creature, ability, ctx.player, ctx.world, ctx.out_events)
        elif kind == "burrow":
            handle_burrow(creature, ctx.player.body.center, ctx.world, ctx.dt)
        elif kind == "morph":
            handle_morph_check(creature, ability)
