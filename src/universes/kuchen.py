"""Universum kuchen: Die Kuchenkruste (Phase J02)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "kuchen",
    "Die Kuchenkruste",
    "Gebacken vor einer Million Jahren. Oben knusprige Baisers, unten kochendes Karamell.",
    rule="rule_hot",
    shape="quadrat",
    ambient=0.65,
    material_set="kuchen",
    regions=(
        Region("glasur_kamm", "Glasur-Kamm"),
        Region("biskuit_hoehlen", "Biskuit-Höhlen"),
        Region("karamell_tiefe", "Karamell-Tiefe"),
    ),
    natives=("zuckerspinne", "kerzenkobold", "marzipanschwein", "baiser_geist"),
    event="karamell_ausbruch",
    samples=("probe_zucker", "probe_marzipan"),
    sample_key="probe_zucker",
    mid_boss="marzipan_ritter",
    boss="hochzeitstorte",
    arena_de="Runde Tortenplatte mit herabfallenden Baiser-Brocken",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"ignite_chance": 0.01, "sugar_blast": 1.0},
    2: {"ignite_chance": 0.03, "sugar_blast": 1.5},
    3: {"ignite_chance": 0.05, "sugar_blast": 2.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Die Kuchenkruste level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="biskuit",
        trim_key="zuckerglasur",
        liquid_key="karamell_kuchen",
        powder_key="puderzucker",
        props=("riesen_kerze", "keks_rad"),
    )
