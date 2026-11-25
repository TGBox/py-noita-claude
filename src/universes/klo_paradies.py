"""Universum klo_paradies: Das Verbotene Klo-Paradies (Phase S01)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "klo_paradies",
    "Das Verbotene Klo-Paradies",
    "Makelloses Glanzporzellan und ruhiges Heilquell-Wasser, das Schild und Flux regeneriert — aber niemals HP.",
    rule="rule_zen_keramik",
    shape="kammer",
    ambient=0.84,
    material_set="klo_paradies",
    regions=(
        Region("vorraum", "Marmor-Waschbecken"),
        Region("seifen_grotte", "Seifenschaum-Grotte"),
        Region("thronsaal", "Heiliger Keramikthron"),
    ),
    natives=("rohr_geist", "klopapier_mumie", "puempel_ritter", "duftstein_elementar"),
    event="wasserrohr_wunder",
    samples=("probe_porzellan", "probe_heilquelle"),
    sample_key="probe_porzellan",
    mid_boss="ober_klempner",
    boss="thron_waechter",
    arena_de="Lichtdurchflutete Keramik-Kathedrale mit goldener Spülkette",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"calm_radius": 32.0, "shield_regen": 5.0},
    2: {"calm_radius": 48.0, "shield_regen": 8.0},
    3: {"calm_radius": 64.0, "shield_regen": 12.0},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    from src.universes.catalog_phase3 import generate_phase3_level

    _ = rank
    return generate_phase3_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="porzellan_glanz",
        trim_key="bimsstein_mehl",
        liquid_key="heilquell_wasser",
        powder_key="bimsstein_mehl",
        props=("keramik_thron", "gold_spuelkasten"),
    )
