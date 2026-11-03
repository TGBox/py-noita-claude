# Implementation Plan: Phase 3 »Absurdität, Zynismus & Multiversums-Satire« (Phasen N–U)

## Overview

Dieses Dokument beschreibt den Implementierungsplan für die **dritte große Entwicklungsstufe (Phase 3)** von *Cloita Interdimensional*. Es schließt direkt an den Abschluss von Phase 2 (`tasks/plan_erweiterung.md`, Phasen H–M) an und setzt die Worldbuilding-, Satire- und Humor-Elemente aus [`docs/phase3_absurditaet/`](../docs/phase3_absurditaet/00-uebersicht.md) als 100 % originäres Sci-Fi-Satire-Multiversum um.

---

## Architecture Decisions

1. **Strikte Drei-Schichten-Entkopplung:**
   - Schicht 1: MVP-Fundament (Phasen A–G, `docs/bibel/`, `tasks/plan.md`)
   - Schicht 2: System-Erweiterung (Phasen H–M, `docs/erweiterung/`, `tasks/plan_erweiterung.md`)
   - Schicht 3: Satire & Worldbuilding (Phasen N–U, `docs/phase3_absurditaet/`, `tasks/plan_phase3.md`)
   - Keine Schicht bricht bestehenden Code oder bestehende Tests.
2. **Eigenständiges Gadget-Subsystem (`src/gadgets.py`):**
   - Signature-Gadgets (Notfall-Tauchkapsel, Büchse des Amts-Imps, Pipetten-Libelle, Interdimensionale Schwungscheibe, Schaben-Notfallmutation) werden über ein modulares Slot-System (`Player.active_gadget`, Standard `Taste G`) verwaltet, getrennt vom Waffen- und Kolbengürtel.
3. **CRT-TV Minispiel-Engine (`src/tv_engine.py`):**
   - Ein dedizierter Videotext- und Scanline-Renderer für die Röhrenglotze (`ws_tv`) mit 12 originären Cloita-Kanälen, Promo-Code-Eingabe (`RABATT-42-GLIBBER`) und temporären Zuschauer-Buffs.
4. **Das Interdimensionale Patentamt als Groß-Szenario (`src/patentamt/`):**
   - Ein interdimensionaler Knotenpunkt (`patentamt_hub`) jenseits der regulären Universen mit eigener Palette, Patent-Archiv und alternativen Cloitas. Klonita ist einzigartig und besitzt ein „Patent-Alibi“ (Naivitäts-Tarnfeld gegen Beamten-Fahndung).
5. **Parasiten-Deduktions-Logik (`src/events_parasites.py`):**
   - Ein soziales Deduktions-Minispiel in der Werkstatt: Dialogbäume prüfen die Tonalität der Erinnerungen von bizarren Figuren wie Thermoskanne Theobald oder Onkel Locher (ausschließlich kitschig-positive Erinnerungen = interdimensionaler Parasit).
6. **Zynismus- & Meta-Dialog-Matrix (`src/cynical_dialogues.py`):**
   - Kontextsensitive Sprechblasen und Vierte-Wand-Brüche für Cloita & Klonita.
7. **Kein Heilungs-Bruch & Keine fremden Medienzitate:**
   - Alle Flüssigkeiten in den 12 Satire-Biomen spenden Schilde, Tempo oder Flux, niemals direkte Lebenspunkte. Sämtliche Figuren und Institutionen sind eigenständige satirische Schöpfungen.

---

## Dependency Graph

```text
Phase M (Abschluss Phase 2)
    │
    ▼
Phase N: Absurde Gadgets & Notfall-Apparate (Tauchkapsel, Amts-Imp, Libelle, Schabe)
    │
    ▼
Phase O: Interdimensionale Röhrenglotze (ws_tv, 12 Sender, Werbecodes & Zuschauer-Buffs)
    │
    ▼
Phase P: Das Interdimensionale Patentamt (Hub, Fraktionen, Patent-Alibi)
    │
    ▼
Phase Q: Die Rebellin Cloita-Null & der Koffer-Staatsstreich (Bosskampf, Titan-Aktentasche)
    │
    ▼
Phase R: Satire-Universen Teil 1 (Beamten-Park, Pastell-Hölle, Klonenberg, Talent-Show, Antrags-Labyrinth, Krawatten)
    │
    ▼
Phase S: Satire-Universen Teil 2 (Sanitärium, Simulation, Kollektiv 404, Resort, Quantenkammer, Kater-Bunker)
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

- **N01:** Modulares Gadget-Framework & Tastenbelegung `Taste G` (`src/gadgets.py`)
- **N02:** Die Notfall-Tauchkapsel (`gadget_tauchkapsel` mit Fake-Schrott & Schleich-Modus)
- **N03:** Die Büchse des Amts-Imps (`gadget_amts_imp` mit Hilfsgeist-KI)
- **N04:** Pipetten-Libelle & Schwungscheiben-Batterie (`gadget_kolben_libelle`, `gadget_schwungscheibe`)
- **N05:** Die Schaben-Notfallmutation (`mod_schaben_flucht`, `kuechenschabe_cloita`)

### Phase O: Interdimensionale Röhrenglotze (`ws_tv`)

- **O01:** Röhrenglotzen-Station & CRT-Scanline-Renderer (`src/tv_engine.py`)
- **O02:** Die 12 originären Cloita-Fernsehkanäle mit surrealen Skripten & Sound-Jingles
- **O03:** Teleshopping-Gutscheincodes (`RABATT-42-GLIBBER`) & Fabrikator-Rabatt-System
- **O04:** Zuschauer-Buffs nach 15 Sekunden Verweildauer

### Phase P: Das Interdimensionale Patentamt

- **P01:** Patentamt-Hub Kartengenerierung & Sektoren (`src/patentamt/hub.py`)
- **P02:** Alternative Cloita-NPCs (Bürokratie-Cloita, Quanten-Cloita, Steampunk-Cloita)
- **P03:** Patent-Alibi-Mechanik (Klonitas Tarnfeld halbiert Fahndungs-Zuwachs)
- **P04:** Das Endlose Patent-Archiv mit Aktenbergen und satirischen Bekanntmachungen

### Phase Q: Die Rebellin Cloita-Null & der Koffer-Staatsstreich

- **Q01:** Quest-Reihe »Schatten über dem Patentamt« (Flugblätter, Senatssitzung, Putsch)
- **Q02:** Bosskampf: Die Rebellin Cloita-Null (Aktentaschen-Raketen, Paragraphen-Inverter, Dimensional-Riss)
- **Q03:** Belohnung: Titan-Aktentasche (`waffe_patent_koffer`) & Befriedung des Amts

### Phase R: Sechs handgefertigte Satire-Universen Teil 1

- **R01:** Universum `anatomie_park` (Der Beamten-Park - Rohrpost-Röhren, Dr. Pfortader)
- **R02:** Universum `pastell_hoelle` (Klonitas Pastell-Hölle - Plüsch-Raserei, Erdbeer-Schildbuff, Ur-Kuscheltier)
- **R03:** Universum `klonenberg_welt` (Das Klonenberg-Desaster - Mutagen-Sud, Gen-Mutationen, Klonenberg-Monstrum)
- **R04:** Universum `talent_kosmos` (Der Kosmische Talentwettbewerb - Hype-Check, Orbital-Laser)
- **R05:** Universum `antrags_labyrinth` (Das Pneumatische Antrags-Labyrinth - Formular-Wände, Toner-Nebel, Minotaurus)
- **R06:** Universum `krawatten_planet` (Das Krawatten-Imperium - Panzer-Seide, Zeitreise-Terminatoren)

### Phase S: Sechs handgefertigte Satire-Universen Teil 2

- **S01:** Universum `klo_paradies` (Das Heilige Sanitärium - Friedens-Zen, Schild-Quellwasser, Thron-Vergeltungssystem)
- **S02:** Universum `matroschka_simulation` (Die Simulations-Schachtel - Wireframe-Wände, Glitch-Pixel, Zigerion-Admin)
- **S03:** Universum `kollektiv_buerokratie` (Das Büro-Kollektiv 404 - Schwarm-Lebensbalken, Synapsen-Gehirn)
- **S04:** Universum `unsterblichkeits_resort` (Das Unsterblichkeits-Resort - Kraftfeld-Kuppel, Schadens-Stapel)
- **S05:** Universum `schroedinger_kammer` (Das Quanten-Scherbenmeer - Quanten-Phasenechos, Zeit-Polizist)
- **S06:** Universum `kater_bunker` (Der Kater-Bunker - Betrunkene-Cloita-Puzzles, Zeitdruck, Giftgas)

### Phase T: Parasiten-Event »Falsche Freunde« & Zynismus-Dialoge

- **T01:** Parasiten-Invasions-Event in der Werkstatt (`src/events_parasites.py`)
- **T02:** Soziales Deduktions-System (Prüfung auf ausschließlich positive Erinnerungen)
- **T03:** Zynische Dialog-Bibliothek für Cloita & existenzielle Klonita-Zeilen
- **T04:** Fallblatt-Statistikanzeige im Pausenraum (`ws_statistik_wand`, Cloita-Schäden, Kaffee-Verbrauch, Strafzettel)

### Phase U: Worldbuilding-Gesamtabnahme & Satire-Polishing

- **U01:** Integrationstest aller Gadgets in Kombination mit Noita-Zaubermathematik
- **U02:** Narrative Konsistenzprüfung aller Zynismus-Dialoge und Vierte-Wand-Brüche
- **U03:** Performance- und Animationsprüfung der Röhrenglotze, des Patentamts und aller 12 Satire-Biome
- **U04:** Gesamtabnahme Phase 3 (`tests/spec_phase3/`)

---

## Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
| --- | --- |
| Kollision der Gadget-Steuerung mit bisherigen Tasten | Separater Tastatur-Slot `Taste G` mit optischer HUD-Anzeige und Umbelegbarkeit im Optionen-Menü. |
| Textüberflutung durch die 12 TV-Sender | Leicht überspringbar; TV läuft im Pausenraum optional im Hintergrund ohne Zwangs-Pausierung. |
| Zu hoher Schwierigkeitsgrad beim Parasiten-Minispiel | Eindeutige Text-Hinweise in Klonitas Dialogen; Parasiten haben auffällig kitschige Dialog-Muster. |
| Reibung mit Phase 1 & 2 Plänen | Völlig eigenständige Phasen N–U und isolierte Test-Suite `tests/spec_phase3/`. MVP bleibt unberührt. |
