"""Expansion universe registry, shared level generator, factions & samples (Phase J)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass

from src import materials as mat
from src.materials import AIR
from src.player import PLAYER_HEIGHT
from src.universes import (
    freizeitpark,
    kuchen,
    schrott,
    spule,
    suppenmeer,
    uhrwerkwueste,
)
from src.universes.model import Universe
from src.world import BORDER, World
from src.worldgen import Level

EXPANSION_ACTIVE: bool = True


@dataclass(frozen=True)
class ExpansionSample:
    key: str
    name_de: str
    universe_key: str


EXPANSION_SAMPLES: dict[str, ExpansionSample] = {
    "probe_rost": ExpansionSample("probe_rost", "Rostprobe", "schrott"),
    "probe_magnetit": ExpansionSample("probe_magnetit", "Magnetit-Splitter", "schrott"),
    "probe_zucker": ExpansionSample("probe_zucker", "Zuckerkruste", "kuchen"),
    "probe_marzipan": ExpansionSample("probe_marzipan", "Marzipan-Nase", "kuchen"),
    "probe_spule": ExpansionSample("probe_spule", "Kupferspule", "spule"),
    "probe_kondensator": ExpansionSample("probe_kondensator", "Kondensator-Zelle", "spule"),
    "probe_unruh": ExpansionSample("probe_unruh", "Unruh-Feder", "uhrwerkwueste"),
    "probe_chrono": ExpansionSample("probe_chrono", "Chrono-Tropfen", "uhrwerkwueste"),
    "probe_nudel_a": ExpansionSample("probe_nudel_a", "Buchstabennudel A", "suppenmeer"),
    "probe_nelke": ExpansionSample("probe_nelke", "Getrocknete Nelke", "suppenmeer"),
    "probe_kirmes_chip": ExpansionSample("probe_kirmes_chip", "Kirmes-Chip", "freizeitpark"),
    "probe_apfel": ExpansionSample("probe_apfel", "Glasierter Apfel", "freizeitpark"),
}


def generate_expansion_level(
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
    """Shared deterministic generator for all 6 Phase J expansion universes."""
    mat.activate_key(universe.material_set)
    wall = mat.MAT_ID[wall_key]
    trim = mat.MAT_ID[trim_key]
    liquid = mat.MAT_ID[liquid_key]
    powder = mat.MAT_ID[powder_key]

    w, h = world.width, world.height
    world.reset(wall)
    spawn = (max(24, min(60, w // 4)), max(28, min(60, h // 3)))
    exit_pos = (max(spawn[0] + 24, w - 36), max(spawn[1] + 10, h - 32))

    # Carve spawn cavern, mid corridor, and arena cavern
    world.fill_disc(spawn[0], spawn[1], 18, AIR)
    mid_x = (spawn[0] + exit_pos[0]) // 2
    mid_y = (spawn[1] + exit_pos[1]) // 2
    world.fill_disc(mid_x, mid_y, 20, AIR)
    world.fill_disc(exit_pos[0], exit_pos[1], 22, AIR)

    # Clear walkable tunnel between spawn -> mid -> exit
    for (ax, ay), (bx, by) in ((spawn, (mid_x, mid_y)), ((mid_x, mid_y), exit_pos)):
        steps = max(1, max(abs(bx - ax), abs(by - ay)) // 4)
        for s in range(steps + 1):
            t = s / steps
            cx = int(ax + (bx - ax) * t)
            cy = int(ay + (by - ay) * t)
            world.fill_disc(cx, cy, 12, AIR)

    # Trim floor under spawn and seed local liquid/powder pockets safely away from spawn
    floor_y = min(h - BORDER - 4, spawn[1] + PLAYER_HEIGHT)
    world.fill_rect(spawn[0] - 12, floor_y, spawn[0] + 12, floor_y + 3, trim)
    lx = min(w - BORDER - 16, mid_x)
    ly = min(h - BORDER - 12, mid_y + 8)
    world.fill_rect(lx - 8, ly, lx + 8, ly + 4, liquid)
    px = max(BORDER + 10, rng.randint(mid_x - 16, mid_x + 16))
    py = max(BORDER + 8, mid_y - 10)
    world.fill_rect(px - 4, py, px + 4, py + 3, powder)

    band_w = max(1, w // max(1, len(universe.regions)))
    regions = [
        (r.key, (idx * band_w, 0, min(w, (idx + 1) * band_w), h))
        for idx, r in enumerate(universe.regions)
    ]
    destructible = [(props[0], mid_x - 8, mid_y), (props[1], mid_x + 8, mid_y)]
    world.wake_all()

    return Level(
        spawn=spawn,
        exit=exit_pos,
        exit_point=exit_pos,
        arena=exit_pos,
        universe_key=universe.key,
        mid_boss_arena=(max(0, mid_x - 24), max(0, mid_y - 24), min(w, mid_x + 24), min(h, mid_y + 24)),
        boss_arena=(max(0, exit_pos[0] - 28), max(0, exit_pos[1] - 28), min(w, exit_pos[0] + 28), min(h, exit_pos[1] + 28)),
        regions=regions,
        destructible_props=destructible,
    )


EXPANSION_UNIVERSES: tuple[Universe, ...] = (
    schrott.UNIVERSE,
    kuchen.UNIVERSE,
    spule.UNIVERSE,
    uhrwerkwueste.UNIVERSE,
    suppenmeer.UNIVERSE,
    freizeitpark.UNIVERSE,
)

EXPANSION_BY_KEY: dict[str, Universe] = {u.key: u for u in EXPANSION_UNIVERSES}

EXPANSION_GENERATORS: dict[str, Callable[[World, random.Random, int], Level]] = {
    "schrott": schrott.generate,
    "kuchen": kuchen.generate,
    "spule": spule.generate,
    "uhrwerkwueste": uhrwerkwueste.generate,
    "suppenmeer": suppenmeer.generate,
    "freizeitpark": freizeitpark.generate,
}

EXPANSION_FACTIONS: dict[str, str] = {u.key: u.key for u in EXPANSION_UNIVERSES}


def combined_universes(include_expansion: bool = EXPANSION_ACTIVE) -> dict[str, Universe]:
    """Return MVP universes optionally merged with the 6 Phase J expansion universes."""
    from src.universes.catalog import BY_KEY

    merged = dict(BY_KEY)
    if include_expansion:
        merged.update(EXPANSION_BY_KEY)
    return merged
