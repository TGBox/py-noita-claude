"""Universum suppenmeer: Das Endlose Suppenmeer (Phase J05)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "suppenmeer",
    "Das Endlose Suppenmeer",
    "Ein siedender Ozean aus Gemüsesuppe. Buchstabennudeln formen verzweifelte Worte.",
    rule="rule_flooded_soup",
    shape="hoch",
    ambient=0.35,
    material_set="suppenmeer",
    regions=(
        Region("bruehe_spiegel", "Brühe-Spiegel"),
        Region("sellerie_riff", "Sellerie-Riff"),
        Region("tiefer_topf", "Tiefer Topf"),
    ),
    natives=("suppenlaus", "buchstaben_krake", "karotten_aal", "markbaellchen_krabbe"),
    event="wallendes_kochen",
    samples=("probe_nudel_a", "probe_nelke"),
    sample_key="probe_nudel_a",
    mid_boss="chefkoch_ghul",
    boss="kellen_leviathan",
    arena_de="Emaille-Kasserolle mit seitlichen Hitzeventilen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"breath": 16.0, "boil_updraft": False},
    2: {"breath": 12.0, "boil_updraft": False},
    3: {"breath": 9.0, "boil_updraft": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Das Endlose Suppenmeer level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="nudel_teig",
        trim_key="rock",
        liquid_key="bouillon",
        powder_key="sand",
        props=("suppen_schuessel", "nudel_holz"),
    )
