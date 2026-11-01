# V0 – Code-Angleichung (T1–T4), Kanonische Schlüssel & Vorab-Entscheidungen

Verbindlicher Vorvertrag für alle Phasen. Löst sämtliche Widersprüche zwischen dem bestehenden Stand in `src/` (Arbeitspakete T1–T4) und der Bibel (`docs/bibel/`) auf und schließt alle offenen Detailfragen, damit keine Aufgabenkarte während der Umsetzung abbrechen muss.

---

## V0a Kanonische Proben- und Regions-Schlüssel (`src/universes/catalog.py`)

In `src/universes/catalog.py` weichen aktuell mehrere Schlüssel von `docs/bibel/03-universen.md` und `docs/bibel/07-gegenstaende-und-werkstatt.md` ab. **Die Bibel-Schlüssel sind verbindlich.** Eine Vorab-Karte (`T5.00a` bzw. `U0.00a`) gleicht `src/universes/catalog.py` und `tests/test_universes.py` vor Beginn von Phase C an:

### 1. Proben-Schlüssel (`Universe.samples` & `src/samples.py`)

Alle 12 Proben tragen zwingend das Präfix `probe_`:

| Universum | Kanonisches Tupel `Universe.samples` | Anzeigename (`name_de`) |
| --- | --- | --- |
| `fleischwelt` | `("probe_gallenstein", "probe_wucherung")` | `"Gallenstein"`, `"Wucherungsableger"` |
| `aktenhalde` | `("probe_stempelkissen", "probe_formular")` | `"Stempelkissen"`, `"Formular B-38"` |
| `glibbria` | `("probe_glibberkern", "probe_brauseperle")` | `"Glibberkern"`, `"Brauseperle"` |
| `kruemelreich` | `("probe_zuckerkristall", "probe_ameisenduft")` | `"Riesenzuckerkristall"`, `"Ameisenduft-Ampulle"` |
| `sporenklub` | `("probe_leuchtspore", "probe_plattennadel")` | `"Leuchtspore im Glas"`, `"Plattennadel"` |
| `abtei` | `("probe_glockensplitter", "probe_kerzenstumpf")` | `"Glockensplitter"`, `"Kerzenstumpf mit Gesicht"` |

```python
# Rückwärtskompatibilität für alte Schlüssel ohne Präfix (in src/samples.py):
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

In `src/spells.py` ist `Block.rarity: float = 1.0` ein **Drop-Gewicht** (kleiner = seltener, z. B. `0.25` bis `1.2`). Damit Fabrikator (`W3.02`), Herausforderungen (`U0.10`, `U3.12`) und Beute-Tabellen mit ganzzahligen Seltenheitsstufen (`1`, `2`, `3`) arbeiten können, ohne bestehende Gewichtungen zu brechen, erhält `src/spells.py` eine berechnete Eigenschaft und eine Hilfsfunktion:

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

- „Seltenheit 3+“ in Bibel 02 / W3.02 bedeutet exakt: `block.rarity_tier >= 3`.
- Belohnung `("module_rarity", 3)` in V13 zieht mit `rng.choice(blocks_of_tier(3)).key`.

---

## V0c Zerstörte Zellen & Goldadern in `World` (`src/world.py`)

Der Rust-Kern (`native`) bleibt unverändert. Zerstörte Zellen werden deterministisch in `World` gezählt:

```python
# Neue Felder in World.__init__ / World.reload / World.reset:
self.destroyed_cells: int = 0       # seit letztem Abruf durch Run zerstörte feste/Pulver-Zellen
self.destroyed_gold_cells: int = 0  # seit letztem Abruf zerstörte Zellen mit Schlüssel "gold_vein"

def take_destroyed_cells(self) -> tuple[int, int]:
    """Return (destroyed_cells, destroyed_gold_cells) and reset both counters to 0."""
    cells, gold = self.destroyed_cells, self.destroyed_gold_cells
    self.destroyed_cells = 0
    self.destroyed_gold_cells = 0
    return cells, gold
```

- `World.explode`, `World.dig` und `World.crumble_loose` erhöhen bei jeder entfernten `SOLID`/`POWDER`-Zelle `self.destroyed_cells += 1`.
- Hat die entfernte Zelle den Materialschlüssel `"gold_vein"` (`KEYS[current] == "gold_vein"`), wird zusätzlich `self.destroyed_gold_cells += 1` erhöht.
- `Run.update` ruft einmal pro Simulationsframe `cells, gold_cells = self.world.take_destroyed_cells()` auf:
  - Wenn `cells > 0`: `self.emit("cells_destroyed", count=cells)`.
  - Für je `8` zerstörte `gold_vein`-Zellen (Rest bleibt im Puffer `Run._gold_vein_remainder: int` erhalten) spawnt `Run` eine Goldmünze (`Pickup(x, y, kind="gold", amount=5)`) nahe dem Spieler/Explosionsort.

---

## V0d Vorab entschiedene Bibel-/Plan-Detailfragen

Damit kein günstiges Modell auf eine offene Designfrage stößt, gelten folgende Festlegungen verbindlich:

1. **Blattlaus-Weidematerial (`U4.08`, Krümelreich):**
   - `GRAZE_MATERIAL["blattlaus"] = "zucker"` (Blattläuse weiden an `zucker`-Zellen und verwandeln sich beim Treten in eine Honigtau-Quelle: Treffer mit `cause == "Tritt"` spawnt `3` Zellen `"honig"` in Luft unter der Blattlaus, ohne sie beim ersten Tritt zu töten: Tritt-Schaden an `blattlaus` wird in `on_hurt` auf `2.0` begrenzt).
2. **Krypta-Strömung (`U6.04`, Versunkene Abtei):**
   - Keine Änderung am Rust-Kern. Stattdessen liest `Run.update` für jeden `Body` im Wasser (`body.in_liquid(self.world)`), dessen Mittelpunkt in einer Region `rect` liegt, den Regions-Parameter `region.param("current_vx", 0.0)` und addiert `current_vx * dt` auf `body.vx` (in der `krypta`: `current_vx = 28.0` px/s nach rechts).
3. **`glow`-Format in Sprite-JSON (`V5` vs. Bibel 01):**
   - `V5` gewinnt verbindlich: In der `.json`-Datei ist `"glow"` immer ein Objekt `{"0": [[x, y], ...], "1": [[x, y], ...]}` (Frame-Index als String-Key → Liste von `[x, y]`-Koordinaten). `load_meta` akzeptiert zur Sicherheit auch eine flache Liste `[[x, y], ...]` und ordnet sie dann Frame `0` zu.
4. **Türsteherpilz-Bestechung (`U5.07`, Sporenklub):**
   - `CreatureSpec` für `tuersteherpilz` ist `neutral`. Drückt der Spieler `E` (`controls.pickup`) in `<= 28 px` Abstand zu einem nicht-aggressiven `tuersteherpilz` und hat `run.gold >= 20`, zieht `Run` `20` Gold ab, setzt `creature.bribed = True`, verschiebt den Pilz um `16 px` zur Seite (aus dem Durchgang) und gibt die Sprechblase `"20 Gold – ich hab dich nie gesehen."` aus.
5. **Mönchsfisch-Chor (`U6.07`, Versunkene Abtei):**
   - Sind `>= 3` lebende `moenchsfisch` innerhalb von `180 px` umeinander, erhalten alle Kreaturen im Umkreis von `180 px` um diese Gruppe `creature.chorus_buff = 1.0` (Sekunden-Timer); solange `chorus_buff > 0`, ist ihr Angriffsschaden `× 1.25`.
