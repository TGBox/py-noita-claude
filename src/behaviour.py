"""Contract V1: Creature special abilities and behaviour helpers (Cards A12, A13)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enemies import Creature
    from .loot import Pickup
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
    raise NotImplementedError("Card A12")


def handle_morph_check(creature: Creature, ability: Ability) -> bool:
    """Trigger a one-time morph when HP ratio drops below ability.param_float."""
    raise NotImplementedError("Card A12")


def handle_reflect_projectiles(
    creature: Creature,
    projectiles: list[Projectile],
    out_events: list[tuple[str, dict[str, object]]],
) -> int:
    """Reflect nearby non-piercing projectiles and return count reflected."""
    raise NotImplementedError("Card A12")


def handle_steal_pickup(
    creature: Creature,
    pickups: list[Pickup],
    out_events: list[tuple[str, dict[str, object]]],
) -> bool:
    """Pick up a nearby gold/sample pickup into creature.carrying."""
    raise NotImplementedError("Card A12")


def handle_eat_material(
    creature: Creature,
    material_name: str,
    world: World,
    pickups: list[Pickup],
) -> bool:
    """Consume an adjacent matching material cell, heal, and optionally drop a byproduct."""
    raise NotImplementedError("Card A12")


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

