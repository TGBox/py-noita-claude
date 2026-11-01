# V9–V10, V13–V14 – Universum-Generatoren, `Level`, Ereignisse, Herausforderungen & Bot

Verbindliche Schnittstellen für `src/worldgen.py`, `src/universes/gen/`, `src/events.py`, `src/challenges.py` und `src/bot.py`. Alle Module sind **headless**.

---

## V9 Universum-Generator (`src/universes/gen/` & `src/worldgen.py`)

### 1. Erweiterung von `Level` in `src/worldgen.py`

```python
@dataclass(frozen=True)
class Level:
    spawn: tuple[int, int]                                         # Spieler-Start (oben links)
    exit: tuple[int, int] = (0, 0)                                 # Mittelpunkt des Ankerpunkts
    arena: tuple[int, int] | None = None                           # Mittelpunkt der Zwischengegner-Arena
    secret: tuple[int, int] | None = None                          # Kammer mit Erinnerungssplitter / Urauge
    vault: tuple[int, int] | None = None                           # Schatzkammer
    exit_point: tuple[int, int] = (0, 0)                           # Kanonischer Exit-Koordinaten-Alias
    universe_key: str = "fleischwelt"                              # Schlüssel des MVP-Universums
    mid_boss_arena: tuple[int, int, int, int] = (0, 0, 0, 0)       # (x0, y0, x1, y1) Unter-Zwischenboss-Arena
    boss_arena: tuple[int, int, int, int] = (0, 0, 0, 0)           # (x0, y0, x1, y1) Haupt-Zwischengegner-Arena
    trader_nook: tuple[int, int, int, int] | None = None           # (x0, y0, x1, y1) Händler-Nische
    challenge_shrine: tuple[int, int, int, int] | None = None      # (x0, y0, x1, y1) Herausforderungs-Schrein
    regions: list[tuple[str, tuple[int, int, int, int]]] = field(default_factory=list)  # [(region_key, (x0, y0, x1, y1)), ...]
    destructible_props: list[tuple[str, int, int]] = field(default_factory=list)        # [(prop_key, x, y), ...]
```

- **Rechteck-Konvention (`(x0, y0, x1, y1)`):** Alle Rechtecke im gesamten Projekt haben `0 <= x0 < x1 <= width` und `0 <= y0 < y1 <= height`.
- **Abwärtskompatibilität:** Bestehende Aufrufe `Level(spawn, exit_point, arena, secret, vault)` funktionieren dank der Default-Parameter für alle neuen Felder unverändert weiter.

### 2. Registry in `src/universes/gen/__init__.py`

```python
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
    from ...worldgen import Level
    from ..model import Universe

GENERATORS: dict[str, Callable[[World, Universe, int, int], Level]] = {}


def generate_universe(world: World, universe: Universe, depth: int, seed: int) -> Level:
    """Generate a universe level using the registered generator for universe.key."""
    ...
```

- `GENERATORS` enthält für jedes der **6 MVP-Universen** (`"fleischwelt"`, `"aktenhalde"`, `"glibbria"`, `"kruemelreich"`, `"sporenklub"`, `"abtei"`) einen eigenen Generator.

### 3. Gemeinsame Bausteine in `src/universes/gen/common.py`

```python
def region_bands(
    width: int,
    height: int,
    topology: str,
) -> list[tuple[int, int, int, int]]:
    """Return 3 (x0, y0, x1, y1) bounding boxes for topology
    ('vertical_3', 'horizontal_3', 'vertical', 'horizontal', 'top_split', 'islands')."""
    ...

def carve_room(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    wall_mat: int | None = None,
) -> tuple[int, int, int, int]: ...

def carve_tunnel(
    world: World,
    start: tuple[int, int],
    end: tuple[int, int],
    radius: int = 4,
) -> None: ...

def fill_basin(
    world: World,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    liquid_mat: int,
) -> None: ...

def place_trader_nook(
    world: World,
    rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[int, int, int, int]: ...

def place_challenge_shrine(
    world: World,
    rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[int, int, int, int]: ...

def place_boss_arenas(
    world: World,
    mid_rect: tuple[int, int, int, int],
    boss_rect: tuple[int, int, int, int],
    rng: random.Random,
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]: ...

def scatter_props(
    world: World,
    rect: tuple[int, int, int, int],
    prop_keys: tuple[str, ...],
    count: int,
    rng: random.Random,
) -> list[tuple[str, int, int]]: ...
```

---

## V10 Universums-Ereignisse (`src/events.py`)

```python
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

    def on_start(self, run: Run) -> None: ...
    def tick(self, dt: float, run: Run) -> None: ...
    def on_end(self, run: Run) -> None: ...
    def to_data(self) -> dict[str, object]: ...
    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Event | None: ...


EVENTS: dict[str, EventSpec] = {...}


def pick_event(universe_key: str, depth: int, rng: random.Random) -> Event | None:
    """Roll (35% chance) and return an Event for universe_key, or None."""
    ...
```

### Kanonische Ereignisse in `EVENTS` (6 Bibel-Hauptevents + 3 Sekundärereignisse)

| `key` | `name` | `preferred_universes` | Wirkung (`on_start` / `tick` / `on_end`) |
| --- | --- | --- | --- |
| `"verdauung"` | `"Verdauungsschub"` | `("fleischwelt",)` | Magensäure sprudelt in Becken auf, Wände kontrahieren leicht |
| `"pruefung"` | `"Steuerprüfung"` | `("aktenhalde",)` | Stempeldrohne erscheint, Stempelfarbe/Formulare regnen herab |
| `"brauseregen"` | `"Brauseregen"` | `("glibbria",)` | Brausesirup regnet von oben, Sprungkraft erhöht |
| `"riesenschritt"` | `"Riesenschritt"` | `("kruemelreich",)` | Erdstoß schüttelt Krümel und Zucker von der Decke |
| `"bass_drop"` | `"Bass-Drop"` | `("sporenklub",)` | Druckwelle alle paar Takte, Sporenwirbel leuchten |
| `"glockenschlag"` | `"Glockenschlag"` | `("abtei",)` | Schallwelle im Wasser, lose Steine bröckeln |
| `"schrottregen"` | `"Schrott-Schauer"` | `("aktenhalde",)` | Metallteile und Büroklammern regnen herab |
| `"zuckersturm"` | `"Puderzucker-Böe"` | `("kruemelreich",)` | Puderzucker-Wirbel mit erhöhter Beweglichkeit |
| `"sporenregen"` | `"Leuchtsporen-Nebel"` | `("sporenklub",)` | Heilender/leuchtender Sporenteppich |

---

## V13 Optionale Prüfungen (`src/challenges.py`)

```python
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run


@dataclass(frozen=True)
class ChallengeSpec:
    key: str
    name: str
    description: str
    reward_gold: int
    reward_samples: int = 2
    reward_perk: bool = False
    time_limit: float = 0.0


@dataclass
class Challenge:
    spec: ChallengeSpec
    active: bool = False
    completed: bool = False
    failed: bool = False
    reward_paid: bool = False
    progress: int = 0
    elapsed: float = 0.0

    def activate(self) -> None: ...
    def on_event(self, name: str, data: dict[str, object], run: Run) -> None: ...
    def tick(self, dt: float, run: Run) -> None: ...
    def pay_reward(self, run: Run) -> None: ...
    def to_data(self) -> dict[str, object]: ...
    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Challenge | None: ...


CHALLENGES: dict[str, ChallengeSpec] = {...}


def pick_challenge(universe_key: str, depth: int, rng: random.Random) -> Challenge:
    """Pick a deterministic Challenge instance for universe_key and depth."""
    ...
```

### Die 6 kanonischen Prüfungs-Schlüssel in `CHALLENGES` (Bibel Kap. 07)

1. `"pacifist"`: *"Pazifistischer Durchgang"* – Ausgang erreichen ohne direkten Spieler-Kill (`"kill"` mit `killer == "player"` lässt die Prüfung scheitern; `"leave_universe"` schließt sie erfolgreich ab).
2. `"no_gold"`: *"Gold-Askese"* – Ausgang erreichen ohne Gold aufzuheben (`"pickup"` mit `kind == "gold"` lässt sie scheitern; `"leave_universe"` schließt sie ab).
3. `"speed_run"`: *"Eilzustellung"* – Ausgang innerhalb von `time_limit` Sekunden erreichen (`tick` prüft Zeitlimit).
4. `"no_damage"`: *"Unversehrt"* – `5` Gegner besiegen oder Ausgang erreichen ohne `"hurt_player"` (`amount > 0`).
5. `"kill_streak"`: *"Kammerjäger-Quote"* – `8` Kreaturen besiegen (`progress >= 8` über `"kill"`-Events).
6. `"dry_feet"`: *"Trockene Stiefel"* – Ausgang erreichen ohne Flüssigkeitsschaden (`"hurt_player"` mit `source == "material"`).

---

## V14 Bot-Lauf (`src/bot.py`, headless)

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BotReport:
    universe_key: str
    seed: int
    ticks: int = 0
    reached_exit: bool = False
    died: bool = False
    kills: int = 0
    gold_collected: int = 0
    samples_collected: int = 0
    stuck_ratio: float = 0.0
    min_hp_ratio: float = 1.0
    errors: list[str] = field(default_factory=list)


def run_bot(
    universe_key: str,
    seed: int = 1,
    max_seconds: float = 120.0,
) -> BotReport:
    """Run deterministic bot in a single MVP universe and return BotReport."""
    ...


def run_full(
    seed: int = 1,
    max_seconds_per_stage: float = 120.0,
) -> list[BotReport]:
    """Run deterministic bot across a 6-universe sequence (RunPlan) and return reports."""
    ...
```
