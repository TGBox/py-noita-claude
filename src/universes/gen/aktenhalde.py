"""Generator for the Aktenhalde universe (Card D02).

Regions: registratur, grossraumbuero, archivkeller.
Topology: breit (horizontal_3).
Base material set: aktenhalde (papier, aktendeckel, tinte, etc.).
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


def generate_aktenhalde(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("aktenhalde")
    base_solid = mat.id_of("papier")
    world.reset(base_solid)

    bands = common.region_bands(world.width, world.height, "horizontal_3")
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

    # Ensure spawn and exit points are in air
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
        regions=list(zip(keys, bands, strict=True)),
    )

