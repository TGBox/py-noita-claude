# 03 – Universen

Jedes Universum ist eine Datendatei (`src/universes/<key>.py` oder JSON) mit allen Feldern unten. MVP: 6 Universen. Sie müssen auf allen drei Rängen funktionieren.

## Felder eines Universums

| Feld | Bedeutung |
|---|---|
| `key`, `name` | Schlüssel, Anzeigename |
| `pitch` | ein Satz für Ladebildschirm und Archiv |
| `rule` | Hauptregel aus Kapitel 02 |
| `shape`, `size` | Weltform und Zellengröße |
| `regions` | 2–3 Teilgebiete mit eigener Mischung (Generator-Parameter) |
| `materials` | eigene Materialien (MVP: 3–6) mit allen Materialwerten und Reaktionen |
| `palette` | 8–12 Farben (Teilpalette) |
| `ambient` | Grundhelligkeit 0–1 |
| `natives` | Kreaturen mit Häufigkeit je Rang |
| `event` | wiederkehrendes Ereignis |
| `samples` | 2 Proben (Kapitel 07) |
| `music` | Stimmung für die prozedurale Musik (Grundton, Tempo, Klangfarbe) |
| `arena` | wie eine Zwischengegner-Arena hier aussieht |
| `klonita` | 3+ Sprüche, nur in diesem Universum (Kapitel 08) |

---

## 1. Fleischwelt (`fleischwelt`)

- **Pitch:** „Ein Universum, das nur aus einem einzigen, sehr großen und sehr hungrigen Lebewesen besteht.“
- **Regel:** `rule_living_walls` – Fleisch wächst langsam in Löcher nach; Wände bluten bei Treffern.
- **Form:** Quadrat, 2048×1536. **Licht:** 0,28.
- **Teilgebiete:** Schlund (Fleisch, Zähne), Magen (Säurebecken, Talg), Knochenmark (Knochen, Zahnschmelz).
- **Materialien:** übernimmt den bisherigen Biohorror-Satz, höchstens 10 (Engine-Grenze, Kapitel 02). Auswahl: Fleisch, Knochen, Zahnschmelz, Blut, Magensäure, Wucherung, Sporen, Talg, Schorf, Glutblut. Entfallen (oder später in „Fleischwelt (Spätstadium)“): Schleim, Eiter, Sehnen, Nervenstrom, Knochenstaub (ersetzt durch Grundmaterial Sand), Rauch/Feuer (Grundmaterialien).
- **Teilpalette:** #561E26 #86303A #B85060 #9A8A70 #CEDAE2 #8CC428 #A480A0 #C4AE76
- **Einheimische:** Fleischmade (Kap. 05, `fleischmade`), Blutegel (`blutegel`).
- **Ereignis „Verdauung“:** alle 90 s steigt in einem Magen-Gebiet für 20 s der Säurespiegel um 30 px (Ankündigung: Rumpeln, Kamerawackeln, Klonita: „Hörst du das? Ich glaube, die Welt hat Hunger.“).
- **Proben:** Gallenstein, Wucherungsableger.
- **Musik:** tiefe Drones, Herzschlag (bisherige Stimmung „magen“).
- **Arena:** runde Knochenhalle mit Fleischboden, der nachwächst.
- **Geheimnisse:** versiegelte Knochenkammer mit Erinnerungssplitter; Schatzkammer hinter Knochenpanzer.

## 2. Aktenhalde (`aktenhalde`)

- **Pitch:** „Hier wurde vor Äonen ein Antrag gestellt. Er wird noch bearbeitet.“
- **Regel:** `rule_paperwork` – das meiste Feste ist Papier: brennt schnell und weit.
- **Form:** Breit, 3072×1024: endlose Regalreihen, Treppen aus Aktenordnern, Rohrpost-Schächte.
- **Licht:** 0,55, kaltes Neonlicht (bläulich).
- **Teilgebiete:** Registratur (dichte Regale), Großraumbüro (offene Flächen, Schreibtische als Plattformen), Archivkeller (dunkel, Tintenseen).
- **Materialien:**

| Schlüssel | Name | Art | Härte | Farbe | Wirkung |
|---|---|---|---|---|---|
| `papier` | Papier | fest | weich | #EDE6D2 | Brennbarkeit 0,6 (sehr hoch), verbrennt zu Asche |
| `aktendeckel` | Aktendeckel | fest | hart | #C8A060 | stabile Wände, brennt langsam |
| `tinte` | Tinte | flüssig | – | #1E2A5A | macht Kreaturen „markiert“ (sichtbar durch Wände für 20 s), färbt Papier dunkel (dann nicht mehr brennbar) |
| `siegellack` | Siegellack | flüssig, erstarrt | – | #B0202A | erstarrt nach 3 s zu festem Lack (weich); geschmolzen durch Feuer |
| `asche` | Asche | Pulver | weich | #5A5458 | Rückstand von Papier |
| `stempelfarbe` | Stempelfarbe | flüssig | – | #6A2080 | Trinken: Status „Genehmigt“ für 15 s |

- **Teilpalette:** #EDE6D2 #C8BFA6 #C8A060 #8A6A40 #1E2A5A #B0202A #6A2080 #9AB4D0 #5A5458
- **Einheimische:** Aktenfresser (`aktenfresser`), Stempler (`stempler`).
- **Ereignis „Prüfung“:** alle 120 s ertönt eine Durchsage („Bitte halten Sie Ihre Unterlagen bereit.“); 2 Behörden-Agenten erscheinen, unabhängig von der Fahndungsstufe.
- **Proben:** Stempelkissen, Formular B-38 (in dreifacher Ausfertigung).
- **Musik:** Schreibmaschinen-Rhythmus, Fahrstuhlmusik in Moll.
- **Arena:** großer Sitzungssaal mit Tischen als Plattformen; Papierboden.
- **Wechselwirkungen, die das Universum zeigen soll:** Feuer + Papier = Flächenbrand; Tinte löscht Brandausbreitung; Siegellack als selbstgebaute Brücke; Stempler-Status beeinflusst Kämpfe.

## 3. Glibbria (`glibbria`)

- **Pitch:** „Ein Planet aus Wackelpudding. Alles federt. Niemand stirbt am Fall – nur an allem anderen.“
- **Regel:** `rule_bounce` – Geschosse prallen zweimal öfter ab, kein Fallschaden, Sprünge federn (Sprungkraft +30 % nach Landung aus großer Höhe).
- **Form:** Inseln, 2560×1280: schwebende Glibber-Inseln über einem Brausesirup-Meer.
- **Licht:** 0,6, warm-bunt.
- **Teilgebiete:** Gelee-Hügel, Sirupküste, Kaugummi-Höhlen.
- **Materialien:**

| Schlüssel | Name | Art | Härte | Farbe | Wirkung |
|---|---|---|---|---|---|
| `glibber` | Glibber | fest | weich | #6CE0A0 | Geschosse prallen daran immer ab (zusätzlich zur Regel); Körper federn darauf |
| `glibber_rot` | Himbeerglibber | fest | weich | #F0507A | wie Glibber, explodiert bei Feuer zu Sirup |
| `brausesirup` | Brausesirup | flüssig | – | #F6A0E0 | sprudelt; in Kontakt mit Feuer oder Explosion → Schaumexplosion (kleine Explosion, verteilt Schaum) |
| `schaum` | Schaum | Pulver, leicht | weich | #FFF0FA | zerfällt nach 10 s |
| `kaugummi` | Kaugummi | flüssig, sehr zäh | – | #FF80C0 | macht „klebrig“; erstarrt nicht |
| `zuckerguss` | Zuckerguss | fest | hart | #FFFFFF | Plattformen; schmilzt bei Feuer zu Sirup |

- **Teilpalette:** #6CE0A0 #3AA070 #F0507A #F6A0E0 #FFF0FA #FF80C0 #FFD860 #7A60D0 #FFFFFF
- **Einheimische:** Hüpfling (`huepfling`), Glibberteiler (`glibberteiler`); **große Kreatur:** Trampolinwal (`trampolinwal`).
- **Ereignis „Brauseregen“:** alle 100 s regnet es 15 s Brausesirup (Regel `rule_rain` als Ereignis).
- **Proben:** Glibberkern, Brauseperle.
- **Musik:** fröhlicher Synthesizer mit schiefen Tönen, Tempo hoch.
- **Arena:** große Gelee-Schüssel; Wände federn.

## 4. Krümelreich (`kruemelreich`)

- **Pitch:** „Du bist etwa so groß wie ein Brotkrümel. Das Brot ist größer. Die Ameisen auch.“
- **Regel:** `rule_tiny` – Schwerkraft 50 %, Wasser in großen, zähen Tropfen; riesige Alltagsgegenstände als Gelände.
- **Form:** Breit, 3072×1024: Küchenboden mit Fliesenfugen, darunter ein Ameisenbau.
- **Licht:** 0,7 oben (Tageslicht durchs Fenster), 0,2 im Bau.
- **Teilgebiete:** Fliesenwüste (riesige Krümel, Zuckerkörner, eine Erbse als Fels), Unter dem Kühlschrank (dunkel, Staubflusen), Ameisenbau (Gänge, Kammern, Königinnenkammer).
- **Materialien:**

| Schlüssel | Name | Art | Härte | Farbe | Wirkung |
|---|---|---|---|---|---|
| `kruemel` | Brotkrümel | fest | weich | #D8A860 | bröselt bei Explosionen zu Bröseln |
| `brosel` | Brösel | Pulver | weich | #C89850 | Ameisen fressen es |
| `zucker` | Zucker | Pulver | weich | #F4F4F8 | lockt Ameisen an (Duftquelle); Feuer → Karamell |
| `karamell` | Karamell | flüssig, erstarrt | – | #C07020 | heiß klebrig, erstarrt zu hartem Karamell |
| `honig` | Honig | flüssig, zäh | – | #F0B020 | klebrig; Trinken: Flux-Schub |
| `fliese` | Fliese | fest | hart | #D0D8DC | glatt (wenig Reibung) |
| `staubfluse` | Staubfluse | fest | weich | #8A8890 | sehr brennbar, leicht |

- **Teilpalette:** #D8A860 #C89850 #F4F4F8 #C07020 #F0B020 #D0D8DC #8A8890 #503020 #A0C860
- **Einheimische:** Ameisenkrieger (`ameisenkrieger`), Blattlaus (`blattlaus`).
- **Ereignis „Riesenschritt“:** alle 80 s bebt die Welt; an einer zufälligen Stelle der Oberfläche stürzt ein riesiger Schatten herab, Zellen in einem breiten Streifen werden zusammengedrückt (Ankündigung 3 s Schatten am Boden).
- **Proben:** Riesenzuckerkristall, Ameisenduft-Ampulle.
- **Musik:** Pizzicato-Streicher, Grillenzirpen.
- **Arena:** Teetasse (Rand als Wände, Teesatz am Boden).

## 5. Sporenklub (`sporenklub`)

- **Pitch:** „Die Party läuft seit 400 Jahren. Die Pilze wollen nicht, dass sie aufhört.“
- **Regel:** `rule_beat` – Takt alle 0,5 s: Licht pulsiert, Kreaturen bewegen sich im Takt, Treffer auf dem Beat +25 % Schaden (kleines Takt-Symbol in der HUD).
- **Form:** Quadrat, 2048×1536: Höhlenclub mit Tanzflächen-Kavernen, Lautsprechertürmen aus Pilzhüten.
- **Licht:** 0,15 Grundlicht, stark farbige Leuchtsporen.
- **Teilgebiete:** Tanzfläche (offen, Lichtorgeln), Hinterzimmer (enge Gänge, Diebe), Lautsprechertürme (vertikal).
- **Materialien:**

| Schlüssel | Name | Art | Härte | Farbe | Wirkung |
|---|---|---|---|---|---|
| `pilzfleisch` | Pilzfleisch | fest | weich | #B080C0 | wächst auf jeden 8. Beat ein wenig in Luft hinein |
| `pilzhut` | Pilzhut | fest | hart | #E04080 | federt leicht |
| `leuchtsporen` | Leuchtsporen | Gas | – | #60FFE0 | leuchtet; Einatmen: „Beschwipst“ |
| `neonsaft` | Neonsaft | flüssig | – | #E0FF40 | leuchtet stark; Trinken: Tempo-Schub |
| `nebel` | Bühnennebel | Gas | – | #A0A0C0 | verdeckt Sicht, harmlos |

- **Teilpalette:** #1A0E2A #B080C0 #E04080 #60FFE0 #E0FF40 #A0A0C0 #FF60A0 #4060FF
- **Einheimische:** Türsteherpilz (`tuersteherpilz`), Sporenschnorrer (`sporenschnorrer`).
- **Ereignis „Bass-Drop“:** alle 60 s ein starker Puls: alle Körper und losen Gegenstände werden 40 px hochgeschleudert, Pulver hüpft.
- **Proben:** Leuchtspore im Glas, Plattennadel.
- **Musik:** Four-on-the-floor mit verzerrtem Bass; Tempo exakt passend zum Takt der Regel (120 BPM).
- **Arena:** Hauptbühne mit DJ-Pult und Lautsprechertürmen.

## 6. Versunkene Abtei (`abtei`)

- **Pitch:** „Die Mönche haben ein Schweigegelübde abgelegt. Dann haben sie Kiemen bekommen.“
- **Regel:** `rule_flooded` – weite Teile unter Wasser; Auftrieb, Feuer erlischt, Strom verteilt sich im Wasser, Atem-Leiste.
- **Form:** Hoch, 1280×2560: ein versunkener Turm, oben Luftblasen-Kapellen, unten Krypta.
- **Licht:** 0,35, grünlich, Kerzen als Lichtpunkte.
- **Teilgebiete:** Glockenturm (oben, trocken), Kirchenschiff (geflutet), Krypta (dunkel, Strömung).
- **Materialien:**

| Schlüssel | Name | Art | Härte | Farbe | Wirkung |
|---|---|---|---|---|---|
| `mauerwerk` | Mauerwerk | fest | hart | #6A7468 | Standardwand |
| `buntglas` | Buntglas | fest | weich | #40A0D0 / #D04060 / #E0C040 | zerspringt bei Treffern in Splitter (schneiden) |
| `kerzenwachs` | Kerzenwachs | fest, schmilzt | weich | #EEE6C8 | Feuer schmilzt es zu flüssigem Wachs, erstarrt wieder |
| `glockenbronze` | Glockenbronze | fest | sehr hart | #B08840 | leitet Strom, klingt bei Treffern (Klonita hält sich die Ohren zu) |
| `algen` | Algen | fest | weich | #3A7A40 | wächst langsam im Wasser |
| `weihrauch` | Weihrauch | Gas | – | #C8C0B0 | macht Gegner benebelt (zielen schlechter) |

- **Teilpalette:** #1C2E2A #3A5A50 #6A7468 #40A0D0 #D04060 #E0C040 #EEE6C8 #B08840 #3A7A40
- **Einheimische:** Mönchsfisch (`moenchsfisch`), Orgelaal (`orgelaal`); **große Kreatur:** Kirchenkrake (`kirchenkrake`).
- **Ereignis „Glockenschlag“:** alle 75 s läutet die große Glocke: Schockwelle durch Wasser (Stromschlag für alle im Wasser, auch Gegner), Ankündigung durch ein leiseres Vorläuten 2 s vorher.
- **Proben:** Glockensplitter, Kerzenstumpf mit Gesichtsabdruck.
- **Musik:** Orgel-Drone, Unterwasser-Gluckern, gregorianisches Summen.
- **Arena:** Kirchenschiff mit Luftblase unter der Kuppel.

---

## Pool für später (nicht im MVP)

Kurzbeschreibungen, damit nichts verloren geht. Jedes wird später nach demselben Schema ausgearbeitet.

| Schlüssel | Name | Regel | Idee |
|---|---|---|---|
| `freizeitpark` | Freizeitpark Endzeit | `rule_magnet` | Ein Vergnügungspark nach dem Weltuntergang, Achterbahnschienen als Wege, Maskottchen-Kostüme ohne Inhalt, Zuckerwatte brennt. |
| `gerichtssaal` | Gerichtsdimension | `rule_transmute` | Alles wird verhandelt; Urteile verwandeln Materie. Richterhämmer als Gegner. |
| `spiegelwelt` | Spiegelwelt | `rule_reverse_gravity` | Alles ist Glas und Spiegel, Geschosse spiegeln, dein Spiegelbild läuft verzögert mit. |
| `tiefkuehltruhe` | Tiefkühltruhe | `rule_cold` | Gefrorene Lebensmittel, Eis, rutschige Böden, Fischstäbchen-Schwärme. |
| `uhrwerkwueste` | Uhrwerkwüste | `rule_slowtime` | Sand und Zahnräder, Zeit tickt zäh, Sanduhren als Gegner. |
| `teppichwelt` | Unterm Teppich | `rule_tiny` | Hausstaubmilben, verlorene Münzen (viel Gold), Fusseln. |
| `spielzeugkiste` | Spielzeugkiste | `rule_bounce` | Bauklötze, Plüschtiere, Batteriesäure. |
| `suppenmeer` | Suppenmeer | `rule_flooded` | Ein Ozean aus Suppe, Buchstabennudeln formen Worte. |
| `vulkankueche` | Vulkanküche | `rule_hot` | Lava als Bratfett, Köche aus Stein. |
| `schrottplatz` | Magnetschrottplatz | `rule_magnet` | Metallberge, Magnetkräne, Roboter-Ratten. |
| `wolkenstadt` | Wolkenstadt | `rule_low_gravity` | Häuser auf Wolken, Regen als Untergrund. |
| `fernsehdimension` | Werbepause | `rule_beat` | Alles ist Werbung; Gegner verkaufen dir Dinge, Jingles als Takt. |
| `kaesemond` | Käsemond | `rule_low_gravity` | Löcher, Mäuse-Astronauten, schimmlige Höhlen. |
| `datengitter` | Datengitter | `rule_transmute` | Alles aus Pixeln und Glitches, Viren als Gegner. |
| `katzenplanet` | Katzenplanet | `rule_darkness` | Riesige Katzen schlafen, Wollknäuel als Plattformen; wecken = Ärger. |
| `nebelwald` | Nebelwald | `rule_darkness` | Leuchtende Pilze, Pflanzen, die sich bewegen, wenn man nicht hinsieht. |
| `zahnarztpraxis` | Wartezimmer der Ewigkeit | `rule_slowtime` | Nummer ziehen, warten, Bohrer als Gegner. |
| `biohorror_plus` | Fleischwelt (Spätstadium) | `rule_living_walls` + `rule_darkness` | Härtere Fassung der Fleischwelt mit den übrigen alten Biomen (Leber, Lunge, Herzkammer). |

Die 32 alten Biome (Schlund, Magen, …) gehen als Teilgebiete in Fleischwelt und „Fleischwelt (Spätstadium)“ auf.
