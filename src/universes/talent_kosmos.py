"""Universum talent_kosmos: Show-Me-What-You-Got Kosmos (Phase R04)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "talent_kosmos",
    "Show-Me-What-You-Got Kosmos",
    "Eine kosmische Castingshow, in der schlechte Manieren mit Plasmablitzen bewertet werden.",
    rule="rule_bewertung",
    shape="arena",
    ambient=0.72,
    material_set="talent_kosmos",
    regions=(
        Region("backstage", "Backstage-Dunst"),
        Region("hauptbuehne", "Laser-Showbühne"),
        Region("jury_loge", "Richter-Loge"),
    ),
    natives=("kopf_waechter", "takt_drohne", "buhruf_schatten", "mikrofon_krabbe"),
    event="talent_scouting",
    samples=("probe_applaus", "probe_spotlight"),
    sample_key="probe_applaus",
    mid_boss="jury_vorsitz",
    boss="himmel_regisseur",
    arena_de="Überdimensionierte Quiz- und Talentbühne unter Wander-Spotlights",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"period": 0.6, "bonus": 0.20},
    2: {"period": 0.5, "bonus": 0.30},
    3: {"period": 0.4, "bonus": 0.40},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="buehnen_stein",
        trim_key="applaus_gold",
        liquid_key="scheinwerfer_plasma",
        powder_key="applaus_gold",
        props=("scheinwerfer_turm", "buzzer_pult"),
    )
