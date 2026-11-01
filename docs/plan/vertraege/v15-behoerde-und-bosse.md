# Verträge V15–V17: Behörde für Realitätsordnung, Boss-Phasen, Böse Ichs & Hauptquartier

> Teil des Vertrags-Index [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md). Kanonische Quelle: [docs/bibel/04-behoerde-und-bosse.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/bibel/04-behoerde-und-bosse.md).

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
    "agent_sachbearbeiter",   # ab 1 Stern: verschießt Stempel-Projektile (Verlangsamung)
    "agent_vollstrecker",     # ab 2 Sternen: gepanzert, Aktenkoffer-Schild (reflect), Salvenfeuer
    "agent_abteilungsleiter", # ab 4 Sternen: fliegt, ruft Verstärkung, Paragraphen-Strahl
)


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
    def from_data(cls, data: dict[str, object] | None) -> Wanted:
        ...


def agent_species_for_stars(stars: int) -> list[str]:
    """Deterministische Liste der zu spawnenden Agenten-Spezies für gegebene Sterne (0..5):
    - 0: []
    - 1: ["agent_sachbearbeiter"]
    - 2: ["agent_sachbearbeiter", "agent_vollstrecker"]
    - 3: ["agent_sachbearbeiter", "agent_vollstrecker", "agent_vollstrecker"]
    - 4: ["agent_sachbearbeiter", "agent_vollstrecker", "agent_vollstrecker", "agent_abteilungsleiter"]
    - 5: ["agent_sachbearbeiter", "agent_sachbearbeiter", "agent_vollstrecker", "agent_vollstrecker", "agent_abteilungsleiter", "agent_abteilungsleiter"]
    """


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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enemies import Creature
    from ..run import Run


@dataclass(frozen=True)
class BossPhase:
    index: int
    hp_threshold: float          # Eintritt bei boss.body.hp / boss.body.max_hp <= hp_threshold
    name_de: str                 # z. B. "Notfall-Kompression"
    line_de: str                 # Deutsche Boss-Ansage beim Phasenwechsel
    attack_interval_scale: float = 1.0
    speed_scale: float = 1.0
    summon_species: str = ""
    summon_count: int = 0
    arena_hazard: str = ""       # "", "acid_rain", "steam_vents", "stamp_barrage", "frost_floor", "electric_arcs", "jelly_bounce"


class BossScript:
    """Basisklasse für alle 9 Endbosse, 3 Bösen Ichs und Ober-Cloita."""

    boss_key: str = ""
    title_de: str = ""
    phases: tuple[BossPhase, ...] = ()

    def __init__(self, boss: Creature) -> None:
        self.boss: Creature = boss
        self.phase: int = 0
        self.phase_timer: float = 0.0
        self.invuln_timer: float = 0.0
        self.hazard_timer: float = 0.0

    def update(self, dt: float, run: Run) -> None:
        """Prüft HP-Schwellen für Phasenwechsel, tickt invuln_timer (1.0 s Unverwundbarkeit
        nach Phasenwechsel) und führt phasenspezifische Angriffe/Arena-Effekte in tick_phase aus."""

    def phase_change(self, new_phase: int, run: Run) -> None:
        """Setzt self.phase = new_phase, self.phase_timer = 0.0, self.invuln_timer = 1.0,
        spawnt ggf. summon_species, ruft run.boss_line(phase_spec.line_de) und
        run.emit('boss_phase', boss_key=self.boss_key, phase=new_phase, line_de=phase_spec.line_de) auf."""

    def tick_phase(self, dt: float, run: Run) -> None:
        """Wird von Unterklassen überschrieben oder nutzt die deklarativen BossPhase-Felder."""

    def on_death(self, run: Run) -> None:
        """Standard-Tod: schaltet Ausgangsportal frei, dropt Wächter-Kern ('probe_kern') + Boss-Beute."""


def make_boss_script(boss: Creature) -> BossScript | None:
    """Fabrikfunktion: liefert die passende BossScript-Instanz für boss.species
    (alle 9 Universums-Endbosse, 3 Böse Ichs, 'ober_cloita'), sonst None."""
```

### Kanonische Phasenschwellen

- **3-Phasen-Bosse** (9 Universums-Endbosse + 3 Böse Ichs):
  - Phase `0`: Start (`hp_threshold = 1.0`)
  - Phase `1`: bei `hp_ratio <= 0.66` (`1.0 s` Unverwundbarkeit während Übergang)
  - Phase `2`: bei `hp_ratio <= 0.33` (`1.0 s` Unverwundbarkeit während Übergang)
- **4-Phasen-Boss (`ober_cloita`)**:
  - Phase `0`: Start (`1.0`, *"Akte geschlossen? Noch lange nicht!"*)
  - Phase `1`: `hp_ratio <= 0.75` (*"Formular B-12: Beschwörung der Beamtenschaft!"*)
  - Phase `2`: `hp_ratio <= 0.50` (*"Paragraph 9: Realitäts-Kompression!"*)
  - Phase `3`: `hp_ratio <= 0.25` (*"Total-Revision! Alles wird gestempelt!"*)

### Die 9 Universums-Endboss-Module unter `src/bosses/`

| Datei | `boss_key` | Universum | Phasen-Kernthema (`arena_hazard` / Summons) |
| --- | --- | --- | --- |
| `src/bosses/schrott.py` | `"schrottpresse"` | `schrott` | Stampf-Wellen, Schrottregen, Magnet-Anziehung + `rostkaefer`-Summons |
| `src/bosses/myzel.py` | `"muttermyzel"` | `myzel` | Sporenwolken, Wurzel-Ausbrüche, Teilungs-Sprossen (`sporenwerfer`) |
| `src/bosses/magen.py` | `"pfuetzenkoenig"` | `magen` | `"acid_rain"`, steigender Magensaft-Pegel, `saeurespucker`-Summons |
| `src/bosses/amt.py` | `"oberamtsrat"` | `amt` | `"stamp_barrage"`, Stempel-Schockwellen, ruft `agent_sachbearbeiter` |
| `src/bosses/kuchen.py` | `"hochzeitstorte"` | `kuchen` | 3 Torten-Etagen schmelzen nacheinander ab, Karamell-Boden, `kerzenkobold`-Summons |
| `src/bosses/abtei.py` | `"abt_nautilus"` | `abtei` | Gezeiten-Strömungswechsel, Glocken-Schallwellen, `moenchsfisch`-Chor |
| `src/bosses/ameisen.py` | `"koenigin_mandibula"` | `ameisen` | Pheromon-Fokus, Harz-Käfige, `ameisensoldat`-Wellen |
| `src/bosses/spule.py` | `"transformator"` | `spule` | `"electric_arcs"`, Polaritätswechsel (`pull`/`push`), `funkenhornisse`-Summons |
| `src/bosses/glibber.py` | `"zirkusdirektor"` | `glibber` | `"jelly_bounce"`, Beat-Pflicht-Salven, teilt Mini-Klone (`quallenhund`) |

---

## V17 — Böse Ichs (`src/bosses/evil_selves.py`) & Hauptquartier (`src/bosses/headquarters.py`)

### 1. Böse Ichs (`src/bosses/evil_selves.py`)

```python
EVIL_SELVES: tuple[str, ...] = (
    "boese_kaiserin",  # Universum 2 (depth == 2) im Secret-Raum
    "boese_gute",      # Universum 3 (depth == 3) im Secret-Raum
    "boese_omega",     # Universum 4 (depth == 4) im Secret-Raum
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

#### Eintrittsbedingung nach dem Endboss in Universum 5 (`depth == 5`)

- Standard-Ausgangsportal führt zum normalen Sieg (`victory = True`).
- Hat die Spielerin **`run.badges >= 3` oder `run.wanted.stars >= 4`**, erscheint neben dem normalen Ausgang ein zweites, rot-goldenes **Behörden-Portal** (`"portal_headquarters"`).
- Betritt die Spielerin dieses Portal (oder wird `run.enter_headquarters()` aufgerufen), wechselt `run.in_headquarters = True` und lädt die 3-stufige Arena (`320 × 200` Zellen):

```python
HQ_STAGES: tuple[str, ...] = (
    "anhoerung",   # Stufe 1: Welle aus 4 Behörden-Agenten + Stempel-Geschützen
    "boese_ichs",  # Stufe 2: Alle noch NICHT im Run besiegten Bösen Ichs (falls alle 3 schon besiegt: 2 Elite-Abteilungsleiter)
    "ober_cloita", # Stufe 3: 4-Phasen-Endkampf gegen 'ober_cloita'
)
```

- Sieg über `"ober_cloita"` setzt `run.victory = True`, `run.true_ending = True` und vergibt den Rang `"Realitäts-Rebellin"` (`+500` Bonus-Punkte).
