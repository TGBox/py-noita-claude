# Phase B — Prozedurale Grafik & Sprite-Sheets (33 atomare S-Karten: `B01`–`B36`; `B06`, `B10`, `B13` entfallen)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_b.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Grafik-Karten halten die Qualitätsregeln aus [v05-sprites-und-teile.md](vertraege/v05-sprites-und-teile.md) (`V8`) ein: mindestens 5 Farbtöne pro Sprite, dunkle Kontur `OUTLINE_DARK`, `> 20 %` nicht-transparente Pixel, `.png` + `.json` Paar.

---

> `B06`, `B10`, `B13` (Kreaturen der Pool-Universen `schrott`, `kuchen`, `spule`) sind nach Phase J verschoben. Die frei gewordenen IDs werden nicht neu vergeben.

## B01 — Spielerin-Sprite-Sheet (`charaktere/spielerin`) (`V5`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`, `V8`), `tools/palette.py`, `tools/sprites.py`, `tests/spec/test_phase_b.py` (`-k b01`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_chars.py` und implementiere `build_player_sheet(out_dir)` für `charaktere/spielerin.{png,json}` (`20×24` px pro Frame, Animationen `"idle"` (4), `"walk"` (6), `"jump"` (2), `"fall"` (2), `"cast"` (3), `"hurt"` (2), `"dead"` (1)) mit Kapuzenmantel, leuchtendem Zauberfokus (`glow`-Punkt) und Schattierung aus `ENTITY_PALETTES["spielerin"]`.
  2. Registriere `build_player_sheet` in `tools/sprites.py` (`build_all`).
- **Akzeptanzkriterien:**
  - `charaktere/spielerin.png` und `charaktere/spielerin.json` existieren nach Aufruf, haben `frame_size == (20, 24)` und enthalten alle 7 benannten Animationen sowie mindestens 1 `glow`-Punkt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b01 -q && uv run pytest --ignore=tests/spec -q`

---

## B02 — Klonita-Sprite-Sheet (`charaktere/klonita`) (`V5`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`, `V8`), `tools/sprites_chars.py`, `tests/spec/test_phase_b.py` (`-k b02`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_klonita_sheet(out_dir)` für `charaktere/klonita.{png,json}` (`18×22` px, Animationen `"idle"` (4), `"fly"` (4), `"assist"` (3), `"quirk"` (3), `"knocked"` (2)) mit schwebendem Saum, schiefem Hexenhut und lila Laternen-`glow`.
- **Akzeptanzkriterien:**
  - `charaktere/klonita.{png,json}` wird erzeugt, besitzt alle 5 Animationen (`idle`, `fly`, `assist`, `quirk`, `knocked`) und besteht den `V8`-Qualitätstest (`>= 5` Farben, `> 20 %` Füllgrad).
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b02 -q && uv run pytest --ignore=tests/spec -q`

---

## B03 — Behörden-Agenten-Sheets (`charaktere/agent_*`) (`V8`, `V15`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `tools/sprites_chars.py`, `tests/spec/test_phase_b.py` (`-k b03`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_agent_sheets(out_dir)` für die 4 Behörden-Agenten in `charaktere/`: `"agent_streife"` (sowie Alias `"agent_sachbearbeiter"`), `"agent_drohne"`, `"agent_vollstrecker"` (`22×26` mit Aktenkoffer-Schild) und `"agent_abteilungsleiter"` (`24×28` schwebend mit Paragraphen-Krone), jeweils mit `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`.
- **Akzeptanzkriterien:**
  - Alle Agenten-Sheets unter `charaktere/agent_*.{png,json}` existieren, lassen sich über `load_sheet_meta` laden und erfüllen die `V8`-Qualitätsregeln.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b03 -q && uv run pytest --ignore=tests/spec -q`

---

## B04 — Böse-Ichs- & Ober-Cloita-Sheets (`charaktere/boese_*`, `ober_cloita`) (`V8`, `V17`)

- **Größe:** S
- **Abhängigkeiten:** `B03`
- **Ziel-Dateien:** `tools/sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `tools/sprites_chars.py`, `tests/spec/test_phase_b.py` (`-k b04`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_evil_and_hq_sheets(out_dir)` für `"boese_kaiserin"` (`22×26`), `"boese_gute"` (`22×26`), `"boese_omega"` (`24×28`) und `"ober_cloita"` (`36×42`), jeweils mit `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und leuchtenden `glow`-Punkten.
- **Akzeptanzkriterien:**
  - Alle 4 Sheets unter `charaktere/` existieren, haben gültige JSON-Metadaten mit `glow`-Einträgen und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b04 -q && uv run pytest --ignore=tests/spec -q`

---

## B05 — Die 6 Händler-Sprite-Sheets (`charaktere/npc_*`) (`V8`, `V19`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `tools/sprites_chars.py`, `tests/spec/test_phase_b.py` (`-k b05`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_trader_sheets(out_dir)` für alle 6 Händler aus `V19`: `"npc_magenhaendler"`, `"npc_sachbearbeiterin"`, `"npc_glibberhaendler"`, `"npc_ameisenhehler"`, `"npc_dj"`, `"npc_kuester"` (`20×24` px, Animationen `"idle"` (4), `"talk"` (3), `"hurt"` (2)).
- **Akzeptanzkriterien:**
  - Alle 6 `charaktere/npc_*.{png,json}`-Dateien existieren, enthalten `"idle"`, `"talk"`, `"hurt"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b05 -q && uv run pytest --ignore=tests/spec -q`

---

## B07 — Kreaturen-Sheets Sporenklub (`sporenklub`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Sporenklub“), `src/universes/catalog.py` (`sporenklub`), `tests/spec/test_phase_b.py` (`-k b07`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_creatures.py` mit `build_creature_sheets(out_dir, universe_key=None)` (und binde es in `tools/sprites.py` ein). die 4 Kreaturen-Sheets für `sporenklub` unter `kreaturen/`: `"tuersteherpilz"`, `"sporenschnorrer"`, `"sporenwerfer"`, `"leuchtmotte"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; Leuchtpunkte (`glow`) bei `"leuchtmotte"` und `"sporenwerfer"`). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["sporenklub"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b07 -q && uv run pytest --ignore=tests/spec -q`

---

## B08 — Kreaturen-Sheets Fleischwelt (`fleischwelt`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B07`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Fleischwelt“), `src/universes/catalog.py` (`fleischwelt`), `tests/spec/test_phase_b.py` (`-k b08`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `fleischwelt` unter `kreaturen/`: `"fleischmade"`, `"blutegel"`, `"saeurespucker"`, `"zottenwurm"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; Sonderzustände `"hang"`/`"latched"` beim `"blutegel"`, `"burrow_out"` bei der `"fleischmade"`). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["fleischwelt"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b08 -q && uv run pytest --ignore=tests/spec -q`

---

## B09 — Kreaturen-Sheets Aktenhalde (`aktenhalde`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B07`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Aktenhalde“), `src/universes/catalog.py` (`aktenhalde`), `tests/spec/test_phase_b.py` (`-k b09`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `aktenhalde` unter `kreaturen/`: `"aktenfresser"`, `"stempler"`, `"paragraphenreiter"`, `"kaffeegolem"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; Sonderzustände `"dig"` (Aktenfresser) und `"stamp"` (Stempler)). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["aktenhalde"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b09 -q && uv run pytest --ignore=tests/spec -q`

---

## B11 — Kreaturen-Sheets Versunkene Abtei (`abtei`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B07`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Versunkene Abtei“), `src/universes/catalog.py` (`abtei`), `tests/spec/test_phase_b.py` (`-k b11`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `abtei` unter `kreaturen/`: `"moenchsfisch"`, `"orgelaal"`, `"glockenqualle"`, `"korallenwaechter"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; Leuchtpunkte bei `"glockenqualle"`; der `"orgelaal"` als Segment-Sheet für `Chain`). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["abtei"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b11 -q && uv run pytest --ignore=tests/spec -q`

---

## B12 — Kreaturen-Sheets Krümelreich (`kruemelreich`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B07`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Krümelreich“), `src/universes/catalog.py` (`kruemelreich`), `tests/spec/test_phase_b.py` (`-k b12`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `kruemelreich` unter `kreaturen/`: `"ameisenkrieger"`, `"blattlaus"`, `"arbeiterameise"`, `"harzspucker"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; bernsteinfarbener Leuchtakzent im Ausholen des `"harzspucker"`). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["kruemelreich"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b12 -q && uv run pytest --ignore=tests/spec -q`

---

## B14 — Kreaturen-Sheets Glibbria (`glibbria`: 4 Einheimische) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B07`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` (Abschnitt „Glibbria“), `src/universes/catalog.py` (`glibbria`), `tests/spec/test_phase_b.py` (`-k b14`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `glibbria` unter `kreaturen/`: `"huepfling"`, `"glibberteiler"`, `"zuckerwatte_wolke"`, `"konfetti_kanone"` (Zustände `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`; Sonderzustand `"squash"` beim `"huepfling"`; `"glibberteiler"` in den 3 Größen aus `SPLIT_SIZES`). Aussehen und Größe nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für jede Art in `UNIVERSES["glibbria"].creatures` existiert `kreaturen/<key>.png` + `.json` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b14 -q && uv run pytest --ignore=tests/spec -q`

---

## B15 — Unter-Zwischenboss-Sheets Teil 1 (`pfuetzenwurm`, `aktenwolf`, `manege_clown`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` („Unter-Zwischenbosse“), `tests/spec/test_phase_b.py` (`-k b15`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_bosses.py` mit `build_mid_boss_sheets(out_dir)` (und binde es in `tools/sprites.py` ein) und den Sheets (`28×28` bis `32×32` px) unter `bosse/` für `"pfuetzenwurm"` (Fleischwelt), `"aktenwolf"` (Aktenhalde) und `"manege_clown"` (Glibbria).
- **Akzeptanzkriterien:**
  - Alle 3 Sheets existieren unter `bosse/`, haben `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b15 -q && uv run pytest --ignore=tests/spec -q`

---

## B16 — Unter-Zwischenboss-Sheets Teil 2 (`harzgeneral`, `sporenherz`, `glockenwaechter`) + `warden` (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/05-gegner.md` („Unter-Zwischenbosse“), `tests/spec/test_phase_b.py` (`-k b16`)
- **Aufgabe:**
  1. Ergänze in `build_mid_boss_sheets` die Sheets unter `bosse/` für `"harzgeneral"` (Krümelreich), `"sporenherz"` (Sporenklub), `"glockenwaechter"` (Versunkene Abtei) sowie für den Bestands-Boss `"warden"`.
- **Akzeptanzkriterien:**
  - Alle 6 `u.mid_boss` aus `UNIVERSES` und `"warden"` haben ein Sheet unter `bosse/`, das `V8` erfüllt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b16 -q && uv run pytest --ignore=tests/spec -q`

---

## B17 — Zwischengegner-Sheets (`weltenherz`, `oberstempler`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `A20`, `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/bibel/05-gegner.md` („Zwischengegner“, „Große Kreaturen“), `tests/spec/test_phase_b.py` (`-k b17`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Funktion `build_end_boss_sheets(out_dir)` mit den Haupt- und Körperteil-Sheets (`36×36` bis `96×64` px) unter `bosse/` für `"weltenherz"`, `"oberstempler"` und trage ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`) ein. Aussehen, Größe und Teile nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für `"weltenherz"`, `"oberstempler"` existieren `bosse/<key>`-Sheets nach `V8` und Einträge in `RIG_LAYOUTS`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b17 -q && uv run pytest --ignore=tests/spec -q`

---

## B18 — Zwischengegner-Sheets (`mutter_glibber`, `dj_myzel`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B17`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/bibel/05-gegner.md` („Zwischengegner“, „Große Kreaturen“), `tests/spec/test_phase_b.py` (`-k b18`)
- **Aufgabe:**
  1. Ergänze in `build_end_boss_sheets` die Haupt- und Körperteil-Sheets (`36×36` bis `96×64` px) unter `bosse/` für `"mutter_glibber"`, `"dj_myzel"` und trage ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`) ein. Aussehen, Größe und Teile nach Bibel 04/05.
- **Akzeptanzkriterien:**
  - Für `"mutter_glibber"`, `"dj_myzel"` existieren `bosse/<key>`-Sheets nach `V8` und Einträge in `RIG_LAYOUTS`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b18 -q && uv run pytest --ignore=tests/spec -q`

---

## B19 — Zwischengegner-Sheets (`ameisenkoenigin`, `abt_kieme` + Großkreaturen) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B18`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/bibel/05-gegner.md` („Zwischengegner“, „Große Kreaturen“), `tests/spec/test_phase_b.py` (`-k b19`)
- **Aufgabe:**
  1. Ergänze in `build_end_boss_sheets` die Haupt- und Körperteil-Sheets (`36×36` bis `96×64` px) unter `bosse/` für `"ameisenkoenigin"`, `"abt_kieme"` und trage ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`) ein. Aussehen, Größe und Teile nach Bibel 04/05.
  2. Erzeuge außerdem die Teil-Sheets der Großkreaturen `"trampolinwal"` (Kopf, Rumpf, Schwanz, Flossen) und `"kirchenkrake"` (Mantel, 6 Tentakel, Augen) unter `kreaturen/` und ihre `RIG_LAYOUTS`-Einträge.
- **Akzeptanzkriterien:**
  - Für `"ameisenkoenigin"`, `"abt_kieme"` existieren `bosse/<key>`-Sheets nach `V8` und Einträge in `RIG_LAYOUTS`.
  - `kreaturen/trampolinwal` und `kreaturen/kirchenkrake` existieren nach `V8` und haben `RIG_LAYOUTS`-Einträge.
  - Damit haben alle 6 `u.boss` aus `UNIVERSES` Sheet und Rig.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b19 -q && uv run pytest --ignore=tests/spec -q`

---

## B20 — Die 20 Waffenteil-Sprites (`waffen/*`) (`V8`, `V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A22`, `A23`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`, `V8b`), `docs/bibel/06-waffen-und-module.md` („Aussehen aus Teilen“), `tests/spec/test_phase_b.py` (`-k b20`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_items.py` (und binde es in `tools/sprites.py` ein) mit `build_weapon_part_sheets(out_dir)`, das für jeden der 20 Schlüssel in `WEAPON_PART_KEYS` ein kleines Teil-Sprite (2–12 px breit, `idle` 1 Frame) + `.json` unter `waffen/` erzeugt; die Tanks bekommen einen `glow`-Punkt in `flux`. Gleiche Gruppen dürfen sich eine Zeichenfunktion mit Parametern teilen.
- **Akzeptanzkriterien:**
  - Für jeden Schlüssel in `WEAPON_PART_KEYS` existiert `waffen/<key>.{png,json}` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b20 -q && uv run pytest --ignore=tests/spec -q`

---

## B21 — Modul-Icons: Geschosse (`zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/06-waffen-und-module.md` („Kategorien“, „Icons“), `src/spells.py` (`Category`, `BLOCKS`), `tests/spec/test_phase_b.py` (`-k b21`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die Funktion `build_spell_icon_sheets(out_dir)` und erzeuge für **jeden** Block in `BLOCKS` mit `block.category == Category.FORM` ein `12×12`-Icon unter `zauber/<key>` (Geschosse, Motiv nach Bibel 06 „Icon-Idee“, Rahmenfarbe nach Kategorie).
- **Akzeptanzkriterien:**
  - Für alle Blöcke mit `category == Category.FORM` existiert `zauber/<key>` nach `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b21 -q && uv run pytest --ignore=tests/spec -q`

---

## B22 — Modul-Icons: Aufsätze (`zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B21`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/06-waffen-und-module.md` („Kategorien“, „Icons“), `src/spells.py` (`Category`, `BLOCKS`), `tests/spec/test_phase_b.py` (`-k b22`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` (`build_spell_icon_sheets(out_dir)`) für **jeden** Block in `BLOCKS` mit `block.category == Category.MODIFIER` ein `12×12`-Icon unter `zauber/<key>` (Aufsätze, Motiv nach Bibel 06 „Icon-Idee“, Rahmenfarbe nach Kategorie).
- **Akzeptanzkriterien:**
  - Für alle Blöcke mit `category == Category.MODIFIER` existiert `zauber/<key>` nach `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b22 -q && uv run pytest --ignore=tests/spec -q`

---

## B23 — Modul-Icons: Füllungen (`zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B22`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/06-waffen-und-module.md` („Kategorien“, „Icons“), `src/spells.py` (`Category`, `BLOCKS`), `tests/spec/test_phase_b.py` (`-k b23`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` (`build_spell_icon_sheets(out_dir)`) für **jeden** Block in `BLOCKS` mit `block.category == Category.PAYLOAD` ein `12×12`-Icon unter `zauber/<key>` (Füllungen, Motiv nach Bibel 06 „Icon-Idee“, Rahmenfarbe nach Kategorie).
- **Akzeptanzkriterien:**
  - Für alle Blöcke mit `category == Category.PAYLOAD` existiert `zauber/<key>` nach `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b23 -q && uv run pytest --ignore=tests/spec -q`

---

## B24 — Modul-Icons: Zünder & alle übrigen Blöcke (`zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B23`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/bibel/06-waffen-und-module.md` („Kategorien“, „Icons“), `src/spells.py` (`Category`, `BLOCKS`), `tests/spec/test_phase_b.py` (`-k b24`)
- **Aufgabe:**
  1. Ergänze die Icons für alle restlichen Blöcke in `BLOCKS` (`Category.TRIGGER` und die Familien-Blöcke aus `_families()`).
- **Akzeptanzkriterien:**
  - Für **jeden** Schlüssel in `BLOCKS` existiert `zauber/<key>` nach `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b24 -q && uv run pytest --ignore=tests/spec -q`

---

## B25 — Gegenstands-Icons Teil 1: Gold & Grundgegenstände (`gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A05`, `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`, `pickup_sprite_key`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Gegenstände in der Welt“), `tests/spec/test_phase_b.py` (`-k b25`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die Funktion `build_item_icon_sheets(out_dir)` mit `12×12`-Sprites unter `gegenstaende/` für `"gold_klein"`, `"gold_mittel"`, `"gold_gross"`, `"stab"`, `"modul"`, `"gabe"`, `"flasche_voll"`, `"flasche_leer"`, `"lebenskapsel"`, `"kokon"`.
- **Akzeptanzkriterien:**
  - Alle 10 Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b25 -q && uv run pytest --ignore=tests/spec -q`

---

## B26 — Gegenstands-Icons Teil 2: Sammel- und Quest-Gegenstände (`gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `B25`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`, `pickup_sprite_key`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Gegenstände in der Welt“), `tests/spec/test_phase_b.py` (`-k b26`)
- **Aufgabe:**
  1. Ergänze in `build_item_icon_sheets` `12×12`-Sprites unter `gegenstaende/` für `"auge"`, `"wuerfel"`, `"erinnerungssplitter"`, `"bauplan_splitter"`, `"beutekiste"`, `"dienstmarke"`, `"formular_stempel"`, `"portal_stein"`.
- **Akzeptanzkriterien:**
  - Alle 8 Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b26 -q && uv run pytest --ignore=tests/spec -q`

---

## B27 — Gegenstands-Icons Teil 3: alle 17 Proben (`gegenstaende/probe_*`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A04`, `B26`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`, `SAMPLES`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Proben“), `tests/spec/test_phase_b.py` (`-k b27`)
- **Aufgabe:**
  1. Ergänze in `build_item_icon_sheets` je ein `12×12`-Sprite unter `gegenstaende/` für **jede** Probe in `SAMPLES` (12 Universums-Proben + 5 seltene Proben), Aussehen nach Bibel 07.
- **Akzeptanzkriterien:**
  - Für jeden Schlüssel in `SAMPLES` existiert `gegenstaende/<key>` nach `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b27 -q && uv run pytest --ignore=tests/spec -q`

---

## B28 — Werkstatt-Stationen Teil 1 (`umgebung/`) (`V8`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`, Spalte `sprite_key`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Die Werkstatt“), `tests/spec/test_phase_b.py` (`-k b28`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_env.py` mit `build_env_prop_sheets(out_dir)` (und binde es in `tools/sprites.py` ein) und den Stations-Sprites (`24×24` bis `48×48` px, `idle` 2–4 und `use` 2–4 Frames) unter `umgebung/` für die `sprite_key`s `"portal_stein"`, `"werkbank"`, `"fabrikator"`, `"experimentier_liege"`, `"haendler_stand"`, `"zapfhahn"`.
- **Akzeptanzkriterien:**
  - Alle 6 Sprites existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b28 -q && uv run pytest --ignore=tests/spec -q`

---

## B29 — Werkstatt-Stationen Teil 2 + Hauptquartier-Portal & Attrappe (`umgebung/`) (`V8`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `B28`
- **Ziel-Dateien:** `tools/sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`, Spalte `sprite_key`), `tests/spec/test_phase_b.py` (`-k b29`)
- **Aufgabe:**
  1. Ergänze in `build_env_prop_sheets` die Sprites unter `umgebung/` für `"physik_o_mat"`, `"schiessstand"`, `"archiv_pult"`, `"klonita_sofa"`, `"akten_schredder"`, `"flaschen_brunnen"`, `"portal_headquarters"`, `"trainings_attrappe"`.
- **Akzeptanzkriterien:**
  - Zusammen mit `B28` hat jede Station in `STATIONS` ein Sprite `umgebung/<station.sprite_key>` nach `V8`; dazu `"portal_headquarters"` und `"trainings_attrappe"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b29 -q && uv run pytest --ignore=tests/spec -q`

---

## B30 — Umgebungs-Props der 6 Universen (`umgebung/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B29`
- **Ziel-Dateien:** `tools/sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`Level.destructible_props`), `tests/spec/test_phase_b.py` (`-k b30`)
- **Aufgabe:**
  1. Ergänze in `build_env_prop_sheets` 13 interaktive bzw. zerstörbare Props (`16×16` bis `24×24` px) unter `umgebung/`: `"explosionsfass"`, `"saeure_behaelter"`, `"magen_zotte"`, `"akten_regal"`, `"amt_uhr"`, `"glibber_ballon"`, `"ameisen_kokon"`, `"sporen_knolle"`, `"pilz_laterne"`, `"abtei_glocke"`, `"pruefungs_schrein"`, `"geheim_altar"`, `"gold_statue"`. Die universumsbezogenen Props gehören zu: Fleischwelt (`saeure_behaelter`, `magen_zotte`), Aktenhalde (`akten_regal`, `amt_uhr`), Glibbria (`glibber_ballon`), Krümelreich (`ameisen_kokon`), Sporenklub (`sporen_knolle`, `pilz_laterne`), Abtei (`abtei_glocke`).
- **Akzeptanzkriterien:**
  - Alle 13 Props existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b30 -q && uv run pytest --ignore=tests/spec -q`

---

## B31 — Partikel- & Projektil-Sheets (`partikel/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B30`
- **Ziel-Dateien:** `tools/sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `tests/spec/test_phase_b.py` (`-k b31`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` `build_particle_sheets(out_dir)` für 12 mehrframige `8×8`-/`12×12`-Effekt-Sheets unter `partikel/`: `"funken"`, `"flamme"`, `"eis_splitter"`, `"saeure_tropfen"`, `"sporen_wolke"`, `"blitz_bogen"`, `"heil_stern"`, `"stempel_abdruck"`, `"schleim_blase"`, `"zucker_glitzer"`, `"schatten_rauch"`, `"explosion_ring"`.
- **Akzeptanzkriterien:**
  - Alle 12 Partikel-Sheets existieren unter `partikel/`, haben mindestens 3 Animationsframes in `"loop"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b31 -q && uv run pytest --ignore=tests/spec -q`

---

## B32 — Spielerin- & Klonita-Sprite-Rendering in `src/rendering.py` (`V6`)

- **Größe:** S
- **Abhängigkeiten:** `A18`, `B02`
- **Ziel-Dateien:** `src/rendering.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V6`), `src/rendering.py`, `src/sprite_render.py`, `tests/spec/test_phase_b.py` (`-k b32`)
- **Aufgabe:**
  1. Implementiere die Fassade `Renderer` in `src/rendering.py` laut `V6` („Renderer“): `__init__` legt `self.sheet_cache = SheetCache()` an; `draw(run)` zeichnet Welt, Kreaturen, Pickups und Spielerin über die vorhandenen Zeichenfunktionen und ruft danach `draw_hud` auf.
  2. Zeichne in `Renderer.draw` die Spielerin über `charaktere/spielerin` (passend zu Bewegungszustand `idle`/`walk`/`jump`/`fall`/`hurt`, Blickrichtung `facing` und `glow_points`) sowie Klonita (falls auf `Run` vorhanden und `state != "dismissed"`) über `charaktere/klonita`.
- **Akzeptanzkriterien:**
  - `Renderer(screen).sheet_cache` ist ein `SheetCache`; `Renderer(screen).draw(Run(seed=1))` läuft headless fehlerfrei und zeichnet Spielerin und Klonita über `blit_frame`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b32 -q && uv run pytest --ignore=tests/spec -q`

---

## B33 — Modulare Zauberstab-Darstellung in der Hand & im HUD (`V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A23`, `B20`, `B32`
- **Ziel-Dateien:** `src/rendering.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8b`), `src/weapon_parts.py`, `src/rendering.py`, `tests/spec/test_phase_b.py` (`-k b33`)
- **Aufgabe:**
  1. Ergänze in `src/rendering.py` `draw_wand_parts(target, cache, wand, screen_x, screen_y, angle_deg=0.0, flip_x=False)`, das `layout_for(wand)` aus `src/weapon_parts.py` nutzt, um Griff, Kern und Spitze aus `waffen/` in der Hand der Spielerin sowie in der Zauberstab-Anzeige zu zeichnen.
- **Akzeptanzkriterien:**
  - `draw_wand_parts` zeichnet alle Teile aus `layout_for(wand)` ohne Ausnahme auf ein Test-Surface und verändert das Aussehen je nach bestückten Blöcken.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b33 -q && uv run pytest --ignore=tests/spec -q`

---

## B34 — Kreaturen-, Agenten- & Boss-Rig-Rendering in `src/rendering.py` (`V6`, `V7`)

- **Größe:** S
- **Abhängigkeiten:** `B04`, `B14`, `B19`, `B32`
- **Ziel-Dateien:** `src/rendering.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V6`, `V7`), `src/rendering.py`, `src/procbody.py`, `tests/spec/test_phase_b.py` (`-k b34`)
- **Aufgabe:**
  1. Aktualisiere die Kreaturen-Zeichenfunktion in `src/rendering.py`: Wähle das passende Sheet aus `kreaturen/`, `bosse/` oder `charaktere/` (`agent_*`, `boese_*`, `ober_cloita`), zeichne bei `state == "windup"` das Telegrafie-Aufleuchten (`flash`), nutze bei Bossen mit `RIG_LAYOUTS`-Eintrag `ProcRig.world_parts` und trage `glow_points` in die Beleuchtungsmaske ein.
- **Akzeptanzkriterien:**
  - Reguläre Kreaturen, Agenten und mehrteilige Bosse werden im Headless-Test ohne Fehler über `SheetCache` und `ProcRig` gerendert; `state == "windup"` aktiviert `flash > 0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b34 -q && uv run pytest --ignore=tests/spec -q`

---

## B35 — Pickup-, Stations- & Umgebungs-Prop-Rendering in `src/rendering.py` (`V6`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A05`, `B27`, `B30`, `B32`
- **Ziel-Dateien:** `src/rendering.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `src/rendering.py`, `src/loot.py`, `tests/spec/test_phase_b.py` (`-k b35`)
- **Aufgabe:**
  1. Aktualisiere `draw_pickups` in `src/rendering.py`, sodass jedes `Pickup` über `pickup_sprite_key(p)` aus `gegenstaende/` gezeichnet wird (und bei `kind == "block"` das spezifische Zauber-Icon aus `zauber/<item_key>` anzeigt).
  2. Ergänze `draw_props_and_stations` in `src/rendering.py` für `level.destructible_props` und Werkstatt-Stationen aus `umgebung/`.
- **Akzeptanzkriterien:**
  - Alle 18 `Pickup.kind`-Varianten und zerstörbare Props werden im Headless-Test fehlerfrei über `SheetCache` gezeichnet.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b35 -q && uv run pytest --ignore=tests/spec -q`

---

## B36 — Vollständiger Sprite-Generierungslauf & Qualitäts-Abnahme (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B05`, `B14`, `B19`, `B24`, `B27`, `B31`
- **Ziel-Dateien:** `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `tools/sprites.py`, `tests/spec/test_phase_b.py` (`-k b36`)
- **Aufgabe:**
  1. Vervollständige `build_all()` in `tools/sprites.py`, sodass ein einziger Aufruf `uv run python -m tools.sprites` sämtliche Sheets in `charaktere/`, `kreaturen/`, `bosse/`, `waffen/`, `zauber/`, `gegenstaende/`, `umgebung/` und `partikel/` deterministisch erzeugt.
- **Akzeptanzkriterien:**
  - `uv run python -m tools.sprites` läuft unter 5 Sekunden fehlerfrei durch.
  - Der schreibgeschützte Abnahmetest `tests/spec/test_phase_b.py -k b36` bestätigt alle `V8`-Qualitätskriterien (`.png`/`.json`-Paar existiert, über `load_sheet_meta` ladbar, mindestens 5 verschiedene RGB-Farben und `> 20 %` nicht-transparente Pixel im ersten Frame) ohne Ausnahme.
- **Verifikation:** `uv run python -m tools.sprites && uv run pytest tests/spec/test_phase_b.py -k b36 -q && uv run pytest --ignore=tests/spec -q`
