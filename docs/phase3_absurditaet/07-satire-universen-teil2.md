# 07 – Handgefertigte Satire-Universen (Teil 2)

Dieses Kapitel spezifiziert sechs weitere handgefertigte Satire-Universen der Phase 3. Alle Universen besitzen vollständige **Rang-Steigerungstabellen für Ränge 1 bis 3** und respektieren die physikalischen Grenzen der Engine.

---

## 1. Das Heilige Sanitärium (`klo_paradies`)

- **Pitch:** „Ein atemberaubend friedlicher Zen-Garten im Niemandsland mit einem goldenen Thron. Wer ihn berührt, löst den Alarm aus.“
- **Regel:** `rule_sanctuary_retribution` – Alle Kreaturen sind zunächst absolut friedlich (`passive`), kein Kampflärm. Doch sobald der Thron-Altar betreten oder beschädigt wird, wechselt der Himmel in Alarmrot: Ein orbitrotes Abwehrsystem eröffnet das Feuer!
- **Form:** Quadrat, 2048×1536. **Licht:** 0,70.
- **Teilgebiete:** Zen-Kies-Terrassen (weißer Sand), Bambus-Schlucht (reine Quellbäche), Der Thron-Gipfel (erhabener Sockel).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `zen_kies` | Gebleichter Zen-Kies | Pulver | weich | #F4EEDC | dämpft Schritte; rieselt sanft |
  | `porzellan_edel` | Sakrales Porzellan | fest | sehr hart | #FFFFFF | prallt Geschosse ab; glänzt golden |
  | `heilquell_wasser` | Reines Quellwasser | flüssig | – | #A0F0FF | trinken beschleunigt Flux-Regeneration |
  | `laser_beton` | Abwehr-Sockelstein | fest | unzerstörbar | #2A2A38 | beherbergt verborgene Lasergeschütze |

- **Rang-Steigerung von `rule_sanctuary_retribution`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Abwehrsystem startet nach 5 s | Startet nach 3 s; Feuerrate +50 % | Startet sofort; feuert zielsuchende Laser |

- **Einheimische:** Sanfter Kolibri (`sanft_kolibri`), Moos-Schildkröte (`moos_kroete`), Porzellan-Wächter (`porzellan_waechter`), Spott-Drohne (`spott_drohne`).
- **Unter-Zwischenboss:** Der Zen-Gärtner (`zen_gaertner`). **Hauptboss:** Das Autonome Thron-Vergeltungssystem (`thron_abwehr_system`).
- **Props:** Kloschüssel-Schrein (`porzellan_thron`), Bambus-Brunnen (`bambus_brunnen`).
- **Ereignis „Hologramm-Spott“:** Ein gigantisches Hologramm am Himmel liest Cloitas peinlichste Laborpannen vor.
- **Proben:** Goldenes Klopapier (`probe_gold_papier`), Zen-Kiesel (`probe_zen_kiesel`).
- **Arena:** Der isolierte Gipfel mit dem goldenen Thron.

---

## 2. Die Simulations-Schachtel (`matroschka_simulation`)

- **Pitch:** „Ein Universum aus billigen Hologrammen und Pop-in-Wänden. Du bist in einer Simulation in einer Simulation gefangen.“
- **Regel:** `rule_low_cpu_glitch` – Die Physik spart Rechenleistung: Wände ploppen erst auf 60 px Nähe auf; getötete Feinde hinterlassen kurz T-Pose-Geister; Kisten lösen sich bei Berührung in Glitch-Pixel auf.
- **Form:** Quadrat, 2048×1536. **Licht:** 0,45.
- **Teilgebiete:** Wireframe-Korridor (Gitter-Räume), Low-Poly-Büros (eckige Tische), Der Server-Bunker (Schaltschränke im Vakuum).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `wireframe_wand` | Drahtgitter-Platte | fest | hart | #00FFA0 | flackert; wird bei Beschuss transparent |
  | `glitch_pixel` | Korrupter Byte-Schleim | flüssig | – | #FF00FF | invertiert kurzzeitig die Bewegungssteuerung |
  | `hologramm_nebel` | Render-Qualm | Gas | – | #4080A0 | verdeckt Sicht; Projektile fliegen ungestört durch |
  | `server_kupfer` | Datenleiter-Kabel | fest | weich | #C08040 | leitet Strom widerstandsarm |

- **Rang-Steigerung von `rule_low_cpu_glitch`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Pop-in-Distanz 70 px | Pop-in 50 px; Wände flackern | Pop-in 35 px; Feinde glitchen durch Schüsse |

- **Einheimische:** Zigerion-Betrüger (`zigerion_spion`), T-Pose-Zivilist (`t_pose_zivilist`), Glitch-Hund (`glitch_hund`), Ladekreis-Drohne (`ladekreis_drohne`).
- **Unter-Zwischenboss:** Der Simulations-Admin (`sim_admin`). **Hauptboss:** Der Zigerion-Chefbetrüger (`zigerion_chef`).
- **Props:** Fake-Tresor (`fake_tresor`), Absturz-Terminal (`absturz_terminal`).
- **Ereignis „Speichermangel“:** Alle 75 s friert das Geschehen für 1 s ein; Entitäten springen leicht nach vorn.
- **Proben:** Glitch-Pixel (`probe_glitch_pixel`), Gefälschter Bauplan (`probe_fake_plan`).
- **Arena:** Weißer Raum mit schwebendem Ladebalken.

---

## 3. Das Büro-Kollektiv Einheit 404 (`kollektiv_buerokratie`)

- **Pitch:** „Eine Bürostadt unter einem Schwarm-Verstand. Alle lächeln. Alle trinken zur selben Sekunde Kamillentee.“
- **Regel:** `rule_hive_mind` – Alle Feinde in einem Raum teilen sich einen gemeinsamen **Schwarm-Lebensbalken**! Trifft man einen, spüren es alle. Greift einer an, greifen alle synchron an.
- **Form:** Breit, 3072×1024. **Licht:** 0,55.
- **Teilgebiete:** Schwarm-Zentrale (synchron tippende Pulte), Gemeinschafts-Kantine (Reihen mit Tee), Synapsen-Schacht (violette Kabel).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `synapsen_kabel` | Bio-Nervenfaser | fest | weich | #8A30B0 | verbindet Möbel; leitet Schaden an Nachbarn |
  | `kamillentee` | Beruhigungstee | flüssig | – | #D8C040 | beruhigt Figuren; senkt Aggro |
  | `linoleum_grau` | Amts-Linoleum | fest | hart | #7A8088 | isoliert elektrisch; leicht zu reinigen |
  | `aktenstapel_rein` | Geordnete Akten | fest | weich | #F0EAD6 | brennt langsam mit weißem Rauch |

- **Rang-Steigerung von `rule_hive_mind`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Schwarm-Radius 100 px | Schwarm-Radius 160 px | Ganzer Raum teilt Lebensbalken & Angriffe |

- **Einheimische:** Synchron-Sekretär (`synchron_sekretaer`), Schwarm-Hausmeister (`schwarm_hausmeister`), Akten-Drohne (`kollektiv_drohne`), Kaffee-Verteiler (`kaffee_verteiler`).
- **Unter-Zwischenboss:** Der Abteilungs-Sprecher (`abteilungs_sprecher`). **Hauptboss:** Das Synapsen-Gehirn Einheit 404 (`einheit_404_hirn`).
- **Props:** Schwarm-Lautsprecher (`schwarm_lautsprecher`), Teekessel-Altar (`teekessel_altar`).
- **Ereignis „Kollektiver Seufzer“:** Alle 80 s seufzen alle Feinde synchron; eine Druckwelle dämpft Projektile.
- **Proben:** Schwarm-Synapse (`probe_schwarm_synapse`), Synchron-Stempel (`probe_synchron_stempel`).
- **Arena:** Runder Hauptkonferenzraum mit drehbarem Tisch.

---

## 4. Das Unsterblichkeits-Resort (`unsterblichkeits_resort`)

- **Pitch:** „Ein Luxus-Kurort unter einer Kraftfeld-Kuppel. Niemand kann sterben – dahinter wartet der Zahltag.“
- **Regel:** `rule_immortality_field` – Innerhalb des blauen Feldes sinkt kein LP unter 1. Doch **aller erlittene Schaden wird gestapelt**. Fliegt eine Figur durch eine Wand aus der Kuppel ins Freie, schlägt der gesamte gestapelte Schaden sofort ein!
- **Form:** Inseln, 2560×1280. **Licht:** 0,65.
- **Teilgebiete:** Spa- und Wellnessdeck (Thermalbäder), Die Rennbahn (Looping-Schienen), Das Niemandsland (karges Ödland außerhalb).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `feld_grenze` | Resonanz-Schleier | Energie | – | #40A0FF | Markierung der Unsterblichkeits-Grenze |
  | `thermal_wasser` | Schwefelbad-Wasser | flüssig, heiß | – | #50E0C0 | verleiht +15 % Geschwindigkeit |
  | `marmor_gold` | Luxus-Marmor | fest | hart | #EAE6DA | edel; reflektiert Projektile mit Goldglanz |
  | `zerfalls_sand` | Ödland-Sand | Pulver | weich | #5A4030 | außerhalb der Kuppel; ätzt Stiefel an |

- **Rang-Steigerung von `rule_immortality_field`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Kuppel ist 300 px groß | Kuppel ist 200 px groß | Kuppel schrumpft periodisch |

- **Einheimische:** Unsterblicher Urlauber (`unsterblich_urlauber`), Risiko-Junkie (`risiko_junkie`), Spa-Masseur (`spa_masseur`), Kraftfeld-Wurm (`kraftfeld_wurm`).
- **Unter-Zwischenboss:** Der Chefarzt des Resorts (`resort_chefarzt`). **Hauptboss:** Der Verschwörungs-Direktor (`resort_direktor`).
- **Props:** Whirlpool (`whirlpool_prop`), Liegestuhl (`liegestuhl_prop`).
- **Ereignis „Feld-Flackern“:** Alle 90 s flackert das Feld für 4 Sekunden – alle Feinde suchen Deckung.
- **Proben:** Unsterblichkeits-Chip (`probe_unsterblich_chip`), Spa-Handtuch (`probe_handtuch`).
- **Arena:** Aussichtsplattform direkt an der Kuppelgrenze.

---

## 5. Das Quanten-Scherbenmeer (`schroedinger_kammer`)

- **Pitch:** „Zeit pulsiert in Quanten-Phasen. Schrödingers Katzen schweben in Röhren und Zeit-Polizisten jagen Unschärfe-Sünder.“
- **Regel:** `rule_quantum_phase` – Die Welt wechselt alle 10 Sekunden zwischen **Phase Alpha und Phase Beta**: Bestimmte Wände und Hindernisse existieren nur in einer Phase; Projektile hinterlassen flüchtige Zeitechos.
- **Form:** Quadrat, 2048×1536. **Licht:** 0,40.
- **Teilgebiete:** Alpha-Kammer (Gegenwart), Beta-Ruinen (verfallene Gegenphase), Zeit-Vakuum (der Spalt dazwischen).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `quanten_glas` | Unschärfe-Glas | fest | spröde | #80E0FF | existiert nur in einer der beiden Phasen |
  | `tachyonen_schleim` | Zeit-Gel | flüssig | – | #C040FF | verlangsamt Bewegung um 60 % |
  | `unschaerfe_staub` | Schrödingers Asche | Pulver | weich | #A0A0A0 | verdoppelt Geschosse beim Durchflug |
  | `zeitpolizei_stahl` | Chrono-Monolith | fest | sehr hart | #303040 | absorbiert Laser und Projektile |

- **Rang-Steigerung von `rule_quantum_phase`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Phasenwechsel alle 12 s | Wechsel alle 8 s; Zeitechos aggressiver | Wechsel alle 5 s; Quanten-Risse ziehen Objekte an |

- **Einheimische:** Schrödingers Katze (`schroedinger_katze`), Zeitstrahl-Sünder (`zeit_suender`), Vektor-Käfer (`vektor_kaefer`), Zeitpolizei-Prügler (`zeitpolizei_pruegler`).
- **Unter-Zwischenboss:** Der Vierte-Dimensions-Schläger (`zeit_schlaeger`). **Hauptboss:** Das Kosmische Zeit-Polizist-Monster (`zeit_polizist_boss`).
- **Props:** Zeit-Kristall-Säule (`zeit_saeule`), Reagenzglas-Käfig (`reagenz_kaefig`).
- **Ereignis „Quanten-Kollaps“:** Alle 70 s verschmelzen beide Phasen kurzzeitig zu einem Raum.
- **Proben:** Quanten-Bartel (`probe_quanten_bartel`), Katzenhaare der Unschärfe (`probe_katzenhaar`).
- **Arena:** Plattform im Zeitstrudel mit gegenläufig tickenden Uhren.

---

## 6. Der Kater-Bunker (`kater_bunker`)

- **Pitch:** „Ein extrem tödlicher Rätsel-Dungeon, den eine betrunkene Cloita vor drei Tagen erbaut hat. Sie kann sich an keine Lösung erinnern.“
- **Regel:** `rule_drunk_puzzles` – Absurde Rätselräume mit Zeitdruck: Cloita muss Aufgaben lösen (z. B. „Wirf die Granate in den Korb“, „Lösche das Feuer mit dem Kolben“, „Drücke den roten Knopf“). Scheitern flutet den Raum mit Reizgas!
- **Form:** Breit, 3072×1024. **Licht:** 0,35.
- **Teilgebiete:** Basketball-Halle (Spielfeld mit Minen), Brauerei-Keller (kochende Hopfenbecken), Die Video-Zentrale (Monitore mit Sprachnachrichten).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `kater_beton` | Schmier-Beton | fest | hart | #505058 | mit Edding und Formeln bekritzelt |
  | `starkbier` | 18-prozentiges Bockbier | flüssig | – | #8A3810 | brennbar; trinken schwankt das Zielen |
  | `demuetigungs_glas` | Flutlicht-Glas | fest | spröde | #FFFFC0 | zerspringt in blendende Splitter |
  | `kater_giftgas` | Reizgas | Gas | – | #70A020 | verursacht kontinuierlichen Giftschaden |

- **Rang-Steigerung von `rule_drunk_puzzles`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Rätsel-Zeitlimit 35 s | Limit 25 s; Reizgas steigt schneller | Limit 15 s; Geschütztürme feuern mit |

- **Einheimische:** Kater-Kobold (`kater_kobold`), Rätsel-Roboter (`raetsel_roboter`), Scham-Geist (`scham_geist`), Video-Drohne (`video_drohne`).
- **Unter-Zwischenboss:** Der Sicherheits-Dackel (`sicherheits_dackel`). **Hauptboss:** Die Kater-KI „Betrunkene Cloita“ (`kater_cloita_ki`).
- **Props:** Basketballkorb (`basketball_korb`), Roter Demütigungsknopf (`rot_knopf_prop`).
- **Ereignis „Peinliche Rückblende“:** Lautsprecher spielen Cloitas betrunkene Sprachnachrichten an das Finanzamt ab.
- **Proben:** Kater-Aspirin (`probe_aspirin`), Edding-Kappe (`probe_edding`).
- **Arena:** Verhörraum mit zwei Klappstühlen und Riesen-Countdown an der Wand.
