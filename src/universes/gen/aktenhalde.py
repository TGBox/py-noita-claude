"""Generator for the Aktenhalde universe (Card D02).

Regions: registratur, grossraumbuero, archivkeller.
Topology: horizontal.
Base material set: aktenhalde.
Content:
  - Registratur (left): Dense shelving units with "aktendeckel" shelves and "papier" between them.
  - Grossraumbuero (middle): Open office floor ("air" >= 25%), desks as platforms ("aktendeckel").
  - Archivkeller (right): Dark basement with ink lakes ("tinte").
  - Firebreaks (Brandabschnitte): Grid of non-flammable walls ("rock", "aktendeckel", "tintenpapier")
    ensuring no connected paper cluster is larger than 640x360.
  - Destructible props: "akten_regal", "amt_uhr".
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


def generate_aktenhalde(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("aktenhalde")
    id_papier = mat.id_of("papier")
    id_aktendeckel = mat.id_of("aktendeckel")
    id_tinte = mat.id_of("tinte")
    id_tintenpapier = mat.id_of("tintenpapier")
    id_rock = mat.id_of("rock")
    id_air = mat.AIR

    # 1. Base world: fill with bedrock/rock boundary, primary solid is rock / aktendeckel grid
    world.reset(id_rock)

    bands = common.region_bands(world.width, world.height, "horizontal")
    reg_band, buero_band, archiv_band = bands[0], bands[1], bands[2]

    # --- Registratur (left band): dense paper shelves ---
    # Draw shelves: horizontal rows of aktendeckel with papier between them
    rx0, ry0, rx1, ry1 = reg_band
    world.fill_rect(rx0, ry0, rx1, ry1, id_papier)
    # Firebreaks & shelves inside Registratur:
    shelf_step = max(8, (ry1 - ry0) // 10)
    for y in range(ry0 + shelf_step, ry1, shelf_step):
        world.fill_rect(rx0, y - 1, rx1, y + 1, id_aktendeckel)
    # Vertical dividers for firebreaks
    col_step = max(40, (rx1 - rx0) // 3)
    for x in range(rx0 + col_step, rx1, col_step):
        world.fill_rect(x - 2, ry0, x + 2, ry1, id_aktendeckel)

    # --- Grossraumbuero (middle band): open airy space with desk platforms ---
    bx0, by0, bx1, by1 = buero_band
    world.fill_rect(bx0, by0, bx1, by1, id_air)
    # Boundary pillars/separators
    world.fill_rect(bx0, by0, bx0 + 3, by1, id_aktendeckel)
    world.fill_rect(bx1 - 3, by0, bx1, by1, id_aktendeckel)
    # Place office floor platforms / desks
    desk_h = max(20, (by1 - by0) // 5)
    for y in range(by0 + desk_h, by1 - 10, desk_h):
        # Desks as platforms
        for dx in range(bx0 + 10, bx1 - 25, 30):
            world.fill_rect(dx, y, dx + 20, y + 2, id_aktendeckel)
            # small stacks of paper on desks
            world.fill_rect(dx + 3, y - 2, dx + 8, y, id_papier)
    # Bottom floor for office
    world.fill_rect(bx0, by1 - 6, bx1, by1, id_aktendeckel)

    # --- Archivkeller (right band): dark basement with ink lakes ---
    ax0, ay0, ax1, ay1 = archiv_band
    world.fill_rect(ax0, ay0, ax1, ay1, id_papier)
    # Dividers / stone vaults in archive
    for y in range(ay0 + 30, ay1, 35):
        world.fill_rect(ax0, y - 1, ax1, y + 2, id_aktendeckel)
    # Create ink basins / lakes
    lake_w = max(30, (ax1 - ax0) * 3 // 4)
    lake_x0 = ax0 + (ax1 - ax0 - lake_w) // 2
    lake_x1 = lake_x0 + lake_w
    lake_y0 = ay0 + (ay1 - ay0) // 2
    lake_y1 = min(ay1 - 4, lake_y0 + (ay1 - ay0) // 3)
    # Basin shell from rock
    world.fill_rect(lake_x0 - 2, lake_y0 - 2, lake_x1 + 2, lake_y1 + 2, id_rock)
    world.fill_rect(lake_x0, lake_y0, lake_x1, lake_y1, id_air)
    common.fill_basin(world, lake_x0, lake_y0, lake_x1, lake_y1, id_tinte)

    # --- Strict Firebreaks (Brandabschnitte <= 640x360 across full world) ---
    # Place non-flammable firebreak grid across the entire world:
    # Vertical firebreaks every <= 400 px
    for fx in range(350, world.width, 350):
        world.fill_rect(fx - 2, 0, fx + 2, world.height, id_aktendeckel)
    # Horizontal firebreaks every <= 250 px
    for fy in range(220, world.height, 220):
        world.fill_rect(0, fy - 2, world.width, fy + 2, id_aktendeckel)
    # Region boundary dividers (non-flammable)
    for band in bands:
        bx = band[2]
        if bx < world.width:
            world.fill_rect(bx - 2, 0, bx + 2, world.height, id_tintenpapier)

    # --- Rooms and arenas ---
    rooms = [common._place_room(world, band, (45, 36), rng) for band in bands]
    for first, second in itertools.pairwise(rooms):
        common.carve_tunnel(world, _centre(first), _centre(second), 8)

    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 8)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 8)

    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)

    # --- Props ("akten_regal", "amt_uhr") ---
    props = common.scatter_props(world, reg_band, ("akten_regal",), 4, rng)
    props.extend(common.scatter_props(world, buero_band, ("amt_uhr", "akten_regal"), 6, rng))
    has_regal = any(p[0] == "akten_regal" for p in props)
    has_uhr = any(p[0] == "amt_uhr" for p in props)
    if not has_regal or not has_uhr:
        rx = (rooms[1][0] + rooms[1][2]) // 2
        ry = rooms[1][3] - 1
        world.set_cell(rx, ry, id_air)
        world.set_cell(rx, ry + 1, id_aktendeckel)
        world.set_cell(rx + 4, ry, id_air)
        world.set_cell(rx + 4, ry + 1, id_aktendeckel)
        if not has_regal:
            props.append(("akten_regal", rx, ry))
        if not has_uhr:
            props.append(("amt_uhr", rx + 4, ry))

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
        qx, qy = rooms[0][0] + 8, rooms[0][3] - 4
        world.fill_rect(qx - 2, qy + 1, qx + 3, qy + 3, id_aktendeckel)
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
