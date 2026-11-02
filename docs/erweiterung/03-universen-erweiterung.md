# 03 – Die sechs Erweiterungs-Universen

Dieses Kapitel definiert die sechs neuen, vollwertigen Universen der Erweiterung (Phasen H–M). Jedes Universum folgt exakt der kanonischen Schnittstelle von `docs/bibel/03-universen.md` und verdoppelt den Gesamtkatalog des Spiels auf 12 Welten.

---

## 1. Der Große Schrott (`schrott`)

- **Pitch:** „Ein endloser Friedhof interdimensionaler Maschinen. Alles rostet, knistert und zieht magnetisch an.“
- **Regel:** `rule_magnet` – Metallische Geschosse und Trümmer werden von Schrottmagneten und Eisenerzadern angezogen; Roststaub explodiert bei Funkenflug.
- **Form:** Breit, 3072×1024: meterhohe Schrottberge, Förderbänder, Schreddergruben.
- **Licht:** 0,42, staubig-rostiges Dämmerlicht mit gelben Scheinwerfer-Kegeln.
- **Teilgebiete:** Schrotthalde (lockere Trümmer, Schrottberge), Schmelze (Flüssigeisen-Kanäle), Kernwerk (rotierende Magnetkräne und Transformatoren).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `schrott` | Altmetall | fest | hart | #706558 | leitend, reflektiert Querschläger |
  | `roststaub` | Roststaub | Pulver | weich | #B55030 | brennt explosionsartig bei Funken |
  | `fluessigeisen` | Flüssigeisen | flüssig, heiß | – | #FF7020 | schmilzt Feststoffe; verbrennt organisches Gewebe sofort |
  | `magnetit` | Magnetiterz | fest | sehr hart | #303038 | zieht Projektile im 30-px-Radius an |

- **Einheimische:** Rostkäfer (`rostkaefer`), Schweiß-Imp (`schweissimp`), Magnetwurm (`magnetwurm`), Schrottgolem (`schrottgolem`).
- **Unter-Zwischenboss:** Gabelstapler-Krabbe (`gabelstapler_krabbe`).
- **Hauptboss:** Die Schrottpresse (`schrottpresse`).
- **Zerstörbare Props:** Magnetkran (`magnet_kran`), Batteriesäule (`batterie_saeule`).
- **Ereignis „Magnetsturm“:** alle 90 s werden alle metallischen Partikel und Waffen für 15 s mit hoher Wucht quer durch den Bildschirm geschleudert.
- **Proben:** Rostprobe (`probe_rost`), Magnetit-Splitter (`probe_magnetit`).
- **Arena:** Rechteckige Stahlhalle mit zwei gigantischen Schrottpressen an den Seiten.

---

## 2. Die Kuchenkruste (`kuchen`)

- **Pitch:** „Gebacken vor einer Million Jahren. Oben knusprige Baisers, unten kochende Karamell-Lava.“
- **Regel:** `rule_hot` – Dauerhitze; weiche Substanzen schmelzen; Zucker karamellisiert bei Brand.
- **Form:** Schichten, 2048×1536: Biskuit-Terrassen, Zuckerglasur-Plateaus, tiefes Karamell.
- **Licht:** 0,65, warm-goldener Backofen-Glow.
- **Teilgebiete:** Glasur-Kamm (weißer Puderzucker, Baisers), Biskuit-Höhlen (poröser Teig, Krumen-Tunnel), Karamell-Tiefe (heiß, zäh, kochend).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `biskuit` | Biskuitteig | fest | weich | #E8C07A | saugt Flüssigkeiten wie Schwamm auf |
  | `zuckerglasur` | Zuckerglasur | fest | hart | #FFF5EA | schmilzt bei Feuer zu süßem Sirup |
  | `karamell` | Kochendes Karamell | flüssig, zäh | – | #B86014 | brennt lang, klebt an Füßen |
  | `puderzucker` | Puderzucker | Pulver | weich | #FFFFFF | erzeugt bei Explosion gewaltige Mehlstaub-Detonation |

- **Einheimische:** Zuckerspinne (`zuckerspinne`), Kerzenkobold (`kerzenkobold`), Marzipanschwein (`marzipanschwein`), Baiser-Geist (`baiser_geist`).
- **Unter-Zwischenboss:** Marzipanritter (`marzipan_ritter`).
- **Hauptboss:** Die Mehrstöckige Hochzeitstorte (`hochzeitstorte`).
- **Zerstörbare Props:** Riesenkerze (`riesen_kerze`), Keksrad (`keks_rad`).
- **Ereignis „Karamell-Ausbruch“:** alle 80 s schießen heiße Geysire aus flüssigem Karamell aus dem Boden.
- **Proben:** Zuckerkruste (`probe_zucker`), Marzipan-Nase (`probe_marzipan`).
- **Arena:** Runde Tortenplatte; herabfallende Baiser-Brocken dienen als Deckung.

---

## 3. Die Summende Spule (`spule`)

- **Pitch:** „Ein Alptraum aus blanken Kupferdrähten und permanenten Hochspannungs-Entladungen.“
- **Regel:** `rule_electric` – Elektrische Ströme leiten 3× weiter; Funken laden Schutzschilde auf; Kurzschlüsse entzünden Gas.
- **Form:** Hoch, 1280×2560: endlose vertikale Spulentürme, gigantische Kondensatoren.
- **Licht:** 0,38, zuckende blaue Lichtbögen erhellen die Dunkelheit.
- **Teilgebiete:** Spulenwald (dichte Kupferwicklungen), Kondensatordeck (Spannungs-Kammern), Plasmakern (extreme Hitze und Strahlung).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `kupfer` | Kupferdraht | fest | hart | #C87540 | leitet Strom widerstandsfrei weiter |
  | `isolator` | Isolierkeramik | fest | hart | #4A5568 | blockiert jeglichen Stromfluss |
  | `plasma` | Plasmagas | Gas, glühend | – | #70E0FF | verbrennt Projektile und Fleisch |
  | `elektrolyt` | Elektrolytlösung | flüssig | – | #40FFA0 | explodiert in Schockwelle bei Stromeinleitung |

- **Einheimische:** Funkenhornisse (`funkenhornisse`), Spulenkrabbe (`spulenkrabbe`), Kupferschlange (`kupferschlange`), Kondensator-Geist (`kondensator_geist`).
- **Unter-Zwischenboss:** Spulenmeister (`spulenmeister`).
- **Hauptboss:** Der Kolossale Transformator (`transformator`).
- **Zerstörbare Props:** Trafo-Kasten (`trafo_kasten`), Blitzableiter (`blitzableiter`).
- **Ereignis „Kurzschluss“:** alle 70 s zucken gewaltige Blitz-Kaskaden quer durch alle Kupferleitungen.
- **Proben:** Kupferspule (`probe_spule`), Kondensator-Zelle (`probe_kondensator`).
- **Arena:** Faraday-Käfig mit beweglichen Elektroden-Armen.

---

## 4. Die Uhrwerkwüste (`uhrwerkwueste`)

- **Pitch:** „Ein Meer aus tickendem Zahnradsand. Zeit ist hier keine Konstante, sondern eine klebrige Flüssigkeit.“
- **Regel:** `rule_slowtime` – Die Zeit pulsiert im Sekunden-Takt; Projektile ziehen Zeit-Schleppen hinter sich her.
- **Form:** Weitläufiges Plateau, 2560×1536: riesige halb versunkene Ziffernblätter, Pendelgruben.
- **Licht:** 0,50, mattes Messing-Glänzen unter sepiafarbenem Himmel.
- **Teilgebiete:** Zahnrad-Dünen (Dünen aus feinem Messinggrieß), Gruft der Sekunden (tickende Pendel), Chrono-Oase (flüssige Zeit-Teiche).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `chrono_sand` | Zeitensand | Pulver | weich | #E0C070 | rieselt träge; verlangsamt Fußgänger |
  | `messing` | Zahnradmessing | fest | sehr hart | #D4AF37 | extrem stabil; reflektiert Energiestrahlen |
  | `fluessig_zeit` | Flüssige Zeit | flüssig | – | #C0D8E8 | bremst alles darin auf 15 % Geschwindigkeit |
  | `unruh_fett` | Uhrenöl | flüssig | – | #8A7030 | extrem rutschig; entflammbar |

- **Einheimische:** Zecken-Uhr (`zecken_uhr`), Pendel-Schreiter (`pendel_schreiter`), Chrono-Wächter (`chrono_waechter`), Sanduhr-Skarabäus (`sanduhr_skarabaeus`).
- **Unter-Zwischenboss:** Der Unruh-Vogel (`unruh_vogel`).
- **Hauptboss:** Das Ewige Pendel (`ewiges_pendel`).
- **Zerstörbare Props:** Standuhr (`stand_uhr`), Federwerk (`feder_werk`).
- **Ereignis „Zeitsprung“:** alle 100 s werden alle Projektile und Figuren für 3 Sekunden eingefroren, gefolgt von einer Geschwindigkeits-Eruption.
- **Proben:** Unruh-Feder (`probe_unruh`), Chrono-Tropfen (`probe_chrono`).
- **Arena:** Innenraum einer gigantischen Kirchenuhr mit rotierenden Zahnrädern als beweglichen Plattformen.

---

## 5. Das Endlose Suppenmeer (`suppenmeer`)

- **Pitch:** „Ein siedender Ozean aus Gemüsesuppe. Buchstabennudeln versuchen verzweifelt, Warnungen zu formulieren.“
- **Regel:** `rule_flooded_soup` – Hoher Auftrieb; Suppenfett schwimmt oben und brennt; heißer Dampf benebelt die Sicht.
- **Form:** Tiefsee, 1536×2560: senkrechter Topf mit Brühe, Gemüseriffen und dunklem Hefe-Bodensatz.
- **Licht:** 0,35, trübes Bernsteingelb mit aufsteigenden Dampfblasen.
- **Teilgebiete:** Brühe-Spiegel (schwimmende Kräuterinseln, Fettaugen), Sellerie-Riff (massives Suppengemüse als Wände), Tiefer Topf (dunkler, dichter Bodensatz).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `bouillon` | Fleischbrühe | flüssig | – | #E5C158 | dämpft Stürze; verleiht leichten Auftrieb |
  | `suppenfett` | Suppenfett | flüssig, leicht | – | #FFF090 | schwimmt immer oben; brennt heiß |
  | `nudel_teig` | Nudelteig | fest | weich | #F5E0A0 | federt Stöße ab; löst sich nach 60 s in Suppe auf |
  | `pfefferdampf` | Pfeffergas | Gas | – | #4A4030 | blendet Feinde (-40 % Zielgenauigkeit) |

- **Einheimische:** Suppenlaus (`suppenlaus`), Buchstaben-Krake (`buchstaben_krake`), Karotten-Aal (`karotten_aal`), Markbällchen-Krabbe (`markbaellchen_krabbe`).
- **Unter-Zwischenboss:** Der Chefkoch-Ghul (`chefkoch_ghul`).
- **Hauptboss:** Der Kellen-Leviathan (`kellen_leviathan`).
- **Zerstörbare Props:** Suppenschüssel (`suppen_schuessel`), Nudelholz (`nudel_holz`).
- **Ereignis „Wallendes Kochen“:** alle 75 s kocht die Brühe auf – riesige Dampfblasen reißen Cloita und Feinde mit hoher Wucht nach oben.
- **Proben:** Buchstabennudel A (`probe_nudel_a`), Getrocknete Nelke (`probe_nelke`).
- **Arena:** Der Boden einer gewaltigen Emaille-Kasserolle mit aufsteigenden Hitzeventilen.

---

## 6. Freizeitpark Endzeit (`freizeitpark`)

- **Pitch:** „Seit dreihundert Jahren geschlossen. Die Maskottchen haben Hunger und die Achterbahn fährt noch immer.“
- **Regel:** `rule_momentum` – Nahezu reibungsfreie Schienen; extreme Fluggeschwindigkeiten; bunte Ballons erzeugen Schwerelosigkeit.
- **Form:** Horizontales Band, 3584×1024: verschlungene Achterbahnschienen, Geisterbahn-Grotten, Wurfbuden.
- **Licht:** 0,55, flackernde Neon-Reklamen in Pink, Cyan und giftigem Grün.
- **Teilgebiete:** Geisterbahn (enge schwarze Tunnel mit Grusel-Mechanismen), Kirmesplatz (zerstörte Pavillons, Wurfbuden), Achterbahn-Looping (schwindelerregende Schienen über dem Abgrund).
- **Materialien:**

  | Schlüssel | Name | Art | Härte | Farbe | Wirkung |
  | --- | --- | --- | --- | --- | --- |
  | `rost_schiene` | Achterbahnschiene | fest | hart | #805040 | beschleunigt darauf rutschende Figuren um 100 % |
  | `zuckerwatte_rot` | Zuckerwatte | Pulver, leicht | weich | #FF80A0 | explodiert in rosafarbene Rauchwand |
  | `helium_gas` | Helium | Gas | – | #E0FFFF | hebt alles an; ändert Klonitas Sprachfrequenz (hoch!) |
  | `spiegel_glas` | Spiegelglas | fest | spröde | #B0C4DE | splittert in tausend Scherben; reflektiert Licht |

- **Einheimische:** Geisterbahn-Clown (`geisterbahn_clown`), Leer-Kostüm (`leer_kostuem`), Popcorn-Drohne (`popcorn_drohne`), Autoscooter-Käfer (`autoscooter_kaefer`).
- **Unter-Zwischenboss:** Der Losverkäufer (`los_verkaeufer`).
- **Hauptboss:** Der Mechanische Achterbahn-Drache (`achterbahn_drache`).
- **Zerstörbare Props:** Karussellpferd (`karussell_pferd`), Popcorn-Maschine (`popcorn_maschine`).
- **Ereignis „Freie Fahrt“:** alle 90 s heulen alte Sirenen auf, und leere Achterbahnwagen rasen im Tiefflug quer durch den Raum.
- **Proben:** Kirmes-Chip (`probe_kirmes_chip`), Glasierter Apfel (`probe_apfel`).
- **Arena:** Ein dreidimensionales Looping-Geflecht mit frei schwingenden Gondeln als Plattformen.
