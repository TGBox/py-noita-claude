"""Universum krawatten_planet: Planet der Gestressten Krawatten (Phase R06)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "krawatten_planet",
    "Planet der Gestressten Krawatten",
    "Alles rennt von Termin zu Termin durch Espressoschlamm und brennende PowerPoint-Folien.",
    rule="rule_deadline",
    shape="schacht",
    ambient=0.66,
    material_set="krawatten_planet",
    regions=(
        Region("pendler_rampe", "Pendler-Rolltreppe"),
        Region("konferenz_deck", "Konferenzraum Omega"),
        Region("chef_etage", "Vorstands-Penthouse"),
    ),
    natives=("quartals_drohne", "projektmanager_schleim", "powerpoint_geist", "pendler_kaefer"),
    event="meeting_marathons",
    samples=("probe_krawatte", "probe_espresso"),
    sample_key="probe_krawatte",
    mid_boss="senior_consultant",
    boss="vorstands_titan",
    arena_de="Gläserner Konferenzsaal über heißem Espressoschlamm",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"speed_bonus": 1.15, "deadline_sec": 45.0},
    2: {"speed_bonus": 1.25, "deadline_sec": 35.0},
    3: {"speed_bonus": 1.35, "deadline_sec": 25.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="akten_marmor",
        trim_key="krawatten_stoff",
        liquid_key="espresso_schlamm",
        powder_key="krawatten_stoff",
        props=("krawatten_statue", "beamer_altar"),
    )
