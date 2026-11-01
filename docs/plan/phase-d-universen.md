# Phase D — Universums-Generatoren, Ereignisse, Prüfungen & Playtest-Bot (16 atomare S-Karten: `D01`–`D16`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_d.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Generatoren und Systeme folgen `V9`, `V10`, `V13`, `V14` aus [v09-universen-und-ereignisse.md](vertraege/v09-universen-und-ereignisse.md).

---

## D01 — Generator MVP-Universum 1: Die Fleischwelt (`src/universes/gen/magen.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`
- **Ziel-Dateien:** `src/universes/gen/magen.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`fleischwelt`), `tests/spec/test_phase_d.py` (`-k d01`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/magen.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="concentric"`, Regionen `"schlund"`, `"zotten"`, `"pfuetze"`) mit organischen Fleisch-/Knochen-Kammern (`"flesh"`, `"bone"`), Magensäure-Seen (`"acid"`) im Zentrum `"pfuetze"` und Props (`"saeure_behaelter"`, `"magen_zotte"`).
  2. Registriere `"fleischwelt": generate` (sowie Alias `"magen": generate`) in `GENERATORS` (`src/universes/gen/__init__.py`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["fleischwelt"], 1, 42)` liefert ein `Level` mit `[r[0] for r in level.regions] == ["schlund", "zotten", "pfuetze"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d01 -q && uv run pytest --ignore=tests/spec -q`

---

## D02 — Generator MVP-Universum 2: Die Große Aktenhalde (`src/universes/gen/amt.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/amt.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`aktenhalde`), `tests/spec/test_phase_d.py` (`-k d02`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/amt.py` (`topology="horizontal"`, Regionen `"wartezone"`, `"registratur"`, `"chefbueros"`) mit rechtwinkligen Büro-Etagen aus Ziegel/Stein/Papier (`"brick"`, `"paper"`), Treppenhäusern und Props (`"akten_regal"`, `"amt_uhr"`) und registriere `"aktenhalde"` (sowie Alias `"amt"`) in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["wartezone", "registratur", "chefbueros"]` in horizontaler Links-nach-Rechts-Abfolge und gültigen Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d02 -q && uv run pytest --ignore=tests/spec -q`

---

## D03 — Generator MVP-Universum 3: Glibbria (`src/universes/gen/glibber.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/glibber.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`glibbria`), `tests/spec/test_phase_d.py` (`-k d03`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/glibber.py` (`topology="islands"`, Regionen `"zelt"`, `"backstage"`, `"manege"` gemäß `V9`) mit schwebenden Gelee-/Zucker-Inseln (`"jelly"`, `"sugar"`, `"cloth"`), Trampolin-Mulden und Props (`"glibber_ballon"`) und registriere `"glibbria"` (sowie Alias `"glibber"`) in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["zelt", "backstage", "manege"]` und freie `spawn`/`exit_point`-Zellen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d03 -q && uv run pytest --ignore=tests/spec -q`

---

## D04 — Generator MVP-Universum 4: Das Krümel-Reich (`src/universes/gen/ameisen.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/ameisen.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`kruemelreich`), `tests/spec/test_phase_d.py` (`-k d04`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/ameisen.py` (`topology="top_split"`, Regionen `"oberbau"`, `"gaenge"`, `"thronsaal"` gemäß `V9`): `"oberbau"` oben, `"gaenge"` unten links, `"thronsaal"` unten rechts, verbunden über verzweigte Erd-/Harz-/Teig-Tunnel (`"dirt"`, `"sand"`, `"resin"`, `"dough"`, `"honey"`) und Props (`"ameisen_kokon"`) und registriere `"kruemelreich"` (sowie Alias `"ameisen"`) in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["oberbau", "gaenge", "thronsaal"]` mit `top_split`-Aufteilung und gültigen Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d04 -q && uv run pytest --ignore=tests/spec -q`

---

## D05 — Generator MVP-Universum 5: Der Sporen-Klub (`src/universes/gen/myzel.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/myzel.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`sporenklub`), `tests/spec/test_phase_d.py` (`-k d05`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/myzel.py` (`topology="vertical"`, Regionen `"kappenwald"`, `"sporennebel"`, `"wurzelherz"`) mit riesigen Pilzhut-Terrassen (`"fungus"`), Sporen-Taschen (`"spore"`), Schleim-Becken (`"slime"`) und Props (`"sporen_knolle"`, `"pilz_laterne"`) und registriere `"sporenklub"` (sowie Alias `"myzel"`) in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["kappenwald", "sporennebel", "wurzelherz"]`, `spawn` und `exit_point` liegen in Luftzellen, und alle Arenen sind innerhalb der Weltgrenzen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d05 -q && uv run pytest --ignore=tests/spec -q`

---

## D06 — Generator MVP-Universum 6: Die Versunkene Abtei (`src/universes/gen/abtei.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/abtei.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`abtei`), `tests/spec/test_phase_d.py` (`-k d06`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/abtei.py` (`topology="vertical"`, Regionen `"schiff"`, `"kreuzgang"`, `"krypta"`) mit gotischen Gewölbebögen (`"stone"`, `"brick"`, `"glass"`), gefluteten Wasserbecken (`"water"` mit Luftglocken zum Atmen) und Props (`"abtei_glocke"`) und registriere `"abtei"` in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["schiff", "kreuzgang", "krypta"]`, reichlich `"water"`-Zellen mit erreichbaren Lufttaschen und gültigen Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d06 -q && uv run pytest --ignore=tests/spec -q`

---

## D07 — Generator Pool-Universum 1: Der Große Schrott (`src/universes/gen/schrott.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/schrott.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`schrott`), `tests/spec/test_phase_d.py` (`-k d07`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/schrott.py` (`topology="vertical"`, Regionen `"halde"`, `"schmelze"`, `"kernwerk"`) mit Schrott-Plattformen, Öl-/Säure-Wannen, Lava-/Dampfkesseln und Props (`"explosionsfass"`, `"schrott_ventil"`) und registriere `"schrott"` in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["halde", "schmelze", "kernwerk"]` und alle Pflicht-Rechtecke aus `V9` sind belegt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d07 -q && uv run pytest --ignore=tests/spec -q`

---

## D08 — Generator Pool-Universum 2: Die Kuchenkruste (`src/universes/gen/kuchen.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/kuchen.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`kuchen`), `tests/spec/test_phase_d.py` (`-k d08`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/kuchen.py` (`topology="vertical"`, Regionen `"glasur"`, `"biskuit"`, `"boden"`) mit Zuckerguss-Brücken (`"sugar"`, `"icing"`), fluffigen Teig-Kavernen (`"dough"`), Milch-/Honig-Mulden (`"milk"`, `"honey"`) und Props (`"kuchen_kerze"`) und registriere `"kuchen"` in `GENERATORS`.
- **Akzeptanzkriterien:**
  - `[r[0] for r in level.regions] == ["glasur", "biskuit", "boden"]` und alle Pflicht-Rechtecke aus `V9` sind belegt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d08 -q && uv run pytest --ignore=tests/spec -q`

---

## D09 — Generator Pool-Universum 3: Die Summende Spule (`src/universes/gen/spule.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`
- **Ziel-Dateien:** `src/universes/gen/spule.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/universes/gen/common.py`, `src/universes/catalog.py` (`spule`), `tests/spec/test_phase_d.py` (`-k d09`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/spule.py` (`topology="columns"`, Regionen `"spulenwald"`, `"kondensator"`, `"kern"`) mit vertikalen Kupferspulen-Türmen (`"copper"`, `"steel"`, `"glass"`), Funkenstrecken (`"spark"`) und Props (`"spule_isolator"`) und registriere `"spule"` in `GENERATORS`.
- **Akzeptanzkriterien:**
  - Alle 6 MVP-Universen in `UNIVERSES` (sowie die Pool-Universen in `POOL_UNIVERSES`) sind in `GENERATORS` registriert und erzeugen gültige `Level`-Instanzen mit ihren 3 kanonischen Regionen aus `V0a`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d09 -q && uv run pytest --ignore=tests/spec -q`

---

## D10 — Universums-Generatoren & Props-Spawns in `worldgen.py` und `Run` verdrahten (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D09`
- **Ziel-Dateien:** `src/worldgen.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/worldgen.py`, `src/run.py` (Zeilen 495–560), `tests/spec/test_phase_d.py` (`-k d10`)
- **Aufgabe:**
  1. Leite `generate_level(world, depth, seed, *, universe=None)` in `src/worldgen.py` an `generate_universe(world, universe, depth, seed)` weiter, sobald `universe is not None` übergeben wird (und nutze für `universe is None` `"fleischwelt"` als Default).
  2. Spawne in `Run._populate` den Zwischenboss (`universe.mid_boss`) in der Mitte von `level.mid_boss_arena` und den Endboss (`universe.boss`) in der Mitte von `level.boss_arena`.
- **Akzeptanzkriterien:**
  - Ein `Run(seed=7, universe_key=k)` erzeugt für jedes der 6 MVP-Universen in `UNIVERSES` ein `Level` mit `level.universe_key == k` sowie je einem gespawnten Zwischenboss und Endboss.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d10 -q && uv run pytest --ignore=tests/spec -q`

---

## D11 — Universums-Ereignisse Teil 1: Datenmodell & 6 Bibel-Events (`src/events.py`) (`V10`)

- **Größe:** S
- **Abhängigkeiten:** `A07`
- **Ziel-Dateien:** `src/events.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V10`), `tests/spec/test_phase_d.py` (`-k d11`)
- **Aufgabe:**
  1. Erstelle `src/events.py` mit `EventSpec`, `Event` (`on_start`, `tick`, `on_end`, `to_data`, `from_data`), `pick_event(universe_key, depth, rng) -> Event | None` und implementiere die 6 kanonischen Bibel-Events in `EVENTS`:
     - `"verdauung"` (`fleischwelt`): Säurepegel steigt und senkt sich periodisch.
     - `"pruefung"` (Alias `"steuerpruefung"`, `aktenhalde`): spawnt 1 `"agent_streife"`/`"agent_sachbearbeiter"` und erhöht `price_factor` während der Dauer um `+25 %`.
     - `"brauseregen"` (`glibbria`): lässt Brause-/Gelee-Tropfen regnen.
     - `"riesenschritt"` (`kruemelreich`): Kamerawackeln + herabrieselnde Krümel (`"dough"`/`"sugar"`).
     - `"bass_drop"` (`sporenklub`): verstärkter Beat-Puls + Sporenwolken.
     - `"glockenschlag"` (`abtei`): periodische Unterwasser-Schallwelle.
- **Akzeptanzkriterien:**
  - Alle 6 kanonischen Bibel-Events lassen sich starten, über `tick(dt, run)` fortschreiben, beenden (`active == False` bei `remaining <= 0`) und via `to_data`/`from_data` serialisieren.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d11 -q && uv run pytest --ignore=tests/spec -q`

---

## D12 — Universums-Ereignisse Teil 2: Sekundärereignisse & `Run`-Integration (`src/events.py`, `src/run.py`) (`V10`)

- **Größe:** S
- **Abhängigkeiten:** `D11`
- **Ziel-Dateien:** `src/events.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V10`), `src/events.py`, `src/run.py`, `tests/spec/test_phase_d.py` (`-k d12`)
- **Aufgabe:**
  1. Ergänze in `src/events.py` die Sekundärereignisse aus `V10`: `"lieferung"`, `"pilz_schwarm"`, `"gold_regen"`, `"stromausfall"`, `"flutwelle"`, `"zucker_rausch"`, `"wanderzirkus"`, `"ameisen_karawane"`.
  2. Hänge `self.event: Event | None = None` in `Run` (`src/run.py`) ein: Beim Universums-Start wird `pick_event` ausgewertet, bei Aktivierung `event.on_start(self)` aufgerufen und in `Run.update` `event.tick(dt, self)` ausgeführt.
- **Akzeptanzkriterien:**
  - `len(EVENTS) >= 9`; `event.on_start` feuert `run.emit("event_start", ...)` und `event.on_end` feuert `run.emit("event_end", ...)`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d12 -q && uv run pytest --ignore=tests/spec -q`

---

## D13 — Optionale Prüfungen (`src/challenges.py`) (`V13`)

- **Größe:** S
- **Abhängigkeiten:** `A07`
- **Ziel-Dateien:** `src/challenges.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13`), `tests/spec/test_phase_d.py` (`-k d13`)
- **Aufgabe:**
  1. Erstelle `src/challenges.py` mit `ChallengeSpec`, `Challenge` (`activate`, `on_event`, `tick`, `pay_reward`, `to_data`, `from_data`), `CHALLENGES` (alle 6 Prüfungen aus `V13`: `"pacifist"`, `"no_gold"`, `"speed_run"`, `"no_damage"`, `"kill_streak"`, `"dry_feet"`) und `pick_challenge(universe_key, depth, rng) -> Challenge`.
- **Akzeptanzkriterien:**
  - `"pacifist"` schlägt bei `"kill"` mit `killer=="player"` fehl und gewinnt bei `"leave_universe"`.
  - `"no_gold"` schlägt bei `"pickup"` mit `kind=="gold"` fehl und gewinnt bei `"leave_universe"`.
  - `"speed_run"` gewinnt bei `"leave_universe"` innerhalb von `90 s` und schlägt bei `elapsed > 90 s` fehl.
  - `"no_damage"` gewinnt nach `45 s` ohne `"hurt_player"`; `"kill_streak"` gewinnt nach `8` Kills innerhalb von `20 s`; `"dry_feet"` gewinnt nach `40 s` ohne Flüssigkeitskontakt (`player.in_liquid(world)`).
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d13 -q && uv run pytest --ignore=tests/spec -q`

---

## D14 — Prüfungs-Schrein-Interaktion & Auszahlung in `src/run.py` (`V13`)

- **Größe:** S
- **Abhängigkeiten:** `D10`, `D13`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13`), `src/challenges.py`, `src/run.py`, `tests/spec/test_phase_d.py` (`-k d14`)
- **Aufgabe:**
  1. Initialisiere auf `Run` (`src/run.py`) beim Universums-Eintritt `self.challenge = pick_challenge(self.universe.key, self.depth, self.rng)` und registriere einen Listener in `self.listeners`, der alle Events an `self.challenge.on_event(name, data, self)` weiterleitet.
  2. Aktiviere die Prüfung (`self.challenge.activate()`), wenn die Spielerin in `level.challenge_shrine` die Interaktionstaste `[E]` drückt (`Run.try_activate_shrine()`), ticke `self.challenge.tick(dt, self)` in `Run.update` und zahle bei `completed == True` einmalig `self.challenge.pay_reward(self)` aus.
- **Akzeptanzkriterien:**
  - Aktivieren am Schrein und Bestehen der Prüfung erhöht `run.gold` um `spec.reward_gold`, fügt `spec.reward_samples` Proben hinzu und feuert `run.emit("challenge_done", key=..., success=True)`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d14 -q && uv run pytest --ignore=tests/spec -q`

---

## D15 — Deterministischer Playtest-Bot: Einzel-Universum (`src/bot.py` Teil 1) (`V14`)

- **Größe:** S
- **Abhängigkeiten:** `D10`
- **Ziel-Dateien:** `src/bot.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V14`), `src/pathfind.py`, `src/run.py`, `tests/spec/test_phase_d.py` (`-k d15`)
- **Aufgabe:**
  1. Erstelle `src/bot.py` mit `BotReport` und `run_bot(universe_key: str, seed: int = 1, max_seconds: float = 120.0) -> BotReport` gemäß `V14`:
     - Steuert die Spielerin in festen `dt = 1/60`-Schritten Richtung `exit_point` (nutzt `find_path` / Graben / Fliegen / Feuern auf nahe Gegner), hebt nahe Pickups auf und protokolliert `ticks`, `reached_exit`, `died`, `kills`, `gold_collected`, `samples_collected`, `stuck_ratio`, `min_hp_ratio`, `errors`.
- **Akzeptanzkriterien:**
  - `run_bot("fleischwelt", seed=1, max_seconds=30.0)` läuft headless unter 2 Sekunden durch und liefert einen validen `BotReport` mit `errors == []` und `stuck_ratio < 0.8`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d15 -q && uv run pytest --ignore=tests/spec -q`

---

## D16 — Deterministischer Playtest-Bot: Kompletter Universen-Run (`src/bot.py` Teil 2) (`V14`)

- **Größe:** S
- **Abhängigkeiten:** `D15`
- **Ziel-Dateien:** `src/bot.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V14`), `src/bot.py`, `tests/spec/test_phase_d.py` (`-k d16`)
- **Aufgabe:**
  1. Ergänze in `src/bot.py` `run_full(seed: int = 1, max_seconds_per_stage: float = 120.0) -> list[BotReport]`, das einen kompletten Universen-Durchlauf über `RunPlan(seed)` / `UniversePlan(seed)` simuliert (inkl. Übergang zum nächsten Universum bei Erreichen des Ausgangs) und für jede Stufe einen `BotReport` zurückgibt.
- **Akzeptanzkriterien:**
  - `run_full(seed=1, max_seconds_per_stage=15.0)` liefert eine Liste von `BotReport`-Objekten ohne `errors`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d16 -q && uv run pytest --ignore=tests/spec -q`
