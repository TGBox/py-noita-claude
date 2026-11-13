"""Contract V18: the workshop hub and its 12 stations (Card E01)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World

WORKSHOP_SIZE: tuple[int, int] = (640, 360)


@dataclass(frozen=True)
class Station:
    key: str
    name: str
    rect: tuple[int, int, int, int]
    prompt_de: str

    @property
    def sprite_key(self) -> str:
        return self.key


@dataclass(frozen=True)
class WorkshopLayout:
    width: int
    height: int
    spawn: tuple[int, int]
    klonita_pos: tuple[int, int]
    trader_slots: tuple[tuple[int, int], tuple[int, int]]
    target_dummy_pos: tuple[int, int]
    stations: dict[str, Station]


STATIONS: dict[str, Station] = {
    "ws_couch": Station(
        "ws_couch",
        "Klonitas Couch",
        (40, 192, 80, 210),
        "[E] Mit Klonita sprechen / ausruhen",
    ),
    "ws_liege": Station(
        "ws_liege",
        "Experimentierliege",
        (90, 186, 138, 210),
        "[E] Experimentierliege benutzen",
    ),
    "ws_fabrikator": Station(
        "ws_fabrikator",
        "Fabrikator",
        (148, 170, 188, 210),
        "[E] Fabrikator benutzen",
    ),
    "ws_werkbank": Station(
        "ws_werkbank",
        "Werkbank",
        (198, 182, 246, 210),
        "[E] Werkbank öffnen",
    ),
    "ws_haendler": Station(
        "ws_haendler",
        "Händlerplatz",
        (256, 178, 328, 210),
        "[E] Händler ansprechen",
    ),
    "ws_zapfhahn": Station(
        "ws_zapfhahn",
        "Schnapszapfanlage",
        (338, 186, 354, 210),
        "[E] Fluxschnaps zapfen (10 Gold)",
    ),
    "ws_well": Station(
        "ws_well",
        "Flaschen-Brunnen",
        (364, 192, 380, 210),
        "[E] Wasser auffüllen (kostenlos)",
    ),
    "ws_automat": Station(
        "ws_automat",
        "Physik-o-Mat",
        (390, 174, 414, 210),
        "[E] Physik-o-Mat starten (30 Gold)",
    ),
    "ws_schiessstand": Station(
        "ws_schiessstand",
        "Schießstand",
        (424, 186, 488, 210),
        "[E] Schießstand starten (20 Gold)",
    ),
    "ws_archiv": Station(
        "ws_archiv",
        "Archivschrank",
        (498, 178, 522, 210),
        "[E] Archiv öffnen",
    ),
    "ws_shredder": Station(
        "ws_shredder",
        "Akten-Schredder",
        (532, 190, 548, 210),
        "[E] Akten-Schredder benutzen",
    ),
    "ws_portal": Station(
        "ws_portal",
        "Portalrahmen",
        (558, 162, 598, 210),
        "[E] Portal aktivieren",
    ),
}

STATION_ALIASES: dict[str, str] = {
    "ws_workbench": "ws_werkbank",
    "ws_fabricator": "ws_fabrikator",
    "ws_trader": "ws_haendler",
    "ws_physik_o_mat": "ws_automat",
    "ws_archive": "ws_archiv",
}


def generate_workshop(world: World) -> WorkshopLayout:
    """Build the 640x360 workshop in world and return its layout."""
    from src import materials as mat

    id_air = mat.AIR
    id_rock = mat.MAT_ID.get("rock", 2)
    id_water = mat.MAT_ID.get("water", 6)

    # Clear everything with air
    world.reset(id_air)

    # Floor from y = 210 to world.height
    world.fill_rect(0, 210, world.width, world.height, id_rock)

    # Outer brick walls / ceiling
    world.fill_rect(0, 0, world.width, 10, id_rock)
    world.fill_rect(0, 0, 10, world.height, id_rock)
    world.fill_rect(world.width - 10, 0, world.width, world.height, id_rock)

    # Water basin under ws_well: rect (364, 192, 380, 210), basin in floor below it
    world.fill_rect(364, 210, 380, 222, id_water)

    # Ensure air at spawn (300, 200)
    world.fill_disc(300, 200, 10, id_air)

    stations_dict: dict[str, Station] = dict(STATIONS)
    for alias, canon in STATION_ALIASES.items():
        if canon in STATIONS:
            stations_dict[alias] = STATIONS[canon]

    return WorkshopLayout(
        width=world.width,
        height=world.height,
        spawn=(300, 200),
        klonita_pos=(64, 190),
        trader_slots=((276, 194), (316, 194)),
        target_dummy_pos=(484, 196),
        stations=stations_dict,
    )


def _rect_distance(rect: tuple[int, int, int, int], px: int, py: int) -> float:
    x0, y0, x1, y1 = rect
    dx = max(0, x0 - px, px - x1)
    dy = max(0, y0 - py, py - y1)
    return math.hypot(dx, dy)


def station_at(
    layout: WorkshopLayout,
    cell_x: int,
    cell_y: int,
    radius: int = 10,
) -> Station | None:
    """Return the nearest station whose rect is within radius cells of (cell_x, cell_y)."""
    best_station: Station | None = None
    best_dist = float("inf")

    # Check distinct canonical stations in STATIONS
    for st in STATIONS.values():
        dist = _rect_distance(st.rect, cell_x, cell_y)
        if dist <= radius and dist < best_dist:
            best_dist = dist
            best_station = st

    return best_station
