"""Contract V18: the workshop hub and its 12 stations (Card E01)."""

from __future__ import annotations

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


STATIONS: dict[str, Station] = {}

STATION_ALIASES: dict[str, str] = {
    "ws_workbench": "ws_werkbank",
    "ws_fabricator": "ws_fabrikator",
    "ws_trader": "ws_haendler",
    "ws_physik_o_mat": "ws_automat",
    "ws_archive": "ws_archiv",
}


def generate_workshop(world: World) -> WorkshopLayout:
    """Build the 640x360 workshop in world and return its layout."""
    raise NotImplementedError("Card E01")


def station_at(
    layout: WorkshopLayout,
    cell_x: int,
    cell_y: int,
    radius: int = 10,
) -> Station | None:
    """Return the nearest station whose rect is within radius cells of (cell_x, cell_y)."""
    raise NotImplementedError("Card E01")
