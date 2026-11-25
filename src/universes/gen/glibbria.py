"""Generator for the Glibbria universe (Card D03).

Regions: gelee_huegel, kaugummi_hoehlen, sirupkueste.
Topology: islands.
Base material set: glibbria.
Content:
  - Floating islands made of "glibber" and "glibber_rot" with "zuckerguss" platforms.
  - Kaugummi caves with "kaugummi" puddles / viscous pockets.
  - Bottom syrup sea: bottom 10% of world >= 30% "brausesirup".
  - Bridges made of "zuckerguss" connecting islands.
  - Destructible props: "glibber_ballon".
  - Quest giver on solid ground and quest target on opposite coast of syrup lake.
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


def generate_glibbria(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("glibbria")
    id_glibber = mat.id_of("glibber")
    id_glibber_rot = mat.id_of("glibber_rot")
    id_kaugummi = mat.id_of("kaugummi")
    id_zuckerguss = mat.id_of("zuckerguss")
    id_brausesirup = mat.id_of("brausesirup")
    id_air = mat.AIR

    # 1. Base world: air with open space between floating islands
    world.reset(id_air)

    bands = common.region_bands(world.width, world.height, "islands")
    gelee_band, kaugummi_band, sirup_band = bands[0], bands[1], bands[2]

    # --- Syrup Sea (bottom 10% of world >= 30% brausesirup) ---
    sea_y0 = world.height * 9 // 10
    world.fill_rect(0, sea_y0, world.width, world.height, id_brausesirup)

    # --- Gelee-Huegel (band 0): floating islands of glibber / glibber_rot with zuckerguss platforms ---
    gx0, gy0, gx1, gy1 = gelee_band
    # Carve solid floating islands within the band
    world.fill_rect(gx0, gy0, gx1, gy1, id_glibber)
    # Scatter patches of glibber_rot
    for _ in range(8):
        ix = rng.randint(gx0 + 5, gx1 - 5)
        iy = rng.randint(gy0 + 5, gy1 - 5)
        world.fill_disc(ix, iy, rng.randint(4, 8), id_glibber_rot)
    # Zuckerguss platforms / crusts
    for py in range(gy0 + 8, gy1, max(8, (gy1 - gy0) // 5)):
        for px in range(gx0 + 4, gx1 - 10, 15):
            world.fill_rect(px, py, px + 10, py + 2, id_zuckerguss)

    # --- Kaugummi-Hoehlen (band 1): caves with sticky kaugummi puddles ---
    kx0, ky0, kx1, ky1 = kaugummi_band
    world.fill_rect(kx0, ky0, kx1, ky1, id_glibber)
    # Pockets and pools of kaugummi
    for _ in range(6):
        kx = rng.randint(kx0 + 6, kx1 - 6)
        ky = rng.randint(ky0 + 6, ky1 - 6)
        world.fill_disc(kx, ky, rng.randint(3, 6), id_kaugummi)

    # --- Sirupkueste (band 2): coastline above syrup sea ---
    sx0, sy0, sx1, sy1 = sirup_band
    world.fill_rect(sx0, sy0, sx1, sy1, id_glibber)
    # Coastline syrup pools
    for _ in range(5):
        cx = rng.randint(sx0 + 8, sx1 - 8)
        cy = rng.randint(sy0 + (sy1 - sy0) // 3, sy1 - 4)
        world.fill_disc(cx, cy, rng.randint(4, 9), id_brausesirup)

    # --- Carve rooms & chambers in islands ---
    rooms = [common._place_room(world, band, (45, 34), rng) for band in bands]

    # Connect islands with Zuckerguss bridges and tunnels
    for first, second in itertools.pairwise(rooms):
        c1, c2 = _centre(first), _centre(second)
        common.carve_tunnel(world, c1, c2, 7)
        # Add Zuckerguss bridge footing along the tunnel
        steps = 10
        for s in range(steps):
            bx = int(c1[0] + (c2[0] - c1[0]) * (s / steps))
            by = int(c1[1] + (c2[1] - c1[1]) * (s / steps)) + 7
            if 0 <= bx < world.width and 0 <= by < world.height:
                world.fill_rect(bx - 2, by, bx + 2, min(world.height, by + 2), id_zuckerguss)

    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 7)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 7)

    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)

    # Reinforce bottom 10% syrup sea after carving/clearing
    world.fill_rect(0, sea_y0, world.width, world.height, id_brausesirup)

    # --- Props ("glibber_ballon") ---
    props = common.scatter_props(world, gelee_band, ("glibber_ballon",), 5, rng)
    props.extend(common.scatter_props(world, kaugummi_band, ("glibber_ballon",), 5, rng))
    if not any(p[0] == "glibber_ballon" for p in props):
        rx = (rooms[0][0] + rooms[0][2]) // 2
        ry = rooms[0][3] - 1
        world.set_cell(rx, ry, id_air)
        world.set_cell(rx, ry + 1, id_glibber)
        props.append(("glibber_ballon", rx, ry))

    # --- Quest Giver (V13b) & Quest Target (Cow escort across syrup lake) ---
    quest_giver = None
    for y in range(rooms[0][3] - 1, rooms[0][1], -1):
        for x in range(rooms[0][0] + 5, rooms[0][2] - 5):
            if world.get(x, y) == id_air and world.get(x, y + 1) != id_air:
                quest_giver = (x, y)
                break
        if quest_giver is not None:
            break
    if quest_giver is None:
        qx, qy = rooms[0][0] + 6, rooms[0][3] - 4
        world.fill_rect(qx - 2, qy + 1, qx + 3, qy + 3, id_glibber)
        world.fill_rect(qx - 2, qy - 4, qx + 3, qy + 1, id_air)
        quest_giver = (qx, qy)

    # Quest target: across the syrup coast in sirupkueste
    tx = min(world.width - 20, max(sx0 + 10, sx1 - 25))
    ty = max(sy0 + 10, min(world.height - 15, sea_y0 - 8))
    world.fill_rect(tx - 3, ty + 1, tx + 4, ty + 4, id_zuckerguss)
    world.fill_rect(tx - 3, ty - 6, tx + 4, ty + 1, id_air)
    quest_target = (tx, ty)

    # --- Spawn and Exit Points ---
    spawn = (rooms[0][0] + 4, rooms[0][3] - 15)
    exit_point = _centre(rooms[2])

    world.fill_disc(spawn[0], spawn[1], 6, id_air)
    world.fill_disc(exit_point[0], exit_point[1], 6, id_air)

    keys = [r.key for r in universe.regions][:3]

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
        destructible_props=props,
        quest_giver=quest_giver,
        quest_target=quest_target,
    )
