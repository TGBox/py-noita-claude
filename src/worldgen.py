"""Procedural level generation: tunnels through the flesh of a living organism."""

from __future__ import annotations

import math

from src.materials import (
    ACID,
    AIR,
    BLOOD,
    BONE,
    BONE_DUST,
    FLESH,
    GROWTH,
    SINEW,
    TALLOW,
)
from src.player import PLAYER_HEIGHT
from src.world import BORDER, World, disc_offsets

SPAWN_HALF_WIDTH = 52
SPAWN_FLOOR = 132  # first solid row below the spawn cavern
SPAWN_CLEARANCE = 40  # keep hazards this far away from the spawn cavern
SPAWN_RADIUS_Y = 34


def generate_world(world: World) -> tuple[int, int]:
    """Fill ``world`` with a level and return the player's spawn (top-left, in cells)."""
    rng = world.rng
    w, h = world.width, world.height
    scale = (w * h) / (1280 * 720)  # feature counts follow the world area
    world.reset(FLESH)
    centre_x = w // 2

    _ribs(world, count=int(34 * scale))

    # Organic cavities (organs) connected by winding tunnels into one network.
    spawn = (centre_x, SPAWN_FLOOR - SPAWN_RADIUS_Y)
    _carve_oval(world, spawn[0], spawn[1], SPAWN_HALF_WIDTH, SPAWN_RADIUS_Y)
    nodes = [spawn]
    for _attempt in range(int(400 * scale)):
        if len(nodes) > int(56 * scale):
            break
        x = rng.randint(60, w - 60)
        y = rng.randint(SPAWN_FLOOR + 40, h - 50)
        if all((x - nx) ** 2 + (y - ny) ** 2 > 75**2 for nx, ny in nodes):
            nodes.append((x, y))
    for x, y in nodes[1:]:
        _carve_cavity(world, x, y, rng.randint(16, 40))
    for a, b in _connections(world, nodes):
        _carve_tunnel(world, a, b)

    # Bone platform under the spawn so tunnels cannot eat the floor.
    for y in range(SPAWN_FLOOR, SPAWN_FLOOR + 5):
        row = y * w
        world.grid[row + centre_x - 16 : row + centre_x + 16] = bytes([BONE]) * 32

    _scatter(world, BONE_DUST, count=int(18 * scale), radius=(8, 14), min_y=SPAWN_FLOOR + 10)
    _scatter(world, BLOOD, count=int(16 * scale), radius=(9, 15), min_y=SPAWN_FLOOR + 10)
    _scatter(world, TALLOW, count=int(7 * scale), radius=(7, 11), min_y=h // 2)
    _scatter(world, ACID, count=int(8 * scale), radius=(7, 12), min_y=int(h * 0.6))
    for _ in range(int(6 * scale)):
        _growth_nest(world)
    for _ in range(int(10 * scale)):
        _sinew_bridge(world)

    world.wake_all()  # every chunk settles once the camera comes near
    return centre_x - 4, SPAWN_FLOOR - PLAYER_HEIGHT


def _carve_oval(world: World, cx: int, cy: int, rx: int, ry: int) -> None:
    w = world.width
    for dy in range(-ry, ry):
        half = int(rx * math.sqrt(max(0.0, 1 - (dy / ry) ** 2)))
        row = (cy + dy) * w
        world.grid[row + cx - half : row + cx + half] = bytes(2 * half)


def _carve_cavity(world: World, x: int, y: int, radius: int) -> None:
    """A lumpy, organ-like hollow made of overlapping discs."""
    rng = world.rng
    world.fill_disc(x, y, radius, AIR)
    for _ in range(rng.randint(3, 7)):
        angle = rng.uniform(0, 2 * math.pi)
        distance = radius * rng.uniform(0.4, 0.9)
        world.fill_disc(
            int(x + math.cos(angle) * distance),
            int(y + math.sin(angle) * distance * 0.8),
            int(radius * rng.uniform(0.35, 0.7)),
            AIR,
        )


def _connections(world: World, nodes: list[tuple[int, int]]) -> list[tuple]:
    """Minimum spanning tree over the cavities plus a few extra loops."""
    connected = [0]
    edges: list[tuple] = []
    remaining = set(range(1, len(nodes)))
    while remaining:
        a, b = min(
            ((a, b) for a in connected for b in remaining),
            key=lambda e: (nodes[e[0]][0] - nodes[e[1]][0]) ** 2
            + (nodes[e[0]][1] - nodes[e[1]][1]) ** 2,
        )
        edges.append((nodes[a], nodes[b]))
        connected.append(b)
        remaining.remove(b)
    for _ in range(len(nodes) // 4):
        a, b = world.rng.sample(nodes, 2)
        if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 320**2:
            edges.append((a, b))
    return edges


def _carve_tunnel(world: World, start: tuple[int, int], end: tuple[int, int]) -> None:
    """Winding passage with lumpy walls from ``start`` to ``end``."""
    rng = world.rng
    x, y = float(start[0]), float(start[1])
    radius = rng.randint(5, 9)
    wobble = 0.0
    for _ in range(2000):
        dx, dy = end[0] - x, end[1] - y
        if dx * dx + dy * dy < 9:
            break
        wobble = max(-1.1, min(1.1, wobble + rng.uniform(-0.25, 0.25)))
        angle = math.atan2(dy, dx) + wobble
        x += math.cos(angle) * 3
        y += math.sin(angle) * 3
        world.fill_disc(int(x), int(y), radius, AIR)
        if rng.random() < 0.15:
            side = angle + math.pi / 2 * rng.choice((-1, 1))
            world.fill_disc(
                int(x + math.cos(side) * radius),
                int(y + math.sin(side) * radius),
                rng.randint(3, 6),
                AIR,
            )
        radius = min(max(radius + rng.choice((-1, 0, 0, 0, 1)), 5), 10)


def _in_spawn_zone(world: World, x: int, y: int) -> bool:
    centre_x = world.width // 2
    return (
        abs(x - centre_x) < SPAWN_HALF_WIDTH + SPAWN_CLEARANCE
        and y < SPAWN_FLOOR + SPAWN_CLEARANCE
    )


def _ribs(world: World, count: int) -> None:
    """Curved bone ribs running through the flesh (only overwrite flesh)."""
    rng = world.rng
    for _ in range(count):
        x, y = float(rng.randint(30, world.width - 30)), float(rng.randint(30, world.height - 30))
        angle = rng.uniform(0, 2 * math.pi)
        bend = rng.uniform(-0.04, 0.04)
        thickness = rng.randint(2, 4)
        for _ in range(rng.randint(40, 110)):
            for dx, dy in disc_offsets(thickness):
                if world.get(int(x) + dx, int(y) + dy) == FLESH:
                    world.grid[(int(y) + dy) * world.width + int(x) + dx] = BONE
            angle += bend
            x += math.cos(angle) * 2
            y += math.sin(angle) * 2
            if not (BORDER + 6 < x < world.width - BORDER - 6) or not (
                BORDER + 6 < y < world.height - BORDER - 6
            ):
                break


def _floor_y(world: World, x: int, y: int) -> int:
    while world.get(x, y + 1) == AIR:
        y += 1
    return y


def _random_air(world: World, min_y: int) -> tuple[int, int] | None:
    rng = world.rng
    for _attempt in range(60):
        x = rng.randint(BORDER + 16, world.width - BORDER - 16)
        y = rng.randint(min_y, world.height - 30)
        if world.get(x, y) == AIR and not _in_spawn_zone(world, x, y):
            return x, y
    return None


def _scatter(world: World, material: int, count: int, radius: tuple[int, int], min_y: int) -> None:
    """Drop ``count`` blobs of ``material`` onto cave floors (they settle in play)."""
    for _ in range(count):
        spot = _random_air(world, min_y)
        if spot is None:
            continue
        x, y = spot
        r = world.rng.randint(*radius)
        floor = _floor_y(world, x, y)
        for dx, dy in disc_offsets(r):
            if world.get(x + dx, floor - r // 2 + dy) == AIR:
                world.set_cell(x + dx, floor - r // 2 + dy, material)


def _growth_nest(world: World) -> None:
    """Embed a growth colony into a flesh wall next to open space."""
    spot = _random_air(world, SPAWN_FLOOR + 20)
    if spot is None:
        return
    x, y = spot
    floor = _floor_y(world, x, y)
    r = world.rng.randint(6, 11)
    for dx, dy in disc_offsets(r):
        if world.get(x + dx, floor + dy) in (FLESH, BLOOD):
            world.set_cell(x + dx, floor + dy, GROWTH)


def _sinew_bridge(world: World) -> None:
    """Stretch a band of sinew across open space, anchored on both ends."""
    rng = world.rng
    for _attempt in range(60):
        spot = _random_air(world, SPAWN_FLOOR + 20)
        if spot is None:
            return
        x, y = spot
        left = x
        while world.get(left - 1, y) == AIR and x - left < 120:
            left -= 1
        right = x
        while world.get(right + 1, y) == AIR and right - x < 120:
            right += 1
        span = right - left + 1
        if not 24 <= span <= 110 or world.get(left - 1, y) == AIR or world.get(right + 1, y) == AIR:
            continue
        thickness = rng.randint(2, 3)
        sag = rng.uniform(2, 8)
        for xx in range(left, right + 1):
            t = (xx - left) / max(1, span - 1)
            yy = y + int(sag * math.sin(math.pi * t))
            for k in range(thickness):
                if world.get(xx, yy + k) == AIR:
                    world.set_cell(xx, yy + k, SINEW)
        return
