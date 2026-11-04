# Phase D — Universums-Generatoren, Ereignisse, Prüfungen & Playtest-Bot (26 atomare S-Karten: `D01`–`D29`; `D07`–`D09` entfallen)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_d.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Generatoren und Systeme folgen `V9`, `V10`, `V13`, `V14` aus [v09-universen-und-ereignisse.md](vertraege/v09-universen-und-ereignisse.md).

---

> `D07`–`D09` (Pool-Generatoren `schrott`, `kuchen`, `spule`) sind nach Phase J verschoben. `D17`–`D21` legen die Materialsätze der fünf Universen an, die noch keinen eigenen Satz haben (Aktenhalde hat ihn seit T1); sie müssen vor dem jeweiligen Generator fertig sein.

## D01 — Generator Fleischwelt (`src/universes/gen/fleischwelt.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D17`
- **Ziel-Dateien:** `src/universes/gen/fleischwelt.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Fleischwelt“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d01`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/fleischwelt.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="vertical"` über `region_bands`, Regionen `"schlund"`, `"magen"`, `"knochenmark"` in dieser Reihenfolge). Inhalt: Schlund mit Zähnen aus `"enamel"` an den Höhlenrändern; Magen mit Säurebecken (`"acid"`) und Talg (`"tallow"`); Knochenmark aus `"bone"` mit Zahnschmelzadern. Grundmasse `"flesh"`. Props `"saeure_behaelter"`, `"magen_zotte"`. Geheimkammer (Erinnerungssplitter) in Knochen versiegelt.
  2. Registriere `"fleischwelt": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"fleischwelt"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["fleischwelt"], 1, 42)` liefert ein `Level` mit `level.universe_key == "fleischwelt"`, `[r[0] for r in level.regions] == ["schlund", "magen", "knochenmark"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d01 -q && uv run pytest --ignore=tests/spec -q`

---

## D02 — Generator Aktenhalde (`src/universes/gen/aktenhalde.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`
- **Ziel-Dateien:** `src/universes/gen/aktenhalde.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Aktenhalde“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d02`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/aktenhalde.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="horizontal"` über `region_bands`, Regionen `"registratur"`, `"grossraumbuero"`, `"archivkeller"` in dieser Reihenfolge). Inhalt: Registratur mit dichten Regalreihen (`"aktendeckel"`-Böden, `"papier"` dazwischen); Großraumbüro mit Schreibtischen als Plattformen; Archivkeller dunkel mit Tintenseen (`"tinte"`). **Brandabschnitte** nach Bibel 03: kein zusammenhängender brennbarer Bereich größer als 640×360 (Trennwände aus `"rock"`, `"aktendeckel"` oder `"tintenpapier"`). Props `"akten_regal"`, `"amt_uhr"`.
  2. Registriere `"aktenhalde": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"aktenhalde"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["aktenhalde"], 1, 42)` liefert ein `Level` mit `level.universe_key == "aktenhalde"`, `[r[0] for r in level.regions] == ["registratur", "grossraumbuero", "archivkeller"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d02 -q && uv run pytest --ignore=tests/spec -q`

---

## D03 — Generator Glibbria (`src/universes/gen/glibbria.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D18`
- **Ziel-Dateien:** `src/universes/gen/glibbria.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Glibbria“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d03`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/glibbria.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="islands"` über `region_bands`, Regionen `"gelee_huegel"`, `"kaugummi_hoehlen"`, `"sirupkueste"` in dieser Reihenfolge). Inhalt: Schwebende Inseln aus `"glibber"` und `"glibber_rot"` mit `"zuckerguss"`-Plattformen; Kaugummi-Höhlen mit `"kaugummi"`-Pfützen; unten ein Meer aus `"brausesirup"`. Wo `ensure_path` scheitert, Brücken aus `"zuckerguss"`. Props `"glibber_ballon"`.
  2. Registriere `"glibbria": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"glibbria"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`) und `Level.quest_target` auf einen Punkt an der gegenüberliegenden Küste des Sirupsees.
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["glibbria"], 1, 42)` liefert ein `Level` mit `level.universe_key == "glibbria"`, `[r[0] for r in level.regions] == ["gelee_huegel", "kaugummi_hoehlen", "sirupkueste"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d03 -q && uv run pytest --ignore=tests/spec -q`

---

## D04 — Generator Krümelreich (`src/universes/gen/kruemelreich.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D19`
- **Ziel-Dateien:** `src/universes/gen/kruemelreich.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Krümelreich“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d04`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/kruemelreich.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="top_split"` über `region_bands`, Regionen `"fliesenwueste"`, `"unter_kuehlschrank"`, `"ameisenbau"` in dieser Reihenfolge). Inhalt: Fliesenwüste oben links (`"fliese"` mit Fugen, riesige `"kruemel"`, `"zucker"`-Körner, eine Erbse als Kreis aus `"rock"`); Unter dem Kühlschrank oben rechts (dunkel, `"staubfluse"`); Ameisenbau unten (Gänge und Kammern in `"brosel"`/`"kruemel"`, Königinnenkammer). Props `"ameisen_kokon"`.
  2. Registriere `"kruemelreich": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"kruemelreich"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["kruemelreich"], 1, 42)` liefert ein `Level` mit `level.universe_key == "kruemelreich"`, `[r[0] for r in level.regions] == ["fliesenwueste", "unter_kuehlschrank", "ameisenbau"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d04 -q && uv run pytest --ignore=tests/spec -q`

---

## D05 — Generator Sporenklub (`src/universes/gen/sporenklub.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D20`
- **Ziel-Dateien:** `src/universes/gen/sporenklub.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Sporenklub“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d05`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/sporenklub.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="vertical"` über `region_bands`, Regionen `"lautsprechertuerme"`, `"tanzflaeche"`, `"hinterzimmer"` in dieser Reihenfolge). Inhalt: Lautsprechertürme oben (vertikale Schächte aus `"pilzhut"`); Tanzfläche als offene Kavernen mit Lichtorgeln aus `"leuchtsporen"`; Hinterzimmer mit engen Gängen (`"pilzfleisch"`), an den schmalsten Stellen ein Platz für den Türsteherpilz. Props `"sporen_knolle"`, `"pilz_laterne"`.
  2. Registriere `"sporenklub": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"sporenklub"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["sporenklub"], 1, 42)` liefert ein `Level` mit `level.universe_key == "sporenklub"`, `[r[0] for r in level.regions] == ["lautsprechertuerme", "tanzflaeche", "hinterzimmer"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d05 -q && uv run pytest --ignore=tests/spec -q`

---

## D06 — Generator Versunkene Abtei (`src/universes/gen/abtei.py`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A25`, `D21`
- **Ziel-Dateien:** `src/universes/gen/abtei.py`, `src/universes/gen/__init__.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `docs/bibel/03-universen.md` (Abschnitt „Versunkene Abtei“), `src/universes/gen/common.py`, `tests/spec/test_phase_d.py` (`-k d06`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/abtei.py` mit `generate(world, universe, depth, seed) -> Level` (`topology="vertical"` über `region_bands`, Regionen `"glockenturm"`, `"kirchenschiff"`, `"krypta"` in dieser Reihenfolge). Inhalt: Glockenturm oben trocken mit Glocke aus `"glockenbronze"`; Kirchenschiff aus `"mauerwerk"` mit `"buntglas"`-Fenstern, geflutet (`"water"`) mit Luftblasen-Kapellen zum Atmen; Krypta dunkel mit Strömung (`current_vx`, V0a) und `"algen"`. Kerzen aus `"kerzenwachs"` als Lichtpunkte. Props `"abtei_glocke"`.
  2. Registriere `"abtei": generate` in `GENERATORS` (`src/universes/gen/__init__.py`). Nur Materialschlüssel aus dem aktiven Materialsatz `"abtei"` verwenden.
  3. Setze `Level.quest_giver` auf einen freien Bodenplatz (Auftraggeber der Herausforderung, `V13b`).
- **Akzeptanzkriterien:**
  - `generate_universe(world, UNIVERSES["abtei"], 1, 42)` liefert ein `Level` mit `level.universe_key == "abtei"`, `[r[0] for r in level.regions] == ["glockenturm", "kirchenschiff", "krypta"]`, freien `spawn`-/`exit_point`-Zellen und gültigen `(x0, y0, x1, y1)`-Arenen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d06 -q && uv run pytest --ignore=tests/spec -q`

---

## D10 — Universums-Generatoren & Props-Spawns in `worldgen.py` und `Run` verdrahten (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `D01`–`D06`, `C12` (Arten von Unter-Zwischenboss und Zwischengegner; ohne sie fällt `EnemyManager.spawn` auf `"made"` zurück)
- **Ziel-Dateien:** `src/worldgen.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/worldgen.py`, `src/run.py` (Zeilen 495–560), `tests/spec/test_phase_d.py` (`-k d10`)
- **Aufgabe:**
  0. Aktiviere im `Run` vor dem Generieren den Materialsatz des Universums (`mat.activate_key(universe.material_set)`; Welt neu aufbauen, wenn sich der Satz ändert – vorhandene Technik aus T1).
  1. Leite `generate_level(world, depth, seed, *, universe=None)` in `src/worldgen.py` an `generate_universe(world, universe, depth, seed)` weiter, sobald `universe is not None` übergeben wird (und nutze für `universe is None` `"fleischwelt"` als Default).
  2. Der `Run`-Konstruktor nimmt bereits `boss_slot: bool = False` an und speichert es als `self.boss_slot` (`V9` „Bossplatz“). Spawne in `Run._populate` den Unter-Zwischenboss (`universe.mid_boss`) immer in der Mitte von `level.mid_boss_arena` und den Zwischengegner (`universe.boss`) nur bei `boss_slot=True` in der Mitte von `level.boss_arena`.
- **Akzeptanzkriterien:**
  - Nach `Run(seed=7, universe_key=k)` ist der Materialsatz `universe.material_set` aktiv; `Run` erzeugt für jedes der 6 MVP-Universen ein `Level` mit `level.universe_key == k` und genau einem Unter-Zwischenboss, aber keinem Zwischengegner; mit `boss_slot=True` erscheint zusätzlich der Zwischengegner.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d10 -q && uv run pytest --ignore=tests/spec -q`

---

## D11 — Universums-Ereignisse Teil 1: Datenmodell & 6 Bibel-Events (`src/events.py`) (`V10`)

- **Größe:** S
- **Abhängigkeiten:** `A07`
- **Ziel-Dateien:** `src/events.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V10`), `docs/bibel/03-universen.md` (Zeilen „Ereignis“), `tests/spec/test_phase_d.py` (`-k d11`)
- **Aufgabe:**
  1. Erstelle `src/events.py` mit `EventSpec`, `Event` (`on_start`, `tick`, `on_end`, `to_data`, `from_data`), `pick_event(universe_key, depth, rng) -> Event | None` (liefert das Ereignis des Universums) und lege die 6 Bibel-Ereignisse mit `interval`, `warn` und `duration` aus `V10` in `EVENTS` an:
     - `"verdauung"` (`fleischwelt`): alle 90 s steigt in der Region `"magen"` für 20 s der Säurespiegel um 30 px (`"acid"`); Ankündigung durch Kamerawackeln.
     - `"pruefung"` (`aktenhalde`): alle 120 s Durchsage „Bitte halten Sie Ihre Unterlagen bereit.“; es erscheinen 2 `"agent_streife"`, unabhängig von der Fahndungsstufe.
     - `"brauseregen"` (`glibbria`): alle 100 s regnet es 15 s lang `"brausesirup"` am oberen Rand der Simulationszone.
     - `"riesenschritt"` (`kruemelreich`): alle 80 s nach 3 s Schatten-Ankündigung werden Zellen in einem 120 px breiten Streifen der Oberfläche zusammengedrückt; Kamerawackeln.
     - `"bass_drop"` (`sporenklub`): alle 60 s werden alle Körper und losen Gegenstände 40 px hochgeschleudert, Pulver hüpft.
     - `"glockenschlag"` (`abtei`): alle 75 s, 2 s Vorläuten, dann Stromschlag für alle Körper im Wasser (auch Gegner).
    Zeiten und Wirkung genau nach Bibel 03 („Ereignis“ je Universum).
- **Akzeptanzkriterien:**
  - Alle 6 kanonischen Bibel-Events lassen sich starten, über `tick(dt, run)` fortschreiben, beenden (`active == False` bei `remaining <= 0`) und via `to_data`/`from_data` serialisieren.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d11 -q && uv run pytest --ignore=tests/spec -q`

---

## D12 — Universums-Ereignisse Teil 2: Takt & `Run`-Integration (`src/events.py`, `src/run.py`) (`V10`)

- **Größe:** S
- **Abhängigkeiten:** `D11`
- **Ziel-Dateien:** `src/events.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V10`), `src/events.py`, `src/run.py`, `tests/spec/test_phase_d.py` (`-k d12`)
- **Aufgabe:**
  1. Hänge in `Run` (`src/run.py`) `self.event: Event | None` und `self.event_timer: float` ein: Beim Universums-Start `self.event_timer = spec.interval`; in `Run.update` herunterzählen, bei `warn` die Ankündigung (`emit("event_warn", key=…)`), bei `0` `event.on_start(self)`, während `duration` `event.tick(dt, self)`, danach `on_end` und Neustart des Timers.
  2. `on_start` feuert `run.emit("event_start", ...)`, `on_end` feuert `run.emit("event_end", ...)`.
- **Akzeptanzkriterien:**
  - `EVENTS` enthält genau die 6 Bibel-Ereignisse; jedes lässt sich starten, ticken und beenden.
  - Nach `interval` Sekunden Spielzeit ist in `Run` das Ereignis des Universums aktiv.
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

## D17 — Materialsatz Fleischwelt (`"fleischwelt"`) in `src/materials.py` (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/materials.py`, `src/universes/catalog.py`
- **Zu lesender Kontext:** `docs/bibel/03-universen.md` (Abschnitt „Fleischwelt“, Materialtabelle), `docs/bibel/02-systeme.md` („Materialien“), `src/materials.py` (Vorbild: `_FILES` und `AKTENHALDE`), `src/reactions.py` (`Reaction`), `tests/spec/test_phase_d.py` (`-k d17`)
- **Aufgabe:**
  1. Lege in `src/materials.py` die eigenen Materialien `"flesh"`, `"bone"`, `"enamel"`, `"blood"`, `"acid"`, `"growth"`, `"spores"`, `"tallow"`, `"crust"`, `"magma"` mit Farbe, Art und Härte aus der Bibel-Tabelle an (sofern nicht schon in `LIBRARY`) und definiere `MaterialSet("fleischwelt", (*BASE_KEYS, …))` mit höchstens 10 eigenen Materialien; trage ihn in `SETS` ein. Übernimm die 10 Materialien aus `_BODY` in `LIBRARY` (keine neuen Werte). Lege `DEFAULT_ALIASES`-Einträge für die entfallenden Materialien an (`mucus`, `pus`, `sinew` → nächstliegendes Material des Satzes; `bone_dust` → `"sand"`). Die globalen Reaktionen aus `src/reactions.py` gelten weiter.
  2. Setze in `src/universes/catalog.py` `material_set="fleischwelt"` für dieses Universum.
- **Akzeptanzkriterien:**
  - `SETS["fleischwelt"]` enthält alle 11 Grundmaterialien und genau die eigenen Materialien oben (≤ 10, Gesamtzahl ≤ `MAX_MATERIALS`); `activate(SETS["fleischwelt"])` läuft fehlerfrei.
  - `UNIVERSES["fleischwelt"].material_set == "fleischwelt"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d17 -q && uv run pytest --ignore=tests/spec -q`

---

## D18 — Materialsatz Glibbria (`"glibbria"`) in `src/materials.py` (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/materials.py`, `src/universes/catalog.py`
- **Zu lesender Kontext:** `docs/bibel/03-universen.md` (Abschnitt „Glibbria“, Materialtabelle), `docs/bibel/02-systeme.md` („Materialien“), `src/materials.py` (Vorbild: `_FILES` und `AKTENHALDE`), `src/reactions.py` (`Reaction`), `tests/spec/test_phase_d.py` (`-k d18`)
- **Aufgabe:**
  1. Lege in `src/materials.py` die eigenen Materialien `"glibber"`, `"glibber_rot"`, `"brausesirup"`, `"schaum"`, `"kaugummi"`, `"zuckerguss"` mit Farbe, Art und Härte aus der Bibel-Tabelle an (sofern nicht schon in `LIBRARY`) und definiere `MaterialSet("glibbria", (*BASE_KEYS, …))` mit höchstens 10 eigenen Materialien; trage ihn in `SETS` ein. Reaktionen: `glibber_rot` + Feuer → `brausesirup`; `brausesirup` + Feuer → kleine Schaumexplosion (`schaum`); `schaum` zerfällt nach 10 s (`life`); `zuckerguss` + Feuer → `brausesirup`. `kaugummi` sehr zäh (`mobility` klein), erstarrt nicht.
  2. Setze in `src/universes/catalog.py` `material_set="glibbria"` für dieses Universum.
- **Akzeptanzkriterien:**
  - `SETS["glibbria"]` enthält alle 11 Grundmaterialien und genau die eigenen Materialien oben (≤ 10, Gesamtzahl ≤ `MAX_MATERIALS`); `activate(SETS["glibbria"])` läuft fehlerfrei.
  - `UNIVERSES["glibbria"].material_set == "glibbria"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d18 -q && uv run pytest --ignore=tests/spec -q`

---

## D19 — Materialsatz Krümelreich (`"kruemelreich"`) in `src/materials.py` (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/materials.py`, `src/universes/catalog.py`
- **Zu lesender Kontext:** `docs/bibel/03-universen.md` (Abschnitt „Krümelreich“, Materialtabelle), `docs/bibel/02-systeme.md` („Materialien“), `src/materials.py` (Vorbild: `_FILES` und `AKTENHALDE`), `src/reactions.py` (`Reaction`), `tests/spec/test_phase_d.py` (`-k d19`)
- **Aufgabe:**
  1. Lege in `src/materials.py` die eigenen Materialien `"kruemel"`, `"brosel"`, `"zucker"`, `"karamell"`, `"honig"`, `"fliese"`, `"staubfluse"` mit Farbe, Art und Härte aus der Bibel-Tabelle an (sofern nicht schon in `LIBRARY`) und definiere `MaterialSet("kruemelreich", (*BASE_KEYS, …))` mit höchstens 10 eigenen Materialien; trage ihn in `SETS` ein. Reaktionen: `zucker` + Feuer → `karamell`; `staubfluse` sehr brennbar (`flammability` hoch); `karamell` erstarrt mit der Zeit (`decay_into` fest); `kruemel` hinterlässt bei Explosionen `brosel` (`debris`). `honig` zäh.
  2. Setze in `src/universes/catalog.py` `material_set="kruemelreich"` für dieses Universum.
- **Akzeptanzkriterien:**
  - `SETS["kruemelreich"]` enthält alle 11 Grundmaterialien und genau die eigenen Materialien oben (≤ 10, Gesamtzahl ≤ `MAX_MATERIALS`); `activate(SETS["kruemelreich"])` läuft fehlerfrei.
  - `UNIVERSES["kruemelreich"].material_set == "kruemelreich"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d19 -q && uv run pytest --ignore=tests/spec -q`

---

## D20 — Materialsatz Sporenklub (`"sporenklub"`) in `src/materials.py` (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/materials.py`, `src/universes/catalog.py`
- **Zu lesender Kontext:** `docs/bibel/03-universen.md` (Abschnitt „Sporenklub“, Materialtabelle), `docs/bibel/02-systeme.md` („Materialien“), `src/materials.py` (Vorbild: `_FILES` und `AKTENHALDE`), `src/reactions.py` (`Reaction`), `tests/spec/test_phase_d.py` (`-k d20`)
- **Aufgabe:**
  1. Lege in `src/materials.py` die eigenen Materialien `"pilzfleisch"`, `"pilzhut"`, `"leuchtsporen"`, `"neonsaft"`, `"nebel"` mit Farbe, Art und Härte aus der Bibel-Tabelle an (sofern nicht schon in `LIBRARY`) und definiere `MaterialSet("sporenklub", (*BASE_KEYS, …))` mit höchstens 10 eigenen Materialien; trage ihn in `SETS` ein. `leuchtsporen` und `neonsaft` leuchten (`glow > 0`); `nebel` ist ein harmloses Gas, das Sicht verdeckt (`OPAQUE`); `pilzhut` fest und hart.
  2. Setze in `src/universes/catalog.py` `material_set="sporenklub"` für dieses Universum.
- **Akzeptanzkriterien:**
  - `SETS["sporenklub"]` enthält alle 11 Grundmaterialien und genau die eigenen Materialien oben (≤ 10, Gesamtzahl ≤ `MAX_MATERIALS`); `activate(SETS["sporenklub"])` läuft fehlerfrei.
  - `UNIVERSES["sporenklub"].material_set == "sporenklub"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d20 -q && uv run pytest --ignore=tests/spec -q`

---

## D21 — Materialsatz Versunkene Abtei (`"abtei"`) in `src/materials.py` (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/materials.py`, `src/universes/catalog.py`
- **Zu lesender Kontext:** `docs/bibel/03-universen.md` (Abschnitt „Versunkene Abtei“, Materialtabelle), `docs/bibel/02-systeme.md` („Materialien“), `src/materials.py` (Vorbild: `_FILES` und `AKTENHALDE`), `src/reactions.py` (`Reaction`), `tests/spec/test_phase_d.py` (`-k d21`)
- **Aufgabe:**
  1. Lege in `src/materials.py` die eigenen Materialien `"mauerwerk"`, `"buntglas"`, `"kerzenwachs"`, `"glockenbronze"`, `"algen"`, `"weihrauch"` mit Farbe, Art und Härte aus der Bibel-Tabelle an (sofern nicht schon in `LIBRARY`) und definiere `MaterialSet("abtei", (*BASE_KEYS, …))` mit höchstens 10 eigenen Materialien; trage ihn in `SETS` ein. Reaktionen: Feuer schmilzt `kerzenwachs` (Wachs erstarrt wieder); `algen` wachsen langsam neben `water` (kleine Chance); `buntglas` zerspringt bei Explosionen in Splitter (`debris`, Gefahr-Schaden); `glockenbronze` sehr hart (`hardness=3`).
  2. Setze in `src/universes/catalog.py` `material_set="abtei"` für dieses Universum.
- **Akzeptanzkriterien:**
  - `SETS["abtei"]` enthält alle 11 Grundmaterialien und genau die eigenen Materialien oben (≤ 10, Gesamtzahl ≤ `MAX_MATERIALS`); `activate(SETS["abtei"])` läuft fehlerfrei.
  - `UNIVERSES["abtei"].material_set == "abtei"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d21 -q && uv run pytest --ignore=tests/spec -q`

---

## D22 — Herausforderungen: Daten, Annehmen & Auszahlung (`src/challenges.py`) (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `A04`, `A05`, `A07`, `A02`
- **Ziel-Dateien:** `src/challenges.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d22`)
- **Aufgabe:**
  1. Fülle `QUESTS` mit den 6 Einträgen der Tabelle in `V13b` (Texte aus Bibel 07) und implementiere `quest_for`, `Quest.accept`, `Quest.turn_in`, `to_data` und `from_data` nach den Regeln in `V13b`.
  2. Implementiere in `turn_in` alle sechs Auszahlungsarten der Tabelle (Spalte „Auszahlung“). `on_event` und `tick` ändern hier noch nichts (die universumsspezifische Logik folgt in `D24`–`D29`).
- **Akzeptanzkriterien:**
  - `turn_in` gelingt erst bei `progress >= goal`, zahlt genau einmal aus und feuert `quest_done`.
  - Jede der 6 Belohnungsarten landet wie in `V13b` beschrieben (Gold, Pickup, Proben, Neuwurf).
  - `to_data`/`from_data` stellt `accepted`, `progress`, `failed` und `reward_paid` wieder her.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d22 -q && uv run pytest --ignore=tests/spec -q`

---

## D23 — Herausforderungen in `Run`: Auftraggeber, `E`-Interaktion & Ereignisweiterleitung (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D22`, `D10`, `A16`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `src/run.py` (`try_interact_creature`, `listeners`), `tests/spec/test_phase_d.py` (`-k d23`)
- **Aufgabe:**
  1. Belege beim Betreten eines Universums `self.quest = quest_for(universe.key)` und spawne den Auftraggeber (`spec.giver`, `giver=True`, Haltung `passive`) an `level.quest_giver`.
  2. Erweitere `try_interact_creature`: Steht die Spielerin `<= 32 px` am Auftraggeber, ruft sie `quest.accept(self)` (wenn noch nicht angenommen) bzw. `quest.turn_in(self)` auf und zeigt `spec.text_de` als Sprechblase. Registriere einen Hörer, der alle `emit`-Ereignisse an `quest.on_event` weiterreicht, und rufe `quest.tick(dt, self)` in `Run.update` auf. Speichere `quest` im Spielstand.
- **Akzeptanzkriterien:**
  - In jedem MVP-Universum steht nach dem Start genau ein Auftraggeber mit `giver == True`.
  - `E` beim Auftraggeber nimmt die Herausforderung an; nach Erfüllen zahlt ein zweites `E` aus.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d23 -q && uv run pytest --ignore=tests/spec -q`

---

## D24 — Fleischwelt: „Bring mir 3 Gallensteine“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`
- **Ziel-Dateien:** `src/challenges.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d24`)
- **Aufgabe:**
  1. In `tick`: `progress = min(goal, inventory.sample_count("probe_gallenstein"))`. In `turn_in` vorher `inventory.take_samples({"probe_gallenstein": 3})`; scheitert diese Abbuchung, bleibt die Quest offen.
- **Akzeptanzkriterien:**
  - Mit 3 Gallensteinen im Rucksack ist `progress == 3`; `turn_in` zieht sie ab und legt eine Lebenskapsel ab.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d24 -q && uv run pytest --ignore=tests/spec -q`

---

## D25 — Aktenhalde: „Stempel 5 Formulare ab, bevor die Prüfung kommt“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`, `D12`
- **Ziel-Dateien:** `src/challenges.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d25`)
- **Aufgabe:**
  1. In `on_event`: `+1` je `"form_stamped"`, Scheitern bei `"event_start"` mit `key == "pruefung"`. In `run.py`: Auf das Ereignis `"quest_accepted"` mit `key == "challenge_aktenhalde"` 6 Pickups `kind="form_stamp"` (Sprite `formular_stempel`) auf freien Bodenplätzen verteilen; `Run._pick_up` auf ein solches Pickup entfernt es, gibt `True` zurück und feuert `emit("form_stamped", x=…, y=…)`.
- **Akzeptanzkriterien:**
  - 5 gestempelte Formulare ergeben `progress == 5`; eine Prüfung vorher lässt die Quest scheitern.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d25 -q && uv run pytest --ignore=tests/spec -q`

---

## D26 — Glibbria: „Bring meine Kuh heil über den Sirupsee“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`, `D03`, `C03`
- **Ziel-Dateien:** `src/challenges.py`, `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d26`)
- **Aufgabe:**
  1. In `src/enemies.py` die Art `"glibberkuh"` nach Bibel 05 anlegen (`faction="gelee"`, `passive`). In `src/challenges.py`: Beim Annehmen eine Glibberkuh neben dem Auftraggeber spawnen; in `tick` die Kuh per `steer_to` zur Spielerin lenken, solange der Abstand `< 120 px` ist, ihre Sirup-Kontaktzeit zählen (nach `3 s` stirbt sie) und `progress = 1` setzen, sobald sie `<= 24 px` an `level.quest_target` ist. Scheitern bei `"kill"` mit `species == "glibberkuh"`.
- **Akzeptanzkriterien:**
  - Kuh im Ziel → `progress == 1`; tote Kuh → `failed == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d26 -q && uv run pytest --ignore=tests/spec -q`

---

## D27 — Krümelreich: „Füttere die Blattläuse, ohne dass die Ameisen dich sehen“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`, `C04`, `D19`
- **Ziel-Dateien:** `src/challenges.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d27`)
- **Aufgabe:**
  1. In `tick` (höchstens einmal pro Sekunde): für jede `blattlaus` vorhandene `"zucker"`-Zellen im Umkreis `20 px` in Luft verwandeln und dafür `emit("aphid_fed", …)` feuern; in `on_event` zählt `"aphid_fed"` `+1`. Sieht ein `ameisenkrieger` die Spielerin (`can_see`), scheitert die Quest.
- **Akzeptanzkriterien:**
  - Drei Fütterungen ergeben `progress == 3`; ein sehender Ameisenkrieger lässt sie scheitern.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d27 -q && uv run pytest --ignore=tests/spec -q`

---

## D28 — Sporenklub: „Tanz mit mir!“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`
- **Ziel-Dateien:** `src/challenges.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d28`)
- **Aufgabe:**
  1. In `run.py` das Ereignis `"jump"` zusätzlich mit `on_beat=self.rule.on_beat()` feuern. In `on_event`: `"jump"` mit `on_beat` zählt `+1`, ohne Beat setzt es `progress = 0`.
- **Akzeptanzkriterien:**
  - 5 Sprünge auf dem Beat hintereinander ergeben `progress == 5`; ein Fehlsprung setzt zurück.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d28 -q && uv run pytest --ignore=tests/spec -q`

---

## D29 — Versunkene Abtei: „Läute die Glocke dreimal, ohne den Kraken zu wecken“ (`V13b`)

- **Größe:** S
- **Abhängigkeiten:** `D23`, `C09`, `D21`
- **Ziel-Dateien:** `src/challenges.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Herausforderungen in Universen“), `tests/spec/test_phase_d.py` (`-k d29`)
- **Aufgabe:**
  1. In `run.py`: Trifft ein Geschoss oder eine Explosion `"glockenbronze"`-Zellen im Rechteck des Props `abtei_glocke`, `emit("bell_rung", …)` und `emit("noise", x, y, radius=200)` (reicht an `EnemyManager.on_noise` weiter, `C09`). In `on_event`: `"bell_rung"` zählt `+1`, `"creature_woke"` mit `species == "kirchenkrake"` lässt die Quest scheitern.
- **Akzeptanzkriterien:**
  - Drei Glockenschläge ohne geweckte Krake ergeben `progress == 3`; eine geweckte Krake lässt die Quest scheitern.
- **Verifikation:** `uv run pytest tests/spec/test_phase_d.py -k d29 -q && uv run pytest --ignore=tests/spec -q`

---
