# Task List: Phase 3 »Absurdität, Zynismus & Multiversums-Satire« (Phasen N–U)

Master-Plan: [`tasks/plan_phase3.md`](plan_phase3.md) · Bibel: [`docs/phase3_absurditaet/`](../docs/phase3_absurditaet/00-uebersicht.md)

---

## Phase N: Absurde Gadgets & Notfall-Apparate

### Task N01: Modulares Gadget-Framework & Tastenbelegung

- **Description:** Implementiert das `Gadget`-Basissystem in `src/gadgets.py` mit `Player.active_gadget`, Cooldown-/Ladungsverwaltung, HUD-Icon und Tastenzuweisung (Standard `Taste G`).
- **Acceptance criteria:**
  - `src/gadgets.py` definiert `class Gadget`, `GadgetManager` und `GadgetState`
  - Gadgets können ausgerüstet, gewechselt und per Tastendruck aktiviert werden
- **Files touched:** `src/gadgets.py`, `tests/spec_phase3/test_phase_n.py`

### Task N02: Die Notfall-Tauchkapsel (`gadget_tauchkapsel`)

- **Description:** Implementiert die Tauchkapsel mit Fake-Schrott-Partikeln, Feind-Aggro-Reset und Schleich-Modus mit kritischem Hinterhaltsschaden.
- **Acceptance criteria:**
  - Aktivierung spawnt optische Kapsel mit treibenden Schrott- und Schrauben-Pixeln
  - Feinde brechen Verfolgung ab und wechseln in IDLE-Zustand
  - Angriff aus der Kapsel verursacht garantierten kritischen Treffer (+200 %)
- **Files touched:** `src/gadgets.py`, `src/player.py`

### Task N03: Die Büchse des Amts-Imps (`gadget_amts_imp`)

- **Description:** Implementiert den kleinen koboldartigen Beamten-Geist mit bürokratischer Sprachausgabe, Sammel-, Schalter- und Schutzschild-Verhalten sowie der Existenz-Verpuffung bei erledigtem Antrag.
- **Acceptance criteria:**
  - Spawnt `AmtsImp`-Entität mit winziger Aktentasche und Brille
  - Erledigt die nächstgelegene Aufgabe (Gold sammeln, Hebel drücken oder Schutzschild sein)
  - Löst sich bei Aufgabenerfüllung in Formularschnipsel auf; eskaliert nach 25 Sekunden Kampf in bürokratische Panik
- **Files touched:** `src/gadgets.py`, `src/behaviour.py`

### Task N04: Pipetten-Libelle & Schwungscheiben-Batterie

- **Description:** Implementiert die fliegende Kolben-Libelle (`gadget_kolben_libelle`) und die kinetische Schwungscheiben-Batterie (`gadget_schwungscheibe`).
- **Acceptance criteria:**
  - Pipetten-Libelle holt selbstständig Flüssigkeiten und reicht Kolben
  - Schwungscheibe spendet +60 Flux/s; Überhitzung alle 120 s erfordert Abkühlung oder Klonita-Zuspruch
- **Files touched:** `src/gadgets.py`, `src/flask.py`

### Task N05: Die Schaben-Notfallmutation (`mod_schaben_flucht`)

- **Description:** Implementiert das Überlebensmodul, das Cloita bei lethalem Schaden in die winzige Küchenschabe verwandelt.
- **Acceptance criteria:**
  - Bei LP <= 0 verwandelt sich Cloita in `kuechenschabe_cloita` mit Fühlern und Chitin-Panzer
  - Schabe kann durch 2-Pixel-Schlitze kriechen und Chitin-Stacheln verschießen
  - Erreichen des Werkstatt-Portals stellt die menschliche Form vollständig wieder her
- **Files touched:** `src/gadgets.py`, `src/player.py`

---

## Phase O: Interdimensionale Röhrenglotze (`ws_tv`)

### Task O01: CRT-Scanline-Engine & Röhrenfernseher-Station

- **Description:** Implementiert die Station `ws_tv` in der Werkstatt mit Röhren-Scanlines, Krümmungseffekt und Kanalwahl-Interaktion.
- **Acceptance criteria:**
  - `src/tv_engine.py` rendert ein stimmungsvolles 80er-Jahre-CRT-Overlay
  - Umschalten zwischen Kanälen 1 bis 12 mit Soundeffekt
- **Files touched:** `src/tv_engine.py`, `src/workshop.py`

### Task O02: Die 12 Fernsehkanäle mit originären Cloita-Skripten

- **Description:** Integriert die 12 originären Fernsehsendungen (Plümpel-Herstellung, Das Interdimensionale Kaffeekränzchen, Ameisen-Müller, Kochen mit Lava etc.) als animierte Text-/Pixel-Sequenzen.
- **Acceptance criteria:**
  - Alle 12 Kanäle aus Bibel Kap. 02 sind abspielbar und besitzen eigene Farb-/Tonmuster
- **Files touched:** `src/tv_engine.py`, `src/tv_channels.py`

### Task O03: Teleshopping-Gutscheincodes & Fabrikator-Rabatt

- **Description:** Implementiert das Einlösen von Werbecodes aus Kanal 5 am Fabrikator (`RABATT-42-GLIBBER`).
- **Acceptance criteria:**
  - Eingabe des Codes senkt die Baukosten des nächsten Waffenbaus um 50 %
- **Files touched:** `src/tv_engine.py`, `src/fabricator.py`

### Task O04: Zuschauer-Buffs nach 15 Sekunden Verweildauer

- **Description:** Verleiht der Spielerin nach mindestens 15 Sekunden Zuschauen je nach Kanal temporäre Buffs (Adrenalin, Schnäppchen-Fieber, Fokus).
- **Acceptance criteria:**
  - Timer prüft ununterbrochenes Zuschauen und aktiviert den entsprechenden Statuseffekt
- **Files touched:** `src/tv_engine.py`, `src/player.py`

---

## Phase P: Das Interdimensionale Patentamt

### Task P01: Patentamt-Hub Kartengenerierung & Sektoren

- **Description:** Implementiert das Szenario `patentamt_hub` mit Oberamt, Schrott-Basar und Endlosem Patent-Archiv.
- **Acceptance criteria:**
  - Eigener Weltaufbau mit futuristisch-bürokratischer Ästhetik und interdimensionalem Portalzugang
- **Files touched:** `src/patentamt/hub.py`, `src/patentamt/generator.py`

### Task P02: Alternative Cloita-NPCs

- **Description:** Implementiert Bürokratie-Cloita, Quanten-Cloita, Steampunk-Cloita und Snob-Cloita mit eigenen Animationen und Dialogen.
- **Acceptance criteria:**
  - NPCs bevölkern das Amt und interagieren zynisch mit der Spielerin
- **Files touched:** `src/patentamt/npcs.py`, `tools/sprites_patentamt.py`

### Task P03: Patent-Alibi-Mechanik

- **Description:** Verknüpft Klonitas Anwesenheit und ihr Patent-Zertifikat mit dem behördlichen Fahndungssystem.
- **Acceptance criteria:**
  - Solange Klonita aktiv an Cloitas Seite ist, sinkt der Fahndungs-Zuwachs um 50 %
  - Geht Klonita k.o., erlischt das Tarnfeld bis zu ihrer Reaktivierung nach 5 Sekunden
- **Files touched:** `src/authority.py`, `src/klonita.py`

### Task P04: Das Endlose Patent-Archiv

- **Description:** Generiert die monumentale Archiv-Halle mit gigantischen Aktenschränken, Förderbändern und satirischen Paragraphen-Plakaten.
- **Acceptance criteria:**
  - Begehbare Halle mit animierten Aktenströmen und interaktiven Informationstafeln
- **Files touched:** `src/patentamt/archive.py`, `src/patentamt/hub.py`

---

## Phase Q: Die Rebellin Cloita-Null & der Koffer-Staatsstreich

### Task Q01: Quest-Reihe »Schatten über dem Patentamt«

- **Description:** Implementiert die 3-teilige Quest mit Untergrund-Flugblättern, Ausschuss-Infiltration und dem versuchten Staatsstreich von Cloita-Null.
- **Acceptance criteria:**
  - Flugblätter spawnen zufällig in den Schrott-Biomen und schalten geheime Dialoge frei
  - Senatssitzung gipfelt im dramatischen Putsch der abtrünnigen Cloita-Null
- **Files touched:** `src/quest_patentamt.py`, `src/patentamt/hub.py`

### Task Q02: Bosskampf: Die Rebellin Cloita-Null

- **Description:** Implementiert den 3-Phasen-Bosskampf gegen das böse Ich (Aktentaschen-Raketen, Paragraphen-Inverter, Dimensionalkern-Riss).
- **Acceptance criteria:**
  - Phase 1: Koffer-Raketen und Akten-Schutzmauer
  - Phase 2: Paragraphen-Inverter entsättigt den Bildschirm und lähmt Flux
  - Phase 3: Vakuum-Riss saugt Partikel an; Sieg schaltet Flucht-Zwischensequenz frei
- **Files touched:** `src/bosses/cloita_null.py`, `tests/spec_phase3/test_phase_q.py`

### Task Q03: Belohnung: Titan-Aktentasche & Amts-Befriedung

- **Description:** Schaltet die Waffe `waffe_patent_koffer` frei und befriedet das Patentamt.
- **Acceptance criteria:**
  - Titan-Aktentasche besitzt 16 Slots und 0 Nachladezeit
  - Beamte arbeiten wieder in geregelten Bahnen und bieten seltene Bausätze an
- **Files touched:** `src/weapon_parts.py`, `src/patentamt/hub.py`

---

## Phase R: Sechs handgefertigte Satire-Universen Teil 1

### Task R01: Universum `anatomie_park` (Der Beamten-Park)

- **Description:** Implementiert Universumsdaten, Materialien (`speisebrei`, `gallenstein_beton`, `nervenstrang`, `magensaft_limo`), Regel `rule_peristaltik` (Strömungswinde), Kreaturen, Boss Dr. Pfortader, Event Akutes Sodbrennen und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/anatomie_park.py`, `tools/sprites_anatomie_park.py`

### Task R02: Universum `pastell_hoelle` (Klonitas Pastell-Hölle)

- **Description:** Implementiert Universumsdaten, Materialien (`schaumstoff`, `erdbeernektar`, `zuckerglas_scherbe`, `honigkleber`), Regel `rule_kitsch_carnage`, Plüsch-Kreaturen, Boss Ur-Kuscheltier, Event Kuschel-Alarm und Rang 1–3 Skalierung. Erdbeernektar verleiht temporäre Schilde (keine direkte HP-Heilung).
- **Files touched:** `src/universes/pastell_hoelle.py`, `tools/sprites_pastell_hoelle.py`

### Task R03: Universum `klonenberg_welt` (Das Klonenberg-Desaster)

- **Description:** Implementiert Universumsdaten, Materialien (`mutagen_schleim`, `wucherndes_fleisch`, `augen_fett`, `knochen_dorn`), Regel `rule_mutation_ooze`, Gen-Mutationen, Boss Klonenberg-Monstrum, Event Zellteilungs-Welle und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/klonenberg_welt.py`, `tools/sprites_klonenberg.py`

### Task R04: Universum `talent_kosmos` (Der Kosmische Talentwettbewerb)

- **Description:** Implementiert Universumsdaten, Materialien (`buehnen_gold`, `schall_kristall`, `applaus_nebel`, `jury_plasma`), Regel `rule_show_me`, Hype-Check, Boss Jury-Kopf, Event RICHTERSPRUCH-Laser und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/talent_kosmos.py`, `tools/sprites_talent_kosmos.py`

### Task R05: Universum `antrags_labyrinth` (Das Pneumatische Antrags-Labyrinth)

- **Description:** Implementiert Universumsdaten, Materialien (`formular_wand`, `toner_staub`, `siegelwachs`, `papierkorb_asche`), Regel `rule_pneumatic_flow`, Rohrpost-Winde, Boss Bürokraten-Minotaurus, Event Aktensturz und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/antrags_labyrinth.py`, `tools/sprites_antrags_labyrinth.py`

### Task R06: Universum `krawatten_planet` (Das Krawatten-Imperium)

- **Description:** Implementiert Universumsdaten, Materialien (`panzer_seide`, `zeitreise_treibstoff`, `manschetten_chrom`, `buegel_dampf`), Regel `rule_temporal_ties`, Zeitreise-Beamte, Boss Kragen-Tribunal, Event Zeitschleife und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/krawatten_planet.py`, `tools/sprites_krawatten.py`

---

## Phase S: Sechs handgefertigte Satire-Universen Teil 2

### Task S01: Universum `klo_paradies` (Das Heilige Sanitärium)

- **Description:** Implementiert Universumsdaten, Materialien (`zen_kies`, `porzellan_edel`, `heilquell_wasser`, `laser_beton`), Regel `rule_sanctuary_retribution`, Boss Thron-Abwehrsystem, Event Hologramm-Spott und Rang 1–3 Skalierung. Heilquell-Wasser spendet Schild-Buffs statt direkter HP.
- **Files touched:** `src/universes/klo_paradies.py`, `tools/sprites_sanitaer.py`

### Task S02: Universum `matroschka_simulation` (Die Simulations-Schachtel)

- **Description:** Implementiert Universumsdaten, Materialien (`wireframe_wand`, `glitch_pixel`, `hologramm_nebel`, `server_kupfer`), Regel `rule_low_cpu_glitch`, Boss Zigerion-Chef, Event Speichermangel und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/matroschka_simulation.py`, `tools/sprites_simulation.py`

### Task S03: Universum `kollektiv_buerokratie` (Das Büro-Kollektiv 404)

- **Description:** Implementiert Universumsdaten, Materialien (`synapsen_kabel`, `kamillentee`, `linoleum_grau`, `aktenstapel_rein`), Regel `rule_hive_mind`, Boss Synapsen-Gehirn, Event Kollektiver Seufzer und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/kollektiv_buerokratie.py`, `tools/sprites_kollektiv.py`

### Task S04: Universum `unsterblichkeits_resort` (Das Unsterblichkeits-Resort)

- **Description:** Implementiert Universumsdaten, Materialien (`feld_grenze`, `thermal_wasser`, `marmor_gold`, `zerfalls_sand`), Regel `rule_immortality_field`, Schadens-Stapelung, Boss Resort-Direktor, Event Feld-Flackern und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/unsterblichkeits_resort.py`, `tools/sprites_resort.py`

### Task S05: Universum `schroedinger_kammer` (Das Quanten-Scherbenmeer)

- **Description:** Implementiert Universumsdaten, Materialien (`quanten_glas`, `tachyonen_schleim`, `unschaerfe_staub`, `zeitpolizei_stahl`), Regel `rule_quantum_phase` (Phasenecho-Geschosse), Boss Zeit-Polizist, Event Quanten-Kollaps und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/schroedinger_kammer.py`, `tools/sprites_quanten.py`

### Task S06: Universum `kater_bunker` (Der Kater-Bunker)

- **Description:** Implementiert Universumsdaten, Materialien (`kater_beton`, `starkbier`, `demuetigungs_glas`, `kater_giftgas`), Regel `rule_drunk_puzzles`, Zeitdruck-Rätsel, Boss Kater-Cloita-Projektion, Event Peinliche Rückblende und Rang 1–3 Skalierung.
- **Files touched:** `src/universes/kater_bunker.py`, `tools/sprites_kater_bunker.py`

---

## Phase T: Parasiten-Event »Falsche Freunde« & Zynismus-Dialoge

### Task T01: Parasiten-Invasions-Event in der Werkstatt

- **Description:** Implementiert den Zufallsausbruch von `event_falsche_freunde` in der Werkstatt mit 4–6 bizarren Gestalten (Thermoskanne Theobald, Onkel Locher etc.).
- **Acceptance criteria:**
  - Event spawnt bunte, kumpelhafte Gestalten, die Cloita und Klonita schmeicheln wollen
- **Files touched:** `src/events_parasites.py`, `src/workshop.py`

### Task T02: Soziales Deduktions-System

- **Description:** Baut das Fragesystem auf: Figuren, die ausschließlich zuckersüße Erinnerungen teilen, sind Parasiten und müssen exekutiert werden.
- **Acceptance criteria:**
  - Dialogabfrage deckt parasitäre Kitsch-Erinnerungen auf
  - Erschießen des Parasiten spuckt Gedächtnis-Essenz aus; Fehltritte verfluchen Cloita
- **Files touched:** `src/events_parasites.py`, `src/dialogue.py`

### Task T03: Zynismus- & Meta-Dialog-Matrix

- **Description:** Integriert Cloitas philosophischen Nihilismus, Klonitas Existenzängste und Vierte-Wand-Kommentare über Steuerung und PCs.
- **Acceptance criteria:**
  - Kontext-Trigger bei Fast-Toden, langen Pausen und Säureunfällen
- **Files touched:** `src/cynical_dialogues.py`, `src/ui.py`

### Task T04: Fallblatt-Statistikanzeige im Pausenraum

- **Description:** Platziert die dynamische Fallblatt-Tafel `ws_statistik_wand` in der Werkstatt mit Cloita-Totalschäden, Kaffee-Verbrauch und gepfändetem Steuer-Gold (keine Klonita-Todeszähler).
- **Acceptance criteria:**
  - Interaktives Schild zählt K.o.-Reaktivierungen, Totalschäden und verschütteten Kaffee pro Lauf
- **Files touched:** `src/workshop_stats.py`, `src/workshop.py`

---

## Phase U: Worldbuilding-Gesamtabnahme & Satire-Polishing

### Task U01: Gadget- & Zaubermathematik-Integrationstest

- **Description:** Stellt sicher, dass Gadgets harmonisch mit den Zauberkaskaden aus Phase 2 zusammenspielen.
- **Files touched:** `tests/spec_phase3/test_phase_u_integration.py`

### Task U02: Satire- und Dialog-Audit

- **Description:** Prüft alle deutschen Spieltexte auf fehlerfreie Typografie, Wortwitz und Einhaltung der Lore.
- **Files touched:** `tests/spec_phase3/test_phase_u_dialogues.py`

### Task U03: Performance- & Render-Check des Patentamts und aller 12 Satire-Biome

- **Description:** Validiert stabile 60 FPS im Patentamt-Hub, während des Scanline-CRT-Modus und in den neuen Biomen.
- **Files touched:** `tests/spec_phase3/test_phase_u_perf.py`

### Task U04: Gesamtabnahme Phase 3

- **Description:** Führt sämtliche Spec-Tests für Phase 3 aus und bestätigt Code-Qualität (`ruff check`).
- **Files touched:** `tests/spec_phase3/`
