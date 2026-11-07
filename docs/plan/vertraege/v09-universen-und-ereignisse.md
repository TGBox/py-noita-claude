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
    quest_giver: tuple[int, int] | None = None                     # Standplatz des Auftraggebers (V13b)
    quest_target: tuple[int, int] | None = None                    # Ziel der Kuh-Eskorte (V13b, nur Glibbria)
```

- **Rechteck-Konvention (`(x0, y0, x1, y1)`):** Alle Rechtecke im gesamten Projekt haben `0 <= x0 < x1 <= width` und `0 <= y0 < y1 <= height`.
- **Bossplatz:** `Run(seed, …, universe_key=k, boss_slot=False)`. Der Unter-Zwischenboss (`universe.mid_boss`) erscheint in jedem Universum in `mid_boss_arena`; der Zwischengegner (`universe.boss`) nur bei `boss_slot=True` in `boss_arena` (Bibel 02: zweites Universum jedes Rangs). Im Lauf setzt `RunPlan.boss_slot` den Wert.
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
    duration: float                       # Sekunden aktiv
    preferred_universes: tuple[str, ...] = ()
    interval: float = 0.0                 # Sekunden zwischen zwei Starts (Bibel 03)
    warn: float = 0.0                     # Sekunden Ankündigung vor dem Start

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
    """Return a fresh Event for the universe's own event (UNIVERSES[key].event), or None."""
    ...
```

### Kanonische Ereignisse in `EVENTS` (genau die 6 Universums-Ereignisse aus Bibel 03)

Jedes Universum hat genau ein wiederkehrendes Ereignis (`Universe.event`). `Run` zählt `interval` herunter, kündigt `warn` Sekunden vorher an und startet dann das Ereignis für `duration` Sekunden. Zufällige Zusatzereignisse gibt es im MVP nicht (nach Phase 2 verschoben, `tasks/todo_erweiterung.md`).

| `key` | `name` | `preferred_universes` | `interval` / `warn` / `duration` | Wirkung (Bibel 03) |
| --- | --- | --- | --- | --- |
| `"verdauung"` | `"Verdauung"` | `("fleischwelt",)` | `90` / `3` / `20` | Säurespiegel in Region `"magen"` +30 px; Kamerawackeln bei Ankündigung |
| `"pruefung"` | `"Prüfung"` | `("aktenhalde",)` | `120` / `3` / `1` | Durchsage „Bitte halten Sie Ihre Unterlagen bereit.“; 2 `agent_streife` erscheinen |
| `"brauseregen"` | `"Brauseregen"` | `("glibbria",)` | `100` / `3` / `15` | `"brausesirup"` regnet am oberen Rand der Simulationszone |
| `"riesenschritt"` | `"Riesenschritt"` | `("kruemelreich",)` | `80` / `3` / `1` | 120 px breiter Streifen der Oberfläche wird zusammengedrückt; Schatten als Ankündigung |
| `"bass_drop"` | `"Bass-Drop"` | `("sporenklub",)` | `60` / `1` / `1` | alle Körper und losen Gegenstände +40 px hoch, Pulver hüpft |
| `"glockenschlag"` | `"Glockenschlag"` | `("abtei",)` | `75` / `2` / `1` | Stromschlag für alle Körper im Wasser; leises Vorläuten als Ankündigung |

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

## V13b Universums-Herausforderungen (`src/challenges.py`)

Die sechs Herausforderungen aus Bibel 07 („Herausforderungen in Universen“). Anders als die Schrein-Prüfungen (V13) vergibt sie ein Einheimischer (Auftraggeber), man nimmt sie mit `E` an, und die Belohnung kommt beim Auftraggeber.

```python
@dataclass(frozen=True)
class QuestSpec:
    key: str                  # "challenge_<universum>"
    universe: str
    giver: str                # Art des Auftraggebers (wird friedlich gespawnt, giver=True)
    text_de: str              # Sprechblase beim Ansprechen
    goal: int                 # benötigter Fortschritt
    reward: tuple[str, int]   # (Art, Menge), siehe Tabelle

@dataclass
class Quest:
    spec: QuestSpec
    accepted: bool = False
    progress: int = 0
    done: bool = False
    failed: bool = False
    reward_paid: bool = False

    def accept(self, run: Run) -> None: ...                                  # accepted=True, emit("quest_accepted")
    def on_event(self, name: str, data: dict[str, object], run: Run) -> None: ...
    def tick(self, dt: float, run: Run) -> None: ...
    def turn_in(self, run: Run) -> bool: ...                                 # beim Auftraggeber mit E; zahlt aus
    def to_data(self) -> dict[str, object]: ...
    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Quest | None: ...

QUESTS: dict[str, QuestSpec] = {...}          # genau 6, Schlüssel = QuestSpec.key
def quest_for(universe_key: str) -> Quest: ...   # neue Quest-Instanz des Universums
```

Regeln: Vor `accept` werden Ereignisse ignoriert. Nach `failed` oder `reward_paid` ändert sich nichts mehr. `turn_in` gelingt nur bei `progress >= goal` und nicht `failed`, zahlt genau einmal aus und feuert `emit("quest_done", key=…, success=True)`; Scheitern feuert `quest_done` mit `success=False`.

| `key` | Auftraggeber | `goal` | Fortschritt / Scheitern | `reward` | Auszahlung in `turn_in` |
| --- | --- | --- | --- | --- | --- |
| `challenge_fleischwelt` | `fleischmade` | `3` | Fortschritt = `run.inventory.sample_count("probe_gallenstein")` (in `tick`); `turn_in` zieht 3 ab | `("life_capsule", 1)` | Pickup `kind="life_capsule"` beim Auftraggeber |
| `challenge_aktenhalde` | `stempler` | `5` | `+1` je `"form_stamped"`; scheitert bei `"event_start"` mit `key == "pruefung"` | `("gold", 150)` | `run.gold += 150` |
| `challenge_glibbria` | `huepfling` | `1` | `+1`, wenn die `glibberkuh` die Zielzone (`Level.quest_target`) erreicht; scheitert, wenn sie stirbt (`"kill"` mit `species == "glibberkuh"`) | `("module_tier", 3)` | Pickup `kind="block"` mit `rng.choice(blocks_of_tier(3))` |
| `challenge_kruemelreich` | `blattlaus` | `3` | `+1` je `"aphid_fed"`; scheitert, sobald ein `ameisenkrieger` die Spielerin sieht (`can_see`, in `tick`) | `("samples", 2)` | `run.inventory.add_sample(universe.sample_key, 2)` |
| `challenge_sporenklub` | `leuchtmotte` | `5` | `+1` je `"jump"` mit `on_beat == True`; ein Sprung neben dem Beat setzt `progress = 0` | `("neonsaft_gold", 80)` | Kolben mit `"neonsaft"` (voll) als Pickup + `run.gold += 80` |
| `challenge_abtei` | `moenchsfisch` | `3` | `+1` je `"bell_rung"`; scheitert bei `"creature_woke"` mit `species == "kirchenkrake"` | `("reroll", 1)` | `run.inventory.rerolls += 1` |

Ergänzend:

- `Level.quest_giver` – freier Bodenplatz für den Auftraggeber, von jedem Generator gesetzt.
- `Level.quest_target: tuple[int, int] | None = None` – Zielpunkt der Kuh-Eskorte (Glibbria, gegenüberliegende Küste des Sirupsees); die Zielzone ist ein Kreis mit Radius `24 px`.
- `glibberkuh` (Bibel 05, Glibbria): `passive`, folgt der Spielerin, solange die Quest angenommen ist und der Abstand `< 120 px` ist; löst sich nach `3 s` ununterbrochenem Kontakt mit `"brausesirup"` auf (stirbt).
- `kirchenkrake` schläft mit einem Lärmzähler: jedes `"noise"` im Umkreis `200 px` addiert `40`, der Zähler sinkt um `10` pro Sekunde, bei `>= 100` wacht sie auf (`emit("creature_woke", species="kirchenkrake")`). Jeder Glockenschlag (`"bell_rung"`) erzeugt ein `"noise"`. Wer zu schnell läutet, weckt sie.
- `Run.quest: Quest | None` wird beim Betreten eines Universums mit `quest_for(universe.key)` belegt; der Auftraggeber erscheint an `Level.quest_giver`. `Run.try_interact_creature()` ruft beim Auftraggeber `accept` bzw. `turn_in` auf.

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

### Inhalts-Abnahme der Generatoren (Plan-Korrektur 2026-11-07)

Jeder MVP-Generator (`D01`–`D06`) muss in `World(320, 200)` mit `depth=1, seed=42` folgende Mindestwerte erreichen (Anteil der Zellen einer Region, Stichprobe jede 2. Zelle). Die Werte stehen als `GENERATOR_CONTENT` in `tests/spec/test_phase_d.py`; die Karten-Beschreibung bleibt der eigentliche Auftrag, die Werte sind nur die Untergrenze.

| Universum | Topologie | Region: Material ≥ Anteil | sonst |
| --- | --- | --- | --- |
| `fleischwelt` | `vertical` | schlund: `enamel` 0,5 %; magen: `acid` 1 %, `tallow` 0,5 %; knochenmark: `bone` 15 %, `enamel` 0,3 % | `flesh` ≥ 20 % der Welt; `Level.secret` gesetzt |
| `aktenhalde` | `horizontal` | registratur: `aktendeckel` 2 %, `papier` 5 %; grossraumbuero: `air` 25 %; archivkeller: `tinte` 2 % | in `World(1280, 720)` keine zusammenhängende `papier`-Fläche größer als 640×360 (Trennwände ≥ 2 px dick) |
| `glibbria` | `islands` | gelee_huegel: `glibber`+`glibber_rot` 10 %, `zuckerguss` 0,3 %; kaugummi_hoehlen: `kaugummi` 1 %; sirupkueste: `brausesirup` 5 % | unterste 10 % der Welt ≥ 30 % `brausesirup`; `Level.quest_target` gesetzt |
| `kruemelreich` | `top_split` | fliesenwueste: `fliese` 5 %, `kruemel` 0,5 %, `zucker` 0,3 %; unter_kuehlschrank: `staubfluse` 1 %; ameisenbau: `brosel`+`kruemel` 15 % | – |
| `sporenklub` | `vertical` | lautsprechertuerme: `pilzhut` 5 %; tanzflaeche: `leuchtsporen` 0,3 %, `air` 30 %; hinterzimmer: `pilzfleisch` 15 % | – |
| `abtei` | `vertical` | glockenturm: `glockenbronze` 0,3 %, `water` ≤ 1 %; kirchenschiff: `mauerwerk` 5 %, `buntglas` 0,3 %, `water` 20 %; krypta: `algen` 0,3 % | `kerzenwachs` ≥ 0,05 % der Welt |

Für alle gilt außerdem: `[r[1] for r in level.regions] == region_bands(width, height, <Topologie>)`, alle Props der Karte stehen in `Level.destructible_props`, und `Level.quest_giver` ist eine Luftzelle mit festem Boden höchstens 12 px darunter.
