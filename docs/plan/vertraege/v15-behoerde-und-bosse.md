# Verträge V15–V17: Behörde für Realitätsordnung, Boss-Phasen, Böse Ichs & Hauptquartier

> Teil des Vertrags-Index [vertraege.md](../vertraege.md). Kanonische Quellen: [docs/bibel/04-figuren.md](../../bibel/04-figuren.md), [docs/bibel/05-gegner.md](../../bibel/05-gegner.md).

---

## V15 — Fahndungslevel & Behörden-Agenten (`src/authority.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enemies import Creature
    from .run import Run

WANTED_MAX: float = 5.0

AGENT_TYPES: tuple[str, ...] = (
    "agent_streife",          # (Alias: "agent_sachbearbeiter") ab 1 Stern: Stempel-Projektile
    "agent_drohne",           # fliegende Späh- und Markierdrohne
    "agent_vollstrecker",     # ab 2 Sternen: gepanzert, Aktenkoffer-Schild (reflect), Salvenfeuer
    "agent_abteilungsleiter", # ab 4 Sternen: fliegt, ruft Verstärkung, Paragraphen-Strahl
)

AGENT_ALIASES: dict[str, str] = {
    "agent_sachbearbeiter": "agent_streife",
}


@dataclass
class Wanted:
    level: float = 0.0
    crimes: list[str] = field(default_factory=list)
    cells_destroyed_total: int = 0
    _cells_carry: int = 0

    @property
    def stars(self) -> int:
        """Ganze Fahndungssterne 0..5 (abgerundet, geklemmt auf 0..5)."""
        return max(0, min(5, int(self.level)))

    def add(self, delta: float, reason: str) -> bool:
        """Ändert level um delta (geklemmt auf 0.0..WANTED_MAX).
        Fügt reason zu crimes hinzu (max. 20 letzte Einträge), wenn delta > 0.
        Gibt True zurück, wenn sich self.level tatsächlich geändert hat."""

    def on_cells_destroyed(self, count: int) -> bool:
        """Zählt zerstörte Zellen hoch. Je 500 zerstörte Zellen steigt level um +0.25
        mit Grund 'Sachbeschädigung'. Gibt True zurück, wenn level gestiegen ist."""

    def on_workshop(self) -> bool:
        """Baut in der Werkstatt automatisch -0.5 Fahndungslevel ab ('Aktenablage').
        Gibt True zurück, wenn level gesunken ist."""

    def bribe_cost(self) -> int:
        """Kosten am Akten-Schredder (ws_shredder) für -1.0 Fahndungslevel:
        40 + 25 * self.stars Gold."""
        return 40 + 25 * self.stars

    def agent_count(self) -> int:
        """Anzahl der beim Universums-Eintritt zu spawnenden Behörden-Agenten:
        0 Sterne -> 0, 1 Stern -> 1, 2 Sterne -> 2, 3 Sterne -> 3, 4 Sterne -> 4, 5 Sterne -> 6."""

    def to_data(self) -> dict[str, object]:
        return {
            "level": round(self.level, 4),
            "crimes": list(self.crimes[-20:]),
            "cells_destroyed_total": self.cells_destroyed_total,
            "cells_carry": self._cells_carry,
        }

    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Wanted: ...


def agent_species_for_stars(stars: int) -> list[str]:
    """Deterministische Liste der zu spawnenden Agenten-Spezies für gegebene Sterne (0..5)."""


def spawn_agents(run: Run, count: int | None = None) -> list[Creature]:
    """Spawnt Behörden-Agenten in der Nähe von run.level.spawn (Mindestabstand 48 px,
    Maximalabstand 140 px auf freien Luftzellen).
    Gibt die Liste der erzeugten Creature-Instanzen zurück."""
```

### Fahndungs-Auslöser (Übersicht)

| Vergehen | `delta` | `reason` |
| --- | --- | --- |
| Je `500` zerstörte Weltzellen | `+0.25` | `"Sachbeschädigung"` |
| Verbotener Zauber gewirkt (`nuke`, `black_hole`, `omega`) | `+0.5` | `"Verbotene Magie"` |
| Ladendiebstahl | `+1.0` | `"Ladendiebstahl"` |
| Händler verletzt | `+1.5` | `"Händler angegriffen"` |
| Händler getötet | `+3.0` | `"Händler getötet"` |
| Werkstatt betreten (`on_workshop`) | `-0.5` | `"Aktenablage"` |
| Akten-Schredder bezahlt (`ws_shredder`) | `-1.0` | `"Akten geschreddert"` |

---

## V16 — Mehrphasige Boss-Skripte (`src/bosses/__init__.py`)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enemies import Creature
    from ..run import Run


@dataclass(frozen=True)
class BossPhase:
    index: int
    hp_threshold: float          # Eintritt bei boss.hp / boss.max_hp <= hp_threshold
    name_de: str                 # z. B. "Notfall-Kompression"
    line_de: str                 # Deutsche Boss-Ansage beim Phasenwechsel
    attack_interval_scale: float = 1.0
    speed_scale: float = 1.0
    summon_species: str = ""
    summon_count: int = 0
    arena_hazard: str = ""       # "", "acid_rain", "steam_vents", "stamp_barrage", "frost_floor", "electric_arcs", "jelly_bounce"


class BossScript:
    """Basisklasse für alle 6 Universums-Zwischengegner, 3 Bösen Ichs und Ober-Cloita."""

    boss_key: str = ""
    title_de: str = ""
    phases: tuple[BossPhase, ...] = ()

    def __init__(self, boss: Creature) -> None:
        self.boss: Creature = boss
        self.phase: int = 0
        self.phase_timer: float = 0.0
        self.invuln_timer: float = 0.0
        self.hazard_timer: float = 0.0

    def update(self, dt: float, run: Run) -> None: ...
    def phase_change(self, new_phase: int, run: Run) -> None: ...
    def tick_phase(self, dt: float, run: Run) -> None: ...
    def on_death(self, run: Run) -> None: ...


def apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run) -> None:
    """Wendet periodische Arena-Gefahren während eines Bosskampfs an."""


def make_boss_script(boss: Creature) -> BossScript | None:
    """Fabrikfunktion: liefert die passende BossScript-Instanz für boss.species
    (alle 6 Universums-Zwischengegner, 3 Bösen Ichs, 'ober_cloita'), sonst None."""
```

### Kanonische Phasenschwellen

- **3-Phasen-Bosse** (6 Universums-Zwischengegner + 3 Böse Ichs):
  - Phase `0`: Start (`hp_threshold = 1.0`)
  - Phase `1`: bei `hp_ratio <= 0.66` (`1.0 s` Unverwundbarkeit während Übergang)
  - Phase `2`: bei `hp_ratio <= 0.33` (`1.0 s` Unverwundbarkeit während Übergang)
- **4-Phasen-Boss (`ober_cloita`)**:
  - Phase `0`: Start (`1.0`, *"Akte geschlossen? Noch lange nicht!"*)
  - Phase `1`: `hp_ratio <= 0.75` (*"Formular B-12: Beschwörung der Beamtenschaft!"*)
  - Phase `2`: `hp_ratio <= 0.50` (*"Paragraph 9: Realitäts-Kompression!"*)
  - Phase `3`: `hp_ratio <= 0.25` (*"Total-Revision! Alles wird gestempelt!"*)

### Die 6 kanonischen Universums-Zwischengegner in `src/bosses/` (Bibel Kap. 03 & 05)

| `boss_key` | Universum | Deutscher Name | Phasen-Kernthema (`arena_hazard` / Summons) |
| --- | --- | --- | --- |
| `"weltenherz"` | `fleischwelt` | `"Das Weltenherz"` | `"acid_rain"`, Blutpuls, ruft `zottenwurm` / `saeurespucker` |
| `"oberstempler"` | `aktenhalde` | `"Der Oberstempler"` | `"stamp_barrage"`, Stempel-Schockwellen, ruft `aktenfresser` / `agent_streife` |
| `"mutter_glibber"` | `glibbria` | `"Mutter Glibber"` | `"jelly_bounce"`, Brause-Eruptionen, teilt `glibberteiler` |
| `"ameisenkoenigin"` | `kruemelreich` | `"Die Ameisenkönigin"` | `"steam_vents"`, Pheromon-Fokus, ruft `ameisenkrieger` |
| `"dj_myzel"` | `sporenklub` | `"DJ Myzel"` | `"electric_arcs"`, Bass-Schallwellen im Takt, ruft `sporentraeger` |
| `"abt_kieme"` | `abtei` | `"Abt Kieme"` | `"frost_floor"`, Glocken-Schallwellen, ruft `moenchsfisch`-Chor |

*(Zusätzlich akzeptiert `make_boss_script` als Rückwärtskompatibilitäts-Aliase auch die Pool-/Legacy-Schlüssel `"pfuetzenkoenig"`, `"oberamtsrat"`, `"zirkusdirektor"`, `"koenigin_mandibula"`, `"muttermyzel"`, `"abt_nautilus"`, `"schrottpresse"`, `"hochzeitstorte"`, `"transformator"`).*

---

## V17 — Böse Ichs (`src/bosses/evil_selves.py`) & Hauptquartier (`src/bosses/headquarters.py`)

### 1. Böse Ichs (`src/bosses/evil_selves.py`)

```python
EVIL_SELVES: tuple[str, ...] = (
    "boese_kaiserin",  # Optionale Begegnung in Universum 2 (depth == 2) im Secret-Raum + Kaiserin-Handel
    "boese_gute",      # Optionale Begegnung in Universum 3 (depth == 3) im Secret-Raum
    "boese_omega",     # Optionale Begegnung in Universum 4 (depth == 4) im Secret-Raum
)

def evil_self_for_depth(depth: int) -> str | None:
    """Gibt für depth 2 -> 'boese_kaiserin', depth 3 -> 'boese_gute',
    depth 4 -> 'boese_omega' zurück, sonst None."""

def signature_wand_for_evil_self(species: str) -> Wand:
    """Erzeugt den einzigartigen Signatur-Zauberstab, den das besiegte Böse Ich fallen lässt:
    - 'boese_kaiserin': 'Kaiserliches Zepter' (Mana 180, Recharge 0.22, vorbestückt mit ['chain', 'lance', 'spark'])
    - 'boese_gute':     'Heiligenschein-Gerte' (Mana 200, Recharge 0.18, vorbestückt mit ['heal', 'shield', 'orb'])
    - 'boese_omega':    'Omega-Prisma' (Mana 260, Recharge 0.30, vorbestückt mit ['omega', 'split_cast', 'plasma'])
    """

def apply_empress_bargain(run: Run, accepted: bool) -> None:
    """Wird im Kaiserin-Handel-Menü aufgerufen:
    - accepted == False: Kampf gegen 'boese_kaiserin' beginnt normal.
    - accepted == True: 'boese_kaiserin' verschwindet friedlich, lässt 'Kaiserliches Zepter' + 100 Gold
      fallen, erhöht aber Wanted um +2.0 ('Pakt mit der Kaiserin') und reduziert player.body.max_hp um 20 %."""
```

Tod eines Bösen Ichs:

- Ruft `run.records.discover("evil_self", species)` auf.
- Dropt den Signatur-Zauberstab (`signature_wand_for_evil_self(species)`), `1` `"badge"` (`"dienstmarke"`) und `1` `"memory_shard"`.

### 2. Hauptquartier & Wahres Ende (`src/bosses/headquarters.py`)

#### Eintrittsbedingung (`can_enter_headquarters(run: Run) -> bool`)

- Gibt `True` zurück, wenn die Spielerin **alle `6` Erinnerungssplitter (`run.memory_shards >= 6`)** gesammelt hat **ODER** mindestens **`3` Dienstausweise (`run.badges >= 3`)** besitzt **ODER** **`run.wanted.stars >= 4`** erreicht hat.
- Betritt die Spielerin das Hauptquartier-Portal (`run.enter_headquarters()`), wechselt `run.in_headquarters = True` und lädt die 3-stufige Arena (`320 × 200` Zellen):

```python
HQ_STAGES: tuple[str, ...] = (
    "anhoerung",   # Stufe 1: Welle aus 4 Behörden-Agenten + Stempel-Geschützen
    "boese_ichs",  # Stufe 2: Alle noch NICHT im Run besiegten Bösen Ichs (falls alle 3 schon besiegt: 2 Elite-Abteilungsleiter)
    "ober_cloita", # Stufe 3: 4-Phasen-Endkampf gegen 'ober_cloita'
)

def can_enter_headquarters(run: Run) -> bool: ...
def generate_headquarters_arena(world: World) -> tuple[int, int]: ...

class HeadquartersController:
    def __init__(self) -> None:
        self.stage_index: int = 0
        self.completed: bool = False
    def spawn_stage(self, run: Run) -> None: ...
    def update(self, dt: float, run: Run) -> None: ...
```

- Sieg über `"ober_cloita"` setzt `run.victory = True`, `run.true_ending = True` und vergibt den Rang `"Realitäts-Rebellin"` (`+500` Bonus-Punkte).
