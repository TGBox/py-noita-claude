"""Procedural level generation: tunnels through the flesh of a living organism."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src import materials as mat
from src.depths import DEPTHS, Depth
from src.materials import AIR, BEDROCK, BLOCKS_BODY, KIND, LIQUID, SOLID
from src.native import byte_view, reachable
from src.player import PLAYER_HEIGHT, PLAYER_WIDTH
from src.world import BORDER, World, disc_offsets

SPAWN_HALF_WIDTH = 52
SPAWN_FLOOR = 132  # first solid row below the spawn cavern
SPAWN_CLEARANCE = 40  # keep hazards this far away from the spawn cavern
SPAWN_RADIUS_Y = 34
SPAWN_OFFSET_X = -36  # the player starts left of the cavern's centre
SETTLE_STEPS = (240, 90, 90)  # simulation ticks before each path check
TUNNEL_MIN_RADIUS = 11  # 22 px: comfortably taller than the 18 px player
BRIDGE_GAP = 20
PATH_REPAIRS = 6
ARENA_RADIUS = 72


@dataclass(frozen=True)
class Level:
    """Where things are in a generated level."""

    spawn: tuple[int, int]  # player top-left
    exit: tuple[int, int]  # centre of the way down
    arena: tuple[int, int] | None  # centre of the boss chamber, if any
    secret: tuple[int, int] | None = None  # centre of the sealed chamber with an Urauge
    vault: tuple[int, int] | None = None  # centre of the bone-sealed treasure vault


def generate_world(world: World) -> tuple[int, int]:
    """Fill ``world`` with a first-depth level and return the player's spawn."""
    return generate_level(world, DEPTHS[0]).spawn


def generate_level(world: World, depth: Depth) -> Level:
    """Fill ``world`` with a level of the given depth."""
    rng = world.rng
    w, h = world.width, world.height
    scale = (w * h) / (1280 * 720)  # feature counts follow the world area
    bone_walls = depth.wall == "knochen"
    world.reset(mat.BONE if bone_walls else mat.FLESH)
    centre_x = w // 2

    if bone_walls:  # inverted: veins of flesh running through solid bone
        _ribs(world, count=int(46 * scale), base=mat.BONE, vein=mat.FLESH)
    else:
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
    arena = None
    if depth.boss:
        arena = (centre_x + rng.randint(-200, 200), h - ARENA_RADIUS - 40)
        nodes = [n for n in nodes if math.dist(n, arena) > ARENA_RADIUS + 50]
        nodes.append(arena)
    for x, y in nodes[1:]:
        if (x, y) != arena:
            _carve_cavity(world, x, y, int(rng.randint(16, 40) * depth.cavity_scale))
    for a, b in _connections(world, nodes):
        _carve_tunnel(world, a, b)

    # Bone platform under the spawn (left of centre, where tunnels rarely leave the
    # cavern) so the player never starts above a hole.
    spawn_x = centre_x + SPAWN_OFFSET_X
    for y in range(SPAWN_FLOOR - PLAYER_HEIGHT - 8, SPAWN_FLOOR):  # flat alcove
        row = y * w
        world.grid[row + spawn_x - 12 : row + spawn_x + 12] = bytes(24)
    for y in range(SPAWN_FLOOR, SPAWN_FLOOR + 5):
        row = y * w
        world.grid[row + spawn_x - 12 : row + spawn_x + 12] = bytes([mat.BONE]) * 24

    def amount(base: float, factor: float) -> int:
        return int(base * scale * factor)

    for _ in range(amount(26, depth.alveoli)):
        _alveolus_cluster(world)

    _scatter(
        world, mat.BONE_DUST, amount(18, depth.bone_dust), (6, 10), SPAWN_FLOOR + 10, min_width=70
    )
    _scatter(world, mat.BLOOD, amount(16, depth.blood), (9, 15), SPAWN_FLOOR + 10)
    _scatter(world, mat.TALLOW, amount(7, depth.tallow), (7, 11), h // 2)
    _scatter(world, mat.ACID, amount(8, depth.acid), (7, 12), int(h * 0.6))
    if depth.pus:
        _scatter(world, mat.PUS, amount(9, depth.pus), (7, 11), SPAWN_FLOOR + 10)
    if depth.magma:
        _scatter(world, mat.MAGMA, amount(10, depth.magma), (7, 10), int(h * 0.55))
    if depth.mucus:
        _scatter(world, mat.MUCUS, amount(10, depth.mucus), (8, 13), SPAWN_FLOOR + 10)
        for _ in range(amount(40, depth.mucus)):
            _mucus_drip(world)
    for _ in range(amount(6, depth.growth)):
        _growth_nest(world)
    for _ in range(amount(14, depth.enamel)):
        _enamel_vein(world)
    for _ in range(amount(10, depth.bridges)):
        _sinew_bridge(world)

    if arena is not None:
        # The boss chamber: a big round hall with a bone floor, kept free of hazards.
        _carve_oval(world, arena[0], arena[1], ARENA_RADIUS + 30, ARENA_RADIUS)
        for y in range(arena[1] + ARENA_RADIUS - 6, arena[1] + ARENA_RADIUS):
            row = y * w
            x0, x1 = arena[0] - ARENA_RADIUS, arena[0] + ARENA_RADIUS
            world.grid[row + x0 : row + x1] = bytes([mat.BONE]) * (x1 - x0)
        exit_point = arena
    else:
        deepest = max(nodes[1:], key=lambda n: n[1] + 0.3 * math.dist(n, spawn))
        exit_point = (deepest[0], _floor_y(world, deepest[0], deepest[1]) - 12)

    vault = None if depth.final else _vault(world, arena, exit_point)
    player_spawn = (spawn_x - PLAYER_WIDTH // 2, SPAWN_FLOOR - PLAYER_HEIGHT)
    # Let powders and liquids settle first: falling bone dust can plug a tunnel that was
    # open right after carving. Digging may release more dust, so repeat until stable.
    for steps in SETTLE_STEPS:
        for _ in range(steps):
            world.step()
        if not ensure_path(world, player_spawn, exit_point):
            break
    secret = _secret_chamber(world, player_spawn, exit_point)
    world.wake_all()  # every chunk settles once the camera comes near
    return Level(player_spawn, exit_point, arena, secret, vault)


def ensure_path(world: World, spawn: tuple[int, int], target: tuple[int, int]) -> int:
    """Make sure the player can get from ``spawn`` to ``target`` (flying allowed).

    Searches all positions where the player's body fits; if the target cannot be
    reached, a passage is dug from the closest reachable point. Returns the number
    of passages dug.
    """
    goal = (target[0] - PLAYER_WIDTH // 2, target[1] - PLAYER_HEIGHT // 2)
    box = (PLAYER_WIDTH + 2, PLAYER_HEIGHT + 2)  # a little headroom
    # Liquids count as walls here: blood clots into scab over time and could otherwise
    # turn a pool that fills a tunnel into a plug later on.
    blocking = [int(b or k == LIQUID) for b, k in zip(BLOCKS_BODY, KIND)]
    dug = 0
    for _ in range(PATH_REPAIRS):
        found, closest = reachable(
            byte_view(world.grid), world.width, world.height, blocking, box,
            (spawn[0] - 1, spawn[1] - 2), goal,
        )  # fmt: skip
        if found:
            return dug
        start = (closest[0] + box[0] // 2, closest[1] + box[1] // 2)
        _carve_tunnel(world, start, target, radius_range=(12, 14), wobble_limit=0.5)
        dug += 1
    return dug


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


def _alveolus_cluster(world: World) -> None:
    """Spongy tissue: a clump of air sacs with thin, torn sinew membranes.

    Membranes are only drawn where there was tissue before, so they never wall off
    the tunnels and cavities that are already there.
    """
    rng = world.rng
    w, h = world.width, world.height
    for _attempt in range(12):
        cx, cy = rng.randint(80, w - 80), rng.randint(SPAWN_FLOOR + 30, h - 60)
        if world.get(cx, cy) == mat.FLESH and not _in_spawn_zone(world, cx, cy):
            break
    else:
        return
    before = bytes(world.grid)
    sacs = []
    for _ in range(rng.randint(7, 14)):
        x = cx + rng.randint(-45, 45)
        y = cy + rng.randint(-32, 32)
        r = rng.randint(8, 18)
        world.fill_disc(x, y, r, AIR)
        sacs.append((x, y, r))
    for x, y, r in sacs:
        steps = int(2 * math.pi * r * 1.5)
        gap_start = rng.uniform(0, 2 * math.pi)
        for k in range(steps):
            angle = 2 * math.pi * k / steps
            if (angle - gap_start) % (2 * math.pi) < 1.1:  # a tear in every membrane
                continue
            px, py = int(x + math.cos(angle) * r), int(y + math.sin(angle) * r)
            if 0 <= px < w and 0 <= py < h and before[py * w + px] == mat.FLESH:
                world.set_cell(px, py, mat.SINEW)


VAULT_RX, VAULT_RY = 46, 26  # the treasure vault's hall
VAULT_SHELL = 7  # thick bone all around: it has to be blasted open


def _vault(
    world: World, arena: tuple[int, int] | None, exit_point: tuple[int, int]
) -> tuple[int, int] | None:
    """A bone-walled hall at the left or right edge, guarded and full of loot."""
    rng = world.rng
    w, h = world.width, world.height
    for _attempt in range(40):
        side = rng.choice((-1, 1))
        x = w // 2 + side * (w // 2 - BORDER - VAULT_RX - VAULT_SHELL - 6)
        y = rng.randint(SPAWN_FLOOR + 80, h - VAULT_RY - VAULT_SHELL - 30)
        far_from_arena = arena is None or math.dist((x, y), arena) > ARENA_RADIUS + VAULT_RX + 60
        if far_from_arena and math.dist((x, y), exit_point) > VAULT_RX + VAULT_SHELL + 40:
            break
    else:
        return None
    _carve_oval_material(world, x, y, VAULT_RX + VAULT_SHELL, VAULT_RY + VAULT_SHELL, mat.BONE)
    _carve_oval(world, x, y, VAULT_RX, VAULT_RY)
    for row in range(y + VAULT_RY - 4, y + VAULT_RY):  # a floor to stand on
        world.grid[row * w + x - VAULT_RX + 4 : row * w + x + VAULT_RX - 4] = bytes([mat.BONE]) * (
            2 * VAULT_RX - 8
        )
    return x, y


SECRET_RADIUS = 7  # air inside the chamber
SECRET_SHELL = 4  # bone wall around it
SECRET_CLEARANCE = 30  # solid tissue needed around the spot (so it stays hidden)


def _secret_chamber(
    world: World, spawn: tuple[int, int], exit_point: tuple[int, int]
) -> tuple[int, int] | None:
    """Seal a small bone-walled chamber deep inside solid tissue. Returns its centre."""
    rng = world.rng
    w = world.width
    grid = world.grid
    for attempt in range(1200):
        x = rng.randint(80, w - 80)
        y = rng.randint(SPAWN_FLOOR + 40, world.height - 50)
        if math.dist((x, y), spawn) < 200 or math.dist((x, y), exit_point) < 120:
            continue
        # be less picky the longer it takes: every depth must hide its Urauge
        r = SECRET_CLEARANCE - 6 * (attempt // 400)
        if any(
            not BLOCKS_BODY[grid[(y + dy) * w + x + dx]]
            for dy in range(-r, r + 1, 3)
            for dx in range(-r, r + 1, 3)
            if dx * dx + dy * dy <= r * r
        ):
            continue
        world.fill_disc(x, y, SECRET_RADIUS + SECRET_SHELL, mat.BONE)
        world.fill_disc(x, y, SECRET_RADIUS, AIR)
        return x, y
    return None


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


def _carve_tunnel(
    world: World,
    start: tuple[int, int],
    end: tuple[int, int],
    radius_range: tuple[int, int] = (TUNNEL_MIN_RADIUS, TUNNEL_MIN_RADIUS + 3),
    wobble_limit: float = 1.1,
) -> None:
    """Winding passage with lumpy walls from ``start`` to ``end``.

    The radius never drops below ``radius_range[0]`` so the player always fits.
    """
    rng = world.rng
    x, y = float(start[0]), float(start[1])
    low, high = radius_range
    radius = rng.randint(low, high)
    wobble = 0.0
    for _ in range(2000):
        dx, dy = end[0] - x, end[1] - y
        if dx * dx + dy * dy < 9:
            world.fill_disc(int(end[0]), int(end[1]), radius, AIR)
            break
        wobble = max(-wobble_limit, min(wobble_limit, wobble + rng.uniform(-0.25, 0.25)))
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
        radius = min(max(radius + rng.choice((-1, 0, 0, 0, 1)), low), high + 2)


def _in_spawn_zone(world: World, x: int, y: int) -> bool:
    centre_x = world.width // 2
    return (
        abs(x - centre_x) < SPAWN_HALF_WIDTH + SPAWN_CLEARANCE
        and y < SPAWN_FLOOR + SPAWN_CLEARANCE
    )


def _ribs(world: World, count: int, base: int | None = None, vein: int | None = None) -> None:
    """Curved ribs of ``vein`` running through the ``base`` tissue (only overwrite base)."""
    base = mat.FLESH if base is None else base
    vein = mat.BONE if vein is None else vein
    rng = world.rng
    for _ in range(count):
        x, y = float(rng.randint(30, world.width - 30)), float(rng.randint(30, world.height - 30))
        angle = rng.uniform(0, 2 * math.pi)
        bend = rng.uniform(-0.04, 0.04)
        thickness = rng.randint(2, 4)
        for _ in range(rng.randint(40, 110)):
            for dx, dy in disc_offsets(thickness):
                if world.get(int(x) + dx, int(y) + dy) == base:
                    world.grid[(int(y) + dy) * world.width + int(x) + dx] = vein
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


def _scatter(
    world: World,
    material: int,
    count: int,
    radius: tuple[int, int],
    min_y: int,
    min_width: int = 0,
) -> None:
    """Drop ``count`` blobs of ``material`` onto cave floors (they settle in play).

    With ``min_width`` the blob only lands where the floor is at least that wide,
    so powders do not plug narrow tunnels.
    """
    for _ in range(count):
        spot = _random_air(world, min_y)
        if spot is None:
            continue
        x, y = spot
        r = world.rng.randint(*radius)
        floor = _floor_y(world, x, y)
        if min_width and _air_span(world, x, floor - 3) < min_width:
            continue
        for dx, dy in disc_offsets(r):
            if world.get(x + dx, floor - r // 2 + dy) == AIR:
                world.set_cell(x + dx, floor - r // 2 + dy, material)


def _air_span(world: World, x: int, y: int) -> int:
    """Width of the open run of air through (x, y) on row y (capped at 200)."""
    left = right = x
    while world.get(left - 1, y) == AIR and x - left < 100:
        left -= 1
    while world.get(right + 1, y) == AIR and right - x < 100:
        right += 1
    return right - left + 1


def _mucus_drip(world: World) -> None:
    """A clump of mucus clinging to a ceiling; it oozes down slowly."""
    spot = _random_air(world, SPAWN_FLOOR + 20)
    if spot is None:
        return
    x, y = spot
    while y > 0 and world.get(x, y - 1) == AIR:
        y -= 1
    if _in_spawn_zone(world, x, y) or KIND[world.get(x, y - 1)] != SOLID:
        return
    radius = world.rng.randint(2, 4)
    for dy in range(radius + 1):
        for dx in range(-radius + dy, radius - dy + 1):
            if world.get(x + dx, y + dy) == AIR:
                world.set_cell(x + dx, y + dy, mat.MUCUS)


def _growth_nest(world: World) -> None:
    """Embed a growth colony into a flesh wall next to open space."""
    spot = _random_air(world, SPAWN_FLOOR + 20)
    if spot is None:
        return
    x, y = spot
    floor = _floor_y(world, x, y)
    r = world.rng.randint(6, 11)
    for dx, dy in disc_offsets(r):
        if world.get(x + dx, floor + dy) in (mat.FLESH, mat.BLOOD):
            world.set_cell(x + dx, floor + dy, mat.GROWTH)


def _enamel_vein(world: World) -> None:
    """A winding vein of tooth enamel through solid wall (never into open space)."""
    rng = world.rng
    for _attempt in range(30):
        x = rng.randint(30, world.width - 30)
        y = rng.randint(SPAWN_FLOOR + 30, world.height - 30)
        if world.get(x, y) in (mat.FLESH, mat.BONE) and not _in_spawn_zone(world, x, y):
            break
    else:
        return
    angle = rng.uniform(0, 2 * math.pi)
    for _step in range(rng.randint(8, 26)):
        r = rng.randint(2, 4)
        for dx, dy in disc_offsets(r):
            if world.get(x + dx, y + dy) in (mat.FLESH, mat.BONE, mat.SINEW):
                world.set_cell(x + dx, y + dy, mat.ENAMEL)
        angle += rng.uniform(-0.6, 0.6)
        x += round(math.cos(angle) * 3)
        y += round(math.sin(angle) * 3)


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
        # A torn gap so the bridge never seals a shaft the player must pass.
        gap_start = left + rng.randint(span // 5, max(span // 5, span - BRIDGE_GAP - span // 5))
        for xx in range(left, right + 1):
            if gap_start <= xx < gap_start + BRIDGE_GAP:
                continue
            t = (xx - left) / max(1, span - 1)
            yy = y + int(sag * math.sin(math.pi * t))
            for k in range(thickness):
                if world.get(xx, yy + k) == AIR:
                    world.set_cell(xx, yy + k, mat.SINEW)
        return


SANCTUM_CENTRE = (640, 300)
SANCTUM_RX, SANCTUM_RY = 280, 92


@dataclass(frozen=True)
class SanctumLayout:
    """Where things are in the sanctum between two depths."""

    spawn: tuple[int, int]  # player top-left
    exit: tuple[int, int]
    shop: tuple[tuple[int, int], ...]  # item positions on pedestals
    altar: tuple[tuple[int, int], ...]  # perk orb positions


def generate_sanctum(world: World) -> SanctumLayout:
    """A safe, sealed chamber: bedrock shell, flesh lining, bone floor."""
    world.reset(BEDROCK)
    cx, cy = SANCTUM_CENTRE
    _carve_oval_material(world, cx, cy, SANCTUM_RX + 6, SANCTUM_RY + 6, mat.FLESH)
    _carve_oval(world, cx, cy, SANCTUM_RX, SANCTUM_RY)
    floor = cy + 40
    w = world.width
    for y in range(floor, cy + SANCTUM_RY):
        row = y * w
        for x in range(cx - SANCTUM_RX, cx + SANCTUM_RX):
            if world.grid[row + x] == AIR:
                world.grid[row + x] = mat.BONE
    shop = []
    for k in range(5):
        x = cx - 150 + k * 60
        for py in range(floor - 4, floor):  # pedestal
            row = py * w
            world.grid[row + x - 4 : row + x + 4] = bytes([mat.BONE]) * 8
        shop.append((x, floor - 12))
    altar_floor = floor - 46
    for py in range(altar_floor, altar_floor + 4):
        row = py * w
        world.grid[row + cx - 50 : row + cx + 50] = bytes([mat.BONE]) * 100
    altar = tuple((cx + dx, altar_floor - 10) for dx in (-34, 0, 34))
    world.wake_all()
    return SanctumLayout(
        spawn=(cx - SANCTUM_RX + 40, floor - PLAYER_HEIGHT),
        exit=(cx + SANCTUM_RX - 40, floor - 14),
        shop=tuple(shop),
        altar=altar,
    )


def _carve_oval_material(world: World, cx: int, cy: int, rx: int, ry: int, material: int) -> None:
    w = world.width
    for dy in range(-ry, ry):
        half = int(rx * math.sqrt(max(0.0, 1 - (dy / ry) ** 2)))
        row = (cy + dy) * w
        world.grid[row + cx - half : row + cx + half] = bytes([material]) * (2 * half)
