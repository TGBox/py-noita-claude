"""Universum antrags_labyrinth: Die Unbeantworteten Anträge (Phase R05)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "antrags_labyrinth",
    "Die Unbeantworteten Anträge",
    "Verlorene Durchschläge, kalter Filterkaffee und endlose Korridore voller wartender Eingänge.",
    rule="rule_buerokratie",
    shape="labyrinth",
    ambient=0.58,
    material_set="antrags_labyrinth",
    regions=(
        Region("poststelle", "Verirrte Poststelle"),
        Region("stempel_gang", "Korridor der Fristen"),
        Region("archiv_keller", "Abgelehntes Endlager"),
    ),
    natives=("sachbearbeiter_golem", "locher_assassine", "ordner_spinne", "fax_wichtel"),
    event="mahnungswelle",
    samples=("probe_formular", "probe_tacker"),
    sample_key="probe_formular",
    mid_boss="abteilungsleiter",
    boss="ober_buerokrat",
    arena_de="Quadratischer Stempel-Saal mit Aktentürmen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"delay_mult": 1.15, "stamp_rate": 0.5},
    2: {"delay_mult": 1.30, "stamp_rate": 0.8},
    3: {"delay_mult": 1.45, "stamp_rate": 1.1},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="formular_beton",
        trim_key="tacker_schrott",
        liquid_key="kaffee_alt",
        powder_key="tacker_schrott",
        props=("stempel_presse", "fax_schrein"),
    )
