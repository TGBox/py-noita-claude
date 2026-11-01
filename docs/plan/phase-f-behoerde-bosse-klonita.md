# Phase F — Behörde, Mehrphasige Bosse, Böse Ichs, Hauptquartier & Klonita (14 atomare S-Karten: `F01`–`F14`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_f.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Module folgen `V15`–`V17` aus [v15-behoerde-und-bosse.md](vertraege/v15-behoerde-und-bosse.md) und `V21`–`V22` aus [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md).

---

## F01 — Fahndungslevel `Wanted` & Agenten-Spawner (`src/authority.py`) (`V15`)

- **Größe:** S
- **Abhängigkeiten:** `C14`
- **Ziel-Dateien:** `src/authority.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `src/enemies.py`, `tests/spec/test_phase_f.py` (`-k f01`)
- **Aufgabe:**
  1. Erstelle `src/authority.py` mit `WANTED_MAX = 5.0`, `AGENT_TYPES`, `Wanted` (`stars`, `add`, `on_cells_destroyed`, `on_workshop`, `bribe_cost`, `agent_count`, `to_data`, `from_data`), `agent_species_for_stars(stars)` und `spawn_agents(run, count=None)` exakt nach `V15`.
- **Akzeptanzkriterien:**
  - `Wanted.on_cells_destroyed(1000)` erhöht `level` um `+0.5` (`"Sachbeschädigung"`).
  - `Wanted.on_workshop()` senkt `level` um `-0.5` (geklemmt auf `>= 0.0`).
  - `agent_species_for_stars(1..5)` liefert genau `1, 2, 3, 4, 6` Agenten-Spezies gemäß `V15`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f01 -q && uv run pytest --ignore=tests/spec -q`

---

## F02 — Fahndungs-Vergehen, Agenten-Spawns & Akten-Schredder (`ws_shredder`) in `Run` (`V15`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `E10`, `F01`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `src/authority.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f02`)
- **Aufgabe:**
  1. Binde `self.wanted = Wanted()` in `Run` (`src/run.py`) ein:
     - Verknüpfe die Events `"cells_destroyed"`, `"trader_hurt"` (`+1.5`), `"trader_killed"` (`+3.0`), `"steal"` (`+1.0`) sowie das Wirken verbotener Zauberblöcke (`"nuke"`, `"black_hole"`, `"omega"` → `+0.5` `"Verbotene Magie"`) mit `self.wanted` und feuere bei Änderung `self.emit("wanted_change", level=self.wanted.level, stars=self.wanted.stars, reason=...)`.
     - Spawne beim Eintritt in ein Universum `spawn_agents(self)` (außer wenn `player.body.stamped_good > 0`).
     - In `enter_workshop()` wird `self.wanted.on_workshop()` aufgerufen; an der Station `"ws_shredder"` senkt `interact_station` gegen `self.wanted.bribe_cost()` Gold das Fahndungslevel um `-1.0`.
- **Akzeptanzkriterien:**
  - Zerstören von 2000 Zellen erhöht `run.wanted.stars` auf `1`; Betreten des nächsten Universums spawnt `1` `"agent_sachbearbeiter"`.
  - Bezahlen am `"ws_shredder"` zieht `bribe_cost()` Gold ab und senkt `wanted.level` um `1.0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f02 -q && uv run pytest --ignore=tests/spec -q`

---

## F03 — Mehrphasiges Boss-Framework (`src/bosses/__init__.py`) (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `C13`
- **Ziel-Dateien:** `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/enemies.py`, `tests/spec/test_phase_f.py` (`-k f03`)
- **Aufgabe:**
  1. Erstelle `src/bosses/__init__.py` mit `BossPhase`, `BossScript` (`update`, `phase_change`, `tick_phase`, `on_death`), der Arena-Gefahren-Hilfe `apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run)` (`"acid_rain"`, `"steam_vents"`, `"stamp_barrage"`, `"frost_floor"`, `"electric_arcs"`, `"jelly_bounce"`) und der Fabrikfunktion `make_boss_script(boss: Creature) -> BossScript | None` gemäß `V16`.
- **Akzeptanzkriterien:**
  - Sinkt `boss.body.hp / boss.body.max_hp` auf `<= 0.66` bzw. `<= 0.33`, wechselt `BossScript.phase` auf `1` bzw. `2`, setzt `invuln_timer = 1.0` und feuert `run.emit("boss_phase", ...)`.
  - Während `invuln_timer > 0` wird eingehender Schaden am Boss blockiert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f03 -q && uv run pytest --ignore=tests/spec -q`

---

## F04 — Boss-Skripte Paket 1: `schrottpresse`, `muttermyzel`, `pfuetzenkoenig` (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F03`
- **Ziel-Dateien:** `src/bosses/schrott.py`, `src/bosses/myzel.py`, `src/bosses/magen.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f04`)
- **Aufgabe:**
  1. Implementiere die 3-Phasen-Boss-Skripte (`1.0`, `0.66`, `0.33`) in `src/bosses/schrott.py` (`"schrottpresse"`), `src/bosses/myzel.py` (`"muttermyzel"`) und `src/bosses/magen.py` (`"pfuetzenkoenig"`) mit ihren deutschen Phasen-Ansagen, Summons und Arena-Gefahren aus `V16` und registriere sie in `make_boss_script`.
- **Akzeptanzkriterien:**
  - `make_boss_script` liefert für alle 3 Bosse eine `BossScript`-Instanz mit `len(script.phases) == 3`, die bei HP `60 %` und `30 %` die Phasen `1` und `2` inkl. Summons/Hazards auslöst.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f04 -q && uv run pytest --ignore=tests/spec -q`

---

## F05 — Boss-Skripte Paket 2: `oberamtsrat`, `hochzeitstorte`, `abt_nautilus` (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F04`
- **Ziel-Dateien:** `src/bosses/amt.py`, `src/bosses/kuchen.py`, `src/bosses/abtei.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f05`)
- **Aufgabe:**
  1. Implementiere die 3-Phasen-Boss-Skripte in `src/bosses/amt.py` (`"oberamtsrat"`), `src/bosses/kuchen.py` (`"hochzeitstorte"`, zerstört bei Phase 1 und 2 jeweils die oberste Torten-Etage über `ProcRig.destroy_part`) und `src/bosses/abtei.py` (`"abt_nautilus"`) gemäß `V16` und registriere sie in `make_boss_script`.
- **Akzeptanzkriterien:**
  - Alle 3 Bosse durchlaufen im Test sauber ihre 3 Phasen; `"hochzeitstorte"` ruft beim Phasenwechsel `destroy_part` für die Torten-Etagen auf.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f05 -q && uv run pytest --ignore=tests/spec -q`

---

## F06 — Boss-Skripte Paket 3: `koenigin_mandibula`, `transformator`, `zirkusdirektor` & `Run`-Anbindung (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F05`
- **Ziel-Dateien:** `src/bosses/ameisen.py`, `src/bosses/spule.py`, `src/bosses/glibber.py`, `src/bosses/__init__.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f06`)
- **Aufgabe:**
  1. Implementiere die 3-Phasen-Boss-Skripte in `src/bosses/ameisen.py` (`"koenigin_mandibula"`), `src/bosses/spule.py` (`"transformator"`) und `src/bosses/glibber.py` (`"zirkusdirektor"`) und registriere sie in `make_boss_script`.
  2. Binde `self.boss_script: BossScript | None = None` in `Run` (`src/run.py`) ein: wird beim Spawn des Endbosses über `make_boss_script` erzeugt, in `Run.update` getickt und beim Tod des Bosses via `boss_script.on_death(self)` abgeschlossen.
- **Akzeptanzkriterien:**
  - Alle 9 Universums-Endbosse werden von `make_boss_script` unterstützt und in `Run.update` mehrphasig gesteuert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f06 -q && uv run pytest --ignore=tests/spec -q`

---

## F07 — Die 3 Bösen Ichs & Kaiserin-Handel (`src/bosses/evil_selves.py`) (`V17`)

- **Größe:** S
- **Abhängigkeiten:** `F06`
- **Ziel-Dateien:** `src/bosses/evil_selves.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `src/spells.py`, `tests/spec/test_phase_f.py` (`-k f07`)
- **Aufgabe:**
  1. Erstelle `src/bosses/evil_selves.py` mit `EVIL_SELVES = ("boese_kaiserin", "boese_gute", "boese_omega")`, `evil_self_for_depth(depth)`, `signature_wand_for_evil_self(species)`, `apply_empress_bargain(run, accepted)` und dem 3-Phasen-`EvilSelfBossScript` (inkl. Drop von Signatur-Stab, `"badge"` und `"memory_shard"` in `on_death` sowie `run.records.discover("evil_self", species)`) gemäß `V17`.
- **Akzeptanzkriterien:**
  - `evil_self_for_depth` liefert für `depth` `2, 3, 4` die 3 Bösen Ichs.
  - `apply_empress_bargain(run, True)` spawnt das `"Kaiserliches Zepter"`, gibt `+100` Gold, erhöht `wanted` um `+2.0` und reduziert `player.body.max_hp` um `20 %`.
  - Tod eines Bösen Ichs dropt den Signatur-Stab, `1` `"badge"` und `1` `"memory_shard"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f07 -q && uv run pytest --ignore=tests/spec -q`

---

## F08 — Böse-Ichs-Begegnung im Geheimraum & Kaiserin-Handel-Menü (`"empress_bargain"`) (`V17`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `F07`
- **Ziel-Dateien:** `src/run.py`, `src/menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/bosses/evil_selves.py`, `src/run.py`, `src/menus.py`, `tests/spec/test_phase_f.py` (`-k f08`)
- **Aufgabe:**
  1. Spawne in `Run._populate` (`src/run.py`) auf `depth in (2, 3, 4)` das jeweilige Böse Ich (`evil_self_for_depth(self.depth)`) im `level.secret`-Raum (`stance="territorial"` für `"boese_kaiserin"`, bis der Handel entschieden ist).
  2. Öffne bei Annäherung (`< 48 px`) oder `[E]` an eine noch nicht feindliche `"boese_kaiserin"` `self.menu_mode = "empress_bargain"` und ergänze `draw_empress_bargain_menu` in `src/menus.py` sowie `resolve_empress_bargain(self, accepted: bool)` auf `Run`.
- **Akzeptanzkriterien:**
  - Auf `depth == 2` steht `"boese_kaiserin"` im Geheimraum; `resolve_empress_bargain(False)` macht sie feindlich, `resolve_empress_bargain(True)` entfernt sie friedlich gegen den Pakt aus `V17`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f08 -q && uv run pytest --ignore=tests/spec -q`

---

## F09 — Hauptquartier der Behörde & 4-Phasen-Boss `"ober_cloita"` (`src/bosses/headquarters.py`) (`V17`)

- **Größe:** S
- **Abhängigkeiten:** `F07`
- **Ziel-Dateien:** `src/bosses/headquarters.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f09`)
- **Aufgabe:**
  1. Erstelle `src/bosses/headquarters.py` mit `HQ_STAGES = ("anhoerung", "boese_ichs", "ober_cloita")`, `can_enter_headquarters(run: Run) -> bool` (`run.badges >= 3 or run.wanted.stars >= 4`), `generate_headquarters_arena(world: World) -> tuple[int, int]`, `OberCloitaBossScript` (4 Phasen bei `1.0`, `0.75`, `0.50`, `0.25` gemäß `V16`/`V17`) und der Stufen-Steuerung `HeadquartersController` (`stage_index`, `spawn_stage`, `update`).
- **Akzeptanzkriterien:**
  - `can_enter_headquarters` ist `True` ab `3` Dienstmarken oder `4` Fahndungssternen.
  - `HeadquartersController` schaltet nach dem Besiegen aller Gegner einer Stufe automatisch von `"anhoerung"` auf `"boese_ichs"` und schließlich auf `"ober_cloita"` weiter; Tod von `"ober_cloita"` setzt `run.victory = True` und `run.true_ending = True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f09 -q && uv run pytest --ignore=tests/spec -q`

---

## F10 — Hauptquartier-Portal & Wahres Ende in `src/run.py` (`V17`)

- **Größe:** S
- **Abhängigkeiten:** `F09`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17`), `src/bosses/headquarters.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f10`)
- **Aufgabe:**
  1. Ergänze auf `Run` (`src/run.py`) `self.in_headquarters: bool = False`, `self.true_ending: bool = False`, `self.hq_controller: HeadquartersController | None = None` und `enter_headquarters(self) -> None`.
  2. Wenn auf `depth == 5` der Endboss stirbt und `can_enter_headquarters(self)` erfüllt ist, spawne neben dem normalen Ausgang ein zweites Pickup/Portal (`kind="portal"`, `item_key="headquarters"`), dessen Betreten `self.enter_headquarters()` auslöst.
- **Akzeptanzkriterien:**
  - `run.enter_headquarters()` startet Stufe `"anhoerung"`; das Durchspielen aller 3 Stufen endet mit `run.victory == True` und `run.true_ending == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f10 -q && uv run pytest --ignore=tests/spec -q`

---

## F11 — Klonita-Kommentar-Datenbank (`src/klonita_lines.py`) (`V21`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/klonita_lines.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`), `docs/bibel/03-klonita-und-ton.md`, `tests/spec/test_phase_f.py` (`-k f11`)
- **Aufgabe:**
  1. Erstelle `src/klonita_lines.py` mit `LINES: dict[str, tuple[str, ...]]` (mindestens je 4 trockene, deutsche Sätze für alle 9 Universums-Eintritte `"enter_schrott"`..`"enter_glibber"`, `"player_low_hp"`, `"boss_spawn"`, `"wanted_high"`, `"event_start"`, `"couch"`, `"memory_shard"`, `"assist_shield"`, `"assist_snack"`, `"quirk"`, `"default"`) und `line_for(topic: str, rng: random.Random) -> str`.
- **Akzeptanzkriterien:**
  - Alle 15 Pflicht-Themen aus `V21` sind in `LINES` mit mindestens 4 nicht-leeren deutschen Strings vertreten; `line_for` fällt bei unbekanntem Thema deterministisch auf `"default"` zurück.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f11 -q && uv run pytest --ignore=tests/spec -q`

---

## F12 — Klonita-Zustandsmaschine, Bewegung & 5 Auto-Trigger (`src/klonita.py` Teil 1) (`V21`)

- **Größe:** S
- **Abhängigkeiten:** `F11`
- **Ziel-Dateien:** `src/klonita.py`, `src/keybinds.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`), `src/keybinds.py`, `tests/spec/test_phase_f.py` (`-k f12`)
- **Aufgabe:**
  1. Ergänze in `src/keybinds.py` die Aktion `"klonita"` mit Standardtaste `pygame.K_k`.
  2. Erstelle `src/klonita.py` mit `KLONITA_STATES`, `AUTO_TRIGGERS` und `Klonita` (`toggle`, `on_trigger`, `take_damage` mit `5.0 s` `"knocked"` statt Tod, `to_data`, `from_data` sowie der Schwebe-/Folge-Bewegung und dem Teleport bei Distanz `> 220 px` in `update`).
- **Akzeptanzkriterien:**
  - `klonita.take_damage(999)` tötet Klonita nicht, sondern setzt `state == "knocked"` und `knocked_timer == 5.0`; nach `update(5.1, run)` ist `state == "follow"` und `hp == max_hp`.
  - `klonita.toggle()` schaltet zwischen `"follow"` und `"dismissed"` um; jeder der 5 `AUTO_TRIGGERS` holt sie in `"follow"` zurück und liefert einen Spruch.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f12 -q && uv run pytest --ignore=tests/spec -q`

---

## F13 — Klonitas 4 Hilfsaktionen & 3 Einmal-pro-Universum-Macken (`src/klonita.py` Teil 2) (`V21`)

- **Größe:** S
- **Abhängigkeiten:** `F12`
- **Ziel-Dateien:** `src/klonita.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`), `src/klonita.py`, `tests/spec/test_phase_f.py` (`-k f13`)
- **Aufgabe:**
  1. Ergänze in `Klonita.update` (`src/klonita.py`) die 4 Hilfsaktionen mit ihren Cooldowns aus `V21`:
     - `"shield"` (`18 s`, löscht feindliches Projektil `< 28 px` vor der Spielerin)
     - `"snack"` (`35 s`, heilt `+12 HP` bei Spieler-HP `< 35 %`)
     - `"spark"` (`4.5 s`, schießt `6.0`-Schaden-Hilfsfunken auf Feind `< 90 px`)
     - `"cleanse"` (`22 s`, löscht Feuer/Frost/`stamped_bad` auf der Spielerin)
  2. Ergänze `trigger_quirk(self, kind: str, run: Run) -> bool` für die 3 Macken (`"shiny_poke"`, `"loud_sneeze"`, `"sample_nibble"`), die pro Universum höchstens einmal ausgelöst werden (`quirk_used_in_universe = True`).
- **Akzeptanzkriterien:**
  - Jede der 4 Hilfsaktionen löst unter ihrer Bedingung aus und setzt ihren spezifischen Cooldown.
  - `"sample_nibble"` entnimmt maximal `1` Probe bei `>= 5` Proben, gibt `+15` Gold und setzt `quirk_used_in_universe = True`, sodass im selben Universum keine zweite Macke auftritt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f13 -q && uv run pytest --ignore=tests/spec -q`

---

## F14 — Klonita & Sprechblasen (`SpeechBubble`, `Run.say`, `Run.boss_line`) in `Run` verdrahten (`V21`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `F06`, `F13`
- **Ziel-Dateien:** `src/hud.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`, `V22`), `src/hud.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f14`)
- **Aufgabe:**
  1. Definiere `SpeechBubble` in `src/hud.py` gemäß `V22` und ergänze auf `Run` (`src/run.py`) `self.klonita = Klonita()`, `self.bubbles: list[SpeechBubble] = []`, `self.boss_banner: tuple[str, float] | None = None`, `say(self, speaker, text, x, y, ttl=3.2, color=(235, 225, 255))` und `boss_line(self, text_de)`.
  2. Verknüpfe `self.klonita.update(dt, self)`, die Taste `[K]` (`klonita.toggle()`) und die 5 Auto-Trigger (`enter_universe`, `hurt_player` bei HP `< 25 %`, `boss_phase` bei `phase == 0`, `wanted_change` bei `stars >= 3`, `event_start`) in `Run` mit `self.say("Klonita", ...)`.
- **Akzeptanzkriterien:**
  - `run.say(...)` begrenzt `run.bubbles` auf maximal `3` gleichzeitige Blasen und baut deren `ttl` in `Run.update` ab.
  - Eintritt in ein Universum oder Sinken der Spieler-HP unter `25 %` erzeugt automatisch eine Klonita-Sprechblase in `run.bubbles`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f14 -q && uv run pytest --ignore=tests/spec -q`
