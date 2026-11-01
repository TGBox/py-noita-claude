# 06 – Waffen und Module

Die Mechanik der bisherigen Augmentationen bleibt vollständig erhalten (Deck, Mehrfachwurf, Zünder, Ladungen, Mischen, Familien, Seltenheit). Neu sind Namen, Texte, Icons und das Aussehen der Waffen.

## Waffen (Rahmen)

Werte wie bisher: Flux-Maximum, Flux pro Sekunde, Verzögerung, Nachladen, Plätze, Schüsse pro Abzug, Streuung, Mischen.

### Aussehen aus Teilen

Waffen in der Welt (12–20×5–8) und an Cloitas Arm werden aus Teilen zusammengesetzt; die Werte bestimmen die Teile, damit man einer Waffe ihre Art ansieht:

| Teil | Varianten | Bestimmt durch |
|---|---|---|
| Gehäuse | kurz (6 px), mittel (9 px), lang (12 px) | Plätze 2–4 / 5–8 / 9–12 |
| Lauf | einfach, Doppellauf, Dreifachlauf | Schüsse pro Abzug 1 / 2 / 3+ |
| Mündung | spitz, Trichter, Sieb | Streuung klein / mittel / groß |
| Flux-Tank | klein, mittel, groß (leuchtet in `flux`) | Flux-Maximum |
| Griff | Pistolengriff, Kurbel, Gummihandschuh | Verzögerung kurz / mittel / lang |
| Zierteil | Klebeband (mischt), Antenne, Wackelauge, Glühbirne, Schraubenzieher | Mischen = Klebeband; sonst zufällig nach Seed |

Je Teil 1 Sprite (Raster), Farben aus `metal`, `flux`, `n1`–`n5` plus eine Zufallsfarbe der Universumspalette, in der sie gefunden wurde.

### Namen

Zufällig aus Adjektiv + Hauptwort (Startliste, je 12):
- Adjektive: Geliehene, Verbotene, Wackelige, Notdürftige, Selbstgebaute, Überladene, Verfluchte, Rostige, Klebrige, Leise, Beleidigte, Experimentelle
- Hauptwörter: Kanone, Strahlenpistole, Spritze, Pumpe, Schleuder, Röhre, Puste, Knarre, Apparatur, Zwille, Heizdecke, Gießkanne

### Startwaffen

| Schlüssel | Name | Module | Hinweis |
|---|---|---|---|
| `start_funken` | Cloitas Funkenpistole | Turbo, Flux-Funke, Flux-Funke, Flux-Funke | entspricht der alten Funkendrüse |
| `start_granate` | Der Matschwerfer | Wasserfüllung, Hüpfgranate, Feuerfüllung, Matschbatzen | entspricht dem alten Gallenwerfer |

### Portal-Funktion

Jede Waffe öffnet am **Ankerpunkt** eines Universums (wo bisher der Ausgang war) genau ein Portal zur Werkstatt: In der Nähe des Ankers erscheint „E: Portal öffnen“, Cloita zielt, ein Portal (Ring aus `flux`, 24×32, 6 Frames) öffnet sich. Sonst hat die Waffe keine Portal-Funktion.

## Kategorien

| Intern | Anzeige | Rahmenfarbe Icon | Bedeutung |
|---|---|---|---|
| FORM | Geschoss | `n4` | was fliegt |
| MODIFIER | Aufsatz | `cloth` | verändert das nächste Geschoss |
| TRIGGER | Zünder | `gold` | das Geschoss setzt die nächste Gruppe frei |
| PAYLOAD | Füllung | `danger` | Material, das das Geschoss bringt |

## 60 Basismodule

Die Spalte „bisher“ nennt den alten Baustein, dessen Werte übernommen werden (Feinschliff in der Balance-Runde). Ladungen (L) bleiben.

### Geschosse (24)

| Schlüssel | Name | Bisher | Beschreibung | Icon-Idee |
|---|---|---|---|---|
| `flux_funke` | Flux-Funke | funke | Schneller Funke, kleine Explosion. Das Brot und Butter jeder Wissenschaftlerin. | türkiser Funke mit Schweif |
| `nadelschuss` | Nadelschuss | nadel | Sehr schnell, kratzt kaum an Wänden. | Spritzennadel |
| `huepfgranate` | Hüpfgranate | gallenblase | Prallt ab und platzt nach kurzer Zeit gewaltig. | Granate mit Sprungfeder |
| `matschbatzen` | Matschbatzen | klumpen | Fliegt im Bogen und zerplatzt zu einer Pfütze (Wasser). | Matschkugel |
| `schrotladung` | Schrotladung | knochensplitter | Fünf Kugeln auf kurze Distanz. | Patrone mit Kügelchen |
| `bohrkopf` | Bohrkopf | zahnbohrer | Frisst sich ein Stück weit durch Weiches und Hartes. | Bohrspitze |
| `lebenssauger` | Lebenssauger | blutegel | Langsam; heilt dich um die Hälfte seines Schadens. | Strohhalm mit Tropfen |
| `sprungbolzen` | Sprungbolzen (L15) | teleportbolzen | Wo er einschlägt, reißt er dich hin. | Pfeil mit Fußspuren |
| `kreissaege` | Kreissäge | knochensaege | Prallt oft ab und schneidet durch alles Lebendige. | Sägeblatt |
| `haftmine` | Haftmine | sporenmine | Bleibt liegen und platzt, wenn etwas naht. | Mine mit Saugnapf |
| `tunnelfresser` | Tunnelfresser (L6) | fressgeschwuer | Träge Kugel, frisst einen breiten Gang. | Kugel mit Mund |
| `durchschlagbolzen` | Durchschlagbolzen | knochenspeer | Spießt alles in seiner Bahn auf. | langer Bolzen |
| `mikrofunke` | Mikrofunke | mikrofunke | Winzig, billig, schnell. | Pünktchen |
| `feuerball` | Feuerball | feuerball | Glühender Klumpen, brennende Explosion. | Flammenkugel |
| `kraterbombe` | Kraterbombe (L8) | knochenbombe | Prallt einmal ab, dann ein riesiger Krater. | Bombe mit Totenkopf |
| `nadelregen` | Nadelregen | nadelregen | Acht Nadeln auf einmal. | Nadelfächer |
| `klebekugel` | Klebekugel | schleimkugel | Macht Gegner klebrig, löscht Brände. | rosa Kaugummikugel |
| `stromstoss` | Stromstoß | nervenstrom | Ein Blitz; in Wasser und Metall läuft er weiter. | Blitz |
| `wandelstrahl` | Wandelstrahl (L5) | wandlungsdruese | Wen er trifft, der wird zu etwas anderem. | Fragezeichen-Strahl |
| `tauschstrahl` | Tauschstrahl (L15) | tauschdruese | Du tauschst den Platz mit dem Getroffenen. | zwei Pfeile |
| `kettenblitz` | Kettenblitz | kettenfunke | Springt auf bis zu drei weitere Kreaturen. | Zickzack |
| `leuchtfackel` | Leuchtfackel | leuchtkugel | Schwebt lange und erhellt die Dunkelheit. | Glühbirne |
| `mahlwerk` | Mahlwerk | zahnrad | Ein Zahnrad, das lange durch Wände mahlt. | Zahnrad |
| `flummi` | Flummi | gelenkkugel | Prallt immer wieder ab. | bunter Ball |

### Aufsätze (22)

| Schlüssel | Name | Bisher | Beschreibung |
|---|---|---|---|
| `turbo` | Turbo | beschleunigung | Nächstes Geschoss fliegt schneller. |
| `turbo_x` | Überturbo | beschleunigung_stark | Zweieinhalbmal so schnell. Hält nicht lange. |
| `sprengladung` | Sprengladung | sprengkraft | Größere Explosion. |
| `atomkern` | Taschen-Atomkern | sprengkern | Viel größere Explosion. Nicht schütteln. |
| `antigrav` | Antigrav | umkehr | Nächstes Geschoss fällt nach oben. |
| `schwebefeld` | Schwebefeld | schwerelos | Nächstes Geschoss fällt gar nicht. |
| `bleimantel` | Bleimantel | schwere_ladung | Mehr Schaden, aber langsamer. |
| `zielsuchkopf` | Zielsuchkopf | zielsuche | Lenkt zum Mauszeiger. |
| `doppellauf` | Doppellauf | doppel | Zwei Gruppen auf einmal. |
| `dreifachlauf` | Dreifachlauf | dreifach | Drei Gruppen auf einmal. |
| `rundumschlag` | Rundumschlag (L15) | achterkreis | Acht Gruppen im Kreis um dich. |
| `faecherduese` | Fächerdüse | faecher | Fünf Gruppen, weit aufgefächert. |
| `rueckspiegel` | Rückspiegel | vorne_hinten | Eine Gruppe nach vorn, eine nach hinten. |
| `panzerbrechend` | Panzerbrechend | durchbohren | Fliegt durch Kreaturen hindurch. |
| `gummierung` | Gummierung | abprall | Prallt dreimal von Wänden ab. |
| `brandsatz` | Brandsatz | brandbeschleuniger | Getroffene fangen Feuer. |
| `langstrecke` | Langstrecke | langlebigkeit | Fliegt doppelt so lange, aber langsamer. |
| `kurzstrecke` | Kurzstrecke | kurzlebig | Vergeht nach halber Zeit, dafür schneller schießen. |
| `wucht` | Wucht | giftzahn | Trifft deutlich härter. |
| `fluxpumpe` | Fluxpumpe | blutpreis | Gibt 60 Flux, kostet eine längere Pause. |
| `schnelllader` | Schnelllader | dauerladung | Lädt nach diesem Durchgang fast sofort. |
| `abzugsfeder` | Abzugsfeder | hast | Kürzere Pause bis zum nächsten Schuss. |

### Zünder (4)

| Schlüssel | Name | Bisher | Beschreibung |
|---|---|---|---|
| `aufschlagzuender` | Aufschlagzünder | nerv_aufprall | Setzt die nächste Gruppe beim Aufprall frei. |
| `zeitzuender` | Zeitzünder | nerv_zeit | Nach kurzer Zeit. |
| `endzuender` | Endzünder | nerv_ende | Am Ende des Flugs. |
| `naessezuender` | Nässezünder | nerv_naesse | Sobald das Geschoss in Flüssigkeit eintaucht. |

### Füllungen (10)

Füllungen müssen in jedem Universum funktionieren; deshalb nur Grundmaterialien, plus zwei Sonderfüllungen.

| Schlüssel | Name | Material | Beschreibung |
|---|---|---|---|
| `fuellung_wasser` | Wasserfüllung | Wasser | Löscht, macht nass, leitet Strom. |
| `fuellung_oel` | Ölfüllung | Öl | Brennbar und rutschig. |
| `fuellung_feuer` | Feuerfüllung | Feuer | Setzt in Brand. |
| `fuellung_rauch` | Rauchfüllung | Rauch | Nimmt die Sicht. |
| `fuellung_dampf` | Dampffüllung | Dampf | Verbrüht leicht. |
| `fuellung_sand` | Sandfüllung | Sand | Schüttet zu. |
| `fuellung_erde` | Erdfüllung | Erde | Baut eine Plattform. |
| `fuellung_fels` | Felsfüllung | Fels | Baut eine Deckung. |
| `fuellung_kolben` | Kolbenfüllung | Inhalt des Kolbens in der Hand | Verbraucht 10 Zellen deines Kolbens je Schuss. Ohne Kolben: Wasser. |
| `fuellung_lokal` | Lokalkolorit | zufälliges Universumsmaterial | Etwas, das es nur hier gibt. Überraschung! |

## Familien

Wie bisher erzeugt der Code weitere Module: **jede Grundform in jedem Element**, Aufsatz-Stufen I–IV, Ringformationen, Zeitzünder-Varianten. Neue Element-Liste: Wasser, Öl, Feuer, Rauch, Dampf, Sand, Erde, Fels, Flux (statt der 14 Biohorror-Elemente). Namen nach dem Schema „Wasser-Tropfen“, „Öl-Bombe“, „Sand-Säge“; Beschreibungstexte wie bisher mit `{n}`.

## Icons

Die vorhandene Icon-Erzeugung (`src/icons.py`) bleibt das Grundgerüst. Für die 60 Basismodule werden **gezeichnete** 16×16-Icons nach der Spalte „Icon-Idee“ erstellt (Rahmen in Kategorienfarbe, 1 px, abgerundete Ecken; Motiv 12×12 innen). Familien behalten das erzeugte Icon mit Element-Farbe.

## Flüssigkeiten: Schübe beim Trinken

Ein Schluck (30 Zellen) gibt einen zeitlich begrenzten Effekt. Kein Effekt ist Voraussetzung zum Schießen. Heilen tut keine Flüssigkeit ohne Selbstexperiment.

| Flüssigkeit | Universum | Effekt |
|---|---|---|
| Wasser | alle | Erfrischt: Flux lädt 20 % schneller, 15 s; löscht Brand |
| Öl | alle | Geschmiert: 15 % kürzere Verzögerung, 15 s; macht ölig |
| Flux-Schnaps | Werkstatt (Zapfhahn) | Beschwipst: Flux lädt 50 % schneller, Zielen schwankt, 20 s |
| Magensäure | Fleischwelt | 25 Schaden |
| Blut | Fleischwelt | nichts (mit Selbstexperiment „Blutsauger“: heilt) |
| Talg | Fleischwelt | Geschmiert wie Öl |
| Tinte | Aktenhalde | Tintenblick: Kreaturen leuchten durch Wände, 20 s |
| Stempelfarbe | Aktenhalde | Genehmigt (+20 % Schaden), 15 s |
| Siegellack | Aktenhalde | 15 Schaden (heiß) |
| Brausesirup | Glibbria | Sprudelnd: Sprungkraft +50 %, 20 s |
| Kaugummi | Glibbria | Klebrig, 5 s |
| Honig | Krümelreich | Flux sofort +100 |
| Karamell | Krümelreich | Klebrig + 10 Schaden (heiß) |
| Neonsaft | Sporenklub | Aufgedreht: Lauftempo +30 %, 20 s |
| (Leuchtsporen, Gas) | Sporenklub | Einatmen: Beschwipst |

Flux-Schnaps ist ein elftes Grundmaterial, das nur in der Werkstatt vorkommt (Zapfhahn, kostet 10 Gold je Kolbenfüllung).
