"""Phase 3 satire universe registry, shared level delegation, samples & factions (Phases R-S)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass

from src.universes import (
    anatomie_park,
    antrags_labyrinth,
    kater_bunker,
    klo_paradies,
    klonenberg_welt,
    kollektiv_buerokratie,
    krawatten_planet,
    matroschka_simulation,
    pastell_hoelle,
    schroedinger_kammer,
    talent_kosmos,
    unsterblichkeits_resort,
)
from src.universes.catalog_expansion import (
    EXPANSION_ACTIVE,
    EXPANSION_BY_KEY,
    generate_expansion_level,
)
from src.universes.model import Universe
from src.world import World
from src.worldgen import Level

PHASE3_ACTIVE: bool = True


@dataclass(frozen=True)
class Phase3Sample:
    """Universe sample specification introduced by Phase 3 universes (R01-S06)."""

    key: str
    name_de: str
    universe_key: str


PHASE3_SAMPLES: dict[str, Phase3Sample] = {
    "probe_magensaeure": Phase3Sample("probe_magensaeure", "Magensäure-Ampulle", "anatomie_park"),
    "probe_lebergewebe": Phase3Sample("probe_lebergewebe", "Lebergewebe-Schnitt", "anatomie_park"),
    "probe_glitzer": Phase3Sample("probe_glitzer", "Pastell-Glitzer", "pastell_hoelle"),
    "probe_erdbeernektar": Phase3Sample("probe_erdbeernektar", "Erdbeernektar-Probe", "pastell_hoelle"),
    "probe_bartstoppel": Phase3Sample("probe_bartstoppel", "Klonenberg-Stoppel", "klonenberg_welt"),
    "probe_klon_dna": Phase3Sample("probe_klon_dna", "Einheits-DNA-Tupfer", "klonenberg_welt"),
    "probe_applaus": Phase3Sample("probe_applaus", "Konserven-Applaus", "talent_kosmos"),
    "probe_spotlight": Phase3Sample("probe_spotlight", "Spotlight-Splitter", "talent_kosmos"),
    "probe_formular": Phase3Sample("probe_formular", "Vergessenes Formular", "antrags_labyrinth"),
    "probe_tacker": Phase3Sample("probe_tacker", "Tacker-Relikt", "antrags_labyrinth"),
    "probe_krawatte": Phase3Sample("probe_krawatte", "Gestresste Krawatte", "krawatten_planet"),
    "probe_espresso": Phase3Sample("probe_espresso", "Espresso-Satz", "krawatten_planet"),
    "probe_porzellan": Phase3Sample("probe_porzellan", "Porzellan-Scherbe", "klo_paradies"),
    "probe_heilquelle": Phase3Sample("probe_heilquelle", "Quellwasser-Fläschchen", "klo_paradies"),
    "probe_voxel": Phase3Sample("probe_voxel", "Roh-Voxel", "matroschka_simulation"),
    "probe_pixel": Phase3Sample("probe_pixel", "Subpixel-Korn", "matroschka_simulation"),
    "probe_lochkarte": Phase3Sample("probe_lochkarte", "Gestanzte Lochkarte", "kollektiv_buerokratie"),
    "probe_wabe": Phase3Sample("probe_wabe", "Wabenstahl-Chip", "kollektiv_buerokratie"),
    "probe_cocktail": Phase3Sample("probe_cocktail", "Schirmchen-Tropfen", "unsterblichkeits_resort"),
    "probe_marmor": Phase3Sample("probe_marmor", "Poolmarmor-Eckchen", "unsterblichkeits_resort"),
    "probe_karton": Phase3Sample("probe_karton", "Ungeöffnete Lasche", "schroedinger_kammer"),
    "probe_quanten": Phase3Sample("probe_quanten", "Quantensuppen-Tropfen", "schroedinger_kammer"),
    "probe_konterbrause": Phase3Sample("probe_konterbrause", "Konterbrause-Rest", "kater_bunker"),
    "probe_blei": Phase3Sample("probe_blei", "Bunkerblei-Span", "kater_bunker"),
}


def generate_phase3_level(
    world: World,
    rng: random.Random,
    *,
    universe: Universe,
    wall_key: str,
    trim_key: str,
    liquid_key: str,
    powder_key: str,
    props: tuple[str, str],
) -> Level:
    """Shared generator for Phase R and Phase S universes via expansion terrain builder."""
    return generate_expansion_level(
        world,
        rng,
        universe=universe,
        wall_key=wall_key,
        trim_key=trim_key,
        liquid_key=liquid_key,
        powder_key=powder_key,
        props=props,
    )


PHASE3_R_UNIVERSES: tuple[Universe, ...] = (
    anatomie_park.UNIVERSE,
    pastell_hoelle.UNIVERSE,
    klonenberg_welt.UNIVERSE,
    talent_kosmos.UNIVERSE,
    antrags_labyrinth.UNIVERSE,
    krawatten_planet.UNIVERSE,
)

PHASE3_S_UNIVERSES: tuple[Universe, ...] = (
    klo_paradies.UNIVERSE,
    matroschka_simulation.UNIVERSE,
    kollektiv_buerokratie.UNIVERSE,
    unsterblichkeits_resort.UNIVERSE,
    schroedinger_kammer.UNIVERSE,
    kater_bunker.UNIVERSE,
)

PHASE3_UNIVERSES: tuple[Universe, ...] = PHASE3_R_UNIVERSES + PHASE3_S_UNIVERSES
PHASE3_BY_KEY: dict[str, Universe] = {u.key: u for u in PHASE3_UNIVERSES}

PHASE3_GENERATORS: dict[str, Callable[[World, random.Random, int], Level]] = {
    "anatomie_park": anatomie_park.generate,
    "pastell_hoelle": pastell_hoelle.generate,
    "klonenberg_welt": klonenberg_welt.generate,
    "talent_kosmos": talent_kosmos.generate,
    "antrags_labyrinth": antrags_labyrinth.generate,
    "krawatten_planet": krawatten_planet.generate,
    "klo_paradies": klo_paradies.generate,
    "matroschka_simulation": matroschka_simulation.generate,
    "kollektiv_buerokratie": kollektiv_buerokratie.generate,
    "unsterblichkeits_resort": unsterblichkeits_resort.generate,
    "schroedinger_kammer": schroedinger_kammer.generate,
    "kater_bunker": kater_bunker.generate,
}

PHASE3_FACTIONS: dict[str, str] = {u.key: u.key for u in PHASE3_UNIVERSES}


def all_catalog_universes(
    *,
    include_expansion: bool = EXPANSION_ACTIVE,
    include_phase3: bool = PHASE3_ACTIVE,
) -> dict[str, Universe]:
    """Return full universe catalog across MVP, Phase 2, and Phase 3 layers."""
    from src.universes.catalog import BY_KEY

    merged = dict(BY_KEY)
    if include_expansion:
        merged.update(EXPANSION_BY_KEY)
    if include_phase3:
        merged.update(PHASE3_BY_KEY)
    return merged
