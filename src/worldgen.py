"""Procedural cave generation: carves tunnels into stone and scatters materials."""

from __future__ import annotations

import math

from src.materials import AIR, LAVA, OIL, SAND, STONE, WATER, WOOD
from src.player import PLAYER_HEIGHT
from src.world import BORDER, World, disc_offsets

SPAWN_HALF_WIDTH = 26
SPAWN_TOP = 36
SPAWN_FLOOR = 66  # first stone row below the spawn cavern


def generate_world(world: World) -> tuple[int, int]:
    """Fill ``world`` with a cave level and return the player's spawn (top-left, in cells)."""
    rng = world.rng
    w, h = world.width, world.height
    world.reset(STONE)
    centre_x = w // 2

    # Spawn cavern with a flat floor.
    for y in range(SPAWN_TOP, SPAWN_FLOOR):
        for x in range(centre_x - SPAWN_HALF_WIDTH, centre_x + SPAWN_HALF_WIDTH):
            world.grid[y * w + x] = AIR

    # Tunnels: the first ones start in the spawn cavern so the level is always reachable.
    for index in range(16):
        if index < 3:
            x, y = float(centre_x + rng.randint(-15, 15)), float(SPAWN_FLOOR)
            angle = math.pi / 2 + rng.uniform(-0.6, 0.6)
        else:
            x, y = float(rng.randint(20, w - 20)), float(rng.randint(40, h - 20))
            angle = rng.uniform(0, 2 * math.pi)
        radius = rng.randint(3, 7)
        for _ in range(rng.randint(70, 160)):
            world.carve_disc(int(x), int(y), radius)
            angle += rng.uniform(-0.6, 0.6)
            x = min(max(x + math.cos(angle) * 2, 12), w - 12)
            y = min(max(y + math.sin(angle) * 2, 12), h - 12)
            radius = min(max(radius + rng.choice((-1, 0, 0, 1)), 3), 8)

    # A few larger chambers.
    for _ in range(6):
        world.carve_disc(rng.randint(30, w - 30), rng.randint(90, h - 30), rng.randint(10, 18))

    # Tunnels may have eaten the spawn floor: restore a solid platform under the player.
    for y in range(SPAWN_FLOOR, SPAWN_FLOOR + 3):
        for x in range(centre_x - 8, centre_x + 8):
            world.grid[y * w + x] = STONE

    _scatter(world, SAND, count=10, radius=(4, 8), min_y=70)
    _scatter(world, WATER, count=8, radius=(5, 8), min_y=70)
    _scatter(world, OIL, count=4, radius=(4, 6), min_y=h // 2)
    _scatter(world, LAVA, count=5, radius=(4, 7), min_y=int(h * 0.6))
    for _ in range(6):
        _plank(world)

    world.sleep_all()  # only the chunks holding liquids, powders and wood stay awake
    return centre_x - 2, SPAWN_FLOOR - PLAYER_HEIGHT


def _in_spawn_zone(x: int, y: int, centre_x: int) -> bool:
    return abs(x - centre_x) < SPAWN_HALF_WIDTH + 20 and y < SPAWN_FLOOR + 20


def _floor_y(world: World, x: int, y: int) -> int:
    while world.get(x, y + 1) == AIR:
        y += 1
    return y


def _scatter(
    world: World, material: int, count: int, radius: tuple[int, int], min_y: int
) -> None:
    """Drop ``count`` blobs of ``material`` onto cave floors."""
    rng = world.rng
    for _ in range(count):
        for _attempt in range(40):
            x = rng.randint(BORDER + 8, world.width - BORDER - 8)
            y = rng.randint(min_y, world.height - 20)
            if world.get(x, y) != AIR or _in_spawn_zone(x, y, world.width // 2):
                continue
            r = rng.randint(*radius)
            floor = _floor_y(world, x, y)
            for dx, dy in disc_offsets(r):
                if world.get(x + dx, floor - r // 2 + dy) == AIR:
                    world.set_cell(x + dx, floor - r // 2 + dy, material)
            break


def _plank(world: World) -> None:
    """Place a wooden platform with a support post in open cave space."""
    rng = world.rng
    for _attempt in range(40):
        x = rng.randint(20, world.width - 50)
        y = rng.randint(80, world.height - 30)
        length = rng.randint(12, 24)
        cells = [(x + i, y + j) for i in range(length) for j in range(2)]
        post = [(x + length // 2, y + 2 + k) for k in range(5)]
        if _in_spawn_zone(x, y, world.width // 2):
            continue
        if all(world.get(cx, cy) == AIR for cx, cy in cells + post):
            for cx, cy in cells + post:
                world.set_cell(cx, cy, WOOD)
            return
