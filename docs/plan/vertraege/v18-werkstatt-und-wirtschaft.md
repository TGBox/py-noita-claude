# Verträge V18–V20: Werkstatt-Hub, Wirtschaft, Händler, Fabrikator & Minispiele

> Teil des Vertrags-Index [vertraege.md](../vertraege.md). Kanonische Quelle: [docs/bibel/07-gegenstaende-und-werkstatt.md](../../bibel/07-gegenstaende-und-werkstatt.md).

---

## V18 — Die Werkstatt (`src/workshop.py`)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World

WORKSHOP_SIZE: tuple[int, int] = (640, 360)  # Zellen (Breite, Höhe)


@dataclass(frozen=True)
class Station:
    key: str             # "ws_portal", "ws_fabrikator", ...
    name: str            # Deutscher Anzeigename
    rect: tuple[int, int, int, int]  # (x0, y0, x1, y1) in Welt-Zellen
    prompt_de: str       # Interaktionshinweis für Hover/HUD, z. B. "[E] Fabrikator öffnen"
    sprite_key: str      # Schlüssel in umgebung/ ("portal_stein", "fabrikator", ...)


@dataclass(frozen=True)
class WorkshopLayout:
    width: int
    height: int
    spawn: tuple[int, int]                  # Spieler-Spawn in Zellen
    klonita_pos: tuple[int, int]            # Klonita-Stammplatz nahe der Couch
    trader_pos: tuple[int, int]             # Position des gastierenden Händlers
    target_dummy_pos: tuple[int, int]       # Position der Trainings-Attrappe
    stations: dict[str, Station]            # key -> Station
```

### Alle 12 kanonischen Werkstatt-Stationen (`STATIONS`) + `STATION_ALIASES`

Alle Koordinaten liegen auf der Hauptplattform (`y = 210` Bodenoberkante, Innenraum `x = 40..600`, `y = 140..210` Luft):

| Kanonischer Bibel-`key` | Englischer Alias (`STATION_ALIASES`) | `name` | `rect` `(x0, y0, x1, y1)` | `sprite_key` | Funktion bei `[E]` |
| --- | --- | --- | --- | --- | --- |
| `"ws_portal"` | — | `"Reise-Portal"` | `(548, 186, 572, 210)` | `"portal_stein"` | Öffnet die Portal-Auswahl (`2` Universums-Angebote aus `RunPlan.offers_for`) |
| `"ws_werkbank"` | `"ws_workbench"` | `"Zauberstab-Werkbank"` | `(176, 192, 196, 210)` | `"werkbank"` | Erlaubt freies Umsortieren von Zauberstab-Modulen + Reroll |
| `"ws_fabrikator"` | `"ws_fabricator"` | `"Fabrikator"` | `(140, 190, 160, 210)` | `"fabrikator"` | Öffnet das Fabrikator-Menü (max. `3` Bauten pro Besuch) |
| `"ws_liege"` | — | `"Experimentier-Liege"` | `(118, 194, 136, 210)` | `"experimentier_liege"` | Öffnet die Experiment-Auswahl (`1` aus `3` Perks pro Besuch) |
| `"ws_haendler"` | `"ws_trader"` | `"Händler-Stand"` | `(210, 186, 238, 210)` | `"haendler_stand"` | Öffnet das Kauf-/Tauschmenü des aktuellen Händlers |
| `"ws_zapfhahn"` | — | `"Flüssigkeits-Zapfhahn"` | `(246, 190, 266, 210)` | `"zapfhahn"` | Füllt die Phiole mit einer wählbaren bekannten Flüssigkeit |
| `"ws_automat"` | `"ws_physik_o_mat"` | `"Physik-o-Mat"` | `(280, 186, 300, 210)` | `"physik_o_mat"` | Startet ein Material-Rätsel-Minispiel (`1×` pro Besuch) |
| `"ws_schiessstand"` | — | `"Schießstand"` | `(340, 190, 360, 210)` | `"schiessstand"` | Startet das Zielscheiben-Minispiel (`1×` pro Besuch) |
| `"ws_archiv"` | `"ws_archive"` | `"Archiv-Pult"` | `(400, 192, 416, 210)` | `"archiv_pult"` | Öffnet das Entdeckungs-Archiv (5 Reiter) |
| `"ws_couch"` | — | `"Klonitas Sofa"` | `(86, 194, 114, 210)` | `"klonita_sofa"` | Heilt `+35 %` `max_hp` (`1×` pro Besuch) und triggert ein Klonita-Gespräch |
| `"ws_shredder"` | — | `"Akten-Schredder"` | `(456, 190, 472, 210)` | `"akten_schredder"` | Senkt `Wanted` um `-1.0` gegen `Wanted.bribe_cost()` Gold |
| `"ws_well"` | — | `"Flaschen-Brunnen"` | `(500, 192, 516, 210)` | `"flaschen_brunnen"` | Füllt die gehaltene Flasche kostenlos mit `"water"` auf |

- Sowohl `STATIONS` als auch `layout.stations` unterstützen den Zugriff über die 12 kanonischen Bibel-Schlüssel **und** über die 5 englischen Aliase (`"ws_fabricator"`, `"ws_trader"`, `"ws_physik_o_mat"`, `"ws_archive"`, `"ws_workbench"` über `STATION_ALIASES`).

### Öffentliche Funktionen in `src/workshop.py`

```python
STATION_ALIASES: dict[str, str] = {
    "ws_fabricator": "ws_fabrikator",
    "ws_trader": "ws_haendler",
    "ws_physik_o_mat": "ws_automat",
    "ws_archive": "ws_archiv",
    "ws_workbench": "ws_werkbank",
}

def generate_workshop(world: World) -> WorkshopLayout:
    """Baut die 640×360-Werkstatt deterministisch in world auf (Stein-/Ziegel-Halle,
    Becken am Flaschen-Brunnen, Schießstand-Nische) und gibt das WorkshopLayout zurück."""

def station_at(layout: WorkshopLayout, cell_x: int, cell_y: int, radius: int = 10) -> Station | None:
    """Gibt die nächstgelegene Station zurück, deren rect maximal radius Zellen von
    (cell_x, cell_y) entfernt ist, sonst None."""
```

---

## V19 — Wirtschaft (`src/economy.py`) & 6 Händler (`src/traders.py`)

### 1. Preis- und Beuteformeln (`src/economy.py`)

```python
from __future__ import annotations

import random


def creature_gold(max_hp: float, depth: int, rng: random.Random) -> int:
    """Gold-Drop einer Kreatur:
    base = max(1, int(round(max_hp / 12.0)))
    scale = 1.0 + 0.18 * max(0, depth - 1)
    return max(1, int(round(base * scale * rng.uniform(0.85, 1.15))))"""


def pile_gold(depth: int, rng: random.Random) -> int:
    """Goldhaufen in der Welt: round((8 + 4 * depth) * rng.uniform(0.8, 1.25))."""


def crate_gold(depth: int, rng: random.Random) -> int:
    """Beutekiste: round((18 + 7 * depth) * rng.uniform(0.85, 1.2))."""


def mid_boss_gold(depth: int) -> int:
    """Zwischenboss-Fixbetrag: 45 + 15 * depth."""


def module_price(rarity_tier: int, depth: int, price_factor: float = 1.0) -> int:
    """Basispreis nach Tier (1 -> 25, 2 -> 55, 3 -> 110),
    skaliert mit (1.0 + 0.12 * max(0, depth - 1)) * price_factor, mindestens 5."""


def weapon_price(wand_tier: int, depth: int, price_factor: float = 1.0) -> int:
    """Basispreis nach Tier (1 -> 65, 2 -> 125, 3 -> 210),
    skaliert mit (1.0 + 0.15 * max(0, depth - 1)) * price_factor, mindestens 15."""


def reroll_price(reroll_index: int, price_factor: float = 1.0) -> int:
    """Kosten für Angebots-Erneuerung: int(round((20 * (2 ** max(0, reroll_index))) * price_factor))."""
```

### 2. Die 6 Händler-Spezifikationen (`src/traders.py`, Bibel Kap. 07)

```python
@dataclass(frozen=True)
class TraderOffer:
    kind: str            # "block", "wand", "flask", "heart", "sample"
    key: str             # Block-Key, Sample-Key oder Leerstring bei wand/heart
    gold_cost: int       # Goldpreis (inkl. Händler-Eigenheit)
    sample_cost: tuple[tuple[str, int], ...] = ()  # Optionaler Proben-Tauschpreis (für Krümel-Karl)
    blessed: bool = False  # Küster-Segen auf Zauberstäben


@dataclass(frozen=True)
class TraderSpec:
    key: str             # "npc_magenhaendler", ...
    name: str            # "Herr Pansen", "Frau Abheft", ...
    home_universe: str   # "fleischwelt", "aktenhalde", "glibbria", "kruemelreich", "sporenklub", "abtei"
    greeting_de: str
    quirk_de: str        # Deutsche Kurzbeschreibung der Sonderregel für UI/Hover
    price_multiplier: float = 1.0
    flat_fee: int = 0
```

#### Kanonische Tabelle der 6 Händler (`TRADERS: dict[str, TraderSpec]`)

| `key` | `name` (Bibel Kap. 07) | `home_universe` | Verbindliche Sonderregel (`generate_offers` & `buy_offer`) |
| --- | --- | --- | --- |
| `"npc_magenhaendler"` | `"Herr Pansen"` | `"fleischwelt"` | Verkauft bevorzugt organische Payloads (`"spore"`, `"acid_orb"`, `"slime_arc"`, `"heal"`, `"blood_pact"`) + 1 Lebenskapsel (`"heart"`). |
| `"npc_sachbearbeiterin"` | `"Frau Abheft"` | `"aktenhalde"` | Erhebt auf **jedes** Angebot pauschal `+10` Gold Bearbeitungsgebühr (`flat_fee = 10`). Beim Kauf wird `player.body.stamped_good = 30.0` gesetzt (`-20 %` Preise, keine Agenten-Aggro). |
| `"npc_glibberhaendler"` | `"Wobbel"` | `"glibbria"` | Verkauft ausschließlich Flugbahn-/Modifikator-Module (`"bounce"`, `"split_cast"`, `"orbit"`, `"spiral"`, `"chaos"`, `"homing"`) und bunte Flaschen (`"brausesirup"`, `"kaugummi"`, `"jelly"`, `"honey"`). |
| `"npc_ameisenhehler"` | `"Krümel-Karl"` | `"kruemelreich"` | `price_multiplier = 0.75` (`25 %` Rabatt auf Goldpreise). Zusätzlich kann jedes Modul alternativ ohne Gold gegen **`2` Proben des aktuellen Universums** (`sample_cost`) eingetauscht werden! |
| `"npc_dj"` | `"DJ Lamelle"` | `"sporenklub"` | Verkauft Blitz-/Klang-Module (`"chain"`, `"lightning"`, `"beam"`, `"nova"`, `"echo"`). **Takt-Pflicht:** Ein Kauf in einem Universum mit aktivem Beat (`rule.beat_interval > 0`) ist nur während `rule.on_beat == True` möglich (sonst Rückgabe `False` + Sprechblase *"Nicht im Takt!"*); in der Werkstatt pulsiert ein eigener `0.75 s`-Takt (`int(run.time / 0.75) % 2 == 0`). |
| `"npc_kuester"` | `"Bruder Flosse"` | `"abtei"` | Verkauft geweihte Zauberstäbe und Schutz-Module (`"shield"`, `"heal"`, `"ice_lance"`). Jeder bei ihm gekaufte Zauberstab ist **gesegnet** (`blessed = True`: `mana_max` wird um `+10 %` erhöht und `recharge` um `-10 %` gesenkt). |

```python
def pick_trader_for_universe(universe_key: str, rng: random.Random) -> TraderSpec:
    """Wählt mit 60 % Wahrscheinlichkeit den Heimat-Händler des Universums (falls vorhanden),
    sonst gleichverteilt einen der 6 Händler."""

def generate_offers(
    trader: TraderSpec,
    depth: int,
    rng: random.Random,
    *,
    price_factor: float = 1.0,
    universe_sample_key: str = "probe_gallenstein",
) -> list[TraderOffer]:
    """Erzeugt deterministisch 4 Angebote passend zur Händler-Sonderregel."""

def buy_offer(
    run: Run,
    trader: TraderSpec,
    offer: TraderOffer,
    *,
    use_samples: bool = False,
) -> tuple[bool, str]:
    """Führt den Kauf von offer bei trader auf run aus und gibt (ok, msg_de) zurück."""
```

---

## V20 — Fabrikator (`src/fabricator.py`) & Minispiele (`src/minigames/__init__.py`)

### 1. Fabrikator (`src/fabricator.py`)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run

MAX_BUILDS_PER_VISIT: int = 3


@dataclass(frozen=True)
class Recipe:
    block_key: str
    rarity_tier: int
    samples: tuple[tuple[str, int], ...]  # ((sample_key, count), ...)
    gold: int


def build_cost(block_key: str) -> Recipe:
    """Deterministisches Rezept für jeden Zauberblock in src/spells.py (BLOCKS):
    - Tier 1: 2× Universums-Probe (aus den 12 kanonischen MVP-Proben) + 15 Gold
    - Tier 2: 3× Universums-Probe + 1× Tier-2-Probe ('probe_knochen'/'probe_aether'/'probe_schatten') + 35 Gold
    - Tier 3: 4× Universums-Probe + 1× Tier-3-Probe ('probe_gold'/'probe_kern') + 75 Gold"""


class Fabricator:
    def __init__(self) -> None:
        self.builds_this_visit: int = 0

    def reset_visit(self) -> None:
        self.builds_this_visit = 0

    def can_build(
        self,
        block_key: str,
        *,
        unlocked_blueprints: set[str],
        gold: int,
        sample_counts: dict[str, int],
    ) -> tuple[bool, str]: ...

    def craft(self, run: Run, block_key: str) -> tuple[bool, str]: ...
```

### 2. Werkstatt-Minispiele (`src/minigames/__init__.py`, `physik_o_mat.py`, `schiessstand.py`)

```python
MINIGAME_WORLD_SIZE: tuple[int, int] = (160, 120)

NEXT_BOOST_KEYS: tuple[str, ...] = (
    "mana_regen",   # +25 % Mana-Regeneration im nächsten Universum
    "max_hp",       # +20 temporäre Max-HP im nächsten Universum
    "gold_magnet",  # +25 % mehr Gold aus allen Quellen im nächsten Universum
    "discount",     # -20 % Händlerpreise im nächsten Universum
)


@dataclass
class MinigameResult:
    completed: bool
    won: bool
    reward_gold: int = 0
    reward_sample: str = ""
    next_boost: str = ""
    message_de: str = ""


class Minigame:
    key: str = ""
    title_de: str = ""
    time_limit: float = 20.0

    def __init__(self, seed: int = 0) -> None: ...
    def step(self, dt: float, action: str | None = None, cursor: tuple[int, int] = (80, 60)) -> MinigameResult | None: ...
```

#### Die 8 Physik-o-Mat-Rätsel (`PUZZLE_KEYS` in `src/minigames/physik_o_mat.py`, Bibel Kap. 07)

`PUZZLE_KEYS` umfasst die 4 klassischen Bibel-Rätsel und die 4 Elementar-Rätsel:

1. `"lava_water"`: Lava mit Wasser zu einer Steinbrücke (`>= 24` `"stone"`-Zellen) erstarren lassen.
2. `"acid_gold"`: Säure durch Kalkstein ätzen lassen, um die Goldkammer freizulegen.
3. `"oil_fire"`: Ölspur legen und alle `3` Docht-Ziele entzünden.
4. `"electricity_water"`: Salzwasser-Leitung zwischen zwei Elektroden schließen (`"spark"`).
5. `"glas_fuellen"`: Becher über Rinnen bis zur Markierung mit Flüssigkeit füllen.
6. `"vase_retten"`: Fallende Säure umlenken, bevor sie die Porzellanvase verätzt.
7. `"kerze_zuenden"`: Über Zündschnur und Öltropfen den Kerzendocht entflammen.
8. `"ameisenstrasse"`: Zuckerbrücke schütten, damit der Weg zum Ziel verbunden ist.

```python
PUZZLE_KEYS: tuple[str, ...] = (
    "lava_water",
    "acid_gold",
    "oil_fire",
    "electricity_water",
    "glas_fuellen",
    "vase_retten",
    "kerze_zuenden",
    "ameisenstrasse",
)

def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame: ...
```
