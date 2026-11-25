"""Universum spule: Die Summende Spule (Phase J03)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "spule",
    "Die Summende Spule",
    "Ein Alptraum aus blanken Kupferdrähten und permanenten Hochspannungs-Entladungen.",
    rule="rule_electric",
    shape="hoch",
    ambient=0.38,
    material_set="spule",
    regions=(
        Region("spulenwald", "Spulenwald"),
        Region("kondensatordeck", "Kondensatordeck"),
        Region("plasmakern", "Plasmakern"),
    ),
    natives=("funkenhornisse", "spulenkrabbe", "kupferschlange", "kondensator_geist"),
    event="kurzschluss",
    samples=("probe_spule", "probe_kondensator"),
    sample_key="probe_spule",
    mid_boss="spulenmeister",
    boss="transformator",
    arena_de="Faraday-Käfig mit beweglichen Elektroden",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"conduct_bonus": 1.5, "air_arc": False},
    2: {"conduct_bonus": 2.0, "air_arc": False},
    3: {"conduct_bonus": 2.5, "air_arc": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Die Summende Spule level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="kupferdraht",
        trim_key="isolator",
        liquid_key="elektrolyt",
        powder_key="sand",
        props=("trafo_kasten", "blitzableiter"),
    )
