"""Universum unsterblichkeits_resort: Das Unsterblichkeits-Resort (Phase S04)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "unsterblichkeits_resort",
    "Das Unsterblichkeits-Resort (Keine Konsequenzen)",
    "Luxus-Pools voller Schirmchendrinks — wo jeder Schaden erst nach dem Urlaub auf die Rechnung kommt.",
    rule="rule_all_inclusive",
    shape="breit",
    ambient=0.86,
    material_set="unsterblichkeits_resort",
    regions=(
        Region("poolbar", "All-Inclusive Poolbar"),
        Region("sauna_fluegel", "Sauna-Flügel"),
        Region("vip_terrasse", "VIP-Sonnendeck"),
    ),
    natives=("bademeister_zyklop", "liegestuhl_mimic", "gelangweilter_gott", "buffet_schleim"),
    event="happy_hour",
    samples=("probe_cocktail", "probe_marmor"),
    sample_key="probe_cocktail",
    mid_boss="club_direktor",
    boss="ewiger_gaeste_koenig",
    arena_de="Marmorner Innenpool mit schwimmender Bühne",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"damping": 0.85, "grace_sec": 2.0},
    2: {"damping": 0.75, "grace_sec": 3.0},
    3: {"damping": 0.65, "grace_sec": 4.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="marmor_pool",
        trim_key="sonnencreme_sand",
        liquid_key="cocktail_elixir",
        powder_key="sonnencreme_sand",
        props=("sonnenschirm", "liegestuhl"),
    )
