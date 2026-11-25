"""Universum uhrwerkwueste: Die Uhrwerkwüste (Phase J04)."""

from __future__ import annotations

import random

from src.universes.model import Region, Universe
from src.world import World
from src.worldgen import Level

UNIVERSE = Universe(
    "uhrwerkwueste",
    "Die Uhrwerkwüste",
    "Ein Meer aus tickendem Zahnradsand. Zeit ist hier eine zähe Flüssigkeit.",
    rule="rule_slowtime",
    shape="breit",
    ambient=0.50,
    material_set="uhrwerkwueste",
    regions=(
        Region("zahnrad_duenen", "Zahnrad-Dünen"),
        Region("gruft_der_sekunden", "Gruft der Sekunden"),
        Region("chrono_oase", "Chrono-Oase"),
    ),
    natives=("zecken_uhr", "pendel_schreiter", "chrono_waechter", "sanduhr_skarabaeus"),
    event="zeitsprung",
    samples=("probe_unruh", "probe_chrono"),
    sample_key="probe_unruh",
    mid_boss="unruh_vogel",
    boss="ewiges_pendel",
    arena_de="Großes Ziffernblatt mit rotierenden Messing-Zeigern als Plattformen",
    ready=True,
)

RANK_SCALING: dict[int, dict[str, object]] = {
    1: {"min_scale": 0.80, "freeze_projectiles": False},
    2: {"min_scale": 0.60, "freeze_projectiles": False},
    3: {"min_scale": 0.40, "freeze_projectiles": True},
}


def generate(world: World, rng: random.Random, rank: int = 1) -> Level:
    """Generate Die Uhrwerkwüste level for the given rank (1..3)."""
    from src.universes.catalog_expansion import generate_expansion_level

    _ = rank
    return generate_expansion_level(
        world,
        rng,
        universe=UNIVERSE,
        wall_key="messing_zahnrad",
        trim_key="rock",
        liquid_key="fluessig_zeit",
        powder_key="chrono_sand",
        props=("stand_uhr", "feder_werk"),
    )
