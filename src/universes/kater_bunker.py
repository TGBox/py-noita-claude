"""Universum kater_bunker: Der Kater-nach-Weltuntergang-Bunker (Phase S06)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "kater_bunker",
    "Der Kater-nach-Weltuntergang-Bunker",
    "Sonntagmorgen nach der Apokalypse: graues Blei, Konterbrause und dröhnende Basstreffer.",
    rule="rule_brummschaedel",
    shape="bunker",
    ambient=0.38,
    material_set="kater_bunker",
    regions=(
        Region("schleuse", "Kater-Schleuse"),
        Region("vorratsraum", "Leergut-Gewölbe"),
        Region("sofa_festung", "Verdunkeltes Wohnzimmer"),
    ),
    natives=("aspirin_golem", "nebel_kater", "muellsack_geist", "kaffeefilter_kraehe"),
    event="stille_stunde",
    samples=("probe_konterbrause", "probe_blei"),
    sample_key="probe_konterbrause",
    mid_boss="lichtempfindlicher_riese",
    boss="sonntags_kopfschmerz",
    arena_de="Schallisolierter Bleibunker mit sanft brummenden Leuchtstoffröhren",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"thump_scale": 1.1, "glare_dim": 0.9},
    2: {"thump_scale": 1.25, "glare_dim": 0.8},
    3: {"thump_scale": 1.4, "glare_dim": 0.7},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="bunker_blei",
        trim_key="kopfschmerz_asche",
        liquid_key="konter_brause",
        powder_key="kopfschmerz_asche",
        props=("vorhang_tuch", "kaffeemaschine_leer"),
    )
