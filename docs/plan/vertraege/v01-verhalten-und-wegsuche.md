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

GRAZE_MATERIAL: dict[str, str] = {
    "huepfling": "zuckerguss",
    "blattlaus": "zucker",
    "rostkaefer": "rust",
    "zottenwurm": "flesh",
    "aktenfresser": "paper",
    "marzipanschwein": "dough",
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
    sample_drop: tuple[str, float] | None = None
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
- `next_waypoint` aktualisiert `cache: PathCacheEntry` nur, wenn `now - cache.updated_at >= PATH_CACHE_TTL` oder sich das Ziel signifikant verschoben hat.

---

## V4 Fraktionen (`src/factions.py`)

```python
FACTIONS: tuple[str, ...] = (
    "spieler",
    "wildnis",
    "fleischwelt",
    "aktenhalde",
    "glibbria",
    "kruemelreich",
    "sporenklub",
    "abtei",
    "schrott",
    "pilze",
    "parasiten",
    "behoerde",
    "backwerk",
    "tiefsee",
    "insekten",
    "automaten",
    "zirkus",
    "haendler",
    "boese_ichs",
)

HATE_MATRIX: dict[str, frozenset[str]] = {...}


def are_hostile(
    faction_a: str,
    faction_b: str,
    grudges: set[tuple[str, str]] | None = None,
) -> bool:
    """Return True if faction_a and faction_b are hostile by default or via grudges."""
    ...


def record_grudge(
    grudges: set[tuple[str, str]],
    faction_a: str,
    faction_b: str,
) -> None:
    """Record a symmetric blood feud between faction_a and faction_b."""
    ...


class Grudges:
    """Objektorientierter Wrapper um ein symmetrisches Blutfehden-Set."""
    def __init__(self) -> None: ...
    def add(self, faction_a: str, faction_b: str) -> None: ...
    def has(self, faction_a: str, faction_b: str) -> bool: ...
    def to_data(self) -> list[list[str]]: ...
    @classmethod
    def from_data(cls, data: list[list[str]]) -> Grudges: ...
```

- `"haendler"` ist von Natur aus gegen **niemanden** feindselig (wird erst durch `record_grudge` nach Angriff feindselig).
- `"behoerde"` ist standardmäßig feindselig gegenüber `"spieler"` und Wildnis-/Universums-Fraktionen.
- `record_grudge(grudges, a, b)` trägt `(a, b)` und `(b, a)` symmetrisch ein (ignoriert `a == b`).

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

### 2. Trink-Schübe (`Flask.drink` in `src/flask.py`)

`Flask.drink(target: Body | Player, blood_heals: bool = False) -> str` unterstützt sowohl die kanonischen Bibel-Flüssigkeiten als auch die allgemeinen Flüssigkeits-Schlüssel:

| Material-Key | Sofortwirkung auf `body` / `player` |
| --- | --- |
| `"water"` | `burning = 0.0`, `wet = max(wet, 3.0)`, heilt leicht / setzt `refresh_time = 15.0` |
| `"blood"` | heilt `+6.0..15.0 HP` (mit `blood_heals` oder direkt), löscht `poisoned = 0.0` |
| `"acid"` | verursacht Säureschaden (`hurt`) |
| `"oil"`, `"tallow"` | setzt `oily = 8.0`, `lubed_time = 15.0` |
| `"lava"`, `"magma"` | verursacht Feuerschaden (`hurt`) und setzt `burning > 0` |
| `"slime"`, `"mucus"` | löscht `burning = 0.0`, setzt `sticky` / milde Heilung |
| `"pus"` | setzt `poisoned = 8.0` |
| `"fluxschnaps"`, `"broth"` | setzt `drunk > 0` (und heilt bei `"broth"`) |
| `"tinte"`, `"ink"` | setzt `marked_time > 0` / `ink_sight = 20.0` |
| `"stempelfarbe"` | setzt `stamped_good = 15.0`, `stamped_bad = 0.0` |
| `"siegellack"` | verursacht Schaden und setzt `sticky = 5.0` |
| `"brausesirup"` | setzt `fizzy_time = 20.0` |
| `"kaugummi"`, `"jelly"` | setzt `sticky > 0` |
| `"honig"`, `"honey"` | heilt / gewährt `instant_flux += 100.0` und setzt `sticky = 3.0` |
| `"karamell"` | verursacht leichten Schaden und setzt `sticky = 5.0` |
| `"neonsaft"`, `"milk"`, `"wax"`, `"brine"`, `"sap"`, `"mercury"` | gewährt den jeweiligen Spezialschub (`haste_time`, Heilung, Rüstung, `charged`, `sticky`, `frozen`) |
