# Task List: Phase 3 »Absurdität, Zynismus & Multiversums-Satire« (Phasen N–S)

Master-Plan: [`tasks/plan_phase3.md`](plan_phase3.md) · Bibel: [`docs/phase3_absurditaet/`](../docs/phase3_absurditaet/00-uebersicht.md)

---

## Phase N: Absurde Gadgets & Notfall-Apparate

### Task N01: Modulares Gadget-Framework & Tastenbelegung

- **Description:** Implementiert das `Gadget`-Basissystem in `src/gadgets.py` mit `Player.active_gadget`, Cooldown-/Ladungsverwaltung, HUD-Icon und Tastenzuweisung (Standard `Taste G`).
- **Acceptance criteria:**
  - `src/gadgets.py` definiert `class Gadget`, `GadgetManager` und `GadgetState`
  - Gadgets können ausgerüstet, gewechselt und per Tastendruck aktiviert werden
- **Files touched:** `src/gadgets.py`, `tests/spec_phase3/test_phase_n.py`

### Task N02: Der Gefälschte Säurebottich (`gadget_saeurebottich`)

- **Description:** Implementiert den Säurebottich mit Schnorchel, Fake-Knochen-Partikeln, Feind-Aggro-Reset und Schleich-Modus mit kritischem Hinterhaltsschaden.
- **Acceptance criteria:**
  - Aktivierung spawnt optischen Bottich mit Schnorchel und treibenden Knochen-Pixeln
  - Feinde brechen Verfolgung ab und wechseln in IDLE-Zustand
  - Angriff aus dem Bottich verursacht garantierten kritischen Treffer (+200 %)
- **Files touched:** `src/gadgets.py`, `src/player.py`

### Task N03: Die Büchse des Herrn Fleißig (`gadget_herr_fleissig`)

- **Description:** Implementiert den blauen Hilfsgeist mit hysterischer Sprachausgabe, Sammel-, Schalter- und Schutzschild-Verhalten sowie der Existenz-Verpuffung bei Erfolg.
- **Acceptance criteria:**
  - Spawnt `HerrFleissig`-Entität mit hoher blauer Silhouette
  - Erledigt die nächstgelegene Aufgabe (Gold sammeln, Hebel drücken oder Schutzschild sein)
  - Löst sich bei Aufgabenerfüllung in Glitzer auf; eskaliert nach 25 Sekunden Kampf in Panik
- **Files touched:** `src/gadgets.py`, `src/behaviour.py`

### Task N04: Kaffee-Drohne & Mikro-Universums-Batterie

- **Description:** Implementiert die melancholische Kolben-Drohne (`gadget_kaffee_drohne`) und die streikende Mini-Galaxie-Batterie (`gadget_mikro_batterie`).
- **Acceptance criteria:**
  - Kaffee-Drohne holt selbstständig Flüssigkeiten und reicht Kolben
  - Mikro-Batterie spendet +60 Flux/s; Streik alle 120 s erfordert Schütteln oder Klonita-Zuspruch
- **Files touched:** `src/gadgets.py`, `src/flask.py`

### Task N05: Die Gurken-Notfallmutation (`mod_gurken_flucht`)

- **Description:** Implementiert das Überlebensmodul, das Cloita bei lethalem Schaden in die 8×14 Pixel kleine Salzgurke verwandelt.
- **Acceptance criteria:**
  - Bei LP <= 0 verwandelt sich Cloita in `salzgurke_cloita` mit Kakerlaken-Beinen
  - Gurke kann durch 2-Pixel-Schlitze kriechen und Schrauben verschießen
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

### Task O02: Die 12 Fernsehkanäle mit surrealen Skripten

- **Description:** Integriert die 12 kanonischen Sendungen (Plümpel-Herstellung, Zwei Schwestern im Lieferwagen, Ameisen-Müller, Kochen mit Lava etc.) als animierte Text-/Pixel-Sequenzen.
- **Acceptance criteria:**
  - Alle 12 Kanäle aus Bibel Kap. 02 sind abspielbar und besitzen eigene Farb-/Tonmuster
- **Files touched:** `src/tv_engine.py`, `src/tv_channels.py`

### Task O03: Teleshopping-Gutscheincodes & Fabrikator-Rabatt

- **Description:** Implementiert das Einlösen von Werbecodes aus Kanal 5 am Fabrikator (`RABATT-42-GLIBBER`).
- **Acceptance criteria:**
  - Eingabe des Codes senkt die Baukosten des nächsten Waffenbaus um 50 %
- **Files touched:** `src/tv_engine.py`, `src/fabricator.py`

### Task O04: Zuschauer-Buffs nach 15 Sekunden Verweildauer

- **Description:** Verleiht dem Spieler nach mindestens 15 Sekunden Zuschauen je nach Kanal temporäre Buffs (Adrenalin, Schnäppchen-Fieber, Gute Laune).
- **Acceptance criteria:**
  - Timer prüft ununterbrochenes Zuschauen und aktiviert den entsprechenden Statuseffekt
- **Files touched:** `src/tv_engine.py`, `src/player.py`

---

## Phase P: Die Zitadelle der Cloitas & Klon-Legebatterie

### Task P01: Zitadellen-Hub Kartengenerierung & Viertel

- **Description:** Implementiert das Raumstations-Szenario `citadel_hub` mit Oberstadt, Schrott-Basar und Klon-Legebatterie.
- **Acceptance criteria:**
  - Eigener Weltaufbau mit futuristisch-schrottiger Ästhetik und interdimensionalem Portalzugang
- **Files touched:** `src/citadel/hub.py`, `src/citadel/generator.py`

### Task P02: Alternative Cloita-NPCs

- **Description:** Implementiert Cowboy-Cloita, Fabrik-Cloita, Gurken-Cloita und Snob-Cloita mit eigenen Animationen und Dialogen.
- **Acceptance criteria:**
  - NPCs bevölkern die Zitadelle und interagieren zynisch mit der Spielerin
- **Files touched:** `src/citadel/npcs.py`, `tools/sprites_citadel.py`

### Task P03: Naivitäts-Tarnfeld-Mechanik

- **Description:** Verknüpft Klonitas Anwesenheit mit dem behördlichen Fahndungssystem.
- **Acceptance criteria:**
  - Solange Klonita lebt, sinkt der Fahndungs-Zuwachs um 50 %
  - Fällt Klonita, spawnen sofort doppelt so viele Behörden-Agenten
- **Files touched:** `src/authority.py`, `src/klonita.py`

### Task P04: Die Klon-Legebatterie mit Zucht-Bottichen

- **Description:** Generiert die industrielle Klon-Fabrik mit Glaszylindern, Förderbändern und zynischen Propaganda-Plakaten.
- **Acceptance criteria:**
  - Begehbare Industrie-Halle mit animierten Klon-Embryos und interaktiven Schildern
- **Files touched:** `src/citadel/hatchery.py`, `src/citadel/hub.py`

---

## Phase Q: Der Rat der Chef-Forscherinnen & die Revoluzzer-Klonita

### Task Q01: Quest-Reihe »Schatten über der Zitadelle«

- **Description:** Implementiert die 3-teilige Quest mit Untergrund-Flugblättern, Senats-Infiltration und dem Staatsstreich der Klonitas.
- **Acceptance criteria:**
  - Flugblätter spawnen zufällig in den Müll-Biomen und schalten geheime Dialoge frei
  - Senatssitzung gipfelt im dramatischen Putsch der Revoluzzer-Klonita
- **Files touched:** `src/quest_citadel.py`, `src/citadel/hub.py`

### Task Q02: Bosskampf: Die Revoluzzer-Klonita

- **Description:** Implementiert den 3-Phasen-Bosskampf (Aktenkoffer-Raketen, Naivitäts-Inverter, Dimensionalkern-Riss).
- **Acceptance criteria:**
  - Phase 1: Koffer-Raketen und Klon-Schutzmauer
  - Phase 2: Naivitäts-Inverter entsättigt den Bildschirm und lähmt Flux
  - Phase 3: Vakuum-Riss saugt Partikel an; Sieg schaltet Flucht-Zwischensequenz frei
- **Files touched:** `src/bosses/revoluzzer_klonita.py`, `tests/spec_phase3/test_phase_q.py`

### Task Q03: Belohnung: Titan-Koffer & Klon-Befreiung

- **Description:** Schaltet die Waffe `waffe_revoluzzer_koffer` frei und verwandelt die Zitadelle in eine befreite Klon-Oase.
- **Acceptance criteria:**
  - Titan-Koffer besitzt 16 Slots und 0 Nachladezeit
  - Klonitas laufen glücklich in bunten Kitteln umher und verteilen Gratis-Proben
- **Files touched:** `src/weapon_parts.py`, `src/citadel/hub.py`

---

## Phase R: Sechs handgefertigte Satire-Universen

### Task R01: Universum `anatomie_park` (Der Beamten-Park)

- **Description:** Implementiert Universumsdaten, Materialien (`speisebrei`, `gallenstein_beton`, `nervenstrang`, `magensaft_limo`), Regel `rule_peristaltik`, Kreaturen, Boss Dr. Pfortader und Event Akutes Sodbrennen.
- **Files touched:** `src/universes/anatomie_park.py`, `tools/sprites_anatomie_park.py`

### Task R02: Universum `pastell_hoelle` (Klonitas Pastell-Hölle)

- **Description:** Implementiert Universumsdaten, Materialien (`schaumstoff`, `erdbeermilch`, `zuckerglas_scherbe`, `honigkleber`), Regel `rule_kitsch_carnage`, Plüsch-Kreaturen, Boss Ur-Kuscheltier und Event Kuschel-Alarm.
- **Files touched:** `src/universes/pastell_hoelle.py`, `tools/sprites_pastell_hoelle.py`

### Task R03: Universum `klonenberg_welt` (Das Klonenberg-Desaster)

- **Description:** Implementiert Universumsdaten, Materialien (`mutagen_schleim`, `wucherndes_fleisch`, `augen_fett`, `knochen_dorn`), Regel `rule_mutation_ooze`, Gen-Mutationen, Boss Klonenberg-Monstrum und Event Zellteilungs-Welle.
- **Files touched:** `src/universes/klonenberg_welt.py`, `tools/sprites_klonenberg.py`

### Task R04: Universum `talent_kosmos` (Der Kosmische Talentwettbewerb)

- **Description:** Implementiert Universumsdaten, Materialien (`buehnen_gold`, `schall_kristall`, `applaus_nebel`, `jury_plasma`), Regel `rule_show_me`, Hype-Check, Boss Jury-Kopf und Event RICHTERSPRUCH-Laser.
- **Files touched:** `src/universes/talent_kosmos.py`, `tools/sprites_talent_kosmos.py`

### Task R05: Universum `spaghetti_dimension` (Die Teigwaren-Trauerweide)

- **Description:** Implementiert Universumsdaten, Materialien (`bolognese`, `parmesan_staub`, `hartweizen_stein`, `basilikum_oel`), Regel `rule_delicious_despair`, Nudel-Dropraten, Boss Nudelpresse und Event Mittagspause.
- **Files touched:** `src/universes/spaghetti_dimension.py`, `tools/sprites_spaghetti.py`

### Task R06: Universum `krawatten_planet` (Das Krawatten-Imperium)

- **Description:** Implementiert Universumsdaten, Materialien (`panzer_seide`, `zeitreise_treibstoff`, `manschetten_chrom`, `buegel_dampf`), Regel `rule_temporal_ties`, Terminator-Krawatten-Spawn, Boss Kragen-Tribunal und Event Zeitschleife.
- **Files touched:** `src/universes/krawatten_planet.py`, `tools/sprites_krawatten.py`

---

## Phase S: Sechs handgefertigte Satire-Universen Teil 2

### Task S01: Universum `klo_paradies` (Das Heilige Sanitärium)

- **Description:** Implementiert Universumsdaten, Materialien (`zen_kies`, `porzellan_edel`, `heilquell_wasser`, `laser_beton`), Regel `rule_sanctuary_retribution`, Boss Thron-Abwehrsystem und Event Hologramm-Spott.
- **Files touched:** `src/universes/klo_paradies.py`, `tools/sprites_sanitaer.py`

### Task S02: Universum `matroschka_simulation` (Die Simulations-Schachtel)

- **Description:** Implementiert Universumsdaten, Materialien (`wireframe_wand`, `glitch_pixel`, `hologramm_nebel`, `server_kupfer`), Regel `rule_low_cpu_glitch`, Boss Zigerion-Chef und Event Speichermangel.
- **Files touched:** `src/universes/matroschka_simulation.py`, `tools/sprites_simulation.py`

### Task S03: Universum `kollektiv_buerokratie` (Das Büro-Kollektiv Einheit 404)

- **Description:** Implementiert Universumsdaten, Materialien (`synapsen_kabel`, `kamillentee`, `linoleum_grau`, `aktenstapel_rein`), Regel `rule_hive_mind`, Boss Synapsen-Gehirn und Event Kollektiver Seufzer.
- **Files touched:** `src/universes/kollektiv_buerokratie.py`, `tools/sprites_kollektiv.py`

### Task S04: Universum `unsterblichkeits_resort` (Das Unsterblichkeits-Resort)

- **Description:** Implementiert Universumsdaten, Materialien (`feld_grenze`, `thermal_wasser`, `marmor_gold`, `zerfalls_sand`), Regel `rule_immortality_field`, Schadens-Stapelung, Boss Resort-Direktor und Event Feld-Flackern.
- **Files touched:** `src/universes/unsterblichkeits_resort.py`, `tools/sprites_resort.py`

### Task S05: Universum `schroedinger_kammer` (Das Quanten-Scherbenmeer)

- **Description:** Implementiert Universumsdaten, Materialien (`quanten_glas`, `tachyonen_schleim`, `unschaerfe_staub`, `zeitpolizei_stahl`), Regel `rule_split_timeline`, Boss Zeit-Polizist und Event Quanten-Kollaps.
- **Files touched:** `src/universes/schroedinger_kammer.py`, `tools/sprites_quanten.py`

### Task S06: Universum `kater_bunker` (Der Kater-Bunker)

- **Description:** Implementiert Universumsdaten, Materialien (`kater_beton`, `starkbier`, `demuetigungs_glas`, `kater_giftgas`), Regel `rule_drunk_puzzles`, Zeitdruck-Rätsel, Boss Betrunkene-Cloita-KI und Event Peinliche Rückblende.
- **Files touched:** `src/universes/kater_bunker.py`, `tools/sprites_kater_bunker.py`

---

## Phase T: Parasiten-Event »Falsche Freunde« & Zynismus-Dialoge

### Task T01: Parasiten-Invasions-Event in der Werkstatt

- **Description:** Implementiert den Zufallsausbruch von `event_falsche_freunde` in der Werkstatt oder Aufenthaltsräumen mit 4–6 bizarren Gestalten (Kühlschrank-Klaus, Onkel Büroklammer etc.).
- **Acceptance criteria:**
  - Event spawnt bunte, fröhliche Gestalten, die Cloita und Klonita umarmen wollen
- **Files touched:** `src/events_parasites.py`, `src/workshop.py`

### Task T02: Soziales Deduktions-System

- **Description:** Baut das Fragesystem auf: Figuren, die nur zuckersüße Erinnerungen teilen, sind Parasiten und müssen exekutiert werden.
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

- **Description:** Platziert die dynamische Fallblatt-Tafel `ws_statistik_wand` in der Werkstatt mit Klonita-Verschleißzähler und gepfändetem Steuer-Gold.
- **Acceptance criteria:**
  - Interaktives Schild zählt Klonita-Tode, Cloita-Totalschäden und verschütteten Kaffee pro Lauf
- **Files touched:** `src/workshop_stats.py`, `src/workshop.py`

---

## Phase U: Worldbuilding-Gesamtabnahme & Satire-Polishing

### Task U01: Gadget- & Zaubermathematik-Integrationstest

- **Description:** Stellt sicher, dass Gadgets harmonisch mit den Noita-Zauberkaskaden aus Phase 2 zusammenspielen.
- **Files touched:** `tests/spec_phase3/test_phase_u_integration.py`

### Task U02: Satire- und Dialog-Audit

- **Description:** Prüft alle deutschen Spieltexte auf fehlerfreie Typografie, Wortwitz und Einhaltung der Lore.
- **Files touched:** `tests/spec_phase3/test_phase_u_dialogues.py`

### Task U03: Performance- & Render-Check der Zitadelle und aller 12 Satire-Biome

- **Description:** Validiert stabile 60 FPS im Zitadellen-Hub, während des Scanline-CRT-Modus und in den neuen Biomen.
- **Files touched:** `tests/spec_phase3/test_phase_u_perf.py`

### Task U04: Gesamtabnahme Phase 3

- **Description:** Führt sämtliche Spec-Tests für Phase 3 aus und bestätigt Code-Qualität (`ruff check`).
- **Files touched:** `tests/spec_phase3/`
