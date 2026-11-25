"""Universum kollektiv_buerokratie: Kollektiv-Schwarmbürokratie (Phase S03)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "kollektiv_buerokratie",
    "Kollektiv-Schwarmbürokratie",
    "Ein sechseckiger Bienenstock aus Wabenstahl, in dem tausend Drohnen denselben Umlaufbeschluss abnicken.",
    rule="rule_schwarmbewusstsein",
    shape="waben",
    ambient=0.60,
    material_set="kollektiv_buerokratie",
    regions=(
        Region("vorzimmer_wabe", "Empfangswabe"),
        Region("lochkarten_stock", "Lochkarten-Stock"),
        Region("koeniginnen_dezernat", "Dezernat der Schwarmzentrale"),
    ),
    natives=("schwarm_tipper", "stempel_wespe", "rundschreiben_larve", "protokoll_drohne"),
    event="rundschreiben_alarm",
    samples=("probe_lochkarte", "probe_wabe"),
    sample_key="probe_lochkarte",
    mid_boss="ober_koordinator",
    boss="schwarm_zentrale",
    arena_de="Sechseckige Wabenhalle unter surrenden Protokolldrohnen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"alert_radius": 80.0, "swarm_sync": False},
    2: {"alert_radius": 120.0, "swarm_sync": True},
    3: {"alert_radius": 180.0, "swarm_sync": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="waben_stahl",
        trim_key="lochkarten_staub",
        liquid_key="tinten_nectar",
        powder_key="lochkarten_staub",
        props=("waben_regal", "stempel_turm"),
    )
