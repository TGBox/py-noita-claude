"""Generator for the Kruemelreich universe (Card D04).

Regions: fliesenwueste, unter_kuehlschrank, ameisenbau.
Topology: top_split.
Base material set: kruemelreich.
Content:
  - Fliesenwueste (top left): "fliese" with grouts, huge "kruemel", "zucker" crystals, pea ("rock" circle).
  - Unter_kuehlschrank (top right): Dark, "staubfluse" clusters.
  - Ameisenbau (bottom): Tunnels and chambers in "brosel" / "kruemel", queen chamber.
  - Destructible props: "ameisen_kokon".
  - Quest giver on solid ground.
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


def generate_kruemelreich(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("kruemelreich")
    id_fliese = mat.id_of("fliese")
    id_kruemel = mat.id_of("kruemel")
    id_brosel = mat.id_of("brosel")
    id_zucker = mat.id_of("zucker")
    id_staubfluse = mat.id_of("staubfluse")
    id_rock = mat.id_of("rock")
    id_air = mat.AIR

    # 1. Base world: fill with brosel/kruemel underground
    world.reset(id_kruemel)

    bands = common.region_bands(world.width, world.height, "top_split")
    fliesen_band, kuehl_band, ameisen_band = bands[0], bands[1], bands[2]

    # --- Fliesenwueste (band 0, top-left): fliese floor with grouts, kruemel, zucker, pea (rock circle) ---
    fx0, fy0, fx1, fy1 = fliesen_band
    # Carve mostly air cavern with tile patterns
    world.fill_rect(fx0, fy0, fx1, fy1, id_air)
    # Tile layers (fliese floor)
    tile_h = max(10, (fy1 - fy0) // 4)
    for y in range(fy0 + tile_h, fy1, tile_h):
        world.fill_rect(fx0, y, fx1, y + 3, id_fliese)
        # Grout gaps every 25 px
        for gx in range(fx0 + 20, fx1, 25):
            world.fill_rect(gx, y, gx + 2, y + 3, id_kruemel)
    # Huge kruemel blocks & zucker grains
    for _ in range(8):
        kx = rng.randint(fx0 + 8, fx1 - 15)
        ky = rng.randint(fy0 + 5, fy1 - 10)
        world.fill_disc(kx, ky, rng.randint(3, 6), id_kruemel)
    for _ in range(6):
        zx = rng.randint(fx0 + 8, fx1 - 15)
        zy = rng.randint(fy0 + 5, fy1 - 10)
        world.fill_disc(zx, zy, rng.randint(2, 4), id_zucker)
    # Giant pea (circle of rock)
    pea_x = (fx0 + fx1) // 2
    pea_y = (fy0 + fy1) // 2
    world.fill_disc(pea_x, pea_y, 7, id_rock)

    # --- Unter Kuehlschrank (band 1, top-right): dark, dusty, lots of staubfluse ---
    ux0, uy0, ux1, uy1 = kuehl_band
    world.fill_rect(ux0, uy0, ux1, uy1, id_kruemel)
    # Carve dusty cavities
    world.fill_rect(ux0 + 5, uy0 + 5, ux1 - 5, uy1 - 5, id_air)
    # Staubfluse clusters along floor and ceiling
    for _ in range(10):
        sx = rng.randint(ux0 + 6, ux1 - 6)
        sy = rng.randint(uy0 + 6, uy1 - 6)
        world.fill_disc(sx, sy, rng.randint(3, 7), id_staubfluse)

    # --- Ameisenbau (band 2, bottom): ant tunnels and chambers in brosel / kruemel ---
    ax0, ay0, ax1, ay1 = ameisen_band
    world.fill_rect(ax0, ay0, ax1, ay1, id_kruemel)
    # Mix in large patches of brosel
    for y in range(ay0, ay1, 2):
        for x in range(ax0, ax1, 2):
            if rng.random() < 0.45:
                world.fill_rect(x, y, min(ax1, x + 2), min(ay1, y + 2), id_brosel)

    # --- Rooms and arenas ---
    rooms = [common._place_room(world, band, (42, 32), rng) for band in bands]
    for first, second in itertools.pairwise(rooms):
        common.carve_tunnel(world, _centre(first), _centre(second), 7)

    # Queen's chamber in ameisenbau (extra spacious chamber)
    queen_cx = (ax0 + ax1) // 2
    queen_cy = ay0 + (ay1 - ay0) // 2
    world.fill_disc(queen_cx, queen_cy, 14, id_air)
    common.carve_tunnel(world, _centre(rooms[2]), (queen_cx, queen_cy), 6)

    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 7)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 7)

    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)

    # --- Props ("ameisen_kokon") ---
    props = common.scatter_props(world, ameisen_band, ("ameisen_kokon",), 6, rng)
    if not any(p[0] == "ameisen_kokon" for p in props):
        rx = (rooms[2][0] + rooms[2][2]) // 2
        ry = rooms[2][3] - 1
        world.set_cell(rx, ry, id_air)
        world.set_cell(rx, ry + 1, id_kruemel)
        props.append(("ameisen_kokon", rx, ry))

    # --- Quest Giver (V13b) ---
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
        world.fill_rect(qx - 2, qy + 1, qx + 3, qy + 3, id_fliese)
        world.fill_rect(qx - 2, qy - 4, qx + 3, qy + 1, id_air)
        quest_giver = (qx, qy)

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
    )
