"""Universum klonenberg_welt: Klonenberg (Alles ist der gleiche Typ) (Phase R03)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "klonenberg_welt",
    "Klonenberg (Alles ist der gleiche Typ)",
    "Sämtliche Bewohner, Steine und Ansagen gehören demselben leicht genervten Mann im Bademantel.",
    rule="rule_klon_synchro",
    shape="raster",
    ambient=0.62,
    material_set="klonenberg_welt",
    regions=(
        Region("vorort", "Klonenberg-Vorort"),
        Region("badezimmer_trakt", "Spiegel-Korridor"),
        Region("stammkneipe", "Stammtisch der Identitäten"),
    ),
    natives=("ur_klonenberg", "buero_klonenberg", "bademantel_klonenberg", "keller_klonenberg"),
    event="gruppen_telefonat",
    samples=("probe_bartstoppel", "probe_klon_dna"),
    sample_key="probe_bartstoppel",
    mid_boss="rat_der_klonenbergs",
    boss="alpha_klonenberg",
    arena_de="Spiegelsaal voller synchron nickender Klonenbergs",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"sync_window": 0.20, "clone_wave": 2},
    2: {"sync_window": 0.35, "clone_wave": 3},
    3: {"sync_window": 0.50, "clone_wave": 4},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="klon_fleisch",
        trim_key="bartstoppel_sand",
        liquid_key="spiegel_lauge",
        powder_key="bartstoppel_sand",
        props=("bademantel_statue", "telefonzelle"),
    )
