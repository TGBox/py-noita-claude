# Task List: Erweiterung »Cloita Interdimensional: Entfesselte Wissenschaft« (Phasen H–M)

Master-Plan: [`tasks/plan_erweiterung.md`](plan_erweiterung.md) · Bibel: [`docs/erweiterung/`](../docs/erweiterung/00-uebersicht.md)

---

## Phase H: Modul-Mathematik & Deck-Evaluation

### Task H01: `_Draw`-Erweiterung & Deck-Wrapping-Logik

- **Description:** Erweitert die bestehende `_Draw`-Zustandsmaschine in `src/wand.py` um das kontrollierte Deck-Wrapping (`wrapped = True`), Verfolgung von `draw_count` und dem automatischen Modul-Rückgriff auf Slot 0, wenn ein Zieh-Befehl das Deck-Ende erreicht.
- **Acceptance criteria:**
  - `src/wand.py` implementiert in `_Draw.next()` den kontrollierten Einmal-Wrap pro Abzug
  - Modul-Rückgriff greift bei verbleibendem `draw_count` genau einmal pro Abzug auf Slot 0 zurück
  - Tests verifizieren, dass Wrapping Feuerraten und Kaskaden verdoppelt, ohne Endlosschleifen zu erzeugen
- **Files touched:** `src/wand.py`, `tests/spec_erweiterung/test_phase_h.py`

### Task H02: Die Kopier-Protokolle (`proto_alpha` .. `proto_mu`)

- **Description:** Implementiert die 6 Protokoll-Module (`proto_alpha`, `proto_gamma`, `proto_tau`, `proto_omega`, `proto_zeta`, `proto_mu`), die bestehende Module im Deck kopieren, unabhängig von deren verbleibenden Ladungen.
- **Acceptance criteria:**
  - `proto_alpha` kopiert Slot 0; `proto_gamma` kopiert den letzten Slot; `proto_omega` kopiert alle Projektil-Module
  - Das Kopieren verbraucht keine Ladungen des Zielmoduls
- **Files touched:** `src/wand.py`, `src/weapon_parts_expansion.py`

### Task H03: Klon-Splitter (`split_duo` .. `split_dekade`)

- **Description:** Implementiert die Klon-Splitter-Module mit Multiplikator (2×, 3×, 4×, 10×), Schadenskompensation und strikter Rekursionsgrenze (`recursion_depth <= 8`).
- **Acceptance criteria:**
  - Verschachtelte Splitter berechnen die korrekte Kopien-Anzahl
  - Bei Tiefe > 8 bricht die Rekursion ab und emittiert einen Rauch-Partikel sowie Zischen
- **Files touched:** `src/wand.py`, `src/weapon_parts_expansion.py`

### Task H04: Satelliten-Funken & Chaos-Aufsätze

- **Description:** Implementiert Orbit- und Spiegelschwarm-Aufsätze (`mod_satellit`, `mod_larpa_chaos`, `mod_larpa_treffer`, `mod_bumerang_magnet`).
- **Acceptance criteria:**
  - Projektile mit `mod_satellit` spawnen 2 rotierende Miniatur-Geschosse im Orbit
  - Projektile mit `mod_larpa_chaos` spucken im Flug zufällige Geschosskopien ab
- **Files touched:** `src/projectiles.py`, `src/wand.py`

### Task H05: Spezielle Zünder

- **Description:** Ergänzt zeit-, material- und kontaktgesteuerte Zünder (`trig_ablaufdatum`, `trig_feindkontakt_kette`, `trig_stoffwechsel`, `trig_abprall`).
- **Acceptance criteria:**
  - `trig_stoffwechsel` detektiert Kollision mit Flüssigkeitspixeln und löst sofort seine Nutzlast aus
  - `trig_abprall` zündet bis zu 3 Mal bei Wandberührung
- **Files touched:** `src/projectiles.py`, `src/weapon_parts_expansion.py`

---

## Phase I: Alchemie-Labor & Realitäts-Flimmern

### Task I01: Seed-abhängige Rezept-Engine (`schutztonikum`, `gold_vein`)

- **Description:** Implementiert die deterministische Rezept-Berechnung aus `RunPlan.seed` für die beiden seltenen Alchemie-Stoffe unter Einhaltung des 11+10-Materialbudgets.
- **Acceptance criteria:**
  - Gleicher Seed erzeugt immer exakt dieselben 3 Zutaten aus dem aktiven Materialpool
  - Treffen alle 3 Stoffe aufeinander, entsteht `schutztonikum` (Schutzschild + Flux, kein direkter HP-Heiltrank) oder `gold_vein` (Golderz/Partikel)
- **Files touched:** `src/alchemy_advanced.py`, `tests/spec_erweiterung/test_phase_i.py`

### Task I02: Destillierkessel & Verlassener Kesselraum

- **Description:** Generiert den Kesselraum als Geheimraum ab Rang 2 und implementiert den Kessel (`ws_kessel`) mit Trichter-Befüllung (300-Zellen-Kapazität) und Feuer-Aktivierung.
- **Acceptance criteria:**
  - Kessel nimmt Flüssigkeiten aus Kolben (Kapazität 300) an; erhitzen startet 5-Sekunden-Brauprozess
  - Richtige Zutaten werfen fertiges Schutztonikum/Golderz aus; falsche Zutaten erzeugen Rauchfontäne
- **Files touched:** `src/alchemy_advanced.py`, `src/workshop.py`

### Task I03: Dynamische Kolben-Physik & Wurfbomben

- **Description:** Erweitert `Flask` (Kapazität 300) um Druckaufbau bei reagierenden Stoffen und aerosolische Zersplitterung beim Werfen.
- **Acceptance criteria:**
  - Reagierende Flüssigkeiten im Kolben erhöhen den Druckzähler
  - Geworfene Hochdruck-Kolben erzeugen eine Druckwelle mit 60 px Radius
- **Files touched:** `src/flask.py`, `src/alchemy_advanced.py`

### Task I04: Globales Realitäts-Flimmern (Palette-Bound Shift)

- **Description:** Implementiert das Realitäts-Flimmern bei Sporenverzehr oder Kesselüberlastung mit Bildschirmverzerrung und Material-Transmutation, beschränkt auf im Universum geladene Materialien.
- **Acceptance criteria:**
  - 10-sekündiger psychoaktiver Bildschirmeffekt
  - Quellmaterial wird permanent in allen Chunks ins Zielmaterial gewandelt (inklusive 50 % Kolben-Präferenz), ausschließlich innerhalb des aktiven 11+10 Katalogs
  - Mindestens 180 Sekunden Abklingzeit und maximal 5 Shifts pro Durchlauf
- **Files touched:** `src/reality_shift.py`, `src/materials.py`

---

## Phase J: Die 6 Erweiterungs-Universen

### Task J01: Universum `schrott` (Der Große Schrott)

- **Description:** Implementiert Universumsdaten, Materialien (`altmetall`, `roststaub`, `fluessigeisen`, `magnetit`), Regel `rule_magnet`, Kreaturen, Boss Schrottpresse, Event Magnetsturm und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/schrott.py`, `tools/sprites_creatures_expansion.py`

### Task J02: Universum `kuchen` (Die Kuchenkruste)

- **Description:** Implementiert Universumsdaten, Materialien (`biskuit`, `zuckerglasur`, `karamell_kuchen`, `puderzucker`), Regel `rule_hot`, Kreaturen, Boss Hochzeitstorte, Event Karamell-Ausbruch und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/kuchen.py`, `tools/sprites_creatures_expansion.py`

### Task J03: Universum `spule` (Die Summende Spule)

- **Description:** Implementiert Universumsdaten, Materialien (`kupferdraht`, `isolator`, `plasma`, `elektrolyt`), Regel `rule_electric`, Kreaturen, Boss Transformator, Event Kurzschluss und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/spule.py`, `tools/sprites_creatures_expansion.py`

### Task J04: Universum `uhrwerkwueste` (Die Uhrwerkwüste)

- **Description:** Implementiert Universumsdaten, Materialien (`chrono_sand`, `messing_zahnrad`, `fluessig_zeit`, `unruh_fett`), Regel `rule_slowtime`, Kreaturen, Boss Ewiges Pendel, Event Zeitsprung und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/uhrwerkwueste.py`, `tools/sprites_creatures_expansion.py`

### Task J05: Universum `suppenmeer` (Das Endlose Suppenmeer)

- **Description:** Implementiert Universumsdaten, Materialien (`bouillon`, `suppenfett`, `nudel_teig`, `pfefferdampf`), Regel `rule_flooded_soup`, Kreaturen, Boss Kellen-Leviathan, Event Wallendes Kochen und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/suppenmeer.py`, `tools/sprites_creatures_expansion.py`

### Task J06: Universum `freizeitpark` (Freizeitpark Endzeit)

- **Description:** Implementiert Universumsdaten, Materialien (`rost_schiene`, `zuckerwatte_rot`, `helium_gas`, `spiegel_glas`), Regel `rule_momentum`, Kreaturen, Boss Achterbahn-Drache, Event Freie Fahrt und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/freizeitpark.py`, `tools/sprites_creatures_expansion.py`

### Task J07: Sekundäre Zufallsereignisse

- **Description:** Ergänzt `src/events.py` um 8 universumsübergreifende Nebenereignisse: `lieferung`, `pilz_schwarm`, `gold_regen`, `stromausfall`, `flutwelle`, `zucker_rausch`, `wanderzirkus`, `ameisen_karawane`. Sie laufen zusätzlich zum universumseigenen Ereignis aus `V10` (MVP: genau 6 Ereignisse, eines je Universum). Wirkung, Intervall und Warnzeit sind noch offen und werden vor der Umsetzung in der Bibel festgelegt.
- **Herkunft:** Am 2026-11-04 aus dem MVP (alte Karte D12) nach Phase 2 verschoben.
- **Files touched:** `src/events.py`, `docs/bibel/03-universen.md`

### Task J08: Physik-o-Mat-Rätsel „Stromkreis“

- **Description:** Ergänzt `PUZZLE_KEYS` in `src/minigames/physik_o_mat.py` um `"electricity_water"` (Bibel 07): Salzwasser-Leitung zwischen zwei Elektroden schließen. Braucht Strom im Wasser aus `rule_electric` (Universum `spule`, J03).
- **Herkunft:** Am 2026-11-04 aus dem MVP (Karte E08) nach Phase 2 verschoben.
- **Files touched:** `src/minigames/physik_o_mat.py`

---

## Phase K: Klonita-Laborassistenz

### Task K01: Klonita-Ausrüstung an der Liege

- **Description:** Schaltet an der Experimentierliege den Reiter „Assistentinnen-Ausrüstung“ frei (`klonita_schwebe`, `klonita_packesel`, `klonita_feuerwehr`, `klonita_funkenkamm`, `klonita_bioleuchte`) für die unzerstörbare Klonita.
- **Files touched:** `src/klonita_expansion.py`, `src/workshop.py`

### Task K02: Klonitas Rucksack-Erweiterung

- **Description:** Bindet die 2 zusätzlichen Kolben-Slots und 4 Proben-Slots von `klonita_packesel` in die UI und die Schnellwahltasten ein.
- **Files touched:** `src/klonita_expansion.py`, `src/ui.py`

### Task K03: Dynamische Klonita-Dialoge für Alchemie & Welten

- **Description:** Erweitert Klonitas Sprachbibliothek um humorvolle und panische Reaktionen auf kochende Kessel, Golderz, Realitäts-Shifts und die 6 neuen Universen.
- **Files touched:** `src/klonita_dialogue.py`, `docs/bibel/08-ui-und-texte.md`

### Task K04: Parallelwelt-Klonitas & Bekehrungs-Mechanik

- **Description:** Generiert alternative, verwirrte Klon-Versionen in Parallelwelten und ermöglicht die friedliche Befriedung mittels Schutztonikum.
- **Files touched:** `src/klonita_expansion.py`, `src/parallel_worlds.py`

---

## Phase L: Behörden-Großalarm & Kosmische Quest

### Task L01: Werkstatt-Stations-Vandalismus & S.O.K.O. Paragraf

- **Description:** Detektiert Beschädigung oder Sabotage von Werkstatt-Stationen (`ws_kessel`, `ws_liege`, `ws_tv`, `ws_fabrikator`), da Bedrock unzerstörbar bleibt. Löst Großalarm aus und spawnt `soko_paragraf` mit Paragraphen-Schild und Pfändungs-Status.
- **Files touched:** `src/authority_expansion.py`, `src/workshop.py`

### Task L02: Chef-Prüfer Boss-Mechanik

- **Description:** Implementiert den wiederholten Frevel-Boss `chef_pruefer` mit Projektil-Auflösungs-Aura und Schwachpunkt am Rücken.
- **Files touched:** `src/authority_expansion.py`, `src/bosses/chef_pruefer.py`

### Task L03: Wackel-Parallelwelten

- **Description:** Erzeugt an den Kartengrenzen die toxische Bürokratie-Barriere und generiert gespiegelte Welten mit Parallel-Kreaturen.
- **Files touched:** `src/parallel_worlds.py`, `src/world.py`

### Task L04: Kosmische Quest: Die 4 Essenzen & Ur-Perkolator

- **Description:** Platziert die 4 Wachheits-Essenzen in den jeweiligen Universen und implementiert das Ur-Perkolator-Ritual (250+250 Einheiten) auf dem Glockenturm der Abtei.
- **Files touched:** `src/quest_coffee_sun.py`, `src/universes/abtei.py`

### Task L05: Die Schwarze Kaffee-Sonne & Wahres Ende

- **Description:** Implementiert die physikalische Entität der Schwarzen Kaffee-Sonne (Gravitationsstrudel, +120 Flux/s) und das Freischalten des wahren Endes im Archiv.
- **Files touched:** `src/quest_coffee_sun.py`, `src/records.py`

---

## Phase M: Abnahme, Balance & Synergie-Polishing

### Task M01: Modul-Mathematik Stresstest

- **Description:** Verifiziert Klon-Kaskaden, Wrapping und Rekursionsstopp unter Volllast mit automatisierter Test-Matrix.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_balance.py`

### Task M02: Alchemie- und Shift-Verifikation

- **Description:** Prüft Transmutationen aller Universums-Materialien auf 11+10-Budget, Korrektheit und Speicherstand-Integrität.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_alchemy.py`

### Task M03: Performance- und Parallelwelten-Audit

- **Description:** Stellt sicher, dass das Durchqueren toxischer Grenzen keine Frame-Drops oder Speicherlecks verursacht.
- **Files touched:** `tests/spec_erweiterung/test_phase_m_perf.py`

### Task M04: Gesamtabnahme-Suite für Phase H–M

- **Description:** Führt sämtliche neuen Spec-Tests (`tests/spec_erweiterung/`) aus und validiert Code-Konformität (`ruff check`).
- **Files touched:** `tests/spec_erweiterung/`
