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
    "agent_streife",          # ab 1 Stern (Alias "agent_sachbearbeiter"): Formularblitz 8, Leben 45
    "agent_drohne",           # ab 2 Sternen: fliegt, markiert Cloita 10 s, Leben 15
    "agent_vollstrecker",     # ab 3 Sternen: Schild, reflect, Stempelschlag 20, Leben 120
    "agent_abteilungsleiter", # ab 4 Sternen: fliegt, ruft agent_streife, Paragraphen-Strahl 14, Leben 160
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

FORBIDDEN_BLOCKS: tuple[str, ...] = ("sprengkern", "knochenbombe")  # Bibel 06: Atomkern, Kraterbombe

AGENT_GOLD: dict[str, int] = {"agent_streife": 15, "agent_drohne": 5, "agent_vollstrecker": 40,
                              "agent_abteilungsleiter": 40}
BADGE_CHANCE: dict[str, float] = {"agent_streife": 0.10, "agent_drohne": 0.05, "agent_vollstrecker": 0.15,
                                  "agent_abteilungsleiter": 0.50}   # Dienstausweis (kind="badge")

def agent_species_for_stars(stars: int) -> list[str]:
    """Bibel 02: Streife ab 1, Drohne ab 2, Vollstrecker ab 3, Abteilungsleiter ab 4 Sternen.
    0 -> [], 1 -> [streife], 2 -> [streife, drohne], 3 -> [streife, drohne, vollstrecker],
    4 -> [streife, drohne, vollstrecker, abteilungsleiter],
    5 -> [streife, streife, drohne, vollstrecker, vollstrecker, abteilungsleiter]."""

def spawn_agents(run: Run, count: int | None = None) -> list[Creature]:
    """Spawnt Behörden-Agenten in der Nähe von run.level.spawn (Mindestabstand 48 px,
    Maximalabstand 140 px auf freien Luftzellen).
    Gibt die Liste der erzeugten Creature-Instanzen zurück."""
```

### Fahndungs-Auslöser (Übersicht)

| Vergehen | `delta` | `reason` |
| --- | --- | --- |
| Je `500` zerstörte Weltzellen | `+0.25` | `"Sachbeschädigung"` |
| Neutrale oder passive Kreatur getötet (`spec.stance` in `"peaceful"`, `"passive"`, `"neutral"`, `"territorial"`, `"shy"`) | `+0.25` | `"Unnötige Gewalt"` |
| Verbotener Großzauber gewirkt (`FORBIDDEN_BLOCKS`) | `+0.5` | `"Verbotene Magie"` |
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
    arena_hazard: str = ""       # "" oder einer der Schlüssel in ARENA_HAZARDS (unten)

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

ARENA_HAZARDS: tuple[str, ...] = ("acid_rain", "magma_veins", "sealing_wax", "closing_walls", "rising_water", "electric_water", "bass_drop", "spore_cloud")

def apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run) -> None:
    """Wendet periodische Arena-Gefahren während eines Bosskampfs an."""

def make_boss_script(boss: Creature) -> BossScript | None:
    """Fabrikfunktion: liefert die passende BossScript-Instanz für boss.species
    (alle 6 Universums-Zwischengegner, 3 Bösen Ichs, 'ober_cloita'), sonst None."""
```

### Kanonische Phasenschwellen (Bibel 05)

Jeder Phasenwechsel: `1.0 s` Unverwundbarkeit, Boss-Zeile über `run.boss_line`, `run.emit("boss_phase", …)`.

- **6 Zwischengegner:** 3 Phasen bei `1.0`, `0.66`, `0.33`.
- **3 böse Ichs im Endkampf:** 4 Phasen bei `1.0`, `0.75`, `0.50`, `0.25`.
- **Echos und böse Ichs im Hauptquartier (Stufe 2):** 2 Phasen bei `1.0`, `0.50`.
- **`ober_cloita`:** 3 Phasen bei `1.0`, `0.66`, `0.33`; Phase `k` nutzt die Angriffe des `k`-ten bösen Ichs in `EVIL_SELVES`, die letzte alle gemischt.

### Die 6 kanonischen Universums-Zwischengegner in `src/bosses/` (Bibel Kap. 03 & 05)

Phasen genau nach Bibel 05 („Zwischengegner“); Phase 1 gilt ab 100 %, Phase 2 ab 66 %, Phase 3 ab 33 % Leben. Zuordnung der Arena-Gefahren: Weltenherz P2 `magma_veins`; Oberstempler P1 `sealing_wax`, P3 `closing_walls`; Ameisenkönigin P3 `acid_rain`; DJ Myzel P2 `bass_drop`, P3 `spore_cloud`; Abt Kieme P2 `rising_water`, P3 `electric_water`. Mutter Glibber nutzt keine Arena-Gefahr.

| `boss_key` | Universum | Deutscher Name | Phase 1 | Phase 2 | Phase 3 |
| --- | --- | --- | --- | --- | --- |
| `"weltenherz"` | `fleischwelt` | `"Das Weltenherz"` | Blutfontänen im Herzschlag | Glutblut-Adern (`"magma"`) brechen auf, Fleisch wächst schneller nach | reißt sich los, rollt; ruft `fleischmade` |
| `"oberstempler"` | `aktenhalde` | `"Der Oberstempler"` | Stempelschläge (Ausholen 0,8 s), `"siegellack"`-Pfützen | verfolgende Formular-Geschosse; ruft 2 `agent_streife` | Aktendeckel-Wände fahren von beiden Seiten heran |
| `"mutter_glibber"` | `glibbria` | `"Mutter Glibber"` | Sprung mit Druckwelle (Ausholen 0,7 s) | teilt sich bei großem Treffer (bis 4 Kinder à 80 Leben) | zieht die Kinder ein und rollt |
| `"ameisenkoenigin"` | `kruemelreich` | `"Die Ameisenkönigin"` | legt Eier (→ `ameisenkrieger`), Säurestrahl | gräbt sich um, taucht nach Bodenbeben wieder auf | fliegt, Säureregen |
| `"dj_myzel"` | `sporenklub` | `"DJ Myzel"` | Schallringe im Takt | alle 8 Beats Bass-Drop, Tanzschwarm als Schild | zerstört das Pult, Sporenwolken (`drunk`) |
| `"abt_kieme"` | `abtei` | `"Abt Kieme"` | Orgelstöße durch Wasser, `moenchsfisch`-Chor | flutet die Arena schrittweise | Glockenschläge elektrisieren das Wasser |

---

## V17 — Böse Ichs (`src/bosses/evil_selves.py`), Endkampf & Hauptquartier (`src/bosses/headquarters.py`)

Kanonische Quellen: Bibel 02 („Aufbau eines Laufs“, „Wahres Ende“) und Bibel 05 („Böse Ichs“, „Wahres Ende“). Überarbeitet am 2026-11-04.

### 1. Böse Ichs, Endgegner & Echos

```python
EVIL_SELVES: tuple[str, ...] = ("boese_kaiserin", "boese_gute", "boese_omega")
EVIL_HP: dict[str, int] = {"boese_kaiserin": 3500, "boese_gute": 3200, "boese_omega": 3800}
ECHO_HP_FACTOR = 0.30
ECHO_DEPTHS: tuple[int, int] = (3, 5)   # erstes Universum von Rang 2 und Rang 3 (plan.slot + 1)
ECHO_GOLD = 100

def final_evil_self(run: Run) -> str:
    """Endgegner dieses Laufs: run.plan.evil_self (der Seed wählt, Bibel 02)."""

def echo_for_depth(run: Run, depth: int) -> str | None:
    """Echo im Geheimraum (level.secret): bei depth == 3 das erste, bei depth == 5 das zweite
    der beiden bösen Ichs, die nicht Endgegner sind (Reihenfolge wie in EVIL_SELVES); sonst None."""

def signature_wand_for_evil_self(species: str) -> Wand:
    """Waffe des bösen Ichs (Bibel 05: eigene Waffe mit Modulen), Code-Schlüssel aus BLOCKS:
    - 'boese_kaiserin': "Kaiserliches Zepter"  (mana_max 180, recharge 0.22) ['nadelregen', 'beschleunigung', 'sprengkraft']
    - 'boese_gute':     "Heiligenschein-Gerte" (mana_max 200, recharge 0.18) ['leuchtkugel', 'zielsuche', 'kettenfunke']
    - 'boese_omega':    "Omega-Armkanone"      (mana_max 260, recharge 0.30) ['feuerball', 'dreifach', 'zielsuche']"""

def apply_empress_bargain(run: Run, accepted: bool) -> None:
    """Angebot „die Hälfte des Multiversums“ (Phase 2 der Kaiserin, auch als Echo):
    - accepted == False: Kampf geht weiter.
    - accepted == True: Böses Ende. run.ending = "boese", run.outcome = "bad_ending" (beendet den Lauf wie "dead"), run.victory = False,
      run.records.discover("ending", "boese"); kein Weiterspielen."""
```

- **Echo:** Art wie das böse Ich, `hp = EVIL_HP * ECHO_HP_FACTOR`, 2 Phasen (V16). Tod: `ECHO_GOLD` Gold, `1` `"badge"` (Dienstausweis), `run.records.discover("evil_self", species)`.
- **Tod im Endkampf:** Signatur-Waffe, `run.records.discover("evil_self", species)`. Kein Erinnerungssplitter (es gibt genau 6, einen je Universum).

### 2. Endkampf in der Heimatwelt (`src/universes/gen/evil_homes.py`)

Nach dem 6. Universum bietet der Portalrahmen nur noch die Heimatwelt des Endgegners (`run.plan.finished`). Jede Heimatwelt ist `1280×720` groß, hat einen eigenen Materialsatz und eine Arena-Mechanik:

| Böses Ich | Heimatwelt | Materialsatz (Grundmaterialien +) | Mechanik |
| --- | --- | --- | --- |
| `boese_kaiserin` | Thronsaal aus Gold | `"goldboden"` (fest und rutschig: Bremsweg ×3) | Phase 4: der Thron wird zur Kanone (fester Punkt, schießt alle 1,2 s) |
| `boese_gute` | Kathedrale aus Licht | `"lichtstein"` (fest, leuchtet), `"heiliges_licht"` (Gas, 4 Schaden/s bei Berührung) | Lichtstrahlen hinterlassen `"heiliges_licht"`; Bekehrung: Klonita 10 s auf ihrer Seite (harmlos) |
| `boese_omega` | Fabrikhalle | `"foerderband"` (fest, schiebt Körper darauf mit 40 px/s), `"stahl"` (sehr hart) | 4 Pressen (alle 3 s, 30 Schaden im 16-px-Streifen); Phase 3: Riesenmaschine aus Teilen |

```python
def generate_evil_home(world: World, species: str, seed: int) -> Level:
    """Baut die Heimatwelt; Level.boss_arena = ganze Halle, Level.universe_key = species."""
```

- `Run.enter_final()` lädt die Heimatwelt, spawnt das böse Ich mit `EVIL_HP` und seinem 4-Phasen-Skript.
- **Sieg:** `run.victory = True`. Ist `can_enter_headquarters(run)` erfüllt, erscheint zusätzlich das Hauptquartier-Portal (`kind="portal"`, `item_key="headquarters"`); sonst endet der Lauf normal.

### 3. Hauptquartier & wahres Ende

```python
HQ_STAGES: tuple[str, ...] = ("anhoerung", "boese_ichs", "ober_cloita")
COUNCIL_SIZE = 5
OBER_CLOITA_HP = 6000

def can_enter_headquarters(run: Run) -> bool:
    """Bibel 02: run.memory_shards >= 6 or run.badges >= 3 or run.wanted.stars >= 4
    (geprüft nach dem Sieg über das böse Ich)."""

def generate_headquarters_arena(world: World) -> tuple[int, int]:
    """Endloser Aktensaal (960×360) mit Ratspult (120×32) am rechten Ende; gibt den Spawn zurück."""

class HeadquartersController:
    stage_index: int
    completed: bool
    def spawn_stage(self, run: Run) -> None: ...
    def update(self, dt: float, run: Run) -> None: ...
```

- **Eintritt:** kein Werkstatt-Besuch, volle Heilung (Boss-Zeile „Die Splitter erinnern sich an dich.“).
- **Stufe 1 „anhoerung“:** `COUNCIL_SIZE` Räte (`"ratsmitglied"`, Leben 90, `faction="behoerde"`, `ranged`) hinter dem Pult; solange einer lebt, alle 10 s 2 `"agent_streife"` und Formular-Regen. Jeder gefallene Rat verliert die Maske: `run.say` mit einer Zeile „Ich war die Cloita, die …“.
- **Stufe 2 „boese_ichs“:** die zwei bösen Ichs außer dem Endgegner nacheinander, je 2 Phasen (V16) und `50 %` von `EVIL_HP`.
- **Stufe 3 „ober_cloita“:** `OBER_CLOITA_HP`, 3 Phasen (V16). Je `10 %` verlorenes Leben fällt ein Kopf-Splitter (`kind="memory_shard"`, zählt nicht zu den 6); Klonita fängt ihn und gibt Cloita `+50` Flux. Zu Beginn von Phase 3 umarmt Klonita die Ober-Cloita: `3 s` gelähmt.
- **Sieg:** `run.victory = True`, `run.true_ending = True`, `run.records.discover("ending", "wahr")`.
