"""Generator for the Versunkene Abtei universe (Card D06).

Regions (vertical bands):
  - glockenturm (top band): dry bell tower (water <= 1%), glockenbronze (>= 0.3%).
  - kirchenschiff (middle band): flooded nave (water >= 20%), mauerwerk (>= 5%), buntglas (>= 0.3%).
  - krypta (bottom band): flooded crypt with algen (>= 0.3%).

World:
  - kerzenwachs >= 0.05% (0.0005 across the whole world).

Props:
  - abtei_glocke
"""

from __future__ import annotations

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


def generate_abtei(world: World, universe: Universe, depth: int, seed: int) -> Level:
    rng = random.Random(seed * 1009 + depth)
    mat.activate_key("abtei")

    id_air = mat.AIR
    id_water = mat.id_of("water")
    id_mauerwerk = mat.id_of("mauerwerk")
    id_buntglas = mat.id_of("buntglas")
    id_kerzenwachs = mat.id_of("kerzenwachs")
    id_glockenbronze = mat.id_of("glockenbronze")
    id_algen = mat.id_of("algen")

    # Reset base solid as mauerwerk
    world.reset(id_mauerwerk)

    bands = common.region_bands(world.width, world.height, "vertical")
    b_tower, b_nave, b_crypt = bands[0], bands[1], bands[2]

    # --- 1. Glockenturm (Top band: y 0..y1) ---
    # Dry tower: water <= 1%. Large bell made of glockenbronze (>= 0.3%).
    # Carve interior of the bell tower
    tower_pad_x = max(15, world.width // 6)
    world.fill_rect(
        b_tower[0] + tower_pad_x, b_tower[1] + 8, b_tower[2] - tower_pad_x, b_tower[3] - 4, id_air
    )

    # Place the giant bronze bell in the center of the tower
    bell_cx = (b_tower[0] + b_tower[2]) // 2
    bell_top = b_tower[1] + 12
    # Ensure bell is large enough for glockenbronze >= 0.3% (e.g. 0.015 share)
    # Area of b_tower is 320 * 66 = 21120. 0.3% is ~64 pixels.
    # A 20x16 bell has 320 pixels.
    bell_w = min(28, (b_tower[2] - b_tower[0]) // 4)
    world.fill_rect(
        bell_cx - bell_w // 2, bell_top, bell_cx + bell_w // 2, bell_top + 16, id_glockenbronze
    )
    # Bell clapper / rim
    world.fill_rect(
        bell_cx - bell_w // 2 - 4,
        bell_top + 14,
        bell_cx + bell_w // 2 + 4,
        bell_top + 18,
        id_glockenbronze,
    )

    # Add wooden / candle platforms and candles (kerzenwachs) in the tower
    world.fill_rect(bell_cx - 30, bell_top + 26, bell_cx - 10, bell_top + 28, id_mauerwerk)
    world.fill_rect(bell_cx - 25, bell_top + 22, bell_cx - 15, bell_top + 26, id_kerzenwachs)

    world.fill_rect(bell_cx + 10, bell_top + 26, bell_cx + 30, bell_top + 28, id_mauerwerk)
    world.fill_rect(bell_cx + 15, bell_top + 22, bell_cx + 25, bell_top + 26, id_kerzenwachs)

    # Ensure no water in the bell tower
    # (world was reset to mauerwerk and carved with air)

    # --- 2. Kirchenschiff (Middle band: y1..y2) ---
    # Flooded nave: water >= 20%, mauerwerk >= 5%, buntglas >= 0.3%.
    # Carve main hall
    nave_pad = 10
    world.fill_rect(
        b_nave[0] + nave_pad, b_nave[1] + 4, b_nave[2] - nave_pad, b_nave[3] - 4, id_water
    )

    # Air bubble chapel under vault / dome
    chapel_w = min(60, (b_nave[2] - b_nave[0]) // 3)
    chapel_cx = (b_nave[0] + b_nave[2]) // 2
    world.fill_rect(
        chapel_cx - chapel_w // 2, b_nave[1] + 4, chapel_cx + chapel_w // 2, b_nave[1] + 20, id_air
    )

    # Pillars and archways of mauerwerk
    num_pillars = max(2, world.width // 60)
    step_pillar = (b_nave[2] - b_nave[0]) // (num_pillars + 1)
    for i in range(1, num_pillars + 1):
        px = b_nave[0] + i * step_pillar
        # Vertical pillar
        world.fill_rect(px - 4, b_nave[1] + 8, px + 4, b_nave[3] - 4, id_mauerwerk)
        # Arch connection
        world.fill_rect(px - 10, b_nave[1] + 10, px + 10, b_nave[1] + 14, id_mauerwerk)

    # Stained glass windows (buntglas) in pillars and side walls
    # b_nave area is ~21440. 0.3% is ~65 pixels.
    # Let's place several nice stained glass patches (e.g. 5x12 or similar)
    target_glass = int((b_nave[2] - b_nave[0]) * (b_nave[3] - b_nave[1]) * 0.015)
    placed_glass = 0
    while placed_glass < target_glass:
        gx = rng.randint(b_nave[0] + 12, b_nave[2] - 20)
        gy = rng.randint(b_nave[1] + 8, b_nave[3] - 18)
        world.fill_rect(gx, gy, gx + 6, gy + 10, id_buntglas)
        placed_glass += 60

    # Ensure mauerwerk >= 5% in nave (pillars already provide >5%, but outer walls also exist)

    # --- 3. Krypta (Bottom band: y2..y3) ---
    # Dark flooded crypt: algen >= 0.3%.
    # Carve flooded burial chambers / passages
    world.fill_rect(b_crypt[0] + 10, b_crypt[1] + 4, b_crypt[2] - 10, b_crypt[3] - 8, id_water)

    # Tombs / sarcophagi of mauerwerk
    num_tombs = max(3, world.width // 50)
    tomb_step = (b_crypt[2] - b_crypt[0]) // (num_tombs + 1)
    for i in range(1, num_tombs + 1):
        tx = b_crypt[0] + i * tomb_step
        world.fill_rect(tx - 8, b_crypt[3] - 22, tx + 8, b_crypt[3] - 10, id_mauerwerk)

    # Algen carpets along floor and tombs
    target_algen = int((b_crypt[2] - b_crypt[0]) * (b_crypt[3] - b_crypt[1]) * 0.02)
    placed_algen = 0
    while placed_algen < target_algen:
        ax = rng.randint(b_crypt[0] + 12, b_crypt[2] - 20)
        ay = rng.randint(b_crypt[1] + 10, b_crypt[3] - 14)
        world.fill_rect(ax, ay, ax + 8, ay + 6, id_algen)
        placed_algen += 48

    # --- 4. World-wide kerzenwachs (>= 0.05% = 0.0005) ---
    # World area 320*200 = 64000. 0.05% is 32 pixels.
    # Place candle shrines/altars in crypt and nave
    for _ in range(5):
        wx = rng.randint(20, world.width - 25)
        wy = rng.randint(b_tower[1] + 10, b_nave[3] - 10)
        # Small dry air pocket for the candle so it doesn't extinguish immediately
        world.fill_rect(wx - 2, wy - 6, wx + 6, wy + 2, id_air)
        world.fill_rect(wx - 1, wy - 1, wx + 5, wy + 2, id_kerzenwachs)

    # --- 5. Connecting Rooms & Arenas ---
    rooms = [
        (bell_cx - 25, b_tower[1] + 25, bell_cx + 25, b_tower[3] - 6),
        (chapel_cx - 25, b_nave[1] + 10, chapel_cx + 25, b_nave[3] - 15),
        (bell_cx - 30, b_crypt[1] + 15, bell_cx + 30, b_crypt[3] - 12),
    ]

    tower_mid = _centre(rooms[0])
    nave_mid = _centre(rooms[1])
    crypt_mid = _centre(rooms[2])

    common.carve_tunnel(world, tower_mid, nave_mid, 8)
    common.carve_tunnel(world, nave_mid, crypt_mid, 8)

    # Replace any water that leaked into glockenturm with air, leaving mauerwerk, bronze, etc. intact
    for ty in range(b_tower[1], b_tower[3]):
        for tx in range(b_tower[0], b_tower[2]):
            if world.get(tx, ty) == id_water:
                world.set(tx, ty, id_air)

    # Arenas: mid-boss in nave, boss in crypt
    mid, boss = common.place_boss_arenas(world, b_nave, b_crypt, rng)
    common.carve_tunnel(world, nave_mid, _centre(mid), 8)
    common.carve_tunnel(world, crypt_mid, _centre(boss), 8)

    # Nook in tower, shrine in nave
    nook = common.place_trader_nook(world, b_tower, rng)
    shrine = common.place_challenge_shrine(world, b_nave, rng)

    # Again ensure no water in tower
    for ty in range(b_tower[1], b_tower[3]):
        for tx in range(b_tower[0], b_tower[2]):
            if world.get(tx, ty) == id_water:
                world.set(tx, ty, id_air)

    # --- 1. Glockenturm (Top band: y 0..y1) ---
    # Dry tower: water <= 1%. Large bell made of glockenbronze (>= 0.3%).
    # Carve interior of the bell tower
    tower_pad_x = max(15, world.width // 6)
    world.fill_rect(b_tower[0] + tower_pad_x, b_tower[1] + 8, b_tower[2] - tower_pad_x, b_tower[3] - 4, id_air)

    # Place the giant bronze bell in the center of the tower
    bell_cx = (b_tower[0] + b_tower[2]) // 2
    bell_top = b_tower[1] + 12
    # Ensure bell is large enough for glockenbronze >= 0.3% (e.g. 0.015 share)
    # Area of b_tower is 320 * 66 = 21120. 0.3% is ~64 pixels.
    # A 20x16 bell has 320 pixels.
    bell_w = min(28, (b_tower[2] - b_tower[0]) // 4)
    world.fill_rect(bell_cx - bell_w // 2, bell_top, bell_cx + bell_w // 2, bell_top + 16, id_glockenbronze)
    # Bell clapper / rim
    world.fill_rect(bell_cx - bell_w // 2 - 4, bell_top + 14, bell_cx + bell_w // 2 + 4, bell_top + 18, id_glockenbronze)

    # Add wooden / candle platforms and candles (kerzenwachs) in the tower
    world.fill_rect(bell_cx - 30, bell_top + 26, bell_cx - 10, bell_top + 28, id_mauerwerk)
    world.fill_rect(bell_cx - 25, bell_top + 22, bell_cx - 15, bell_top + 26, id_kerzenwachs)

    world.fill_rect(bell_cx + 10, bell_top + 26, bell_cx + 30, bell_top + 28, id_mauerwerk)
    world.fill_rect(bell_cx + 15, bell_top + 22, bell_cx + 25, bell_top + 26, id_kerzenwachs)

    # Ensure no water in the bell tower
    # (world was reset to mauerwerk and carved with air)

    # --- 2. Kirchenschiff (Middle band: y1..y2) ---
    # Flooded nave: water >= 20%, mauerwerk >= 5%, buntglas >= 0.3%.
    # Carve main hall
    nave_pad = 10
    world.fill_rect(b_nave[0] + nave_pad, b_nave[1] + 4, b_nave[2] - nave_pad, b_nave[3] - 4, id_water)

    # Air bubble chapel under vault / dome
    chapel_w = min(60, (b_nave[2] - b_nave[0]) // 3)
    chapel_cx = (b_nave[0] + b_nave[2]) // 2
    world.fill_rect(chapel_cx - chapel_w // 2, b_nave[1] + 4, chapel_cx + chapel_w // 2, b_nave[1] + 20, id_air)

    # Pillars and archways of mauerwerk
    num_pillars = max(2, world.width // 60)
    step_pillar = (b_nave[2] - b_nave[0]) // (num_pillars + 1)
    for i in range(1, num_pillars + 1):
        px = b_nave[0] + i * step_pillar
        # Vertical pillar
        world.fill_rect(px - 4, b_nave[1] + 8, px + 4, b_nave[3] - 4, id_mauerwerk)
        # Arch connection
        world.fill_rect(px - 10, b_nave[1] + 10, px + 10, b_nave[1] + 14, id_mauerwerk)

    # Stained glass windows (buntglas) in pillars and side walls
    # b_nave area is ~21440. 0.3% is ~65 pixels.
    # Let's place several nice stained glass patches (e.g. 5x12 or similar)
    target_glass = int((b_nave[2] - b_nave[0]) * (b_nave[3] - b_nave[1]) * 0.015)
    placed_glass = 0
    while placed_glass < target_glass:
        gx = rng.randint(b_nave[0] + 12, b_nave[2] - 20)
        gy = rng.randint(b_nave[1] + 8, b_nave[3] - 18)
        world.fill_rect(gx, gy, gx + 6, gy + 10, id_buntglas)
        placed_glass += 60

    # Ensure mauerwerk >= 5% in nave (pillars already provide >5%, but outer walls also exist)

    # --- 3. Krypta (Bottom band: y2..y3) ---
    # Dark flooded crypt: algen >= 0.3%.
    # Carve flooded burial chambers / passages
    world.fill_rect(b_crypt[0] + 10, b_crypt[1] + 4, b_crypt[2] - 10, b_crypt[3] - 8, id_water)

    # Tombs / sarcophagi of mauerwerk
    num_tombs = max(3, world.width // 50)
    tomb_step = (b_crypt[2] - b_crypt[0]) // (num_tombs + 1)
    for i in range(1, num_tombs + 1):
        tx = b_crypt[0] + i * tomb_step
        world.fill_rect(tx - 8, b_crypt[3] - 22, tx + 8, b_crypt[3] - 10, id_mauerwerk)

    # Algen carpets along floor and tombs
    target_algen = int((b_crypt[2] - b_crypt[0]) * (b_crypt[3] - b_crypt[1]) * 0.02)
    placed_algen = 0
    while placed_algen < target_algen:
        ax = rng.randint(b_crypt[0] + 12, b_crypt[2] - 20)
        ay = rng.randint(b_crypt[1] + 10, b_crypt[3] - 14)
        world.fill_rect(ax, ay, ax + 8, ay + 6, id_algen)
        placed_algen += 48

    # --- 4. World-wide kerzenwachs (>= 0.05% = 0.0005) ---
    # World area 320*200 = 64000. 0.05% is 32 pixels.
    # Place candle shrines/altars in crypt and nave
    for _ in range(5):
        wx = rng.randint(20, world.width - 25)
        wy = rng.randint(b_tower[1] + 10, b_nave[3] - 10)
        # Small dry air pocket for the candle so it doesn't extinguish immediately
        world.fill_rect(wx - 2, wy - 6, wx + 6, wy + 2, id_air)
        world.fill_rect(wx - 1, wy - 1, wx + 5, wy + 2, id_kerzenwachs)

    # --- 5. Connecting Rooms & Arenas ---
    rooms = [
        (bell_cx - 25, b_tower[1] + 25, bell_cx + 25, b_tower[3] - 6),
        (chapel_cx - 25, b_nave[1] + 10, chapel_cx + 25, b_nave[3] - 15),
        (bell_cx - 30, b_crypt[1] + 15, bell_cx + 30, b_crypt[3] - 12),
    ]

    tower_mid = _centre(rooms[0])
    nave_mid = _centre(rooms[1])
    crypt_mid = _centre(rooms[2])

    common.carve_tunnel(world, tower_mid, nave_mid, 8)
    common.carve_tunnel(world, nave_mid, crypt_mid, 8)

    # Replace any water that leaked into glockenturm with air, leaving mauerwerk, bronze, etc. intact
    for ty in range(b_tower[1], b_tower[3]):
        for tx in range(b_tower[0], b_tower[2]):
            if world.get(tx, ty) == id_water:
                world.set(tx, ty, id_air)

    # Arenas: mid-boss in nave, boss in crypt
    mid, boss = common.place_boss_arenas(world, b_nave, b_crypt, rng)
    common.carve_tunnel(world, nave_mid, _centre(mid), 8)
    common.carve_tunnel(world, crypt_mid, _centre(boss), 8)

    # Nook in tower, shrine in nave
    nook = common.place_trader_nook(world, b_tower, rng)
    shrine = common.place_challenge_shrine(world, b_nave, rng)

    # Again ensure no water in tower
    for ty in range(b_tower[1], b_tower[3]):
        for tx in range(b_tower[0], b_tower[2]):
            if world.get(tx, ty) == id_water:
                world.set(tx, ty, id_air)

    keys = [r.key for r in universe.regions][:3]
    spawn = (rooms[0][0] + 6, rooms[0][3] - 6)
    exit_point = _centre(rooms[2])

    world.fill_disc(spawn[0], spawn[1], 6, id_air)
    world.fill_disc(exit_point[0], exit_point[1], 6, id_air)

    # --- 6. Props: abtei_glocke ---
    props: list[tuple[str, int, int]] = [
        ("abtei_glocke", bell_cx, bell_top + 8),
    ]

    # --- 7. Quest Giver ---
    # Stands in air with solid floor beneath (within 1..12 px) in the dry bell tower
    qx = max(5, min(world.width - 6, rooms[0][0] + 10))
    qy = rooms[0][3] - 8
    world.fill_disc(qx, qy, 4, id_air)
    world.fill_rect(qx - 5, qy + 4, qx + 6, qy + 8, id_mauerwerk)
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
