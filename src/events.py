"""Contract V10: Secondary universe events (Cards D11, D12)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class EventSpec:
    key: str
    name: str
    description: str
    duration: float
    interval: float = 90.0
    preferred_universes: tuple[str, ...] = ()


EVENTS: dict[str, EventSpec] = {
    "verdauung": EventSpec(
        "verdauung",
        "Verdauungswelle",
        "Magensäure steigt auf und Wände ziehen sich zusammen.",
        duration=20.0,
        interval=90.0,
        preferred_universes=("fleischwelt",),
    ),
    "pruefung": EventSpec(
        "pruefung",
        "Unangekündigte Steuerprüfung",
        "Streifen-Agenten prüfen alle Anträge auf Vollständigkeit.",
        duration=25.0,
        interval=90.0,
        preferred_universes=("aktenhalde",),
    ),
    "brauseregen": EventSpec(
        "brauseregen",
        "Brauseperlenregen",
        "Bunte Brauseperlen fallen vom Himmel und explodieren prickelnd.",
        duration=20.0,
        interval=90.0,
        preferred_universes=("glibbria",),
    ),
    "riesenschritt": EventSpec(
        "riesenschritt",
        "Schritt eines Riesen",
        "Ein gigantischer Fuß erschüttert den Boden und wirbelt Krümel auf.",
        duration=15.0,
        interval=90.0,
        preferred_universes=("kruemelreich",),
    ),
    "bass_drop": EventSpec(
        "bass_drop",
        "Der Bass Drop",
        "Extremer Subbass lässt die Pilze im Takt pulsieren.",
        duration=20.0,
        interval=90.0,
        preferred_universes=("sporenklub",),
    ),
    "glockenschlag": EventSpec(
        "glockenschlag",
        "Glockenschlag zur Geisterstunde",
        "Tiefseeglocken hallen durch das Wasser und wecken Ruhende.",
        duration=20.0,
        interval=90.0,
        preferred_universes=("abtei",),
    ),
}


@dataclass
class Event:
    spec: EventSpec
    remaining: float
    active: bool = True
    _tick_acc: float = 0.0

    def on_start(self, run: Run) -> None:
        """Trigger initial event effects and emit 'event_start'."""
        self.active = True
        run.emit("event_start", key=self.spec.key, name=self.spec.name)

    def tick(self, dt: float, run: Run) -> None:
        """Advance event timer and periodic effects."""
        if not self.active:
            return
        self.remaining -= dt
        self._tick_acc += dt
        if self.remaining <= 0.0:
            self.on_end(run)

    def on_end(self, run: Run) -> None:
        """Clean up event effects, mark active=False, and emit 'event_end'."""
        self.active = False
        run.emit("event_end", key=self.spec.key)

    def to_data(self) -> dict[str, object]:
        """Serialize event state to a JSON-compatible dict."""
        return {
            "key": self.spec.key,
            "remaining": self.remaining,
            "active": self.active,
            "_tick_acc": self._tick_acc,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Event | None:
        """Restore Event from serialized dict."""
        if not data:
            return None
        key = str(data.get("key", ""))
        spec = EVENTS.get(key)
        if spec is None:
            return None
        remaining = float(data.get("remaining", spec.duration))
        active = bool(data.get("active", True))
        acc = float(data.get("_tick_acc", 0.0))
        return cls(spec=spec, remaining=remaining, active=active, _tick_acc=acc)


def pick_event(universe_key: str, depth: int, rng: random.Random) -> Event | None:
    """Roll (35% chance) and return a secondary Event for universe_key, or None."""
    if rng.random() > 0.35:
        return None
    matches = [e for e in EVENTS.values() if universe_key in e.preferred_universes]
    spec = rng.choice(matches) if matches else rng.choice(list(EVENTS.values()))
    return Event(spec=spec, remaining=spec.duration)
