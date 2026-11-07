# Verträge V18–V20: Werkstatt, Wirtschaft, Händler, Fabrikator & Minispiele

> Teil des Vertrags-Index [vertraege.md](../vertraege.md). Kanonische Quellen: [Bibel 07](../../bibel/07-gegenstaende-und-werkstatt.md) (Werkstatt, Minispiele), [Bibel 02](../../bibel/02-systeme.md) („Wirtschaft“, „Fabrikator“), [Bibel 04](../../bibel/04-figuren.md) („Händler“). Überarbeitet am 2026-11-04 nach der Prüfung gegen die Bibel.

---

## V18 — Die Werkstatt (`src/workshop.py`)

```python
WORKSHOP_SIZE: tuple[int, int] = (640, 360)  # Zellen (Breite, Höhe)

@dataclass(frozen=True)
class Station:
    key: str             # Bibel-Schlüssel, z. B. "ws_portal"; dient auch als Sprite-Schlüssel in umgebung/
    name: str            # Deutscher Anzeigename aus Bibel 07
    rect: tuple[int, int, int, int]  # (x0, y0, x1, y1) in Welt-Zellen, Größe laut Bibel 07
    prompt_de: str       # Hinweis für Hover/HUD, z. B. "[E] Fabrikator benutzen"

    @property
    def sprite_key(self) -> str:
        return self.key

@dataclass(frozen=True)
class WorkshopLayout:
    width: int
    height: int
    spawn: tuple[int, int]                         # Spieler-Spawn in Zellen
    klonita_pos: tuple[int, int]                   # auf der Couch
    trader_slots: tuple[tuple[int, int], tuple[int, int]]  # Mitte der beiden 32×32-Händlerplätze
    target_dummy_pos: tuple[int, int]              # rechtes Ende der Schießstand-Bahn
    stations: dict[str, Station]                   # key -> Station
```

### Die 12 Stationen (`STATIONS`, Bibel 07 „Stationen“)

Alle Stationen stehen auf der Hauptplattform (Bodenoberkante `y = 210`, Innenraum `x = 40..600`), von links nach rechts mit 10 Zellen Abstand. Breite × Höhe stammen aus Bibel 07.

| `key` | `name` | Größe | `rect` | Funktion bei `[E]` (`Run.interact_station`) |
| --- | --- | --- | --- | --- |
| `"ws_couch"` | `"Klonitas Couch"` | 40×18 | `(40, 192, 80, 210)` | Klonita sitzt hier. `[E]`: Spruch aus `LINES["couch"]` und einmal je Besuch `+35 %` `max_hp` Heilung |
| `"ws_liege"` | `"Experimentierliege"` | 48×24 | `(90, 186, 138, 210)` | Öffnet die Experiment-Auswahl (`menu_mode = "experiment"`): 3 Selbstexperimente zur Wahl, 1 je Besuch; neu würfeln gegen `experiment_reroll_price` |
| `"ws_fabrikator"` | `"Fabrikator"` | 40×40 | `(148, 170, 188, 210)` | Öffnet das Fabrikator-Menü (`menu_mode = "fabricator"`, höchstens 3 Bauten je Besuch) |
| `"ws_werkbank"` | `"Werkbank"` | 48×28 | `(198, 182, 246, 210)` | Öffnet den Rucksack im Umbau-Modus (`inventory_open = True`) |
| `"ws_haendler"` | `"Händlerplatz"` | 72×32 | `(256, 178, 328, 210)` | Zwei Händlerplätze (je 32×32); `[E]` am nächsten Händler öffnet sein Kaufmenü (`menu_mode = "trader"`) |
| `"ws_zapfhahn"` | `"Schnapszapfanlage"` | 16×24 | `(338, 186, 354, 210)` | Füllt den gehaltenen Kolben für `10` Gold mit `"fluxschnaps"` (voll) |
| `"ws_well"` | `"Flaschen-Brunnen"` | 16×18 | `(364, 192, 380, 210)` | Füllt den gehaltenen Kolben kostenlos mit `"water"` (voll) |
| `"ws_automat"` | `"Physik-o-Mat"` | 24×36 | `(390, 174, 414, 210)` | Startet ein Physik-Rätsel (Einsatz `30` Gold, 1 Versuch je Besuch) |
| `"ws_schiessstand"` | `"Schießstand"` | 64×24 | `(424, 186, 488, 210)` | Startet das Zielschießen (Einsatz `20` Gold, 1 Versuch je Besuch) |
| `"ws_archiv"` | `"Archivschrank"` | 24×32 | `(498, 178, 522, 210)` | Öffnet das Archiv (`menu_mode = "archive"`, 5 Reiter) |
| `"ws_shredder"` | `"Akten-Schredder"` | 16×20 | `(532, 190, 548, 210)` | Senkt `Wanted` um `1.0` gegen `Wanted.bribe_cost()` = `40 + 25 × Sterne` Gold |
| `"ws_portal"` | `"Portalrahmen"` | 40×48 | `(558, 162, 598, 210)` | Öffnet die Portal-Auswahl (`menu_mode = "portal_select"`, Vorschläge aus `run.plan.offers()`) |

- `spawn = (300, 200)`, `klonita_pos = (64, 190)`, `trader_slots = ((276, 194), (316, 194))`, `target_dummy_pos = (484, 196)`.
- `STATION_ALIASES` (`"ws_fabricator"`, `"ws_trader"`, `"ws_physik_o_mat"`, `"ws_archive"`, `"ws_workbench"` → Bibel-Schlüssel) bleibt für alte Spielstände; `layout.stations` nimmt beide Schlüssel an.
- **Betreten (`Run.enter_workshop`, Bibel 07 „sicherer Ort“):** volle Heilung, `wanted.on_workshop()`, `fabricator.reset_visit()`, `couch_used = False`, `minigames_played = set()`, `experiment_picked = False`, Händler neu besetzen (V19 §2), danach `save_state()`.

```python
def generate_workshop(world: World) -> WorkshopLayout:
    """Baut die 640×360-Werkstatt deterministisch in world (Ziegel-Halle aus "rock",
    Boden ab y = 210, Becken mit "water" unter ws_well) und gibt das Layout zurück."""

def station_at(layout: WorkshopLayout, cell_x: int, cell_y: int, radius: int = 10) -> Station | None:
    """Nächstgelegene Station, deren rect höchstens radius Zellen von (cell_x, cell_y) entfernt ist."""
```

---

## V19 — Wirtschaft (`src/economy.py`) & Händler (`src/traders.py`)

### 1. Gold- und Preisformeln (Bibel 02 „Wirtschaft (Gold)“)

`rank` ist der Rang des Universums (`1..3`), `stage` die Beutestufe (`1..6` = Nummer des Universums im Lauf, `run.plan.slot + 1`, in der Werkstatt die des nächsten Universums). Alle Funktionen sind rein.

```python
CREATURE_GOLD: dict[int, tuple[int, int]] = {1: (5, 10), 2: (10, 18), 3: (18, 30)}
BIG_CREATURE_GOLD: dict[int, int] = {1: 40, 2: 70, 3: 110}   # große Kreaturen und Unter-Zwischenbosse
BOSS_GOLD: dict[int, int] = {1: 200, 2: 350, 3: 500}         # Zwischengegner
PILES_PER_UNIVERSE: tuple[int, int] = (6, 8)
MODULE_BASE: dict[int, int] = {1: 50, 2: 85, 3: 120}         # nach Block.rarity_tier
PHYSIK_STAKE = 30
SCHIESS_STAKE = 20
ZAPF_PRICE = 10

def creature_gold(rank: int, rng: random.Random, *, big: bool = False) -> int:
    """big: BIG_CREATURE_GOLD[rank]; sonst rng.randint(*CREATURE_GOLD[rank])."""

def mid_boss_gold(rank: int) -> int:
    """Unter-Zwischenboss (spec.is_mid_boss): BIG_CREATURE_GOLD[rank]."""

def boss_gold(rank: int) -> int:
    """Zwischengegner: BOSS_GOLD[rank]."""

def pile_gold(rank: int, rng: random.Random) -> int:
    """Goldhaufen: rng.randint(10, 40) * rank."""

def crate_gold(rank: int, rng: random.Random) -> int:
    """Fundkiste: rng.randint(20, 60) * rank (dazu 1–3 Gegenstände, siehe loot.py)."""

def module_price(rarity_tier: int, stage: int, price_factor: float = 1.0) -> int:
    """round(MODULE_BASE[rarity_tier] * (1 + 0.25 * stage) * price_factor)."""

def weapon_price(stage: int, price_factor: float = 1.0) -> int:
    """round((160 + 70 * (stage - 1)) * price_factor)."""

def fabricator_gold(rarity_tier: int, stage: int) -> int:
    """round(module_price(rarity_tier, stage) * 0.7)."""

def experiment_reroll_price(reroll_index: int) -> int:
    """100 * 2 ** reroll_index (100, 200, 400, …; Zähler gilt für den ganzen Lauf)."""
```

`price_factor` fasst Rabatte zusammen: Selbstexperiment `feilscher` (Bibel: `feilscherin`) × `2/3`. Weitere Faktoren gibt es im MVP nicht.

### 2. Die 6 Händler (Bibel 04 „Händler“)

Händler stehen **nur in der Werkstatt**. Jedes besuchte Universum bringt seinen Heimat-Händler mit; es stehen höchstens 2 gleichzeitig da, nämlich die Händler der beiden zuletzt besuchten Universen (`traders_for_workshop`). Vor dem ersten Universum ist der Händlerplatz leer.

```python
@dataclass(frozen=True)
class TraderOffer:
    kind: str            # "block" oder "wand"
    key: str             # Block-Schlüssel; "" bei "wand"
    gold_cost: int       # Goldpreis inkl. Sonderregel
    sample_cost: tuple[tuple[str, int], ...] = ()  # Proben-Tausch (nur Krümel-Karl)
    blessing: str = ""   # Küster-Segen: "mana_max", "recharge" oder "capacity"

@dataclass(frozen=True)
class TraderSpec:
    key: str
    name: str
    home_universe: str
    greeting_de: str
    quirk_de: str
    category: str        # "PAYLOAD", "TRIGGER", "MODIFIER", "ANY", "FORM" oder "WAND"
    price_multiplier: float = 1.0
    flat_fee: int = 0
```

| `key` | `name` | `home_universe` | `category` | Sonderregel |
| --- | --- | --- | --- | --- |
| `"npc_magenhaendler"` | `"Herr Pansen"` | `"fleischwelt"` | `"PAYLOAD"` | nur Füllungen mit einem eigenen Material des Satzes `"fleischwelt"` (nicht in `BASE_KEYS`): Blut-, Säure-, Glutfüllung |
| `"npc_sachbearbeiterin"` | `"Frau Abheft"` | `"aktenhalde"` | `"TRIGGER"` | `flat_fee = 10` („Bearbeitungsgebühr“) auf jedes Angebot |
| `"npc_glibberhaendler"` | `"Wobbel"` | `"glibbria"` | `"MODIFIER"` | keine |
| `"npc_ameisenhehler"` | `"Krümel-Karl"` | `"kruemelreich"` | `"ANY"` | `price_multiplier = 0.75`; jedes Angebot alternativ gegen `2` × `"probe_zuckerkristall"` (`sample_cost`) |
| `"npc_dj"` | `"DJ Lamelle"` | `"sporenklub"` | `"FORM"` | Kauf nur auf dem Beat: in der Werkstatt `int(run.time / 0.75) % 2 == 0`, sonst `(False, "Nicht im Takt!")` |
| `"npc_kuester"` | `"Bruder Flosse"` | `"abtei"` | `"WAND"` | jede Waffe gesegnet: zufällig `"mana_max"` (+10 %), `"recharge"` (−10 %) oder `"capacity"` (+1 Platz) |

```python
def traders_for_workshop(visited: list[str]) -> list[TraderSpec]:
    """Heimat-Händler der (höchstens) zwei zuletzt besuchten Universen, neuestes zuerst."""

def generate_offers(trader: TraderSpec, stage: int, rng: random.Random, *,
                    price_factor: float = 1.0) -> list[TraderOffer]:
    """4 Angebote aus trader.category (retired-Blöcke ausgenommen), Preise nach §1."""

def buy_offer(run: Run, trader: TraderSpec, offer: TraderOffer, *,
              use_samples: bool = False) -> tuple[bool, str]:
    """Kauf ausführen; (ok, deutscher Text). Zu wenig Gold: (False, "Zu wenig Gold.")."""
```

---

## V20 — Fabrikator (`src/fabricator.py`) & Minispiele (`src/minigames/`)

### 1. Fabrikator (Bibel 02 „Fabrikator (Handwerk)“)

- **Bauplan:** Jedes Modul, das Cloita je besessen hat, steht in `records.blueprints`. Ohne Bauplan kein Bau.
- **Proben je Kategorie:** Geschoss 1, Aufsatz 1, Zünder 2, Füllung 1. Füllungen mit Universumsmaterial brauchen die Probe genau dieses Universums (`SAMPLES` mit passendem `universe_key`); bei allen anderen zählt jede der 12 Universums-Proben.
- **Höhere Seltenheit** (Bibel 07 „Allgemeine Proben“): `rarity_tier == 2` zusätzlich 1 Probe aus `("probe_knochen", "probe_aether", "probe_schatten")`; `rarity_tier == 3` zusätzlich 1 Probe aus `("probe_gold", "probe_kern")` **und** 1 Bauplan-Splitter (`run.blueprint_shards`).
- **Gold:** `fabricator_gold(rarity_tier, stage)`.
- **Grenze:** `MAX_BUILDS_PER_VISIT = 3`.

```python
@dataclass(frozen=True)
class Recipe:
    block_key: str
    rarity_tier: int
    universe_samples: int                 # Anzahl Universums-Proben
    universe: str | None                  # nur bei Füllungen mit Universumsmaterial, sonst None
    special_samples: tuple[str, ...]      # erlaubte Zusatzproben (eine davon nötig), () bei Stufe 1
    blueprint_shards: int                 # 1 bei Stufe 3, sonst 0
    gold: int

def build_cost(block_key: str, stage: int = 1) -> Recipe: ...

class Fabricator:
    builds_this_visit: int
    def reset_visit(self) -> None: ...
    def can_build(self, run: Run, block_key: str) -> tuple[bool, str]: ...
    def craft(self, run: Run, block_key: str) -> tuple[bool, str]:
        """Zieht Gold, Proben (die meistvorhandenen zuerst) und ggf. 1 Splitter ab, legt das Modul in den Rucksack."""
```

### 2. Minispiele (Bibel 07 „Minispiele“)

Beide nutzen die echte Physik in einer eigenen `160×120`-Welt. Je Minispiel höchstens ein Versuch pro Werkstatt-Besuch; der Einsatz wird beim Start abgezogen.

```python
MINIGAME_WORLD_SIZE = (160, 120)
NEXT_BOOST_KEYS = ("flux", "damage", "speed")   # Flux-Aufladung +20 %, Schaden +10 %, Lauftempo +10 %, je für das nächste Universum

@dataclass
class MinigameResult:
    completed: bool
    won: bool
    reward_gold: int = 0
    reward_sample: str = ""
    next_boost: str = ""
    message_de: str = ""

class Minigame:
    key: str
    title_de: str
    stake: int
    time_limit: float
    result: MinigameResult | None
    def step(self, dt: float, action: str | None = None,
             cursor: tuple[int, int] = (80, 60)) -> MinigameResult | None: ...
```

**Physik-o-Mat** (`src/minigames/physik_o_mat.py`, Einsatz `PHYSIK_STAKE`): Ein Rätsel im Rahmen, 15 s Zeit. Aktionen am `cursor`: `"blast"` (Explosion Radius 6), `"dig"` (Loch Radius 3), `"ignite"` (Feuer), `"pour"` (das Rätsel-Material des Werkzeugs). Eigener Materialsatz `"physik_o_mat"` = Grundmaterialien + `"magma"`, `"acid"`, `"papier"`, `"zucker"`, `"tallow"` (Docht/Kerze), `"enamel"` (Vase/Glas). Sieg: rng wählt `PHYSIK_STAKE * 2` Gold, eine zufällige Universums-Probe oder einen Schub.

| `key` | Bibel-Rätsel | Aufbau & Siegbedingung |
| --- | --- | --- |
| `"glas_fuellen"` | Füll das Glas | Wasserbecken oben, Glas aus `"enamel"` unten; nur `"blast"`/`"dig"`. Sieg: `>= 40` Wasserzellen im Glas |
| `"vase_retten"` | Rette die Vase | Turm aus `"rock"` neben einer Vase (Prop mit 1 Leben); Sieg: Turm `<= 20 %` seiner Zellen, Vase heil (keine Explosion näher als 10 Zellen an der Vase) |
| `"kerze_zuenden"` | Zünde die Kerze | Öl, Papier und Wasser zwischen Startfeuer-Punkt und Kerze aus `"tallow"`; Sieg: Kerze brennt |
| `"ameisenstrasse"` | Ameisenstraße | 5 Ameisen laufen zum nächsten `"zucker"`; Sieg: `>= 3` Ameisen im Ziel |
| `"lava_water"` | Lava-Brücke | Magma-Becken, Wasser hinter einem Riegel; Sieg: `>= 24` `"rock"`-Zellen in der Brückenzone |
| `"acid_gold"` | Säure-Tresor | Säure hinter einem Riegel, Kammer hinter `"dirt"`; Sieg: Kammer offen (Luftweg) |
| `"oil_fire"` | Docht-Kette | Öl ausgießen, 3 Dochte aus `"tallow"`; Sieg: alle 3 brennen |

Das achte Bibel-Rätsel „Stromkreis“ (`electricity_water`) kommt mit `rule_electric` in Phase J (`tasks/todo_erweiterung.md`).

```python
PUZZLE_KEYS = ("glas_fuellen", "vase_retten", "kerze_zuenden", "ameisenstrasse",
               "lava_water", "acid_gold", "oil_fire")
def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame: ...
def solve_actions(puzzle_key: str) -> list[tuple[str, tuple[int, int]]]:
    """Feste Lösungsfolge für Tests und den Playtest-Bot."""
```

**Schießstand** (`src/minigames/schiessstand.py`, Einsatz `SCHIESS_STAKE`): 30 s. Pappfiguren tauchen auf: Agenten (`kind = "agent"`, `+1` Punkt) und Klonita (`kind = "klonita"`, `−3` Punkte, nicht treffen!). Schuss = `action == "shoot"` am `cursor`, trifft im Radius 8. Belohnung: ab `8` Punkten ein zufälliger Schub aus `NEXT_BOOST_KEYS`, ab `14` Punkten zusätzlich `SCHIESS_STAKE * 2` Gold.

```python
@dataclass
class ShootingTarget:
    x: float
    y: float
    kind: str            # "agent" oder "klonita"
    visible_time: float
    hit: bool = False

class SchiessstandMinigame(Minigame):
    targets: list[ShootingTarget]   # feste Folge aus dem Seed (24 Agenten, 6 Klonitas)
    score: int
```
