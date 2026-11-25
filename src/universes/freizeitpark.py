"""Universum freizeitpark: Freizeitpark Endzeit (Phase J06)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "freizeitpark",
    "Freizeitpark Endzeit",
    "Seit Jahrhunderten geschlossen. Die Maskottchen haben Hunger und die Achterbahn fährt noch immer.",
    rule="rule_momentum",
    shape="breit",
    ambient=0.55,
    material_set="freizeitpark",
    regions=(
        Region("geisterbahn", "Geisterbahn"),
        Region("kirmesplatz", "Kirmesplatz"),
        Region("achterbahn_looping", "Achterbahn-Looping"),
    ),
    natives=("geisterbahn_clown", "leer_kostuem", "popcorn_drohne", "autoscooter_kaefer"),
    event="freie_fahrt",
    samples=("probe_kirmes_chip", "probe_apfel"),
    sample_key="probe_kirmes_chip",
    mid_boss="los_verkaeufer",
    boss="achterbahn_drache",
    arena_de="Looping-Geflecht mit schwingenden Gondeln als Deckung",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"bounces": 2, "rail_boost": 1.4},
    2: {"bounces": 3, "rail_boost": 1.6},
    3: {"bounces": 4, "rail_boost": 1.8},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Freizeitpark Endzeit level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="rost_schiene",
        trim_key="spiegel_glas",
        liquid_key="water",
        powder_key="zuckerwatte_rot",
        props=("karussell_pferd", "popcorn_maschine"),
    )
