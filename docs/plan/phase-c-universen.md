# Phase C – Universen

Aufbau: **U0** baut den gemeinsamen Unterbau (einmal). **U1 Fleischwelt** wird als Referenz vollständig nach der Vorlage **UX** gebaut. **U2–U6** folgen derselben Vorlage; je Universum gibt es nur eine Tabelle mit den konkreten Werten plus wenige Sonderkarten.

Eine Karte `U3.06` bedeutet: Vorlage `UX.06`, eingesetzt mit Zeile „UX.06“ aus der Tabelle von U3.

## U0 Gemeinsamer Unterbau

### U0.01 Level-Felder erweitern

- Art: Code · Größe: S · Hängt ab von: –
- Lesen: V9 (`Level`); `class Level` in `src/worldgen.py`
- Dateien: `src/worldgen.py`, `tests/test_world.py`
- Tun: Felder aus V9 mit Standardwerten ergänzen; `Run._mirror_level` spiegelt die neuen Punktfelder mit (grep in `src/run.py`).
- Test: Spiegeln eines Levels mit allen Feldern.

### U0.02 Generator-Registry

- Art: Code · Größe: S · Hängt ab von: U0.01
- Lesen: V9
- Dateien: `src/universes/gen/__init__.py` (neu), `tests/test_universe_gen.py` (neu)
- Tun: `GENERATORS`, `register`, `generate` laut V9. Fehlt ein Generator → `KeyError` mit Universumsschlüssel.
- Test: Dummy-Generator registrieren und aufrufen.

### U0.03 Gemeinsame Bausteine I (Höhlen, Wege, Teilgebiete)

- Art: Code · Größe: M · Hängt ab von: U0.02
- Lesen: V9 „Gemeinsame Bausteine“; in `src/worldgen.py` `_carve_oval`, `_carve_tunnel`, `ensure_path`, `_connections`
- Dateien: `src/universes/gen/common.py` (neu), Test
- Tun: dünne Wrapper bzw. Re-Exporte (keine Kopien) für `carve_oval`, `carve_tunnel`, `ensure_path`; neu `split_regions(world, layout: str, keys: tuple[str, ...]) -> dict[str, rect]` mit Layouts `"vertical"` (Streifen von oben nach unten), `"horizontal"` (links → rechts), `"islands"` (Inseln über einem Meer: unterstes Drittel = letzter Schlüssel).
- Test: Rechtecke decken die Welt ohne Überlappung ab.

### U0.04 Gemeinsame Bausteine II (Anker, Geheimnisse, Beute)

- Art: Code · Größe: M · Hängt ab von: U0.03
- Lesen: V9; in `src/worldgen.py` `_vault`, `_secret_chamber`; Bibel 02 „Wirtschaft“ (Goldhaufen 6–8), Bibel 07 Gegenstände
- Dateien: `src/universes/gen/common.py`, Test
- Tun: `place_anchor(world, region, rng)` (fester Sockel aus `bedrock`, freie Fläche 24×24 davor), `place_secret(world, region, shell_material, rng)`, `place_vault(...)`, `place_life_capsule(world, region, rng)` (versteckt: hinter ≥ 6 px Material), `place_crates(world, n, rng)`, `place_gold(world, n=rng.randint(6, 8), rng)`, `place_natives(world, universe, rank, rng)` (Anzahl je Rang ×1/×1,3/×1,6 der Fläche, Gruppen nach `spec.group_size`). Alle geben Koordinaten zurück, schreiben nichts in `Run`.
- Test: Punkte liegen in Luft bzw. im Material wie verlangt; Anzahl Gold 6–8.

### U0.05 Run lädt ein Universum

- Art: Code · Größe: M · Hängt ab von: U0.02, U0.04
- Lesen: `Run.enter_depth`, `_prepare_world`, `_apply_rule` in `src/run.py` (grep); `src/universes/catalog.py`
- Dateien: `src/run.py`, `tests/test_run.py`
- Tun: `Run.enter_universe(key: str, rank: int, boss: bool)`: Materialsatz + Größe + Regel aus `Universe`, `generate(...)`, Spawns aus `Level.spawns`, Gold/Kisten/Lebenskapsel als Pickups, `emit("enter_universe", ...)`. `enter_depth` bleibt bestehen (wird in W1 entfernt).
- Test: `enter_universe("fleischwelt", 1, False)` mit Dummy-Generator; Speichern/Laden danach.

### U0.06 Sandbox: Universum wählen

- Art: Code · Größe: S · Hängt ab von: U0.05
- Lesen: Sandbox-Tasten U/O/R in `src/main.py`/`src/run.py` (grep `cycle_rule`)
- Dateien: `src/run.py`, `src/main.py`, `src/keybinds.py`
- Tun: Taste **J** (Sandbox): nächstes Universum mit `ready=True` bzw. registriertem Generator; Taste **Shift+J**: Rang 1→2→3.
- Test: Zyklus über registrierte Universen.

### U0.07 Ereignis-Rahmen

- Art: Code · Größe: S · Hängt ab von: T5.21
- Lesen: V10, V12
- Dateien: `src/events.py` (neu), `src/run.py` (Aufruf in `update`, Speichern), `tests/test_events.py` (neu)
- Test: Dummy-Ereignis: `on_warn` bei `interval - warn`, `on_start`, `on_tick`, `on_end` in richtiger Reihenfolge; Rundreise Speichern/Laden.

### U0.08 Proben und neue Gegenstandsarten

- Art: Code · Größe: M · Hängt ab von: –
- Lesen: V11; `class Pickup` in `src/loot.py`; `src/inventory.py`
- Dateien: `src/samples.py` (neu, alle 12 Proben aus Bibel 07), `src/loot.py`, `src/inventory.py`, `tests/test_samples.py` (neu)
- Tun: Proben-Leiste (12 Plätze, Stapel 99), Aufheben, Speichern.
- Test: 100. Probe gleicher Art passt nicht; Speichern/Laden.
- Nicht: Rucksack-Oberfläche (R2.04).

### U0.09 Drops beim Tod

- Art: Code · Größe: S · Hängt ab von: U0.08, T5.01
- Lesen: `Run._on_death`
- Dateien: `src/run.py`, Test
- Tun: `spec.drops` würfeln (Seed-Zufall), Pickup an Todesposition.
- Test: Chance 1,0 → Probe liegt da.

### U0.10 Herausforderungs-Rahmen

- Art: Code · Größe: M · Hängt ab von: U0.07
- Lesen: V13; Bibel 07 „Herausforderungen in Universen“
- Dateien: `src/challenges.py` (neu), `src/run.py` (Annehmen mit E beim Auftraggeber, Hörer registrieren, Belohnung auszahlen), `tests/test_challenges.py` (neu)
- Tun: nur Rahmen + Belohnungsarten `gold`, `sample`, `life_capsule`, `module_rarity`, `flask`, `reroll`. Konkrete Herausforderungen kommen je Universum (UX.12).
- Test: Dummy-Herausforderung mit Ziel 3 über `emit`.

### U0.11 Bot-Lauf

- Art: Code · Größe: M · Hängt ab von: U0.05, T5.05
- Lesen: V14
- Dateien: `src/bot.py` (neu), `tests/test_bot.py` (neu)
- Tun: laut V14; Logikzeit je Bild messen (`time.perf_counter`), p99 berechnen. Fehler abfangen und als Text in `crashed`.
- Test: Dummy-Universum, 2 s, `crashed is None`, `anchor_reachable`.

### U0.12 Arena-Rahmen

- Art: Code · Größe: S · Hängt ab von: U0.04
- Lesen: `ARENA_RADIUS`, Arena-Erzeugung in `generate_level` (`src/worldgen.py`)
- Dateien: `src/universes/gen/common.py`, Test
- Tun: `carve_arena(world, centre, w, h, floor_material, wall_material)`; die Arena liegt vor dem Anker; auf Bossplätzen setzt der Generator `Level.arena`.
- Test: Arena ist frei, Anker liegt dahinter.

## UX Vorlage für jedes Universum

Jede Zeile = eine Karte. „Lesen“ immer: der Universums-Abschnitt in Bibel 03, bei Kreaturen der Kreatur-Abschnitt in Bibel 05, dazu die genannten Verträge.

| Schritt | Titel | Art · Größe | Hängt ab von | Dateien | Fertig, wenn |
| --- | --- | --- | --- | --- | --- |
| UX.01 | Materialsatz | Daten · S | – | `src/materials.py` (Tupel `_<KEY>` + Eintrag im Satz-Verzeichnis, wie `_FILES`/„aktenhalde“), `tests/test_material_sets.py` | Satz aktivierbar, ≤ 10 eigene Materialien, Farben aus Bibel |
| UX.02 | Reaktionen | Daten · S | UX.01 | `src/reactions.py` (`RULES`), `tests/test_reactions.py` | je Wirkung in der Materialtabelle eine Reaktion + Test (Testwelt 20×20, n Schritte, Material entstanden/verschwunden) |
| UX.03 | Generator Grundform | Code · M | U0.03 | `src/universes/gen/<key>.py` (neu), `tests/test_universe_gen.py` | Welt in Bibelgröße, Teilgebiete via `split_regions`, Spawn frei, `ensure_path` Spawn → Anker |
| UX.04 | Generator Teilgebiet-Details | Code · M | UX.03 | dito | jedes Teilgebiet hat die in Bibel 03 genannten Merkmale (je Merkmal eine Funktion `_<merkmal>`) |
| UX.05 | Anker, Geheimnisse, Beute, Arena | Code · S | UX.04, U0.04, U0.12 | dito | `Level` mit `exit`, `secret`, `vault`, `life_capsule`, Gold, Kisten, `arena` (nur Bossplatz) |
| UX.06 | Einheimische A: Werte | Daten · S | T5.21 | `src/enemies.py` (`CreatureSpec` mit Haltung, Fähigkeiten, Werten, `drops`, `gold`), `tests/test_enemies.py` | Werte = Bibel 05; Fähigkeiten registriert |
| UX.07 | Einheimische A: Sonderverhalten | Code · S | UX.06 | `src/behaviour.py` oder `src/enemies.py` | nur was die Bibliothek nicht abdeckt (siehe Tabelle), mit Test |
| UX.08 | Einheimische B: Werte | Daten · S | T5.21 | wie UX.06 | wie UX.06 |
| UX.09 | Einheimische B: Sonderverhalten | Code · S | UX.08 | wie UX.07 | wie UX.07 |
| UX.10 | Ereignis | Code · S–M | U0.07 | `src/events.py` (Klasse `<Name>Event`), `tests/test_events.py` | Zeiten und Wirkung laut Bibel 03, Test misst die Wirkung |
| UX.11 | Regel-Rest | Code · S | – | `src/rules.py`, `tests/test_rules.py` | offener Punkt aus 09 „Stand Phase A“ für diese Regel erledigt |
| UX.12 | Herausforderung | Code · S | U0.10 | `src/challenges.py`, Test | Text, Ziel, Belohnung laut Bibel 07 |
| UX.13 | Texte | Text · S | UX.06, UX.08 | `src/universes/catalog.py` (`klonita_de` ≥ 3), Hover-Texte (grep `hover` in `src/hover.py`) für alle neuen Kreaturen und Materialien | Mengen laut Bibel 08 „Textmengen“, max. 120 Zeichen |
| UX.14 | Geräusche | Code · S | UX.06, UX.08 | `src/sounds.py` (prozedural, wie vorhandene) | je Kreatur Laut, Angriff, Tod |
| UX.15 | Sprites Kreaturen | Grafik · S je Motiv | G0.05 | `assets/sprites/kreaturen/<key>.py` | eine Karte je Kreatur; Kontaktbogen freigegeben |
| UX.16 | Abnahme | Code · S | alle obigen | `tests/test_universe_<key>.py` (neu), `src/universes/catalog.py` (`ready=True`) | `run_bot` auf Rang 1–3 ohne Absturz, Anker erreichbar; Nutzer-Spieltest notiert in 09 |

Große Kreaturen und Sonderteile stehen als Zusatzkarten (`UX.17+`) in der Tabelle des Universums.

## U1 Fleischwelt (Referenz)

Besonderheit: Umbau des Bestehenden. Der Satz „koerper“ bleibt für die alten Tiefen erhalten, bis W1 sie entfernt. U1 wird **vor** U2–U6 fertig; dessen Dateien sind die Vorlage, auf die U2–U6 verweisen dürfen („wie `gen/fleischwelt.py`“).

| Schritt | Konkret |
| --- | --- |
| U1.01 | Satz `fleischwelt`: Fleisch, Knochen, Zahnschmelz, Blut, Magensäure, Wucherung, Sporen, Talg, Schorf, Glutblut (aus `_BODY` übernehmen, keine neuen Werte). Aliase für entfallende Materialien (Schleim, Eiter, Sehnen, Nervenstrom, Knochenstaub → Sand) in `DEFAULT_ALIASES`. |
| U1.02 | vorhandene Reaktionen der 10 Materialien behalten; Test, dass keine Reaktion ein Material außerhalb des Satzes erzeugt. |
| U1.03 | `gen/fleischwelt.py`: Quadrat 2048×1536, `split_regions("vertical", ("schlund", "magen", "knochenmark"))`; Grundlage `generate_level` (Rippen, Höhlen, Tunnel) – aufrufen bzw. Teile auslagern, nicht kopieren. |
| U1.04 | Schlund: Zähne aus Zahnschmelz an Höhlenrändern; Magen: Säurebecken + Talg; Knochenmark: Knochen mit Zahnschmelzadern (`_enamel_vein`). |
| U1.05 | Erinnerungssplitter in versiegelter Knochenkammer; Schatzkammer hinter Knochenpanzer (vorhandenes `_vault`); Arena „runde Knochenhalle mit Fleischboden“. |
| U1.06 | `fleischmade`: aus `MAGGOT` ableiten; `hostile`, `melee`, `hunt`, `retaliate`; Werte Bibel 05. |
| U1.07 | `fleischmade` Sonderzustand `burrow_out` beim Erscheinen (2 Frames, kommt aus der nächsten Fleischwand) und Springen an Hindernissen (`jump_speed`). |
| U1.08 | `blutegel`: aus `LEECH` ableiten; `hostile`, `melee`, `hunt`; `hangs=True`. |
| U1.09 | `blutegel` festsaugen: Zustand `latched`, 2 Schaden/s, löst sich bei Tritt oder wenn Spieler in Wasser. |
| U1.10 | Ereignis `verdauung`: alle 90 s für 20 s Säurespiegel in Region `magen` +30 px (Zellen am Beckenrand in Magensäure umwandeln, danach zurück zu Luft); Ankündigung Kamerawackeln + Spruch. |
| U1.11 | `rule_living_walls` Rang 3: nachgewachsenes Fleisch schluckt Geschosse (Geschoss, das in einer Zelle jünger als 2 s endet, explodiert nicht). |
| U1.12 | „Bring mir 3 Gallensteine“ → Lebenskapsel. Auftraggeber: `fleischmade` mit Haltung `passive` und Feld `giver=True` (Kreatur bleibt friedlich). |
| U1.13 | Sprüche aus Bibel 08 für Fleischwelt; Hover für `fleischmade`, `blutegel`. |
| U1.14 | Geräusche: vorhandene Made/Egel-Geräusche zuordnen. |
| U1.15 | Sprites `fleischmade`, `blutegel` (inkl. `hang`, `latched`). |
| U1.16 | Abnahme. |
| U1.17 | Alte Fleisch-Kreaturen (Schwärmer, Magenwurm, …) als Sandbox-only markieren (`SPECIES` bleibt, werden nicht gespawnt) – Art Code S. |

## U2 Aktenhalde

Schon erledigt (T1): Materialsatz „aktenhalde“ → **U2.01 entfällt**; U2.02 prüft nur, dass alle Wirkungen eine Reaktion + Test haben.

| Schritt | Konkret |
| --- | --- |
| U2.02 | Feuer + Papier → Flächenbrand; Papier → Asche; Tinte + Papier → getränktes Papier (nicht brennbar); Siegellack erstarrt nach 3 s; Feuer schmilzt Lack. |
| U2.03 | Breit 3072×1024, `split_regions("horizontal", ("registratur", "grossraumbuero", "archivkeller"))`. |
| U2.04 | Registratur: Regalreihen (Aktendeckel-Böden, Papier dazwischen); Großraumbüro: Schreibtische als Plattformen; Archivkeller: Tintenseen, dunkel. **Brandabschnitte** (Bibel 03): Funktion `_fire_compartments(rect, max_w=640, max_h=360)` setzt Trennwände aus Fels/Aktendeckel/getränktem Papier; Test: Flutfüllung über brennbare Zellen findet keinen Bereich > 640×360. |
| U2.05 | Rohrpost-Schächte als vertikale Verbindungen; Arena „Sitzungssaal, Tische als Plattformen, Papierboden“. |
| U2.06 | `aktenfresser`: `neutral`; `dig` (Härte von Aktendeckel), `melee`, `retaliate`, `pack`; Werte Bibel 05; `drops` Formular. |
| U2.07 | brennend rennt er umher und zündet Regale an (Status brennend → `flee` in Zufallsrichtung, setzt Feuer an berührte Papierzellen). |
| U2.08 | `stempler`: `neutral`; `melee`, `summon` (1 Agent), `retaliate`. |
| U2.09 | Stempeln: Zustand `stamp` 0,6 s Ausholen; zufällig Status `stamped` gut/schlecht (Bibel 02 „Status-Effekte“); angegriffen → nur noch „Abgelehnt“ und ruft 1 Agent. Status `stamped` neu in `src/body.py`/Spieler (eigene Karte **U2.17**, Code S, vorher). |
| U2.10 | Ereignis `pruefung`: alle 120 s Durchsage, 2 Agenten erscheinen (braucht B5.03). |
| U2.11 | `rule_paperwork` Rang 3: Funken entzünden Papier aus 3 px Abstand. |
| U2.12 | „Stempel 5 Formulare ab, bevor die Prüfung kommt“ → 150 Gold; Formulare = Pickups `formular_stempel`, E stempelt. |
| U2.13–U2.16 | nach Vorlage. |
| U2.17 | Status `stamped` (Genehmigt +20 % / Abgelehnt −20 % Schaden, 15 s) – vor U2.09. |
| U2.18 | Stempelfarbe trinken → `stamped` gut (Kolben-Wirkung, grep `Getrunken` in `src/flask.py`). |
| U2.19 | Tinte markiert Kreaturen (durch Wände sichtbar 20 s): Feld `marked_time` an `Body`, Zeichnen in `draw_creatures` ohne Sichtprüfung. |

Hängt zusätzlich ab von: B5.01–B5.04 (Behörde-Kern).

## U3 Glibbria

| Schritt | Konkret |
| --- | --- |
| U3.01 | `glibber`, `glibber_rot`, `brausesirup`, `schaum`, `kaugummi`, `zuckerguss`. |
| U3.02 | Himbeerglibber + Feuer → Sirup; Brausesirup + Feuer/Explosion → Schaumexplosion; Schaum zerfällt nach 10 s; Zuckerguss + Feuer → Sirup. |
| U3.03 | Inseln 2560×1280, `split_regions("islands", ("gelee_huegel", "kaugummi_hoehlen", "sirupkueste"))`; Meer aus Brausesirup unten. |
| U3.04 | Gelee-Hügel: schwebende Inseln; Kaugummi-Höhlen: Höhlen in großen Inseln mit Kaugummi-Pfützen; Sirupküste: Strand + Meer. Erreichbarkeit: Brücken aus Zuckerguss, wo `ensure_path` sonst scheitert. |
| U3.05 | Arena „große Gelee-Schüssel; Wände federn“. |
| U3.06 | `huepfling`: `passive`; `flee`, `graze` (`GRAZE_MATERIAL["huepfling"] = "zuckerguss"`); `group_size=(3, 6)`; `gold` 3. |
| U3.07 | springt ständig (Sprung bei Bodenkontakt alle 0,6–1,2 s), Zustand `squash` beim Landen; Tötung → Fahndung +0,25 (Ereignis `kill` mit Haltung, wertet B5.02 aus). |
| U3.08 | `glibberteiler`: `hostile`; `melee`, `hunt`, `split` (2 Generationen), `armor`. |
| U3.09 | Größenstufen 18×14 → 12×10 → 8×7 (statt 60 %-Regel: Tabelle `SPLIT_SIZES`). |
| U3.10 | Ereignis `brauseregen`: alle 100 s 15 s Brausesirup-Regen am oberen Rand der Simulationszone. |
| U3.11 | `rule_bounce` Rang 3: Gegnergeschosse prallen mehrfach (prüfen, ob `bounce_bonus(enemy=True)` schon greift; sonst einbauen). Zusätzlich: Glibber lässt Geschosse immer abprallen; Körper federn auf Glibber (Sprungkraft +30 % nach Landung aus > 60 px). |
| U3.12 | „Bring meine Kuh heil über den Sirupsee“ → Modul Seltenheit 3; braucht Kreatur `glibberkuh` (**U3.20**). |
| U3.17 | `trampolinwal` Werte: `neutral`, schwebt langsam (`flying`, Tempo 15). |
| U3.18 | `trampolinwal` Körper aus Teilen (`PartLayout`: Kopf, Rumpf, Schwanz-`Chain`, Flossen). |
| U3.19 | Rücken als Trampolin: Spieler landet oben → Sprung ×2. |
| U3.20 | `glibberkuh`: `passive`, folgt dem Spieler in < 60 px, stirbt in Sirup nach 3 s; Ziel = Gegenküste. |
| U3.21 | Sprites `trampolinwal_*` (Teile), `glibberkuh`. |

## U4 Krümelreich

| Schritt | Konkret |
| --- | --- |
| U4.01 | `kruemel`, `brosel`, `zucker`, `karamell`, `honig`, `fliese`, `staubfluse`. |
| U4.02 | Krümel + Explosion → Brösel; Zucker + Feuer → Karamell; Karamell erstarrt (hart); Staubfluse sehr brennbar; Honig zäh. |
| U4.03 | Breit 3072×1024, oben Küchenboden, unten Bau: `split_regions("vertical", ("fliesenwueste", "unter_kuehlschrank", "ameisenbau"))` – Fliesenwüste und Kühlschrank nebeneinander in der oberen Hälfte (eigenes Layout `"top_split"` in U0.03 nachtragen, Karte **U4.22**, Code S, vorher). |
| U4.04 | Fliesenwüste: riesige Krümel, Zuckerkörner, eine Erbse als Fels (Kreis aus `rock`); Fliesenfugen (Fliese mit Lücken); Kühlschrank: dunkel, Staubflusen; Ameisenbau: Gänge + Kammern + Königinnenkammer (= Arena). |
| U4.05 | Arena „Teetasse (Rand als Wände, Teesatz am Boden)“ – auf Bossplatz statt Königinnenkammer. Licht oben 0,7, im Bau 0,2 (Licht je Region: `Universe.ambient` als Startwert, Region-Parameter `ambient`). |
| U4.06 | `ameisenkrieger`: `hostile`; `pack`, `hunt`, `melee`, `dig` (Brösel, Krümel). |
| U4.07 | Duftspur: `hunt` bevorzugt Zucker-Zellen und den Kolben mit Ameisenduft (Spieler hält ihn → Spieler ist Ziel auch ohne Sicht). |
| U4.08 | `blattlaus`: `passive`; `graze` (Pflanzenmaterial: `GRAZE_MATERIAL["blattlaus"] = "kruemel"`, bis Bibel anderes sagt – als offene Frage notieren). |
| U4.09 | Schutz: Treffer an Blattlaus → alle `ameisenkrieger` in 300 px `aggro` (Ereignis-Hörer). |
| U4.10 | Ereignis `riesenschritt`: alle 80 s, 3 s Schatten-Ankündigung am Boden, dann Streifen (Breite 120 px) Zellen zusammendrücken (Luft im Streifen bis 60 px Höhe durch Nachbarmaterial füllen), Kamerawackeln, Cloita-Zustand `tiny_scared`. |
| U4.11 | `rule_tiny` Rang 3: Riesenschritt doppelt so oft (Ereignis liest Rang). Große, zähe Wassertropfen: Wasser-Viskosität im Satz erhöhen. |
| U4.12 | „Füttere die Blattläuse, ohne dass die Ameisen dich sehen“ → Proben ×2; Füttern = Zucker in 20 px Nähe einer Blattlaus gießen; scheitert, wenn ein Ameisenkrieger den Spieler sieht. |

## U5 Sporenklub

| Schritt | Konkret |
| --- | --- |
| U5.01 | `pilzfleisch`, `pilzhut`, `leuchtsporen`, `neonsaft`, `nebel`. |
| U5.02 | Pilzhut federt (wie Glibber, schwächer); Leuchtsporen und Neonsaft leuchten (`GLOW`); Nebel verdeckt Sicht. |
| U5.03 | Quadrat 2048×1536, `split_regions("vertical", ("lautsprechertuerme", "tanzflaeche", "hinterzimmer"))`. |
| U5.04 | Tanzfläche: offene Kavernen, Lichtorgeln (Leuchtsporen-Quellen); Hinterzimmer: enge Gänge; Lautsprechertürme: vertikale Schächte aus Pilzhüten. |
| U5.05 | Arena „Hauptbühne mit DJ-Pult und Lautsprechertürmen“. Licht 0,15. |
| U5.06 | `tuersteherpilz`: `neutral`; `stationary`, `shield`, `melee`, `retaliate`. |
| U5.07 | steht an Durchgängen (Spawnpunkt = schmalste Stelle eines Gangs, Funktion `place_at_chokepoints`). |
| U5.08 | `sporenschnorrer`: `hostile`; `steal`, `flee`. |
| U5.09 | Zustände `steal`, `carry`; bevorzugt das Hinterzimmer. |
| U5.10 | Ereignis `bass_drop`: alle 60 s Körper und lose Gegenstände +40 px hoch, Pulver hüpft (Pulverzellen in Simulationszone 1–3 px nach oben versetzen). |
| U5.11 | `rule_beat`: Kreaturen bewegen sich im Takt (Bewegung nur in den ersten 50 % jedes Takts) und Rang 3: Gegner nehmen außerhalb des Beats nur 50 % Schaden. |
| U5.12 | „Tanz mit mir!“ (5 Sprünge genau auf dem Beat; Ereignis `jump` + `rule.on_beat()`) → Neonsaft-Kolben + 80 Gold. |
| U5.17 | `pilzfleisch` wächst auf jeden 8. Beat in Luft (Hörer auf `beat`). |
| U5.18 | Leuchtsporen einatmen → `drunk`; Neonsaft trinken → Tempo-Schub (Status `drunk` neu, Bibel 02, Karte **U5.19**, Code S, vorher). |

## U6 Versunkene Abtei

| Schritt | Konkret |
| --- | --- |
| U6.01 | `mauerwerk`, `buntglas`, `kerzenwachs`, `glockenbronze`, `algen`, `weihrauch`. |
| U6.02 | Buntglas zerspringt in Splitter (Debris, schneidet: Gefahr-Schaden); Feuer schmilzt Kerzenwachs, erstarrt wieder; Algen wachsen langsam in Wasser; Glockenbronze leitet Strom. |
| U6.03 | Hoch 1280×2560, `split_regions("vertical", ("glockenturm", "kirchenschiff", "krypta"))`; Wasser ab Kirchenschiff. |
| U6.04 | Glockenturm trocken mit Glocke aus Glockenbronze; Kirchenschiff geflutet mit Luftblasen-Kapellen (Luftkammern unter Wasser); Krypta dunkel mit Strömung (Wasser-Strömungsparameter, falls die Engine keine hat: offene Frage). |
| U6.05 | Kerzen als Lichtpunkte (Glow-Zellen). Arena laut Bibel 05 „Abt Kieme“. |
| U6.06 | `moenchsfisch`: `neutral`; `pack`, `ranged` (Blasenstrahl), `retaliate`. |
| U6.07 | Chor: Gruppe schießt gleichzeitig (Takt der Gruppe). |
| U6.08 | `orgelaal`: `hostile`; `hunt` (nur im Wasser), `ranged` (Stromstoß, Ausholen 0,7 s). |
| U6.09 | Körper aus Segmenten (`Chain`, 28×6); Ausholen-Leuchten von hinten nach vorne. |
| U6.10 | Ereignis `glockenschlag`: alle 75 s, Vorläuten 2 s, Stromschlag für alle Körper in Wasser. |
| U6.11 | `rule_flooded` Rang 3: Wasser steigt alle 60 s um 20 px. |
| U6.12 | „Läute die Glocke dreimal, ohne den Kraken zu wecken“ → Selbstexperiment-Neuwurf gratis. |
| U6.17 | `kirchenkrake` Werte: `hostile` in ihrer Kammer, sonst schlafend. |
| U6.18 | Schlaf + Lärm: Lärmpegel aus Explosionen/Glocke (Hörer), weckt bei Schwelle. |
| U6.19 | Körper aus Teilen (Mantel, 6 `Tentacle`, Augen). |
| U6.20 | Weihrauch: Gegner „benebelt“ (Streuung ×2 für 5 s). |
| U6.21 | Sprites `kirchenkrake_*`. |
