"""Universum pastell_hoelle: Pastell-Hölle (Niedlichkeitsoverdose) (Phase R02)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "pastell_hoelle",
    "Pastell-Hölle (Niedlichkeitsoverdose)",
    "Blendendes Rosa, Plüschwände und klebriger Erdbeernektar, der Schilde und Tempo verleiht — nie Heilung.",
    rule="rule_ueberzuckerung",
    shape="breit",
    ambient=0.88,
    material_set="pastell_hoelle",
    regions=(
        Region("zuckerwiese", "Watte-Boulevard"),
        Region("glitzerschlucht", "Glitzer-Schlucht"),
        Region("plueschzitadelle", "Plüsch-Thronsaal"),
    ),
    natives=("zucker_fee", "knuddel_monster", "buntstift_geist", "schleifen_spinne"),
    event="konfetti_hagel",
    samples=("probe_glitzer", "probe_erdbeernektar"),
    sample_key="probe_glitzer",
    mid_boss="marzipan_engel",
    boss="pluesch_diktator",
    arena_de="Bonbonfarbener Festsaal mit federnden Plüschbanden",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"bounce_bonus": 0.15, "sugar_shield": 12.0},
    2: {"bounce_bonus": 0.25, "sugar_shield": 18.0},
    3: {"bounce_bonus": 0.35, "sugar_shield": 25.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="pluesch_wand",
        trim_key="glitzer_sand",
        liquid_key="erdbeernektar",
        powder_key="glitzer_sand",
        props=("riesen_schleife", "pluesch_thron"),
    )
