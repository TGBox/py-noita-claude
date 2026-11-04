# Verträge V21–V23: Klonita, UI/Menüs/Sprechblasen & Speicher-/Archiv-Schema

> Teil des Vertrags-Index [vertraege.md](../vertraege.md). Kanonische Quellen: [docs/bibel/02-systeme.md](../../bibel/02-systeme.md), [docs/bibel/04-figuren.md](../../bibel/04-figuren.md), [docs/bibel/08-ui-und-texte.md](../../bibel/08-ui-und-texte.md).

---

## V21 — Klonita-Begleiterin (`src/klonita.py` & `src/klonita_lines.py`)

### 1. Zustandsmaschine & Signatur (`src/klonita.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .run import Run

KLONITA_STATES: tuple[str, ...] = (
    "dismissed",  # Weggeschickt (in der Tasche), erscheint nur bei Auto-Triggern
    "follow",     # Folgt der Spielerin mit Schwebe-Offset (-18 px hinter ihr, +10 px oberhalb)
    "assist",     # Führt gerade eine Hilfsaktion aus (Schild, Snack, Funken, Entstempeln)
    "quirk",      # Einmal-pro-Universum-Missgeschick
    "knocked",    # Für 5.0 s benommen am Boden (unsterblich, steht danach wieder auf)
)

HELPERS: tuple[str, ...] = ("point", "carry", "hug")
QUIRKS: tuple[str, ...] = (
    "shiny_poke", "loud_sneeze", "sample_nibble",  # F13
    "tip_trader", "feed_creature", "warn_enemy",   # F17
)
QUIRK_CHANCE_PER_S = 0.02
POINT_RADIUS = 240.0
CARRY_MIN_RISE = 40.0
HUG_RADIUS = 80.0

AUTO_TRIGGERS: tuple[str, ...] = (
    "enter_universe",  # Beim Eintritt in ein neues Universum
    "player_low_hp",   # Wenn player.body.hp / player.body.max_hp < 0.25
    "boss_spawn",      # Wenn ein Zwischen- oder Endboss aktiviert wird
    "wanted_high",     # Wenn Wanted.stars >= 3 erreicht wird
    "event_start",     # Wenn ein Universums-Ereignis startet
)

@dataclass
class Klonita:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    hp: float = 60.0
    max_hp: float = 60.0
    state: str = "follow"
    knocked_timer: float = 0.0
    quirk_used_in_universe: bool = False
    cooldowns: dict[str, float] = field(
        default_factory=lambda: {
            "shield": 0.0,
            "snack": 0.0,
            "spark": 0.0,
            "cleanse": 0.0,
            "point": 0.0,
            "carry": 0.0,
        }
    )
    facing: int = 1
    pointing: tuple[float, float] | None = None
    point_timer: float = 0.0

    def toggle(self) -> str:
        """Schaltet per Taste [K] ('klonita'-Aktion in keybinds.py) zwischen 'dismissed'
        und 'follow' um (außer während 'knocked'). Gibt den neuen state zurück."""

    def on_trigger(self, trigger: str, run: Run) -> str | None:
        """Wird bei einem der 5 AUTO_TRIGGERS aufgerufen.
        Holt Klonita bei 'dismissed' kurzzeitig in 'follow' zurück und gibt eine passende
        deutsche Sprechblasen-Zeile aus src/klonita_lines.py zurück."""

    def take_damage(self, amount: float) -> bool:
        """Zieht Schaden ab. Fällt hp <= 0, stirbt Klonita NICHT, sondern wechselt für
        5.0 s in state = 'knocked' (knocked_timer = 5.0) und gibt True zurück."""

    def trigger_quirk(self, kind: str, run: Run) -> bool:
        """Führt einmal pro Universum eine der 6 QUIRKS aus (Abschnitt 3)."""

    def helper_point(self, run: Run) -> tuple[float, float] | None: ...  # Abschnitt 2b
    def helper_carry(self, run: Run) -> Pickup | None: ...               # Abschnitt 2b
    def helper_hug(self, run: Run) -> int: ...                           # Abschnitt 2b

    def update(self, dt: float, run: Run) -> None:
        """Bewegt Klonita weich hinter der Spielerin her (Teleport zur Spielerin bei
        Distanz > 220 px), tickt Cooldowns, führt Hilfsaktionen und maximal 1× pro
        Universum eine Quirk-Aktion aus."""

    def to_data(self) -> dict[str, object]: ...
    @classmethod
    def from_data(cls, data: dict[str, object] | None) -> Klonita: ...
```

### 2. Die 4 Hilfsaktionen (`assist`) & Cooldowns

| Schlüssel | Cooldown | Bedingung | Wirkung |
| --- | --- | --- | --- |
| `"shield"` | `18.0 s` | Feindliches Projektil näher als `28 px` an der Spielerin | Löscht das Projektil und erzeugt einen kurzen Schild-Funken |
| `"snack"` | `45.0 s` | `player.body.hp / player.body.max_hp < 0.35` **und** kein Bosskampf aktiv (`run.boss_script is None`) | Gibt der Spielerin einen Snack: `+15 HP` (höchstens `max_hp`), Sprechblase |
| `"spark"` | `4.5 s` | Feind näher als `90 px` | Verschießt einen schwachen lila Hilfsfunken (`6.0` Schaden) |
| `"cleanse"` | `22.0 s` | Spielerin brennt, ist gefroren oder hat `stamped_bad > 0` | Löscht Feuer/Frost bzw. setzt `stamped_bad = 0.0` |

### 2b. Die 4 Bibel-Aktionen (`helper`, Bibel 02 „Nützlich“) — Karten `F15`, `F16`

Entscheidung (2026-11-04): Klonita kombiniert die Bibel-Aktionen mit den 4 Hilfsaktionen aus Abschnitt 2. Das Spiel hat keinen Fallschaden, deshalb entfällt „Auffangen“. `cooldowns` erhält zusätzlich `"point"` und `"carry"`.

| Schlüssel | Cooldown | Bedingung | Wirkung | Methode |
| --- | --- | --- | --- | --- |
| `"point"` | `60.0 s` | Ziel näher als `POINT_RADIUS = 240 px` an Klonita: `run.level.secret` oder ein `Pickup` mit `kind` in `("life_capsule", "heart", "memory_shard")` | `self.pointing = (x, y)`, `self.point_timer = 3.0`, `run.emit("klonita_point", x=…, y=…)`; Klonita bleibt stehen, bis `point_timer` abgelaufen ist | `helper_point(run) -> tuple[float, float] \| None` |
| `"carry"` | `30.0 s` | Ein `Pickup` (nicht `kind="portal"`) liegt mehr als `CARRY_MIN_RISE = 40 px` über der Spielerin und horizontal näher als `200 px` | Setzt `pickup.x, pickup.y` auf die Position der Spielerin | `helper_carry(run) -> Pickup \| None` |
| `"hug"` | — (passiv, jedes `update`) | Kreatur mit `spec.stance` in `("peaceful", "passive", "territorial", "neutral")` näher als `HUG_RADIUS = 80 px` an Klonita | `creature.calmed = 0.5` (s); Rückgabe = Anzahl beruhigter Kreaturen | `helper_hug(run) -> int` |

Kreaturen-Felder (Karte `F15`, `src/enemies.py`): `Creature.calmed: float = 0.0` (zählt in `Creature.update` auf `0` herunter) und `Creature.dodge_charges: int = 0`. `evaluate_stance` (`src/enemies.py`): Kreaturen mit `territorial`/`neutral` und `calmed > 0` werden **nicht** durch Nähe der Spielerin aggressiv; Treffer (`was_hit`) und Gruppen-Aggro wirken weiter.

Während `state == "dismissed"` oder `"knocked"` laufen keine Aktionen.

### 3. Die 6 Macken (`quirk`) — Karten `F13`, `F17`

Alle Macken teilen sich `quirk_used_in_universe`: höchstens **eine** Macke je Universum (Bibel 02, Faustregel). `trigger_quirk(kind, run)` führt die Macke sofort aus und liefert `True`, wenn sie ausgelöst hat. Automatisch prüft `update` jede Sekunde jede Macke, deren Bedingung erfüllt ist, mit `QUIRK_CHANCE_PER_S = 0.02` (`run.rng`).

| Schlüssel | Bedingung | Wirkung | Karte |
| --- | --- | --- | --- |
| `"shiny_poke"` | explosive Kiste oder instabiles Fass näher als `40 px` | stupst es an (*„Oh, glänzt das?“*) | `F13` |
| `"loud_sneeze"` | schlafende Kreatur näher als `90 px` | `run.emit("noise", x=self.x, y=self.y, radius=90.0)` | `F13` |
| `"sample_nibble"` | `>= 5` Proben im Inventar | nascht `1` Tier-1-Probe, lässt sofort `15` Gold fallen (*„Schmeckt nach Wissenschaft!“*) | `F13` |
| `"tip_trader"` | Kreatur mit `spec.stance == "trader"` näher als `60 px` und `run.gold >= 5` | `run.gold -= min(run.gold, run.rng.randint(5, 15))` (*„Für Ihre Mühe!“*) | `F17` |
| `"feed_creature"` | Kreatur mit `spec.stance` in `("peaceful", "passive", "territorial", "neutral")` näher als `24 px` | Kreatur heilt `20 %` ihres `max_hp` (höchstens bis `max_hp`) | `F17` |
| `"warn_enemy"` | Kreatur mit `spec.stance == "hostile"` näher als `120 px` | `creature.dodge_charges += 1`; das nächste Geschoss der Spielerin, das diese Kreatur treffen würde, fliegt durch (`dodge_charges -= 1`, kein Schaden) (*„Pass auf, sie schießt gleich!“*) | `F17` |

### 4. Kommentar-Datenbank (`src/klonita_lines.py`)

```python
LINES: dict[str, tuple[str, ...]] = {
    # Kanonische 6 MVP-Universen (Bibel Kap. 03 & 08):
    "enter_fleischwelt": (...),
    "enter_aktenhalde": (...),
    "enter_glibbria": (...),
    "enter_kruemelreich": (...),
    "enter_sporenklub": (...),
    "enter_abtei": (...),
    # Auto-Trigger & Situationen:
    "player_low_hp": (...),
    "boss_spawn": (...),
    "wanted_high": (...),
    "event_start": (...),
    "couch": (...),
    "memory_shard": (...),
    "helper_point": (...),
    "helper_carry": (...),
    "quirk_tip_trader": (...),
    "quirk_feed_creature": (...),
    "quirk_warn_enemy": (...),
}

def line_for(topic: str, rng: random.Random) -> str:
    """Wählt deterministisch einen deutschen Spruch zum Thema topic (Fallback auf 'default')."""
```

---

## V22 — UI, Sprechblasen, Hover & Menüs (`src/hud.py`, `src/menus.py`, `src/hover.py`)

### 1. Sprechblasen (`SpeechBubble` in `src/hud.py` & Warteschlange auf `Run`)

```python
@dataclass
class SpeechBubble:
    speaker: str          # "Klonita", Boss-Name oder Händler-Name
    text: str             # Deutscher Anzeigetext
    x: float              # Welt-X oder Anker-X
    y: float              # Welt-Y oder Anker-Y
    ttl: float = 3.2      # Verbleibende Lebensdauer in Sekunden
    color: tuple[int, int, int] = (235, 225, 255)
```

- `Run.bubbles: list[SpeechBubble]` hält maximal `3` gleichzeitige Sprechblasen (älteste wird verdrängt).
- `Run.say(speaker: str, text: str, x: float, y: float, ttl: float = 3.2, color: tuple[int, int, int] = (235, 225, 255)) -> None` fügt eine Blase hinzu.
- `Run.boss_line(text_de: str) -> None` erzeugt eine hervorgehobene Boss-Sprechblase und setzt das Boss-Phasenbanner für `3.0 s`.

### 2. HUD-Erweiterung (`src/hud.py`)

`draw_hud` rendert zusätzlich zu HP, Luft, Mana, Zauberstäben, Flasche und Perks:

- **Gold-Anzeige:** Münz-Icon + `run.gold` oben rechts.
- **Fahndungssterne:** `0..5` Behörden-Sterne (`run.wanted.stars`) neben der Gold-Anzeige (ausgegraut bei `0`, gelb/rot pulsierend ab `1`).
- **Proben-Beutel-Zusammenfassung:** Anzahl belegter Proben-Slots (`len([s for s in inv.samples if s]) / 12`).
- **Aktives Event / aktive Challenge:** Einzeiliger kompakter Statusbalken unter der Regionsanzeige (`event.spec.name` + Restzeit bzw. `challenge.spec.name` + Status).
- **Sprechblasen:** Rendert `run.bubbles` in Bildschirmkoordinaten über dem jeweiligen Sprecher (geklemmt an den sichtbaren Viewport).

### 3. Menü-Modi (`src/menus.py`)

`Run.menu_mode: str` (Standard `""` = kein Vollbild-Submenü aktiv) steuert die neuen Werkstatt- und Begegnungs-Menüs:

- `"portal_select"`: Auswahl zwischen den `2` Universums-Angeboten aus `RunPlan.offers_for(run.depth)` (zeigt Name, Untertitel, Weltregel, Heimat-Probe, Zwischengegner).
- `"fabricator"`: Rezeptliste aller Zauberblöcke (gruppiert nach Tier `1..3`), zeigt benötigte Proben + Gold, verbleibende Bauten (`3 - fabricator.builds_this_visit`) und Bautaste `[Enter]`/`[E]`.
- `"trader"`: Zeigt die `4` Angebote des aktuellen Händlers, dessen `greeting_de` & `quirk_de`, Kauf per `[1]`–`[4]` (oder Auswahl + `[Enter]`).
- `"empress_bargain"`: Dialog für den Handel mit `"boese_kaiserin"` (`[J]` Handel annehmen vs. `[N]` Kämpfen).
- `"archive"`: 5 Reiter im Entdeckungs-Archiv (`"Zaubermodule"`, `"Baupläne"`, `"Kreaturen"`, `"Universen"`, `"Böse Ichs"`).

### 4. Hover-Erweiterung (`src/hover.py`)

`inspect_world` erkennt zusätzlich:

- **Werkstatt-Stationen (`Station`):** Titel = `station.name`, Untertitel = `"Werkstatt-Station"`, Hinweis = `station.prompt_de`.
- **Händler:** Titel = `trader.name`, Untertitel = `"Händler"`, Hinweis = `trader.quirk_de`.
- **Klonita:** Titel = `"Klonita"`, Untertitel = aktueller Zustand auf Deutsch (`"Folgt dir"`, `"Benommen"`, `"Hilft"`).
- **Kreaturen-Haltung:** Zeigt unter dem Kreaturennamen die deutsche Haltung (`"Friedlich"`, `"Scheu"`, `"Territorial"`, `"Feindselig"`, `"Bestochen"`).
- **Proben-Pickups (`kind == "sample"`):** Titel = `Sample.name`, Untertitel = `f"Probe (Stufe {sample.tier})"`, Beschreibung = `sample.description`.

---

## V23 — Speicherstand, Archiv (`src/records.py`), Rang-Formel & Alias-Migration

### 1. Archiv-Erweiterung (`src/records.py`)

`Records` wird abwärtskompatibel erweitert:

```python
@dataclass
class Records:
    runs: int = 0
    victories: int = 0
    best_depth: int = 1
    total_kills: int = 0
    blocks: list[str] = field(default_factory=list)
    creatures: dict[str, int] = field(default_factory=dict)
    blueprints: list[str] = field(default_factory=list)   # NEU
    universes: list[str] = field(default_factory=list)    # NEU
    evil_selves: list[str] = field(default_factory=list)  # NEU
    badges: int = 0                                       # NEU: höchste/gesammelte Dienstmarken
    best_rank: str = "Praktikantin"                       # NEU
```

#### Kanonische `Records.discover(self, kind: str, key: str = "") -> None`-Verzweigung

- `kind == "block"`: fügt `key` zu `self.blocks` hinzu (falls noch nicht enthalten).
- `kind == "blueprint"`: fügt `key` zu `self.blueprints` hinzu (falls noch nicht enthalten).
- `kind == "universe"`: fügt `key` zu `self.universes` hinzu (falls noch nicht enthalten).
- `kind == "evil_self"`: fügt `key` zu `self.evil_selves` hinzu (falls noch nicht enthalten).
- `kind == "badge"`: erhöht `self.badges += 1`.
- `kind == "creature"` (oder Legacy-1-Argument-Aufruf `discover(block_key)`): bei `key == ""` wird `kind` zu `self.blocks` hinzugefügt; sonst erhöht `self.creatures[key] = self.creatures.get(key, 0) + 1` und `self.total_kills += 1`.

### 2. Kanonische Rang-Berechnung (`compute_score` & `rank_for_score` in `src/records.py`)

```python
RANKS: tuple[tuple[int, str], ...] = (
    (0, "Praktikantin"),
    (150, "Hilfs-Alchemistin"),
    (350, "Sachbearbeiterin der Magie"),
    (650, "Ober-Laborantin"),
    (1000, "Erz-Klonologin"),
    (1500, "Realitäts-Rebellin"),
)

def compute_score(
    *,
    depth: int,
    kills: int,
    gold: int,
    samples_collected: int,
    challenges_won: int,
    bosses_killed: int,
    victory: bool,
    true_ending: bool = False,
) -> int:
    return (
        max(0, depth - 1) * 80
        + kills * 5
        + (gold // 5)
        + samples_collected * 10
        + challenges_won * 75
        + bosses_killed * 120
        + (300 if victory else 0)
        + (500 if true_ending else 0)
    )

def rank_for_score(score: int) -> str:
    """Gibt den höchsten Rang zurück, dessen Schwellenwert <= score ist."""
```

### 3. Vollständiges Live-Save-Schema (`Run.save_state` / `Run.restore` in `src/run.py`)

Zusätzlich zu den bestehenden Feldern in `save_state()` / `restore()` werden im `"live"`-Dictionary folgende Schlüssel gespeichert und beim Laden mit sicheren Defaults (`data.get(...)`) wiederhergestellt:

```python
"gold": self.gold,
"memory_shards": self.memory_shards,
"blueprint_shards": self.blueprint_shards,
"badges": self.badges,
"price_factor": self.price_factor,
"next_boost": self.next_boost,
"in_workshop": self.in_workshop,
"in_headquarters": self.in_headquarters,
"true_ending": self.true_ending,
"plan": self.plan.to_data(),
"wanted": self.wanted.to_data(),
"grudges": [[a, b] for (a, b) in sorted(self.grudges)],
"event": self.event.to_data() if self.event else None,
"challenge": self.challenge.to_data() if self.challenge else None,
"klonita": self.klonita.to_data(),
"samples": list(self.inventory.samples),
"level_meta": {
    "universe_key": self.level.universe_key,
    "mid_boss_arena": list(self.level.mid_boss_arena),
    "boss_arena": list(self.level.boss_arena),
    "trader_nook": list(self.level.trader_nook) if self.level.trader_nook else None,
    "challenge_shrine": list(self.level.challenge_shrine) if self.level.challenge_shrine else None,
    "regions": [[r, list(rect)] for r, rect in self.level.regions],
    "destructible_props": [[p, x, y] for p, x, y in self.level.destructible_props],
},
```

- **Rückwärtskompatibilität für `live["level"]`:** `live["level"]` behält exakt die 5-Elemente-Liste `[spawn, exit_point, arena, secret, vault]`, damit alte Spielstände ohne `level_meta` weiterhin fehlerfrei laden!
- **Kreaturen-Serialisierung (`_creature_data` / `_creature_from`):** Speichert zusätzlich `state`, `aggro`, `group_id`, `generation`, `carrying`, `bribed`, `giver`.
- **Spieler-Status-Timer:** Speichert `drunk`, `sticky`, `stamped_good`, `stamped_bad`, `marked_time`, `frozen`, `charged`, `befogged` im `"player"`-Objekt (Fallback `0.0` beim Laden alter Spielstände).

### 4. Kanonische Alias-Tabellen (`MODULE_ALIASES` & `PERK_ALIASES`)

Im MVP bleiben die heutigen Code-Schlüssel in `BLOCKS` kanonisch (eine Umbenennung auf die Bibel-06-Schlüssel ist nicht Teil von A–G). Damit die Bibel-Schlüssel trotzdem überall (Tests, Rezepte, Händler, Loot-Tabellen, Savegames) auf denselben kanonischen Schlüssel abbilden:

```python
# In src/spells.py:
MODULE_ALIASES: dict[str, str] = {
    # Bibel-06-Schlüssel -> heutiger Code-Schlüssel, aus der Spalte „Bisher“ in Bibel 06
    # (nur Zeilen, deren „Bisher“-Wert ein Schlüssel in BLOCKS ist), z. B.:
    "flux_funke": "funke",
    "nadelschuss": "nadel",
    "huepfgranate": "gallenblase",
    "matschbatzen": "klumpen",
    "fuellung_feuer": "sekret_feuer",
    "fuellung_rauch": "sekret_rauch",
    # … alle übrigen Zeilen der Tabellen Geschosse, Aufsätze, Zünder in Bibel 06 nach demselben Muster
    # (die acht neuen Füllungen aus V0e tragen ihren Bibel-Schlüssel direkt und brauchen keinen Alias)
}

def resolve_block_key(key: str) -> str:
    return MODULE_ALIASES.get(key, key)
```

Enthält `src/perks.py` entsprechend `PERK_ALIASES: dict[str, str]` mit `resolve_perk_key(key: str) -> str`.
