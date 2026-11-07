"""Generator for the Sporenklub universe (Card D05).

Regions: lautsprechertuerme, tanzflaeche, hinterzimmer.
Topology: quadrat (top_split).
Base material set: sporenklub (pilzfleisch, pilzhut, leuchtsporen, etc.).
"""

from __future__ import annotations

import itertools
import random
from typing import TYPE_CHECKING

from src import materials as mat
from src.universes.gen import common
from src.worldgen import Level

if TYPE_CHECKING:
    from src.universes.model import Universe
    from src.world import World


def _centre(rect: common.Rect) -> tuple[int, int]:
    return ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)


def generate_sporenklub(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("sporenklub")
    base_solid = mat.id_of("pilzfleisch")
    world.reset(base_solid)

    bands = common.region_bands(world.width, world.height, "top_split")
    rooms = [common._place_room(world, band, (50, 40), rng) for band in bands]
    for first, second in itertools.pairwise(rooms):
        common.carve_tunnel(world, _centre(first), _centre(second), 9)

    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 9)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 9)

    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)

    keys = [r.key for r in universe.regions][:3]
    spawn = (rooms[0][0] + 4, rooms[0][3] - 15)
    exit_point = _centre(rooms[2])

    world.fill_disc(spawn[0], spawn[1], 6, mat.AIR)
    world.fill_disc(exit_point[0], exit_point[1], 6, mat.AIR)

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
        regions=list(zip(keys, bands, strict=False)),
    )

