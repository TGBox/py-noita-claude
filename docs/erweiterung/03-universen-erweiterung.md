# 03 – Die sechs Pool-Universen der Erweiterung

Dieses Kapitel definiert die sechs vollwertigen Pool-Universen der Phase 2 (`schrott`, `kuchen`, `spule`, `uhrwerkwueste`, `suppenmeer`, `freizeitpark`). Sie nutzen die vier kanonischen Bibel-Weltformen und besitzen eine verbindliche **Rang-Steigerung für Ränge 1 bis 3**.

Dieses Kapitel ist die **einzige Quelle** für diese sechs Universen (Bibel 03 verweist nur hierher). Sie gehören nicht zum MVP (Phasen A–G) und werden in Phase J gebaut. Die Regel `rule_electric` (Spule) ist neu und wird in Phase J in die Regelbibliothek (Bibel 02) aufgenommen; ihre Universums-Fraktionen ergänzen `UNIVERSE_FACTIONS` (Vertrag V4) erst dann.

---

## 1. Der Große Schrott (`schrott`)

- **Pitch:** „Ein endloser Friedhof interdimensionaler Maschinen. Alles rostet, knistert und zieht magnetisch an.“
- **Regel:** `rule_magnet` – Metall zieht Geschosse und Trümmer an; Roststaub brennt explosionsartig.
- **Form:** Breit, 3072×1024. **Licht:** 0,42.
- **Teilgebiete:** Schrotthalde (lockeres Altmetall), Schmelze (Flüssigeisen-Rinnen), Kernwerk (rotierende Magnetspulen).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `altmetall` | Altmetall | fest | hart | #706558 | leitend, reflektiert Querschläger |
  | `roststaub` | Roststaub | Pulver | weich | #B55030 | brennt blitzartig bei Funken |
  | `fluessigeisen` | Flüssigeisen | flüssig, heiß | – | #FF7020 | schmilzt weiche Feststoffe; verbrennt Fleisch |
  | `magnetit` | Magnetiterz | fest | sehr hart | #303038 | zieht Projektile im 32-px-Radius an |

- **Rang-Steigerung von `rule_magnet`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Magnetkraft schwach (15 px) | Magnetkraft verdoppelt (30 px) | Magnetkraft 45 px; Waffen werden magnetisch angezogen |

- **Einheimische:** Rostkäfer (`rostkaefer`), Schweiß-Imp (`schweissimp`), Magnetwurm (`magnetwurm`), Schrottgolem (`schrottgolem`).
- **Unter-Zwischenboss:** Gabelstapler-Krabbe (`gabelstapler_krabbe`). **Hauptboss:** Die Schrottpresse (`schrottpresse`).
- **Props:** Magnetkran (`magnet_kran`), Batteriesäule (`batterie_saeule`).
- **Ereignis „Magnetsturm“:** Alle 90 s werden Metallpartikel für 15 s quer über den Schirm geweht.
- **Proben:** Rostprobe (`probe_rost`), Magnetit-Splitter (`probe_magnetit`).
- **Arena:** Rechteckige Stahlhalle mit zwei beweglichen Pressblöcken.

---

## 2. Die Kuchenkruste (`kuchen`)

- **Pitch:** „Gebacken vor einer Million Jahren. Oben knusprige Baisers, unten kochendes Karamell.“
- **Regel:** `rule_hot` – Dauerhitze; weiche Substanzen schmelzen; Zucker karamellisiert bei Brand.
- **Form:** Quadrat, 2048×1536. **Licht:** 0,65.
- **Teilgebiete:** Glasur-Kamm (Puderzucker, Baisers), Biskuit-Höhlen (poröser Teig), Karamell-Tiefe (heiß und zäh).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `biskuit` | Biskuitteig | fest | weich | #E8C07A | saugt Flüssigkeiten wie ein Schwamm auf |
  | `zuckerglasur` | Zuckerglasur | fest | hart | #FFF5EA | schmilzt bei Feuer zu Sirup |
  | `karamell_kuchen` | Kochendes Karamell | flüssig, zäh | – | #B86014 | brennt lang, klebt an den Füßen |
  | `puderzucker` | Puderzucker | Pulver | weich | #FFFFFF | Mehlstaub-Detonation bei Funken |

- **Rang-Steigerung von `rule_hot`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Entzündungs-Chance 1 % | Chance 3 %; Karamell kocht heißer | Chance 5 %; Puderzucker explodiert doppelt so groß |

- **Einheimische:** Zuckerspinne (`zuckerspinne`), Kerzenkobold (`kerzenkobold`), Marzipanschwein (`marzipanschwein`), Baiser-Geist (`baiser_geist`).
- **Unter-Zwischenboss:** Marzipanritter (`marzipan_ritter`). **Hauptboss:** Die Hochzeitstorte (`hochzeitstorte`).
- **Props:** Riesenkerze (`riesen_kerze`), Keksrad (`keks_rad`).
- **Ereignis „Karamell-Geysir“:** Alle 80 s schießen heiße Karamell-Fontänen empor.
- **Proben:** Zuckerkruste (`probe_zucker`), Marzipan-Nase (`probe_marzipan`).
- **Arena:** Runde Tortenplatte; herabfallende Baiser-Brocken bieten Schutz.

---

## 3. Die Summende Spule (`spule`)

- **Pitch:** „Ein Alptraum aus blanken Kupferdrähten und permanenten Hochspannungs-Entladungen.“
- **Regel:** `rule_electric` – Ströme leiten 2× weiter; Funken laden Schilde; Kurzschlüsse entzünden Gas.
- **Form:** Hoch, 1280×2560. **Licht:** 0,38.
- **Teilgebiete:** Spulenwald (vertikale Kupferwicklungen), Kondensatordeck (Spannungskammern), Plasmakern (Hitzezone).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `kupfer` | Kupferdraht | fest | hart | #C87540 | leitet Strom widerstandsfrei weiter |
  | `isolator` | Isolierkeramik | fest | hart | #4A5568 | blockiert jeden Stromfluss |
  | `plasma` | Plasmagas | Gas, glühend | – | #70E0FF | verbrennt Projektile und Fleisch |
  | `elektrolyt` | Elektrolytlösung | flüssig | – | #40FFA0 | erzeugt Schockwellen bei Stromschlag |

- **Rang-Steigerung von `rule_electric`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Strom leitet +50 % weiter | Strom leitet +100 %; Funken springen weiter | Ströme springen durch die Luft auf nahe Feinde |

- **Einheimische:** Funkenhornisse (`funkenhornisse`), Spulenkrabbe (`spulenkrabbe`), Kupferschlange (`kupferschlange`), Kondensator-Geist (`kondensator_geist`).
- **Unter-Zwischenboss:** Spulenmeister (`spulenmeister`). **Hauptboss:** Der Transformator (`transformator`).
- **Props:** Trafo-Kasten (`trafo_kasten`), Blitzableiter (`blitzableiter`).
- **Ereignis „Kurzschluss“:** Alle 70 s zucken Blitz-Kaskaden quer durch die Kupferleitungen.
- **Proben:** Kupferspule (`probe_spule`), Kondensator-Zelle (`probe_kondensator`).
- **Arena:** Faraday-Käfig mit beweglichen Elektroden.

---

## 4. Die Uhrwerkwüste (`uhrwerkwueste`)

- **Pitch:** „Ein Meer aus tickendem Zahnradsand. Zeit ist hier eine zähe Flüssigkeit.“
- **Regel:** `rule_slowtime` – Zeit pulsiert im Takt; Geschosse ziehen Verzögerungs-Echos hinter sich her.
- **Form:** Breit, 3072×1024. **Licht:** 0,50.
- **Teilgebiete:** Zahnrad-Dünen (Messingsand), Gruft der Sekunden (tickende Pendel), Chrono-Oase (Zeit-Teiche).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `chrono_sand` | Zeitensand | Pulver | weich | #E0C070 | rieselt träge; dämpft Stürze |
  | `messing` | Zahnradmessing | fest | sehr hart | #D4AF37 | extrem stabil; reflektiert Funken |
  | `fluessig_zeit` | Flüssige Zeit | flüssig | – | #C0D8E8 | bremst alles darin auf 25 % Tempo |
  | `unruh_fett` | Uhrenöl | flüssig | – | #8A7030 | extrem rutschig; entflammbar |

- **Rang-Steigerung von `rule_slowtime`:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Tempo pulsiert 80–100 % | Tempo pulsiert 60–100 % | Tempo pulsiert 40–100 %; Projektile frieren kurz ein |

- **Einheimische:** Zecken-Uhr (`zecken_uhr`), Pendel-Schreiter (`pendel_schreiter`), Chrono-Wächter (`chrono_waechter`), Sanduhr-Skarabäus (`sanduhr_skarabaeus`).
- **Unter-Zwischenboss:** Der Unruh-Vogel (`unruh_vogel`). **Hauptboss:** Das Ewige Pendel (`ewiges_pendel`).
- **Props:** Standuhr (`stand_uhr`), Federwerk (`feder_werk`).
- **Ereignis „Zeitsprung“:** Alle 90 s werden alle Projektile für 2 Sekunden eingefroren.
- **Proben:** Unruh-Feder (`probe_unruh`), Chrono-Tropfen (`probe_chrono`).
- **Arena:** Großes Ziffernblatt mit rotierenden Messing-Zeigern als Plattformen.

---

## 5. Das Endlose Suppenmeer (`suppenmeer`)

- **Pitch:** „Ein siedender Ozean aus Gemüsesuppe. Buchstabennudeln formen verzweifelte Worte.“
- **Regel:** `rule_flooded` (Sonderform Suppe) – Hoher Auftrieb; Suppenfett brennt oben; Atemleiste greift.
- **Form:** Hoch, 1280×2560. **Licht:** 0,35.
- **Teilgebiete:** Brühe-Spiegel (schwimmende Kräuterinseln), Sellerie-Riff (massives Gemüse als Wände), Tiefer Topf (dunkler Bodensatz).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `bouillon` | Fleischbrühe | flüssig | – | #E5C158 | verleiht Auftrieb; trinken erfrischt Flux |
  | `suppenfett` | Suppenfett | flüssig, leicht | – | #FFF090 | schwimmt immer oben; brennt heiß |
  | `nudel_teig` | Nudelteig | fest | weich | #F5E0A0 | federt Stöße ab; löst sich in kochendem Wasser |
  | `pfefferdampf` | Pfeffergas | Gas | – | #4A4030 | blendet Feinde (-30 % Trefferchance) |

- **Rang-Steigerung:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | Atem 16 s | Atem 12 s | Atem 9 s; Brühe kocht periodisch auf |

- **Einheimische:** Suppenlaus (`suppenlaus`), Buchstaben-Krake (`buchstaben_krake`), Karotten-Aal (`karotten_aal`), Markbällchen-Krabbe (`markbaellchen_krabbe`).
- **Unter-Zwischenboss:** Der Chefkoch-Ghul (`chefkoch_ghul`). **Hauptboss:** Der Kellen-Leviathan (`kellen_leviathan`).
- **Props:** Suppenschüssel (`suppen_schuessel`), Nudelholz (`nudel_holz`).
- **Ereignis „Wallendes Kochen“:** Alle 75 s reißen aufsteigende Dampfblasen Entitäten nach oben.
- **Proben:** Buchstabennudel A (`probe_nudel_a`), Getrocknete Nelke (`probe_nelke`).
- **Arena:** Emaille-Kasserolle mit seitlichen Hitzeventilen.

---

## 6. Freizeitpark Endzeit (`freizeitpark`)

- **Pitch:** „Seit Jahrhunderten geschlossen. Die Maskottchen haben Hunger und die Achterbahn fährt noch immer.“
- **Regel:** `rule_bounce` (Sonderform Dynamik) – Extrem rutschige Schienen; Projektile federn stark ab.
- **Form:** Breit, 3072×1024. **Licht:** 0,55.
- **Teilgebiete:** Geisterbahn (schwarze Tunnel), Kirmesplatz (Wurfbuden), Achterbahn-Looping (Schienen im Himmel).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `rost_schiene` | Achterbahnschiene | fest | hart | #805040 | beschleunigt rutschende Figuren um 60 % |
  | `zuckerwatte_rot` | Zuckerwatte | Pulver, leicht | weich | #FF80A0 | explodiert in rosa Rauchwand |
  | `helium_gas` | Helium | Gas | – | #E0FFFF | hebt Objekte an |
  | `spiegel_glas` | Spiegelglas | fest | spröde | #B0C4DE | zerspringt in schneidende Scherben |

- **Rang-Steigerung:**

  | Rang 1 | Rang 2 | Rang 3 |
  | --- | --- | --- |
  | +2 Abpraller | +3 Abpraller; Schienen schneller | +4 Abpraller; leere Loren rasen durch die Gänge |

- **Einheimische:** Geisterbahn-Clown (`geisterbahn_clown`), Leer-Kostüm (`leer_kostuem`), Popcorn-Drohne (`popcorn_drohne`), Autoscooter-Käfer (`autoscooter_kaefer`).
- **Unter-Zwischenboss:** Der Losverkäufer (`los_verkaeufer`). **Hauptboss:** Der Achterbahn-Drache (`achterbahn_drache`).
- **Props:** Karussellpferd (`karussell_pferd`), Popcorn-Maschine (`popcorn_maschine`).
- **Ereignis „Freie Fahrt“:** Alle 90 s heulen Sirenen auf und leere Loren rasen durch Schienenabschnitte.
- **Proben:** Kirmes-Chip (`probe_kirmes_chip`), Glasierter Apfel (`probe_apfel`).
- **Arena:** Looping-Geflecht mit schwingenden Gondeln als Deckung.
