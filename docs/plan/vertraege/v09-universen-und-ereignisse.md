# V9–V10, V13–V14 – Universum-Generatoren, `Level`, Ereignisse, Herausforderungen & Bot

Verbindliche Schnittstellen für `src/worldgen.py`, `src/universes/gen/`, `src/events.py`, `src/challenges.py` und `src/bot.py`. Alle Module sind **headless**.

---

## V9 Universum-Generator (`src/universes/gen/` & `src/worldgen.py`)

### 1. Erweiterung von `Level` in `src/worldgen.py`

```python
@dataclass(frozen=True)
class Level:
    spawn: tuple[int, int]                                         # Spieler-Start (oben links)
    exit: tuple[int, int]                                          # Mittelpunkt des Ankerpunkts
    arena: tuple[int, int] | None                                  # Mittelpunkt der Zwischengegner-Arena
    secret: tuple[int, int] | None = None                          # Kammer mit Erinnerungssplitter
    vault: tuple[int, int] | None = None                           # Schatzkammer
    life_capsule: tuple[int, int] | None = None                    # Versteckte Lebenskapsel
    crates: tuple[tuple[int, int], ...] = ()                       # Positionen von Fundkisten
    gold_piles: tuple[tuple[int, int], ...] = ()                   # Positionen von Goldhaufen
    regions: dict[str, tuple[int, int, int, int]] = field(default_factory=dict)  # key -> (x0, y0, x1, y1)
    spawns: tuple[tuple[str, int, int, int], ...] = ()             # (creature_key, x, y, group_id)
    challenge: tuple[int, int] | None = None                       # Position des Auftraggebers (V13)
```

- **Wichtig für Rechtecke (`regions`):** Alle Rechtecke im gesamten Projekt (wie `Rect` in `src/world.py`) sind **`(x0, y0, x1, y1)` mit exklusivem Ende** (`0 <= x0 < x1 <= width`, `0 <= y0 < y1 <= height`).
- **Spiegelung in `Run._mirror_level(level: Level) -> Level`:**
  - Punktfelder (`exit`, `arena`, `secret`, `vault`, `life_capsule`, `challenge`, Elemente aus `crates` und `gold_piles`) werden mit `flip(pt)` (`(w - 1 - pt[0], pt[1])`) gespiegelt.
  - `regions`: `(x0, y0, x1, y1)` wird zu `(w - x1, y0, w - x0, y1)`.
  - `spawns`: `(key, x, y, group_id)` wird mit der Breite `SPECIES[key].width` zu `(key, w - x - SPECIES[key].width, y, group_id)` gespiegelt.

### 2. Registry in `src/universes/gen/__init__.py`

```python
from collections.abc import Callable
import random
from src.universes.model import Universe
from src.world import World
from src.worldgen import Level

Generator = Callable[[World, Universe, int, random.Random, bool], Level]
GENERATORS: dict[str, Generator] = {}

def register(key: str) -> Callable[[Generator], Generator]: ...
def generate(world: World, universe: Universe, rank: int, *, boss: bool = False) -> Level:
    """Call GENERATORS[universe.key](world, universe, rank, world.rng, boss)."""
    ...
```

- Fehlt `universe.key` in `GENERATORS`, wirft `generate` einen `KeyError(universe.key)`.

### 3. Gemeinsame Bausteine in `src/universes/gen/common.py`

```python
Rect = tuple[int, int, int, int]  # (x0, y0, x1, y1)

def carve_oval(world: World, cx: int, cy: int, rx: int, ry: int) -> None: ...
def carve_tunnel(world: World, a: tuple[int, int], b: tuple[int, int], radius: int = 11) -> None: ...
def ensure_path(world: World, spawn: tuple[int, int], target: tuple[int, int]) -> int: ...

def split_regions(
    world: World, layout: str, keys: tuple[str, ...]
) -> dict[str, Rect]:
    """Layouts: 'vertical', 'horizontal', 'islands', 'top_split'."""
    ...

def carve_arena(
    world: World, centre: tuple[int, int], rx: int, ry: int, floor_mat: int, wall_mat: int | None = None
) -> Rect: ...

def place_anchor(world: World, region: Rect, rng: random.Random) -> tuple[int, int]: ...
def place_secret(world: World, region: Rect, shell_mat: int, rng: random.Random) -> tuple[int, int]: ...
def place_vault(world: World, region: Rect, shell_mat: int, rng: random.Random) -> tuple[int, int]: ...
def place_life_capsule(world: World, region: Rect, rng: random.Random) -> tuple[int, int]: ...
def place_crates(world: World, count: int, avoid: tuple[int, int], rng: random.Random) -> tuple[tuple[int, int], ...]: ...
def place_gold(world: World, rng: random.Random, avoid: tuple[int, int], count: int | None = None) -> tuple[tuple[int, int], ...]: ...
def place_natives(
    world: World, universe: Universe, rank: int, avoid: tuple[int, int], rng: random.Random
) -> tuple[tuple[str, int, int, int], ...]: ...
```

- `"top_split"` (für `kruemelreich`, 3 Schlüssel `(k0, k1, k2)`): Obere Hälfte (`y0 = BORDER .. h // 2`) wird vertikal halbiert in `k0` (links) und `k1` (rechts); untere Hälfte (`h // 2 .. h - BORDER`) ist `k2`.
- `"islands"` (für `glibbria`, 3 Schlüssel `(k0, k1, k2)`): Obere `2/3` der Höhe werden links/rechts in `k0` und `k1` geteilt; unteres Drittel (`2 * h // 3 .. h - BORDER`) ist `k2` (Sirupküste/Meer).
- `place_natives`: Skaliert Basis-Anzahl (`14` normale Kreaturen bei Standardfläche `1280×720`) mit `area_scale * (1.0, 1.3, 1.6)[rank - 1]`. Jede Gruppe erhält eine fortlaufende `group_id >= 1` und Größe `rng.randint(*spec.group_size)`. Falls `universe.big` gesetzt und in `SPECIES` vorhanden, wird genau `1` Exemplar mit eigener `group_id` platziert.

---

## V10 Wiederkehrende Universums-Ereignisse (`src/events.py`)

```python
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from src.run import Run

@dataclass(frozen=True)
class EventSpec:
    key: str
    name_de: str
    interval: float        # Sekunden zwischen zwei Starts (Ruhephase)
    duration: float        # Sekunden aktive Dauer
    warn: float = 3.0      # Sekunden Vorwarnung vor dem Start
    announce_de: str = ""  # Text / Klonita-Warnung bei Vorwarnung

class Event:
    spec: ClassVar[EventSpec]

    def __init__(self, rank: int = 1) -> None:
        self.rank = rank
        self.timer: float = 0.0
        self.active: bool = False
        self.warned: bool = False

    @property
    def effective_interval(self) -> float:
        """Interval adjusted by rank (e.g. riesenschritt on rank 3 is half interval)."""
        return self.spec.interval

    def update(self, run: Run, dt: float) -> None: ...
    def on_warn(self, run: Run) -> None: ...
    def on_start(self, run: Run) -> None: ...
    def on_tick(self, run: Run, dt: float) -> None: ...
    def on_end(self, run: Run) -> None: ...

    def to_data(self) -> dict[str, Any]:
        return {
            "key": self.spec.key,
            "rank": self.rank,
            "timer": self.timer,
            "active": self.active,
            "warned": self.warned,
        }

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Event | None: ...

EVENTS: dict[str, type[Event]] = {}
def register(cls: type[Event]) -> type[Event]: ...
def make_event(key: str, rank: int = 1) -> Event | None: ...
```

Zeitablauf in `Event.update(run, dt)`:

- Solange `not self.active`:
  - `self.timer += dt`.
  - Wenn `not self.warned` und `self.timer >= self.effective_interval - self.spec.warn`: `self.warned = True`, `self.on_warn(run)` (fügt `self.spec.announce_de` zu `run.messages` hinzu).
  - Wenn `self.timer >= self.effective_interval`: `self.timer = 0.0`, `self.active = True`, `self.on_start(run)`, `run.emit("event_start", key=self.spec.key)`.
- Solange `self.active`:
  - `self.timer += dt`, `self.on_tick(run, dt)`.
  - Wenn `self.timer >= self.spec.duration`: `self.timer = 0.0`, `self.active = False`, `self.warned = False`, `self.on_end(run)`, `run.emit("event_end", key=self.spec.key)`.

---

## V13 Herausforderungen in Universen (`src/challenges.py`)

```python
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from src.run import Run

@dataclass(frozen=True)
class ChallengeSpec:
    key: str                    # z. B. "challenge_fleischwelt"
    universe: str               # Universumsschlüssel
    giver: str                  # Kreaturschlüssel des friedlichen Auftraggebers
    text_de: str                # Angebotstext bei Ansprache mit E
    goal: int                   # Zielwert (z. B. 3 Gallensteine, 5 Formulare, 5 Beat-Sprünge)
    reward: tuple[str, int]     # ("life_capsule", 1) | ("gold", 150) | ("module_rarity", 3) | ("sample", 2) | ("flask_neonsaft", 80) | ("free_reroll", 1)

class Challenge:
    spec: ClassVar[ChallengeSpec]

    def __init__(self) -> None:
        self.accepted: bool = False
        self.progress: int = 0
        self.done: bool = False
        self.failed: bool = False
        self.rewarded: bool = False

    def accept(self, run: Run) -> bool: ...
    def on_event(self, run: Run, name: str, data: dict[str, Any]) -> None: ...
    def update(self, run: Run, dt: float) -> None: ...

    def to_data(self) -> dict[str, Any]:
        return {
            "key": self.spec.key,
            "accepted": self.accepted,
            "progress": self.progress,
            "done": self.done,
            "failed": self.failed,
            "rewarded": self.rewarded,
        }

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Challenge | None: ...

CHALLENGES: dict[str, type[Challenge]] = {}  # universe_key -> Challenge subclass
def register(cls: type[Challenge]) -> type[Challenge]: ...
def pay_reward(run: Run, reward: tuple[str, int]) -> None: ...
```

---

## V14 Bot-Lauf (`src/bot.py`, headless)

```python
from dataclasses import dataclass

@dataclass
class BotReport:
    universe: str
    rank: int
    seed: int
    crashed: str | None         # Ausnahmetext oder None
    anchor_reachable: bool      # find_path(..., flying=True) von spawn zu exit != None
    frames: int
    logic_p99_ms: float

def run_bot(
    universe: str, rank: int, seed: int, seconds: float = 30.0, dt: float = 1 / 30
) -> BotReport: ...

def run_full(seed: int, seconds_per_stage: float = 10.0) -> list[BotReport]: ...
```
