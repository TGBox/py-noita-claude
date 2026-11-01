# Verträge (Schnittstellen)

Verbindlich für alle Aufgabenkarten. Eine Karte darf einen Vertrag **nicht** ändern; braucht sie eine Änderung, wird das als offene Frage notiert und von einem großen Modell hier nachgetragen.

Grundsätze:

- Logik ist headless testbar (kein `import pygame` in Logikmodulen). Zeichnen nur in `src/rendering.py`, `src/sprite_render.py`, `src/hud.py`, `src/menus.py`, `src/ui.py`.
- Neue Felder bekommen **Standardwerte**, die das heutige Verhalten unverändert lassen. Alte Kreaturen ohne neue Felder laufen über den alten Codepfad weiter, bis U1 sie ersetzt.
- Zeiten in Sekunden, Strecken in Pixeln (= Zellen), Wahrscheinlichkeiten 0–1.
- Spieltexte als `*_de`-Felder oder Konstanten; Schlüssel `snake_case` ohne Umlaute.

## V1 Verhalten (`src/behaviour.py`)

```python
STANCES = ("hostile", "neutral", "passive", "trader")
ABILITY_KEYS = (
    "graze", "pack", "hunt", "retaliate", "dig", "steal", "split", "flee",
    "transform", "ranged", "melee", "shield", "reflect", "armor", "summon", "stationary",
)

@dataclass
class BehaviourContext:
    world: World
    player: Body
    creatures: list[Creature]          # alle lebenden Kreaturen der Welt
    projectiles: ProjectileSystem
    rng: random.Random
    dt: float
    events: list[tuple[str, dict[str, Any]]]  # Ausgabe; Run verarbeitet sie (V12)

class Ability:
    key: ClassVar[str]
    def __init__(self, creature: Creature, params: dict[str, float]) -> None: ...
    def update(self, ctx: BehaviourContext) -> None: ...          # jedes Bild
    def on_hurt(self, ctx: BehaviourContext, amount: float,
                source: tuple[float, float] | None) -> float:     # gibt (veränderten) Schaden zurück
        return amount
    def wants_move(self) -> tuple[float, float] | None:           # Zielpunkt oder None
        return None

ABILITIES: dict[str, type[Ability]] = {}
def register(cls: type[Ability]) -> type[Ability]: ...           # Dekorator, trägt cls.key ein
def build_abilities(creature: Creature) -> list[Ability]: ...     # aus creature.spec
def update_behaviour(creature: Creature, ctx: BehaviourContext) -> None: ...
GRAZE_MATERIAL: dict[str, str] = {}   # Kreaturschlüssel -> Materialschlüssel, den sie frisst
```

Materialien in Parametern immer als **Schlüssel** (nie als ID), weil IDs je Universum wechseln.

Reihenfolge in `update_behaviour`: Haltung prüfen (V1a) → alle `update` → erster nicht-`None` `wants_move` in Reihenfolge von `spec.abilities` bestimmt das Bewegungsziel → Bewegung über `Creature.steer_to(x, y, dt)`.

### V1a Haltung und Aggro

- `Creature.aggro: bool` – greift an. `hostile`: `aggro=True` sobald sie den Spieler sieht. `neutral`: erst nach Treffer an sich oder ihrer Gruppe. `passive`: nie; Treffer setzt `fleeing=True`. `trader`: nie, Treffer → `ctx.events.append(("trader_hurt", {...}))`.
- `retaliate` ist für alle Haltungen außer `passive` automatisch aktiv (in `build_abilities` ergänzen, wenn nicht genannt).

### V1b Neue Felder in `CreatureSpec` (`src/enemies.py`)

```python
stance: str = "hostile"
abilities: tuple[str, ...] = ()                      # leer = alter Codepfad
ability_params: tuple[tuple[str, float], ...] = ()   # z. B. (("dig_hardness", 1), ("split_generations", 2))
faction: str = "native"                              # V4
windup: float = 0.4                                  # Ausholen in s, nie < 0.4
group_size: tuple[int, int] = (1, 1)                 # Spawn in Gruppen
gold: tuple[int, int] = (0, 0)                       # Gold bei Tod (Rang 1), W2 skaliert
drops: tuple[tuple[str, float], ...] = ()            # (Gegenstand-/Probenschlüssel, Chance)
```

### V1c Neue Felder in `Creature`

```python
state: str = "idle"      # V2
state_time: float = 0.0
aggro: bool = False
fleeing: bool = False
group_id: int = 0        # gleiche Gruppe teilt Aggro (pack)
last_hit_from: tuple[float, float] | None = None
path: list[tuple[int, int]] = []
abilities: list[Ability]
def steer_to(self, x: float, y: float, dt: float) -> None: ...   # nutzt _crawl/_fly-Logik
def hurt(self, amount: float, cause: str = "",
         source: tuple[float, float] | None = None) -> None: ...  # source = Weltposition des Verursachers
```

## V2 Zustände und Ausholen

- Zustandsnamen = Sprite-Zustände aus Bibel 01 „Animation“: `idle`, `move`, `windup`, `attack`, `hurt`, `death` + Sonderzustände je Kreatur (z. B. `dig`, `stamp`, `hang`, `latched`, `squash`, `burrow_out`).
- `Creature.set_state(name: str) -> None` setzt `state` und `state_time = 0`.
- Jeder Angriff läuft `windup` (Dauer `spec.windup`) → `attack` → zurück zu `idle`/`move`. Schaden entsteht nur beim Übergang `windup → attack`. Funktion: `Creature.begin_attack(kind: str) -> bool` (False, wenn schon im Angriff oder Abklingzeit).
- `hurt` dauert 0,15 s und unterbricht kein `windup`.

## V3 Wegsuche (`src/pathfind.py`)

```python
GRID = 4  # px pro Wegsuch-Zelle
def find_path(world: World, start: tuple[float, float], goal: tuple[float, float],
              body_w: int, body_h: int, *, flying: bool, max_nodes: int = 3000
              ) -> list[tuple[int, int]] | None: ...
class PathFollower:
    def __init__(self, repath_interval: float = 0.5) -> None: ...
    def next_waypoint(self, creature: Creature, world: World,
                      goal: tuple[float, float], dt: float) -> tuple[float, float] | None: ...
```

- A* auf einem Gitter mit `GRID`-Zellen, 8 Nachbarn. Eine Gitterzelle ist frei, wenn kein Weltpixel im Körperrechteck `mat.BLOCKS_BODY` ist.
- `flying=False`: Kosten +4 für Zellen ohne Boden darunter (bevorzugt Boden), sonst gleich. Laufende Kreaturen springen, wenn der nächste Wegpunkt höher liegt.
- Kein Weg innerhalb `max_nodes` → `None`. Nie Ausnahmen.

## V4 Fraktionen (`src/factions.py`)

```python
PLAYER, NATIVE, AUTHORITY, EVIL_SELF = "player", "native", "authority", "evil_self"
class Grudges:
    def add(self, species_a: str, species_b: str) -> None: ...
    def has(self, species_a: str, species_b: str) -> bool: ...
    def to_data(self) -> list[list[str]]: ...
    @classmethod
    def from_data(cls, data: list[list[str]]) -> Grudges: ...
def hostile(a: Creature, b: Creature, grudges: Grudges) -> bool: ...
```

Regeln aus Bibel 02 „Fraktionen“: Einheimische untereinander friedlich außer bei Groll (`Grudges`), Behörde ↔ alle feindlich, böse Ichs eigene Fraktion. `Run.grudges: Grudges` wird gespeichert.

## V5 Sprite-Metadaten und Animation (`src/sprites.py`, headless)

```python
SPRITE_ROOT = Path("assets/sprites_png")
LOOPING = frozenset({"idle", "move", "hang", "latched"})
@dataclass(frozen=True)
class SheetMeta:
    key: str
    frame_w: int
    frame_h: int
    anchor: tuple[int, int]
    hitbox: tuple[int, int, int, int]
    states: dict[str, tuple[int, int, int]]   # Zustand -> (erstes Frame, Anzahl, fps)
    glow: dict[int, tuple[tuple[int, int], ...]]  # Frame -> leuchtende Pixel
def load_meta(path: Path) -> SheetMeta: ...
def find_meta(category: str, key: str) -> SheetMeta | None: ...   # None, wenn keine Datei
class Animator:
    def __init__(self, meta: SheetMeta) -> None: ...
    def set_state(self, state: str, restart: bool = False) -> None: ...  # unbekannt -> "idle"
    def update(self, dt: float) -> None: ...
    @property
    def frame(self) -> int: ...     # absoluter Frame-Index im Bogen
    @property
    def done(self) -> bool: ...     # nicht-schleifender Zustand ist durchgelaufen
```

JSON-Format wie Bibel 01 „Dateiformat“; zusätzlich `glow` als `{"<frame>": [[x, y], ...]}`.

## V6 Sprite-Zeichnen (`src/sprite_render.py`, pygame)

```python
class SheetCache:
    def surface(self, meta: SheetMeta) -> pygame.Surface: ...      # lädt PNG einmal
def blit_frame(canvas: pygame.Surface, cache: SheetCache, meta: SheetMeta, frame: int,
               x: int, y: int, flip: bool = False) -> None: ...      # x, y = Weltpixel des Ankers minus Kamera
def glow_points(meta: SheetMeta, frame: int, x: int, y: int, flip: bool) -> list[tuple[int, int]]: ...
```

Fehlt ein Bogen (`find_meta` → `None`), zeichnet `rendering.py` wie bisher prozedural. So bleibt das Spiel zu jeder Zeit lauffähig.

## V7 Körper aus Teilen (`src/procbody.py`, headless)

```python
class Chain:      # Segmente, die dem Kopf folgen (Würmer, Schwänze)
    def __init__(self, count: int, spacing: float, x: float, y: float) -> None: ...
    def update(self, head_x: float, head_y: float) -> None: ...
    points: list[tuple[float, float]]
class Legs:       # Schrittbeine mit festen Fußpunkten
    def __init__(self, count: int, length: float, stride: float) -> None: ...
    def update(self, body_x: float, body_y: float, world: World) -> None: ...
    feet: list[tuple[float, float]]
class Tentacle:   # Kette mit Wellenbewegung
    def __init__(self, count: int, spacing: float, wave: float, speed: float) -> None: ...
    def update(self, root_x: float, root_y: float, t: float, reach: tuple[float, float] | None) -> None: ...
    points: list[tuple[float, float]]
@dataclass(frozen=True)
class PartLayout:  # welche Teil-Sprites an welchen Punkt kommen
    key: str
    parts: tuple[tuple[str, str], ...]   # (Teil-Spritekey, "chain"|"legs"|"tentacle:<i>"|"body")
```

## V8 Sprite-Quelle (`tools/sprites.py`, Werkzeug)

- Quellformat genau wie Bibel 01 „Dateiformat“ (Python-Datei mit `PALETTE`, `SIZE`, `ANCHOR`, `HITBOX`, `GLOW`, `FPS`, `FRAMES`).
- Palettennamen → Farben in `tools/palette.py` als `PALETTE: dict[str, str]` (Hex) aus Bibel 01 „Hauptpalette“ plus je Universum die Teilpalette aus Bibel 03 (`PALETTES: dict[str, dict[str, str]]`).
- Aufruf: `uv run python -m tools.sprites build [<kategorie>[/<key>]]`, `... sheet <kategorie>`, `... check`.
- Optionale Konstanten der Quelle: `STATIC = True` (kein `move`), `ATTACKS = True` (verlangt `windup`, `attack`), `MOUNT = (x, y)` (Andockpunkt für Waffenteile), `CATEGORY_MIN_STATES` gilt je Kategorie: `ui`, `module`, `waffenteile` brauchen nur `idle`.
- `check` meldet: falsche Frame-Größe, ungleich lange Zeilen, unbekannte Zeichen, Farbe nicht in Palette, fehlende Pflichtzustände. Exit-Code 1 bei Fehlern.

## V9 Universum-Generator (`src/universes/gen/`)

```python
# src/universes/gen/__init__.py
Generator = Callable[[World, Universe, int, random.Random], Level]
GENERATORS: dict[str, Generator] = {}
def register(key: str) -> Callable[[Generator], Generator]: ...
def generate(world: World, universe: Universe, rank: int) -> Level: ...   # nutzt world.rng
```

`Level` (`src/worldgen.py`) bekommt zusätzlich (mit Standardwerten):

```python
life_capsule: tuple[int, int] | None = None
crates: tuple[tuple[int, int], ...] = ()
gold_piles: tuple[tuple[int, int], ...] = ()
regions: dict[str, tuple[int, int, int, int]] = field(default_factory=dict)  # Schlüssel -> x, y, b, h
spawns: tuple[tuple[str, int, int], ...] = ()     # (Kreaturschlüssel, x, y)
challenge: tuple[int, int] | None = None          # Platz des Auftraggebers
```

`exit` bleibt der Ankerpunkt, `secret` die Kammer mit dem Erinnerungssplitter, `vault` die Schatzkammer, `arena` die Zwischengegner-Arena (nur auf Bossplätzen).

Gemeinsame Bausteine in `src/universes/gen/common.py` (U0): `carve_oval`, `carve_tunnel`, `ensure_path` (aus `worldgen` weiterverwenden, nicht kopieren), `place_anchor`, `place_secret`, `place_vault`, `place_life_capsule`, `place_crates`, `place_gold`, `place_natives`, `split_regions`.

## V10 Ereignisse (`src/events.py`)

```python
@dataclass(frozen=True)
class EventSpec:
    key: str
    name_de: str
    interval: float        # s zwischen Starts
    duration: float        # s aktiv
    warn: float = 3.0      # s Ankündigung vor dem Start
    announce_de: str = ""  # Durchsage/Spruch bei Ankündigung
class Event:
    spec: ClassVar[EventSpec]
    def __init__(self, rank: int) -> None: ...
    def update(self, run: Run, dt: float) -> None: ...     # Zeitsteuerung, ruft die Haken
    def on_warn(self, run: Run) -> None: ...
    def on_start(self, run: Run) -> None: ...
    def on_tick(self, run: Run, dt: float) -> None: ...
    def on_end(self, run: Run) -> None: ...
    def to_data(self) -> dict[str, Any]: ...
EVENTS: dict[str, type[Event]] = {}
def register(cls: type[Event]) -> type[Event]: ...
```

`Run.event: Event | None` entsteht beim Betreten eines Universums aus `Universe.event`.

## V11 Gegenstände, Proben (`src/samples.py`, `src/loot.py`)

```python
@dataclass(frozen=True)
class Sample:
    key: str        # "probe_gallenstein"
    name_de: str
    universe: str
SAMPLES: dict[str, Sample]
SAMPLE_SLOTS, SAMPLE_STACK = 12, 99
```

- `Pickup.kind` kennt zusätzlich `"sample"`, `"gold"`, `"life_capsule"`, `"memory_shard"`, `"crate"`, `"blueprint_shard"`, `"badge"`. Bestehende Arten bleiben.
- `Inventory.samples: list[tuple[str, int] | None]` (12 Plätze), `add_sample(key, n=1) -> bool`, `take_samples(key, n) -> bool`. Speichern über Schlüssel.

## V12 Ereignisbus in `Run`

```python
def emit(self, name: str, **data: Any) -> None: ...     # ruft _log und alle Hörer
self.listeners: list[Callable[[str, dict[str, Any]], None]]
```

Feste Namen (weitere nur per Vertragsänderung): `kill`, `hurt_player`, `pickup`, `sample`, `gold`, `enter_universe`, `leave_universe`, `event_start`, `event_end`, `beat`, `jump`, `trader_hurt`, `trader_killed`, `steal`, `wanted_change`, `boss_phase`, `challenge_done`, `cells_destroyed`.
Kreatur-Ereignisse aus `BehaviourContext.events` werden 1:1 mit `emit` weitergereicht.

## V13 Herausforderungen (`src/challenges.py`)

```python
@dataclass(frozen=True)
class ChallengeSpec:
    key: str            # "challenge_fleischwelt"
    universe: str
    giver: str          # Kreaturschlüssel des Auftraggebers
    text_de: str
    goal: int
    reward: tuple[str, int]   # ("gold", 150) | ("module_rarity", 3) | ("sample", 2) | ("life_capsule", 1) | ...
class Challenge:
    def __init__(self, spec: ChallengeSpec) -> None: ...
    accepted: bool; progress: int; done: bool
    def on_event(self, name: str, data: dict[str, Any]) -> None: ...   # Hörer an Run.emit
CHALLENGES: dict[str, type[Challenge]]
```

## V14 Bot-Lauf (`src/bot.py`, headless)

```python
@dataclass
class BotReport:
    universe: str; rank: int; seed: int
    crashed: str | None        # Fehlermeldung oder None
    anchor_reachable: bool     # find_path/ensure_path von spawn zu exit
    frames: int
    logic_p99_ms: float
def run_bot(universe: str, rank: int, seed: int, seconds: float = 30.0, dt: float = 1 / 30) -> BotReport: ...
```

Der Bot spielt nicht: Spieler im Gottmodus, folgt dem Weg zum Anker per `find_path(..., flying=True)` und lässt die Welt `seconds` lang laufen. Tests rufen ihn mit kleinen `seconds`.

## V15 Behörde (`src/authority.py`)

```python
WANTED_MAX = 5.0
class Wanted:
    level: float = 0.0
    destroyed_cells: int = 0
    def add(self, amount: float, reason: str) -> None: ...     # klemmt 0..5, Run emittiert wanted_change
    def on_cells_destroyed(self, n: int) -> None: ...          # je 5000 Zellen +0,5
    def on_workshop(self) -> None: ...                         # -1
    def agent_count(self) -> int: ...                          # round(level * 2)
    def to_data(self) -> dict[str, Any]: ...
AGENT_TYPES = ("agent_streife", "agent_vollstrecker", "agent_drohne")  # Bibel 05 „Behörden-Agenten“
def spawn_agents(run: Run, count: int) -> list[Creature]: ...
```

Agenten-Auswahl nach Stufe: `agent_streife` ab 1, `agent_drohne` ab 2, `agent_vollstrecker` ab 3 (Bibel 04).
