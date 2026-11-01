# Verträge V11–V12: Gegenstände, Proben, Pickup-Vereinheitlichung & Ereignisbus

> Teil des Vertrags-Index [vertraege.md](../vertraege.md). Kanonische Quelle: [docs/bibel/07-gegenstaende-und-werkstatt.md](../../bibel/07-gegenstaende-und-werkstatt.md).

---

## V11 — Proben (`src/samples.py`), Inventar-Erweiterung & einheitliches `Pickup` (`src/loot.py`)

### 1. Proben-Register (`src/samples.py`)

```python
from __future__ import annotations

from dataclasses import dataclass

SAMPLE_SLOTS: int = 12
SAMPLE_STACK: int = 99


@dataclass(frozen=True)
class Sample:
    key: str            # "probe_gallenstein", "probe_wucherung", ... (exakt wie in V0a)
    name: str           # Deutscher Anzeigename, z. B. "Gallenstein"
    universe_key: str   # "fleischwelt", "aktenhalde", ... oder "allgemein"
    tier: int           # 1 = gewöhnlich, 2 = selten, 3 = rar
    color: tuple[int, int, int]
    description: str


SAMPLES: dict[str, Sample] = {
    # 12 Universums-Proben (je 2 pro MVP-Universum, exakt nach Bibel Kap. 07 & V0a):
    "probe_gallenstein": Sample(
        "probe_gallenstein", "Gallenstein", "fleischwelt", 1, (224, 198, 72),
        "Ausgefällter Säuresplitter aus der Fleischwelt.",
    ),
    "probe_wucherung": Sample(
        "probe_wucherung", "Wucherungsableger", "fleischwelt", 1, (214, 96, 128),
        "Pulsierender Gewebe-Ableger aus der Fleischwelt.",
    ),
    "probe_stempelkissen": Sample(
        "probe_stempelkissen", "Stempelkissen", "aktenhalde", 1, (88, 124, 210),
        "Mit amtlicher Stempelfarbe getränktes Kissen aus der Aktenhalde.",
    ),
    "probe_formular": Sample(
        "probe_formular", "Formular B-38", "aktenhalde", 1, (228, 220, 192),
        "Dreifach gestempeltes Antragsformular aus der Aktenhalde.",
    ),
    "probe_glibberkern": Sample(
        "probe_glibberkern", "Glibberkern", "glibbria", 1, (236, 98, 224),
        "Elastischer Gelatinekern aus Glibbria.",
    ),
    "probe_brauseperle": Sample(
        "probe_brauseperle", "Brauseperle", "glibbria", 1, (255, 216, 84),
        "Prickelnde Brausekapsel aus der Sirupküste von Glibbria.",
    ),
    "probe_zuckerkristall": Sample(
        "probe_zuckerkristall", "Riesenzuckerkristall", "kruemelreich", 1, (244, 182, 216),
        "Glasharter Zuckerkristall aus dem Krümelreich.",
    ),
    "probe_ameisenduft": Sample(
        "probe_ameisenduft", "Ameisenduft-Ampulle", "kruemelreich", 1, (218, 154, 62),
        "Duftstoff-Ampulle aus dem Ameisenbau des Krümelreichs.",
    ),
    "probe_leuchtspore": Sample(
        "probe_leuchtspore", "Leuchtspore im Glas", "sporenklub", 1, (124, 232, 178),
        "Biolumineszente Sporenkapsel aus dem Sporen-Klub.",
    ),
    "probe_plattennadel": Sample(
        "probe_plattennadel", "Plattennadel", "sporenklub", 1, (132, 198, 255),
        "Noch vom Bass vibrierende Plattennadel aus dem Sporen-Klub.",
    ),
    "probe_glockensplitter": Sample(
        "probe_glockensplitter", "Glockensplitter", "abtei", 1, (196, 178, 114),
        "Klingender Bronzesplitter aus der Versunkenen Abtei.",
    ),
    "probe_kerzenstumpf": Sample(
        "probe_kerzenstumpf", "Kerzenstumpf mit Gesicht", "abtei", 1, (238, 222, 176),
        "Wasserfester Wachsstumpf aus der Versunkenen Abtei.",
    ),
    # 5 seltene / allgemeine Proben (Tier 2 & Tier 3):
    "probe_knochen": Sample(
        "probe_knochen", "Mark-Splitter", "allgemein", 2, (230, 222, 200),
        "Dichter Knochensplitter starker Kreaturen.",
    ),
    "probe_aether": Sample(
        "probe_aether", "Äther-Flocke", "allgemein", 2, (164, 214, 255),
        "Schwereloser Rückstand aus instabilen Zaubern.",
    ),
    "probe_schatten": Sample(
        "probe_schatten", "Schatten-Faden", "allgemein", 2, (96, 74, 138),
        "Dunkle Faser aus Geheimräumen und Verliesen.",
    ),
    "probe_gold": Sample(
        "probe_gold", "Reingold-Korn", "allgemein", 3, (255, 214, 70),
        "Hochreines Goldkorn aus tiefen Goldadern.",
    ),
    "probe_kern": Sample(
        "probe_kern", "Wächter-Kern", "allgemein", 3, (255, 96, 132),
        "Pulsierendes Herzstück eines besiegten Wächters.",
    ),
}

SAMPLE_ALIASES: dict[str, str] = {
    "gallenstein": "probe_gallenstein",
    "wucherungsableger": "probe_wucherung",
    "stempelkissen": "probe_stempelkissen",
    "formular_b38": "probe_formular",
    "glibberkern": "probe_glibberkern",
    "brauseperle": "probe_brauseperle",
    "riesenzuckerkristall": "probe_zuckerkristall",
    "ameisenduft": "probe_ameisenduft",
    "leuchtspore_im_glas": "probe_leuchtspore",
    "plattennadel": "probe_plattennadel",
    "glockensplitter": "probe_glockensplitter",
    "kerzenstumpf": "probe_kerzenstumpf",
    "probe_saft": "probe_gallenstein",
    "probe_papier": "probe_stempelkissen",
    "probe_bunt": "probe_glibberkern",
    "probe_zucker": "probe_zuckerkristall",
    "probe_harz": "probe_ameisenduft",
    "probe_pilz": "probe_leuchtspore",
    "probe_spule": "probe_plattennadel",
    "probe_salz": "probe_glockensplitter",
    "probe_rost": "probe_stempelkissen",
}
```

### 2. Inventar-Erweiterung (`src/inventory.py`)

`Inventory` erhält zusätzlich zu den bestehenden Feldern (`wands`, `blocks`, `pearls`, `selected`, `eye`, `rerolls`):

```python
samples: list[tuple[str, int] | None] = field(
    default_factory=lambda: [None] * 12
)
```

Methoden auf `Inventory`:

- `add_sample(self, key: str, count: int = 1) -> int`:
  - Löst `key = SAMPLE_ALIASES.get(key, key)` auf, validiert `key in SAMPLES` und `count > 0` (bei `count <= 0` Rückgabe `0`).
  - Stapelt zuerst auf existierende Slots mit `slot[0] == key` bis maximal `SAMPLE_STACK = 99` pro Slot.
  - Belegt danach freie Slots (`None`) mit `(key, min(rest, 99))`.
  - Gibt die **tatsächlich aufgenommene Menge** (`int`, `0..count`) zurück.
- `sample_count(self, key: str) -> int`:
  - Löst `key = SAMPLE_ALIASES.get(key, key)` auf und liefert die Summe aller Mengen in `self.samples` mit `slot is not None and slot[0] == key`.
- `total_samples(self) -> dict[str, int]`:
  - Liefert `{key: total_count}` für alle im Inventar vorhandenen Proben (`total_count > 0`).
- `take_samples(self, cost: dict[str, int]) -> bool`:
  - Prüft zuerst für alle `(k, need)` in `cost`, ob `self.sample_count(k) >= need`. Falls nicht: verändert nichts und gibt `False` zurück.
  - Zieht danach die benötigten Mengen von hinten nach vorne aus `self.samples` ab; Slots mit Menge `<= 0` werden auf `None` gesetzt. Gibt `True` zurück.

### 3. Vereinheitlichtes `Pickup` & `pickup_sprite_key` (`src/loot.py`)

Um Abwärtskompatibilität mit allen bestehenden Tests (`wand`, `block`, `pearls`, `perk`, `flask`, `heart`, `cocoon`, `eye`, `reroll`, `portal`) zu wahren und gleichzeitig alle neuen Pickup-Arten über ein einheitliches Schema abzubilden, hat `Pickup` in `src/loot.py` folgende Signatur:

```python
@dataclass
class Pickup:
    x: float
    y: float
    wand: WandSpec | None = None
    block: str | None = None
    pearls: int = 0
    perk: str | None = None
    flask: Flask | None = None
    heart: int = 0
    cocoon: bool = False
    eye: bool = False
    reroll: bool | int = False
    portal: bool = False
    kind: str = ""          # NEU: kanonischer Typ-Schlüssel
    item_key: str = ""      # NEU: Sub-Schlüssel (z. B. Sample-Key, Block-Key, Perk-Key)
    amount: int = 0         # NEU: Menge / Wert (Goldbetrag, Probenanzahl, HP-Bonus)
    seen: bool = False
    price: int = 0
    floating: bool = False
    vy: float = 0.0
    vx: float = 0.0
    age: float = 0.0

def pickup_sprite_key(pickup: Pickup) -> str:
    """Return the canonical sprite key in gegenstaende/ for pickup (Card A05)."""
    ...
```

#### Kanonische `kind`-Werte und Synchronisationsregeln (`__post_init__`)

`Pickup.__post_init__` synchronisiert neue (`kind`, `item_key`, `amount`) und bestehende Felder bidirektional:

| `kind` | `item_key` | `amount` | Gespiegeltes Legacy-Feld | Sprite-Schlüssel (`pickup_sprite_key`) |
| --- | --- | --- | --- | --- |
| `"wand"` | `""` | `1` | `wand: WandSpec` | `"stab"` |
| `"block"` | `<block_key>` | `1` | `block = item_key` | `"modul"` |
| `"pearls"` | `""` | `<count>` | `pearls = amount` | `"gold_klein"` |
| `"gold"` | `""` | `<gold_value>` | — | `<10`: `"gold_klein"`, `10..29`: `"gold_mittel"`, `>=30`: `"gold_gross"` |
| `"sample"` | `<sample_key>` | `<count>` (Standard `1`) | — | `<sample_key>` (z. B. `"probe_gallenstein"`) |
| `"perk"` | `<perk_key>` | `1` | `perk = item_key` | `"gabe"` |
| `"flask"` | `""` | `1` | `flask: Flask` | `"flasche_voll"` (oder `"flasche_leer"` wenn `flask.empty`) |
| `"heart"` / `"life_capsule"` | `""` | `<hp_bonus>` (Standard `25`) | `heart = amount` | `"lebenskapsel"` |
| `"cocoon"` | `""` | `1` | `cocoon = True` | `"kokon"` |
| `"eye"` | `""` | `1` | `eye = True` | `"auge"` |
| `"reroll"` | `""` | `<count>` (Standard `1`) | `reroll = amount` | `"wuerfel"` |
| `"portal"` | `""` | `1` | `portal = True` | `"portal_stein"` |
| `"memory_shard"` | `""` | `<count>` (Standard `1`) | — | `"erinnerungssplitter"` |
| `"blueprint_shard"` | `""` | `<count>` (Standard `1`) | — | `"bauplan_splitter"` |
| `"crate"` | `""` | `<tier>` (`1..3`, Standard `1`) | — | `"beutekiste"` |
| `"badge"` | `""` | `<count>` (Standard `1`) | — | `"dienstmarke"` |
| `"formular_stempel"` | `"gut"` oder `"schlecht"` | `1` | — | `"formular_stempel"` |

---

## V12 — Ereignisbus (`Run.emit` & `Run.listeners` in `src/run.py`)

### 1. Trennung von Audio-Cues (`Run.events`) und Gameplay-Ereignisbus (`Run.emit`)

> **WICHTIG:** `self.events: list[str]` auf `Run` wird bereits für Audio-/Sound-Cues (`"cast"`, `"kick"`, `"hurt"`, `"beat"`, `"portal"`, `"victory"` usw.) verwendet und darf **nicht** umbenannt oder im Typ verändert werden!

Stattdessen erhält `Run` zusätzlich:

```python
self.listeners: list[Callable[[str, dict[str, Any]], None]] = []
self.emitted_events: list[tuple[str, dict[str, Any]]] = []  # Puffer des aktuellen Ticks (für Tests/Inspektion, wird zu Beginn von Run.update geleert)
```

und die Methode:

```python
def emit(self, name: str, **data: Any) -> None:
    payload = dict(data)
    self.emitted_events.append((name, payload))
    for listener in list(self.listeners):
        listener(name, payload)
```

### 2. Kanonische Ereignis-Tabelle (24 Events)

Jeder Aufruf von `self.emit(name, **data)` stellt die folgenden Schlüssel im `payload`-Dictionary bereit:

| Event-Name (`name`) | Pflicht-Schlüssel in `data` | Auslöser | Haupt-Abnehmer |
| --- | --- | --- | --- |
| `"kill"` | `species: str`, `x: float`, `y: float`, `killer: str` (`"player"`, `"klonita"`, `"world"`, `"enemy"`) | Tod einer Kreatur in `Run.update` | Challenges (`kill_streak`, `pacifist`), Klonita, Boss-Skripte |
| `"hurt_player"` | `amount: float`, `source: str` (`"projectile"`, `"melee"`, `"material"`, `"self"`, `"authority"`) | Spieler verliert effektiv `hp > 0` | Challenges (`no_damage`, `dry_feet`), Klonita (`"player_low_hp"`) |
| `"pickup"` | `kind: str`, `key: str`, `amount: int` | Erfolgreiches Aufheben in `Run._pick_up` | Challenges (`no_gold`), HUD, Klonita |
| `"sample"` | `key: str`, `count: int` | Probe ins Inventar aufgenommen | HUD, Challenges, Klonita |
| `"gold"` | `amount: int`, `source: str` (`"pickup"`, `"challenge"`, `"trader"`, `"crate"`) | `Run.gold` erhöht sich | Challenges (`no_gold`), Statistik |
| `"enter_universe"` | `universe: str`, `depth: int` | Nach Betreten/Generieren eines Universums | Events, Challenges, Klonita, Records (`discover("universe", ...)`) |
| `"leave_universe"` | `universe: str`, `depth: int`, `destination: str` (`"workshop"`, `"next"`, `"headquarters"`) | Beim Betreten des Ausgangs-Portals | Challenges (`pacifist`, `no_gold`, `speed_run`), Wanted |
| `"event_start"` | `key: str`, `name: str` | `Event.on_start` | HUD-Banner, Klonita (`"event_start"`) |
| `"event_end"` | `key: str` | `Event.on_end` | HUD-Banner |
| `"beat"` | `step: int` | Wenn `RuleEffect.on_beat` von `False` auf `True` wechselt | DJ-Händler, Sporen-Klub-Kreaturen |
| `"jump"` | `x: float`, `y: float` | Spieler führt Sprung aus (`abtei`-Regel `jump_cost_air`) | Atem-Abzug in `abtei` |
| `"trader_hurt"` | `trader_key: str`, `amount: float` | Spieler-Projektil oder Kick trifft Händler | `Wanted.add(1.5, "Händler angegriffen")`, Händler wird feindlich |
| `"trader_killed"` | `trader_key: str`, `x: float`, `y: float` | Händler stirbt | `Wanted.add(3.0, "Händler getötet")`, Drop des Händler-Inventars |
| `"steal"` | `item_key: str`, `value: int` | Spieler nimmt unbezahltes Händler-Item mit | `Wanted.add(1.0, "Ladendiebstahl")`, Klonita |
| `"steal_return"` | `species: str`, `kind: str`, `x: float`, `y: float` | Dieb-Kreatur (`gabelstapler_krabbe`) stirbt mit Beute | `Run` spawnt gestohlenes Pickup am Todesort |
| `"split"` | `species: str`, `x: float`, `y: float`, `generation: int` | Kreatur mit `Ability("split", ...)` stirbt und `generation < 2` | `Run` spawnt 2 kleinere Nachkommen (`generation + 1`) |
| `"reflect"` | `species: str`, `x: float`, `y: float` | Kreatur mit `Ability("reflect", ...)` reflektiert Projektil | Partikel-/Audio-Effekt |
| `"summon"` | `species: str`, `target_species: str`, `x: float`, `y: float`, `count: int` | Kreatur oder Boss wirkt Beschwörung | `Run` spawnt `count` Kreaturen vom Typ `target_species` |
| `"wanted_change"` | `level: float`, `stars: int`, `reason: str` | `Wanted.level` ändert sich | HUD-Fahndungssterne, Klonita (`"wanted_high"` bei `stars >= 3`) |
| `"boss_phase"` | `boss_key: str`, `phase: int`, `line_de: str` | `BossScript` wechselt in nächste Phase | HUD-Boss-Banner, Klonita (`"boss_spawn"` bei `phase == 0`) |
| `"challenge_done"` | `key: str`, `success: bool` | `Challenge.completed` oder `Challenge.failed` wechselt auf `True` | HUD-Hinweis, Auszahlung bei `completed` |
| `"cells_destroyed"` | `count: int`, `gold_vein_cells: int` | `World.take_destroyed_cells()` liefert `> 0` zerstörte Zellen | `Wanted.on_cells_destroyed(count)`, Goldader-Drop (`gold_vein_cells`) |
| `"station"` | `station_key: str` | Spieler aktiviert Werkstatt-Station (`E`) | Werkstatt-Menüs / Minispiele / Couch |
| `"bribe"` | `species: str`, `cost: int` | Spieler besticht `tuersteherpilz` mit `E` | Zieht `20` Gold ab, setzt `creature.bribed = True` |
| `"noise"` | `x: float`, `y: float`, `radius: float` | Explosion oder lauter Zauber | Weckt schlafende Kreaturen im Radius `radius` |
