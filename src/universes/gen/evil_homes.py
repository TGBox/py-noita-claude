"""Contract V17 section 2: home worlds of the three evil selves (Card F18).

Every home is one 1280x720 hall with its own material set and its own arena mechanic
(``Run`` drives the mechanics; here only the terrain and the prop positions are built):

* ``boese_kaiserin`` - a throne hall of gold: slippery ``goldboden`` and the throne that
  becomes a cannon in her last phase (prop ``"thron"``).
* ``boese_gute`` - a cathedral of light: ``lichtstein`` walls, pockets of ``heiliges_licht``.
* ``boese_omega`` - a factory hall: ``foerderband`` strips on the floor, ``stahl`` walls and
  four presses hanging from the ceiling (props ``"presse"``).
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src import materials as mat
from src.world import BORDER
from src.worldgen import Level

if TYPE_CHECKING:
    from ...world import World

HOME_SIZE: tuple[int, int] = (1280, 720)
HALL_MARGIN = 80  # solid mass around the hall
FLOOR_Y = 640  # the hall floor (top edge)
PRESS_COUNT = 4
PRESS_WIDTH = 16
PRESS_HEIGHT = 40
PRESSES_X = (330, 560, 790, 1020)  # left edges of the four presses
BELT_STRIPS = ((200, 480), (560, 740), (820, 1080))  # conveyor belts on the floor
BELT_DIRECTIONS = (1, -1, 1)  # ... and the way each one runs
THRONE = (1096, 40, 36)  # x, width, height of the throne on the dais
DAIS_STEPS = 3
PLAYER_SIZE = (10, 18)  # keeps the spawn above the floor, whatever the body size

# arena mechanics (driven by Run, Card F19)
CANNON_INTERVAL = 1.2  # the throne shoots this often in the Empress's last phase
CONVERSION_TIME = 10.0  # Klonita on the Good One's side (harmless)
BELT_SPEED = 40.0  # px/s a body on a conveyor belt is pushed
PRESS_INTERVAL = 3.0  # seconds between two stamps of Omega's presses
PRESS_HOLD = 0.35  # how long a stamp stays down
PRESS_DAMAGE = 30.0

HOME_NAMES_DE = {
    "boese_kaiserin": "Thronsaal aus Gold",
    "boese_gute": "Kathedrale aus Licht",
    "boese_omega": "Fabrikhalle",
}


def belt_direction(x: int) -> int:
    """Which way the conveyor belt under world column ``x`` runs (0: no belt there)."""
    for (bx0, bx1), direction in zip(BELT_STRIPS, BELT_DIRECTIONS):
        if bx0 <= x < bx1:
            return direction
    return 0

Rect = tuple[int, int, int, int]


def _hall(world: World) -> Rect:
    """Interior of the hall: everything but a margin of solid mass."""
    x0, y0 = HALL_MARGIN, HALL_MARGIN
    x1, y1 = world.width - HALL_MARGIN, min(FLOOR_Y, world.height - HALL_MARGIN)
    return (x0, y0, x1, y1)


def _id(key: str) -> int:
    return mat.id_of(key, mat.ROCK)


def _pillars(world: World, hall: Rect, material: int, xs: tuple[int, ...], width: int,
             gap_y: int) -> None:
    """Pillars from floor to ceiling with a gap to pass at mid height."""
    x0, y0, x1, y1 = hall
    for px in xs:
        world.fill_rect(px, y0, px + width, gap_y - 30, material)
        world.fill_rect(px, gap_y + 30, px + width, y1, material)


def _ledges(world: World, hall: Rect, material: int, rng: random.Random, count: int,
            avoid: tuple[tuple[int, int], ...] = ()) -> None:
    """A few ledges to jump on, never over the spawn, the centre or an ``avoid`` column."""
    x0, y0, x1, y1 = hall
    for i in range(count):
        w = rng.randint(40, 80)
        x = x0 + 160 + (i * (x1 - x0 - 320)) // max(1, count - 1) - w // 2
        y = y1 - rng.choice((90, 150, 210))
        for ax0, ax1 in avoid:
            if x < ax1 + 8 and x + w > ax0 - 8:
                x = ax1 + 8 if x + w // 2 >= (ax0 + ax1) // 2 else ax0 - 8 - w
        world.fill_rect(x, y, x + w, y + 5, material)


def _level(spawn: tuple[int, int], hall: Rect, species: str, region: str,
           props: list[tuple[str, int, int]]) -> Level:
    x0, y0, x1, y1 = hall
    return Level(
        spawn, (-999, -999), arena=((x0 + x1) // 2, (y0 + y1) // 2), universe_key=species,
        boss_arena=hall, regions=[(region, hall)], destructible_props=props,
    )  # fmt: skip


def _throne_hall(world: World, rng: random.Random) -> Level:
    gold = _id("goldboden")
    world.reset(gold)
    hall = _hall(world)
    x0, y0, x1, y1 = hall
    world.fill_rect(x0, y0, x1, y1, mat.AIR)
    # the dais with its steps, the throne on top
    step_h, step_w = 14, 60
    for i in range(DAIS_STEPS):
        top = y1 - step_h * (i + 1)
        world.fill_rect(x1 - 300 + step_w * i, top, x1, y1, gold)
    dais_top = y1 - step_h * DAIS_STEPS
    tx, tw, th = THRONE
    world.fill_rect(tx, dais_top - th, tx + tw, dais_top, gold)
    _pillars(world, hall, gold, (380, 640, 900), 18, (y0 + y1) // 2)
    _ledges(world, hall, gold, rng, 4)
    spawn = (x0 + 40, y1 - PLAYER_SIZE[1] - 1)
    return _level(spawn, hall, "boese_kaiserin", "thronsaal",
                  [("thron", tx + tw // 2, dais_top - th)])


def _cathedral(world: World, rng: random.Random) -> Level:
    stone, light = _id("lichtstein"), _id("heiliges_licht")
    world.reset(stone)
    hall = _hall(world)
    x0, y0, x1, y1 = hall
    world.fill_rect(x0, y0, x1, y1, mat.AIR)
    # a pointed vault: the ceiling rises towards the middle
    for x in range(x0, x1):
        rise = 60 - abs(x - (x0 + x1) // 2) * 60 // max(1, (x1 - x0) // 2)
        world.fill_rect(x, y0 - 1, x + 1, y0 + max(0, 60 - rise), stone)
    _pillars(world, hall, stone, (300, 520, 760, 980), 16, (y0 + y1) // 2 + 40)
    _ledges(world, hall, stone, rng, 5)
    # pockets of holy light glow under the vault, far from the spawn
    for i in range(5):
        cx = x0 + 300 + i * 160
        world.fill_rect(cx, y0 + 70, cx + 28, y0 + 84, light)
    spawn = (x0 + 40, y1 - PLAYER_SIZE[1] - 1)
    return _level(spawn, hall, "boese_gute", "kathedrale", [])


def _factory(world: World, rng: random.Random) -> Level:
    steel, belt = _id("stahl"), _id("foerderband")
    world.reset(steel)
    hall = _hall(world)
    x0, y0, x1, y1 = hall
    world.fill_rect(x0, y0, x1, y1, mat.AIR)
    for (bx0, bx1) in BELT_STRIPS:  # conveyor belts flush with the floor
        world.fill_rect(bx0, y1 - 4, bx1, y1, belt)
    # four presses hang from the ceiling; their stamp strip runs down to the floor
    props = []
    for px in PRESSES_X:
        world.fill_rect(px - 6, y0, px + PRESS_WIDTH + 6, y0 + 12, steel)  # mounting
        world.fill_rect(px, y0 + 12, px + PRESS_WIDTH, y0 + 12 + PRESS_HEIGHT, steel)
        props.append(("presse", px, y0 + 12 + PRESS_HEIGHT))
    strips = tuple((px, px + PRESS_WIDTH) for px in PRESSES_X)
    _ledges(world, hall, steel, rng, 4, avoid=strips)
    spawn = (x0 + 40, y1 - PLAYER_SIZE[1] - 1)
    return _level(spawn, hall, "boese_omega", "fabrikhalle", props)


_BUILDERS = {
    "boese_kaiserin": _throne_hall,
    "boese_gute": _cathedral,
    "boese_omega": _factory,
}


def generate_evil_home(world: World, species: str, seed: int) -> Level:
    """Build the home world of ``species`` (one of EVIL_SELVES); activates its material set."""
    if species not in _BUILDERS:
        raise ValueError(f"{species} has no home world")
    if mat.ACTIVE is None or mat.ACTIVE.key != species:
        mat.activate_key(species)
    rng = random.Random(seed * 7 + len(species))
    level = _BUILDERS[species](world, rng)
    x0, y0, x1, y1 = _hall(world)
    assert BORDER < x0 and y1 < world.height - BORDER
    world.wake_all()
    return level
