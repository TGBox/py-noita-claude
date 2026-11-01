# Phase G — UI, Entdeckungs-Archiv, Speichern/Laden & Vollabnahme (10 atomare S-Karten: `G01`–`G10`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien + `1` Testdatei, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md). Alle Karten folgen `V22`–`V23` aus [v21-klonita-ui-und-speichern.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v21-klonita-ui-und-speichern.md) und `V14` aus [v09-universen-und-ereignisse.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v09-universen-und-ereignisse.md).

---

## G01 — HUD-Erweiterung: Gold, Fahndungssterne, Proben-Beutel & Event-/Challenge-Banner (`src/hud.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `D14`, `F02`, `F14`
- **Ziel-Dateien:** `src/hud.py`, `tests/test_hud_extended.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/hud.py`
- **Aufgabe:**
  1. Erweitere `draw_hud` in `src/hud.py` (mit optionalen Keyword-Parametern bzw. Zugriff auf `run`-Attribute, sodass alte Aufrufe kompatibel bleiben) um:
     - Gold-Zähler (`Gold: <run.gold>`) und `0..5` Fahndungssterne (`run.wanted.stars`) oben rechts,
     - Proben-Beutel-Anzeige (`Proben: <belegt>/12`),
     - kompakte Statuszeile für aktives Sekundärereignis (`run.event`) und aktive Prüfung (`run.challenge`).
- **Akzeptanzkriterien:**
  - `draw_hud` rendert sowohl mit den bisherigen Positions-Argumenten als auch mit aktivem `gold`, `wanted`, `event` und `challenge` fehlerfrei auf ein Offscreen-Surface.
- **Verifikation:** `uv run pytest tests/test_hud_extended.py -k hud_bars -q && uv run pytest -q`

---

## G02 — HUD-Rendering für Sprechblasen (`run.bubbles`) & Boss-Phasenbanner (`src/hud.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `G01`
- **Ziel-Dateien:** `src/hud.py`, `src/rendering.py`, `tests/test_hud_extended.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/hud.py`, `src/rendering.py`
- **Aufgabe:**
  1. Ergänze in `src/hud.py` `draw_speech_bubbles(surface, small_font, bubbles, cam_x, cam_y)` (zeichnet abgerundete Sprechblasen mit Sprechername und Text, geklemmt an den sichtbaren Bildschirmbereich) sowie `draw_boss_banner(surface, font, banner)` und rufe beide in `Renderer.draw` (`src/rendering.py`) auf.
- **Akzeptanzkriterien:**
  - Eine Sprechblase in `run.bubbles` und ein aktives `run.boss_banner` werden von `draw_speech_bubbles` bzw. `draw_boss_banner` ohne Fehler (auch bei Weltkoordinaten außerhalb des Viewports) gezeichnet.
- **Verifikation:** `uv run pytest tests/test_hud_extended.py -k bubbles_and_banner -q && uv run pytest -q`

---

## G03 — Hover-Inspektion für Stationen, Proben, Händler, Klonita & Kreaturen-Haltung (`src/hover.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `E10`, `F14`
- **Ziel-Dateien:** `src/hover.py`, `tests/test_hover_extended.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/hover.py`
- **Aufgabe:**
  1. Erweitere `inspect_world` und `describe_pickup` in `src/hover.py` gemäß `V22`:
     - Pickups mit `kind == "sample"`, `"gold"`, `"blueprint_shard"`, `"memory_shard"`, `"badge"`, `"crate"`, `"formular_stempel"` liefern deutsche Titel, Untertitel und Beschreibungen.
     - In der Werkstatt erkennt `inspect_world` Stationen (`station_at`), den aktuellen Händler (`active_trader`) und Klonita.
     - Bei Kreaturen zeigt der Untertitel die deutsche Haltung (`"Friedlich"`, `"Scheu"`, `"Territorial"`, `"Feindselig"`, `"Bestochen"`).
- **Akzeptanzkriterien:**
  - `inspect_world` liefert für ein Proben-Pickup, eine Werkstatt-Station, Klonita und eine `"peaceful"`-Kreatur jeweils das erwartete deutsche `HoverInfo`-Objekt.
- **Verifikation:** `uv run pytest tests/test_hover_extended.py -q && uv run pytest -q`

---

## G04 — `Records`-Erweiterung, `discover`-Verzweigung & Rang-Berechnung (`src/records.py`) (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/records.py`, `src/perks.py`, `tests/test_records_and_ranks.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/records.py`, `src/perks.py`
- **Aufgabe:**
  1. Erweitere `Records` in `src/records.py` um `blueprints: list[str]`, `universes: list[str]`, `evil_selves: list[str]`, `badges: int = 0`, `best_rank: str = "Praktikantin"` und aktualisiere `discover(self, kind: str, key: str)` für `"block"`, `"blueprint"`, `"universe"`, `"evil_self"`, `"badge"` und `"creature"` exakt nach `V23`.
  2. Implementiere `RANKS`, `compute_score(...)` und `rank_for_score(score)` in `src/records.py` sowie `PERK_ALIASES` und `resolve_perk_key(key)` in `src/perks.py`.
- **Akzeptanzkriterien:**
  - `records.discover("universe", "myzel")` trägt `"myzel"` in `records.universes` ein, ohne `records.creatures` oder `total_kills` zu verändern.
  - `rank_for_score(0) == "Praktikantin"` und `rank_for_score(1600) == "Realitäts-Rebellin"`.
- **Verifikation:** `uv run pytest tests/test_records_and_ranks.py -q && uv run pytest -q`

---

## G05 — Entdeckungs-Archiv-Menü mit 5 Reitern (`"archive"`) in `src/menus.py` (`V22`, `V23`)

- **Größe:** S
- **Abhängigkeiten:** `G04`
- **Ziel-Dateien:** `src/menus.py`, `tests/test_archive_menu.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`, `V23`), `src/menus.py`, `src/records.py`
- **Aufgabe:**
  1. Erweitere das Archiv-Menü (`draw_archive_menu` in `src/menus.py`), sodass mit `[Tab]` oder `[Links]`/`[Rechts]` zwischen den 5 Reitern `"Zaubermodule"`, `"Baupläne"`, `"Kreaturen"`, `"Universen"` und `"Böse Ichs"` gewechselt werden kann und der Entdeckungsfortschritt (`entdeckt / gesamt`) sowie `records.best_rank` und `records.badges` angezeigt werden.
- **Akzeptanzkriterien:**
  - `draw_archive_menu` rendert für alle `tab_index in range(5)` fehlerfrei auf ein Offscreen-Surface und zeigt entdeckte Einträge aus `Records` im Klartext sowie unentdeckte als `"???"`.
- **Verifikation:** `uv run pytest tests/test_archive_menu.py -q && uv run pytest -q`

---

## G06 — Sieges-/Todes-Endbildschirm mit Punktestand & Rang-Abrechnung (`src/menus.py`, `src/run.py`) (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `G04`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`, `tests/test_records_and_ranks.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/menus.py`, `src/run.py`
- **Aufgabe:**
  1. Berechne auf `Run` (`src/run.py`) über `final_score(self) -> int` und `final_rank(self) -> str` den Endpunktestand mittels `compute_score` (`depth`, `kills`, `gold`, gesammelte Proben, gewonnene Challenges, besiegte Bosse, `victory`, `true_ending`) und aktualisiere bei Run-Ende `self.records.best_rank`.
  2. Zeige im Game-Over- und Victory-Overlay (`src/menus.py`) die Aufschlüsselung von `final_score()`, den erreichten Rang (`final_rank()`) und bei `true_ending == True` den Sondertitel `"Wahres Ende: Realitäts-Rebellin"` an.
- **Akzeptanzkriterien:**
  - Ein gewonnener Run mit `true_ending=True` erreicht mindestens den Rang `"Erz-Klonologin"` bzw. `"Realitäts-Rebellin"` und aktualisiert `records.best_rank`.
- **Verifikation:** `uv run pytest tests/test_records_and_ranks.py -k endscreen -q && uv run pytest -q`

---

## G07 — Vollständige Save/Load-Serialisierung Teil 1: `Run`-, `Level`- & `Inventory`-Felder (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `E11`, `F10`, `G04`
- **Ziel-Dateien:** `src/run.py`, `tests/test_save_load_full.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/run.py` (Zeilen 580–740)
- **Aufgabe:**
  1. Erweitere `Run.save_state` und `Run.restore` in `src/run.py` um die Run- und Level-Felder aus `V23` (`gold`, `memory_shards`, `blueprint_shards`, `badges`, `price_factor`, `next_boost`, `in_workshop`, `in_headquarters`, `true_ending`, `plan`, `samples` in `Inventory`, `level_meta`), während `live["level"]` für Abwärtskompatibilität exakt die 5-Elemente-Liste bleibt.
- **Akzeptanzkriterien:**
  - `save_state()` gefolgt von `restore()` stellt `gold`, `samples`, `plan`, `in_workshop`, `level.regions`, `level.mid_boss_arena` und `level.boss_arena` exakt wieder her; alte Save-Payloads ohne `level_meta` laden weiterhin fehlerfrei.
- **Verifikation:** `uv run pytest tests/test_save_load_full.py -k run_and_level -q && uv run pytest -q`

---

## G08 — Vollständige Save/Load-Serialisierung Teil 2: `Wanted`, `Event`, `Challenge`, `Klonita`, `Creature` & Status-Timer (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `G07`
- **Ziel-Dateien:** `src/run.py`, `tests/test_save_load_full.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/run.py` (Zeilen 580–797)
- **Aufgabe:**
  1. Erweitere `Run.save_state` und `Run.restore` (`src/run.py`) um `wanted`, `grudges`, `event`, `challenge`, `klonita`, die 8 neuen `Player.body`-Status-Timer (`drunk`..`befogged`) sowie die erweiterten `Creature`-Felder (`state`, `aggro`, `group_id`, `generation`, `carrying`, `bribed`, `giver`) und reinitialisiere `self.boss_script = make_boss_script(boss)` nach dem Laden lebender Bosse.
- **Akzeptanzkriterien:**
  - Ein mitten in einem Event, einer Challenge und einem Bosskampf gespeicherter `Run` stellt nach `restore()` alle Teilzustände (`wanted.level`, `event.remaining`, `challenge.elapsed`, `klonita.state`, `creature.bribed`, `player.body.stamped_good`, `boss_script.phase`) verlustfrei wieder her.
- **Verifikation:** `uv run pytest tests/test_save_load_full.py -q && uv run pytest -q`

---

## G09 — Tastatur- & Maus-Steuerung für alle neuen Werkstatt- und Begegnungs-Menüs in `src/game.py` / `src/run.py` (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `E14`, `F08`, `G05`
- **Ziel-Dateien:** `src/run.py`, `tests/test_menu_navigation.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/run.py`, `src/menus.py`
- **Aufgabe:**
  1. Bündele die Menü-Eingabeverarbeitung in `Run.handle_menu_input(self, key: int) -> bool` (`src/run.py`) für alle 5 `menu_mode`-Zustände (`"portal_select"`, `"fabricator"`, `"trader"`, `"empress_bargain"`, `"archive"`): Navigation mit Pfeiltasten / `W`/`S`/`A`/`D`, Bestätigen mit `Enter`/`E`/`1`–`4`, Proben-Tausch mit `T`, Reroll mit `R`, Schließen mit `Escape`.
- **Akzeptanzkriterien:**
  - Jeder der 5 `menu_mode`-Zustände lässt sich im Test komplett per Tastendruck (`handle_menu_input`) bedienen und mit `pygame.K_ESCAPE` sauber auf `menu_mode == ""` schließen.
- **Verifikation:** `uv run pytest tests/test_menu_navigation.py -q && uv run pytest -q`

---

## G10 — Bot-Vollabnahme über alle 9 Universen, Werkstatt & Hauptquartier (`V14`)

- **Größe:** S
- **Abhängigkeiten:** `D16`, `G08`, `G09`
- **Ziel-Dateien:** `tests/test_full_acceptance.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V14`), `docs/plan/vertraege.md`
- **Aufgabe:**
  1. Erstelle `tests/test_full_acceptance.py` als abschließende End-to-End-Abnahmesuite:
     - Führt `run_bot(u_key, seed=42, max_seconds=20.0)` über alle 9 Universen in `UNIVERSES` aus (`errors == []`, `stuck_ratio < 0.75`).
     - Prüft einen kompletten Zyklus aus Universum 1 → Werkstatt (Stationen, Fabrikator, Händler, Portalwahl) → Universum 2 → Save/Load-Roundtrip → Hauptquartier (`enter_headquarters` bis Sieg über `"ober_cloita"`).
- **Akzeptanzkriterien:**
  - `uv run pytest -q` und `uv run ruff check src tests tools` laufen ohne jeden Fehler über die gesamte Codebasis durch.
- **Verifikation:** `uv run pytest tests/test_full_acceptance.py -q && uv run pytest -q && uv run ruff check src tests tools`
