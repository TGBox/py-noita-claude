# Task List: Erweiterung »Cloita Interdimensional: Entfesselte Wissenschaft« (Phasen H–M)

Master-Plan: [`tasks/plan_erweiterung.md`](plan_erweiterung.md) · Bibel: [`docs/erweiterung/`](../docs/erweiterung/00-uebersicht.md)

---

## Phase H: Modul-Mathematik & Deck-Evaluation

### Task H01: `CastContext` & Deck-Wrapping-Logik

- **Description:** Implementiert den modularen `WandEvaluator` mit `CastContext`, Verfolgung von `deck`, `hand`, `discard`, `draw_count` und dem automatischen Modul-Rückgriff (`wrap_occurred`), wenn ein Zieh-Befehl das Deck-Ende erreicht.
- **Acceptance criteria:**
  - `src/wand_evaluator.py` implementiert `evaluate_cast(wand, trigger_index=0) -> list[CastGroup]`
  - Modul-Rückgriff greift bei verbleibendem `draw_count` genau einmal pro Abzug auf Slot 0 zurück
  - Tests verifizieren, dass Wrapping die Feuerrate verdoppelt und keine Endlosschleife erzeugt
- **Files touched:** `src/wand_evaluator.py`, `tests/spec_erweiterung/test_phase_h.py`

### Task H02: Die Kopier-Protokolle (`proto_alpha` .. `proto_mu`)

- **Description:** Implementiert die 6 Protokoll-Module (`proto_alpha`, `proto_gamma`, `proto_tau`, `proto_omega`, `proto_zeta`, `proto_mu`), die bestehende Module im Deck kopieren, unabhängig von deren verbleibenden Ladungen.
- **Acceptance criteria:**
  - `proto_alpha` kopiert Slot 0; `proto_gamma` kopiert den letzten Slot; `proto_omega` kopiert alle Module
  - Das Kopieren verbraucht keine Ladungen des Zielmoduls
- **Files touched:** `src/wand_evaluator.py`, `src/weapon_parts_expansion.py`

### Task H03: Klon-Splitter (`split_duo` .. `split_dekade`)

- **Description:** Implementiert die Klon-Splitter-Module mit Multiplikator (2×, 3×, 4×, 10×), Schadenskompensation und strikter Rekursionsgrenze (`recursion_depth <= 8`).
- **Acceptance criteria:**
  - Verschachtelte Splitter berechnen die korrekte Kopien-Anzahl
  - Bei Tiefe > 8 bricht die Rekursion ab und emittiert einen Rauch-Partikel
- **Files touched:** `src/wand_evaluator.py`, `src/weapon_parts_expansion.py`

### Task H04: Satelliten-Funken & Chaos-Aufsätze

- **Description:** Implementiert Orbit- und Spiegelschwarm-Aufsätze (`mod_satellit`, `mod_larpa_chaos`, `mod_larpa_treffer`, `mod_bumerang_magnet`).
- **Acceptance criteria:**
  - Projektile mit `mod_satellit` spawnen 2 rotierende Miniatur-Geschosse im Orbit
  - Projektile mit `mod_larpa_chaos` spucken im Flug zufällige Geschosskopien ab
- **Files touched:** `src/projectiles.py`, `src/wand_evaluator.py`

### Task H05: Spezielle Zünder

- **Description:** Ergänzt zeit-, material- und kontaktgesteuerte Zünder (`trig_ablaufdatum`, `trig_feindkontakt_kette`, `trig_stoffwechsel`, `trig_abprall`).
- **Acceptance criteria:**
  - `trig_stoffwechsel` detektiert Kollision mit Flüssigkeitspixeln und löst sofort seine Nutzlast aus
  - `trig_abprall` zündet bis zu 3 Mal bei Wandberührung
- **Files touched:** `src/projectiles.py`, `src/weapon_parts_expansion.py`

---

## Phase I: Alchemie-Labor & Realitäts-Flimmern

### Task I01: Seed-abhängige Rezept-Engine (`wundertonikum`, `midas_schmelze`)

- **Description:** Implementiert die deterministische Rezept-Berechnung aus `RunPlan.seed` für die beiden seltenen Elixiere.
- **Acceptance criteria:**
  - Gleicher Seed erzeugt immer exakt dieselben 3 Zutaten
  - Treffen alle 3 Stoffe aufeinander, entsteht Wundertonikum oder Midas-Schmelze
- **Files touched:** `src/alchemy_advanced.py`, `tests/spec_erweiterung/test_phase_i.py`

### Task I02: Destillierkessel & Verlassener Kesselraum

- **Description:** Generiert den Kesselraum als Geheimraum ab Rang 2 und implementiert den Kessel (`ws_kessel`) mit Trichter-Befüllung und Feuer-Aktivierung.
- **Acceptance criteria:**
  - Kessel nimmt Flüssigkeiten aus Kolben an; erhitzen startet 5-Sekunden-Brauprozess
  - Richtige Zutaten werfen fertiges Wundertonikum/Midas aus; falsche Zutaten erzeugen Rauchfontäne
- **Files touched:** `src/alchemy_advanced.py`, `src/workshop.py`

### Task I03: Dynamische Kolben-Physik & Wurfbomben

- **Description:** Erweitert `Flask` um Druckaufbau bei reagierenden Stoffen und aerosolische Zersplitterung beim Werfen.
- **Acceptance criteria:**
  - Reagierende Flüssigkeiten im Kolben erhöhen den Druckzähler
  - Geworfene Hochdruck-Kolben erzeugen eine Druckwelle mit 60 px Radius
- **Files touched:** `src/flask.py`, `src/alchemy_advanced.py`

### Task I04: Globales Realitäts-Flimmern (Fungal Shift)

- **Description:** Implementiert das Realitäts-Flimmern bei Sporenverzehr oder Kesselüberlastung mit Bildschirmverzerrung und globaler Material-Transmutation.
- **Acceptance criteria:**
  - 10-sekündiger psychoaktiver Bildschirmeffekt
  - Quellmaterial wird permanent in allen Chunks ins Zielmaterial gewandelt (inklusive 50 % Kolben-Präferenz)
  - Mindestens 180 Sekunden Abklingzeit und maximal 5 Shifts pro Durchlauf
- **Files touched:** `src/reality_shift.py`, `src/materials.py`

---

## Phase J: Die 6 Erweiterungs-Universen

### Task J01: Universum `schrott` (Der Große Schrott)

- **Description:** Implementiert Universumsdaten, Materialien (`schrott`, `roststaub`, `fluessigeisen`, `magnetit`), Regel `rule_magnet`, Kreaturen, Boss Schrottpresse und Event Magnetsturm.
- **Files touched:** `src/universes/schrott.py`, `tools/sprites_creatures_expansion.py`

### Task J02: Universum `kuchen` (Die Kuchenkruste)

- **Description:** Implementiert Universumsdaten, Materialien (`biskuit`, `zuckerglasur`, `karamell`, `puderzucker`), Regel `rule_hot`, Kreaturen, Boss Hochzeitstorte und Event Karamell-Ausbruch.
- **Files touched:** `src/universes/kuchen.py`, `tools/sprites_creatures_expansion.py`

### Task J03: Universum `spule` (Die Summende Spule)

- **Description:** Implementiert Universumsdaten, Materialien (`kupfer`, `isolator`, `plasma`, `elektrolyt`), Regel `rule_electric`, Kreaturen, Boss Transformator und Event Kurzschluss.
- **Files touched:** `src/universes/spule.py`, `tools/sprites_creatures_expansion.py`

### Task J04: Universum `uhrwerkwueste` (Die Uhrwerkwüste)

- **Description:** Implementiert Universumsdaten, Materialien (`chrono_sand`, `messing`, `fluessig_zeit`, `unruh_fett`), Regel `rule_slowtime`, Kreaturen, Boss Ewiges Pendel und Event Zeitsprung.
- **Files touched:** `src/universes/uhrwerkwueste.py`, `tools/sprites_creatures_expansion.py`

### Task J05: Universum `suppenmeer` (Das Endlose Suppenmeer)

- **Description:** Implementiert Universumsdaten, Materialien (`bouillon`, `suppenfett`, `nudel_teig`, `pfefferdampf`), Regel `rule_flooded_soup`, Kreaturen, Boss Kellen-Leviathan und Event Wallendes Kochen.
- **Files touched:** `src/universes/suppenmeer.py`, `tools/sprites_creatures_expansion.py`

### Task J06: Universum `freizeitpark` (Freizeitpark Endzeit)

- **Description:** Implementiert Universumsdaten, Materialien (`rost_schiene`, `zuckerwatte_rot`, `helium_gas`, `spiegel_glas`), Regel `rule_momentum`, Kreaturen, Boss Achterbahn-Drache und Event Freie Fahrt.
- **Files touched:** `src/universes/freizeitpark.py`, `tools/sprites_creatures_expansion.py`

---

## Phase K: Klonita-Laborassistenz

### Task K01: Klonita-Selbstexperimente an der Liege

- **Description:** Schaltet an der Experimentierliege den Reiter „Assistentinnen-Modifikation“ frei (`klonita_schwebe`, `klonita_packesel`, `klonita_feuerwehr`, `klonita_funkenkamm`, `klonita_bioleuchte`).
- **Files touched:** `src/klonita_expansion.py`, `src/workshop.py`

### Task K02: Klonitas Rucksack-Erweiterung

- **Description:** Bindet die 2 zusätzlichen Kolben-Slots und 4 Proben-Slots von `klonita_packesel` in die UI und die Schnellwahltasten ein.
- **Files touched:** `src/klonita_expansion.py`, `src/ui.py`

### Task K03: Dynamische Klonita-Dialoge für Alchemie & Welten

- **Description:** Erweitert Klonitas Sprachbibliothek um Reaktionen auf kochende Kessel, Midas-Gold, Realitäts-Shifts und die 6 neuen Universen.
- **Files touched:** `src/klonita_dialogue.py`, `docs/bibel/08-ui-und-texte.md`

### Task K04: Parallelwelt-Klonitas & Bekehrungs-Mechanik

- **Description:** Generiert alternative Klonitas in Parallelwelten und ermöglicht die friedliche Heilung mittels Wundertonikum.
- **Files touched:** `src/klonita_expansion.py`, `src/parallel_worlds.py`

---

## Phase L: Behörden-Großalarm & Kosmische Quest

### Task L01: Werkstatt-Vandalismus & S.O.K.O. Paragraf

- **Description:** Detektiert Beschädigung von Werkstattwänden, löst akustischen und visuellen Alarm aus und spawnt `soko_paragraf` mit Paragraphen-Schild und Pfändungs-Status.
- **Files touched:** `src/authority_expansion.py`, `src/workshop.py`

### Task L02: Chef-Prüfer Boss-Mechanik

- **Description:** Implementiert den wiederholten Frevel-Boss `chef_pruefer` mit Projektil-Auflösungs-Aura und Schwachpunkt am Rücken.
- **Files touched:** `src/authority_expansion.py`, `src/bosses/chef_pruefer.py`

### Task L03: Wackel-Parallelwelten

- **Description:** Erzeugt an den Kartengrenzen die toxische Bürokratie-Barriere und generiert gespiegelte Welten mit Parallel-Kreaturen.
- **Files touched:** `src/parallel_worlds.py`, `src/world.py`

### Task L04: Kosmische Quest: Die 4 Essenzen & Ur-Perkolator

- **Description:** Platziert die 4 Wachheits-Essenzen in den jeweiligen Universen und implementiert den Ur-Perkolator auf dem Glockenturm der Abtei.
- **Files touched:** `src/quest_coffee_sun.py`, `src/universes/abtei.py`

### Task L05: Die Schwarze Kaffee-Sonne & Wahres Ende

- **Description:** Implementiert die physikalische Entität der Schwarzen Kaffee-Sonne (Gravitationsstrudel, unendlicher Flux) und das Freischalten des wahren Endes im Archiv.
- **Files touched:** `src/quest_coffee_sun.py`, `src/records.py`

---

## Phase M: Abnahme, Balance & Synergie-Polishing

### Task M01: Modul-Mathematik Stresstest

- **Description:** Verifiziert Klon-Kaskaden, Wrapping und Rekursionsstopp unter Volllast mit automatisierter Test-Matrix.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_balance.py`

### Task M02: Alchemie- und Shift-Verifikation

- **Description:** Prüft Transmutationen aller 12 Universums-Materialien auf Korrektheit und Speicherstand-Integrität.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_alchemy.py`

### Task M03: Performance- und Parallelwelten-Audit

- **Description:** Stellt sicher, dass das Durchqueren toxischer Grenzen keine Frame-Drops oder Speicherlecks verursacht.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_perf.py`

### Task M04: Gesamtabnahme-Suite für Phase H–M

- **Description:** Führt sämtliche neuen Spec-Tests (`tests/spec_erweiterung/`) aus und validiert Code-Konformität (`ruff check`).
- **Files touched:** `tests/spec_erweiterung/`
