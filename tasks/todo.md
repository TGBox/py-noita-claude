# Task List: Bibel-Konsolidierung & Atomare S-Karten-Synchronisation

Master-Plan: [`tasks/plan.md`](plan.md) · Referenz-Kritik: [`docs/critique.md`](../docs/critique.md)

---

## Phase 1: Bibel-Erweiterung & Bereinigung

### Task 1: Bibel Kap. 02, 03 und 04 um neue Fähigkeiten, Pool-Universen (`schrott`, `kuchen`, `spule`) und Agenten-Rang 4 erweitern

**Description:** Erweitert die System-, Universums- und Figuren-Kapitel der Bibel um die im Interview bestätigten Ergänzungen (4 zusätzliche Fähigkeiten `aura`, `teleport`, `kamikaze`, `burrow`; Sekundärereignisse & Schrein-Prüfungen; Türsteher-Bestechung, Blattlaus-Melken & Mönchsfisch-Chor; detaillierte Steckbriefe für `schrott`, `kuchen`, `spule` im Pool; 4. Agenten-Typ `agent_abteilungsleiter` ab Fahndungsstufe 4 sowie optionale Böse-Ich-Geheimraum-Begegnungen).

**Acceptance criteria:**

- [ ] `docs/bibel/02-systeme.md` dokumentiert alle 20 Fähigkeiten (`graze`..`stationary` + `aura`, `teleport`, `kamikaze`, `burrow`), Art-Streit/Blutfehden (`Grudges`), Klonitas aktive Kampf-/Schutz-Hilfen (`shield`, `snack`, `spark`, `cleanse`) und Einmal-Macken (`shiny_poke`, `loud_sneeze`, `sample_nibble`)
- [ ] `docs/bibel/03-universen.md` führt bei den 6 MVP-Universen je 4 Einheimische, 1 Unter-Zwischenboss und die zerstörbaren Props auf und enthält im Pool die ausgearbeiteten Entwürfe für `schrott`, `kuchen` und `spule`
- [ ] `docs/bibel/04-figuren.md` enthält `agent_abteilungsleiter` (neben `agent_streife`, `agent_vollstrecker`, `agent_drohne`)

**Verification:**

- [ ] Manuelle Prüfung: Alle Verweise zwischen Kap. 02, 03 und 04 sind konsistent

**Dependencies:** None

**Files likely touched:**

- `docs/bibel/02-systeme.md`
- `docs/bibel/03-universen.md`
- `docs/bibel/04-figuren.md`

**Estimated scope:** Medium (3 files)

---

### Task 2: Bibel Kap. 05, 07, 08 und 09 erweitern & veraltete Plan-Dateien löschen

**Description:** Ergänzt die 12 zusätzlichen Kreaturen und 6 Unter-Zwischenbosse in Kap. 05, die 5 allgemeinen Proben (`probe_knochen`, `probe_aether`, `probe_schatten`, `probe_gold`, `probe_kern`), die 2 neuen Werkstatt-Stationen (`ws_shredder`, `ws_well`), die Trainings-Attrappe, die 4 Elementar-Rätsel am Physik-o-Mat und die 6 Schrein-Prüfungen in Kap. 07, Rang-Abrechnung in Kap. 08/09 und löscht die 4 veralteten `phase-*.md`-Dateien.

**Acceptance criteria:**

- [ ] `docs/bibel/05-gegner.md` enthält alle 24 regulären Einheimischen (4 je MVP-Universum), die 2 großen Kreaturen, die 6 Unter-Zwischenbosse, die 6 Haupt-Zwischengegner, die 4 Behörden-Agenten, die 3 Bösen Ichs (inkl. Geheimraum-Begegnung & Kaiserin-Handel) und den Rat / `ober_cloita`
- [ ] `docs/bibel/07-gegenstaende-und-werkstatt.md` enthält alle 17 Proben (12 Universums-Proben + 5 allgemeine Proben), alle 12 Werkstatt-Stationen + Trainings-Attrappe, alle 8 Physik-o-Mat-Rätsel und beide Herausforderungs-Arten (6 NPC-Aufträge + 6 Schrein-Prüfungen)
- [ ] Die 4 veralteten Dateien `docs/plan/phase-c-universen.md`, `docs/plan/phase-d-werkstatt.md`, `docs/plan/phase-e-bosse.md` und `docs/plan/phase-f-umbenennung.md` sind gelöscht

**Verification:**

- [ ] `Get-ChildItem docs/plan/phase-*.md` zeigt nur noch die 7 kanonischen Dateien `phase-a-fundament.md` bis `phase-g-abnahme.md`

**Dependencies:** Task 1

**Files likely touched:**

- `docs/bibel/05-gegner.md`
- `docs/bibel/07-gegenstaende-und-werkstatt.md`
- `docs/bibel/08-ui-und-texte.md`
- `docs/bibel/09-arbeitspakete.md`

**Estimated scope:** Medium (4 files + 4 deletions)

---

## Checkpoint: Nach Tasks 1–2 (Bibel & Struktur)

- [ ] Alle 6 MVP-Universen und alle erweiterten Inhalte sind in `docs/bibel/` dokumentiert
- [ ] Keine veralteten `phase-*.md`-Dateien mehr unter `docs/plan/`

---

## Phase 2: Schnittstellen-Verträge (`V0`–`V23`) synchronisieren

### Task 3: Master-Index `docs/plan/vertraege.md` sowie `v00`, `v01`, `v05`, `v09` synchronisieren

**Description:** Beseitigt alle Widersprüche zwischen `vertraege.md` und den Teilverträgen `v00`, `v01`, `v05`, `v09` (6 MVP-Universen, `RunPlan` mit Alias `UniversePlan`, Python `>= 3.11`, ctypes-Rust-Kern, 20 Fähigkeiten, Haltungen, `PathFollower` + `next_waypoint`, Fraktionen + `Grudges`, `PixelCanvas` & Sprite-Builder-Funktionen, Waffenteile nach Bibel Kap. 06, `Level`-Felder).

**Acceptance criteria:**

- [ ] `docs/plan/vertraege.md` nennt die 6 MVP-Universen, 17 Proben, 12 Stationen, Python `>= 3.11` und stimmt in allen Zahlen exakt mit den Teilverträgen überein
- [ ] `v00-migration-und-schluessel.md` verwendet keine veralteten Karten-IDs (`T5.00a` etc.) mehr, sondern `A01`–`G10`
- [ ] `v01-verhalten-und-wegsuche.md`, `v05-sprites-und-teile.md` und `v09-universen-und-ereignisse.md` enthalten sämtliche Funktions- und Klassennamen, die in `tests/spec/` geprüft werden

**Verification:**

- [ ] Statischer Abgleich aller Symbolnamen in `v00`–`v09` gegen die Bibel

**Dependencies:** Task 2

**Files likely touched:**

- `docs/plan/vertraege.md`
- `docs/plan/vertraege/v00-migration-und-schluessel.md`
- `docs/plan/vertraege/v01-verhalten-und-wegsuche.md`
- `docs/plan/vertraege/v05-sprites-und-teile.md`
- `docs/plan/vertraege/v09-universen-und-ereignisse.md`

**Estimated scope:** Medium (5 files)

---

### Task 4: Teilverträge `v11`, `v15`, `v18`, `v21` auf Bibel-Kanon umschreiben

**Description:** Schreibt `v11-gegenstaende-und-ereignisbus.md`, `v15-behoerde-und-bosse.md`, `v18-werkstatt-und-wirtschaft.md` und `v21-klonita-ui-und-speichern.md` auf die 6 MVP-Universen (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`), die 17 Proben (12 Bibel-Proben + 5 allgemeine Proben), die 6 Bibel-Zwischengegner (`oberstempler`, `mutter_glibber`, `dj_myzel`, `abt_kieme`, `ameisenkoenigin`, `weltenherz`), die 4 Behörden-Agenten, die 12 Werkstatt-Stationen (inkl. `ws_liege` und `ws_zapfhahn`), die 6 Bibel-Händler (`Herr Pansen`, `Frau Abheft`, `Wobbel`, `Krümel-Karl`, `DJ Lamelle`, `Bruder Flosse`), die 8 Physik-o-Mat-Rätsel und Klonitas Bibel-Trigger um.

**Acceptance criteria:**

- [ ] `V11` definiert alle 17 Proben (inkl. der 12 Bibel-Proben aus `V0a`)
- [ ] `V15`–`V17` definieren die 4 Agenten (`agent_streife`, `agent_drohne`, `agent_vollstrecker`, `agent_abteilungsleiter`), die 6 Bibel-Zwischengegner in `src/bosses/` sowie die 3 Bösen Ichs und das 3-stufige Hauptquartier
- [ ] `V18`–`V20` definieren alle 12 Werkstatt-Stationen (mit `STATION_ALIASES`), die 6 Bibel-Händler mit ihren `home_universe`-Keys (`fleischwelt`..`abtei`), den Fabrikator (inkl. `bauplan_splitter`) und die 8 Physik-o-Mat-Rätsel
- [ ] `V21`–`V23` definieren Klonitas Bibel-Trigger, Hilfen, Macken und Sprüche für die 6 MVP-Universen

**Verification:**

- [ ] Kein einziger Verweis auf nicht-existente MVP-Universen mehr in `v11`, `v15`, `v18`, `v21`

**Dependencies:** Task 3

**Files likely touched:**

- `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md`
- `docs/plan/vertraege/v15-behoerde-und-bosse.md`
- `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md`
- `docs/plan/vertraege/v21-klonita-ui-und-speichern.md`

**Estimated scope:** Medium (4 files)

---

## Checkpoint: Nach Tasks 3–4 (Verträge)

- [ ] Alle 8 Vertragsdateien + `vertraege.md` sind vollständig konsistent mit der Bibel

---

## Phase 3: Phasen-Pläne (`A`–`G`) in echte S-Karten schneiden

### Task 5: `docs/plan/README.md`, `phase-a-fundament.md`, `phase-b-grafik.md` und `phase-c-kreaturen.md` aktualisieren

**Description:** Aktualisiert den Plan-Index sowie die Phasen A, B und C auf die 6 MVP-Universen, 17 Proben, Bibel-Waffenteile, 24 Einheimischen + 2 Großkreaturen + 6 Unter-Zwischenbosse + 6 Zwischengegner und stellt sicher, dass jede Karte maximal 1–2 Zieldateien hat.

**Acceptance criteria:**

- [ ] `A01` prüft die 12 Bibel-Proben (2 je Universum) und die kanonische Region-Reihenfolge der 6 MVP-Universen
- [ ] `phase-b-grafik.md` und `phase-c-kreaturen.md` decken alle Kreaturen, großen Kreaturen, Bosse, Waffenteile, Proben und Stationen der Bibel ab
- [ ] Keine Karte in Phase A, B oder C hat mehr als 2 Zieldateien

**Verification:**

- [ ] Prüfung aller `Ziel-Dateien:`-Zeilen in `phase-a`, `phase-b`, `phase-c` (jeweils `<= 2` Dateien)

**Dependencies:** Task 4

**Files likely touched:**

- `docs/plan/README.md`
- `docs/plan/phase-a-fundament.md`
- `docs/plan/phase-b-grafik.md`
- `docs/plan/phase-c-kreaturen.md`

**Estimated scope:** Medium (4 files)

---

### Task 6: `phase-d-universen.md`, `phase-e-werkstatt.md`, `phase-f-behoerde-bosse-klonita.md`, `phase-g-abnahme.md` und `docs/intent/atomarer-umsetzungsplan.md` aktualisieren

**Description:** Aktualisiert die Phasen D, E, F und G auf die 6 MVP-Universums-Generatoren (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`), die 6 Universums-Events + Sekundärereignisse, die 12 Werkstatt-Stationen, die 6 Bibel-Zwischengegner (`oberstempler`, `mutter_glibber`, `dj_myzel`, `abt_kieme`, `ameisenkoenigin`, `weltenherz`), das 3-stufige Hauptquartier und schneidet Karten mit >2 Zieldateien (wie `F04`–`F06`) auf maximal 2 Zieldateien zu. Aktualisiert zudem `docs/intent/atomarer-umsetzungsplan.md` bezüglich der vorab angelegten Spec-Tests und Gerüste.

**Acceptance criteria:**

- [ ] Keine Karte in Phase D, E, F oder G hat mehr als 2 Zieldateien
- [ ] Alle Karten verweisen ausschließlich auf Symbole aus `V0`–`V23` und `docs/bibel/`
- [ ] `docs/intent/atomarer-umsetzungsplan.md` spiegelt den aktuellen Stand (Vorab-Tests + Gerüste) korrekt wider

**Verification:**

- [ ] Skript-Prüfung über alle `phase-*.md`: Jede Karte hat `1–2` Zieldateien und gültige Vertragsreferenzen

**Dependencies:** Task 5

**Files likely touched:**

- `docs/plan/phase-d-universen.md`
- `docs/plan/phase-e-werkstatt.md`
- `docs/plan/phase-f-behoerde-bosse-klonita.md`
- `docs/plan/phase-g-abnahme.md`
- `docs/intent/atomarer-umsetzungsplan.md`

**Estimated scope:** Medium (5 files)

---

## Checkpoint: Nach Tasks 5–6 (Phasen-Pläne)

- [ ] Alle Phasen-Pläne A–G halten die S-Regel (`<= 2` Zieldateien) und den Bibel-Kanon strikt ein

---

## Phase 4: Code-Gerüste (`src/` & `tools/`) auf Bibel-Kanon bringen

### Task 7: `src/universes/`, `src/samples.py` und `src/materials.py` auf die 6 MVP-Universen und 17 Proben umstellen

**Description:** Bereinigt `src/universes/catalog.py` und `src/universes/model.py`, sodass `UNIVERSES` wieder exakt die 6 MVP-Universen (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`) mit ihren kanonischen `probe_*`-Tupeln, Regionen, 4 Kreaturen, großen Kreaturen und Bossen enthält (und `POOL_UNIVERSES` die Pool-Einträge). Aktualisiert `src/samples.py` auf die 17 Proben + `SAMPLE_ALIASES` und `src/universes/gen/` auf die 6 MVP-Universums-Generatoren.

**Acceptance criteria:**

- [ ] `len(UNIVERSES) == 6` mit den Schlüsseln `("fleischwelt", "aktenhalde", "glibbria", "kruemelreich", "sporenklub", "abtei")`
- [ ] `tests/test_universes.py` läuft vollständig grün
- [ ] `src/samples.py` enthält alle 17 Proben (12 Universums-Proben + 5 allgemeine Proben) und `SAMPLE_ALIASES`

**Verification:**

- [ ] `uv run pytest tests/test_universes.py -q`

**Dependencies:** Task 6

**Files likely touched:**

- `src/universes/model.py`
- `src/universes/catalog.py`
- `src/universes/plan.py`
- `src/samples.py`
- `src/universes/gen/__init__.py`

**Estimated scope:** Medium (5 files)

---

### Task 8: `src/behaviour.py`, `src/factions.py`, `src/pathfind.py`, `src/enemies.py`, `src/weapon_parts.py` und `tools/` synchronisieren

**Description:** Synchronisiert die Verhaltens-, Fraktions-, Wegsuche-, Gegner-, Waffenteil- und Sprite-Werkzeug-Module mit den bereinigten Verträgen `V1`–`V8b` (inkl. aller 24 Einheimischen, 2 Großkreaturen, 6 Unter-Zwischenbosse, 6 Zwischengegner, 4 Agenten, 3 Bösen Ichs, `ober_cloita`, Bibel-Waffenteile + Aliase, `PathFollower` + `next_waypoint`, `Grudges` + `hostile` + `are_hostile`).

**Acceptance criteria:**

- [ ] Alle Kreaturen, großen Kreaturen, Zwischengegner, Agenten und Bösen Ichs der 6 MVP-Universen sind in `SPECIES` (`src/enemies.py`) enthalten
- [ ] `src/factions.py`, `src/pathfind.py`, `src/behaviour.py` und `src/weapon_parts.py` erfüllen alle Vertrags-Signaturen aus `V1`–`V8b`
- [ ] `tools/palette.py` und `tools/sprites*.py` unterstützen alle 6 MVP-Universen und alle Bibel-Sprites

**Verification:**

- [ ] `uv run pytest tests/test_enemies.py tests/test_projectiles.py -q`

**Dependencies:** Task 7

**Files likely touched:**

- `src/behaviour.py`
- `src/factions.py`
- `src/pathfind.py`
- `src/enemies.py`
- `src/weapon_parts.py`

**Estimated scope:** Medium (5 files)

---

### Task 9: `src/workshop.py`, `src/traders.py`, `src/fabricator.py`, `src/minigames/`, `src/authority.py`, `src/bosses/`, `src/events.py`, `src/challenges.py`, `src/klonita*.py` und `src/run.py` angleichen

**Description:** Aktualisiert die Werkstatt-Stationen (alle 12 Stationen + `STATION_ALIASES`), die 6 Händler (`home_universe` auf `fleischwelt`..`abtei`), den Fabrikator, die 8 Physik-o-Mat-Rätsel, die 4 Agenten-Typen in `src/authority.py`, die Boss-Skripte für die 6 Bibel-Zwischengegner (`oberstempler`, `mutter_glibber`, `dj_myzel`, `abt_kieme`, `ameisenkoenigin`, `weltenherz`), das 3-stufige Hauptquartier (Zugang über 6 `memory_shards` oder 3 `badges` / 4 Sterne), die Universums-Events, die Challenges und Klonitas Sprüche/Hilfen/Macken.

**Acceptance criteria:**

- [ ] Alle 12 Stationen in `src/workshop.py` sind über ihre Bibel-Keys und englischen Aliase erreichbar
- [ ] `make_boss_script` unterstützt alle 6 Bibel-Zwischengegner, die 3 Bösen Ichs und `ober_cloita`
- [ ] Alle bestehenden Tests unter `tests/test_*.py` laufen ohne Fehler grün

**Verification:**

- [ ] `uv run pytest --ignore=tests/spec -q`

**Dependencies:** Task 8

**Files likely touched:**

- `src/workshop.py`
- `src/traders.py`
- `src/authority.py`
- `src/bosses/__init__.py`
- `src/run.py`

**Estimated scope:** Medium (5+ files)

---

## Checkpoint: Nach Tasks 7–9 (Bestands-Suite & Gerüste)

- [ ] `uv run pytest --ignore=tests/spec -q` läuft zu 100 % grün

---

## Phase 5: 1:1 Spec-Tests (`tests/spec/`) & Gesamtabnahme

### Task 10: `tests/spec/test_phase_a.py`, `test_phase_b.py` und `test_phase_c.py` auf Bibel-Kanon & 1:1-Karten-Tests umstellen

**Description:** Schreibt die Spec-Tests für die Phasen A, B und C so um, dass sie die kanonischen 6 MVP-Universen, 17 Proben, Bibel-Stationen, Bibel-Waffenteile und Bibel-Kreaturen prüfen und **jede einzelne Karten-ID** (`a01`..`a26`, `b01`..`b36`, `c01`..`c17`) eine eigene Testfunktion `def test_<id_klein>_...` besitzt (keine Sammeltests wie `test_b21_to_b24` mehr).

**Acceptance criteria:**

- [ ] Für jede Karten-ID in Phase A, B und C findet `pytest tests/spec/test_phase_<x>.py -k <id_klein>` mindestens 1 Test und läuft grün
- [ ] Keine Sammel-Testfunktionen ohne Einzel-Funktionen pro Karte mehr vorhanden

**Verification:**

- [ ] `uv run pytest tests/spec/test_phase_a.py tests/spec/test_phase_b.py tests/spec/test_phase_c.py -q`

**Dependencies:** Task 9

**Files likely touched:**

- `tests/spec/test_phase_a.py`
- `tests/spec/test_phase_b.py`
- `tests/spec/test_phase_c.py`

**Estimated scope:** Medium (3 files)

---

### Task 11: `tests/spec/test_phase_d.py`, `test_phase_e.py`, `test_phase_f.py` und `test_phase_g.py` auf Bibel-Kanon & 1:1-Karten-Tests umstellen

**Description:** Schreibt die Spec-Tests für die Phasen D, E, F und G auf die 6 MVP-Universen, 12 Werkstatt-Stationen, 6 Händler, 8 Physik-o-Mat-Rätsel, 6 Bibel-Zwischengegner, 3 Bösen Ichs, das 3-stufige Hauptquartier und Klonita um und legt für **jede einzelne Karten-ID** (`d01`..`g10`) eine eigene Testfunktion `def test_<id_klein>_...` an.

**Acceptance criteria:**

- [ ] Für jede Karten-ID in Phase D, E, F und G findet `pytest tests/spec/test_phase_<x>.py -k <id_klein>` mindestens 1 Test und läuft grün
- [ ] Auch die 17 in `docs/critique.md` genannten fehlenden IDs (`B22`, `B23`, `B26`, `B29`, `B30`, `B33`, `B34`, `E08`, `E11`–`E14`, `F04`, `F05`, `F12`, `F13`, `G05`) haben eigene, direkt ausführbare Testfunktionen

**Verification:**

- [ ] `uv run pytest tests/spec/test_phase_d.py tests/spec/test_phase_e.py tests/spec/test_phase_f.py tests/spec/test_phase_g.py -q`

**Dependencies:** Task 10

**Files likely touched:**

- `tests/spec/test_phase_d.py`
- `tests/spec/test_phase_e.py`
- `tests/spec/test_phase_f.py`
- `tests/spec/test_phase_g.py`

**Estimated scope:** Medium (4 files)

---

### Task 12: Vollständige Abnahme-Verifikation über alle Karten, Tests, Verträge und Linter

**Description:** Prüft automatisiert per Prüfskript, dass (1) jede Karte in `docs/plan/phase-*.md` maximal 2 Zieldateien hat, (2) für jede Karten-ID `-k <id_klein>` mindestens 1 Test gesammelt und bestanden wird, (3) kein von `tests/spec/` importierter Name in den Verträgen fehlt, (4) die gesamte Test-Suite (`uv run pytest -q`) grün ist und (5) `uv run ruff check src tests tools` 0 Fehler meldet.

**Acceptance criteria:**

- [ ] Alle Karten-Einzeltests (`-k <id_klein>`), alle Spec-Tests und alle Bestandstests laufen gemeinsam grün (`uv run pytest -q`)
- [ ] `uv run ruff check src tests tools` ist komplett sauber

**Verification:**

- [ ] `uv run pytest -q && uv run ruff check src tests tools`

**Dependencies:** Task 11

**Files likely touched:**

- `tests/spec/` (Feinschliff falls nötig)
- `src/` (Feinschliff falls nötig)

**Estimated scope:** Small (1-2 files)

---

## Checkpoint: Complete

- [ ] Alle Akzeptanzkriterien aus `tasks/plan.md` und `tasks/todo.md` sind erfüllt
- [ ] Bereit zur Übergabe an den Nutzer
