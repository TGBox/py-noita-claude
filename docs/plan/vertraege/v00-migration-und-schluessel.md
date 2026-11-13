# V0 – Code-Angleichung (T1–T4), Kanonische Schlüssel & Vorab-Entscheidungen

Verbindlicher Vorvertrag für alle Phasen. Löst sämtliche Widersprüche zwischen dem bestehenden Stand in `src/` (Arbeitspakete T1–T4) und der Bibel (`docs/bibel/`) auf und schließt alle offenen Detailfragen, damit keine Aufgabenkarte während der Umsetzung abbrechen muss.

---

## V0a Kanonische Proben- und Regions-Schlüssel (`src/universes/catalog.py`)

In `src/universes/catalog.py` sind die **6 MVP-Universen der Bibel** (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`) der alleinige aktive Kanon (`len(UNIVERSES) == 6`). `ALL_UNIVERSES` enthält im MVP genau diese 6; die Pool-Universen der Erweiterung kommen erst in Phase J dazu. Karte `A01` gleicht `src/universes/catalog.py` vor Beginn der Folgephasen an:

### 1. Proben-Schlüssel (`Universe.samples`, `Universe.sample_key` & `src/samples.py`)

Alle 12 Universums-Proben (je 2 pro MVP-Universum) tragen zwingend das Präfix `probe_`. Zusätzlich besitzt `Universe` die Eigenschaft/das Feld `sample_key: str` (`samples[0]`, die primäre Heimat-Probe des Universums):

| Universum | Kanonisches Tupel `Universe.samples` | Primäre `sample_key` | Anzeigename (`name_de`) |
| --- | --- | --- | --- |
| `fleischwelt` | `("probe_gallenstein", "probe_wucherung")` | `"probe_gallenstein"` | `"Gallenstein"`, `"Wucherungsableger"` |
| `aktenhalde` | `("probe_stempelkissen", "probe_formular")` | `"probe_stempelkissen"` | `"Stempelkissen"`, `"Formular B-38"` |
| `glibbria` | `("probe_glibberkern", "probe_brauseperle")` | `"probe_glibberkern"` | `"Glibberkern"`, `"Brauseperle"` |
| `kruemelreich` | `("probe_zuckerkristall", "probe_ameisenduft")` | `"probe_zuckerkristall"` | `"Riesenzuckerkristall"`, `"Ameisenduft-Ampulle"` |
| `sporenklub` | `("probe_leuchtspore", "probe_plattennadel")` | `"probe_leuchtspore"` | `"Leuchtspore im Glas"`, `"Plattennadel"` |
| `abtei` | `("probe_glockensplitter", "probe_kerzenstumpf")` | `"probe_glockensplitter"` | `"Glockensplitter"`, `"Kerzenstumpf mit Gesicht"` |

```python
# Rückwärtskompatibilität für die alten Schlüssel ohne Präfix aus T1–T4 (in src/samples.py):
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
}
```

### 2. Teilgebiets-Schlüssel (`Region.key` in `src/universes/catalog.py`)

Reihenfolge in `Universe.regions` entspricht der geometrischen Aufteilung in `split_regions` (von oben nach unten bzw. von links nach rechts):

| Universum | `split_regions`-Layout | Kanonische `Region.key`-Reihenfolge |
| --- | --- | --- |
| `fleischwelt` | `"vertical"` | `("schlund", "magen", "knochenmark")` |
| `aktenhalde` | `"horizontal"` | `("registratur", "grossraumbuero", "archivkeller")` |
| `glibbria` | `"islands"` | `("gelee_huegel", "kaugummi_hoehlen", "sirupkueste")` |
| `kruemelreich` | `"top_split"` | `("fliesenwueste", "unter_kuehlschrank", "ameisenbau")` |
| `sporenklub` | `"vertical"` | `("lautsprechertuerme", "tanzflaeche", "hinterzimmer")` |
| `abtei` | `"vertical"` | `("glockenturm", "kirchenschiff", "krypta")` |

Regions-Parameter (`Region.params`):

- `kruemelreich`: `unter_kuehlschrank` und `ameisenbau` tragen `(("ambient", 0.2),)`.
- `abtei`: `krypta` trägt `(("ambient", 0.15), ("current_vx", 28.0))` (horizontale Unterwasser-Strömung in px/s).

---

## V0b Seltenheitsstufen für Module (`src/spells.py`)

`Block.rarity: float` bleibt das **Drop-Gewicht** für Beute und Läden. Die ganzzahlige Stufe `Block.rarity_tier: int` (Feld, Standard `1`) brauchen Fabrikator, Händlerpreise und Belohnungen. Sie wird beim Aufbau von `BLOCKS` gesetzt (Karte `A02`):

- **Stufe 3:** die starken Grundmodule in `TIER3_BLOCKS` (Code-Schlüssel; Bibel-06-Name in Klammern):
  `"sprengkern"` (Atomkern), `"knochenbombe"` (Kraterbombe), `"achterkreis"` (Rundumschlag), `"dreifach"` (Dreifachlauf), `"zielsuche"` (Zielsuchkopf), `"kettenfunke"` (Kettenblitz), `"schwerelos"` (Schwebefeld), `"blutpreis"` (Fluxpumpe).
- **Stufe 2:** alle vom Code erzeugten Familien-Varianten (`rarity == FAMILY_RARITY`), sofern nicht Stufe 3.
- **Stufe 1:** alle übrigen Grundmodule.

```python
TIER3_BLOCKS: frozenset[str] = frozenset({
    "sprengkern", "knochenbombe", "achterkreis", "dreifach",
    "zielsuche", "kettenfunke", "schwerelos", "blutpreis",
})

def blocks_of_tier(tier: int) -> list[str]:
    """Schlüssel aller Blöcke mit block.rarity_tier == tier (ohne retired-Blöcke, siehe V0e)."""
```

- „Seltenheit 3+“ in Bibel 02 / `E06` bedeutet exakt: `block.rarity_tier >= 3`.
- Belohnungen der Stufe 3 (`V13b`) ziehen mit `rng.choice(blocks_of_tier(3))`.

---

## V0c Zerstörte Zellen & Goldadern in `World` (`src/world.py`)

Der Rust-Kern (`native`) bleibt unverändert. Zerstörte Zellen werden deterministisch in `World` gezählt (Karte `A03`):

```python
# Neue Felder in World.__init__ / World.reload / World.reset:
self.destroyed_cells: int = 0            # seit letztem Abruf durch Run zerstörte feste/Pulver-Zellen
self.destroyed_gold_vein_cells: int = 0  # seit letztem Abruf zerstörte Zellen mit Schlüssel "gold_vein"

def take_destroyed_cells(self) -> int:
    """Return destroyed_cells since last call and reset counter to 0."""
    cells = self.destroyed_cells
    self.destroyed_cells = 0
    return cells

def take_destroyed_gold_vein_cells(self) -> int:
    """Return destroyed_gold_vein_cells since last call and reset counter to 0."""
    gold = self.destroyed_gold_vein_cells
    self.destroyed_gold_vein_cells = 0
    return gold
```

- `World.explode`, `World.dig` und `World.crumble_loose` erhöhen bei jeder entfernten `SOLID`/`POWDER`-Zelle `self.destroyed_cells += 1`.
- Hat die entfernte Zelle den Materialschlüssel `"gold_vein"` (`KEYS[current] == "gold_vein"`), wird zusätzlich `self.destroyed_gold_vein_cells += 1` erhöht.
- `Run.update` ruft einmal pro Simulationsframe `cells = self.world.take_destroyed_cells()` und `gold_cells = self.world.take_destroyed_gold_vein_cells()` auf:
  - Wenn `cells > 0` oder `gold_cells > 0`: `self.emit("cells_destroyed", count=cells, gold_vein_cells=gold_cells)`.
  - Für je `8` zerstörte `gold_vein`-Zellen (Rest bleibt im Puffer `Run._gold_vein_remainder: int` erhalten) spawnt `Run` eine Goldmünze (`Pickup(x, y, kind="gold", amount=5)`) nahe dem Spieler/Explosionsort.

---

## V0d Vorab entschiedene Bibel-/Plan-Detailfragen

Damit kein günstiges Modell auf eine offene Designfrage stößt, gelten folgende Festlegungen verbindlich:

1. **Blattlaus-Weidematerial (`C17`, Krümelreich):**
   - `GRAZE_MATERIAL["blattlaus"] = "zucker"` (Blattläuse weiden an `zucker`-Zellen und verwandeln sich beim Treten in eine Honigtau-Quelle: Treffer mit `cause == "Tritt"` spawnt `3` Zellen `"honig"` in Luft unter der Blattlaus, ohne sie beim ersten Tritt zu töten: Tritt-Schaden an `blattlaus` wird in `on_hurt` auf `2.0` begrenzt).
2. **Krypta-Strömung (`A26` / `D06`, Versunkene Abtei):**
   - Keine Änderung am Rust-Kern. Stattdessen liest `Run.update` für jeden `Body` im Wasser (`body.in_liquid(self.world)`), dessen Mittelpunkt in einer Region `rect` liegt, den Regions-Parameter `region.param("current_vx", 0.0)` und addiert `current_vx * dt` auf `body.vx` (in der `krypta`: `current_vx = 28.0` px/s nach rechts).
3. **`glow`-Format in Sprite-JSON (`V5` vs. Bibel 01, Karte `A20`):**
   - `V5` gewinnt verbindlich: In der `.json`-Datei ist `"glow"` ein Objekt `{"0": [[x, y], ...], "1": [[x, y], ...]}` oder eine Liste von `GlowPoint`-Einträgen. `load_meta` / `load_sheet_meta` akzeptiert beide Formate.
4. **Türsteherpilz-Bestechung (`C17`, Sporenklub):**
   - `CreatureSpec` für `tuersteherpilz` ist `neutral`. Drückt der Spieler `E` (`controls.pickup`) in `<= 28 px` Abstand zu einem nicht-aggressiven `tuersteherpilz` und hat `run.gold >= 20`, zieht `Run` `20` Gold ab, setzt `creature.bribed = True`, verschiebt den Pilz um `16 px` zur Seite (aus dem Durchgang) und gibt die Sprechblase `"20 Gold – ich hab dich nie gesehen."` aus.
5. **Mönchsfisch-Chor (`C17`, Versunkene Abtei):**
   - Sind `>= 3` lebende `moenchsfisch` innerhalb von `180 px` umeinander, erhalten alle Kreaturen im Umkreis von `180 px` um diese Gruppe `creature.chorus_buff = 1.0` (Sekunden-Timer); solange `chorus_buff > 0`, ist ihr Angriffsschaden `× 1.25` (`apply_chorus_buff`).

---

## V0e Module: Schlüssel, Anzeigenamen & Füllungen (`src/spells.py`)

Entscheidung (2026-11-04): Die Code-Schlüssel in `BLOCKS` bleiben im MVP unverändert. Spieler sehen die Namen aus Bibel 06, `MODULE_ALIASES` (V23) übersetzt die Bibel-Schlüssel.

**Anzeigenamen:** Für jede Zeile der Tabellen „Geschosse“, „Aufsätze“ und „Zünder“ in Bibel 06 erhält `BLOCKS[<Bisher>]` den `name_de` aus Spalte „Name“ und den `description_de` aus Spalte „Beschreibung“ (Karten `G11`–`G13`).
**Füllungen:** Bibel 06 „Füllungen (10)“. Zwei gibt es schon: `fuellung_feuer` → `sekret_feuer`, `fuellung_rauch` → `sekret_rauch` (nur Alias + Anzeigename). Acht kommen als neue `Block`-Einträge mit `Category.PAYLOAD` und dem Bibel-Schlüssel dazu (Karte `A27`):

| Schlüssel | `name_de` | `material` |
| --- | --- | --- |
| `fuellung_wasser` | Wasserfüllung | `"water"` |
| `fuellung_oel` | Ölfüllung | `"oil"` |
| `fuellung_dampf` | Dampffüllung | `"steam"` |
| `fuellung_sand` | Sandfüllung | `"sand"` |
| `fuellung_erde` | Erdfüllung | `"dirt"` |
| `fuellung_fels` | Felsfüllung | `"rock"` |
| `fuellung_kolben` | Kolbenfüllung | `None`, neues Feld `from_flask=True` |
| `fuellung_lokal` | Lokalkolorit | `None`, neues Feld `local_material=True` |

`material=None` ist nur bei diesen beiden `PAYLOAD`-Blöcken erlaubt; `tests/test_spells.py` (`test_category_fields_are_consistent`) prüft genau das über `from_flask`/`local_material` (Plan-Korrektur 2026-11-07).

**Sonderfüllungen** (Karte `A28`), reine Funktion in `src/spells.py`:

```python
FLASK_PAYLOAD_CELLS = 10

def resolve_payload_material(block: Block, flask: Flask | None, set_keys: tuple[str, ...],
                             base_keys: tuple[str, ...], rng: random.Random) -> str | None:
    """Material key a payload block delivers for one cast.

    - normal block: block.material
    - from_flask: flask material key, and flask.amount -= FLASK_PAYLOAD_CELLS; empty or no flask: "water"
    - local_material: rng.choice of the keys in set_keys that are not in base_keys (universe materials);
      none available: "water"
    """
```

Eingebaut wird sie in `src/projectiles.py` (Karte `A30`): `build(..., resolve=...)` fragt für jeden Modifikator-Block `resolve(block)` statt `block.material`. `ProjectileSystem.payload_resolver` hält den Resolver der Spielerin (`Run._resolve_payload`, mit `self.flask`, `tuple(mat.KEYS)`, `mat.BASE_KEYS`, `self.rng`) und wird nur für `team == PLAYER_TEAM` benutzt.

**Organische Alt-Füllungen** (Entscheidung 2026-11-04, Karte `A29`): Füllungen, die im regulären Spiel Sinn ergeben, bleiben als normale Beute. Die übrigen bleiben in `BLOCKS` (alte Spielstände laden weiter), werden aber nie mehr gezogen: neues Feld `Block.retired: bool = False`; `random_block` (`src/loot.py`) und `blocks_of_tier` überspringen `retired`-Blöcke.

| Schlüssel | Material | Status | neuer `name_de` |
| --- | --- | --- | --- |
| `sekret_blut` | `blood` | bleibt | Blutfüllung |
| `sekret_saeure` | `acid` | bleibt | Säurefüllung |
| `sekret_glut` | `magma` | bleibt | Glutfüllung |
| `sekret_talg`, `sekret_sporen`, `sekret_schleim`, `sekret_eiter`, `sekret_aetzdampf`, `sekret_staub`, `sekret_sehnen`, `sekret_knochen`, `sekret_wucherung` | — | `retired=True` | unverändert |

Damit verkauft Herr Pansen (`V18`) Blut-, Säure- und Glutfüllung (alle drei Materialien liegen im Satz `"fleischwelt"`). Bibel 06 nennt die drei als „Organische Füllungen“.
