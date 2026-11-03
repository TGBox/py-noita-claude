# 06 – Handgefertigte Satire-Universen (Teil 1)

Dieses Kapitel spezifiziert sechs handgefertigte Satire-Universen der Phase 3. Jedes Universum besitzt eine verbindliche **Rang-Steigerung für Ränge 1 bis 3**, nutzt die kanonischen Weltformen der Bibel und verzichtet auf schwerfällige Gimmicks.

---

## 1. Der Beamten-Park (`anatomie_park`)

- **Pitch:** „Ein Vergnügungspark im Magen-Darm-Trakt eines 500 Meter großen, schlafenden Ober-Regierungsrats.“
- **Regel:** `rule_peristaltik` – Rhythmische Druckwellen (alle 15 s) erzeugen starke physikalische Schubkräfte durch die Röhren; Gallenbecken sprudeln bei zu viel Lärm.
- **Form:** Breit, 3072×1024. **Licht:** 0,32.
- **Teilgebiete:** Lungen-Karussell (Alveolen-Plattformen), Magen-Achterbahn (Gallen-Wasserfälle), Blinddarm-Geisterbahn (enge Sackgassen).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `speisebrei` | Halbbeschlossener Antrag | flüssig, zäh | – | #C8B060 | bremst Bewegung um 50 % |
  | `gallenstein_beton` | Beamten-Gallenstein | fest | sehr hart | #4A6030 | säurefest; reflektiert Projektile |
  | `nervenstrang` | Reizleiter-Kabel | fest | weich | #FFE090 | leitet Strom und leuchtet bei Beschädigung |
  | `magensaft_limo` | Prickelnde Galle | flüssig | – | #70E020 | ätzt organisches Gewebe an |

- **Rang-Steigerung von `rule_peristaltik`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Schubkraft mäßig (Intervall 18 s) | Schubkraft hoch (12 s); Galle spritzt weiter | Schubkraft extrem (8 s); Wände scheiden Magensaft aus |

- **Einheimische:** Achterbahn-Bakterie (`achterbahn_bakterie`), Sicherheits-Leukozyt (`sicherheits_leukozyt`), Karies-Schrecken (`karies_schrecken`), Ticket-Bandwurm (`ticket_bandwurm`).
- **Unter-Zwischenboss:** Der Karussell-Polyp (`karussell_polyp`). **Hauptboss:** Dr. Pfortader (`dr_pfortader`).
- **Props:** Knorpel-Drehkreuz (`knorpel_drehkreuz`), Popcorn-Zyste (`popcorn_zyste`).
- **Ereignis „Sodbrennen“:** Alle 80 s steigt der Magensaft-Spiegel kurzzeitig an.
- **Proben:** Park-Eintrittskarte (`probe_park_ticket`), Gallenstein-Murmel (`probe_gallenstein_murmel`).
- **Arena:** Der Magengrund mit herabfallenden Knorpel-Gondeln.

---

## 2. Klonitas Pastell-Hölle (`pastell_hoelle`)

- **Pitch:** „Einst als harmloses Zuckerwatten-Paradies erschaffen. Nach zweihundert Jahren Isolation haben die Plüschtiere Zähne bekommen.“
- **Regel:** `rule_kitsch_carnage` – Alles wirkt quietschbunt und harmlos. Doch sobald Blut oder Kampfschaden den Boden berührt, verfallen Stofftiere in Raserei (+100 % Tempo, schrille Kicher-Laute).
- **Form:** Inseln, 2560×1280. **Licht:** 0,75.
- **Teilgebiete:** Plüsch-Sumpf (Schaumstoffmoore), Zuckerstangen-Wald (scharfe Pfefferminz-Pfähle), Bonbon-Schlucht (glatte Kandisklippen).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `schaumstoff` | Schaumstoffwolle | fest | weich | #FFA0D0 | fängt leicht Feuer; brennt mit rosa Qualm |
  | `erdbeermilch` | Erdbeermilch | flüssig | – | #FFCCD8 | verleiht +20 % Tempo und Schutzschild |
  | `zuckerglas_scherbe` | Kandisscherben | Pulver, scharf | hart | #C0FFFF | schneidet bei schnellem Laufen |
  | `honigkleber` | Riesen-Gummibärchenmasse | zähflüssig | – | #FF8000 | klebt Figuren am Boden fest |

- **Rang-Steigerung von `rule_kitsch_carnage`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Raserei +50 % Tempo | Raserei +100 % Tempo und Schaden | Raserei dauerhaft aktiv; Stofftiere teilen sich |

- **Einheimische:** Fangzahn-Teddy (`fangzahn_teddy`), Lakritz-Schlange (`lakritz_schlange`), Stoff-Kobold (`stoff_kobold`), Einhorn-Hyäne (`einhorn_hyaene`).
- **Unter-Zwischenboss:** Der Flicken-König (`flicken_koenig`). **Hauptboss:** Das Ur-Kuscheltier (`ur_kuscheltier`).
- **Props:** Riesen-Lutscher (`riesen_lutscher`), Spieluhr (`spiel_uhr`).
- **Ereignis „Kuschel-Alarm“:** Alle 90 s ertönt eine scheppernde Spieluhr; Plüschtiere stürmen synchron auf Cloita zu.
- **Proben:** Abgerissenes Knopfauge (`probe_knopfauge`), Watte-Bausch (`probe_watte`).
- **Arena:** Ein verstaubtes Kinderzimmer mit Riesen-Bauklötzen.

---

## 3. Das Klonenberg-Desaster (`klonenberg_welt`)

- **Pitch:** „Hier ging ein einfacher Hustensaft-Versuch schief. Jetzt besteht die gesamte Welt aus amorphen Klumpen mit zu vielen Ellenbogen.“
- **Regel:** `rule_mutation_ooze` – Berührung mit Mutagen-Sud verleiht temporäre Mutationen (drittes Bein = +40 % Tempo, Glotzauge = Radarsicht, Tentakel = Nahkampfpeitsche).
- **Form:** Quadrat, 2048×1536. **Licht:** 0,40.
- **Teilgebiete:** Schleimhaut-Vorstadt (überwachsene Häuser), Ellenbogen-Tal (Knochenauswüchse), Epizentrum (kochender DNA-Krater).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `mutagen_schleim` | Mutagen-Sud | flüssig | – | #30E070 | mutiert Figuren bei Kontakt |
  | `wucherndes_fleisch` | Hyper-Gewebe | fest | weich | #A04060 | wächst explosionsartig bei Erhitzung |
  | `augen_fett` | Sehorgan-Gelee | flüssig | – | #FFF0A0 | extrem glatt; erhöht Sichtweite |
  | `knochen_dorn` | Spontan-Knorpel | fest | hart | #E0DAC8 | schießt bei Erschütterung empor |

- **Rang-Steigerung von `rule_mutation_ooze`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Mutationen dauern 15 s | Mutationen dauern 25 s | Mutationen permanent bis zum nächsten Portal |

- **Einheimische:** Ellenbogen-Mantis (`ellenbogen_mantis`), Schrei-Knäuel (`schrei_knaeuel`), Zungen-Drohne (`zungen_drohne`), Drei-Kopf-Wesen (`drei_kopf_wesen`).
- **Unter-Zwischenboss:** Die Fusions-Beamtin (`fusions_beamtin`). **Hauptboss:** Das Klonenberg-Monstrum (`klonenberg_monstrum`).
- **Props:** DNA-Brutschrank (`dna_schrank`), Mutations-Blase (`mutations_blase`).
- **Ereignis „Zellteilungs-Welle“:** Alle 75 s verdoppeln sich Feinde für 15 s, bevor sie in Schleim platzen.
- **Proben:** Instabile DNA-Helix (`probe_dna`), Verkümmertes Ohr (`probe_ohr`).
- **Arena:** Der Grund eines eingestürzten Labors mit Riesen-Zungen.

---

## 4. Der Kosmische Talentwettbewerb (`talent_kosmos`)

- **Pitch:** „Ein gigantischer, im Himmel schwebender Beamten-Kopf verlangt: 'ZEIGT MIR, WAS IHR KÖNNT!' Wer langweilt, wird pulverisiert.“
- **Regel:** `rule_show_me` – Alle 60 Sekunden startet ein 15-sekündiger **Hype-Check**: Durch Waffenschüsse, Saltos und Explosionen muss der Hype-Balken gefüllt werden, sonst scannt der Desintegrationslaser die Plattform.
- **Form:** Breit, 3072×1024. **Licht:** 0,60.
- **Teilgebiete:** Backstage-Traversen (Kabel und Gerüste), Die Hauptbühne (Mikrofonsockel), Der Verlierer-Graben (Aschehaufen).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `buehnen_gold` | Show-Lametta | fest | weich | #FFD700 | flattert im Wind; spiegelt Licht |
  | `schall_kristall` | Bass-Kristall | fest | spröde | #7030A0 | explodiert in Schockwellen bei Treffern |
  | `applaus_nebel` | Kunstnebel | Gas | – | #E0E0FF | dämpft Schaden um 25 % |
  | `jury_plasma` | Laser-Rückstand | Energie | – | #00FFFF | löscht weiche Feststoffe blitzartig aus |

- **Rang-Steigerung von `rule_show_me`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Hype-Schwelle 60 Punkte | Schwelle 90 Punkte; Laser breiter | Schwelle 120 Punkte; Laser feuert doppelt |

- **Einheimische:** Tanz-Drohne (`tanz_drohne`), Schiedsrichter-Auge (`richter_auge`), Show-Kultist (`show_kultist`), Beat-Boxer (`beat_boxer`).
- **Unter-Zwischenboss:** Der Talent-Scout (`talent_scout`). **Hauptboss:** Der Kosmische Jury-Kopf (`jury_kopf`).
- **Props:** Bühnen-Lautsprecher (`buehnen_box`), Scheinwerfer (`scheinwerfer`).
- **Ereignis „RICHTERSPRUCH“:** Der Laser tastet für 5 s die Arena ab.
- **Proben:** Goldenes Stimmband (`probe_stimmband`), Zersprungene Brille (`probe_jury_brille`).
- **Arena:** Schwebende Open-Air-Bühne im Weltall.

---

## 5. Das Rohrpost-Labyrinth (`antrags_labyrinth`)

- **Pitch:** „Ein gigantisches Labyrinth aus endlosen Aktenschränken und saugenden Rohrpost-Schächten, die alles verschlingen.“
- **Regel:** `rule_pneumatics` – Pneumatische Röhren saugen Projektile, Gase und Figuren an und katapultieren sie mit hoher Wucht quer durch den Raum.
- **Form:** Breit, 3072×1024. **Licht:** 0,48.
- **Teilgebiete:** Die Hauptsortierhalle (riesige Röhrenbündel), Der Stempel-Flur (mechanische Fallbeile), Das Endlager B-12 (staubige Aktenberge).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `rohrpost_blech` | Zink-Rohrleitung | fest | hart | #7A8898 | unzerstörbar; führt Sogströmungen |
  | `stempellack_rot` | Trockener Siegellack | fest | spröde | #A82030 | splittert bei Treffern in Stempelfarbe |
  | `sortier_druckluft` | Pneumatik-Wind | Gas | – | #D0E8FF | drückt Geschosse mit 2-fachem Tempo |
  | `lochstreifen` | Lochkarten-Papier | fest | weich | #EAE4D2 | brennt extrem schnell mit Funkenflug |

- **Rang-Steigerung von `rule_pneumatics`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Sauggeschwindigkeit normal | Saugkraft +50 %; Röhren feuern schneller | Röhren saugen auch feste Brocken ein |

- **Einheimische:** Rohrpost-Marder (`rohrpost_marder`), Stempel-Golem (`stempel_golem`), Lochkarten-Krabbe (`lochkarten_krabbe`), Sortier-Drohne (`sortier_drohne`).
- **Unter-Zwischenboss:** Der Haupt-Archivar (`haupt_archivar`). **Hauptboss:** Die Pneumatische Sortiermaschine (`sortier_maschine_boss`).
- **Props:** Rohrpost-Station (`rohrpost_station`), Aktenkiste (`akten_kiste`).
- **Ereignis „Druckstoß“:** Alle 80 s entleeren sich alle Röhren gleichzeitig in einer gewaltigen Druckwelle.
- **Proben:** Messing-Kapsel (`probe_messing_kapsel`), Gelochter Streifen (`probe_lochstreifen`).
- **Arena:** Eine runde Halle mit 8 Rohrpost-Mündungen an den Wänden.

---

## 6. Das Krawatten-Imperium (`krawatten_planet`)

- **Pitch:** „Eine Welt, die vollständig von intelligenten Krawatten regiert wird. Sie schicken Zeitreise-Agenten, um offene Hemdkragen auszurotten.“
- **Regel:** `rule_temporal_ties` – Wird eine Krawatte besiegt, öffnet sich nach 5 s ein Zeit-Riss, aus dem ein schneller Zeitreise-Schlips schlüpft, um Rache zu nehmen.
- **Form:** Hoch, 1280×2560. **Licht:** 0,50.
- **Teilgebiete:** Seidenstrang-Boulevard (moderne Bürotürme), Bügel-Kasernen (Trainingshallen), Chrono-Knoten-Labor (Zeitmaschinen-Basis).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `panzer_seide` | Titan-Seidengewebe | fest | sehr zäh | #1A2840 | wehrt Projektile ab; schwer entflammbar |
  | `zeitreise_tinte` | Tachyonen-Flüssigkeit | flüssig | – | #8000FF | teleportiert Objekte bei Kontakt um 40 px |
  | `manschetten_chrom` | Chromstahl | fest | hart | #D0E0E8 | leitet Strom; spiegelt Licht |
  | `buegel_dampf` | Heißer Bügeldampf | Gas | – | #FFFFFF | verbrennt und glättet zerknitterte Wände |

- **Rang-Steigerung von `rule_temporal_ties`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Zeitreisende erscheinen nach 6 s | Erscheinen nach 4 s mit Schilden | Erscheinen sofort und rufen Verstärkung |

- **Einheimische:** Schlips-Späher (`schlips_spaeher`), Fliegen-Drohne (`fliegen_drohne`), Chrono-Schlips (`chrono_schlips`), Manschetten-Panzer (`manschetten_panzer`).
- **Unter-Zwischenboss:** Der Windsor-Knoten (`windsor_knoten`). **Hauptboss:** Das Oberste Kragen-Tribunal (`kragen_tribunal`).
- **Props:** Krawattennadel-Säule (`nadel_saeule`), Dampfbügeleisen (`buegeleisen_prop`).
- **Ereignis „Zeitschleife“:** Alle 90 s friert das Geschehen für 2 Sekunden ein; Zeitechos erscheinen.
- **Proben:** Tachyonen-Manschette (`probe_tachyon_manschette`), Seidenfaden (`probe_seidenfaden`).
- **Arena:** Der Uhrenturm der Krawatten-Hauptstadt mit rotierenden Pendeln.
