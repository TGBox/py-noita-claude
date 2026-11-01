# Implementation Plan: Bibel-Konsolidierung & Atomare S-Karten-Synchronisation

## Overview

Dieses Planungsdokument beschreibt die vollständige Konsolidierung zwischen der Design-Bibel ([`docs/bibel/`](../docs/bibel/00-uebersicht.md)), den technischen Schnittstellen-Verträgen ([`docs/plan/vertraege.md`](../docs/plan/vertraege.md) & [`docs/plan/vertraege/`](../docs/plan/vertraege)), den atomaren Phasen-Karten ([`docs/plan/phase-a-fundament.md`](../docs/plan/phase-a-fundament.md) bis [`docs/plan/phase-g-abnahme.md`](../docs/plan/phase-g-abnahme.md)), den Vorab-Abnahmetests ([`tests/spec/`](../tests/spec)) und den Code-Gerüsten unter [`src/`](../src) und [`tools/`](../tools) auf Basis des Reviews in [`docs/critique.md`](../docs/critique.md) sowie der im `/grill-me`-Interview getroffenen Design-Entscheidungen.

## Architecture Decisions

1. **Kanonische 6 MVP-Universen mit erweiterten Inhalten:**
   - Die 6 MVP-Universen der Bibel (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`) sind überall der alleinige aktive Kanon (`len(UNIVERSES) == 6`).
   - Jedes der 6 Universen erhält in der Bibel und in den Verträgen zusätzlich zu den 2 Bibel-Einheimischen 2 weitere thematisch passende Kreaturen (insgesamt 4 reguläre Einheimische je Universum = 24 Einheimische), die 2 großen Kreaturen (`trampolinwal`, `kirchenkrake`), die 6 Bibel-Zwischengegner (`oberstempler`, `mutter_glibber`, `dj_myzel`, `abt_kieme`, `ameisenkoenigin`, `weltenherz`) als Haupt-Bosse der Universen sowie je 1 Unter-Zwischenboss (Sub-Boss) und zerstörbare Umgebungs-Props.
   - Die 3 reinen Zusatz-Universen (`schrott`, `kuchen`, `spule`) werden sauber ausgearbeitet in den Post-MVP-Pool von [`docs/bibel/03-universen.md`](../docs/bibel/03-universen.md) übernommen.
2. **17 Proben & Fabrikator-Rezepte (`src/samples.py`, `V0a`, `V11`, `V20`):**
   - Alle 12 kanonischen Universums-Proben aus der Bibel (2 je Universum: `probe_gallenstein`, `probe_wucherung`, `probe_stempelkissen`, `probe_formular`, `probe_glibberkern`, `probe_brauseperle`, `probe_zuckerkristall`, `probe_ameisenduft`, `probe_leuchtspore`, `probe_plattennadel`, `probe_glockensplitter`, `probe_kerzenstumpf`) plus die 5 allgemeinen Seltenheits-Proben (`probe_knochen`, `probe_aether`, `probe_schatten`, `probe_gold`, `probe_kern`) ergeben `len(SAMPLES) == 17`.
   - Für Seltenheit 3+ im Fabrikator wird zusätzlich `bauplan_splitter` / Freischaltung in `Records.blueprints` unterstützt.
3. **12 Werkstatt-Stationen + Trainings-Attrappe (`src/workshop.py`, `V18`):**
   - Alle 10 Bibel-Stationen mit ihren deutschen Bibel-Schlüsseln (`ws_portal`, `ws_werkbank`, `ws_fabrikator`, `ws_liege`, `ws_haendler`, `ws_zapfhahn`, `ws_automat`, `ws_schiessstand`, `ws_archiv`, `ws_couch`) plus die 2 neuen Stationen (`ws_shredder` Akten-Schredder, `ws_well` Flaschen-Brunnen) und die unsterbliche Trainings-Attrappe werden in [`docs/bibel/07-gegenstaende-und-werkstatt.md`](../docs/bibel/07-gegenstaende-und-werkstatt.md) und `V18` verankert. Englische Aliase (`ws_fabricator`, `ws_trader`, `ws_workbench`, `ws_physik_o_mat`, `ws_archive`) werden über `STATION_ALIASES` abwärtskompatibel aufgelöst.
4. **Böse Ichs, Kaiserin-Handel & 3-stufiges Hauptquartier (`V17`):**
   - Nach den 6 Universen folgt der Endkampf gegen das vom `RunPlan(seed)` gewählte Böse Ich (`boese_kaiserin`, `boese_gute`, `boese_omega`). Zusätzlich können die beiden anderen Bösen Ichs als optionale Begegnungen in den Geheimräumen (`secret`) ab Rang 2 angetroffen werden (inkl. Kaiserin-Handel).
   - Das Portal zum 3-stufigen Hauptquartier der Behörde (`anhoerung` → `boese_ichs` → `ober_cloita`) öffnet sich bei allen 6 `memory_shards` (`erinnerungssplitter`) oder ab 3 `badges` (`dienstausweis`) / 4 Fahndungssternen.
5. **Vereinheitlichte Verhaltensbibliothek, Fraktionen, Events, Challenges & Minispiele:**
   - **Haltungen:** `("hostile", "neutral", "passive", "trader")` (mit Alias-Unterstützung für `peaceful` → `passive`, `territorial` → `neutral`, `shy` → `passive`).
   - **Fähigkeiten (20):** Die 16 Bibel-Fähigkeiten + `aura`, `teleport`, `kamikaze`, `burrow` (und `eat_material` als Alias für `graze`), alle in Bibel Kap. 02 und `V1` dokumentiert.
   - **Fraktionen:** Kanonische Fraktionen (`player`/`spieler`, `native`/`wildnis`, `authority`/`behoerde`, `evil_self`/`boese_ichs`, `trader`/`haendler` + Universums-Unterfraktionen) mit `Grudges`, `hostile()` und `are_hostile()`.
   - **Events & Challenges:** Die 6 Bibel-Universums-Events (`verdauung`, `pruefung`, `brauseregen`, `riesenschritt`, `bass_drop`, `glockenschlag`) + Sekundärereignisse sowie die 6 universumsspezifischen Herausforderungen + 6 Schrein-Prüfungen.
   - **Physik-o-Mat:** Die 4 Bibel-Rätsel (`glas_fuellen`, `vase_retten`, `kerze_zuenden`, `ameisenstrasse`) + die 4 Elementar-Rätsel (`lava_water`, `acid_gold`, `oil_fire`, `electricity_water`).
6. **Strikte 1:1-Zuordnung Karte ↔ Spec-Test & echte S-Größe:**
   - Jede einzelne Aufgabenkarte hat maximal 1–2 Zieldateien, und für jede Karten-ID existiert in `tests/spec/test_phase_<x>.py` mindestens eine eigene Testfunktion `test_<id_klein>_*`, sodass `uv run pytest tests/spec/test_phase_<x>.py -k <id_klein> -q` niemals „no tests collected“ meldet und keine Karte auf spätere Karten einer Sammel-Testfunktion warten muss.
   - Die veralteten Plan-Dateien (`phase-c-universen.md`, `phase-d-werkstatt.md`, `phase-e-bosse.md`, `phase-f-umbenennung.md`) werden entfernt.

## Dependency Graph

```text
Phase 1: Bibel-Erweiterung (docs/bibel/02..09) & Altdateien-Bereinigung
    │
    ▼
Phase 2: Schnittstellen-Verträge (docs/plan/vertraege.md & v00..v21)
    │
    ▼
Phase 3: Atomare Aufgabenkarten (docs/plan/README.md & phase-a..phase-g)
    │
    ▼
Phase 4: Kanonische Angleichung der Code-Gerüste (src/ & tools/)
    │
    ▼
Phase 5: 1:1 Spec-Tests (tests/spec/test_phase_a..g.py) & Gesamtabnahme
```

## Task List

Siehe detaillierte Aufgaben und Checkpoints in [`tasks/todo.md`](todo.md):

### Phase 1: Bibel-Erweiterung & Bereinigung

- [ ] Task 1: Bibel Kap. 02, 03 und 04 um neue Fähigkeiten, Pool-Universen (`schrott`, `kuchen`, `spule`) und Agenten-Rang 4 erweitern
- [ ] Task 2: Bibel Kap. 05, 07, 08 und 09 um die 12 Zusatz-Kreaturen, 5 allgemeinen Proben, 2 Zusatz-Stationen (`ws_shredder`, `ws_well`), Trainings-Attrappe, 4 Elementar-Rätsel und Schrein-Prüfungen erweitern sowie veraltete Plan-Dateien löschen

### Checkpoint: Bibel & Struktur

- [ ] Alle neuen Ideen sind widerspruchsfrei in der Bibel verankert; alte kollidierende Plan-Dateien sind entfernt

### Phase 2: Schnittstellen-Verträge (`V0`–`V23`) synchronisieren

- [ ] Task 3: Master-Index `docs/plan/vertraege.md` sowie `v00`, `v01`, `v05`, `v09` auf 100 % Bibel-Kanon und vollständige Symbol-Abdeckung bringen
- [ ] Task 4: Teilverträge `v11`, `v15`, `v18`, `v21` auf die 6 Bibel-Universen, 17 Proben, 12 Stationen, 6 Zwischengegner und Bibel-Mechaniken umschreiben

### Checkpoint: Verträge

- [ ] Kein einziger Widerspruch mehr zwischen `docs/bibel/`, `vertraege.md` und `v00`–`v21`; jeder von Tests importierte Name steht im Vertrag

### Phase 3: Phasen-Pläne (`A`–`G`) in echte S-Karten (≤ 2 Zieldateien) schneiden

- [ ] Task 5: `docs/plan/README.md`, `phase-a-fundament.md`, `phase-b-grafik.md` und `phase-c-kreaturen.md` aktualisieren und Karten mit >2 Zieldateien teilen
- [ ] Task 6: `docs/plan/phase-d-universen.md`, `phase-e-werkstatt.md`, `phase-f-behoerde-bosse-klonita.md`, `phase-g-abnahme.md` und `docs/intent/atomarer-umsetzungsplan.md` aktualisieren

### Checkpoint: Phasen-Pläne

- [ ] Jede Karte hat max. 1–2 Zieldateien und verweist auf die kanonischen 6 MVP-Universen

### Phase 4: Code-Gerüste (`src/` & `tools/`) auf Bibel-Kanon bringen

- [ ] Task 7: `src/universes/catalog.py`, `src/universes/model.py`, `src/samples.py`, `src/materials.py` und `src/universes/gen/` auf die 6 MVP-Universen und 17 Proben umstellen
- [ ] Task 8: `src/behaviour.py`, `src/factions.py`, `src/pathfind.py`, `src/enemies.py`, `src/weapon_parts.py` und `tools/palette.py` / `tools/sprites*.py` mit den Verträgen synchronisieren
- [ ] Task 9: `src/workshop.py`, `src/traders.py`, `src/fabricator.py`, `src/minigames/`, `src/authority.py`, `src/bosses/`, `src/events.py`, `src/challenges.py`, `src/klonita*.py` und `src/run.py` angleichen

### Checkpoint: Bestands-Suite & Gerüste

- [ ] `uv run pytest --ignore=tests/spec -q` ist 100 % grün (`test_universes.py` prüft `len(UNIVERSES) == 6` erfolgreich)

### Phase 5: 1:1 Spec-Tests (`tests/spec/`) & Gesamtabnahme

- [ ] Task 10: `tests/spec/test_phase_a.py`, `test_phase_b.py` und `test_phase_c.py` auf Bibel-Kanon und strikte 1:1-Testfunktionen pro Karte umstellen
- [ ] Task 11: `tests/spec/test_phase_d.py`, `test_phase_e.py`, `test_phase_f.py` und `test_phase_g.py` auf Bibel-Kanon und strikte 1:1-Testfunktionen pro Karte umstellen
- [ ] Task 12: Vollständige Verifikation aller Einzelkarten-Filter (`-k <id>`), der gesamten Test-Suite (`uv run pytest -q`) und des Linters (`uv run ruff check src tests tools`)

### Checkpoint: Complete

- [ ] Alle Kritikpunkte aus `docs/critique.md` sind behoben, alle Tests (`tests/` und `tests/spec/`) und Ruff-Checks sind grün

## Risks and Mitigations

| Risk | Impact | Mitigation |
| ------ | -------- | ------------ |
| Bestehende Tests (`tests/test_universes.py`, `tests/test_rules.py` etc.) schlagen durch neue Felder/Einträge fehl | High | `UNIVERSES` exakt auf den 6 MVP-Universen der Bibel halten; neue Felder auf Dataclasses nur mit abwärtskompatiblen Defaults am Ende ergänzen |
| Einzelne Karten-IDs werden von `pytest -k <id>` nicht gefunden oder hängen von späteren Karten ab | High | Jede Karte erhält in `tests/spec/test_phase_<x>.py` eine eigene, isoliert ausführbare Funktion `def test_<id_klein>_...()` (keine Sammelnamen wie `test_e10_to_e15_...`) |
| Diskrepanz zwischen deutschen Bibel-Schlüsseln und bestehenden englischen Schlüsseln in `src/` | Med | Explizite Alias-Tabellen (`SAMPLE_ALIASES`, `STATION_ALIASES`, `MODULE_ALIASES`, `PERK_ALIASES`) in Verträgen und Code |

## Open Questions

- Keine offenen Designfragen mehr — alle Entscheidungen wurden im `/grill-me`-Interview geklärt.
