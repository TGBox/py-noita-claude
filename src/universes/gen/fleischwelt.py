"""Generator for the Fleischwelt universe (Card D01).

Regions: schlund, magen, knochenmark.
Topology: vertical.
Base material set: fleischwelt.
Content:
  - Schlund: Teeth made of "enamel" along cave edges.
  - Magen: Acid basins ("acid") and tallow pools ("tallow").
  - Knochenmark: Dense "bone" with enamel veins.
  - Base body: "flesh" (>= 20% of the world).
  - Destructible props: "saeure_behaelter", "magen_zotte".
  - Secret: sealed bone chamber with memory shard (Level.secret).
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


def generate_fleischwelt(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("fleischwelt")
    id_flesh = mat.id_of("flesh")
    id_bone = mat.id_of("bone")
    id_enamel = mat.id_of("enamel")
    id_acid = mat.id_of("acid")
    id_tallow = mat.id_of("tallow")
    id_air = mat.AIR

    # 1. Base world: solid flesh
    world.reset(id_flesh)

    bands = common.region_bands(world.width, world.height, "vertical")
    schlund_band, magen_band, knochen_band = bands[0], bands[1], bands[2]

    # --- Knochenmark (bottom band): lots of bone, enamel veins ---
    # Fill background/structure of knochenmark with bone
    kx0, ky0, kx1, ky1 = knochen_band
    for y in range(ky0, ky1):
        for x in range(kx0, kx1):
            if rng.random() < 0.45:
                world.set_cell(x, y, id_bone)
    # Add enamel veins into bone
    for _ in range(8):
        vx = rng.randint(kx0 + 10, kx1 - 10)
        vy = rng.randint(ky0 + 5, ky1 - 5)
        for _step in range(15):
            world.fill_disc(vx, vy, 2, id_enamel)
            vx = max(kx0 + 2, min(kx1 - 2, vx + rng.randint(-2, 2)))
            vy = max(ky0 + 2, min(ky1 - 2, vy + rng.randint(-1, 2)))

    # 2. Carve main path / rooms
    rooms = [common._place_room(world, band, (50, 36), rng) for band in bands]
    for first, second in itertools.pairwise(rooms):
        common.carve_tunnel(world, _centre(first), _centre(second), 9)

    mid, boss = common.place_boss_arenas(world, bands[1], bands[2], rng)
    common.carve_tunnel(world, _centre(rooms[1]), _centre(mid), 9)
    common.carve_tunnel(world, _centre(rooms[2]), _centre(boss), 9)

    nook = common.place_trader_nook(world, bands[0], rng)
    shrine = common.place_challenge_shrine(world, bands[1], rng)

    # --- Schlund (top band): Teeth from enamel along cave boundaries ---
    sx0, sy0, sx1, sy1 = schlund_band
    # Carve a few organic side-caves in Schlund
    for _ in range(5):
        cx = rng.randint(sx0 + 20, sx1 - 20)
        cy = rng.randint(sy0 + 10, sy1 - 10)
        common.carve_tunnel(world, _centre(rooms[0]), (cx, cy), 7)
    # Grow tooth spikes (enamel) along floor/ceiling where air meets solid
    for y in range(sy0 + 2, sy1 - 2):
        for x in range(sx0 + 2, sx1 - 2):
            if world.get(x, y) == id_air:
                if world.get(x, y - 1) == id_flesh and rng.random() < 0.28:
                    world.set_cell(x, y, id_enamel)
                    world.set_cell(x, y + 1, id_enamel)
                elif world.get(x, y + 1) == id_flesh and rng.random() < 0.28:
                    world.set_cell(x, y, id_enamel)
                    world.set_cell(x, y - 1, id_enamel)

    # --- Magen (middle band): Acid basins and tallow pools ---
    mx0, my0, mx1, my1 = magen_band
    # Carve a dedicated acid basin
    basin_w = min(60, (mx1 - mx0) // 3)
    basin_x0 = mx0 + 15
    basin_x1 = basin_x0 + basin_w
    basin_y0 = (my0 + my1) // 2
    basin_y1 = min(my1 - 4, basin_y0 + 22)
    # Line the basin with bone so acid doesn't immediately leak
    world.fill_rect(basin_x0 - 2, basin_y0 - 2, basin_x1 + 2, basin_y1 + 2, id_bone)
    world.fill_rect(basin_x0, basin_y0, basin_x1, basin_y1, id_air)
    # Fill lower part with acid
    common.fill_basin(world, basin_x0, basin_y0, basin_x1, basin_y1, id_acid)
    # Connect acid basin to the main magen room
    common.carve_tunnel(world, _centre(rooms[1]), ((basin_x0 + basin_x1) // 2, basin_y0), 5)

    # Place tallow deposits / pockets in Magen walls and floor
    for _ in range(6):
        tx = rng.randint(mx0 + 10, mx1 - 10)
        ty = rng.randint(my0 + 5, my1 - 5)
        world.fill_disc(tx, ty, rng.randint(3, 5), id_tallow)

    # --- Secret chamber (Erinnerungssplitter in bone) ---
    # Sealed chamber in bottom band
    sec_x = max(kx0 + 15, min(kx1 - 15, kx0 + (kx1 - kx0) // 4))
    sec_y = max(ky0 + 10, min(ky1 - 10, ky0 + (ky1 - ky0) // 2))
    # Fill surrounding with thick bone
    world.fill_rect(sec_x - 8, sec_y - 8, sec_x + 8, sec_y + 8, id_bone)
    # Small hollow center
    world.fill_rect(sec_x - 3, sec_y - 3, sec_x + 4, sec_y + 4, id_air)
    secret_point = (sec_x, sec_y)

    # --- Quest Giver (V13b) ---
    # Find a free air cell with solid floor right underneath in Schlund
    quest_giver = None
    for y in range(rooms[0][3] - 2, rooms[0][1], -1):
        for x in range(rooms[0][0] + 5, rooms[0][2] - 5):
            if world.get(x, y) == id_air and world.get(x, y + 1) != id_air:
                quest_giver = (x, y)
                break
        if quest_giver is not None:
            break
    if quest_giver is None:
        # Fallback: create a dedicated alcove for the quest giver
        qx, qy = rooms[0][0] + 8, rooms[0][3] - 5
        world.fill_rect(qx - 2, qy + 1, qx + 3, qy + 4, id_flesh)
        world.fill_rect(qx - 2, qy - 4, qx + 3, qy + 1, id_air)
        quest_giver = (qx, qy)

    # --- Props ---
    props = common.scatter_props(world, magen_band, ("saeure_behaelter", "magen_zotte"), 8, rng)
    # Ensure at least one of each required prop exists
    has_saeure = any(p[0] == "saeure_behaelter" for p in props)
    has_zotte = any(p[0] == "magen_zotte" for p in props)
    if not has_saeure or not has_zotte:
        # Place them guaranteed on floor of rooms[1]
        rx = (rooms[1][0] + rooms[1][2]) // 2
        ry = rooms[1][3] - 1
        world.set_cell(rx, ry, id_air)
        world.set_cell(rx, ry + 1, id_flesh)
        world.set_cell(rx + 4, ry, id_air)
        world.set_cell(rx + 4, ry + 1, id_flesh)
        if not has_saeure:
            props.append(("saeure_behaelter", rx, ry))
        if not has_zotte:
            props.append(("magen_zotte", rx + 4, ry))

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
        secret=secret_point,
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
