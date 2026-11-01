"""Contract V10: Secondary universe events (Cards D11, D12)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class EventSpec:
    key: str
    name: str
    description: str
    duration: float
    preferred_universes: tuple[str, ...] = ()


@dataclass
class Event:
    spec: EventSpec
    remaining: float
    active: bool = True
    _tick_acc: float = 0.0

    def on_start(self, run: Run) -> None:
        """Trigger initial event effects and emit 'event_start'."""
        raise NotImplementedError("Card D11")

    def tick(self, dt: float, run: Run) -> None:
        """Advance event timer and periodic effects."""
        raise NotImplementedError("Card D11")

    def on_end(self, run: Run) -> None:
        """Clean up event effects, mark active=False, and emit 'event_end'."""
        raise NotImplementedError("Card D11")

    def to_data(self) -> dict[str, object]:
        """Serialize event state to a JSON-compatible dict."""
        raise NotImplementedError("Card D11")

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Event | None:
        """Restore Event from serialized dict."""
        raise NotImplementedError("Card D11")


EVENTS: dict[str, EventSpec] = {}


def pick_event(universe_key: str, depth: int, rng: random.Random) -> Event | None:
    """Roll (35% chance) and return a secondary Event for universe_key, or None."""
    raise NotImplementedError("Card D11")

