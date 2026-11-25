# V1–V4 – Verhaltensbibliothek, Zustände, Wegsuche, Fraktionen & Status-Effekte

Verbindliche Schnittstellen für `src/behaviour.py`, `src/enemies.py`, `src/pathfind.py`, `src/factions.py`, `src/body.py`, `src/player.py` und `src/flask.py`. Alle Module in diesem Vertrag sind **headless** (kein `import pygame`).

---

## V1 Verhalten (`src/behaviour.py`)

```python
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from .enemies import Creature
    from .loot import Pickup
    from .player import Player
    from .projectiles import Projectile
    from .world import World

STANCES: tuple[str, ...] = ("hostile", "neutral", "passive", "trader")
STANCE_ALIASES: dict[str, str] = {
    "peaceful": "passive",
    "shy": "passive",
    "territorial": "neutral",
}

ABILITY_KEYS: tuple[str, ...] = (
    "graze", "eat_material", "pack", "hunt", "retaliate", "dig", "steal", "split", "flee",
    "transform", "morph", "ranged", "melee", "shield", "reflect", "armor", "summon", "stationary",
    "aura", "teleport", "kamikaze", "burrow",
)

PIERCING_FORMS: frozenset[str] = frozenset({
    "beam", "lance", "laser", "lightning", "chain", "saw",
    "nadel", "nadelschuss", "knochenspeer", "durchschlagbolzen",
    "nadelregen", "knochensaege", "kreissaege",
})

GRAZE_MATERIAL: dict[str, str] = {   # Kreatur -> Materialschlüssel aus src/materials.py
    "huepfling": "zuckerguss",
    "blattlaus": "zucker",
    "zottenwurm": "flesh",
}

SPLIT_SIZES: tuple[tuple[float, float], ...] = (
    (1.0, 1.0),
    (0.7, 0.55),
    (0.5, 0.30),
)

@dataclass(frozen=True)
class Ability:
    kind: str
    param: str = ""
    param_float: float = 0.0

@dataclass
class BehaviourContext:
    dt: float
    world: World
    player: Player
    creatures: list[Creature]
    projectiles: list[Projectile]
    pickups: list[Pickup] = field(default_factory=list)
    grudges: set[tuple[str, str]] = field(default_factory=set)
    on_beat: bool = True
    rng: random.Random = field(default_factory=random.Random)
    out_events: list[tuple[str, dict[str, object]]] = field(default_factory=list)

def handle_split_on_death(
    creature: Creature,
    ability: Ability,
    out_events: list[tuple[str, dict[str, object]]],
) -> None: ...

def handle_morph_check(creature: Creature, ability: Ability) -> bool: ...

def handle_reflect_projectiles(
    creature: Creature,
    projectiles: list[Projectile],
    out_events: list[tuple[str, dict[str, object]]],
) -> int: ...

def handle_steal_pickup(
    creature: Creature,
    pickups: list[Pickup],
    out_events: list[tuple[str, dict[str, object]]],
) -> bool: ...

def handle_eat_material(
    creature: Creature,
    material_name: str,
    world: World,
    pickups: list[Pickup],
) -> bool: ...

def handle_aura(
    creature: Creature,
    ability: Ability,
    player: Player,
    creatures: list[Creature],
    dt: float = 0.016,
) -> None: ...

def handle_teleport(
    creature: Creature,
    world: World,
    rng: random.Random,
) -> bool: ...

def handle_summon(
    creature: Creature,
    ability: Ability,
    out_events: list[tuple[str, dict[str, object]]],
) -> None: ...

def handle_kamikaze(
    creature: Creature,
    ability: Ability,
    player: Player,
    world: World,
    out_events: list[tuple[str, dict[str, object]]],
) -> bool: ...

def handle_burrow(
    creature: Creature,
    target_pos: tuple[float, float],
    world: World,
    dt: float,
) -> None: ...

def apply_chorus_buff(creature: Creature, creatures: list[Creature]) -> float: ...

def tick_abilities(creature: Creature, ctx: BehaviourContext) -> None: ...
```

- Materialien in Parametern immer als **Schlüssel** (nie als ID).
- `tick_abilities(creature, ctx)` iteriert über `creature.spec.abilities` (`tuple[Ability, ...]`) und führt die jeweiligen Handler (`handle_eat_material`, `handle_steal_pickup`, `handle_reflect_projectiles`, `handle_aura`, `handle_summon`, `handle_kamikaze`, `handle_burrow`, `handle_morph_check` usw.) für den aktuellen Tick aus.
- `apply_chorus_buff(creature, creatures)`: Wenn mindestens `3` lebende `moenchsfisch` innerhalb von `90..180 px` umeinander stehen, liefert die Funktion den Schadensmultiplikator `> 1.0` (`1.25` bzw. `1.5`), sonst `1.0`.

---

## V1a–V2 Haltungen, `CreatureSpec`, `Creature` & Zustandsmaschine (`src/enemies.py`)

### 1. Haltungen (`STANCES` & `evaluate_stance`)

```python
STANCES: tuple[str, ...] = ("peaceful", "shy", "territorial", "hostile", "neutral", "passive", "trader")
MIN_WINDUP: float = 0.40

def evaluate_stance(
    creature: Creature,
    player_x: float,
    player_y: float,
    was_hit: bool = False,
    pack_aggro: bool = False,
) -> str:
    """Return behaviour action ('idle', 'flee', 'chase') based on creature.spec.stance,
    distance to (player_x, player_y), creature.aggro, was_hit, and pack_aggro."""
    ...

def begin_attack(creature: Creature, windup: float = MIN_WINDUP) -> None:
    """Transition creature into 'windup' state with windup_timer = max(MIN_WINDUP, windup)."""
    ...

def poll_attack_ready(creature: Creature, dt: float) -> bool:
    """Advance windup_timer by dt; when <= 0 transition into 'attack' and return True."""
    ...
```

- **`peaceful` / `passive`:** Greift nie an (`"idle"`); flieht (`"flee"`) nach Treffer (`was_hit == True`).
- **`shy`:** Flieht (`"flee"`), sobald die Spielerin näher als `creature.spec.aggro_radius` (`sight`) kommt.
- **`territorial` / `neutral`:** Bleibt ruhig (`"idle"`), bis die Spielerin in den Nahbereich (`aggro_radius * 0.6`) eindringt oder die Kreatur bzw. ihre Gruppe (`was_hit` / `pack_aggro`) angegriffen wird; wechselt dann auf `"chase"` und setzt `creature.aggro = True`.
- **`hostile`:** Verfolgt (`"chase"`) und setzt `creature.aggro = True`, sobald Distanz `<= aggro_radius`.

### 2. Felder auf `CreatureSpec` (`src/enemies.py`)

Alle neuen Felder besitzen Standardwerte, sodass bestehende `CreatureSpec`-Einträge unverändert funktionieren:

```python
    stance: str = "hostile"
    faction: str = "wildnis"
    aggro_radius: float = 130.0
    windup_time: float = 0.40
    group_size: tuple[int, int] = (1, 1)
    abilities: tuple[Ability, ...] = ()
    drops_sample: str = ""          # Probenschlüssel (leer = Universums-Probe sample_key)
    sample_chance: float = 0.35     # Bosse und Unter-Zwischenbosse: 1.0
    weak_material: str = ""         # Geschoss-trail mit diesem Material: Schaden × 1.5
    resist_material: str = ""       # Geschoss-trail mit diesem Material: Schaden × 0.5
    is_mid_boss: bool = False
    is_boss: bool = False
```

### 3. Felder & `EnemyManager.update` auf `Creature` (`src/enemies.py`)

```python
    state: str = "idle"                     # "idle", "move", "windup", "attack", "hurt", "death", ...
    state_timer: float = 0.0
    windup_timer: float = 0.0
    aggro: bool = False
    group_id: int = 0
    generation: int = 0
    carrying: Pickup | None = None
    morphed: bool = False
    bribed: bool = False
    giver: bool = False
    chorus_buff: float = 0.0
    last_attacker_faction: str = ""
    path_cache: Any = None
    anim_state: str = "idle"
    anim_time: float = 0.0
    pending_shot: tuple[float, float] | None = None
```

Bestehende Hilfen, die Tests und Karten voraussetzen (bereits im Gerüst vorhanden):

- `Body.body -> Body` gibt `self` zurück, damit `player.body.hp` und `creature.body.hp` gleichwertig zu `player.hp` / `creature.hp` funktionieren.
- `Creature.species: str` ist ein Feld mit dem Artschlüssel (`spec.key`, beim Spawnen gesetzt).

Signatur von `EnemyManager.update` bleibt abwärtskompatibel über optionale Keyword-Only-Parameter:

```python
def update(
    self,
    world: World,
    dt: float,
    player: Body,
    projectiles: ProjectileSystem,
    area: Rect,
    *,
    pickups: list[Any] | None = None,
    grudges: set[tuple[str, str]] | None = None,
    on_beat: bool = True,
    out_events: list[tuple[str, dict[str, Any]]] | None = None,
) -> list[Creature]: ...
```

---

## V3 Wegsuche (`src/pathfind.py`)

```python
PATH_CACHE_TTL: float = 0.4
MAX_PATH_EXPANSIONS: int = 160

@dataclass
class PathCacheEntry:
    path: list[tuple[int, int]] = field(default_factory=list)
    goal: tuple[int, int] = (0, 0)
    updated_at: float = -999.0

def find_path(
    world: World,
    start: tuple[int, int],
    goal: tuple[int, int],
    loco: str = "walk",
    max_expansions: int = MAX_PATH_EXPANSIONS,
) -> list[tuple[int, int]]:
    """Compute a coarse grid path from start to goal cell for loco ('walk', 'fly', 'swim')."""
    ...

def next_waypoint(
    world: World,
    start_x: float,
    start_y: float,
    goal_x: float,
    goal_y: float,
    loco: str,
    cache: PathCacheEntry,
    now: float = 0.0,
) -> tuple[float, float]:
    """Return the next world-pixel waypoint towards (goal_x, goal_y), updating cache if stale."""
    ...

class PathFollower:
    def __init__(self, repath_interval: float = PATH_CACHE_TTL) -> None: ...
    def next_waypoint(
        self, world: World, start_x: float, start_y: float, goal_x: float, goal_y: float, loco: str = "walk", now: float = 0.0
    ) -> tuple[float, float]: ...
```

- A* auf einem vergröberten Gitter (`4×4` Weltzellen pro Knoten), begrenzt auf `max_expansions = 160`.
- Unterstützt die Bewegungsarten `loco in ("walk", "fly", "swim")`.
- **Passierbarkeit eines Knotens** `(nx, ny)` entscheidet allein seine Mittelzelle `(4·nx + 2, 4·ny + 2)`:
  - `"fly"`: Mittelzelle ist Luft oder Gas (Flüssigkeit erlaubt, kostet ×3).
  - `"swim"`: Mittelzelle ist eine Flüssigkeit.
  - `"walk"`: Mittelzelle ist Luft oder Gas **und** die Mittelzelle des Knotens darunter ist fest (oder der Knoten liegt in der untersten Reihe); nach oben höchstens 1 Knoten auf einmal.
  - Der Knoten von Start und Ziel gilt immer als passierbar.
- **Rückgabe von `find_path`:** Liste von Weltzellen `(x, y)`: der Start, dann die Mittelzellen der Zwischenknoten, zuletzt genau das Ziel. Ist das Ziel unerreichbar, endet die Liste am Knoten, der dem Ziel am nächsten kam.
- `next_waypoint` aktualisiert `cache: PathCacheEntry` nur, wenn `now - cache.updated_at >= PATH_CACHE_TTL` oder sich das Ziel signifikant verschoben hat.

---

## V4 Fraktionen (`src/factions.py`)

Grundlage: Bibel 02 „Fraktionen“. Fraktionen regeln **nur Kreatur gegen Kreatur** (und Agenten/böse Ichs gegen die Spielerin). Ob eine Einheimische die Spielerin angreift, entscheidet allein ihre Haltung (`V1a`), nicht die Fraktion.

```python
from __future__ import annotations

# 5 Kern-Fraktionen + 6 Universums-Fraktionen (MVP) = 11.
SPIELER = "spieler"
WILDNIS = "wildnis"          # Standard für Kreaturen ohne Universum (Sandbox, Alt-Kreaturen)
HAENDLER = "haendler"
BEHOERDE = "behoerde"        # Agenten, Ober-Cloita, Rat
BOESE_ICHS = "boese_ichs"

UNIVERSE_FACTIONS: dict[str, str] = {   # Universum -> Fraktion seiner Einheimischen
    "fleischwelt": "parasiten",
    "aktenhalde": "akten",
    "glibbria": "gelee",
    "kruemelreich": "insekten",
    "sporenklub": "pilze",
    "abtei": "tiefsee",
}
NATIVE_FACTIONS: tuple[str, ...] = tuple(UNIVERSE_FACTIONS.values())

FACTIONS: tuple[str, ...] = (SPIELER, WILDNIS, HAENDLER, BEHOERDE, BOESE_ICHS, *NATIVE_FACTIONS)

_EVERYONE = frozenset(FACTIONS)
HATE_MATRIX: dict[str, frozenset[str]] = {
    SPIELER: frozenset({BEHOERDE, BOESE_ICHS}),
    WILDNIS: frozenset({BEHOERDE, BOESE_ICHS}),
    HAENDLER: frozenset({BEHOERDE, BOESE_ICHS}),
    BEHOERDE: _EVERYONE - {BEHOERDE, BOESE_ICHS},
    BOESE_ICHS: _EVERYONE - {BOESE_ICHS, BEHOERDE},
    **{
        f: frozenset({BEHOERDE, BOESE_ICHS, *(set(NATIVE_FACTIONS) - {f})})
        for f in NATIVE_FACTIONS
    },
}

def are_hostile(
    faction_a: str,
    faction_b: str,
    grudges: set[tuple[str, str]] | None = None,
) -> bool:
    """True if a and b fight each other by default (HATE_MATRIX) or via a recorded grudge."""
    ...

def record_grudge(
    grudges: set[tuple[str, str]],
    faction_a: str,
    faction_b: str,
) -> None:
    """Record a symmetric grudge: adds (a, b) and (b, a); ignores a == b."""
    ...

def hostile(a: Creature, b: Creature, grudges: set[tuple[str, str]] | None = None) -> bool:
    """Creature vs. creature: faction rule, plus species-level grudges (collateral damage)."""
    ...
```

Regeln (verbindlich, ein Test je Zeile in `tests/spec/test_phase_a.py -k a11`):

- `are_hostile(f, f)` ist immer `False`.
- `are_hostile(a, b)` ist `True`, wenn `b in HATE_MATRIX.get(a, ∅)` **oder** `a in HATE_MATRIX.get(b, ∅)`, sonst `True` nur, wenn `(a, b) in grudges`.
- Unbekannte Fraktionsschlüssel verhalten sich wie `"wildnis"`.
- Folgen aus der Matrix (Bibel 02):
  - Einheimische **desselben** Universums sind untereinander friedlich.
  - Einheimische **verschiedener** Universen bekämpfen sich (sie treffen sich nur in Parallelwelten, Minispielen oder durch Beschwörungen), z. B. `are_hostile("pilze", "insekten")`.
  - Die Behörde ist mit allen verfeindet außer mit den bösen Ichs; die bösen Ichs sind mit allen verfeindet außer mit der Behörde (sie gehören zum Rat).
  - Händler und Wildnis sind von sich aus mit niemandem außer Behörde und bösen Ichs verfeindet; `are_hostile("haendler", "spieler")` wird erst nach `record_grudge` wahr.
- `hostile(a, b, grudges)`: `False`, wenn `a is b`, eine Seite `spec.prop` ist oder eine Seite die Haltung `"trader"` hat; sonst `are_hostile(a.spec.faction, b.spec.faction, grudges)` **oder** `(a.spec.key, b.spec.key) in grudges` (Streit zwischen Arten nach Kollateraltreffer, Bibel 02).
- `Run.grudges: set[tuple[str, str]]` enthält Fraktions- **und** Artenpaare (beide Schlüsselräume sind disjunkt); gespeichert als sortierte Liste von `[a, b]`-Paaren (V23).
- In `src/projectiles.py` trägt `Projectile` neu `owner_species: str = ""` und `source_pos: tuple[float, float] | None = None`. Trifft ein Gegnergeschoss eine andere Kreatur als den Schützen (`owner_species != victim.spec.key`), ruft `Run` `record_grudge(run.grudges, owner_species, victim.spec.key)` auf.
- Pool-Universen (Phase J, `docs/erweiterung/03`) ergänzen `UNIVERSE_FACTIONS` erst, wenn sie gebaut werden.

---

## V4b Neue Status-Effekte & Flüssigkeits-Schübe (`src/body.py`, `src/player.py`, `src/flask.py`)

### 1. Neue Status-Felder auf `Body` (`src/body.py`)

Alle als `float = 0.0` (Restdauer in Sekunden), in `Body.place` mit `0.0` initialisiert und in `apply_environment` pro Frame um `dt` reduziert:

| Feld auf `Body` | Bedeutung / Wirkung |
| --- | --- |
| `drunk: float = 0.0` | Beschwipst: Waffen-Flux lädt `× 1.5` schneller (`Wand.update`), Zielwinkel schwankt |
| `sticky: float = 0.0` | Klebrig (`kaugummi`, `honig`, `karamell`, `siegellack`, `jelly`, `honey`): Bewegung verlangsamt |
| `stamped_good: float = 0.0` | Genehmigt: verursachter Schaden `× 1.2`, `-20 %` Händlerpreise (`stamped_bad = 0.0`) |
| `stamped_bad: float = 0.0` | Abgelehnt: verursachter Schaden `× 0.8` (`stamped_good = 0.0`) |
| `marked_time: float = 0.0` | Tintenblick / Drohnen-Markierung: durch Wände sichtbar |
| `frozen: float = 0.0` | Unterkühlt: Bewegung `× 0.6` |
| `charged: float = 0.0` | Elektrisch geladen: nächster Kontakt/Treffer entlädt Stromschaden |
| `befogged: float = 0.0` | Benebelt (`weihrauch`): Zielstreuung von Kreaturen `× 2.0` |
| `refresh_time: float = 0.0` | Erfrischt (Wasser): Flux lädt `× 1.2` schneller |
| `lubed_time: float = 0.0` | Geschmiert (Öl, Talg): Zauber-Verzögerung `× 0.85` |
| `fizzy_time: float = 0.0` | Sprudelnd (Brausesirup): Sprungkraft `× 1.5` |
| `haste_time: float = 0.0` | Aufgedreht (Neonsaft): Lauftempo `× 1.3` |
| `ink_sight: float = 0.0` | Tintenblick (Tinte): Kreaturen werden durch Wände gezeichnet |

`Body.damage_factor() -> float` liefert den Faktor für **verursachten** Schaden: `1.2` bei `stamped_good > 0`, `0.8` bei `stamped_bad > 0`, sonst `1.0` (Bibel 02 „Status-Effekte“). Erlittener Schaden wird durch keinen dieser Timer verändert.

### 2. Trink-Schübe (`Flask.drink` in `src/flask.py`)

`Flask.drink(body: Body, blood_heals: bool = False) -> str` setzt genau die Schübe aus Bibel 06 („Flüssigkeiten: Schübe beim Trinken“). Ein Schluck sind `SIP = 30` Zellen; bei weniger Inhalt wirken Schaden und Flux anteilig, Timer voll. **Keine Flüssigkeit heilt** – einzige Ausnahme: `"blood"` mit `blood_heals=True` (Selbstexperiment „Blutsauger“).

| Material-Key | Wirkung |
| --- | --- |
| `"water"` | `burning = 0.0`, `refresh_time = 15.0` |
| `"oil"` | `oily = 8.0`, `lubed_time = 15.0` |
| `"tallow"` | `oily = 8.0`, `lubed_time = 15.0` |
| `"fluxschnaps"` | `drunk = 20.0` |
| `"acid"` | `hurt(25.0)` |
| `"blood"` | nichts; mit `blood_heals=True`: `hp += BLOOD_HEAL` (höchstens `max_hp`) |
| `"tinte"` | `ink_sight = 20.0` |
| `"stempelfarbe"` | `stamped_good = 15.0`, `stamped_bad = 0.0` |
| `"siegellack"` | `hurt(15.0)` |
| `"brausesirup"` | `fizzy_time = 20.0` |
| `"kaugummi"` | `sticky = 5.0` |
| `"honig"` | Spieler: `mana = min(max_mana, mana + 100.0)` (Flux sofort +100) |
| `"karamell"` | `sticky = 5.0`, `hurt(10.0)` |
| `"neonsaft"` | `haste_time = 20.0` |

Jede andere Flüssigkeit: Meldung „Es schmeckt nach nichts.“, keine Wirkung. Leuchtsporen werden nicht getrunken, sondern eingeatmet (`drunk`, bei Gaskontakt in `Body.apply_environment`).
