"""Universum anatomie_park: Anatomie-Park im Riesen (Phase R01)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "anatomie_park",
    "Anatomie-Park im Riesen",
    "Ein vergessener Vergnügungspark im Inneren eines schlafenden Kolosses — zwischen Lebergewebe und Magensäure.",
    rule="rule_peristaltik",
    shape="schlauch",
    ambient=0.45,
    material_set="anatomie_park",
    regions=(
        Region("speiseroehre", "Speiseröhren-Rutsche"),
        Region("magenbucht", "Magensäure-Bucht"),
        Region("herzkammer", "Reaktor-Herzkammer"),
    ),
    natives=("zell_waechter", "leukozyten_ritter", "enzym_geist", "nerven_blitz"),
    event="verdauungsschub",
    samples=("probe_magensaeure", "probe_lebergewebe"),
    sample_key="probe_magensaeure",
    mid_boss="herzklappen_golem",
    boss="immunsystem_titan",
    arena_de="Pulsierende Herzkammer mit periodischen Säureventilen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"pulse_force": 18.0, "acid_tide": False},
    2: {"pulse_force": 28.0, "acid_tide": True},
    3: {"pulse_force": 40.0, "acid_tide": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="lebergewebe",
        trim_key="knochen_bruecke",
        liquid_key="magensaeure",
        powder_key="adrenalin_dampf",
        props=("monorail_wagen", "galle_pumpe"),
    )
