"""Contract V9: Universe generator registry and dispatcher (Card A25, D01..D09)."""

from __future__ import annotations

import itertools
import random
from collections.abc import Callable
from typing import TYPE_CHECKING

from src import materials as mat
from src.universes.gen import common
from src.universes.gen.aktenhalde import generate_aktenhalde
from src.worldgen import Level

if TYPE_CHECKING:
    from src.universes.model import Universe
    from src.world import World

GENERATORS: dict[str, Callable[[World, Universe, int, int], Level]] = {
    "aktenhalde": generate_aktenhalde,
}

SHAPE_TOPOLOGY = {
    "breit": "horizontal",
    "hoch": "vertical",
    "quadrat": "top_split",
    "inseln": "islands",
}


def _centre(rect: common.Rect) -> tuple[int, int]:
    return ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)


def _fallback(world: World, universe: Universe, depth: int, seed: int) -> Level:
    """A plain level for universes without their own generator (until Phase D)."""
    rng = random.Random(seed * 1009 + depth)
    world.reset(mat.FLESH)
    topology = SHAPE_TOPOLOGY.get(universe.shape, "vertical")
    bands = common.region_bands(world.width, world.height, topology)
    rooms = [common._place_room(world, band, (60, 40), rng) for band in bands]
    for first, second in itertools.pairwise(rooms):
        common.carve_tunnel(world, _centre(first), _centre(second), 11)
    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 11)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 11)
    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)
    keys = [region.key for region in universe.regions][:3]
    keys += [f"region_{i}" for i in range(len(keys), 3)]
    spawn = (rooms[0][0] + 4, rooms[0][3] - 20)
    exit_point = _centre(rooms[2])
    return Level(
        spawn,
        exit_point,
        _centre(mid),
        exit_point=exit_point,
        universe_key=universe.key,
        mid_boss_arena=mid,
        boss_arena=boss,
        trader_nook=nook,
        challenge_shrine=shrine,
        regions=list(zip(keys, bands, strict=True)),
    )


def generate_universe(world: World, universe: Universe, depth: int, seed: int) -> Level:
    """Generate a universe level using the registered generator for universe.key."""
    generator = GENERATORS.get(universe.key, _fallback)
    return generator(world, universe, depth, seed)
