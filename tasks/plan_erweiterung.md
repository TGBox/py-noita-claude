# Implementation Plan: Erweiterung »Cloita Interdimensional: Entfesselte Wissenschaft« (Phasen H–M)

## Overview

Dieses Dokument beschreibt den vollständigen Implementierungsplan für den **zweiten großen Entwicklungs-Lauf (Post-MVP)** des Spiels. Es schließt direkt und nahtlos an den Abschluss von Phase G des MVP-Plans (`tasks/plan.md`, `tasks/todo.md`) an.

Die Spezifikation basiert auf der Erweiterungs-Bibel unter [`docs/erweiterung/`](../docs/erweiterung/00-uebersicht.md) und adaptiert fortgeschrittene Zauberstab- und Alchemie-Mechaniken (Deck-Wrapping in `src/wand.py`, Kopier-Protokolle, Klon-Splitter mit Rekursionsbremse, deterministische Geheim-Alchemie innerhalb der 11+10-Materialgrenze, lokales Realitäts-Flimmern, 6 neue Universen mit Rang 1–3 Skalierung, Klonita-Laborassistenz, Behörden-Großalarm durch Stations-Vandalismus und die Kosmische Kaffee-Sonnen-Quest).

---

## Architecture Decisions

1. **Direkte Erweiterung von `src/wand.py` ohne MVP-Bruch:**
   - Keine parallele Schatten-Architektur (`WandEvaluator` als separater Zweig entfällt). Stattdessen wird die bestehende `_Draw`-Zustandsmaschine in `src/wand.py` um kontrolliertes Deck-Wrapping (`wrapped = True`, Einmal-Durchlauf pro Abzug), Kopier-Protokolle (`proto_alpha` .. `proto_mu`) und Klon-Splitter mit `recursion_depth <= 8` erweitert.
   - Die 6 neuen Universen werden in `src/universes/catalog_expansion.py` registriert und können über einen Konfigurationsschalter (`EXPANSION_ACTIVE = True`) nahtlos in den `RunPlan` gemischt werden.
2. **Rekursionssichere Deck-Evaluierung:**
   - Die Evaluierung arbeitet mit einem strikten Rekursions-Zähler (`max_depth = 8`). Bei Erreichen des Limits greift ein definierter Sicherheits-Cutoff (Puff-Partikel und akustisches Zischen).
3. **Deterministische Seed-Alchemie im 11+10 Material-Budget:**
   - `SecretAlchemyEngine` berechnet die geheimen Dreier-Rezepte für `schutztonikum` (Schutzschild + Flux, kein direkter HP-Heiltrank) und `gold_vein` (Midas-Goldader/Golderz) deterministisch aus `RunPlan.seed`.
   - Rezepte nutzen ausschließlich Stoffe aus der aktiven 8-Bit-Palette (11 Basismaterialien + max. 10 Universums-Materialien).
4. **Lokales Realitäts-Flimmern (Palette-Bound Shifts):**
   - Transmutationen werden im Reaktionsgitter als aktive globale Remapping-Einträge hinterlegt (`material_aliases[source] = target`). Es werden ausschließlich Materialien getauscht, die im aktuellen Universum geladen sind.
5. **Wackel-Parallelwelten & Unzerstörbarer Bedrock:**
   - Bedrock (ID 1) bleibt unzerstörbar (`run.py`). Der Behörden-Großalarm (S.O.K.O. Paragraf) wird durch mutwillige Zerstörung von Werkstatt-Stationen (`ws_kessel`, `ws_liege`, `ws_tv`, `ws_fabrikator`) ausgelöst, nicht durch Graben im Bedrock.
   - Parallelwelten werden über einen horizontalen Chunk-Offset $\pm X_{\text{offset}}$ instanziiert; Kreaturen erhalten eine Skalierungs-Hülle (`ParallelCreatureModifier`).
   - Klonita ist einzigartig, unzerstörbar und steht nach 5 Sekunden wieder auf. Klonita-Upgrades sind persönliche Ausrüstungs-Module.

---

## Dependency Graph

```text
Phase G (Abschluss MVP)
    │
    ▼
Phase H: Modul-Mathematik & Deck-Evaluation (Wand-Wrapping, Kopier-Protokolle, Splitter)
    │
    ▼
Phase I: Alchemie-Labor & Realitäts-Flimmern (Kessel, Schutztonikum, Goldader, Transmutation)
    │
    ▼
Phase J: Die 6 Erweiterungs-Universen (Schrott, Kuchen, Spule, Wüste, Suppe, Kirmes)
    │
    ▼
Phase K: Klonita-Laborassistenz (Ausrüstungs-Upgrades, Rucksack, Dialog-Kaskaden)
    │
    ▼
Phase L: Behörden-Großalarm, Parallelwelten & Kosmische Quest (Kaffee-Sonne)
    │
    ▼
Phase M: Abnahme, Balance & Synergie-Polishing
```

---

## Phasen-Übersicht

### Phase H: Modul-Mathematik & Deck-Evaluation

- **H01:** `_Draw`-Erweiterung in `src/wand.py` (Deck-Wrapping-Logik, `wrapped`-Flag)
- **H02:** Die Kopier-Protokolle Alpha bis Mu (`proto_alpha` .. `proto_mu`)
- **H03:** Klon-Splitter (`split_duo` .. `split_dekade`) mit Rekursionsbremse (`depth <= 8`)
- **H04:** Satelliten-Funken, Orbit- und Chaos-Aufsätze (`mod_satellit`, `mod_larpa_chaos`)
- **H05:** Spezielle Zünder (`trig_ablaufdatum`, `trig_feindkontakt_kette`, `trig_abprall`)

### Phase I: Alchemie-Labor, Destillierkessel & Realitäts-Flimmern

- **I01:** Seed-abhängige Rezept-Engine (`schutztonikum`, `gold_vein` im 11+10 Budget)
- **I02:** Destillierkessel (`ws_kessel`) & Kesselraum-Generierung (300-Zellen-Kapazität)
- **I03:** Dynamische Kolben-Physik (Cocktail-Druck, Wurfbomben, Aerosole für 300 Zellen)
- **I04:** Globales Realitäts-Flimmern (Palette-Bound Shifts auf geladene Materialien)

### Phase J: Die 6 Erweiterungs-Universen (mit Rang 1–3 Skalierung)

- **J01:** Universum `schrott` (Der Große Schrott - `altmetall`, `roststaub`, `fluessigeisen`, `magnetit`)
- **J02:** Universum `kuchen` (Die Kuchenkruste - `biskuit`, `zuckerglasur`, `karamell_kuchen`, `puderzucker`)
- **J03:** Universum `spule` (Die Summende Spule - `kupferdraht`, `isolator`, `plasma`, `elektrolyt`)
- **J04:** Universum `uhrwerkwueste` (Die Uhrwerkwüste - `chrono_sand`, `messing_zahnrad`, `fluessig_zeit`, `unruh_fett`)
- **J05:** Universum `suppenmeer` (Das Endlose Suppenmeer - `bouillon`, `suppenfett`, `nudel_teig`, `pfefferdampf`)
- **J06:** Universum `freizeitpark` (Freizeitpark Endzeit - `rost_schiene`, `zuckerwatte_rot`, `helium_gas`, `spiegel_glas`)
- **J07:** 8 sekundäre Zufallsereignisse (aus dem MVP verschoben; Werte vor Umsetzung in der Bibel festlegen)
- **J08:** Physik-o-Mat-Rätsel „Stromkreis“ (aus dem MVP verschoben, braucht `rule_electric` aus J03)

### Phase K: Klonita-Laborassistenz

- **K01:** Klonita-Ausrüstung an der Werkstatt-Liege (`klonita_schwebe`, `klonita_packesel` etc.)
- **K02:** Klonitas Rucksack-Erweiterung (Phiolen- und Probenverwaltung)
- **K03:** Kontextuelle Dialog-Kaskaden für Kessel, Shifts und neue Welten
- **K04:** Parallelwelt-Begegnungen (Abtrünnige Cloita-Klone, friedliche Befriedung via Tonikum)

### Phase L: Behörden-Großalarm, Wackel-Parallelwelten & Kosmische Quest

- **L01:** Erkennung von Werkstatt-Stations-Vandalismus & S.O.K.O. Paragraf Spawn
- **L02:** Chef-Prüfer Boss-Mechanik (Schildaura, Subpoena-Strahlen, Schwachpunkt Rücken)
- **L03:** Wackel-Parallelwelten (Toxische Grenze, Welt-Kopien, mutierte Feinde)
- **L04:** Kosmische Quest: 4 Wachheits-Essenzen & Ur-Perkolator-Ritual (250+250 Einheiten)
- **L05:** Geburt der Schwarzen Kaffee-Sonne (+120 Flux/s) & Wahres Ende

### Phase M: Abnahme, Balance & Synergie-Polishing

- **M01:** Synergie-Tests für extreme Modul-Kombinationen (Klon-Kaskaden, Wrapping)
- **M02:** Alchemie-Stabilitätstest (11+10-Materialbudget, keine irreversiblen Abstürze)
- **M03:** Performance-Messung bei Parallelwelten-Wechseln und Massen-Partikeln
- **M04:** Audio-/Visuelle Effekte für Schwarze Kaffee-Sonne und Realitäts-Shift
- **M05:** Gesamtabnahme der Erweiterung (`tests/spec_erweiterung/`)

---

## Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
| --- | --- |
| Endlosschleifen bei verschachtelten Klon-Splittern (`split_dekade`) | Strikte Obergrenze `recursion_depth <= 8`; automatischer Abbruch mit Zischen und Qualm-Effekt. |
| Palette-Überlauf bei Realitäts-Shifts | Shifts remappen nur bereits im Universum geladene Materialien (aus der 11+10-Auswahl). |
| Unlösbare Spielstände durch feindseliges Realitäts-Flimmern (z.B. Wasser -> Säure) | Mindestens 3 Minuten Cooldown zwischen Shifts; maximal 5 globale Shifts pro Durchlauf; Schutzkleidung federt Schaden ab. |
| Speicherüberlauf bei Wackel-Parallelwelten | Chunks entfernter Welten werden wie bisher komprimiert und bei Verlassen aus dem RAM entladen. |
| Verwirrung mit dem laufenden MVP-Plan | Phasenbezeichnung H–M; isolierte Dateien unter `docs/erweiterung/` und `tasks/*_erweiterung.md`. MVP bleibt unberührt. |
