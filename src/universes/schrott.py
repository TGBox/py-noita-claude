"""Universum schrott: Der Große Schrott (Phase J01)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "schrott",
    "Der Große Schrott",
    "Ein endloser Friedhof interdimensionaler Maschinen. Alles rostet, knistert und zieht magnetisch an.",
    rule="rule_magnet",
    shape="breit",
    ambient=0.42,
    material_set="schrott",
    regions=(
        Region("schrotthalde", "Schrotthalde"),
        Region("schmelze", "Schmelze"),
        Region("kernwerk", "Kernwerk"),
    ),
    natives=("rostkaefer", "schweissimp", "magnetwurm", "schrottgolem"),
    event="magnetsturm",
    samples=("probe_rost", "probe_magnetit"),
    sample_key="probe_rost",
    mid_boss="gabelstapler_krabbe",
    boss="schrottpresse",
    arena_de="Rechteckige Stahlhalle mit zwei beweglichen Pressblöcken",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"magnet_radius": 15.0, "pull_weapons": False},
    2: {"magnet_radius": 30.0, "pull_weapons": False},
    3: {"magnet_radius": 45.0, "pull_weapons": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Der Große Schrott level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="altmetall",
        trim_key="magnetit",
        liquid_key="fluessigeisen",
        powder_key="roststaub",
        props=("magnet_kran", "batterie_saeule"),
    )
