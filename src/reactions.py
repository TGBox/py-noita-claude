"""Data-driven reaction table: what happens when two materials touch.

Every tick, each cell of an *actor* material looks at its four neighbours. If a rule
exists for (actor, neighbour), it fires with the given chance and both cells turn
into their results. Burning is handled separately through ``Material.flammability``
so that every flammable material burns without needing its own rule.

Rules are written with material keys (``RULES``); ``REACTIONS`` holds the id-based
rules of the active material set. Adding an interaction means adding one line to ``RULES``.
"""

from __future__ import annotations

from dataclasses import dataclass

from src import materials as mat


@dataclass(frozen=True)
class Reaction:
    """``actor`` next to ``neighbour`` turns into ``actor_into`` / ``neighbour_into``."""

    actor: int | str  # keys in RULES, ids in REACTIONS
    neighbour: int | str
    actor_into: int | str
    neighbour_into: int | str
    chance: float  # per tick and per touching neighbour


RULES: tuple[Reaction, ...] = (
    # Fire
    Reaction("fire", "blood", "smoke", "crust", 0.5),  # blood douses fire and cooks into scab
    Reaction("fire", "flesh", "fire", "crust", 0.02),  # flesh chars instead of burning away
    # Blood soaks bone dust into scab. (It no longer clots in open air: falling drops
    # used to freeze into floating specks and pool surfaces into lids that plugged tunnels.)
    Reaction("blood", "bone_dust", "blood", "crust", 0.002),
    # Acid dissolves organic matter into fumes (and is used up doing so)
    Reaction("acid", "flesh", "fume", "air", 0.03),
    Reaction("acid", "sinew", "fume", "air", 0.03),
    Reaction("acid", "crust", "fume", "air", 0.03),
    Reaction("acid", "growth", "fume", "air", 0.05),
    Reaction("acid", "bone_dust", "fume", "air", 0.02),
    Reaction("acid", "bone", "fume", "air", 0.004),
    # Growth creeps through flesh, feeds on blood and releases spores
    Reaction("growth", "flesh", "growth", "growth", 0.003),
    Reaction("growth", "blood", "growth", "growth", 0.01),
    Reaction("growth", "air", "growth", "spores", 0.0005),
    # Mucus smothers fire, binds spores and is slowly eaten by acid
    Reaction("fire", "mucus", "smoke", "mucus", 0.6),
    Reaction("mucus", "spores", "mucus", "air", 0.2),
    Reaction("acid", "mucus", "fume", "air", 0.01),
    # Glutblut (molten blood) sets fuel alight, chars flesh and cools in liquids into scab
    Reaction("magma", "tallow", "magma", "fire", 0.2),
    Reaction("magma", "sinew", "magma", "fire", 0.05),
    Reaction("magma", "growth", "magma", "fire", 0.05),
    Reaction("magma", "spores", "magma", "fire", 0.5),
    Reaction("magma", "flesh", "magma", "crust", 0.004),
    Reaction("magma", "blood", "crust", "smoke", 0.3),
    Reaction("magma", "mucus", "crust", "smoke", 0.3),
    Reaction("magma", "pus", "crust", "smoke", 0.3),
    Reaction("magma", "air", "magma", "smoke", 0.0008),
    # Eiter (pus) festers: it slowly rots flesh into growth; acid burns it away
    Reaction("pus", "flesh", "pus", "growth", 0.0015),
    Reaction("acid", "pus", "fume", "air", 0.05),
    # Nerve current runs along sinew as a one-way wave: the current moves on, the sinew it
    # leaves behind is spent for a moment and then heals (so currents never loop forever)
    Reaction("spark", "sinew", "spent", "spark", 1.0),
    Reaction("spark", "spores", "spark", "fire", 0.5),
    Reaction("spark", "tallow", "spark", "fire", 0.2),
    Reaction("spent", "sinew", "sinew", "sinew", 0.008),
    Reaction("spent", "spent", "sinew", "spent", 0.004),
    Reaction("spent", "air", "sinew", "air", 0.004),
    Reaction("spent", "flesh", "sinew", "flesh", 0.004),
    # Spores infect what they land on
    Reaction("spores", "flesh", "air", "growth", 0.05),
    Reaction("spores", "sinew", "air", "growth", 0.05),    # --- base materials (every universe) ---
    Reaction("fire", "water", "steam", "water", 0.6),  # water douses fire into steam
    Reaction("fire", "fluxschnaps", "fire", "steam", 0.05),
    # --- Aktenhalde ---
    Reaction("fire", "papier", "fire", "asche", 0.04),  # paper burns down to ash
    Reaction("fire", "tinte", "smoke", "tinte", 0.5),  # ink stops a blaze
    Reaction("fire", "stempelfarbe", "smoke", "stempelfarbe", 0.5),
    Reaction("fire", "lack", "fire", "siegellack", 0.03),  # fire melts sealing wax
    Reaction("tinte", "papier", "tinte", "tintenpapier", 0.02),  # soaked paper won't burn
    Reaction("siegellack", "air", "lack", "air", 0.002),  # wax sets in the air ...
    Reaction("siegellack", "lack", "lack", "lack", 0.004),  # ... and from the crust inwards
)


def to_fixed(chance: float) -> int:
    """Convert a probability to the core's 16-bit fixed point (``p * 65536``)."""
    return max(0, min(65535, round(chance * 65536)))


def _resolve(rules: tuple[Reaction, ...]) -> list[Reaction]:
    """Key-based rules -> id-based rules for the active set.

    A rule applies when actor and neighbour are both in the set; its results may use
    stand-ins (aliases). Rules whose results have no stand-in are dropped.
    """
    resolved: list[Reaction] = []
    for rule in rules:
        if not (mat.has(rule.actor) and mat.has(rule.neighbour)):
            continue
        a_into, n_into = mat.resolve(rule.actor_into), mat.resolve(rule.neighbour_into)
        if a_into is None or n_into is None:
            continue
        resolved.append(
            Reaction(mat.id_of(rule.actor), mat.id_of(rule.neighbour), a_into, n_into, rule.chance)
        )
    return resolved


# Id-based rules of the active material set (rewritten on every activation).
REACTIONS: list[Reaction] = []


def _refresh() -> None:
    extra = tuple(mat.ACTIVE.reactions) if mat.ACTIVE else ()
    REACTIONS[:] = _resolve(RULES + extra)


mat.subscribe(_refresh)


def build_tables(
    reactions: tuple[Reaction, ...] | list[Reaction] | None = None,
) -> tuple[list[int], list[int], list[int]]:
    """Flatten id-based rules into three ``n * n`` tables indexed ``actor * n + neighbour``."""
    if reactions is None:
        reactions = REACTIONS
    n = mat.MATERIAL_COUNT
    actor_into = [0] * (n * n)
    neighbour_into = [0] * (n * n)
    chance = [0] * (n * n)
    for rule in reactions:
        if rule.actor == mat.AIR:
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
