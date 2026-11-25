# Phase F — Behörde, Mehrphasige Bosse, Böse Ichs, Hauptquartier & Klonita (19 atomare S-Karten: `F01`–`F19`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_f.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Module folgen `V15`–`V17` aus [v15-behoerde-und-bosse.md](vertraege/v15-behoerde-und-bosse.md) und `V21`–`V22` aus [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md).

---

## F01 — Fahndungslevel `Wanted` & Agenten-Spawner (`src/authority.py`) (`V15`)

- **Größe:** S
- **Abhängigkeiten:** `C14`
- **Ziel-Dateien:** `src/authority.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `docs/bibel/02-systeme.md` („Fahndungsstufe“), `src/enemies.py`, `tests/spec/test_phase_f.py` (`-k f01`)
- **Aufgabe:**
  1. Implementiere `Wanted` (`stars`, `add`, `on_cells_destroyed`, `on_workshop`, `bribe_cost`, `agent_count`, `to_data`, `from_data`), `agent_species_for_stars(stars)` und `spawn_agents(run, count=None)` exakt nach `V15`.
- **Akzeptanzkriterien:**
  - `on_cells_destroyed(1000)` erhöht `level` um `0.5`; `on_workshop()` senkt um `0.5`, nie unter `0`.
  - `agent_species_for_stars` liefert für 1–5 Sterne die Listen aus `V15` (Vollstrecker erst ab 3, Abteilungsleiter erst ab 4).
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f01 -q && uv run pytest --ignore=tests/spec -q`

---

## F02 — Fahndungs-Vergehen, Agenten-Spawns & Akten-Schredder in `Run` (`V15`, `V18`)

- **Größe:** S
- **Abhängigkeiten:** `E10`, `F01`, `C16`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `src/authority.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f02`)
- **Aufgabe:**
  1. Binde `self.wanted = Wanted()` in `Run` ein und verknüpfe alle Auslöser aus der Tabelle in `V15` (zerstörte Zellen, getötete neutrale/passive Kreatur `+0.25`, Händler verletzt/getötet, Diebstahl, `FORBIDDEN_BLOCKS`). Jede Änderung feuert `self.emit("wanted_change", level=…, stars=…, reason=…)`.
  2. Spawne beim Betreten eines Universums `spawn_agents(self)`. Getötete Agenten lassen `AGENT_GOLD` fallen und mit `BADGE_CHANCE` einen Dienstausweis (`kind="badge"`). Am `"ws_shredder"` senkt `interact_station` gegen `bribe_cost()` Gold das Level um `1.0`.
- **Akzeptanzkriterien:**
  - 2000 zerstörte Zellen ergeben 1 Stern; das nächste Universum spawnt 1 `"agent_streife"`.
  - Eine getötete passive Kreatur erhöht `wanted.level` um `0.25`; der Schredder zieht `bribe_cost()` Gold ab.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f02 -q && uv run pytest --ignore=tests/spec -q`

---

## F03 — Mehrphasiges Boss-Framework (`src/bosses/__init__.py`) (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `C12`
- **Ziel-Dateien:** `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/enemies.py`, `tests/spec/test_phase_f.py` (`-k f03`)
- **Aufgabe:**
  1. Erstelle `src/bosses/__init__.py` mit `BossPhase`, `BossScript` (`update`, `phase_change`, `tick_phase`, `on_death`), der Arena-Gefahren-Hilfe `apply_arena_hazard(hazard: str, dt: float, boss: Creature, run: Run)` (alle 8 Schlüssel aus `ARENA_HAZARDS` in `V16`) und der Fabrikfunktion `make_boss_script(boss: Creature) -> BossScript | None` gemäß `V16`.
- **Akzeptanzkriterien:**
  - Sinkt `boss.body.hp / boss.body.max_hp` auf `<= 0.66` bzw. `<= 0.33`, wechselt `BossScript.phase` auf `1` bzw. `2`, setzt `invuln_timer = 1.0` und feuert `run.emit("boss_phase", ...)`.
  - Während `invuln_timer > 0` wird eingehender Schaden am Boss blockiert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f03 -q && uv run pytest --ignore=tests/spec -q`

---

## F04 — Boss-Skripte Paket 1: `weltenherz`, `dj_myzel` (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F03`
- **Ziel-Dateien:** `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f04`)
- **Aufgabe:**
  1. Implementiere in `src/bosses/__init__.py` die 3-Phasen-Boss-Skripte (`1.0`, `0.66`, `0.33`) für `"weltenherz"` und `"dj_myzel"` mit ihren deutschen Phasen-Ansagen, Summons und Arena-Gefahren aus `V16` und registriere sie in `make_boss_script`.
- **Akzeptanzkriterien:**
  - `make_boss_script` liefert für alle genannten Bosse eine `BossScript`-Instanz mit `len(script.phases) == 3`, die bei HP `60 %` und `30 %` die Phasen `1` und `2` inkl. Summons/Hazards auslöst.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f04 -q && uv run pytest --ignore=tests/spec -q`

---

## F05 — Boss-Skripte Paket 2: `oberstempler`, `abt_kieme` (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F04`
- **Ziel-Dateien:** `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f05`)
- **Aufgabe:**
  1. Implementiere in `src/bosses/__init__.py` die 3-Phasen-Boss-Skripte für `"oberstempler"` (Phase 3: Aktendeckel-Wände) und `"abt_kieme"` (Phase 2: schrittweise Flutung) gemäß `V16` und registriere sie in `make_boss_script`.
- **Akzeptanzkriterien:**
  - Beide Bosse durchlaufen im Test sauber ihre 3 Phasen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f05 -q && uv run pytest --ignore=tests/spec -q`

---

## F06 — Boss-Skripte Paket 3: `ameisenkoenigin`, `mutter_glibber` & `Run`-Anbindung (`V16`)

- **Größe:** S
- **Abhängigkeiten:** `F05`
- **Ziel-Dateien:** `src/bosses/__init__.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/bosses/__init__.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f06`)
- **Aufgabe:**
  1. Implementiere in `src/bosses/__init__.py` die 3-Phasen-Boss-Skripte für `"ameisenkoenigin"` und `"mutter_glibber"` und registriere sie in `make_boss_script`.
  2. Binde `self.boss_script: BossScript | None = None` in `Run` (`src/run.py`) ein: wird beim Spawn des Endbosses über `make_boss_script` erzeugt, in `Run.update` getickt und beim Tod des Bosses via `boss_script.on_death(self)` abgeschlossen.
- **Akzeptanzkriterien:**
  - Alle 6 MVP-Universums-Bosse aus `UNIVERSES` werden von `make_boss_script` unterstützt und in `Run.update` mehrphasig gesteuert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f06 -q && uv run pytest --ignore=tests/spec -q`

---

## F07 — Böse Ichs: Endgegner, Echos, Waffen & Kaiserin-Angebot (`src/bosses/evil_selves.py`) (`V16`, `V17` §1)

- **Größe:** S
- **Abhängigkeiten:** `F06`
- **Ziel-Dateien:** `src/bosses/evil_selves.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`, `V17` §1), `docs/bibel/05-gegner.md` („Böse Ichs“), `src/wand.py`, `src/universes/plan.py`, `tests/spec/test_phase_f.py` (`-k f07`)
- **Aufgabe:**
  1. Implementiere `final_evil_self`, `echo_for_depth`, `signature_wand_for_evil_self` und `apply_empress_bargain` nach `V17` §1.
  2. Ergänze in `src/bosses/__init__.py` das `EvilSelfBossScript` mit 4 Phasen (Endkampf) bzw. 2 Phasen (`echo=True` oder Hauptquartier), registriere es in `make_boss_script` und setze die Beute aus `V17` §1 in `on_death` um. Die Kaiserin ruft beim Eintritt in Phase 2 (Index 1) `run.menu_mode = "empress_bargain"` auf.
- **Akzeptanzkriterien:**
  - Echos erscheinen auf `depth` 3 und 5 und sind genau die beiden bösen Ichs, die nicht Endgegner sind.
  - `apply_empress_bargain(run, True)` beendet den Lauf mit `run.ending == "boese"`.
  - Das Skript hat im Endkampf 4 Phasen und als Echo 2 Phasen; ein Echo lässt `100` Gold und einen Dienstausweis fallen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f07 -q && uv run pytest --ignore=tests/spec -q`

---

## F08 — Echos im Geheimraum & Kaiserin-Angebot-Menü (`"empress_bargain"`) (`V17` §1, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `F07`, `G04`
- **Ziel-Dateien:** `src/run.py`, `src/menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17` §1), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/bosses/evil_selves.py`, `src/run.py`, `src/menus.py`, `tests/spec/test_phase_f.py` (`-k f08`)
- **Aufgabe:**
  1. Spawne in `Run._populate` das Echo `echo_for_depth(self, depth)` im `level.secret`-Raum (Leben `EVIL_HP × ECHO_HP_FACTOR`, Skript mit `echo=True`).
  2. Ergänze `draw_empress_bargain_menu(surface, font, small_font, selected_index)` („Die Hälfte des Multiversums“ / „Nein danke“) und `Run.resolve_empress_bargain(accepted)`, das `apply_empress_bargain` aufruft und `menu_mode` zurücksetzt. Ergänze dafür `Run.ending: str = ""` (`"normal"`, `"wahr"` oder `"boese"` am Laufende).
- **Akzeptanzkriterien:**
  - Auf `depth == 3` steht das erste Echo im Geheimraum; `resolve_empress_bargain(True)` beendet den Lauf mit dem bösen Ende, `False` setzt den Kampf fort.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f08 -q && uv run pytest --ignore=tests/spec -q`

---

## F09 — Hauptquartier: Rat, böse Ichs & Ober-Cloita (`src/bosses/headquarters.py`) (`V16`, `V17` §3)

- **Größe:** S
- **Abhängigkeiten:** `F07`, `C14`
- **Ziel-Dateien:** `src/bosses/headquarters.py`, `src/bosses/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`, `V17` §3), `docs/bibel/05-gegner.md` („Wahres Ende“), `src/bosses/__init__.py`, `tests/spec/test_phase_f.py` (`-k f09`)
- **Aufgabe:**
  1. Implementiere `can_enter_headquarters`, `generate_headquarters_arena` und `HeadquartersController` mit den 3 Stufen aus `V17` §3 (5 Räte mit Agentenwellen und Demaskierungs-Zeilen; die zwei übrigen bösen Ichs mit 2 Phasen; Ober-Cloita).
  2. Ergänze `OberCloitaBossScript` (3 Phasen, `OBER_CLOITA_HP`, Kopf-Splitter je 10 % Leben mit `+50` Flux, Klonitas 3-s-Umarmung zu Beginn von Phase 3) und registriere es in `make_boss_script`.
- **Akzeptanzkriterien:**
  - `can_enter_headquarters` ist `True` ab 6 Splittern, 3 Dienstausweisen oder 4 Sternen.
  - Stufe 1 hat 5 `"ratsmitglied"`; Stufe 2 die beiden bösen Ichs außer dem Endgegner; der Tod der Ober-Cloita setzt `run.true_ending = True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f09 -q && uv run pytest --ignore=tests/spec -q`

---

## F10 — Hauptquartier-Portal & wahres Ende in `src/run.py` (`V17` §2–3)

- **Größe:** S
- **Abhängigkeiten:** `F09`, `F19`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17` §2–3), `src/bosses/headquarters.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f10`)
- **Aufgabe:**
  1. Ergänze auf `Run` `in_headquarters`, `true_ending`, `hq_controller` und `enter_headquarters()` (volle Heilung, kein Werkstatt-Besuch, Arena aus `generate_headquarters_arena`, Stufe `"anhoerung"`).
  2. Nach dem Sieg im Endkampf (`F19`) spawnt bei erfüllter Bedingung das Portal `kind="portal"`, `item_key="headquarters"`; Betreten ruft `enter_headquarters()`.
- **Akzeptanzkriterien:**
  - `enter_headquarters()` heilt voll und startet Stufe `"anhoerung"`; der Sieg über alle 3 Stufen setzt `victory` und `true_ending`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f10 -q && uv run pytest --ignore=tests/spec -q`

---

## F11 — Klonita-Spruch-Datenbank (`src/klonita_lines.py`) (`V21` §4)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/klonita_lines.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21` §4), `docs/bibel/08-ui-und-texte.md` („Textmengen“, „Tonfall“), `tests/spec/test_phase_f.py` (`-k f11`)
- **Aufgabe:**
  1. Erstelle `src/klonita_lines.py` mit `LINES` für alle Themen aus `V21` §4 in der Anzahl aus Bibel 08 („Textmengen“) und `line_for(topic, rng)`; jeder Spruch höchstens 60 Zeichen, Ton nach Bibel 08.
- **Akzeptanzkriterien:**
  - Jedes Thema aus `V21` §4 hat mindestens die Anzahl Sprüche aus Bibel 08; kein Spruch ist länger als 60 Zeichen; unbekannte Themen fallen auf `"default"` zurück.
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
- **Abhängigkeiten:** `F12`, `A04`
- **Ziel-Dateien:** `src/klonita.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`), `src/klonita.py`, `tests/spec/test_phase_f.py` (`-k f13`)
- **Aufgabe:**
  1. Ergänze in `Klonita.update` (`src/klonita.py`) die 4 Hilfsaktionen mit ihren Cooldowns aus `V21`:
     - `"shield"` (`18 s`, löscht feindliches Projektil `< 28 px` vor der Spielerin)
     - `"snack"` (`45 s`, heilt `+15 HP` bei Spieler-HP `< 35 %`, nicht im Bosskampf)
     - `"spark"` (`4.5 s`, schießt `6.0`-Schaden-Hilfsfunken auf Feind `< 90 px`)
     - `"cleanse"` (`22 s`, löscht Feuer/Frost/`stamped_bad` auf der Spielerin)
  2. Ergänze `trigger_quirk(self, kind: str, run: Run) -> bool` für die 3 Macken (`"shiny_poke"`, `"loud_sneeze"`, `"sample_nibble"`), die pro Universum höchstens einmal ausgelöst werden (`quirk_used_in_universe = True`).
- **Akzeptanzkriterien:**
  - Jede der 4 Hilfsaktionen löst unter ihrer Bedingung aus und setzt ihren spezifischen Cooldown; der Snack heilt genau `15` Leben und löst im Bosskampf nicht aus.
  - `"sample_nibble"` entnimmt maximal `1` Probe bei `>= 5` Proben, gibt `+15` Gold und setzt `quirk_used_in_universe = True`, sodass im selben Universum keine zweite Macke auftritt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f13 -q && uv run pytest --ignore=tests/spec -q`

---

## F14 — Klonita & Sprechblasen (`SpeechBubble`, `Run.say`, `Run.boss_line`) in `Run` verdrahten (`V21`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `F06`, `F13`
- **Ziel-Dateien:** `src/hud.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21`, `V22`), `src/hud.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f14`)
- **Aufgabe:**
  1. Definiere `SpeechBubble` in `src/hud.py` gemäß `V22` und ergänze auf `Run` (`src/run.py`) `self.klonita = Klonita()`, `self.bubbles: list[SpeechBubble] = []`, `self.boss_banner: tuple[str, float] | None = None`, `say(self, speaker, text, x, y, ttl=3.0, color=(235, 225, 255))` (60 Zeichen, je Sprecher höchstens alle 8 s, `V22` §1) und `boss_line(self, text_de)`.
  2. Verknüpfe `self.klonita.update(dt, self)`, die Taste `[K]` (`klonita.toggle()`) und die 5 Auto-Trigger (`enter_universe`, `hurt_player` bei HP `< 25 %`, `boss_phase` bei `phase == 0`, `wanted_change` bei `stars >= 3`, `event_start`) in `Run` mit `self.say("Klonita", ...)`.
- **Akzeptanzkriterien:**
  - `run.say(...)` begrenzt `run.bubbles` auf maximal `3` gleichzeitige Blasen und baut deren `ttl` in `Run.update` ab.
  - Eintritt in ein Universum oder Sinken der Spieler-HP unter `25 %` erzeugt automatisch eine Klonita-Sprechblase in `run.bubbles`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f14 -q && uv run pytest --ignore=tests/spec -q`

## F15 — Beruhigen & Ausweichen: `Creature.calmed` / `dodge_charges` (`V21` 2b)

- **Größe:** S
- **Abhängigkeiten:** `A14`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21` Abschnitte 2b und 3), `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1a`), `src/enemies.py` (`evaluate_stance`), `tests/spec/test_phase_f.py` (`-k f15`)
- **Aufgabe:**
  1. Ergänze `Creature` (`src/enemies.py`) um `calmed: float = 0.0` (zählt in `update` auf `0` herunter) und `dodge_charges: int = 0`.
  2. Lass `evaluate_stance` (`src/enemies.py`) Kreaturen mit `territorial`/`neutral` und `calmed > 0` nicht durch Nähe aggressiv werden; `was_hit` und Gruppen-Aggro wirken weiter.
- **Akzeptanzkriterien:**
  - Eine `territorial`-Kreatur direkt neben der Spielerin bleibt mit `calmed > 0` bei `"idle"` und wird nach einem Treffer trotzdem aggressiv.
  - `Creature.update` senkt `calmed` um `dt` bis auf `0`; `dodge_charges` startet bei `0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f15 -q && uv run pytest --ignore=tests/spec -q`

---

## F16 — Klonitas Bibel-Aktionen Zeigen, Tragen, Umarmen (`src/klonita.py` Teil 3) (`V21` 2b)

- **Größe:** S
- **Abhängigkeiten:** `F13`, `F15`
- **Ziel-Dateien:** `src/klonita.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21` Abschnitte 2b und 3), `src/klonita.py`, `src/loot.py` (`Pickup`), `tests/spec/test_phase_f.py` (`-k f16`)
- **Aufgabe:**
  1. Implementiere `helper_point`, `helper_carry` und `helper_hug` laut Tabelle 2b mit den Cooldowns `"point"` (`60 s`) und `"carry"` (`30 s`) und rufe sie in `Klonita.update` auf (nicht bei `"dismissed"`/`"knocked"`). Ergänze `to_data`/`from_data` um `pointing` und `point_timer`.
- **Akzeptanzkriterien:**
  - `helper_point` findet eine Lebenskapsel in `240 px` und setzt `pointing` sowie den Cooldown `60.0`; ein zweiter Aufruf liefert `None`.
  - `helper_carry` holt einen hoch liegenden Pickup zur Spielerin; `helper_hug` setzt `calmed` bei einer neutralen Kreatur in `80 px`, nicht bei einer feindlichen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f16 -q && uv run pytest --ignore=tests/spec -q`

---

## F17 — Klonitas Bibel-Macken Trinkgeld, Füttern, Warnung (`src/klonita.py` Teil 4) (`V21` 3)

- **Größe:** S
- **Abhängigkeiten:** `F16`, `E13`
- **Ziel-Dateien:** `src/klonita.py`, `src/projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V21` Abschnitte 2b und 3), `src/klonita.py`, `src/projectiles.py` (Treffer auf Kreaturen), `tests/spec/test_phase_f.py` (`-k f17`)
- **Aufgabe:**
  1. Erweitere `trigger_quirk` um `"tip_trader"`, `"feed_creature"` und `"warn_enemy"` laut Tabelle 3 und die automatische Prüfung in `update` (`QUIRK_CHANCE_PER_S`). Ergänze in `src/projectiles.py`: trifft ein Geschoss der Spielerin eine Kreatur mit `dodge_charges > 0`, verbraucht es eine Ladung statt Schaden zu machen.
- **Akzeptanzkriterien:**
  - Jede der 3 Macken wirkt wie in Tabelle 3; alle 6 Macken zusammen lösen höchstens einmal je Universum aus.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f17 -q && uv run pytest --ignore=tests/spec -q`

---

## F18 — Heimatwelten der bösen Ichs (`src/universes/gen/evil_homes.py`, `src/materials.py`) (`V17` §2)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D17`
- **Ziel-Dateien:** `src/universes/gen/evil_homes.py`, `src/materials.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17` §2), `docs/bibel/05-gegner.md` („Böse Ichs“), `src/universes/gen/common.py`, `src/materials.py`, `tests/spec/test_phase_f.py` (`-k f18`)
- **Aufgabe:**
  1. Lege die Materialsätze `"boese_kaiserin"` (`"goldboden"`), `"boese_gute"` (`"lichtstein"`, `"heiliges_licht"`) und `"boese_omega"` (`"foerderband"`, `"stahl"`) mit den Eigenschaften aus `V17` §2 an.
  2. Implementiere `generate_evil_home(world, species, seed)`: `1280×720`-Arena je böses Ich (Thronsaal, Kathedrale, Fabrikhalle mit 4 Pressen-Positionen in `level.destructible_props`), `level.universe_key = species`.
- **Akzeptanzkriterien:**
  - Jede Heimatwelt ist `1280×720`, nutzt ihren eigenen Materialsatz und hat Luft am Spawn und in der Arena-Mitte.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f18 -q && uv run pytest --ignore=tests/spec -q`

---

## F19 — Endkampf in `Run`: Portal zur Heimatwelt, Arena-Mechaniken & Sieg (`V17` §2)

- **Größe:** S
- **Abhängigkeiten:** `F07`, `F18`, `E11`, `D10`
- **Ziel-Dateien:** `src/run.py`, `src/bosses/evil_selves.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V17` §2), `src/universes/plan.py`, `src/run.py`, `tests/spec/test_phase_f.py` (`-k f19`)
- **Aufgabe:**
  1. Ergänze `Run.enter_final()`: Materialsatz aktivieren, `generate_evil_home`, Endgegner `final_evil_self(self)` mit `EVIL_HP` und 4-Phasen-Skript spawnen. Ist `self.plan.finished`, bietet `choose_next_universe` nur noch diesen Weg.
  2. Setze die Arena-Mechaniken aus `V17` §2 in `Run.update` um (Rutschen auf `"goldboden"`, Schaden durch `"heiliges_licht"`, Förderbänder, Pressen, Thron-Kanone) und beende den Kampf mit `victory = True` (Hauptquartier-Portal siehe `F10`).
- **Akzeptanzkriterien:**
  - Nach 6 Universen führt `choose_next_universe(0)` in die Heimatwelt von `run.plan.evil_self`; der Tod des bösen Ichs setzt `run.victory = True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_f.py -k f19 -q && uv run pytest --ignore=tests/spec -q`

---
