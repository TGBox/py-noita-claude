# Implementation Plan: Phase 3 »Absurdität, Zynismus & Multiversums-Satire« (Phasen N–S)

## Overview

Dieses Dokument beschreibt den Implementierungsplan für die **dritte große Entwicklungsstufe (Phase 3)** von *Cloita Interdimensional*. Es schließt direkt an den Abschluss von Phase 2 (`tasks/plan_erweiterung.md`, Phasen H–M) an und setzt die Worldbuilding-, Satire- und Humor-Elemente aus [`docs/phase3_absurditaet/`](../docs/phase3_absurditaet/00-uebersicht.md) um, inspiriert durch das Rick & Morty-Multiversum.

---

## Architecture Decisions

1. **Strikte Drei-Schichten-Entkopplung:**
   - Schicht 1: MVP-Fundament (Phasen A–G, `docs/bibel/`, `tasks/plan.md`)
   - Schicht 2: System-Erweiterung (Phasen H–M, `docs/erweiterung/`, `tasks/plan_erweiterung.md`)
   - Schicht 3: Satire & Worldbuilding (Phasen N–S, `docs/phase3_absurditaet/`, `tasks/plan_phase3.md`)
   - Keine Schicht bricht bestehenden Code oder bestehende Tests.
2. **Eigenständiges Gadget-Subsystem (`src/gadgets.py`):**
   - Signature-Gadgets (Gefälschter Säurebottich, Herr Fleißig, Kaffee-Drohne, Gurken-Flucht, Mikro-Batterie) werden über ein modulares Slot-System (`Player.active_gadget`) verwaltet, getrennt vom Waffen- und Kolbengürtel.
3. **CRT-TV Minispiel-Engine (`src/tv_engine.py`):**
   - Ein dedizierter Videotext- und Scanline-Renderer für die Röhrenglotze (`ws_tv`) mit 12 Kanälen, Promo-Code-Eingabe und temporären Zuschauer-Buffs.
4. **Zitadellen-Hub als separates Groß-Szenario (`src/citadel/`):**
   - Ein interdimensionaler Hub jenseits der regulären Universen mit eigener Palette, Klon-Legebatterie und alternativen Cloitas.
5. **Parasiten-Deduktions-Logik (`src/events_parasites.py`):**
   - Ein soziales Deduktions-Minispiel in der Werkstatt: Dialogbäume prüfen die Tonalität der Erinnerungen (nur positive Erinnerungen = Parasit).
6. **Zynismus- & Meta-Dialog-Matrix (`src/cynical_dialogues.py`):**
   - Kontextsensitive Sprechblasen und Vierte-Wand-Brüche für Cloita & Klonita.

---

## Dependency Graph

```text
Phase M (Abschluss Phase 2)
    │
    ▼
Phase N: Absurde Gadgets & Notfall-Apparate (Säurebottich, Herr Fleißig, Kaffee-Drohne, Gurke)
    │
    ▼
Phase O: Interdimensionale Röhrenglotze (ws_tv, 12 Sender, Werbecodes & Zuschauer-Buffs)
    │
    ▼
Phase P: Die Zitadelle der Cloitas & Klon-Legebatterie (Hub, Fraktionen, Naivitäts-Tarnfeld)
    │
    ▼
Phase Q: Der Rat der Chef-Forscherinnen & die Revoluzzer-Klonita (Putsch, Bosskampf, Freiheit)
    │
    ▼
Phase R: Satire-Universen Teil 1 (Anatomie-Park, Pastell-Hölle, Klonenberg, Talent-Show, Spaghetti, Krawatten)
    │
    ▼
Phase S: Satire-Universen Teil 2 (Sanitärium, Simulation, Kollektiv 404, Whirly-Resort, Quanten, Kater-Bunker)
    │
    ▼
Phase T: Parasiten-Event »Falsche Freunde« & Zynismus-Dialoge (Minispiel, Fallblatt-Statistik)
    │
    ▼
Phase U: Worldbuilding-Gesamtabnahme, Satire-Polishing & Balance
```

---

## Phasen-Übersicht

### Phase N: Absurde Gadgets & Notfall-Apparate

- **N01:** Modulares Gadget-Framework & Tastenbelegung (`src/gadgets.py`)
- **N02:** Der Gefälschte Säurebottich (`gadget_saeurebottich` mit Schnorchel & Fake-Knochen)
- **N03:** Die Büchse des Herrn Fleißig (`gadget_herr_fleissig` mit Hilfsgeist-KI)
- **N04:** Die Kaffee-Drohne & Mikro-Universums-Batterie (`gadget_kaffee_drohne`, `gadget_mikro_batterie`)
- **N05:** Die Gurken-Notfallmutation (`mod_gurken_flucht`, `salzgurke_cloita`)

### Phase O: Interdimensionale Röhrenglotze (`ws_tv`)

- **O01:** Röhrenglotzen-Station & CRT-Scanline-Renderer (`src/tv_engine.py`)
- **O02:** Die 12 Fernsehkanäle mit surrealen Skripten & Sound-Jingles
- **O03:** Teleshopping-Gutscheincodes & Fabrikator-Rabatt-System
- **O04:** Zuschauer-Buffs nach 15 Sekunden Verweildauer

### Phase P: Die Zitadelle der Cloitas & Klon-Legebatterie

- **P01:** Zitadellen-Hub Kartengenerierung & Viertel (`src/citadel/hub.py`)
- **P02:** Alternative Cloita-NPCs (Cowboy-Cloita, Fabrik-Cloita, Gurken-Cloita)
- **P03:** Naivitäts-Tarnfeld-Mechanik (Doppelte Behörden-Jagd bei Klonita-Verlust)
- **P04:** Die Klon-Legebatterie mit Zucht-Bottichen und satirischen Plakaten

### Phase Q: Der Rat der Chef-Forscherinnen & die Revoluzzer-Klonita

- **Q01:** Quest-Reihe »Schatten über der Zitadelle« (Flugblätter, Senatssitzung, Putsch)
- **Q02:** Bosskampf-Phasen der Revoluzzer-Klonita (Koffer, Naivitäts-Inverter, Riss)
- **Q03:** Belohnung: Titan-Koffer-Waffenrahmen & Klon-Befreiung

### Phase R: Sechs handgefertigte Satire-Universen Teil 1

- **R01:** Universum `anatomie_park` (Der Beamten-Park - Peristaltik-Röhren, Dr. Pfortader)
- **R02:** Universum `pastell_hoelle` (Klonitas Pastell-Hölle - Plüsch-Raserei, Ur-Kuscheltier)
- **R03:** Universum `klonenberg_welt` (Das Klonenberg-Desaster - Mutagen-Sud, Gen-Mutationen)
- **R04:** Universum `talent_kosmos` (Der Kosmische Talentwettbewerb - Hype-Check, Orbital-Laser)
- **R05:** Universum `spaghetti_dimension` (Die Teigwaren-Trauerweide - Nudeln aus Verzweiflung)
- **R06:** Universum `krawatten_planet` (Das Krawatten-Imperium - Zeitreise-Terminatoren)

### Phase S: Sechs handgefertigte Satire-Universen Teil 2

- **S01:** Universum `klo_paradies` (Das Heilige Sanitärium - Friedens-Zen & Thron-Vergeltungssystem)
- **S02:** Universum `matroschka_simulation` (Die Simulations-Schachtel - Pop-in-Wände & Zigerion-Admin)
- **S03:** Universum `kollektiv_buerokratie` (Das Büro-Kollektiv 404 - Schwarm-Lebensbalken & Synapsen-Hirn)
- **S04:** Universum `unsterblichkeits_resort` (Das Unsterblichkeits-Resort - Kraftfeld-Kuppel & Schadens-Stapel)
- **S05:** Universum `schroedinger_kammer` (Das Quanten-Scherbenmeer - Geteilte Timeline & Zeit-Polizist)
- **S06:** Universum `kater_bunker` (Der Kater-Bunker - Betrunkene Cloita Saw-Puzzles & Zeitdruck)

### Phase T: Parasiten-Event »Falsche Freunde« & Zynismus-Dialoge

- **T01:** Parasiten-Invasions-Event in der Werkstatt (`src/events_parasites.py`)
- **T02:** Soziales Deduktions-System (Prüfung auf ausschließlich positive Erinnerungen)
- **T03:** Zynische Dialog-Bibliothek für Cloita & existenzielle Klonita-Zeilen
- **T04:** Fallblatt-Statistikanzeige im Pausenraum (`ws_statistik_wand`)

### Phase U: Worldbuilding-Gesamtabnahme & Satire-Polishing

- **U01:** Integrationstest aller Gadgets in Kombination mit Noita-Zaubermathematik
- **U02:** Narrative Konsistenzprüfung aller Zynismus-Dialoge und Vierte-Wand-Brüche
- **U03:** Performance- und Animationsprüfung der Röhrenglotze, der Zitadelle und aller 12 Satire-Biome
- **U04:** Gesamtabnahme Phase 3 (`tests/spec_phase3/`)

---

## Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
| --- | --- |
| Kollision der Gadget-Steuerung mit bisherigen Tasten | Separater Tastatur-Slot `Taste G` mit optischer HUD-Anzeige und Umbelegbarkeit im Optionen-Menü. |
| Textüberflutung durch die 12 TV-Sender | Leicht überspringbar; TV läuft im Pausenraum optional im Hintergrund ohne Zwangs-Pausierung. |
| Zu hoher Schwierigkeitsgrad beim Parasiten-Minispiel | Eindeutige Text-Hinweise in Klonitas Dialogen; Parasiten haben auffällig kitschige Dialog-Muster. |
| Reibung mit Phase 1 & 2 Plänen | Völlig eigenständige Phasen N–S und isolierte Test-Suite `tests/spec_phase3/`. |
