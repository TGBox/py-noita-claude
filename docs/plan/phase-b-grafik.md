# Phase B — Prozedurale Grafik & Sprite-Sheets (36 atomare S-Karten: `B01`–`B36`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien + `1` Testdatei, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md). Alle Grafik-Karten halten die Qualitätsregeln aus [v05-sprites-und-teile.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v05-sprites-und-teile.md) (`V8`) ein: mindestens 5 Farbtöne pro Sprite, dunkle Kontur `OUTLINE_DARK`, `> 20 %` nicht-transparente Pixel, `.png` + `.json` Paar.

---

## B01 — Spielerin-Sprite-Sheet (`charaktere/spielerin`) (`V5`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tools/sprites.py`, `tests/test_sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`, `V8`), `tools/palette.py`, `tools/sprites.py`
- **Aufgabe:**
  1. Erstelle `tools/sprites_chars.py` und implementiere `build_player_sheet(out_dir)` für `charaktere/spielerin.{png,json}` (`20×24` px pro Frame, Animationen `"idle"` (4), `"walk"` (6), `"jump"` (2), `"fall"` (2), `"cast"` (3), `"hurt"` (2), `"dead"` (1)) mit Kapuzenmantel, leuchtendem Zauberfokus (`glow`-Punkt) und Schattierung aus `ENTITY_PALETTES["spielerin"]`.
  2. Registriere `build_player_sheet` in `tools/sprites.py` (`build_all`).
- **Akzeptanzkriterien:**
  - `charaktere/spielerin.png` und `charaktere/spielerin.json` existieren nach Aufruf, haben `frame_size == (20, 24)` und enthalten alle 7 benannten Animationen sowie mindestens 1 `glow`-Punkt.
- **Verifikation:** `uv run pytest tests/test_sprites_chars.py -k player -q && uv run pytest -q`

---

## B02 — Klonita-Sprite-Sheet (`charaktere/klonita`) (`V5`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tests/test_sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`, `V8`), `tools/sprites_chars.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_klonita_sheet(out_dir)` für `charaktere/klonita.{png,json}` (`18×22` px, Animationen `"idle"` (4), `"fly"` (4), `"assist"` (3), `"quirk"` (3), `"knocked"` (2)) mit schwebendem Saum, schiefem Hexenhut und lila Laternen-`glow`.
- **Akzeptanzkriterien:**
  - `charaktere/klonita.{png,json}` wird erzeugt, besitzt alle 5 Animationen (`idle`, `fly`, `assist`, `quirk`, `knocked`) und besteht den `V8`-Qualitätstest (`>= 5` Farben, `> 20 %` Füllgrad).
- **Verifikation:** `uv run pytest tests/test_sprites_chars.py -k klonita -q && uv run pytest -q`

---

## B03 — Behörden-Agenten-Sheets (`charaktere/agent_*`) (`V8`, `V15`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tests/test_sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `tools/sprites_chars.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_agent_sheets(out_dir)` für die 3 Behörden-Agenten in `charaktere/`: `"agent_sachbearbeiter"` (`18×22`), `"agent_vollstrecker"` (`22×26` mit Aktenkoffer-Schild) und `"agent_abteilungsleiter"` (`24×28` schwebend mit Paragraphen-Krone), jeweils mit `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"`.
- **Akzeptanzkriterien:**
  - Alle 3 Sheets unter `charaktere/agent_*.{png,json}` existieren, lassen sich über `load_sheet_meta` laden und erfüllen die `V8`-Qualitätsregeln.
- **Verifikation:** `uv run pytest tests/test_sprites_chars.py -k agent -q && uv run pytest -q`

---

## B04 — Böse-Ichs- & Ober-Cloita-Sheets (`charaktere/boese_*`, `ober_cloita`) (`V8`, `V17`)

- **Größe:** S
- **Abhängigkeiten:** `B03`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tests/test_sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `tools/sprites_chars.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_evil_and_hq_sheets(out_dir)` für `"boese_kaiserin"` (`22×26`), `"boese_gute"` (`22×26`), `"boese_omega"` (`24×28`) und `"ober_cloita"` (`36×42`), jeweils mit `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und leuchtenden `glow`-Punkten.
- **Akzeptanzkriterien:**
  - Alle 4 Sheets unter `charaktere/` existieren, haben gültige JSON-Metadaten mit `glow`-Einträgen und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_chars.py -k evil -q && uv run pytest -q`

---

## B05 — Die 6 Händler-Sprite-Sheets (`charaktere/npc_*`) (`V8`, `V19`)

- **Größe:** S
- **Abhängigkeiten:** `B01`
- **Ziel-Dateien:** `tools/sprites_chars.py`, `tests/test_sprites_chars.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `tools/sprites_chars.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_chars.py` `build_trader_sheets(out_dir)` für alle 6 Händler aus `V19`: `"npc_magenhaendler"`, `"npc_sachbearbeiterin"`, `"npc_glibberhaendler"`, `"npc_ameisenhehler"`, `"npc_dj"`, `"npc_kuester"` (`20×24` px, Animationen `"idle"` (4), `"talk"` (3), `"hurt"` (2)).
- **Akzeptanzkriterien:**
  - Alle 6 `charaktere/npc_*.{png,json}`-Dateien existieren, enthalten `"idle"`, `"talk"`, `"hurt"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_chars.py -k trader -q && uv run pytest -q`

---

## B06 — Kreaturen-Sheets Universum 1 (`schrott`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tools/sprites.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`schrott`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_creatures.py` (und binde es in `tools/sprites.py` ein) mit den 4 Kreaturen-Sheets für `schrott` unter `kreaturen/`: `"rostkaefer"`, `"schweissimp"`, `"magnetwurm"`, `"schrottgolem"` (inkl. `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und Glühpunkten für Schweißflamme/Magnetkern).
- **Akzeptanzkriterien:**
  - Alle 4 Sheets unter `kreaturen/` existieren und bestehen den `V8`-Qualitätstest.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k schrott -q && uv run pytest -q`

---

## B07 — Kreaturen-Sheets Universum 2 (`myzel`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`myzel`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `myzel`: `"sporenwerfer"`, `"leuchtmotte"`, `"kappenschleicher"`, `"tuersteherpilz"` (inkl. Biolumineszenz-`glow` bei `"leuchtmotte"` und `"sporenwerfer"`).
- **Akzeptanzkriterien:**
  - Alle 4 `myzel`-Sheets unter `kreaturen/` existieren, `"leuchtmotte"` hat `len(meta.glow) >= 1`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k myzel -q && uv run pytest -q`

---

## B08 — Kreaturen-Sheets Universum 3 (`magen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`magen`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `magen`: `"saeurespucker"`, `"zottenwurm"`, `"gallenblase"`, `"bandwurm_kopf"`.
- **Akzeptanzkriterien:**
  - Alle 4 `magen`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k magen -q && uv run pytest -q`

---

## B09 — Kreaturen-Sheets Universum 4 (`amt`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`amt`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `amt`: `"stempelkaefer"`, `"aktenfresser"`, `"paragraphenreiter"`, `"kaffeegolem"`.
- **Akzeptanzkriterien:**
  - Alle 4 `amt`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k amt -q && uv run pytest -q`

---

## B10 — Kreaturen-Sheets Universum 5 (`kuchen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`kuchen`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `kuchen`: `"zuckerspinne"`, `"kerzenkobold"` (mit Kerzenflammen-`glow`), `"marzipanschwein"`, `"baiser_geist"`.
- **Akzeptanzkriterien:**
  - Alle 4 `kuchen`-Sheets unter `kreaturen/` existieren, `"kerzenkobold"` hat `glow`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k kuchen -q && uv run pytest -q`

---

## B11 — Kreaturen-Sheets Universum 6 (`abtei`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`abtei`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `abtei`: `"moenchsfisch"`, `"glockenqualle"` (mit Biolumineszenz-`glow`), `"korallenwaechter"`, `"weihrauch_aal"`.
- **Akzeptanzkriterien:**
  - Alle 4 `abtei`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k abtei -q && uv run pytest -q`

---

## B12 — Kreaturen-Sheets Universum 7 (`ameisen`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`ameisen`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `ameisen`: `"arbeiterameise"`, `"ameisensoldat"`, `"harzspucker"`, `"blattlaus"`.
- **Akzeptanzkriterien:**
  - Alle 4 `ameisen`-Sheets unter `kreaturen/` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k ameisen -q && uv run pytest -q`

---

## B13 — Kreaturen-Sheets Universum 8 (`spule`: 4 Spezies) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`spule`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `spule`: `"funkenhornisse"`, `"spulenkrabbe"`, `"kupferschlange"`, `"kondensator_geist"` (mit Elektro-`glow`).
- **Akzeptanzkriterien:**
  - Alle 4 `spule`-Sheets unter `kreaturen/` existieren, `"funkenhornisse"` und `"kondensator_geist"` besitzen `glow`, und alle erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k spule -q && uv run pytest -q`

---

## B14 — Kreaturen-Sheets Universum 9 (`glibber`: 4 Spezies) + Legacy-Kreaturen (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B06`
- **Ziel-Dateien:** `tools/sprites_creatures.py`, `tests/test_sprites_creatures.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py` (`glibber`), `src/enemies.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_creatures.py` die 4 Kreaturen-Sheets für `glibber`: `"quallenhund"`, `"zuckerwatte_wolke"`, `"trampolin_frosch"`, `"konfetti_kanone"` sowie kompakte Sheets für die 9 bestehenden Basis-Spezies aus `src/enemies.py` (`"beetle"`, `"moth"`, `"imp"`, `"leech"`, `"crawler"`, `"golem"`, `"wisp"`, `"turret"`, `"weaver"`).
- **Akzeptanzkriterien:**
  - Alle 36 Universums-Kreaturen + 9 Basis-Spezies existieren als `.png`/`.json` unter `kreaturen/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_creatures.py -k glibber -q && uv run pytest -q`

---

## B15 — Zwischenboss-Sheets Teil 1 (`schrott`, `myzel`, `magen`, `amt`, `kuchen`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `tools/sprites.py`, `tests/test_sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Erstelle `tools/sprites_bosses.py` (und binde es in `tools/sprites.py` ein) mit den ersten 5 Zwischenboss-Sheets (`28×28` bis `32×32` px) unter `bosse/`: `"gabelstapler_krabbe"` (`schrott`), `"sporenherz"` (`myzel`), `"pfuetzenwurm"` (`magen`), `"aktenwolf"` (`amt`), `"marzipan_ritter"` (`kuchen`).
- **Akzeptanzkriterien:**
  - Alle 5 Zwischenboss-Sheets existieren unter `bosse/`, haben `"idle"`, `"walk"`, `"windup"`, `"attack"`, `"hurt"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_bosses.py -k mid_part1 -q && uv run pytest -q`

---

## B16 — Zwischenboss-Sheets Teil 2 (`abtei`, `ameisen`, `spule`, `glibber` + `"warden"`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `tests/test_sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die restlichen 4 Zwischenboss-Sheets unter `bosse/`: `"glockenwaechter"` (`abtei`), `"harzgeneral"` (`ameisen`), `"spulenmeister"` (`spule`), `"manege_clown"` (`glibber`) sowie das Sheet für den Legacy-Boss `"warden"`.
- **Akzeptanzkriterien:**
  - Alle 9 Zwischenbosse aus `[u.mid_boss for u in UNIVERSES.values()]` + `"warden"` existieren unter `bosse/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_bosses.py -k mid_part2 -q && uv run pytest -q`

---

## B17 — Endboss-Sheets & Körperteile Teil 1 (`schrottpresse`, `muttermyzel`, `pfuetzenkoenig`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `A20`, `B15`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`, `tests/test_sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets (`36×36` bis `48×48` px) unter `bosse/` für `"schrottpresse"` (Stempelkolben + Magnetgreifer), `"muttermyzel"` (Hauptknolle + Sporenkelche) und `"pfuetzenkoenig"` (Säurekrone + Schlund) und trage ihre `PartLayout`-Definitionen in `RIG_LAYOUTS` (`src/procbody.py`) ein.
- **Akzeptanzkriterien:**
  - Sheets und `RIG_LAYOUTS`-Einträge für `"schrottpresse"`, `"muttermyzel"` und `"pfuetzenkoenig"` existieren und bestehen den `V8`-Qualitätstest.
- **Verifikation:** `uv run pytest tests/test_sprites_bosses.py -k end_part1 -q && uv run pytest -q`

---

## B18 — Endboss-Sheets & Körperteile Teil 2 (`oberamtsrat`, `hochzeitstorte`, `abt_nautilus`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B17`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`, `tests/test_sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets unter `bosse/` für `"oberamtsrat"` (Riesenstempel + Aktenflügel), `"hochzeitstorte"` (3 abschmelzbare Torten-Etagen) und `"abt_nautilus"` (Spiralschale + Glockententakel) und registriere ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`).
- **Akzeptanzkriterien:**
  - Sheets und `RIG_LAYOUTS`-Einträge für `"oberamtsrat"`, `"hochzeitstorte"` (mit 3 Etagen-Teilen) und `"abt_nautilus"` existieren und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_bosses.py -k end_part2 -q && uv run pytest -q`

---

## B19 — Endboss-Sheets & Körperteile Teil 3 (`koenigin_mandibula`, `transformator`, `zirkusdirektor`) (`V7`, `V8`)

- **Größe:** S
- **Abhängigkeiten:** `B18`
- **Ziel-Dateien:** `tools/sprites_bosses.py`, `src/procbody.py`, `tests/test_sprites_bosses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`, `V8`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_bosses.py` die Haupt- und Körperteil-Sheets unter `bosse/` für `"koenigin_mandibula"` (Abdomen + Mandibeln), `"transformator"` (Spulenturm + Elektrodenarme) und `"zirkusdirektor"` (Wackelzylinder + Peitschenarm) und registriere ihre `PartLayout`-Einträge in `RIG_LAYOUTS` (`src/procbody.py`).
- **Akzeptanzkriterien:**
  - Alle 9 Endbosse aus `[u.boss for u in UNIVERSES.values()]` haben sowohl gültige Sheets unter `bosse/` als auch `PartLayout`-Einträge in `RIG_LAYOUTS`.
- **Verifikation:** `uv run pytest tests/test_sprites_bosses.py -k end_part3 -q && uv run pytest -q`

---

## B20 — Die 10 Waffenteil-Sprites (`waffen/*`) (`V8`, `V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A22`, `A23`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tools/sprites.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`, `V8b`), `src/weapon_parts.py`
- **Aufgabe:**
  1. Erstelle `tools/sprites_items.py` (und binde es in `tools/sprites.py` ein) mit `build_weapon_part_sheets(out_dir)`, das für alle 10 Schlüssel in `WEAPON_PART_KEYS` (`griff_holz`, `griff_eisen`, `griff_knochen`, `kern_rubin`, `kern_spule`, `kern_auge`, `kern_leere`, `spitz_prisma`, `spitz_gabel`, `spitz_zahn`) ein `12×8`-Sprite-Sheet + `.json` unter `waffen/` erzeugt (mit `glow`-Punkt auf den Spitzen und Kernen).
- **Akzeptanzkriterien:**
  - Für jeden Schlüssel in `WEAPON_PART_KEYS` existiert `waffen/<key>.{png,json}` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k weapon_parts -q && uv run pytest -q`

---

## B21 — Zauber-Icons Pack 1: Formen & Payloads Teil 1 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die ersten 9 `12×12`-Zauberblock-Icons unter `zauber/`: `"spark"`, `"bolt"`, `"orb"`, `"lance"`, `"laser"`, `"burst"`, `"nova"`, `"beam"`, `"fire"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}`, haben `frame_size == (12, 12)` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k spells_pack1 -q && uv run pytest -q`

---

## B22 — Zauber-Icons Pack 2: Payloads Teil 2 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B21`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die nächsten 9 `12×12`-Zauberblock-Icons unter `zauber/`: `"ice"`, `"acid_orb"`, `"spore"`, `"lightning"`, `"plasma"`, `"dig"`, `"saw"`, `"black_hole"`, `"nuke"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k spells_pack2 -q && uv run pytest -q`

---

## B23 — Zauber-Icons Pack 3: Modifikatoren Teil 1 (9 Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B22`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` 9 Modifikator-Icons (`12×12`) unter `zauber/`: `"bounce"`, `"pierce"`, `"homing"`, `"split_cast"`, `"heavy"`, `"speed"`, `"orbit"`, `"spiral"`, `"chaos"`.
- **Akzeptanzkriterien:**
  - Alle 9 Icons existieren unter `zauber/<key>.{png,json}` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k spells_pack3 -q && uv run pytest -q`

---

## B24 — Zauber-Icons Pack 4: Restliche Blöcke aus `BLOCKS` (alle verbleibenden Icons in `zauber/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B23`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/spells.py`
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die Icons für alle verbleibenden Schlüssel in `src/spells.py` (`BLOCKS`), darunter `"chain"`, `"echo"`, `"trigger"`, `"timer"`, `"heal"`, `"shield"`, `"mana_charge"`, `"blood_pact"`, `"omega"` sowie eventuelle weitere Schlüssel in `BLOCKS`.
- **Akzeptanzkriterien:**
  - Für **jeden** Schlüssel `k in BLOCKS` existiert `zauber/{k}.{png,json}` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k spells_all -q && uv run pytest -q`

---

## B25 — Gegenstands-Icons Pack 1: Die 9 Universums-Proben (`gegenstaende/probe_*`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A04`, `B20`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` `12×12`-Sprites unter `gegenstaende/` für die 9 Universums-Proben aus `SAMPLES`: `"probe_rost"`, `"probe_pilz"`, `"probe_saft"`, `"probe_papier"`, `"probe_zucker"`, `"probe_salz"`, `"probe_harz"`, `"probe_spule"`, `"probe_bunt"`.
- **Akzeptanzkriterien:**
  - Alle 9 Universums-Proben-Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k samples_u -q && uv run pytest -q`

---

## B26 — Gegenstands-Icons Pack 2: 5 seltene Proben & 3 Gold-Größen (`gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `B25`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die `12×12`-Sprites unter `gegenstaende/` für die 5 seltenen Proben (`"probe_knochen"`, `"probe_aether"`, `"probe_schatten"`, `"probe_gold"`, `"probe_kern"`) sowie die 3 Gold-Größen (`"gold_klein"`, `"gold_mittel"`, `"gold_gross"`).
- **Akzeptanzkriterien:**
  - Alle 14 Proben aus `SAMPLES` und alle 3 Gold-Sprites existieren unter `gegenstaende/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k samples_rare_and_gold -q && uv run pytest -q`

---

## B27 — Gegenstands-Icons Pack 3: Pickups & Sammelobjekte (12 Icons in `gegenstaende/`) (`V8`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `B26`
- **Ziel-Dateien:** `tools/sprites_items.py`, `tests/test_sprites_items.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_items.py` die restlichen 12 Pickup-Sprites unter `gegenstaende/`: `"stab"`, `"modul"`, `"gabe"`, `"flasche_voll"`, `"flasche_leer"`, `"lebenskapsel"`, `"kokon"`, `"auge"`, `"wuerfel"`, `"erinnerungssplitter"`, `"bauplan_splitter"`, `"beutekiste"`, `"dienstmarke"`, `"formular_stempel"`, `"portal_stein"`.
- **Akzeptanzkriterien:**
  - Jeder in der `V11`-Pickup-Tabelle referenzierte Sprite-Schlüssel existiert unter `gegenstaende/` und erfüllt `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_items.py -k pickups_all -q && uv run pytest -q`

---

## B28 — Umgebungs-Props Pack 1: Die 10 Werkstatt-Stationen (`umgebung/`) (`V8`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `A22`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tools/sprites.py`, `tests/test_sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`)
- **Aufgabe:**
  1. Erstelle `tools/sprites_env.py` (und binde es in `tools/sprites.py` ein) mit den 10 Stations-Sprites (`24×24` bis `32×32` px) unter `umgebung/` gemäß `V18`: `"portal_stein"`, `"fabrikator"`, `"haendler_stand"`, `"physik_o_mat"`, `"schiessstand"`, `"archiv_pult"`, `"klonita_sofa"`, `"akten_schredder"`, `"flaschen_brunnen"`, `"werkbank"` sowie `"portal_headquarters"` und `"trainings_attrappe"`.
- **Akzeptanzkriterien:**
  - Alle 10 `station.sprite_key` aus `V18` + `"portal_headquarters"` + `"trainings_attrappe"` existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_env.py -k stations -q && uv run pytest -q`

---

## B29 — Umgebungs-Props Pack 2: Schreine, Behälter & Gefahren (`umgebung/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B28`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tests/test_sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` 8 interaktive/zerstörbare Umgebungs-Props (`16×16` bis `24×24` px) unter `umgebung/`: `"pruefungs_schrein"`, `"geheim_altar"`, `"explosionsfass"`, `"saeure_behaelter"`, `"sporen_knolle"`, `"gold_statue"`, `"akten_regal"`, `"kuchen_kerze"`.
- **Akzeptanzkriterien:**
  - Alle 8 Props existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_env.py -k props_pack2 -q && uv run pytest -q`

---

## B30 — Umgebungs-Props Pack 3: Universums-Dekorationen (`umgebung/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B29`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tests/test_sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` 8 thematische Dekor-Props unter `umgebung/`: `"schrott_ventil"`, `"pilz_laterne"`, `"magen_zotte"`, `"amt_uhr"`, `"abtei_glocke"`, `"ameisen_kokon"`, `"spule_isolator"`, `"glibber_ballon"`.
- **Akzeptanzkriterien:**
  - Alle 8 Dekor-Props existieren unter `umgebung/` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_env.py -k props_pack3 -q && uv run pytest -q`

---

## B31 — Partikel- & Projektil-Sheets (`partikel/`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B30`
- **Ziel-Dateien:** `tools/sprites_env.py`, `tests/test_sprites_env.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`)
- **Aufgabe:**
  1. Ergänze in `tools/sprites_env.py` `build_particle_sheets(out_dir)` für 12 mehrframige `8×8`-/`12×12`-Effekt-Sheets unter `partikel/`: `"funken"`, `"flamme"`, `"eis_splitter"`, `"saeure_tropfen"`, `"sporen_wolke"`, `"blitz_bogen"`, `"heil_stern"`, `"stempel_abdruck"`, `"schleim_blase"`, `"zucker_glitzer"`, `"schatten_rauch"`, `"explosion_ring"`.
- **Akzeptanzkriterien:**
  - Alle 12 Partikel-Sheets existieren unter `partikel/`, haben mindestens 3 Animationsframes in `"loop"` und erfüllen `V8`.
- **Verifikation:** `uv run pytest tests/test_sprites_env.py -k particles -q && uv run pytest -q`

---

## B32 — Spielerin- & Klonita-Sprite-Rendering in `src/rendering.py` (`V6`)

- **Größe:** S
- **Abhängigkeiten:** `A18`, `B02`
- **Ziel-Dateien:** `src/rendering.py`, `tests/test_render_entities.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V6`), `src/rendering.py`, `src/sprite_render.py`
- **Aufgabe:**
  1. Binde `SheetCache` in `Renderer` (`src/rendering.py`) ein und zeichne die Spielerin über `charaktere/spielerin` (passend zu Bewegungszustand `idle`/`walk`/`jump`/`fall`/`hurt`, Blickrichtung `facing` und `glow_points`) sowie Klonita (falls auf `Run` vorhanden und `state != "dismissed"`) über `charaktere/klonita`.
- **Akzeptanzkriterien:**
  - `Renderer` rendert Spielerin und Klonita über `blit_frame` fehlerfrei auf ein Offscreen-Surface (getestet im Headless-Modus).
- **Verifikation:** `uv run pytest tests/test_render_entities.py -k player_and_klonita -q && uv run pytest -q`

---

## B33 — Modulare Zauberstab-Darstellung in der Hand & im HUD (`V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A23`, `B20`, `B32`
- **Ziel-Dateien:** `src/rendering.py`, `tests/test_render_entities.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8b`), `src/weapon_parts.py`, `src/rendering.py`
- **Aufgabe:**
  1. Ergänze in `src/rendering.py` `draw_wand_parts(target, cache, wand, screen_x, screen_y, angle_deg=0.0, flip_x=False)`, das `layout_for(wand)` aus `src/weapon_parts.py` nutzt, um Griff, Kern und Spitze aus `waffen/` in der Hand der Spielerin sowie in der Zauberstab-Anzeige zu zeichnen.
- **Akzeptanzkriterien:**
  - `draw_wand_parts` zeichnet alle Teile aus `layout_for(wand)` ohne Ausnahme auf ein Test-Surface und verändert das Aussehen je nach bestückten Blöcken.
- **Verifikation:** `uv run pytest tests/test_render_entities.py -k wand_parts -q && uv run pytest -q`

---

## B34 — Kreaturen-, Agenten- & Boss-Rig-Rendering in `src/rendering.py` (`V6`, `V7`)

- **Größe:** S
- **Abhängigkeiten:** `B04`, `B14`, `B19`, `B32`
- **Ziel-Dateien:** `src/rendering.py`, `tests/test_render_entities.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V6`, `V7`), `src/rendering.py`, `src/procbody.py`
- **Aufgabe:**
  1. Aktualisiere die Kreaturen-Zeichenfunktion in `src/rendering.py`: Wähle das passende Sheet aus `kreaturen/`, `bosse/` oder `charaktere/` (`agent_*`, `boese_*`, `ober_cloita`), zeichne bei `state == "windup"` das Telegrafie-Aufleuchten (`flash`), nutze bei Bossen mit `RIG_LAYOUTS`-Eintrag `ProcRig.world_parts` und trage `glow_points` in die Beleuchtungsmaske ein.
- **Akzeptanzkriterien:**
  - Reguläre Kreaturen, Agenten und mehrteilige Bosse werden im Headless-Test ohne Fehler über `SheetCache` und `ProcRig` gerendert; `state == "windup"` aktiviert `flash > 0`.
- **Verifikation:** `uv run pytest tests/test_render_entities.py -k creatures_and_bosses -q && uv run pytest -q`

---

## B35 — Pickup-, Stations- & Umgebungs-Prop-Rendering in `src/rendering.py` (`V6`, `V11`)

- **Größe:** S
- **Abhängigkeiten:** `A05`, `B27`, `B30`, `B32`
- **Ziel-Dateien:** `src/rendering.py`, `tests/test_render_entities.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `src/rendering.py`, `src/loot.py`
- **Aufgabe:**
  1. Aktualisiere `draw_pickups` in `src/rendering.py`, sodass jedes `Pickup` über `pickup_sprite_key(p)` aus `gegenstaende/` gezeichnet wird (und bei `kind == "block"` das spezifische Zauber-Icon aus `zauber/<item_key>` anzeigt).
  2. Ergänze `draw_props_and_stations` in `src/rendering.py` für `level.destructible_props` und Werkstatt-Stationen aus `umgebung/`.
- **Akzeptanzkriterien:**
  - Alle 18 `Pickup.kind`-Varianten und zerstörbare Props werden im Headless-Test fehlerfrei über `SheetCache` gezeichnet.
- **Verifikation:** `uv run pytest tests/test_render_entities.py -k pickups_and_props -q && uv run pytest -q`

---

## B36 — Vollständiger Sprite-Generierungslauf & Qualitäts-Abnahmetest (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `B05`, `B14`, `B19`, `B24`, `B27`, `B31`
- **Ziel-Dateien:** `tools/sprites.py`, `tests/test_all_sprites_quality.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `tools/sprites.py`
- **Aufgabe:**
  1. Vervollständige `build_all()` in `tools/sprites.py`, sodass ein einziger Aufruf `uv run python -m tools.sprites` sämtliche Sheets in `charaktere/`, `kreaturen/`, `bosse/`, `waffen/`, `zauber/`, `gegenstaende/`, `umgebung/` und `partikel/` deterministisch erzeugt.
  2. Schreibe `tests/test_all_sprites_quality.py`, der prüft, dass jedes erwartete `.png`/`.json`-Paar existiert, über `load_sheet_meta` ladbar ist, mindestens 5 verschiedene RGB-Farben besitzt und `> 20 %` nicht-transparente Pixel im ersten Frame aufweist.
- **Akzeptanzkriterien:**
  - `uv run python -m tools.sprites` läuft unter 5 Sekunden fehlerfrei durch.
  - `tests/test_all_sprites_quality.py` bestätigt alle `V8`-Qualitätskriterien ohne eine einzige Ausnahme.
- **Verifikation:** `uv run python -m tools.sprites && uv run pytest tests/test_all_sprites_quality.py -q && uv run pytest -q`
