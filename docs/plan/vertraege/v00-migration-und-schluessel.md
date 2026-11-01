# V0 – Code-Angleichung (T1–T4), Kanonische Schlüssel & Vorab-Entscheidungen

Verbindlicher Vorvertrag für alle Phasen. Löst sämtliche Widersprüche zwischen dem bestehenden Stand in `src/` (Arbeitspakete T1–T4) und der Bibel (`docs/bibel/`) auf und schließt alle offenen Detailfragen, damit keine Aufgabenkarte während der Umsetzung abbrechen muss.

---

## V0a Kanonische Proben- und Regions-Schlüssel (`src/universes/catalog.py`)

In `src/universes/catalog.py` sind die **6 MVP-Universen der Bibel** (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`) der alleinige aktive Kanon (`len(UNIVERSES) == 6`). Die 3 zusätzlichen Pool-Universen (`schrott`, `kuchen`, `spule`) liegen separat in `POOL_UNIVERSES`. Karte `A01` gleicht `src/universes/catalog.py` vor Beginn der Folgephasen an:

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
# Rückwärtskompatibilität für alte Schlüssel ohne Präfix und Pool-Proben (in src/samples.py):
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
    "probe_harz": "probe_ameisenduft",
    "probe_pilz": "probe_leuchtspore",
    "probe_salz": "probe_glockensplitter",
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

In `src/spells.py` ist `Block.rarity: float = 1.0` ein **Drop-Gewicht** (kleiner = seltener, z. B. `0.25` bis `1.2`). Damit Fabrikator (`E05`), Herausforderungen (`D12`–`D13`) und Beute-Tabellen mit ganzzahligen Seltenheitsstufen (`1`, `2`, `3`) arbeiten können, ohne bestehende Gewichtungen zu brechen, erhält `src/spells.py` (Karte `A02`) eine berechnete Eigenschaft und eine Hilfsfunktion:

```python
# In class Block (src/spells.py):
@property
def rarity_tier(self) -> int:
    """Integer rarity tier 1 (common), 2 (uncommon), 3 (rare) derived from weight."""
    if self.rarity <= 0.45:
        return 3
    if self.rarity <= 0.8:
        return 2
    return 1

def blocks_of_tier(tier: int) -> tuple[Block, ...]:
    """All blocks in BLOCKS with block.rarity_tier == tier."""
    return tuple(b for b in BLOCKS if b.rarity_tier == tier)
```

- „Seltenheit 3+“ in Bibel 02 / `E05` bedeutet exakt: `block.rarity_tier >= 3`.
- Belohnung `("module_rarity", 3)` in `V13` zieht mit `rng.choice(blocks_of_tier(3)).key`.

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
2. **Krypta-Strömung (`D08` / `D09`, Versunkene Abtei):**
   - Keine Änderung am Rust-Kern. Stattdessen liest `Run.update` für jeden `Body` im Wasser (`body.in_liquid(self.world)`), dessen Mittelpunkt in einer Region `rect` liegt, den Regions-Parameter `region.param("current_vx", 0.0)` und addiert `current_vx * dt` auf `body.vx` (in der `krypta`: `current_vx = 28.0` px/s nach rechts).
3. **`glow`-Format in Sprite-JSON (`V5` vs. Bibel 01, Karte `A20`):**
   - `V5` gewinnt verbindlich: In der `.json`-Datei ist `"glow"` ein Objekt `{"0": [[x, y], ...], "1": [[x, y], ...]}` oder eine Liste von `GlowPoint`-Einträgen. `load_meta` / `load_sheet_meta` akzeptiert beide Formate.
4. **Türsteherpilz-Bestechung (`C17`, Sporenklub):**
   - `CreatureSpec` für `tuersteherpilz` ist `neutral`. Drückt der Spieler `E` (`controls.pickup`) in `<= 28 px` Abstand zu einem nicht-aggressiven `tuersteherpilz` und hat `run.gold >= 20`, zieht `Run` `20` Gold ab, setzt `creature.bribed = True`, verschiebt den Pilz um `16 px` zur Seite (aus dem Durchgang) und gibt die Sprechblase `"20 Gold – ich hab dich nie gesehen."` aus.
5. **Mönchsfisch-Chor (`C17`, Versunkene Abtei):**
   - Sind `>= 3` lebende `moenchsfisch` innerhalb von `180 px` umeinander, erhalten alle Kreaturen im Umkreis von `180 px` um diese Gruppe `creature.chorus_buff = 1.0` (Sekunden-Timer); solange `chorus_buff > 0`, ist ihr Angriffsschaden `× 1.25` (`apply_chorus_buff`).
