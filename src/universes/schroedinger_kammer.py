"""Universum schroedinger_kammer: Schrödingers Ungeöffnete Schachtel (Phase S05)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "schroedinger_kammer",
    "Schrödingers Ungeöffnete Schachtel",
    "Solange niemand nachsieht, sind Wände gleichzeitig stabil, flüssig und beleidigt.",
    rule="rule_superposition",
    shape="kammer",
    ambient=0.52,
    material_set="schroedinger_kammer",
    regions=(
        Region("papp_wand", "Pappkarton-Rand"),
        Region("wellen_senke", "Interferenz-Becken"),
        Region("beobachter_kammer", "Unbeobachtete Mitte"),
    ),
    natives=("halb_katze", "beobachter_auge", "wellen_fuchs", "paradox_wurm"),
    event="messproblem",
    samples=("probe_karton", "probe_quanten"),
    sample_key="probe_karton",
    mid_boss="dekohaerenz_waechter",
    boss="katzen_paradoxon",
    arena_de="Zwielichtiger Kartonwürfel voller violetter Quantensuppe",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"dodge_chance": 0.10, "collapse_period": 4.0},
    2: {"dodge_chance": 0.18, "collapse_period": 3.0},
    3: {"dodge_chance": 0.25, "collapse_period": 2.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="karton_wand",
        trim_key="wellen_staub",
        liquid_key="quanten_supp",
        powder_key="wellen_staub",
        props=("verschluss_flasche", "karton_klappe"),
    )
