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
    from src.body import Body
    from src.enemies import Creature
    from src.factions import Grudges
    from src.projectiles import ProjectileSystem
    from src.world import World

STANCES: tuple[str, ...] = ("hostile", "neutral", "passive", "trader")
ABILITY_KEYS: tuple[str, ...] = (
    "graze", "pack", "hunt", "retaliate", "dig", "steal", "split", "flee",
    "transform", "ranged", "melee", "shield", "reflect", "armor", "summon", "stationary",
)
# Projectile form keys from src/spells.py (both old and new keys) that count as piercing for "armor":
PIERCING_FORMS: frozenset[str] = frozenset({
    "nadel", "nadelschuss", "knochenspeer", "durchschlagbolzen",
    "nadelregen", "knochensaege", "kreissaege",
})
GRAZE_MATERIAL: dict[str, str] = {
    "huepfling": "zuckerguss",
    "blattlaus": "zucker",
}
SPLIT_SIZES: dict[str, tuple[tuple[int, int], ...]] = {
    "glibberteiler": ((18, 14), (12, 10), (8, 7)),
}

@dataclass
class BehaviourContext:
    world: World
    player: Body
    creatures: list[Creature]                 # alle lebenden Kreaturen der Welt
    projectiles: ProjectileSystem
    rng: random.Random
    dt: float
    grudges: Grudges | None = None
    on_beat: bool = True                      # rule_beat: False außerhalb der ersten 50 % des Takts
    events: list[tuple[str, dict[str, Any]]] = field(default_factory=list)  # Ausgabe an Run.emit (V12)

class Ability:
    key: ClassVar[str] = ""

    def __init__(self, creature: Creature, params: dict[str, float]) -> None:
        self.creature = creature
        self.params = params

    def update(self, ctx: BehaviourContext) -> None:
        pass

    def on_hurt(
        self, ctx: BehaviourContext, amount: float, source: tuple[float, float] | None, cause: str = ""
    ) -> float:
        return amount

    def wants_move(self, ctx: BehaviourContext) -> tuple[float, float] | None:
        return None

ABILITIES: dict[str, type[Ability]] = {}

def register(cls: type[Ability]) -> type[Ability]: ...
def build_abilities(creature: Creature) -> list[Ability]: ...
def update_behaviour(creature: Creature, ctx: BehaviourContext) -> None: ...
```

- Materialien in Parametern immer als **Schlüssel** (nie als ID).
- `build_abilities(creature)` liest `dict(creature.spec.ability_params)`. Ist ein Schlüssel in `creature.spec.abilities` weder in `ABILITY_KEYS` noch in `ABILITIES`, wirft `build_abilities` einen `ValueError(key)`.
- Wenn `creature.spec.stance not in ("passive", "trader")` und `"retaliate"` nicht in `creature.spec.abilities` steht, hängt `build_abilities` `"retaliate"` automatisch an (sobald `"retaliate"` in `ABILITIES` registriert ist).
- Reihenfolge in `update_behaviour(creature, ctx)`:
  1. Haltung & Sicht prüfen (`V1a`).
  2. Alle `ability.update(ctx)` in Reihenfolge von `creature.abilities` aufrufen.
  3. Erster nicht-`None`-Rückgabewert von `ability.wants_move(ctx)` bestimmt das Ziel `(tx, ty)`.
  4. Wenn `"stationary"` aktiv oder `creature.spec.stance == "trader"`: `creature.vx = creature.vy = 0.0`. Sonst wenn Ziel `(tx, ty)` vorhanden: `creature.steer_to(world, tx, ty, dt)` (nur wenn `ctx.on_beat` True ist). Sonst: Umherwandern (`creature._wander_step(world, dt)`).

### V1a Haltung und Aggro

- `Creature.aggro: bool` – gibt an, ob die Kreatur aktiv angreift.
- `hostile`: `aggro = True`, sobald sie ihr Ziel (Spieler oder verfeindete Kreatur laut `V4`) innerhalb von `spec.sight` sieht (`can_see`) oder `player.smells_like_ant` (bei `ameisenkrieger`).
- `neutral`: startet mit `aggro = False`; wird bei `hurt(..., amount > 0)` auf `aggro = True` gesetzt (und teilt dies bei `"pack"` mit ihrer `group_id`). Ausnahme `stempler`: bewegt sich auch mit `aggro = False` langsam auf den Spieler zu, wenn Abstand `< 90 px`, um einmalig zu stempeln.
- `passive`: `aggro` ist immer `False`; `hurt(..., amount > 0)` setzt `creature.fleeing = True` (für `8.0 s`).
- `trader`: `aggro` ist immer `False`, bewegt sich nie; `hurt(..., amount > 0)` hängt `("trader_hurt", {"key": creature.spec.key, "x": creature.x, "y": creature.y})` an `ctx.events` an.

### V1b Neue Felder in `CreatureSpec` (`src/enemies.py`)

Alle neuen Felder stehen am Ende von `CreatureSpec` und besitzen Standardwerte, sodass bestehende Kreaturen unverändert funktionieren:

```python
    stance: str = "hostile"
    abilities: tuple[str, ...] = ()                      # leer = alter Codepfad in Creature.update
    ability_params: tuple[tuple[str, float], ...] = ()   # z. B. (("dig_hardness", 2.0), ("flee_distance", 80.0))
    faction: str = "native"                              # V4: "native" | "authority" | "evil_self"
    windup: float = 0.4                                  # Ausholzeit in s (wird auf >= 0.4 geklemmt)
    group_size: tuple[int, int] = (1, 1)                 # (min, max) Gruppengröße beim Spawnen
    gold: tuple[int, int] = (0, 0)                       # (min, max) Gold auf Rang 1
    drops: tuple[tuple[str, float], ...] = ()            # ((item_key, chance_0_to_1), ...)
    sandbox_only: bool = False                           # True = nicht mehr in regulären Läufen spawnen
```

### V1c Neue Felder und Methoden in `Creature` (`src/enemies.py`)

```python
    state: str = "idle"                                  # V2 Animations-/Verhaltenszustand
    state_time: float = 0.0                              # Sekunden im aktuellen Zustand
    attack_kind: str = ""                                # z. B. "melee", "ranged", "stamp"
    aggro: bool = False
    fleeing: bool = False
    flee_timer: float = 0.0
    group_id: int = 0                                    # >0: gleiche Gruppe teilt Aggro (pack)
    generation: int = 0                                  # >0: Teilungs-Generation (split)
    carrying: dict[str, Any] | None = None               # gestohlener Gegenstand (steal), siehe V12
    bribed: bool = False                                 # Türsteherpilz bestochen
    giver: bool = False                                  # Auftraggeber einer Herausforderung (V13)
    chorus_buff: float = 0.0                             # Mönchsfisch-Chor-Timer
    last_hit_from: tuple[float, float] | None = None
    last_attacker_species: str = ""                      # Art des Schützen bei Fremdbeschuss (V4)
    path: list[tuple[int, int]] = []
    abilities: list[Ability]                             # erzeugt durch build_abilities(self)

    def steer_to(self, world: World, x: float, y: float, dt: float) -> None: ...
    def hurt(
        self,
        amount: float,
        cause: str = "",
        source: tuple[float, float] | None = None,
        ctx: BehaviourContext | None = None,
        attacker_species: str = "",
    ) -> None: ...
```

- Signatur von `EnemyManager.update` bleibt abwärtskompatibel:

  ```python
  def update(
      self,
      world: World,
      dt: float,
      player: Body,
      projectiles: ProjectileSystem,
      area: Rect,
      *,
      grudges: Grudges | None = None,
      on_beat: bool = True,
      out_events: list[tuple[str, dict[str, Any]]] | None = None,
  ) -> list[Creature]:
  ```

  `EnemyManager.update` baut pro Aufruf einen `BehaviourContext`, reicht `out_events` (falls übergeben) als `ctx.events` durch und gibt wie bisher `died: list[Creature]` zurück. Dadurch brechen bestehende Aufrufer in Tests nie.

---

## V2 Zustände und Ausholen (`src/enemies.py`)

- `MIN_WINDUP = 0.4`. Effektive Ausholzeit: `max(MIN_WINDUP, self.spec.windup)`.
- Standardzustände: `"idle"`, `"move"`, `"windup"`, `"attack"`, `"hurt"`, `"death"` + Sonderzustände (`"dig"`, `"stamp"`, `"hang"`, `"latched"`, `"squash"`, `"burrow_out"`, `"steal"`, `"carry"`, `"phase_change"`).
- `Creature.set_state(name: str) -> None`: setzt `self.state = name` und `self.state_time = 0.0` (wenn `self.state != name`).
- `Creature.begin_attack(kind: str) -> bool`:
  - Gibt `False` zurück, wenn `self.state in ("windup", "attack")` oder die zugehörige Abklingzeit (`attack_cooldown` für `"melee"`/`"stamp"`, `ranged_cooldown` für `"ranged"`) `> 0` ist.
  - Setzt sonst `self.attack_kind = kind`, `self.set_state("windup")` und gibt `True` zurück.
- `Creature.poll_attack_ready() -> str`:
  - Wenn `self.state == "windup"` und `self.state_time >= max(MIN_WINDUP, self.spec.windup)`, wechselt die Kreatur nach `self.set_state("attack")` und gibt `self.attack_kind` zurück (genau in diesem Frame wird der Schlag/Schuss ausgelöst!). Sonst `""`.
  - Nach `0.2 s` in `"attack"` wechselt die Kreatur automatisch zurück nach `"idle"`.
- `hurt` setzt `self.set_state("hurt")` für `0.15 s`, **außer** `self.state == "windup"` (`windup` wird durch `hurt` nicht abgebrochen).

---

## V3 Wegsuche (`src/pathfind.py`)

```python
GRID = 4  # Weltpixel pro Wegsuch-Zelle

def find_path(
    world: World,
    start: tuple[float, float],
    goal: tuple[float, float],
    body_w: int,
    body_h: int,
    *,
    flying: bool,
    max_nodes: int = 3000,
) -> list[tuple[int, int]] | None: ...

class PathFollower:
    def __init__(self, repath_interval: float = 0.5) -> None: ...
    def next_waypoint(
        self, creature: Creature, world: World, goal: tuple[float, float], dt: float
    ) -> tuple[float, float] | None: ...
```

- A* auf einem Gitter mit `GRID = 4` px Zellengröße, 8 Nachbarn (gerade Kosten `1.0`, diagonal `1.414`).
- Eine Gitterzelle `(gx, gy)` entspricht der Weltposition `(gx * GRID, gy * GRID)` (obere linke Ecke der Box) und ist begehbar, wenn `!world.rect_blocked(gx * GRID, gy * GRID, body_w, body_h)`.
- Wenn `flying == False`: hat die Zelle keinen festen Boden innerhalb von `4 px` unterhalb der Box (`!world.rect_blocked(gx * GRID, gy * GRID + 4, body_w, body_h)`), erhöhen sich die Schrittkosten um `+4.0`.
- Rückgabewert von `find_path`: Liste von Welt-Mittelpunkten `[(wx, wy), ...]` vom ersten Schritt bis zum Ziel, oder `None` wenn unmöglich / `max_nodes` überschritten. Wirft niemals Exceptions.

---

## V4 Fraktionen (`src/factions.py`)

```python
PLAYER = "player"
NATIVE = "native"
AUTHORITY = "authority"
EVIL_SELF = "evil_self"

class Grudges:
    def __init__(self) -> None: ...
    def add(self, species_a: str, species_b: str) -> None: ...
    def has(self, species_a: str, species_b: str) -> bool: ...
    def to_data(self) -> list[list[str]]: ...
    @classmethod
    def from_data(cls, data: list[list[str]]) -> Grudges: ...

def hostile(a: Creature, b: Creature, grudges: Grudges | None = None) -> bool: ...
```

- `Grudges.add(a, b)` ignoriert `a == b` und speichert Paare symmetrisch (`frozenset({a, b})`).
- `hostile(a, b, grudges)` ist `True`, wenn:
  - `a is not b` und keine der beiden `spec.prop` oder `spec.stance == "trader"` ist, UND
  - `(a.spec.faction == AUTHORITY and b.spec.faction != AUTHORITY)` oder umgekehrt, ODER
  - `(a.spec.faction == NATIVE and b.spec.faction == NATIVE and grudges is not None and grudges.has(a.spec.key, b.spec.key))`.
- In `src/projectiles.py` trägt `Projectile` neu `owner_species: str = ""` und `source_pos: tuple[float, float] | None = None`. Trifft ein Geschoss mit `p.team == ENEMY_TEAM`, darf es andere `Creature`-Instanzen treffen, wenn `p.owner_species != ""` und `p.owner_species != victim.spec.key` (bei Kollateraltreffer oder aktivem Streit).

---

## V4b Neue Status-Effekte & Flüssigkeits-Schübe (`src/body.py`, `src/player.py`, `src/flask.py`)

### 1. Neue Status-Felder auf `Body` (`src/body.py`)

Alle als `float = 0.0` (Restdauer in Sekunden), in `Body.place` mit `0.0` initialisiert und in `apply_environment` pro Frame um `dt` reduziert:

| Feld auf `Body` | Bedeutung / Wirkung |
| --- | --- |
| `drunk: float = 0.0` | Beschwipst: Waffen-Flux lädt `× 1.5` schneller (`Wand.update`), Zielwinkel schwankt um `sin(age * 9) * 0.18` rad |
| `sticky: float = 0.0` | Klebrig (durch `kaugummi`, `honig`, `karamell`, `siegellack`): Horizontalbewegung `× 0.5`, Sprunggeschwindigkeit `× 0.7` (außer `mucus_immune` / `rutschfest`) |
| `stamped_good: float = 0.0` | Genehmigt: verursachter Schaden `× 1.2` |
| `stamped_bad: float = 0.0` | Abgelehnt: verursachter Schaden `× 0.8` (setzt `stamped_good = 0.0` und umgekehrt) |
| `marked_time: float = 0.0` | Tintenblick / Drohnen-Markierung: durch Wände sichtbar (`Run.update_visibility`); ist `player.marked_time > 0`, kennen alle `authority`-Agenten Cloitas Position |
| `frozen: float = 0.0` | Unterkühlt: Bewegung `× 0.6` |
| `charged: float = 0.0` | Elektrisch geladen: nächster Kontakt/Treffer entlädt `10.0` Stromschaden |
| `befogged: float = 0.0` | Benebelt (`weihrauch`): Zielstreuung von Kreaturen `× 2.0` |

### 2. Neue Trink-Schübe auf `Player` (`src/player.py` & `src/flask.py`)

Zusätzliche Timer-Felder auf `Player` (`float = 0.0`):

- `refresh_time: float = 0.0` (Wasser: Flux-Regeneration `× 1.2`, löscht `burning`)
- `lubed_time: float = 0.0` (Öl/Talg: `cast_delay × 0.85`, setzt `oily = 8.0`)
- `fizzy_time: float = 0.0` (Brausesirup: `JUMP_SPEED × 1.5`)
- `haste_time: float = 0.0` (Neonsaft: `RUN_SPEED × 1.3`)
- `instant_flux: float = 0.0` (Honig: `Run._use_flask` addiert `player.instant_flux` sofort auf `wand.mana` und setzt es auf `0.0`)

Vollständige Tabelle für `Flask.drink(player, *, blood_heals: bool = False) -> str` (Bibel 06 „Flüssigkeiten: Schübe beim Trinken“):

| Material-Key | Sofortwirkung auf `player` |
| --- | --- |
| `"water"` | `burning = 0.0`, `refresh_time = 15.0` |
| `"oil"`, `"tallow"` | `lubed_time = 15.0`, `oily = 8.0` |
| `"fluxschnaps"` | `drunk = 20.0` |
| `"acid"` | `player.hurt(25.0, "Getrunken: Magensäure")` |
| `"blood"` | `player.hp = min(player.max_hp, player.hp + 6.0)` wenn `blood_heals` |
| `"tinte"` | `player.ink_sight = 20.0` (alle Kreaturen in `Run.update_visibility` sichtbar) |
| `"stempelfarbe"` | `stamped_good = 15.0`, `stamped_bad = 0.0` |
| `"siegellack"` | `player.hurt(15.0, "Getrunken: Siegellack")`, `sticky = 5.0` |
| `"brausesirup"` | `fizzy_time = 20.0` |
| `"kaugummi"` | `sticky = 5.0` |
| `"honig"` | `instant_flux += 100.0`, `sticky = 3.0` |
| `"karamell"` | `player.hurt(10.0, "Getrunken: Karamell")`, `sticky = 5.0` |
| `"neonsaft"` | `haste_time = 20.0` |
