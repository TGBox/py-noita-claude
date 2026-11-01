# Phase B — Prozedurale Grafik & Sprite-Sheets (36 atomare S-Karten: `B01`–`B36`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_b.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Grafik-Karten halten die Qualitätsregeln aus [v05-sprites-und-teile.md](vertraege/v05-sprites-und-teile.md) (`V8`) ein: mindestens 5 Farbtöne pro Sprite, dunkle Kontur `OUTLINE_DARK`, `> 20 %` nicht-transparente Pixel, `.png` + `.json` Paar.

---

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

## B06 — Kreaturen-Sheets Universum 1 (`schrott`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`schrott`), `tests/spec/test_phase_b.py` (`-k b06`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_creatures.py` (und binde es in `tools/sprites.py` ein) mit den 4 Kreaturen-Sheets für `schrott` unter `kreaturen/`: `"rostkaefer"`, `"schweissimp"`, `"magnetwurm"`, `"schrottgolem"` (inkl. `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und Glühpunkten für Schweißflamme/Magnetkern).
- **Akzeptanzkriterien:**
  - Alle 4 Sheets unter `kreaturen/` existieren und bestehen den `V8`-Qualitätstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b06 -q && uv run pytest --ignore=tests/spec -q`

---

## B07 — Kreaturen-Sheets Universum 2 (`myzel`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`myzel`), `tests/spec/test_phase_b.py` (`-k b07`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `myzel`: `"sporenwerfer"`, `"leuchtmotte"`, `"kappenschleicher"`, `"tuersteherpilz"` (inkl. Biolumineszenz-`glow` bei `"leuchtmotte"` und `"sporenwerfer"`).
- **Akzeptanzkriterien:**
  - Alle 4 `myzel`-Sheets unter `kreaturen/` existieren, `"leuchtmotte"` hat `len(meta.glow) >= 1`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b07 -q && uv run pytest --ignore=tests/spec -q`

---

## B08 — Kreaturen-Sheets Universum 3 (`magen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`magen`), `tests/spec/test_phase_b.py` (`-k b08`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `magen`: `"saeurespucker"`, `"zottenwurm"`, `"gallenblase"`, `"bandwurm_kopf"`.
- **Akzeptanzkriterien:**
  - Alle 4 `magen`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b08 -q && uv run pytest --ignore=tests/spec -q`

---

## B09 — Kreaturen-Sheets Universum 4 (`amt`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`amt`), `tests/spec/test_phase_b.py` (`-k b09`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `amt`: `"stempelkaefer"`, `"aktenfresser"`, `"paragraphenreiter"`, `"kaffeegolem"`.
- **Akzeptanzkriterien:**
  - Alle 4 `amt`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b09 -q && uv run pytest --ignore=tests/spec -q`

---

## B10 — Kreaturen-Sheets Universum 5 (`kuchen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`kuchen`), `tests/spec/test_phase_b.py` (`-k b10`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `kuchen`: `"zuckerspinne"`, `"kerzenkobold"` (mit Kerzenflammen-`glow`), `"marzipanschwein"`, `"baiser_geist"`.
- **Akzeptanzkriterien:**
  - Alle 4 `kuchen`-Sheets unter `kreaturen/` existieren, `"kerzenkobold"` hat `glow`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b10 -q && uv run pytest --ignore=tests/spec -q`

---

## B11 — Kreaturen-Sheets Universum 6 (`abtei`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`abtei`), `tests/spec/test_phase_b.py` (`-k b11`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `abtei`: `"moenchsfisch"`, `"glockenqualle"` (mit Biolumineszenz-`glow`), `"korallenwaechter"`, `"weihrauch_aal"`.
- **Akzeptanzkriterien:**
  - Alle 4 `abtei`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b11 -q && uv run pytest --ignore=tests/spec -q`

---

## B12 — Kreaturen-Sheets Universum 7 (`ameisen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`ameisen`), `tests/spec/test_phase_b.py` (`-k b12`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `ameisen`: `"arbeiterameise"`, `"ameisensoldat"`, `"harzspucker"`, `"blattlaus"`.
- **Akzeptanzkriterien:**
  - Alle 4 `ameisen`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b12 -q && uv run pytest --ignore=tests/spec -q`

---

## B13 — Kreaturen-Sheets Universum 8 (`spule`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`spule`), `tests/spec/test_phase_b.py` (`-k b13`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `spule`: `"funkenhornisse"`, `"spulenkrabbe"`, `"kupferschlange"`, `"kondensator_geist"` (mit Elektro-`glow`).
- **Akzeptanzkriterien:**
  - Alle 4 `spule`-Sheets unter `kreaturen/` existieren, `"funkenhornisse"` und `"kondensator_geist"` besitzen `glow`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b13 -q && uv run pytest --ignore=tests/spec -q`

---

## B14 — Kreaturen-Sheets Universum 9 (`glibber`: 4 Spezies) + Legacy-Kreaturen (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`glibber`), `src/enemies.py`, `tests/spec/test_phase_b.py` (`-k b14`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `glibber`: `"quallenhund"`, `"zuckerwatte_wolke"`, `"trampolin_frosch"`, `"konfetti_kanone"` sowie kompakte Sheets für die 9 bestehenden Basis-Spezies aus `src/enemies.py` (`"beetle"`, `"moth"`, `"imp"`, `"leech"`, `"crawler"`, `"golem"`, `"wisp"`, `"turret"`, `"weaver"`).
- **Akzeptanzkriterien:**
  - Alle 36 Universums-Kreaturen + 9 Basis-Spezies existieren als `.png`/`.json` unter `kreaturen/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b14 -q && uv run pytest --ignore=tests/spec -q`

---

## B15 — Zwischenboss-Sheets Teil 1 (`schrott`, `myzel`, `magen`, `amt`, `kuchen`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py`, `tests/spec/test_phase_b.py` (`-k b15`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_bosses.py` (und binde es in `tools/sprites.py` ein) mit den ersten 5 Zwischenboss-Sheets (`28×28` bis `32×32` px) unter `bosse/`: `"gabelstapler_krabbe"` (`schrott`), `"sporenherz"` (`myzel`), `"pfuetzenwurm"` (`magen`), `"aktenwolf"` (`amt`), `"marzipan_ritter"` (`kuchen`).
- **Akzeptanzkriterien:**
  - Alle 5 Zwischenboss-Sheets existieren unter `bosse/`, haben `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b15 -q && uv run pytest --ignore=tests/spec -q`

---

## B16 — Zwischenboss-Sheets Teil 2 (`abtei`, `ameisen`, `spule`, `glibber` + `"warden"`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py`, `tests/spec/test_phase_b.py` (`-k b16`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die restlichen 4 Zwischenboss-Sheets unter `bosse/`: `"glockenwaechter"` (`abtei`), `"harzgeneral"` (`ameisen`), `"spulenmeister"` (`spule`), `"manege_clown"` (`glibber`) sowie das Sheet für den Legacy-Boss `"warden"`.
- **Akzeptanzkriterien:**
  - Alle 9 Zwischenbosse aus `[u.mid_boss for u in UNIVERSES.values()]` + `"warden"` existieren unter `bosse/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b16 -q && uv run pytest --ignore=tests/spec -q`

---

## B17 — Zwischengegner- & Endboss-Sheets Teil 1 (`weltenherz`, `oberstempler`, `mutter_glibber` + Pool-Bosse) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `A20`, `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `tests/spec/test_phase_b.py` (`-k b17`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets (`36×36` bis `48×48` px) unter `bosse/` für `"weltenherz"` / `"pfuetzenkoenig"`, `"oberstempler"` / `"oberamtsrat"`, `"mutter_glibber"` / `"zirkusdirektor"`, `"schrottpresse"` und `"muttermyzel"` und trage ihre `PartLayout`-Definitionen in `RIG_LAYOUTS` (`src/procbody.py`) ein.
- **Akzeptanzkriterien:**
  - Sheets und `RIG_LAYOUTS`-Einträge für die genannten Bosse existieren und bestehen den `V8`-Qualitätstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b17 -q && uv run pytest --ignore=tests/spec -q`

---

## B18 — Zwischengegner- & Endboss-Sheets Teil 2 (`ameisenkoenigin`, `dj_myzel`, `abt_kieme` + Pool-Bosse) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B17`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `tests/spec/test_phase_b.py` (`-k b18`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets unter `bosse/` für `"ameisenkoenigin"` / `"koenigin_mandibula"`, `"dj_myzel"`, `"abt_kieme"` / `"abt_nautilus"` und `"hochzeitstorte"` (3 abschmelzbare Torten-Etagen) und registriere ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`).
- **Akzeptanzkriterien:**
  - Sheets und `RIG_LAYOUTS`-Einträge für `"oberstempler"`/`"oberamtsrat"`, `"hochzeitstorte"` (mit 3 Etagen-Teilen) und `"abt_kieme"`/`"abt_nautilus"` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b18 -q && uv run pytest --ignore=tests/spec -q`

---

## B19 — Zwischengegner-, Großkreaturen- & Endboss-Sheets Teil 3 (`trampolinwal`, `kirchenkrake`, `transformator`, `zirkusdirektor`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B18`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `tests/spec/test_phase_b.py` (`-k b19`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets unter `bosse/` bzw. `kreaturen/` für die Großkreaturen `"trampolinwal"` und `"kirchenkrake"` sowie `"koenigin_mandibula"`, `"transformator"` und `"zirkusdirektor"` und registriere ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`).
- **Akzeptanzkriterien:**
  - Alle 6 MVP-Bosse aus `[u.boss for u in UNIVERSES.values()]` (`weltenherz`, `oberstempler`, `mutter_glibber`, `ameisenkoenigin`, `dj_myzel`, `abt_kieme`) sowie die Pool-Bosse haben gültige Sheets unter `bosse/` und `PartLayout`-Einträge in `RIG_LAYOUTS`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b19 -q && uv run pytest --ignore=tests/spec -q`

---

## B20 — Die 10 Waffenteil-Sprites (`waffen/*`) (`V8`, `V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A22`, `A23`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`, `V8b`), `src/weapon_parts.py`, `tests/spec/test_phase_b.py` (`-k b20`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_items.py` (und binde es in `tools/sprites.py` ein) mit `build_weapon_part_sheets(out_dir)`, das für alle 10 Schlüssel in `WEAPON_PART_KEYS` (`griff_holz`, `griff_eisen`, `griff_knochen`, `kern_rubin`, `kern_spule`, `kern_auge`, `kern_leere`, `spitz_prisma`, `spitz_gabel`, `spitz_zahn`) ein `12×8`-Sprite-Sheet + `.json` unter `waffen/` erzeugt (mit `glow`-Punkt auf den Spitzen und Kernen).
- **Akzeptanzkriterien:**
  - Für jeden Schlüssel in `WEAPON_PART_KEYS` existiert `waffen/<key>.{png,json}` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b20 -q && uv run pytest --ignore=tests/spec -q`

---

## B21 — Zauber-Icons Pack 1: Formen & Payloads Teil 1 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`, `tests/spec/test_phase_b.py` (`-k b21`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die ersten 9 `12×12`-Zauberblock-Icons unter `zauber/`: `"spark"`, `"bolt"`, `"orb"`, `"lance"`, `"laser"`, `"burst"`, `"nova"`, `"beam"`, `"fire"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}`, haben `frame_size == (12, 12)` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b21 -q && uv run pytest --ignore=tests/spec -q`

---

## B22 — Zauber-Icons Pack 2: Payloads Teil 2 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B21`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`, `tests/spec/test_phase_b.py` (`-k b22`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die nächsten 9 `12×12`-Zauberblock-Icons unter `zauber/`: `"ice"`, `"acid_orb"`, `"spore"`, `"lightning"`, `"plasma"`, `"dig"`, `"saw"`, `"black_hole"`, `"nuke"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b22 -q && uv run pytest --ignore=tests/spec -q`

---

## B23 — Zauber-Icons Pack 3: Modifikatoren Teil 1 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B22`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`, `tests/spec/test_phase_b.py` (`-k b23`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` 9 Modifikator-Icons (`12×12`) unter `zauber/`: `"bounce"`, `"pierce"`, `"homing"`, `"split_cast"`, `"heavy"`, `"speed"`, `"orbit"`, `"spiral"`, `"chaos"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b23 -q && uv run pytest --ignore=tests/spec -q`

---

## B24 — Zauber-Icons Pack 4: Restliche Blöcke aus `BLOCKS` (alle verbleibenden Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B23`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`, `tests/spec/test_phase_b.py` (`-k b24`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die Icons für alle verbleibenden Schlüssel in `src/spells.py` (`BLOCKS`), darunter `"chain"`, `"echo"`, `"trigger"`, `"timer"`, `"heal"`, `"shield"`, `"mana_charge"`, `"blood_pact"`, `"omega"` sowie eventuelle weitere Schlüssel in `BLOCKS`.
- **Akzeptanzkriterien:**
  - Für **jeden** Schlüssel `k in BLOCKS` existiert `zauber/{k}.{png,json}` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b24 -q && uv run pytest --ignore=tests/spec -q`

---

## B25 — Gegenstands-Icons Pack 1: Die 12 Universums-Proben (`gegenstaende/probe_*`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A04`, `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `tests/spec/test_phase_b.py` (`-k b25`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` `12×12`-Sprites unter `gegenstaende/` für alle 12 kanonischen Universums-Proben aus `SAMPLES` (`"probe_gallenstein"`, `"probe_wucherung"`, `"probe_stempelkissen"`, `"probe_formular"`, `"probe_glibberkern"`, `"probe_brauseperle"`, `"probe_zuckerkristall"`, `"probe_ameisenduft"`, `"probe_leuchtspore"`, `"probe_plattennadel"`, `"probe_glockensplitter"`, `"probe_kerzenstumpf"`) sowie die Pool-Proben-Aliase.
- **Akzeptanzkriterien:**
  - Alle 12 Universums-Proben-Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b25 -q && uv run pytest --ignore=tests/spec -q`

---

## B26 — Gegenstands-Icons Pack 2: 5 seltene Proben & 3 Gold-Größen (`gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `B25`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `tests/spec/test_phase_b.py` (`-k b26`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die `12×12`-Sprites unter `gegenstaende/` für die 5 seltenen Proben (`"probe_knochen"`, `"probe_aether"`, `"probe_schatten"`, `"probe_gold"`, `"probe_kern"`) sowie die 3 Gold-Größen (`"gold_klein"`, `"gold_mittel"`, `"gold_gross"`).
- **Akzeptanzkriterien:**
  - Alle 17 Proben aus `SAMPLES` und alle 3 Gold-Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b26 -q && uv run pytest --ignore=tests/spec -q`

---

## B27 — Gegenstands-Icons Pack 3: Pickups & Sammelobjekte (12 Icons in `gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `B26`
- **Ziel-Dateien:** `tools/sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `tests/spec/test_phase_b.py` (`-k b27`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die restlichen 12 Pickup-Sprites unter `gegenstaende/`: `"stab"`, `"modul"`, `"gabe"`, `"flasche_voll"`, `"flasche_leer"`, `"lebenskapsel"`, `"kokon"`, `"auge"`, `"wuerfel"`, `"erinnerungssplitter"`, `"bauplan_splitter"`, `"beutekiste"`, `"dienstmarke"`, `"formular_stempel"`, `"portal_stein"`.
- **Akzeptanzkriterien:**
  - Jeder in der `V11`-Pickup-Tabelle referenzierte Sprite-Schlüssel existiert unter `gegenstaende/` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b27 -q && uv run pytest --ignore=tests/spec -q`

---

## B28 — Umgebungs-Props Pack 1: Die 12 Werkstatt-Stationen (`umgebung/`) (`V8`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `tests/spec/test_phase_b.py` (`-k b28`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_env.py` (und binde es in `tools/sprites.py` ein) mit den 12 Stations-Sprites (`24×24` bis `32×32` px) unter `umgebung/` gemäß `V18`: `"portal_stein"`, `"fabrikator"`, `"haendler_stand"`, `"physik_o_mat"`, `"schiessstand"`, `"archiv_pult"`, `"klonita_sofa"`, `"akten_schredder"`, `"flaschen_brunnen"`, `"werkbank"`, `"experimentier_liege"`, `"zapfhahn"` sowie `"portal_headquarters"` und `"trainings_attrappe"`.
- **Akzeptanzkriterien:**
  - Alle 12 `station.sprite_key` aus `V18` + `"portal_headquarters"` + `"trainings_attrappe"` existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b28 -q && uv run pytest --ignore=tests/spec -q`

---

## B29 — Umgebungs-Props Pack 2: Schreine, Behälter & Gefahren (`umgebung/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B28`
- **Ziel-Dateien:** `tools/sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `tests/spec/test_phase_b.py` (`-k b29`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` 8 interaktive/zerstörbare Umgebungs-Props (`16×16` bis `24×24` px) unter `umgebung/`: `"pruefungs_schrein"`, `"geheim_altar"`, `"explosionsfass"`, `"saeure_behaelter"`, `"sporen_knolle"`, `"gold_statue"`, `"akten_regal"`, `"kuchen_kerze"`.
- **Akzeptanzkriterien:**
  - Alle 8 Props existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_b.py -k b29 -q && uv run pytest --ignore=tests/spec -q`

---

## B30 — Umgebungs-Props Pack 3: Universums-Dekorationen (`umgebung/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B29`
- **Ziel-Dateien:** `tools/sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `tests/spec/test_phase_b.py` (`-k b30`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` 8 thematische Dekor-Props unter `umgebung/`: `"schrott_ventil"`, `"pilz_laterne"`, `"magen_zotte"`, `"amt_uhr"`, `"abtei_glocke"`, `"ameisen_kokon"`, `"spule_isolator"`, `"glibber_ballon"`.
- **Akzeptanzkriterien:**
  - Alle 8 Dekor-Props existieren unter `umgebung/` und erfüllen `V8`.
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
  1. Binde `SheetCache` in `Renderer` (`src/rendering.py`) ein und zeichne die Spielerin über `charaktere/spielerin` (passend zu Bewegungszustand `idle`/`walk`/`jump`/`fall`/`hurt`, Blickrichtung `facing` und `glow_points`) sowie Klonita (falls auf `Run` vorhanden und `state != "dismissed"`) über `charaktere/klonita`.
- **Akzeptanzkriterien:**
  - `Renderer` rendert Spielerin und Klonita über `blit_frame` fehlerfrei auf ein Offscreen-Surface (getestet im Headless-Modus).
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
