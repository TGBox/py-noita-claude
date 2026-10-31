# Cloita

Ein düsteres Falling-Sand-Roguelite in Python, inspiriert von Noita. Du steigst in einen
lebenden Organismus hinab. Jeder Pixel ist simuliert und kann mit allem reagieren: Blut
gerinnt, Säure ätzt, Wucherungen kriechen durch Fleisch, Sporen entzünden sich. Deine
Waffen sind Augmentationen, also Zauberstäbe aus Bausteinen, die als Arm aus deinem Körper
wachsen.

**Ziel:** Kämpf dich durch sieben Tiefen und zerstöre das Herz. Der Tod beendet den Lauf. Zwischen
den Tiefen wartet ein Sanktum mit Laden und Perks.

## Voraussetzungen

- [uv](https://docs.astral.sh/uv/)
- [Rust](https://rustup.rs) (`cargo`) für den Simulationskern. Unter Windows braucht Rust
  den MSVC-Linker (Visual Studio Build Tools mit "Desktopentwicklung mit C++").

## Schnellstart

```bash
uv sync               # Abhängigkeiten
uv run main           # Spiel starten (baut den Rust-Kern beim ersten Start automatisch)
uv run build-native   # Rust-Kern manuell neu bauen
uv run test           # Tests
uv run format         # Code formatieren
uv run lint           # Code prüfen
uv run build          # Standalone-Version mit PyInstaller bauen
```

## Steuerung

Alle Tasten lassen sich unter **Steuerung** (Titel oder Pause) neu belegen: Eintrag wählen,
Enter oder Klick, dann die neue Taste, Maustaste oder den Controller-Knopf drücken. Eine
Taste gehört immer nur einer Aktion; Entf stellt den Standard wieder her. Die Belegung wird in
`steuerung.json` neben den Statistiken gespeichert. Die aktuelle Belegung steht im
Pausenmenü: nur Tastatur und Maus, oder nur die Controller-Knöpfe, sobald ein Controller
angeschlossen ist. Eingeblendete Hinweise (Aufheben, Neuer Lauf) folgen ebenso dem Gerät.

| Standard | Controller | Aktion |
| ---------- | ----------- | -------- |
| **A / D** (oder Pfeile) | Linker Stick | Laufen |
| **W / Leertaste** | A | Kleiner Sprung; gedrückt halten zum Schweben |
| **Linke Maus** | RT (zielen mit rechtem Stick) | Zaubern mit der aktiven Augmentation |
| **1-4 / Mausrad** | RB / Steuerkreuz links | Augmentation wählen |
| **Q** | B | Treten: stößt Gegner weg, schleudert Gegenstände, bringt Säcke zum Platzen |
| **Rechte Maus** (halten) | LT | Phiole ausgießen: die Flüssigkeit spritzt im Bogen Richtung Mauszeiger, weg von der Figur |
| **S** (halten) | LB | Phiole füllen: Flüssigkeit am Mauszeiger aufsaugen |
| **F** | Y | Aus der Phiole trinken |
| **T** | Steuerkreuz hoch | Phiole werfen; sie zerplatzt beim Aufprall |
| **C / 5-8** | Steuerkreuz rechts | Nächste Phiole / Phiole 1-4 wählen |
| **E** | X | Aufheben, kaufen, Perk wählen |
| **Tab / I** | Back | Rucksack: jederzeit ansehen, im Sanktum umbauen |
| **L / M** | | Beleuchtung / Ton ein/aus |
| **F11** | | Vollbild |
| **N** | Steuerkreuz runter | Nach dem Sieg: Neues Spiel+ |
| **Enter** (fest) | A | Nach Tod oder Sieg: neuer Lauf |
| **ESC** (fest) | Start | Pause (dort auch „Neuer Lauf“); in Menüs: zurück |

Einen Lauf versehentlich neu starten geht nicht mehr: „Neuer Lauf“ gibt es nur im Pausenmenü
und nach dem Tod.

**Sandbox** (nur aus dem Hauptmenü): ein Testlauf, der nicht für Statistik, Kodex und
Spielstand zählt. Rechte Maus malt, mittlere radiert, Mausrad wählt das Material, +/- die
Pinselgröße, **G** schaltet den Gottmodus (kein Schaden, kein Tod), **N** erzeugt die Tiefe
neu, Bild auf/ab wechselt die Tiefe. Augmentationen lassen sich überall umbauen, und der
Rucksack hat ein **Zauberbuch** mit allen Zaubern aus dem Kodex: Hineinziehen setzt eine Kopie
ein, ein Baustein zurück ins Buch verschwindet.

**Menüs** lassen sich mit Pfeiltasten und Enter, mit der Maus oder mit dem Controller
(Steuerkreuz oder Stick, A wählt, B zurück) bedienen. **Controller:** Jeder Pad mit
Xbox-Belegung wird erkannt, auch wenn er während des Spiels eingesteckt wird. Im Rucksack
bewegt der linke Stick den Mauszeiger, A greift und lässt los.

**Was ist das?** Wie in Noita erklärt das Spiel, was unter dem Mauszeiger (oder dem
Controller-Fadenkreuz) liegt: Materialien (fest, flüssig, Gas, Härte, Schaden pro Sekunde,
brennbar), Kreaturen (Leben, Verhalten, Beute) und Gegenstände. Zauber im Laden zeigen Kosten,
Werte und Preis; Augmentationen am Boden zeigen ihre Werte als Balken, grün oder rot im
Vergleich zur Augmentation in der Hand. Verborgene Kammern und Gegenstände verrät der Mauszeiger nicht;
Kreaturen sieht und erkennt man dagegen überall, auch in unerkundeten, dunklen Bereichen.

**Treten (Q):** Stößt Kreaturen weg, die dann kurz hilflos durch die Luft taumeln, schleudert
Gegenstände und tritt Pulver und Flüssigkeit vor den Füßen beiseite.

**Nie eingemauert:** Material, das in der Figur entsteht (Schorf, Wucherung, Staub), wird
sofort aus ihr gedrückt. Ist die Figur trotzdem von allen Seiten eingeschlossen oder sitzt sie
in einer kleinen versiegelten Höhle fest, reißt sie sich nach kurzer Zeit ohne Schaden frei.

**Rucksack (Tab):** Zeigt alle Augmentationen mit ihren Werten als Balken, den Beutel mit
48 Plätzen (gleiche Zauber stapeln sich in einem Platz, die Zahl zeigt den Stapel) und bis zu vier Phiolen. Alles wird per Drag & Drop bewegt: Bausteine zwischen
Plätzen, eine Augmentation an ihrem Griff (umsortieren oder ablegen), Phiolen untereinander.
Was auf das Feld „Ablegen“ oder aus dem Fenster gezogen wird, fällt vor dir auf den Boden.
Ein Klick auf Griff oder Phiole nimmt sie in die Hand. **Rechtsklick oder Doppelklick** auf einen Zauber setzt ihn aus dem
Beutel in die Augmentation in der Hand oder legt ihn aus der Augmentation in den Beutel.
**Sortieren** fasst Stapel zusammen und ordnet den Beutel nach Drüsen, Mutationen, Nerven und
Sekreten. Mit Controller: X wie Rechtsklick, Y sortiert. Außerhalb des Sanktums kannst du
ansehen, den Beutel ordnen und ablegen; Augmentationen umbauen geht nur im Sanktum (oder mit
dem Perk „Flinke Hände“).

## Der Lauf

| Tiefe | Name | Wächter | Bewohner |
| ------- | ------ | --------- | ---------- |
| 1 | Der Schlund | - | 9 Maden, 4 Schwärmer |
| 2 | Der Magen | Der Magenwurm | 11 Maden, 8 Schwärmer, 3 Knochenspeier, 2 Sporenblasen |
| 3 | Das Knochenmark | Der Knochenfresser | 10 Maden, 6 Schwärmer, 8 Knochenspeier, 3 Sporenblasen, Säurespucker, Nervenknoten, Egel |
| 4 | Das Gedärm | Die Brutmutter | 13 Maden, 8 Schwärmer, 5 Knochenspeier, 7 Sporenblasen |
| 5 | Die Leber | - | 12 Maden, 7 Schwärmer, 4 Knochenspeier, 4 Sporenblasen, Säurespucker, Egel, Schleimkriecher |
| 6 | Die Lunge | Der Atem | 8 Maden, 10 Schwärmer, 5 Knochenspeier, 9 Sporenblasen |
| 7 | Die Herzkammer | Das Herz | 9 Maden, 7 Schwärmer, 4 Knochenspeier, 4 Sporenblasen |

**Wechselnde Wege:** Jede Stufe hat Varianten, und jeder Lauf wählt pro Stufe zufällig eine
(insgesamt 32 Biome). Statt des Schlunds geht es etwa durch die Speiseröhre (viele Sehnenbrücken)
oder die Zahnhöhle (Knochenwände), statt des Magens durch den Pansen, statt des Knochenmarks durch
das Rückenmark (Sehnen voller Nervenstrom), statt des Gedärms durch den Blinddarm (Eiter), statt
der Leber durch die Niere oder die Milz, statt der Lunge durch die Bronchien. Wächter und Ziel
bleiben pro Stufe gleich.

Am Ende jeder Tiefe führt ein Schließmuskel weiter. Im Magen öffnet er sich erst, wenn der
Magenwurm tot ist, im Gedärm erst nach der Brutmutter: Sie schwebt schwer durch ihre Halle,
schleudert Wucherungen, Knochenschrot und Sporen und gebiert abwechselnd Sporenblasen und
Gallenschwärmer. In der Herzkammer schlägt das Herz: Es feuert Ringe aus Feuer, Säure und
Funken und gebiert Maden. Die Tiefen werden dunkler, gefährlicher und bringen bessere Beute.

**Der Knochenfresser** frisst sich quer durch den Knochen auf dich zu und spürt dich auch durch
Wände; er wirft Knochensägen und Speere. **Der Atem** in der Lunge saugt dich immer wieder zu sich
heran, atmet dann einen Kranz aus Sporen aus und gebiert Blutegel.

**Das Knochenmark** ist umgekehrt gebaut: massiver Knochen, durchzogen von Fleischadern, mit
viel Knochenstaub, Blut und Talg. Knochen bricht bei Explosionen zu Staub, der nachrutscht.

**Die Leber** ist eng und giftig: Gallengänge voller Säure, Eiterlachen, wuchernde Nester
und Säcke, die bei jedem Fehlschuss platzen.

**Die Lunge** besteht aus großen Hohlräumen und schwammigem Gewebe: Trauben aus Luftbläschen
mit dünnen, eingerissenen Sehnenhäutchen. Von den Decken tropft zäher Schleim. Darin bewegst du
dich (und jede Kreatur) nur sehr langsam, dafür erstickt er Feuer und bindet Sporen.

**Das Sanktum:** Zwischen zwei Tiefen liegt eine sichere Kammer. Sie heilt dich und füllt
deine Augmentationen auf. Dort gibt es einen Laden mit vier Bausteinen und einer Augmentation
(bezahlt mit Blutperlen) und einen Altar mit drei Perks, von denen du einen wählst.
Neben dem Altar wuchert ein Würfelgewächs: Für Blutperlen würfelt es die drei Perks neu
(100 Perlen, jedes weitere Mal doppelt so teuer). Nur hier darfst du Augmentationen umbauen.

**Statistik:** Der Titelbildschirm zeigt deine Läufe, Siege, die tiefste erreichte Tiefe und
den schnellsten Sieg. Sie liegt als `records.json` im Benutzerordner (Windows:
`%APPDATA%\Cloita`). Läufe, in denen du die Sandbox (F1) benutzt hast, zählen nicht.

**Speichern und Fortsetzen:** Beim Betreten eines Sanktums wird der Lauf gespeichert
(`lauf.json` im selben Ordner). Nach einem Neustart setzt du ihn im Titel mit **F** fort und
stehst wieder in diesem Sanktum, mit demselben Laden und denselben Perks. Tod, Sieg oder ein
neuer Lauf löschen den Spielstand.

**Kodex:** Jeder Baustein, den du aufhebst, und jede Kreatur, die du tötest, wird dauerhaft im
Kodex eingetragen (Titel, **K**). Neue Einträge meldet das Spiel mit „Neu im Kodex“.
Der Kodex schaltet auch etwas frei: Bausteine, die du kennst, tauchen deutlich häufiger im
Laden auf, und für jeden Wächter, den du je bezwungen hast, startest du einen neuen Lauf mit
30 Blutperlen mehr.

**Treffer:** Wunden bluten echtes Material in die Welt: Maden und Schwärmer Blut, der
Magenwurm Säure, Sporenblasen und die Brutmutter Sporen. Über getroffenen Körpern steigen
Schadenszahlen auf (abschaltbar in den Optionen).

**Musik:** Jede Tiefe hat einen eigenen, prozedural erzeugten Klangteppich aus Drones, Atem und
einem fernen Herzschlag, der in der Herzkammer schneller wird. Die Schleifen werden beim ersten
Start im Hintergrund erzeugt und unter `%APPDATA%\Cloita\musik` zwischengespeichert. Eigene
Dateien `assets/audio/musik_<tiefe>.wav/.ogg` (z. B. `musik_lunge.ogg`) ersetzen sie.

**Phiolen:** Du trägst bis zu vier Phiolen und wechselst mit C (oder 5-8) zwischen ihnen. Du startest mit einer halb vollen Phiole Blut, und in jeder Tiefe liegen weitere,
mal gefüllt (Blut, Säure, Talg, Schleim), mal leer. Eine Phiole fasst 300 Zellen einer einzigen
Flüssigkeit. Ausgegossenes ist echtes Material in der Welt: Blut löscht Brände, Säure frisst
Wände, Talg wird zur Brandfalle. Trinken wirkt je nach Inhalt (Blut heilt ein wenig, Säure ätzt
dich, jeder Schluck löscht Feuer). Geworfen zerplatzt die Phiole und verteilt alles auf einmal.

**Blutperlen** liegen in den Höhlen und fallen aus jedem getöteten Gegner. Du sammelst sie
durch Berührung ein.

**Gegner:**

- Fleischmaden kriechen, springen über Kanten und beißen.
- Gallenschwärmer fliegen und spucken Säureklumpen.
- Knochenspeier hängen unter Decken und schießen Nadelsalven.
- Sporenblasen treiben auf dich zu und platzen zu einer entzündlichen Sporenwolke.
- Blutegel schwirren schnell heran und saugen (ab dem Schlund).
- Säurespucker kriechen und werfen Säure im Bogen; Säure macht ihnen nichts (ab dem Magen).
- Brandmaden sind feuerfest und zerplatzen zu Flammen (ab dem Gedärm).
- Schleimkriecher sind zäh und langsam, beißen hart und hinterlassen Schleim (Lunge).
- Augenblasen schweben hoch oben und schießen Knochenspeere über große Distanz (ab der Lunge).
- Nervenknoten hängen an Decken und feuern Funkenkränze in alle Richtungen (Herzkammer).
- Gestaltwandler schweben auf Abstand und verwandeln dich mit einer Wandlungsdrüse für einige
  Sekunden in eine Made: kein Zaubern, keine Phiole, langsam (Leber und Herzkammer).

**Parallelwelten:** In der Schatzkammer des Schlunds wartet ein Weltenportal. Wer hindurchgeht,
beginnt den Lauf in der nächsten Parallelwelt von vorn (wie Noitas Parallelwelten), und auch dort
liegt wieder ein Portal: Wie in Noita zählt die Richtung: Liegt die Schatzkammer am Ostrand, führt das Portal nach
Osten, am Westrand nach Westen. Westliche Welten sind zusätzlich finsterer. Die Welten sind
durchnummeriert und reichen in beide Richtungen beliebig weit. Jede Welt hat
einen neuen Weg durch die Biome, ungerade Welten sind seitenverkehrt, und mit jeder Welt werden
Kreaturen deutlich zäher und die Beute reicher. Ausrüstung und Perks nimmst du mit.

**Wucht:** Explosionen schleudern Körper weg: Gegner, Säcke und auch dich (Raketensprünge wie in
Noita sind möglich, kosten aber Leben). Leichte Körper fliegen weiter, Wächter bewegen sich kaum. Auch lose Gegenstände (Augmentationen, Phiolen, Bausteine, Blutperlen) fliegen davon, prallen ab
und rutschen aus; ein Tritt (Q) schleudert sie weg.

**Neues Spiel+:** Nach dem Sieg führt **N** noch tiefer: Du behältst Augmentationen, Beutel,
Perks und Phiole und steigst erneut durch alle Tiefen hinab. Mit jeder Runde haben Kreaturen
60 % mehr Leben und mehr Schaden. Die Statistik merkt sich die höchste bezwungene Runde.

**Schatzkammern:** Am linken oder rechten Rand jeder Tiefe (außer der Herzkammer) liegt eine
Halle hinter dicken Knochenwänden. Wer sie aufsprengt, findet eine starke Augmentation, Bausteine
und Blutperlen, aber auch einen dreifach gestärkten Hüter.

**Uraugen (Geheimnis):** Jede Tiefe verbirgt ein Urauge in einer versiegelten Knochenkammer
tief im Gewebe. Wer nah genug ist, spürt es („Hinter der Wand pulsiert etwas“), freilegen musst du
es selbst. Jedes Urauge gibt +10 maximales Leben. Wer alle sieben trägt und das Herz zerstört,
erlebt das wahre Ende. Der Titel zählt Uraugen und wahre Siege.

**Einstürze (Starrkörper):** Sprengst du einen Brocken frei, sodass er nirgends mehr anhängt,
wird er wie in Noita zum Starrkörper: mit Schwerpunkt, Geschwindigkeit, Winkel und Drehung. Die
Explosion schleudert ihn weg und versetzt ihn in Drehung, er prallt ab, kippt über Kanten, rollt
aus, zerquetscht, was darunter steht, und wird wieder zu festem Gewebe, sobald er still liegt.
Die Suche nach losen Brocken läuft im Rust-Kern.

**Säcke:** Überall liegen prall gefüllte Säcke wie Fässer in Noita. Ein Treffer genügt:
Talgsäcke explodieren in brennendes Fett, Säuresäcke platzen ätzend, Sporensäcke entlassen eine
entzündliche Wolke. Explosionen reißen benachbarte Säcke mit, und auch Gegnerschüsse bringen
sie zum Platzen.

**Fundstücke:** In jeder Tiefe liegt ein **Herzklumpen** (+20 maximales Leben, heilt voll) und
zwei **Brutkokons**, die beim Öffnen (E) Blutperlen und zufällige Beute ausspucken.

Gegner erinnern sich drei Sekunden lang daran, wo sie dich zuletzt gesehen haben. Deine
eigenen Explosionen verletzen auch dich.

**Statuseffekte:** Wer Feuer berührt, fängt an zu brennen, nimmt Schaden und setzt die Umgebung
in Brand. Flüssigkeit löscht und macht nass, und nasse Körper fangen kein Feuer. Talg dagegen
löscht nicht: Er macht **ölig**, und ölige Körper brennen länger und heißer, bis Wasser, Blut
oder Schleim das Fett abwaschen. Schleim macht **verschleimt** und bremst noch kurz nach. Eiter **vergiftet** (Schaden über Zeit); ein Schluck Blut aus der Phiole spült das Gift aus. Das
gilt für dich und für alle Gegner.

**Perks** (je Lauf jeder höchstens einmal):

| Perk | Wirkung |
| ------ | --------- |
| Feuerfeste Haut | Feuer kann dir nichts mehr anhaben. |
| Säurehaut | Magensäure und Ätzdampf verletzen dich nicht. |
| Zähes Fleisch | +50 maximale Lebenspunkte. |
| Leichte Knochen | Du schwebst 50 % länger. |
| Panzerplatten | Explosionen verletzen dich kaum noch. |
| Blutdurst | Jeder getötete Gegner heilt dich um 6. |
| Schnelle Drüsen | Augmentationen zaubern und laden 25 % schneller. |
| Säureblut | Wenn du verletzt wirst, spritzt ätzendes Blut um dich. |
| Zweiter Puls | Einmal pro Lauf stehst du nach dem Tod wieder auf. |
| Flinke Hände | Du kannst Augmentationen überall umbauen, nicht nur im Sanktum. |
| Wutdrüsen | Deine Geschosse richten 30 % mehr Schaden an. |
| Perlenmagnet | Blutperlen fliegen dir aus großer Entfernung zu. |
| Ausdauernde Flughäute | Deine Schwebekraft lädt sich auch in der Luft schnell auf. |
| Gaslunge | Sporen und Ätzdampf schaden dir nicht. |
| Schleimläufer | Schleim bremst dich nicht mehr. |
| Feilscher | Im Laden zahlst du ein Drittel weniger. |

## Augmentationen (Zauberstäbe)

Eine Augmentation ist ein Deck aus Bausteinen, das beim Zaubern der Reihe nach gezogen wird.

**Ladungen:** Besonders starke Bausteine (Sprungdrüse, Fressgeschwür, Knochenbombe, Wandlungs-
und Tauschdrüse, Glutkugel, Achterkreis, Zehnfachzauber, Glutsekret) haben nur wenige Ladungen.
Die Zahl unten rechts am Baustein zeigt, wie viele noch übrig sind; aufgefüllt wird nur im
Sanktum (wie an Noitas Heiligem Berg). Leere Bausteine werden beim Zaubern übersprungen.

- **Drüse** (Form): das Projektil. Sie beendet einen Zug.
- **Mutation**: verändert die nächste Drüse. Der Doppelzauber zieht zwei Gruppen auf einmal.
- **Nerv** (Auslöser): Die nächste Gruppe wird zur Ladung der Drüse und bei Aufprall, nach
  Zeit, am Flugende oder bei Kontakt mit Flüssigkeit freigesetzt.
- **Sekret** (Nutzlast): Die Drüse hinterlässt am Ende dieses Material.

Jede Augmentation hat eigene Werte: Slots, Mana und Aufladung, Zauberverzögerung, Nachladezeit,
Streuung, Zauber pro Wurf und ob sie ihr Deck mischt. Bausteine, für die das Mana nicht reicht,
werden übersprungen. Gefundene Augmentationen werden prozedural erzeugt und sind in tieferen
Ebenen stärker. Du trägst bis zu vier Augmentationen und 48 Stapel loser Bausteine.

| Baustein | Typ | Mana | Wirkung |
| ---------- | ----- | ------ | --------- |
| Funke | Drüse | 5 | Schneller Funke, kleine Explosion. |
| Knochennadel | Drüse | 3 | Sehr schnell, gräbt sich nur wenig ein. |
| Gallenblase | Drüse | 25 | Prallt ab und platzt nach kurzer Zeit mit großer Wucht. |
| Klumpen | Drüse | 6 | Fliegt im Bogen und zerplatzt zu einer Lache. |
| Knochensplitter | Drüse | 12 | Ein Schrot aus fünf Splittern auf kurze Distanz. |
| Zahnbohrer | Drüse | 18 | Frisst sich ein Stück weit durch Fleisch und Knochen. |
| Blutegel | Drüse | 15 | Langsam; heilt dich um die Hälfte des Schadens, den er anrichtet. |
| Sprungdrüse | Drüse | 40 | Wo sie aufschlägt, reißt sie dich hin. |
| Knochensäge | Drüse | 20 | Eine kreisende Klinge: prallt oft ab und schneidet durch alles Lebende. |
| Sporenmine | Drüse | 25 | Bleibt liegen und platzt, sobald etwas Lebendes nahe kommt. |
| Fressgeschwür | Drüse | 60 | Eine träge Kugel, die einen breiten Gang durch das Gewebe frisst. |
| Knochenspeer | Drüse | 22 | Schwer und durchschlagend: spießt alles in seiner Bahn auf. |
| Gallenregen | Drüse | 18 | Sechs Gallentropfen im hohen Bogen. |
| Talgblase | Drüse | 14 | Eine schwerfällige Blase, die zu einer großen Lache zerplatzt. |
| Mikrofunke | Drüse | 1 | Winzig, billig und sehr schnell. |
| Brandgeschwulst | Drüse | 45 | Ein glühender Klumpen, der in einer brennenden Explosion aufgeht. |
| Knochenbombe | Drüse | 55 | Prallt einmal ab und sprengt dann einen gewaltigen Krater. |
| Nadelregen | Drüse | 16 | Acht Nadeln auf einmal. |
| Sporenball | Drüse | 12 | Eine weiche Kugel, die zu einer Sporenwolke zerplatzt. |
| Schleimkugel | Drüse | 10 | Klebt Gegner fest und löscht Brände. |
| Grabklaue | Drüse | 8 | Kratzt einen schmalen, langen Gang ins Gewebe. |
| Nervenstrom | Drüse | 20 | Ein Stromstoß: Trifft er Sehnen, jagt ein Strom durch das ganze Geflecht. |
| Wandlungsdrüse | Drüse | 60 | Wen sie trifft, der wird zu etwas anderem. Wächter widerstehen. |
| Tauschdrüse | Drüse | 25 | Trifft sie eine Kreatur, tauschst du mit ihr den Platz. |
| Kettenfunke | Drüse | 22 | Springt nach einem Treffer auf bis zu drei weitere Kreaturen über. |
| Leuchtkugel | Drüse | 10 | Schwebt lange und leuchtet die Dunkelheit weit aus. |
| Säurepfeil | Drüse | 9 | Schnell und ätzend. |
| Blutstrahl | Drüse | 3 | Ein dünner Strahl Blut: löscht Brände, schadet kaum. |
| Talgbombe | Drüse | 30 | Prallt ab und platzt dann zu einer brennenden Fettlache. |
| Dornenhagel | Drüse | 26 | Zwölf Knochendornen in alle Richtungen nach vorne. |
| Kauleiste | Drüse | 35 | Eine Reihe Zähne, die lange durch Wände und Gegner mahlt. |
| Gelenkkugel | Drüse | 12 | Prallt immer wieder von Wänden ab. |
| Giftblase | Drüse | 14 | Zerplatzt zu einer Lache vergiftenden Eiters. |
| Glutkugel | Drüse | 50 | Ein Tropfen Glutblut, der alles in Brand setzt, was er berührt. |
| Beschleunigung | Mutation | 3 | Nächste Drüse fliegt schneller. |
| Sprengkraft | Mutation | 12 | Größere Explosion. |
| Schwerkraftumkehr | Mutation | 4 | Nächste Drüse fällt nach oben. |
| Zielsuche | Mutation | 8 | Nächste Drüse lenkt zum Mauszeiger. |
| Doppelzauber | Mutation | 2 | Zieht zwei Gruppen auf einmal. |
| Durchbohren | Mutation | 10 | Nächste Drüse fliegt durch Kreaturen hindurch. |
| Abprall | Mutation | 5 | Nächste Drüse prallt dreimal von Wänden ab. |
| Brandbeschleuniger | Mutation | 8 | Getroffene Kreaturen fangen Feuer. |
| Langlebigkeit | Mutation | 4 | Nächste Drüse fliegt doppelt so lange, aber langsamer. |
| Dreifachzauber | Mutation | 3 | Zieht drei Gruppen auf einmal. |
| Vierfachzauber | Mutation | 5 | Zieht vier Gruppen auf einmal. |
| Achterkreis | Mutation | 12 | Zieht acht Gruppen und verschießt sie im Kreis um dich. |
| Fächer | Mutation | 6 | Zieht fünf Gruppen und fächert sie weit auf. |
| Vorne und hinten | Mutation | 4 | Zieht zwei Gruppen: eine nach vorne, eine nach hinten. |
| Rasende Drüse | Mutation | 10 | Nächste Drüse fliegt zweieinhalbmal so schnell. |
| Sprengkern | Mutation | 25 | Viel größere Explosion. |
| Kurzlebigkeit | Mutation | 1 | Nächste Drüse vergeht nach halber Zeit, dafür zauberst du schneller. |
| Giftzahn | Mutation | 9 | Nächste Drüse trifft deutlich härter und brennt sich ein. |
| Blutpreis | Mutation | -60 | Gibt 60 Mana, kostet aber eine längere Pause. |
| Dauerladung | Mutation | 20 | Die Augmentation lädt nach diesem Durchgang fast sofort nach. |
| Schleimspur | Mutation | 6 | Nächste Drüse zieht eine zähe Schleimspur. |
| Sporenspur | Mutation | 6 | Nächste Drüse zieht eine Sporenwolke hinter sich her. |
| Bluthunger | Mutation | 14 | Nächste Drüse sucht den Mauszeiger und fliegt schneller. |
| Glutspur | Mutation | 18 | Nächste Drüse tropft Glutblut. |
| Eiterspur | Mutation | 6 | Nächste Drüse tropft vergiftenden Eiter. |
| Zündfunke | Mutation | 4 | Kleine Explosion am Ende des Flugs. |
| Gleitfähigkeit | Mutation | 3 | Nächste Drüse fällt nur halb so stark und fliegt länger. |
| Bleischwere | Mutation | 2 | Nächste Drüse fällt dreimal so stark. |
| Glühende Spitze | Mutation | 16 | Nächste Drüse fliegt durch Kreaturen und setzt sie in Brand. |
| Gummisehne | Mutation | 8 | Nächste Drüse prallt sechsmal ab. |
| Zehnfachzauber | Mutation | 20 | Zieht zehn Gruppen und fächert sie breit. |
| Schwerelosigkeit | Mutation | 2 | Nächste Drüse fällt nicht. |
| Schwere Ladung | Mutation | 7 | Mehr Schaden, aber langsamer. |
| Schadenszuwachs | Mutation | 5 | Nächste Drüse trifft härter. |
| Blutspur | Mutation | 4 | Nächste Drüse zieht eine Blutspur hinter sich her. |
| Säurespur | Mutation | 10 | Nächste Drüse tropft Magensäure. |
| Feuerspur | Mutation | 8 | Nächste Drüse zieht eine Flammenspur. |
| Talgspur | Mutation | 4 | Nächste Drüse tropft Talg. |
| Streuung | Mutation | 1 | Nächste Drüse fliegt ungenau. |
| Mana-Zuschuss | Mutation | -30 | Gibt beim Zaubern 30 Mana zurück. |
| Hast | Mutation | 4 | Verkürzt die Pause bis zum nächsten Zauber. |
| Schnellladung | Mutation | 8 | Die Augmentation lädt nach diesem Durchgang schneller nach. |
| Aufprall-Nerv | Nerv | 6 | Setzt die nächste Gruppe beim Aufprall frei. |
| Zeit-Nerv | Nerv | 6 | Setzt die nächste Gruppe nach kurzer Zeit frei. |
| End-Nerv | Nerv | 6 | Setzt die nächste Gruppe am Ende des Flugs frei. |
| Nässe-Nerv | Nerv | 4 | Setzt die nächste Gruppe frei, wenn die Drüse Flüssigkeit trifft. |
| Blutsekret | Sekret | 6 | Hinterlässt Blut |
| Talgsekret | Sekret | 8 | Hinterlässt Talg |
| Säuresekret | Sekret | 14 | Hinterlässt Magensäure |
| Feuersekret | Sekret | 10 | Hinterlässt Feuer |
| Sporensekret | Sekret | 10 | Hinterlässt Sporen |
| Schleimsekret | Sekret | 8 | Hinterlässt Schleim |
| Rauchsekret | Sekret | 3 | Hinterlässt Rauch |
| Glutsekret | Sekret | 30 | Hinterlässt Glutblut, das alles Brennbare entzündet. |
| Eitersekret | Sekret | 8 | Hinterlässt vergiftenden Eiter. |
| Ätzdampfsekret | Sekret | 12 | Hinterlässt Ätzdampf |
| Staubsekret | Sekret | 5 | Hinterlässt Knochenstaub |
| Sehnensekret | Sekret | 12 | Baut einen Klumpen Sehnen - eine Plattform zum Draufstehen. |
| Knochensekret | Sekret | 16 | Baut einen Klumpen Knochen - eine Deckung gegen Geschosse. |
| Wucherungssekret | Sekret | 12 | Pflanzt eine Wucherung, die sich durch Fleisch frisst. |

**Zauberfamilien:** Neben den 94 handgemachten Bausteinen oben gibt es 310 Familienbausteine
(insgesamt 404, so viele wie Noita Zauber hat). Jede Grundform gibt es in jedem Element:
Formen Tropfen, Kugel, Bombe, Regen, Strahl, Bohrer, Sucher, Splitter, Mine, Säge, Welle, Geschoss, Blase, Nadel, Kette, Schauer, Klinge, Leuchte; Elemente Blut, Säure, Talg, Sporen, Schleim, Eiter, Glut, Staub, Dampf, Rauch, Feuer, Wucher, Sehnen, Knochen (z. B. Glutbombe, Sporenregen, Eiternadel, Knochenwelle).
Dazu Element-Kerne und -Spuren als Mutationen, Stufen I–IV für Tempo, Wucht, Sprengsatz, Dauer,
Schwere, Federung, Zittern, Eile, Nachwuchs und Blutopfer, Ringformationen mit 3 bis 12 Gruppen,
Zange, Bündel, Weiter Fächer sowie Zeit-Nerven mit 0,15 s, 0,8 s und 1,5 s. Familienbausteine sind
seltener als die handgemachten.

Vorlagen (in `src/wand.py`). Du startest mit den ersten beiden:

| Augmentation | Bausteine |
| -------------- | ----------- |
| Funkendrüse | Beschleunigung > Funke > Funke > Funke |
| Gallenwerfer | Talgsekret > Gallenblase > Feuersekret > Klumpen |
| Nervennadel | Aufprall-Nerv > Knochennadel > Doppelzauber > Säuresekret > Klumpen > Säuresekret > Klumpen |
| Sporenschleuder | Zielsuche > Zeit-Nerv > Funke > Doppelzauber > Sporensekret > Klumpen > Feuersekret > Funke |

## Materialien und Reaktionen

| Material | Verhalten |
| ---------- | ----------- |
| Fleisch | Feste Wand; verkohlt im Feuer zu Schorf, blutet bei Explosionen |
| Knochen | Fest; kleine Zauber prallen ab, Explosionen sprengen ihn (teils zu Knochenstaub) |
| Zahnschmelz | Sehr hart: nur große Explosionen brechen ihn, Bohrer kommen nicht durch. Adern davon ziehen sich durch die Wände, besonders in Zahnhöhle, Schädel und Knochenmark |
| Panzerknochen | Unzerstörbar (Weltrand, Sanktum) |
| Knochenstaub | Pulver, rutscht und häuft sich |
| Sehnen | Brücken; brennen langsam ab |
| Blut | Flüssigkeit; löscht Feuer (wird dabei zu Schorf), weicht Knochenstaub zu Schorf auf |
| Talg | Leicht, schwimmt auf Blut, brennt heftig |
| Magensäure | Ätzt Fleisch, Sehnen, Schorf, Wucherung und (langsam) Knochen; verbraucht sich dabei und gibt Ätzdampf ab; leuchtet |
| Wucherung | Wächst in Fleisch, frisst Blut, setzt Sporen frei; brennt |
| Sporen | Gas; infizieren Fleisch und Sehnen, entzünden sich explosionsartig |
| Schleim | Sehr zähe Flüssigkeit; bremst alles, was darin steckt, erstickt Feuer, bindet Sporen; Säure zersetzt ihn langsam |
| Glutblut | Geschmolzenes Blut (Herzkammer); verbrennt, entzündet Talg, Sehnen, Sporen; erstarrt in Blut, Schleim und Eiter zu Schorf; leuchtet |
| Eiter | Flüssigkeit (Gedärm); vergiftet, wer hineingerät, und lässt Fleisch langsam wuchern; Säure zersetzt ihn |
| Nervenstrom | Strom, der als Welle durch Sehnen läuft (Brücken, Lungenhäutchen); verletzt jeden, der die Sehne berührt, entzündet Sporen und Talg. Die Sehne ist danach kurz erschöpft und wächst wieder zusammen |
| Feuer, Rauch, Ätzdampf | Steigen auf und vergehen; Feuer leuchtet |

**Härte:** Wie Noitas dichter Fels hält nicht jedes Gewebe gleich viel aus. Weiches Gewebe
(Fleisch, Schorf, Wucherung, Knochenstaub) gibt jedem Zauber nach. Festes Gewebe (Knochen,
Sehnen) ist für Explosionen um 2 Zellen kleiner: Eine Knochennadel kratzt es kaum an, ein
Funke schlägt ein kleines Loch. Zahnschmelz ist für Explosionen um 9 Zellen kleiner und
widersteht Bohrern ganz; nur Gallenblasen, Bomben und verstärkte Explosionen brechen ihn.

**Geschosse und Flüssigkeiten:** Wie in Noita tauchen Geschosse durch Blut, Säure und andere
Flüssigkeiten hindurch, nur gebremst, und treffen auch Kreaturen unter der Oberfläche. Der
Nässe-Nerv löst beim Eintauchen aus.

Reaktionen stehen als Tabelle in `src/reactions.py`. Eine neue Wechselwirkung ist eine Zeile.

## Technik

- Sichtbarer Ausschnitt: 640x360 Weltpixel, verzerrungsfrei auf Fenster oder Vollbild skaliert.
- Welt: 1280x720 Zellen pro Tiefe, aufgeteilt in 16x16-Chunks. Ruhende Chunks schlafen, und
  simuliert wird nur ein Bereich um die Kamera.
- Die Zellsimulation, das Rendern und die Beleuchtung laufen in einem kleinen Rust-Kern ohne
  externe Pakete (`native/`), der per `ctypes` direkt auf den Python-Puffern arbeitet. Alle
  Material- und Reaktionsdaten kommen aus Python.
- Beleuchtung: Leuchtende Materialien und dynamische Lichter (Spielfigur, Projektile,
  Ausgang, Bosse) ergeben ein weiches Lichtfeld, das in vier Helligkeitsstufen der Palette
  gerastert wird.
- Die gesamte Spiellogik (`src/run.py` und darunter) kommt ohne pygame aus und ist getestet.
- Licht wird von festen Materialien verdeckt (Strahlen durch das Lichtraster).
- Alle Soundeffekte werden beim Start synthetisiert (`src/sounds.py`): tiefe, gedämpfte,
  organische Klänge mit weichen Ein- und Ausblendungen. Ohne Audiogerät bleibt das Spiel stumm.
- Eigene Sounds: Leg `<ereignis>.wav` oder `.ogg` nach `assets/audio/` (Varianten als
  `<ereignis>_1.wav`, `<ereignis>_2.wav`, ...). Sie ersetzen dann den synthetisierten Klang.
  Ereignisse: `cast`, `blast`, `blast_big`, `hurt`, `kill`, `pickup`, `pearl`, `buy`, `perk`,
  `descend`, `death`, `victory`.
- Die Weltgenerierung garantiert per Wegsuche, dass jeder Ausgang erreichbar ist (die Figur
  passt durch jeden Tunnel); lose Bruchstücke zerbröseln nach Explosionen.
- **Protokoll für Spieltests:** Jeder Lauf schreibt eine Datei `protokolle/lauf-<Zeit>.jsonl`
  in den Datenordner (Windows: `%APPDATA%\Cloita`, Linux: `~/.local/share/cloita`, macOS:
  `~/Library/Application Support/Cloita`). Jede Zeile ist ein JSON-Objekt mit Zeitpunkt und
  Ereignis: Start (Seed, Route, Optionen, Controller), jede Tiefe und jedes Sanktum mit
  Angeboten, Aufheben und Kaufen, Ablegen, Trinken, Werfen, Schaden nach Ursache, getötete
  Kreaturen, Wächter, Tod mit Ursache und Ort, alle 10 Sekunden Position und Leben,
  Bildraten pro Tiefe (Mittel, 99. Perzentil, Maximum), geänderte Tasten und Fehler mit
  vollständigem Traceback. Die 30 neuesten Protokolle bleiben erhalten; der Pfad steht im
  Pausenmenü und nach dem Tod.
- Zauber-Icons werden aus den Eigenschaften jedes Bausteins gezeichnet (`src/icons.py`):
  Rahmen in der Farbe der Kategorie, ein Symbol für die Wirkung (Bombe, Bohrer, Ring,
  Auge für Zielsuche, Nerv mit Auslöser, ...), eingefärbt mit dem Material.
- Kreaturen haben einen schwachen hellen Rand und leuchten ein wenig: Auch in finsteren
  Tiefen und hinter Wänden sieht man sie.
- Das Bewegungsgefühl und die Zauberstab-Regeln orientieren sich an Noita. Code, Grafiken und
  Texte von Noita werden nicht verwendet.

## Projektstruktur

```text
py-noita-claude/
├── native/              # Rust-Kern: Simulation, Rendern, Licht (keine Abhängigkeiten)
├── src/
│   ├── main.py          # Fenster, Eingabe, Kamera, Zeichnen
│   ├── run.py           # Ein Lauf: Tiefen, Kampf, Beute, Ausgang, Sieg/Tod
│   ├── depths.py        # Die sieben Tiefen und ihre Eigenschaften
│   ├── worldgen.py      # Prozedurale Level mit Ausgang und Bossarena
│   ├── world.py         # Weltpuffer, Malen, Explosionen, Kollision
│   ├── materials.py     # Materialien, Palette, Leuchtkraft
│   ├── reactions.py     # Reaktionstabelle
│   ├── body.py          # Gemeinsame Körperphysik (Spieler und Gegner)
│   ├── player.py        # Spielfigur: Laufen, Hüpfen, Schweben
│   ├── enemies.py       # Gegner, Bosse, Platzierung
│   ├── spells.py        # Baustein-Katalog
│   ├── wand.py          # Augmentationen: Deck-Logik und Vorlagen
│   ├── projectiles.py   # Projektile, Auslöser, Explosionen, Treffer
│   ├── chunks.py        # Herabfallende, losgesprengte Gewebebrocken
│   ├── flask.py         # Phiolen: gießen, aufsaugen, trinken, werfen
│   ├── loot.py          # Prozedurale Augmentationen, Gegenstände in der Welt
│   ├── inventory.py     # Augmentationen und Beutel, Umbau-Logik
│   ├── editor.py        # Rucksack: ansehen, umbauen, ablegen (pygame)
│   ├── editor_layout.py # Rucksack-Layout (rein geometrisch, testbar)
│   ├── perks.py         # Perks
│   ├── menus.py         # Titel, Pause, Optionen, Steuerung, Kodex
│   ├── ui.py            # Gemeinsame UI-Bausteine: Paneele, Balken, Icons, Tooltips
│   ├── hover.py         # Was unter dem Mauszeiger liegt (testbar)
│   ├── icons.py         # Pixel-Icons für alle Bausteine (testbar)
│   ├── keybinds.py      # Frei belegbare Steuerung (testbar)
│   ├── gamepad.py       # Controller-Eingabe
│   ├── runlog.py        # Lauf-Protokoll für Spieltests
│   ├── records.py       # Statistik, Kodex und Spielstand (JSON im Benutzerordner)
│   ├── music.py         # Prozedurale Ambient-Musik pro Tiefe (testbar)
│   ├── options.py       # Einstellungen (JSON im Benutzerordner)
│   ├── floaters.py      # Aufsteigende Schadenszahlen
│   ├── sounds.py        # Synthetisierte Soundeffekte (testbar)
│   ├── audio.py         # Wiedergabe mit stummem Fallback
│   ├── hud.py           # Anzeige
│   ├── rendering.py     # Welt, Figuren, Bosse, Gegenstände zeichnen
│   ├── texture.py       # Marmorierte Materialtextur
│   ├── native.py        # Lädt und baut den Rust-Kern
│   ├── viewport.py      # Virtuelle Auflösung / Letterboxing
│   ├── settings.py      # Auflösung, FPS, Konstanten
│   ├── tools.py         # Format, Lint, Rust-Build
│   └── build.py         # PyInstaller-Build
└── tests/
```
