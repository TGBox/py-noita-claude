"""Data-driven reaction table: what happens when two materials touch.

Every tick, each cell of an *actor* material looks at its four neighbours. If a rule
exists for (actor, neighbour), it fires with the given chance and both cells turn
into their results. Burning is handled separately through ``Material.flammability``
so that every flammable material burns without needing its own rule.

Adding a new interaction means adding one line to ``REACTIONS``.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.materials import (
    ACID,
    AIR,
    BLOOD,
    BONE,
    BONE_DUST,
    CRUST,
    FIRE,
    FLESH,
    FUME,
    GROWTH,
    MAGMA,
    MATERIAL_COUNT,
    MUCUS,
    PUS,
    SINEW,
    SMOKE,
    SPARK,
    SPENT,
    SPORES,
    TALLOW,
)


@dataclass(frozen=True)
class Reaction:
    """``actor`` next to ``neighbour`` turns into ``actor_into`` / ``neighbour_into``."""

    actor: int
    neighbour: int
    actor_into: int
    neighbour_into: int
    chance: float  # per tick and per touching neighbour


REACTIONS: tuple[Reaction, ...] = (
    # Fire
    Reaction(FIRE, BLOOD, SMOKE, CRUST, 0.5),  # blood douses fire and cooks into scab
    Reaction(FIRE, FLESH, FIRE, CRUST, 0.02),  # flesh chars instead of burning away
    # Blood soaks bone dust into scab. (It no longer clots in open air: falling drops
    # used to freeze into floating specks and pool surfaces into lids that plugged tunnels.)
    Reaction(BLOOD, BONE_DUST, BLOOD, CRUST, 0.002),
    # Acid dissolves organic matter into fumes (and is used up doing so)
    Reaction(ACID, FLESH, FUME, AIR, 0.03),
    Reaction(ACID, SINEW, FUME, AIR, 0.03),
    Reaction(ACID, CRUST, FUME, AIR, 0.03),
    Reaction(ACID, GROWTH, FUME, AIR, 0.05),
    Reaction(ACID, BONE_DUST, FUME, AIR, 0.02),
    Reaction(ACID, BONE, FUME, AIR, 0.004),
    # Growth creeps through flesh, feeds on blood and releases spores
    Reaction(GROWTH, FLESH, GROWTH, GROWTH, 0.003),
    Reaction(GROWTH, BLOOD, GROWTH, GROWTH, 0.01),
    Reaction(GROWTH, AIR, GROWTH, SPORES, 0.0005),
    # Mucus smothers fire, binds spores and is slowly eaten by acid
    Reaction(FIRE, MUCUS, SMOKE, MUCUS, 0.6),
    Reaction(MUCUS, SPORES, MUCUS, AIR, 0.2),
    Reaction(ACID, MUCUS, FUME, AIR, 0.01),
    # Glutblut (molten blood) sets fuel alight, chars flesh and cools in liquids into scab
    Reaction(MAGMA, TALLOW, MAGMA, FIRE, 0.2),
    Reaction(MAGMA, SINEW, MAGMA, FIRE, 0.05),
    Reaction(MAGMA, GROWTH, MAGMA, FIRE, 0.05),
    Reaction(MAGMA, SPORES, MAGMA, FIRE, 0.5),
    Reaction(MAGMA, FLESH, MAGMA, CRUST, 0.004),
    Reaction(MAGMA, BLOOD, CRUST, SMOKE, 0.3),
    Reaction(MAGMA, MUCUS, CRUST, SMOKE, 0.3),
    Reaction(MAGMA, PUS, CRUST, SMOKE, 0.3),
    Reaction(MAGMA, AIR, MAGMA, SMOKE, 0.0008),
    # Eiter (pus) festers: it slowly rots flesh into growth; acid burns it away
    Reaction(PUS, FLESH, PUS, GROWTH, 0.0015),
    Reaction(ACID, PUS, FUME, AIR, 0.05),
    # Nerve current runs along sinew as a one-way wave: the current moves on, the sinew it
    # leaves behind is spent for a moment and then heals (so currents never loop forever)
    Reaction(SPARK, SINEW, SPENT, SPARK, 1.0),
    Reaction(SPARK, SPORES, SPARK, FIRE, 0.5),
    Reaction(SPARK, TALLOW, SPARK, FIRE, 0.2),
    Reaction(SPENT, SINEW, SINEW, SINEW, 0.008),
    Reaction(SPENT, SPENT, SINEW, SPENT, 0.004),
    Reaction(SPENT, AIR, SINEW, AIR, 0.004),
    Reaction(SPENT, FLESH, SINEW, FLESH, 0.004),
    # Spores infect what they land on
    Reaction(SPORES, FLESH, AIR, GROWTH, 0.05),
    Reaction(SPORES, SINEW, AIR, GROWTH, 0.05),
)


def to_fixed(chance: float) -> int:
    """Convert a probability to the core's 16-bit fixed point (``p * 65536``)."""
    return max(0, min(65535, round(chance * 65536)))


def build_tables(
    reactions: tuple[Reaction, ...] = REACTIONS,
) -> tuple[list[int], list[int], list[int]]:
    """Flatten the rules into three ``n * n`` tables indexed ``actor * n + neighbour``."""
    n = MATERIAL_COUNT
    actor_into = [0] * (n * n)
    neighbour_into = [0] * (n * n)
    chance = [0] * (n * n)
    for rule in reactions:
        if rule.actor == AIR:
            raise ValueError("air cannot be the actor of a reaction")
        if not 0.0 < rule.chance <= 1.0:
            raise ValueError(f"invalid chance {rule.chance} in {rule}")
        index = rule.actor * n + rule.neighbour
        if chance[index]:
            raise ValueError(f"duplicate reaction for {rule.actor} + {rule.neighbour}")
        actor_into[index] = rule.actor_into
        neighbour_into[index] = rule.neighbour_into
        chance[index] = max(1, to_fixed(rule.chance))
    return actor_into, neighbour_into, chance
