# Implementation Plan: Erweiterung »Cloita Interdimensional: Entfesselte Wissenschaft« (Phasen H–M)

## Overview

Dieses Dokument beschreibt den vollständigen Implementierungsplan für den **zweiten großen Entwicklungs-Lauf (Post-MVP)** des Spiels. Es schließt direkt und nahtlos an den Abschluss von Phase G des MVP-Plans (`tasks/plan.md`, `tasks/todo.md`) an.

Die Spezifikation basiert auf der Erweiterungs-Bibel unter [`docs/erweiterung/`](../docs/erweiterung/00-uebersicht.md) und adaptiert fortgeschrittene Noita-Mechaniken (Deck-Wrapping, Kopier-Protokolle, Klon-Splitter, Geheim-Alchemie, Realitäts-Flimmern, 6 neue Universen, Klonita-Laborassistenz, Behörden-Großalarm und die Kosmische Kaffee-Sonnen-Quest).

---

## Architecture Decisions

1. **Vollständige Entkopplung vom MVP-Fundament:**
   - Keine bestehende Klasse des MVP wird überschrieben. Das Modulsystem wird über einen modularen `WandEvaluator` (`src/wand_evaluator.py`) erweitert, der für Standardwaffen abwärtskompatibel bleibt.
   - Die 6 neuen Universen werden in `src/universes/catalog_expansion.py` registriert und können über einen Konfigurationsschalter (`EXPANSION_ACTIVE = True`) nahtlos in den `RunPlan` gemischt werden.
2. **Rekursionssichere Deck-Evaluierung:**
   - Der `WandEvaluator` arbeitet mit einem expliziten `CastContext` und einem strikten Rekursions-Zähler (`max_depth = 8`). Bei Überlastung greift ein definierter Sicherheits-Cutoff (kleines Qualmwölkchen + akustischer Piepton).
3. **Deterministische Seed-Alchemie:**
   - `SecretAlchemyEngine` berechnet die geheimen Dreier-Rezepte für `wundertonikum` und `midas_schmelze` deterministisch aus `RunPlan.seed`.
4. **Globale Material-Transmutationen (Realitäts-Flimmern):**
   - Transmutationen werden im `WorldEngine`-Rust-Backend bzw. im Material-Reaktionsgitter als aktive globale Remapping-Einträge hinterlegt (`material_aliases[source] = target`).
5. **Wackel-Parallelwelten als Koordinaten-Offset:**
   - Parallelwelten werden prozedural über einen horizontalen Chunk-Offset $\pm X_{\text{offset}}$ instanziiert; Kreaturen erhalten eine Skalierungs-Hülle (`ParallelCreatureModifier`).

---

## Dependency Graph

```text
Phase G (Abschluss MVP)
    │
    ▼
Phase H: Modul-Mathematik & Deck-Evaluation (Wand-Wrapping, Kopier-Protokolle, Splitter)
    │
    ▼
Phase I: Alchemie-Labor & Realitäts-Flimmern (Kessel, Geheimrezepte, Transmutation)
    │
    ▼
Phase J: Die 6 Erweiterungs-Universen (Schrott, Kuchen, Spule, Wüste, Suppe, Kirmes)
    │
    ▼
Phase K: Klonita-Laborassistenz (Selbstexperimente, Rucksack, Reaktionskaskaden)
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

- **H01:** `CastContext` & Deck-Wrapping-Logik (`src/wand_evaluator.py`)
- **H02:** Die Kopier-Protokolle Alpha bis Mu (`proto_alpha` .. `proto_mu`)
- **H03:** Klon-Splitter (`split_duo` .. `split_dekade`) mit Rekursionsbremse
- **H04:** Satelliten-Funken, Orbit- und Chaos-Aufsätze (`mod_satellit`, `mod_larpa_chaos`)
- **H05:** Spezielle Zünder (`trig_ablaufdatum`, `trig_feindkontakt_kette`, `trig_abprall`)

### Phase I: Alchemie-Labor, Destillierkessel & Realitäts-Flimmern

- **I01:** Seed-abhängige Rezept-Engine (`wundertonikum`, `midas_schmelze`)
- **I02:** Destillierkessel (`ws_kessel`) & Geheimraum-Generierung (`cauldron_room`)
- **I03:** Dynamische Kolben-Physik (Cocktail-Druck, Wurfbomben, Aerosole)
- **I04:** Globales Realitäts-Flimmern (Fungal Shifts / Transmutations-Gitter)

### Phase J: Die 6 Erweiterungs-Universen

- **J01:** Universum `schrott` (Der Große Schrott - Magnetismus, Roststaub, Schrottpresse)
- **J02:** Universum `kuchen` (Die Kuchenkruste - Hitze, Biskuit, Hochzeitstorte)
- **J03:** Universum `spule` (Die Summende Spule - Hochspannung, Elektrolyt, Transformator)
- **J04:** Universum `uhrwerkwueste` (Die Uhrwerkwüste - Chrono-Sand, Flüssigzeit, Ewiges Pendel)
- **J05:** Universum `suppenmeer` (Das Endlose Suppenmeer - Bouillon, Suppenfett, Kellen-Leviathan)
- **J06:** Universum `freizeitpark` (Freizeitpark Endzeit - Schienen, Zuckerwatte, Achterbahndrache)

### Phase K: Klonita-Laborassistenz

- **K01:** Klonita-Upgrades an der Werkstatt-Liege (`klonita_schwebe`, `klonita_packesel` etc.)
- **K02:** Klonitas Rucksack-Erweiterung (Phiolen- und Probenverwaltung)
- **K03:** Kontextuelle Dialog-Kaskaden für Kessel, Shifts und neue Welten
- **K04:** Parallelwelt-Klonitas und friedliche Bekehrung

### Phase L: Behörden-Großalarm, Wackel-Parallelwelten & Kosmische Quest

- **L01:** Erkennung von Werkstatt-Vandalismus & S.O.K.O. Paragraf Spawn
- **L02:** Chef-Prüfer Boss-Mechanik (Schildaura, Subpoena-Strahlen)
- **L03:** Wackel-Parallelwelten (Toxische Grenze, Welt-Kopien, mutierte Feinde)
- **L04:** Kosmische Quest: 4 Wachheits-Essenzen & Ur-Perkolator-Ritual
- **L05:** Geburt der Schwarzen Kaffee-Sonne & Wahres Ende

### Phase M: Abnahme, Balance & Synergie-Polishing

- **M01:** Synergie-Tests für extreme Modul-Kombinationen (Klon-Kaskaden, Wrapping)
- **M02:** Alchemie-Stabilitätstest (keine irreversiblen Game-Breaking Loops)
- **M03:** Performance-Messung bei Parallelwelten-Wechseln und Massen-Partikeln
- **M04:** Audio-/Visuelle Effekte für Schwarze Kaffee-Sonne und Realitäts-Shift
- **M05:** Gesamtabnahme der Erweiterung (`tests/spec_erweiterung/`)

---

## Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
| --- | --- |
| Endlosschleifen bei verschachtelten Klon-Splittern (`split_dekade`) | Strikte Obergrenze `recursion_depth <= 8`; automatischer Abbruch mit Qualm-Effekt. |
| Unlösbare Spielstände durch feindseliges Realitäts-Flimmern (z.B. Wasser -> Säure) | Mindestens 3 Minuten Cooldown zwischen Shifts; maximal 5 globale Shifts pro Durchlauf; Schutzkleidung rettet. |
| Speicherüberlauf bei Wackel-Parallelwelten | Chunks entfernter Welten werden wie bisher komprimiert und bei Verlassen aus dem RAM entladen. |
| Verwirrung mit dem laufenden MVP-Plan | Phasenbezeichnung H–M; isolierte Dateien unter `docs/erweiterung/` und `tasks/*_erweiterung.md`. |
