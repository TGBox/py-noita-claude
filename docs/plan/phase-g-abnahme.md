# Phase G — UI, Entdeckungs-Archiv, Speichern/Laden & Vollabnahme (15 atomare S-Karten: `G01`–`G15`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_g.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Karten folgen `V22`–`V23` aus [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md) und `V14` aus [v09-universen-und-ereignisse.md](vertraege/v09-universen-und-ereignisse.md).

---

## G01 — HUD nach Bibel 08: Flux, Gold, Siegel, Universum & Rang, Takt, Atem, Proben, Ereignis (`src/hud.py`) (`V22` §2)

- **Größe:** S
- **Abhängigkeiten:** `D14`, `D23`, `F02`, `F14`, `B32`
- **Ziel-Dateien:** `src/hud.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22` §2), `docs/bibel/08-ui-und-texte.md` („Oberfläche umbenennen“), `src/hud.py`, `tests/spec/test_phase_g.py` (`-k g01`)
- **Aufgabe:**
  1. Erweitere `draw_hud` in `src/hud.py` um alle Anzeigen aus `V22` §2 (alte Aufrufe bleiben gültig): Flux-Leiste, Gold mit Siegeln, „Universum x/6“ mit Rang-Sternen, Takt-Punkt, Atem-Leiste unter Wasser, Proben-Zähler sowie eine Zeile für Ereignis und Herausforderung.
- **Akzeptanzkriterien:**
  - `Renderer(surface).draw(run)` zeichnet mit Gold, 3 Sternen, aktivem Ereignis und angenommener Herausforderung fehlerfrei; ohne diese Werte ebenfalls.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g01 -q && uv run pytest --ignore=tests/spec -q`

---

## G02 — HUD-Rendering für Sprechblasen (`run.bubbles`) & Boss-Phasenbanner (`src/hud.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `G01`
- **Ziel-Dateien:** `src/hud.py`, `src/rendering.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/hud.py`, `src/rendering.py`, `tests/spec/test_phase_g.py` (`-k g02`)
- **Aufgabe:**
  1. Ergänze in `src/hud.py` `draw_speech_bubbles(surface, small_font, bubbles, cam_x, cam_y)` (zeichnet abgerundete Sprechblasen mit Sprechername und Text, geklemmt an den sichtbaren Bildschirmbereich) sowie `draw_boss_banner(surface, font, banner)` und rufe beide in `Renderer.draw` (`src/rendering.py`) auf.
- **Akzeptanzkriterien:**
  - Eine Sprechblase in `run.bubbles` und ein aktives `run.boss_banner` werden von `draw_speech_bubbles` bzw. `draw_boss_banner` ohne Fehler (auch bei Weltkoordinaten außerhalb des Viewports) gezeichnet.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g02 -q && uv run pytest --ignore=tests/spec -q`

---

## G03 — Hover-Inspektion für Stationen, Proben, Händler, Klonita & Kreaturen-Haltung (`src/hover.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `E10`, `F14`
- **Ziel-Dateien:** `src/hover.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/hover.py`, `tests/spec/test_phase_g.py` (`-k g03`)
- **Aufgabe:**
  1. Erweitere `inspect_world` und `describe_pickup` in `src/hover.py` gemäß `V22`:
     - Pickups mit `kind == "sample"`, `"gold"`, `"blueprint_shard"`, `"memory_shard"`, `"badge"`, `"crate"`, `"formular_stempel"` liefern deutsche Titel, Untertitel und Beschreibungen.
     - In der Werkstatt erkennt `inspect_world` Stationen (`station_at`), den aktuellen Händler (`active_trader`) und Klonita.
     - Bei Kreaturen zeigt der Untertitel die deutsche Haltung (`"Friedlich"`, `"Scheu"`, `"Territorial"`, `"Feindselig"`, `"Bestochen"`).
- **Akzeptanzkriterien:**
  - `inspect_world` liefert für ein Proben-Pickup, eine Werkstatt-Station, Klonita und eine `"peaceful"`-Kreatur jeweils das erwartete deutsche `HoverInfo`-Objekt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g03 -q && uv run pytest --ignore=tests/spec -q`

---

## G04 — `Records`-Erweiterung, `discover`-Verzweigung & Rang-Berechnung (`src/records.py`) (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/records.py`, `src/perks.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/records.py`, `src/perks.py`, `tests/spec/test_phase_g.py` (`-k g04`)
- **Aufgabe:**
  1. Erweitere `Records` in `src/records.py` um `blueprints: list[str]`, `universes: list[str]`, `evil_selves: list[str]`, `badges: int = 0`, `best_rank: str = "Praktikantin"`, `endings: list[str]` und aktualisiere `discover(self, kind: str, key: str)` für `"block"`, `"blueprint"`, `"universe"`, `"evil_self"`, `"badge"`, `"ending"` und `"creature"` exakt nach `V23`.
  2. Implementiere `RANKS`, `compute_score(...)` und `rank_for_score(score)` in `src/records.py` sowie `PERK_ALIASES` und `resolve_perk_key(key)` in `src/perks.py`.
- **Akzeptanzkriterien:**
  - `records.discover("universe", "sporenklub")` trägt `"sporenklub"` in `records.universes` ein, ohne `records.creatures` oder `total_kills` zu verändern.
  - `rank_for_score(0) == "Praktikantin"` und `rank_for_score(1600) == "Realitäts-Rebellin"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g04 -q && uv run pytest --ignore=tests/spec -q`

---

## G05 — Entdeckungs-Archiv-Menü mit 5 Reitern (`"archive"`) in `src/menus.py` (`V22`, `V23`)

- **Größe:** S
- **Abhängigkeiten:** `G04`
- **Ziel-Dateien:** `src/menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`, `V23`), `src/menus.py`, `src/records.py`, `tests/spec/test_phase_g.py` (`-k g05`)
- **Aufgabe:**
  1. Implementiere den Platzhalter `draw_archive_menu(screen, font, small_font, records, tab_index)` in `src/menus.py`, sodass mit `[Tab]` oder `[Links]`/`[Rechts]` zwischen den 5 Reitern `"Zaubermodule"`, `"Baupläne"`, `"Kreaturen"`, `"Universen"` und `"Böse Ichs"` gewechselt werden kann und der Entdeckungsfortschritt (`entdeckt / gesamt`) sowie `records.best_rank` und `records.badges` angezeigt werden.
- **Akzeptanzkriterien:**
  - `draw_archive_menu` rendert für alle `tab_index in range(5)` fehlerfrei auf ein Offscreen-Surface und zeigt entdeckte Einträge aus `Records` im Klartext sowie unentdeckte als `"???"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g05 -q && uv run pytest --ignore=tests/spec -q`

---

## G06 — Sieges-/Todes-Endbildschirm mit Punktestand & Rang-Abrechnung (`src/menus.py`, `src/run.py`) (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `G04`, `F07`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/menus.py`, `src/run.py`, `tests/spec/test_phase_g.py` (`-k g06`)
- **Aufgabe:**
  1. Berechne auf `Run` (`src/run.py`) über `final_score(self) -> int` und `final_rank(self) -> str` den Endpunktestand mittels `compute_score` (`depth`, `kills`, `gold`, gesammelte Proben, gewonnene Challenges, besiegte Bosse, `victory`, `true_ending`) und aktualisiere bei Run-Ende `self.records.best_rank`.
  2. Zeige im Game-Over- und Victory-Overlay (`src/menus.py`) die Aufschlüsselung von `final_score()`, den erreichten Rang (`final_rank()`) bei `true_ending == True` den Sondertitel `"Wahres Ende: Realitäts-Rebellin"` und bei `run.ending == "boese"` den Titel `"Böses Ende: Die Hälfte des Multiversums"` an; trage das Ende mit `records.discover("ending", …)` ein (`"normal"`, `"wahr"` oder `"boese"`).
- **Akzeptanzkriterien:**
  - Ein gewonnener Run mit `true_ending=True` erreicht mindestens den Rang `"Erz-Klonologin"` bzw. `"Realitäts-Rebellin"` und aktualisiert `records.best_rank`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g06 -q && uv run pytest --ignore=tests/spec -q`

---

## G07 — Vollständige Save/Load-Serialisierung Teil 1: `Run`-, `Level`- & `Inventory`-Felder (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `E11`, `F10`, `G04`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/run.py` (Zeilen 580–740), `tests/spec/test_phase_g.py` (`-k g07`)
- **Aufgabe:**
  1. Erweitere `Run.save_state` und `Run.restore` in `src/run.py` um die Run- und Level-Felder aus `V23` (`gold`, `memory_shards`, `blueprint_shards`, `badges`, `price_factor`, `next_boost`, `in_workshop`, `in_headquarters`, `true_ending`, `plan`, `samples` in `Inventory`, `level_meta`), während `live["level"]` für Abwärtskompatibilität exakt die 5-Elemente-Liste bleibt.
- **Akzeptanzkriterien:**
  - `save_state()` gefolgt von `restore()` stellt `gold`, `samples`, `plan`, `in_workshop`, `level.regions`, `level.mid_boss_arena` und `level.boss_arena` exakt wieder her; alte Save-Payloads ohne `level_meta` laden weiterhin fehlerfrei.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g07 -q && uv run pytest --ignore=tests/spec -q`

---

## G08 — Vollständige Save/Load-Serialisierung Teil 2: `Wanted`, `Event`, `Challenge`, `Klonita`, `Creature` & Status-Timer (`V23`)

- **Größe:** S
- **Abhängigkeiten:** `G07`, `F01`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `src/run.py` (Zeilen 580–797), `tests/spec/test_phase_g.py` (`-k g08`)
- **Aufgabe:**
  1. Erweitere `Run.save_state` und `Run.restore` (`src/run.py`) um `wanted`, `grudges`, `event`, `challenge`, `klonita`, die 8 neuen `Player.body`-Status-Timer (`drunk`..`befogged`) sowie die erweiterten `Creature`-Felder (`state`, `aggro`, `group_id`, `generation`, `carrying`, `bribed`, `giver`) und reinitialisiere `self.boss_script = make_boss_script(boss)` nach dem Laden lebender Bosse.
- **Akzeptanzkriterien:**
  - Ein mitten in einem Event, einer Challenge und einem Bosskampf gespeicherter `Run` stellt nach `restore()` alle Teilzustände (`wanted.level`, `event.remaining`, `challenge.elapsed`, `klonita.state`, `creature.bribed`, `player.body.stamped_good`, `boss_script.phase`) verlustfrei wieder her.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g08 -q && uv run pytest --ignore=tests/spec -q`

---

## G09 — Tastatur- & Maus-Steuerung für alle neuen Werkstatt- und Begegnungs-Menüs in `src/game.py` / `src/run.py` (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `E14`, `F08`, `G05`, `G14`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/run.py`, `src/menus.py`, `tests/spec/test_phase_g.py` (`-k g09`)
- **Aufgabe:**
  1. Erweitere das in `G14` angelegte `Run.handle_menu_input(self, key: int) -> bool` (`src/run.py`; `"portal_select"` gibt es schon) auf alle 5 `menu_mode`-Zustände (`"portal_select"`, `"fabricator"`, `"trader"`, `"empress_bargain"`, `"archive"`): Navigation mit Pfeiltasten / `W`/`S`/`A`/`D`, Bestätigen mit `Enter`/`E`/`1`–`4`, Proben-Tausch mit `T`, Reroll mit `R`, Schließen mit `Escape`.
- **Akzeptanzkriterien:**
  - Jeder der 5 `menu_mode`-Zustände lässt sich im Test komplett per Tastendruck (`handle_menu_input`) bedienen und mit `pygame.K_ESCAPE` sauber auf `menu_mode == ""` schließen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g09 -q && uv run pytest --ignore=tests/spec -q`

---

## G10 — Bot-Vollabnahme über alle 6 MVP-Universen, Werkstatt & Hauptquartier (`V14`)

- **Größe:** S
- **Abhängigkeiten:** `D16`, `G08`, `G09`
- **Ziel-Dateien:** `src/bot.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V14`), `docs/plan/vertraege.md`, `tests/spec/test_phase_g.py` (`-k g10`)
- **Aufgabe:**
  1. Stelle in `src/bot.py` und `src/run.py` sicher, dass die abschließende End-to-End-Abnahme in `tests/spec/test_phase_g.py` (`-k g10`) vollständig durchläuft:
     - `run_bot(u_key, seed=42, max_seconds=20.0)` über alle 6 MVP-Universen in `UNIVERSES` (`errors == []`, `stuck_ratio < 0.75`).
     - Kompletter Zyklus aus Universum 1 → Werkstatt (Stationen, Fabrikator, Händler, Portalwahl) → Universum 2 → Save/Load-Roundtrip → Hauptquartier (`enter_headquarters` bis Sieg über `"ober_cloita"`).
- **Akzeptanzkriterien:**
  - `uv run pytest -q` und `uv run ruff check src tests tools` laufen ohne jeden Fehler über die gesamte Codebasis durch.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g10 -q && uv run pytest --ignore=tests/spec -q`

## G11 — Anzeigenamen & Beschreibungen der 24 Geschosse nach Bibel 06 (`src/spells.py`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/spells.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`), `docs/bibel/06-waffen-und-module.md` (Tabelle „Geschosse“), `tests/spec/test_phase_g.py` (`-k g11`)
- **Aufgabe:**
  1. Setze für jede Zeile der Tabelle „Geschosse“ in Bibel 06 bei `BLOCKS[<Bisher>]` `name_de` = Spalte „Name“ und `description_de` = Spalte „Beschreibung“. Schlüssel nicht ändern.
- **Akzeptanzkriterien:**
  - Für alle 24 Zeilen stimmen `name_de` und `description_de` exakt mit Bibel 06 überein; alle Schlüssel in `BLOCKS` sind unverändert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g11 -q && uv run pytest --ignore=tests/spec -q`

---

## G12 — Anzeigenamen & Beschreibungen der 22 Aufsätze nach Bibel 06 (`src/spells.py`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/spells.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`), `docs/bibel/06-waffen-und-module.md` (Tabelle „Aufsätze“), `tests/spec/test_phase_g.py` (`-k g12`)
- **Aufgabe:**
  1. Setze für jede Zeile der Tabelle „Aufsätze“ in Bibel 06 bei `BLOCKS[<Bisher>]` `name_de` = Spalte „Name“ und `description_de` = Spalte „Beschreibung“. Schlüssel nicht ändern.
- **Akzeptanzkriterien:**
  - Für alle 22 Zeilen stimmen `name_de` und `description_de` exakt mit Bibel 06 überein; alle Schlüssel in `BLOCKS` sind unverändert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g12 -q && uv run pytest --ignore=tests/spec -q`

---

## G13 — Anzeigenamen & Beschreibungen der 4 Zünder nach Bibel 06 (`src/spells.py`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A02`, `A27`
- **Ziel-Dateien:** `src/spells.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`), `docs/bibel/06-waffen-und-module.md` (Tabelle „Zünder“), `tests/spec/test_phase_g.py` (`-k g13`)
- **Aufgabe:**
  1. Setze für jede Zeile der Tabelle „Zünder“ in Bibel 06 bei `BLOCKS[<Bisher>]` `name_de` = Spalte „Name“ und `description_de` = Spalte „Beschreibung“ sowie für `sekret_feuer` / `sekret_rauch` die Namen „Feuerfüllung“ / „Rauchfüllung“ mit den Beschreibungen aus Bibel 06 „Füllungen“. Schlüssel nicht ändern.
- **Akzeptanzkriterien:**
  - Für alle 4 Zeilen stimmen `name_de` und `description_de` exakt mit Bibel 06 überein; alle Schlüssel in `BLOCKS` sind unverändert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g13 -q && uv run pytest --ignore=tests/spec -q`

---

## G14 — Neuer Lauf beginnt in der Werkstatt; Stationen per [E] und Portal-Menü per Tastatur (`src/run.py`) (`V18`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `E11`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (Stationen-Tabelle, „Betreten“), `src/run.py` nur `Controls`, `Run.new_run`, `Run._reset`, `Run.update` (Stelle mit `controls.pickup`), `Run.enter_workshop`, `Run.interact_station`, `Run.choose_next_universe` – die Datei ist sehr groß, gezielt suchen; `src/universes/plan.py`, `tests/spec/test_phase_g.py` (`-k g14`)
- **Aufgabe:**
  1. Neue Methode `Run.start_multiverse_run()`: `self._reset()`, `self.plan = RunPlan(self.seed)`, `self.portal_index = 0`, dann `self.enter_workshop()`. `new_run()` bleibt unverändert (Sandbox und alte Tests nutzen es).
  2. In `Run.update`: Ist `self.in_workshop` und `self.menu_mode == ""` und `controls.pickup` gesetzt, ruft `update` `self.interact_station()` auf (statt etwas aufzuheben).
  3. Neue Methode `Run.handle_menu_input(self, key: int) -> bool` – vorerst nur für `menu_mode == "portal_select"`: `K_UP`/`K_w` bzw. `K_DOWN`/`K_s` verschieben `self.portal_index` innerhalb von `self.plan.offers()` (umlaufend), `K_RETURN`/`K_e` ruft `self.choose_next_universe(self.portal_index)` auf und setzt `menu_mode = ""` und `portal_index = 0`, `K_ESCAPE` setzt nur `menu_mode = ""`. Rückgabe `True`, wenn die Taste verbraucht wurde; in jedem anderen `menu_mode` `False` (`G09` ergänzt die übrigen Menüs).
- **Akzeptanzkriterien:**
  - Nach `start_multiverse_run()` steht die Spielerin in der Werkstatt, `plan.slot == 0` und das Portal bietet 2 Universen an.
  - [E] am Portalrahmen öffnet `"portal_select"`; Escape schließt es; Pfeil runter + Enter reist in das zweite Angebot.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g14 -q && uv run pytest --ignore=tests/spec -q`

---

## G15 — Spielschleife verdrahten: Lauf startet in der Werkstatt, Portal-Menü sichtbar und bedienbar (`src/main.py`) (`V22`)

- **Größe:** S
- **Abhängigkeiten:** `G14`
- **Ziel-Dateien:** `src/main.py`
- **Zu lesender Kontext:** `src/main.py` nur `Game.__init__`, `_start_run`, `_on_key`, `update`, `draw` und `_key_name`; `src/menus.py` (`draw_portal_select_menu`), `src/ui.py` (`font`), `src/workshop.py` (`station_at`, `STATIONS`), `tests/spec/test_phase_g.py` (`-k g15`)
- **Aufgabe:**
  1. `_start_run`: Ohne Sandbox startet `self.run.start_multiverse_run()` statt `self.run.new_run()`; die Sandbox bleibt beim alten Ablauf.
  2. `_on_key`: Ist `self.run.menu_mode` gesetzt, geht die Taste zuerst an `self.run.handle_menu_input(key)`. Wurde sie nicht verbraucht und ist es `K_ESCAPE`, wird `menu_mode = ""` gesetzt. In beiden Fällen öffnet Escape **nicht** das Pausemenü. Danach `self._snap_camera()`, falls sich `self.run.in_workshop` geändert hat.
  3. `update`: Solange `self.run.menu_mode` gesetzt ist, läuft `self.run.update` nicht (das Spiel pausiert hinter dem Menü).
  4. `draw`: Bei `menu_mode == "portal_select"` `draw_portal_select_menu(self.screen, ui.font(...), ui.font(...), self.run.plan.offers(), self.run.portal_index)` über dem Spielbild. Bei einem anderen, noch nicht gebauten `menu_mode` einen Hinweis „Noch nicht verfügbar – [Esc]“.
  5. In der Werkstatt: Steht die Spielerin an einer Station (`station_at(self.run.workshop_layout, x, y)`), zeigt `self.notice` „[<Taste für pickup>] <name_de der Station>“.
- **Akzeptanzkriterien:**
  - Ein neuer Lauf aus dem Titelmenü beginnt in der Werkstatt; das Portal-Menü lässt sich im laufenden Spiel öffnen, mit Escape schließen und mit Enter bestätigen; danach steht die Spielerin im gewählten Universum.
- **Verifikation:** `uv run pytest tests/spec/test_phase_g.py -k g15 -q && uv run pytest --ignore=tests/spec -q`, danach einmal von Hand: `uv run python -m src.main`, „Neues Spiel“, zum Portalrahmen laufen, [E], Universum wählen.

