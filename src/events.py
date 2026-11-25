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

EXPANSION_EVENTS: dict[str, EventSpec] = {
    # 6 Expansion Universe Main Events (Phase J01-J06)
    "magnetsturm": EventSpec(
        "magnetsturm",
        "Magnetsturm",
        "Metallpartikel fegen 15 Sekunden lang quer über die Halde.",
        duration=15.0,
        interval=90.0,
        preferred_universes=("schrott",),
    ),
    "karamell_ausbruch": EventSpec(
        "karamell_ausbruch",
        "Karamell-Geysir",
        "Heiße Karamell-Fontänen schießen aus dem Biskuitboden empor.",
        duration=15.0,
        interval=80.0,
        preferred_universes=("kuchen",),
    ),
    "kurzschluss": EventSpec(
        "kurzschluss",
        "Kurzschluss",
        "Blitz-Kaskaden zucken quer durch die blanken Kupferleitungen.",
        duration=12.0,
        interval=70.0,
        preferred_universes=("spule",),
    ),
    "zeitsprung": EventSpec(
        "zeitsprung",
        "Zeitsprung",
        "Alle Projektile gefrieren zwei Sekunden lang im Ticktakt.",
        duration=10.0,
        interval=90.0,
        preferred_universes=("uhrwerkwueste",),
    ),
    "wallendes_kochen": EventSpec(
        "wallendes_kochen",
        "Wallendes Kochen",
        "Aufsteigende Dampfblasen reißen alles in der Brühe nach oben.",
        duration=15.0,
        interval=75.0,
        preferred_universes=("suppenmeer",),
    ),
    "freie_fahrt": EventSpec(
        "freie_fahrt",
        "Freie Fahrt",
        "Sirenen heulen auf und leere Achterbahn-Loren rasen los.",
        duration=15.0,
        interval=90.0,
        preferred_universes=("freizeitpark",),
    ),
    # 8 Cross-Universe Secondary Events (Phase J07)
    "lieferung": EventSpec(
        "lieferung",
        "Kurier-Lieferung",
        "Eine Behörden-Drohne wirft eine Notkiste mit Vorräten ab.",
        duration=10.0,
        interval=120.0,
    ),
    "pilz_schwarm": EventSpec(
        "pilz_schwarm",
        "Pilzschwarm",
        "Harmlose Leuchtsporen treiben in bunten Schwaden vorbei.",
        duration=15.0,
        interval=110.0,
    ),
    "gold_regen": EventSpec(
        "gold_regen",
        "Goldregen",
        "Winzige Goldsplitter regnen aus einem dimensionsweiten Riss.",
        duration=12.0,
        interval=130.0,
    ),
    "stromausfall": EventSpec(
        "stromausfall",
        "Stromausfall",
        "Die Beleuchtung flackert für kurze Zeit auf Minimalwert.",
        duration=14.0,
        interval=120.0,
    ),
    "flutwelle": EventSpec(
        "flutwelle",
        "Flutwelle",
        "Eine Welle frischer Flüssigkeit schwappt durch die unteren Gänge.",
        duration=12.0,
        interval=115.0,
    ),
    "zucker_rausch": EventSpec(
        "zucker_rausch",
        "Zuckerrausch",
        "Temporär erhöhtes Bewegungstempo für alle Wesen im Sektor.",
        duration=15.0,
        interval=105.0,
    ),
    "wanderzirkus": EventSpec(
        "wanderzirkus",
        "Wanderzirkus",
        "Konfetti-Geschosse prallen verspielt durch die Höhle.",
        duration=15.0,
        interval=125.0,
    ),
    "ameisen_karawane": EventSpec(
        "ameisen_karawane",
        "Ameisen-Karawane",
        "Friedliche Arbeiterameisen ziehen mit Krümeln vorbei.",
        duration=18.0,
        interval=120.0,
    ),
}

SECONDARY_EVENT_KEYS: tuple[str, ...] = (
    "lieferung",
    "pilz_schwarm",
    "gold_regen",
    "stromausfall",
    "flutwelle",
    "zucker_rausch",
    "wanderzirkus",
    "ameisen_karawane",
)
PHASE3_EVENTS: dict[str, EventSpec] = {
    "verdauungsschub": EventSpec("verdauungsschub", "Verdauungsschub", "Magenwellen schieben alle Körper sanft zur Seite.", 20.0, 90.0),
    "konfetti_hagel": EventSpec("konfetti_hagel", "Konfetti-Hagel", "Klebriger Pastell-Regen füllt Zuckerschilde auf.", 22.0, 95.0),
    "gruppen_telefonat": EventSpec("gruppen_telefonat", "Klon-Telefonkonferenz", "Alle Klonenbergs diskutieren gleichzeitig ihren Urlaub.", 25.0, 100.0),
    "talent_scouting": EventSpec("talent_scouting", "Talent-Casting", "Ein Scheinwerfer sucht den kreativsten Treffer.", 18.0, 85.0),
    "mahnungswelle": EventSpec("mahnungswelle", "Mahnungs-Welle", "Rote Durchschläge regnen von der Decke.", 20.0, 90.0),
    "meeting_marathons": EventSpec("meeting_marathons", "Pflicht-Meeting", "Alle Gegner schauen nervös auf imaginäre Uhren.", 24.0, 100.0),
    "wasserrohr_wunder": EventSpec("wasserrohr_wunder", "Heilquell-Flutung", "Glänzendes Quellwasser sprudelt aus den Keramikfugen.", 20.0, 95.0),
    "speicherleck": EventSpec("speicherleck", "Speicherleck", "Texturen flimmern und spalten lose Voxel ab.", 18.0, 90.0),
    "rundschreiben_alarm": EventSpec("rundschreiben_alarm", "Rundschreiben Eil-A", "Der gesamte Schwarm sortiert gleichzeitig Eilanträge.", 22.0, 100.0),
    "happy_hour": EventSpec("happy_hour", "Resort Happy-Hour", "Schirmchendrinks verzögern jede Konsequenz.", 25.0, 110.0),
    "messproblem": EventSpec("messproblem", "Beobachtungs-Kollaps", "Wahrscheinlichkeitswellen kippen kurzzeitig um.", 16.0, 85.0),
    "stille_stunde": EventSpec("stille_stunde", "Konterbrause-Stunde", "Gedämpftes Licht lindert den kosmischen Brumm-Schädel.", 22.0, 95.0),
    "event_falsche_freunde": EventSpec("event_falsche_freunde", "Falsche Freunde im Labor", "Ein formloser Gestaltwandler imitiert einen alten Bekannten.", 45.0, 140.0),
}
ALL_EVENTS: dict[str, EventSpec] = {**EVENTS, **EXPANSION_EVENTS, **PHASE3_EVENTS}


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
        spec = ALL_EVENTS.get(key)
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
