"""Generator for the Sporenklub universe (Card D05).

Regions (vertical bands):
  - lautsprechertuerme (top band): tall speaker towers made of pilzhut (>= 5%).
  - tanzflaeche (middle band): open dance floor cavern (air >= 30%) with leuchtsporen (>= 0.3%).
  - hinterzimmer (bottom band): dense, cramped backrooms rich in pilzfleisch (>= 15%).

Props:
  - sporen_knolle, pilz_laterne
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

    id_air = mat.AIR
    id_pilzfleisch = mat.id_of("pilzfleisch")
    id_pilzhut = mat.id_of("pilzhut")
    id_leuchtsporen = mat.id_of("leuchtsporen")

    world.reset(id_pilzfleisch)

    bands = common.region_bands(world.width, world.height, "vertical")
    b_towers, b_dance, b_back = bands[0], bands[1], bands[2]

    # --- 1. Lautsprechertürme (Top band: y 0..y1) ---
    # Towers / pillars made of pilzhut, with open air vertical shafts.
    # Air shafts
    num_shafts = max(2, world.width // 70)
    col_w = world.width // num_shafts
    for i in range(num_shafts):
        cx = i * col_w + col_w // 2
        # Carve vertical open shaft
        world.fill_rect(
            max(0, cx - 12), b_towers[1] + 10, min(world.width, cx + 12), b_towers[3], id_air
        )
        # Line with pilzhut towers
        world.fill_rect(max(0, cx - 20), b_towers[1] + 15, max(0, cx - 12), b_towers[3], id_pilzhut)
        world.fill_rect(
            min(world.width, cx + 12),
            b_towers[1] + 15,
            min(world.width, cx + 20),
            b_towers[3],
            id_pilzhut,
        )
        # Add horizontal cross-beams of pilzhut
        world.fill_rect(
            max(0, cx - 25),
            b_towers[1] + 30,
            min(world.width, cx + 25),
            b_towers[1] + 36,
            id_pilzhut,
        )

    # Sprinkle extra pilzhut blocks to guarantee >= 5% share in lautsprechertuerme
    tower_area = (b_towers[2] - b_towers[0]) * (b_towers[3] - b_towers[1])
    target_pilzhut = int(tower_area * 0.12)
    placed_pilzhut = 0
    while placed_pilzhut < target_pilzhut:
        px = rng.randint(b_towers[0], b_towers[2] - 8)
        py = rng.randint(b_towers[1], b_towers[3] - 8)
        world.fill_rect(px, py, px + 8, py + 8, id_pilzhut)
        placed_pilzhut += 64

    # Connect shafts horizontally
    mid_y = (b_towers[1] + b_towers[3]) // 2
    world.fill_rect(10, mid_y - 4, world.width - 10, mid_y + 4, id_air)

    # --- 2. Tanzfläche (Middle band: y1..y2) ---
    # Open cavern: air >= 30%, leuchtsporen >= 0.3%
    dance_pad = 12
    world.fill_rect(
        b_dance[0] + dance_pad,
        b_dance[1] + 6,
        b_dance[2] - dance_pad,
        b_dance[3] - 6,
        id_air,
    )
    # DJ podium / stage platforms in the dance floor
    stage_w = min(80, (b_dance[2] - b_dance[0]) // 3)
    stage_cx = (b_dance[0] + b_dance[2]) // 2
    world.fill_rect(
        stage_cx - stage_w // 2,
        b_dance[3] - 16,
        stage_cx + stage_w // 2,
        b_dance[3] - 6,
        id_pilzhut,
    )

    # Leuchtsporen clouds near ceiling / stage
    spore_area = (b_dance[2] - b_dance[0]) * (b_dance[3] - b_dance[1])
    target_spores = int(spore_area * 0.02)
    placed_spores = 0
    while placed_spores < target_spores:
        sx = rng.randint(b_dance[0] + 15, b_dance[2] - 25)
        sy = rng.randint(b_dance[1] + 8, b_dance[1] + 30)
        world.fill_rect(sx, sy, sx + 10, sy + 6, id_leuchtsporen)
        placed_spores += 60

    # --- 3. Hinterzimmer (Bottom band: y2..y3) ---
    # Dense pilzfleisch corridors / backrooms (pilzfleisch >= 15%)
    # Carve maze of rooms/hallways
    back_rooms: list[common.Rect] = []
    num_back_rooms = max(3, world.width // 60)
    step_x = (b_back[2] - b_back[0]) // num_back_rooms
    for i in range(num_back_rooms):
        rx0 = b_back[0] + i * step_x + 6
        rx1 = rx0 + step_x - 12
        ry0 = rng.randint(b_back[1] + 8, b_back[1] + 20)
        ry1 = min(b_back[3] - 8, ry0 + rng.randint(20, 35))
        r = (rx0, ry0, rx1, ry1)
        world.fill_rect(rx0, ry0, rx1, ry1, id_air)
        back_rooms.append(r)

    for r1, r2 in itertools.pairwise(back_rooms):
        common.carve_tunnel(world, _centre(r1), _centre(r2), 7)

    # --- 4. Main Rooms & Navigation ---
    rooms = [
        common._place_room(world, b_towers, (40, 25), rng),
        (stage_cx - stage_w // 2, b_dance[1] + 10, stage_cx + stage_w // 2, b_dance[3] - 18),
        back_rooms[-1] if back_rooms else common._place_room(world, b_back, (40, 25), rng),
    ]

    # Carve vertical connecting tunnels between the 3 layers
    towers_exit = _centre(rooms[0])
    dance_mid = _centre(rooms[1])
    back_mid = _centre(rooms[2])
    common.carve_tunnel(world, towers_exit, dance_mid, 8)
    common.carve_tunnel(world, dance_mid, back_mid, 8)

    # Arenas: mid_boss in dance floor, boss in backrooms
    mid, boss = common.place_boss_arenas(world, b_dance, b_back, rng)
    common.carve_tunnel(world, dance_mid, _centre(mid), 8)
    common.carve_tunnel(world, back_mid, _centre(boss), 8)

    # Nook & Shrine
    nook = common.place_trader_nook(world, b_towers, rng)
    shrine = common.place_challenge_shrine(world, b_dance, rng)

    # --- 1. Lautsprechertürme (Top band: y 0..y1) ---
    # Towers / pillars made of pilzhut, with open air vertical shafts.
    # Air shafts
    num_shafts = max(2, world.width // 70)
    col_w = world.width // num_shafts
    for i in range(num_shafts):
        cx = i * col_w + col_w // 2
        # Carve vertical open shaft
        world.fill_rect(max(0, cx - 12), b_towers[1] + 10, min(world.width, cx + 12), b_towers[3], id_air)
        # Line with pilzhut towers
        world.fill_rect(max(0, cx - 20), b_towers[1] + 15, max(0, cx - 12), b_towers[3], id_pilzhut)
        world.fill_rect(min(world.width, cx + 12), b_towers[1] + 15, min(world.width, cx + 20), b_towers[3], id_pilzhut)
        # Add horizontal cross-beams of pilzhut
        world.fill_rect(max(0, cx - 25), b_towers[1] + 30, min(world.width, cx + 25), b_towers[1] + 36, id_pilzhut)

    # Sprinkle extra pilzhut blocks to guarantee >= 5% share in lautsprechertuerme
    tower_area = (b_towers[2] - b_towers[0]) * (b_towers[3] - b_towers[1])
    target_pilzhut = int(tower_area * 0.12)
    placed_pilzhut = 0
    while placed_pilzhut < target_pilzhut:
        px = rng.randint(b_towers[0], b_towers[2] - 8)
        py = rng.randint(b_towers[1], b_towers[3] - 8)
        world.fill_rect(px, py, px + 8, py + 8, id_pilzhut)
        placed_pilzhut += 64

    # Connect shafts horizontally
    mid_y = (b_towers[1] + b_towers[3]) // 2
    world.fill_rect(10, mid_y - 4, world.width - 10, mid_y + 4, id_air)

    # --- 2. Tanzfläche (Middle band: y1..y2) ---
    # Open cavern: air >= 30%, leuchtsporen >= 0.3%
    dance_pad = 12
    world.fill_rect(
        b_dance[0] + dance_pad,
        b_dance[1] + 6,
        b_dance[2] - dance_pad,
        b_dance[3] - 6,
        id_air,
    )
    # DJ podium / stage platforms in the dance floor
    stage_w = min(80, (b_dance[2] - b_dance[0]) // 3)
    stage_cx = (b_dance[0] + b_dance[2]) // 2
    world.fill_rect(stage_cx - stage_w // 2, b_dance[3] - 16, stage_cx + stage_w // 2, b_dance[3] - 6, id_pilzhut)

    # Leuchtsporen clouds near ceiling / stage
    spore_area = (b_dance[2] - b_dance[0]) * (b_dance[3] - b_dance[1])
    target_spores = int(spore_area * 0.02)
    placed_spores = 0
    while placed_spores < target_spores:
        sx = rng.randint(b_dance[0] + 15, b_dance[2] - 25)
        sy = rng.randint(b_dance[1] + 8, b_dance[1] + 30)
        world.fill_rect(sx, sy, sx + 10, sy + 6, id_leuchtsporen)
        placed_spores += 60

    # --- 3. Hinterzimmer (Bottom band: y2..y3) ---
    # Dense pilzfleisch corridors / backrooms (pilzfleisch >= 15%)
    # Carve maze of rooms/hallways
    back_rooms: list[common.Rect] = []
    num_back_rooms = max(3, world.width // 60)
    step_x = (b_back[2] - b_back[0]) // num_back_rooms
    for i in range(num_back_rooms):
        rx0 = b_back[0] + i * step_x + 6
        rx1 = rx0 + step_x - 12
        ry0 = rng.randint(b_back[1] + 8, b_back[1] + 20)
        ry1 = min(b_back[3] - 8, ry0 + rng.randint(20, 35))
        r = (rx0, ry0, rx1, ry1)
        world.fill_rect(rx0, ry0, rx1, ry1, id_air)
        back_rooms.append(r)

    for r1, r2 in itertools.pairwise(back_rooms):
        common.carve_tunnel(world, _centre(r1), _centre(r2), 7)

    # --- 4. Main Rooms & Navigation ---
    rooms = [
        common._place_room(world, b_towers, (40, 25), rng),
        (stage_cx - stage_w // 2, b_dance[1] + 10, stage_cx + stage_w // 2, b_dance[3] - 18),
        back_rooms[-1] if back_rooms else common._place_room(world, b_back, (40, 25), rng),
    ]

    # Carve vertical connecting tunnels between the 3 layers
    towers_exit = _centre(rooms[0])
    dance_mid = _centre(rooms[1])
    back_mid = _centre(rooms[2])
    common.carve_tunnel(world, towers_exit, dance_mid, 8)
    common.carve_tunnel(world, dance_mid, back_mid, 8)

    # Arenas: mid_boss in dance floor, boss in backrooms
    mid, boss = common.place_boss_arenas(world, b_dance, b_back, rng)
    common.carve_tunnel(world, dance_mid, _centre(mid), 8)
    common.carve_tunnel(world, back_mid, _centre(boss), 8)

    # Nook & Shrine
    nook = common.place_trader_nook(world, b_towers, rng)
    shrine = common.place_challenge_shrine(world, b_dance, rng)

    keys = [r.key for r in universe.regions][:3]
    spawn = (rooms[0][0] + 6, rooms[0][3] - 6)
    exit_point = _centre(rooms[2])

    world.fill_disc(spawn[0], spawn[1], 6, id_air)
    world.fill_disc(exit_point[0], exit_point[1], 6, id_air)

    # --- 5. Props: sporen_knolle, pilz_laterne ---
    props: list[tuple[str, int, int]] = []
    # Place sporen_knolle in hinterzimmer and tanzflaeche
    props.append(
        (
            "sporen_knolle",
            max(0, min(world.width - 1, back_mid[0])),
            max(0, min(world.height - 1, back_mid[1])),
        )
    )
    props.append(
        (
            "sporen_knolle",
            max(0, min(world.width - 1, back_rooms[0][0] + 5)),
            max(0, min(world.height - 1, back_rooms[0][1] + 5)),
        )
    )
    # Place pilz_laterne in tanzflaeche and lautsprechertuerme
    props.append(
        (
            "pilz_laterne",
            max(0, min(world.width - 1, stage_cx - 20)),
            max(0, min(world.height - 1, b_dance[3] - 20)),
        )
    )
    props.append(
        (
            "pilz_laterne",
            max(0, min(world.width - 1, stage_cx + 20)),
            max(0, min(world.height - 1, b_dance[3] - 20)),
        )
    )
    props.append(
        (
            "pilz_laterne",
            max(0, min(world.width - 1, towers_exit[0])),
            max(0, min(world.height - 1, towers_exit[1])),
        )
    )

    # --- 6. Quest Giver ---
    # Must stand in air with solid floor beneath (within 1..12 px)
    qx = max(5, min(world.width - 6, rooms[0][0] + 12))
    qy = rooms[0][3] - 10
    world.fill_disc(qx, qy, 4, id_air)
    world.fill_rect(qx - 5, qy + 4, qx + 6, qy + 8, id_pilzhut)
    quest_giver = (qx, qy)

    # --- 5. Props: sporen_knolle, pilz_laterne ---
    props: list[tuple[str, int, int]] = []
    # Place sporen_knolle in hinterzimmer and tanzflaeche
    props.append(("sporen_knolle", max(0, min(world.width - 1, back_mid[0])), max(0, min(world.height - 1, back_mid[1]))))
    props.append(("sporen_knolle", max(0, min(world.width - 1, back_rooms[0][0] + 5)), max(0, min(world.height - 1, back_rooms[0][1] + 5))))
    # Place pilz_laterne in tanzflaeche and lautsprechertuerme
    props.append(("pilz_laterne", max(0, min(world.width - 1, stage_cx - 20)), max(0, min(world.height - 1, b_dance[3] - 20))))
    props.append(("pilz_laterne", max(0, min(world.width - 1, stage_cx + 20)), max(0, min(world.height - 1, b_dance[3] - 20))))
    props.append(("pilz_laterne", max(0, min(world.width - 1, towers_exit[0])), max(0, min(world.height - 1, towers_exit[1]))))

    # --- 6. Quest Giver ---
    # Must stand in air with solid floor beneath (within 1..12 px)
    qx = max(5, min(world.width - 6, rooms[0][0] + 12))
    qy = rooms[0][3] - 10
    world.fill_disc(qx, qy, 4, id_air)
    world.fill_rect(qx - 5, qy + 4, qx + 6, qy + 8, id_pilzhut)
    quest_giver = (qx, qy)

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
        destructible_props=props,
        quest_giver=quest_giver,
    )
