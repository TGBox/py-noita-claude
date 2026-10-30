# Cloita

Ein düsteres Falling-Sand-Roguelite in Python, inspiriert von Noita. Du steigst in einen
lebenden Organismus hinab. Jeder Pixel ist simuliert und kann mit allem reagieren: Blut
gerinnt, Säure ätzt, Wucherungen kriechen durch Fleisch, Sporen entzünden sich. Deine
Waffen sind Augmentationen, also Zauberstäbe aus Bausteinen, die als Arm aus deinem Körper
wachsen.

**Ziel:** Kämpf dich durch vier Tiefen und zerstöre das Herz. Der Tod beendet den Lauf. Zwischen
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

| Taste | Aktion |
|-------|--------|
| **A / D** (oder Pfeile) | Laufen |
| **W / Leertaste** | Kleiner Sprung; gedrückt halten zum Schweben (3 s, am Boden schnell wieder voll) |
| **Linke Maus** | Zaubern mit der aktiven Augmentation |
| **1-4 / Mausrad** | Augmentation wählen |
| **E** | Gegenstand aufheben (Augmentation oder Baustein) |
| **Tab** | Augmentationen umbauen (pausiert; Bausteine per Drag & Drop verschieben) |
| **Enter** | Im Titel: Lauf beginnen |
| **R** | Neuer Lauf |
| **L** | Beleuchtung ein/aus |
| **M** | Ton ein/aus |
| **H** | Hilfe ein/aus |
| **F1** | Sandbox: Rechte Maus malt, mittlere radiert, 1-0 Material, Mausrad Pinselgröße, N neue Welt |
| **F11** | Vollbild |
| **ESC** | Pause (Weiter, neuer Lauf, Titel, Beenden); im Umbau-Bildschirm: schließen |

## Der Lauf

| Tiefe | Name | Wächter | Bewohner |
|-------|------|---------|----------|
| 1 | Der Schlund | - | 9 Maden, 4 Schwärmer |
| 2 | Der Magen | Der Magenwurm | 11 Maden, 8 Schwärmer, 3 Knochenspeier, 2 Sporenblasen |
| 3 | Das Gedärm | - | 13 Maden, 8 Schwärmer, 5 Knochenspeier, 7 Sporenblasen |
| 4 | Die Herzkammer | Das Herz | 9 Maden, 7 Schwärmer, 4 Knochenspeier, 4 Sporenblasen |

Am Ende jeder Tiefe führt ein Schließmuskel weiter. Im Magen öffnet er sich erst, wenn der
Magenwurm tot ist. In der Herzkammer schlägt das Herz: Es feuert Ringe aus Feuer, Säure und
Funken und gebiert Maden. Die Tiefen werden dunkler, gefährlicher und bringen bessere Beute.

**Das Sanktum:** Zwischen zwei Tiefen liegt eine sichere Kammer. Sie heilt dich und füllt
deine Augmentationen auf. Dort gibt es einen Laden mit vier Bausteinen und einer Augmentation
(bezahlt mit Blutperlen) und einen Altar mit drei Perks, von denen du einen wählst.

**Blutperlen** liegen in den Höhlen und fallen aus jedem getöteten Gegner. Du sammelst sie
durch Berührung ein.

**Gegner:**
- Fleischmaden kriechen, springen über Kanten und beißen.
- Gallenschwärmer fliegen und spucken Säureklumpen.
- Knochenspeier hängen unter Decken und schießen Nadelsalven.
- Sporenblasen treiben auf dich zu und platzen zu einer entzündlichen Sporenwolke.

Gegner erinnern sich drei Sekunden lang daran, wo sie dich zuletzt gesehen haben. Deine
eigenen Explosionen verletzen auch dich.

**Statuseffekte:** Wer Feuer berührt, fängt an zu brennen, nimmt Schaden und setzt die Umgebung
in Brand. Flüssigkeit löscht und macht nass, und nasse Körper fangen kein Feuer. Das gilt für
dich und für alle Gegner.

**Perks** (je Lauf jeder höchstens einmal):

| Perk | Wirkung |
|------|---------|
| Feuerfeste Haut | Feuer kann dir nichts mehr anhaben. |
| Säurehaut | Magensäure und Ätzdampf verletzen dich nicht. |
| Zähes Fleisch | +50 maximale Lebenspunkte. |
| Leichte Knochen | Du schwebst 50 % länger. |
| Panzerplatten | Explosionen verletzen dich kaum noch. |
| Blutdurst | Jeder getötete Gegner heilt dich um 6. |
| Schnelle Drüsen | Augmentationen zaubern und laden 25 % schneller. |
| Säureblut | Wenn du verletzt wirst, spritzt ätzendes Blut um dich. |
| Zweiter Puls | Einmal pro Lauf stehst du nach dem Tod wieder auf. |

## Augmentationen (Zauberstäbe)

Eine Augmentation ist ein Deck aus Bausteinen, das beim Zaubern der Reihe nach gezogen wird.

- **Drüse** (Form): das Projektil. Sie beendet einen Zug.
- **Mutation**: verändert die nächste Drüse. Der Doppelzauber zieht zwei Gruppen auf einmal.
- **Nerv** (Auslöser): Die nächste Gruppe wird zur Ladung der Drüse und bei Aufprall, nach
  Zeit, am Flugende oder bei Kontakt mit Flüssigkeit freigesetzt.
- **Sekret** (Nutzlast): Die Drüse hinterlässt am Ende dieses Material.

Jede Augmentation hat eigene Werte: Slots, Mana und Aufladung, Zauberverzögerung, Nachladezeit,
Streuung, Zauber pro Wurf und ob sie ihr Deck mischt. Bausteine, für die das Mana nicht reicht,
werden übersprungen. Gefundene Augmentationen werden prozedural erzeugt und sind in tieferen
Ebenen stärker. Du trägst bis zu vier Augmentationen und 16 lose Bausteine.

| Baustein | Typ | Mana | Wirkung |
|----------|-----|------|---------|
| Funke | Drüse | 5 | Schneller Funke, kleine Explosion. |
| Knochennadel | Drüse | 3 | Sehr schnell, gräbt sich nur wenig ein. |
| Gallenblase | Drüse | 25 | Prallt ab und platzt nach kurzer Zeit mit großer Wucht. |
| Klumpen | Drüse | 6 | Fliegt im Bogen und zerplatzt zu einer Lache. |
| Beschleunigung | Mutation | 3 | Nächste Drüse fliegt schneller. |
| Sprengkraft | Mutation | 12 | Größere Explosion. |
| Schwerkraftumkehr | Mutation | 4 | Nächste Drüse fällt nach oben. |
| Zielsuche | Mutation | 8 | Nächste Drüse lenkt zum Mauszeiger. |
| Doppelzauber | Mutation | 2 | Zieht zwei Gruppen auf einmal. |
| Aufprall-Nerv | Nerv | 6 | Setzt die nächste Gruppe beim Aufprall frei. |
| Zeit-Nerv | Nerv | 6 | Setzt die nächste Gruppe nach kurzer Zeit frei. |
| End-Nerv | Nerv | 6 | Setzt die nächste Gruppe am Ende des Flugs frei. |
| Nässe-Nerv | Nerv | 4 | Setzt die nächste Gruppe frei, wenn die Drüse Flüssigkeit trifft. |
| Blutsekret | Sekret | 6 | Hinterlässt Blut |
| Talgsekret | Sekret | 8 | Hinterlässt Talg |
| Säuresekret | Sekret | 14 | Hinterlässt Magensäure |
| Feuersekret | Sekret | 10 | Hinterlässt Feuer |
| Sporensekret | Sekret | 10 | Hinterlässt Sporen |

Vorlagen (in `src/wand.py`). Du startest mit den ersten beiden:

| Augmentation | Bausteine |
|--------------|-----------|
| Funkendrüse | Beschleunigung > Funke > Funke > Funke |
| Gallenwerfer | Talgsekret > Gallenblase > Feuersekret > Klumpen |
| Nervennadel | Aufprall-Nerv > Knochennadel > Doppelzauber > Säuresekret > Klumpen > Säuresekret > Klumpen |
| Sporenschleuder | Zielsuche > Zeit-Nerv > Funke > Doppelzauber > Sporensekret > Klumpen > Feuersekret > Funke |

## Materialien und Reaktionen

| Material | Verhalten |
|----------|-----------|
| Fleisch | Feste Wand; verkohlt im Feuer zu Schorf, blutet bei Explosionen |
| Knochen | Hart; zerfällt bei Explosionen teils zu Knochenstaub |
| Knochenstaub | Pulver, rutscht und häuft sich |
| Sehnen | Brücken; brennen langsam ab |
| Blut | Flüssigkeit; löscht Feuer (wird dabei zu Schorf), gerinnt an der Luft |
| Talg | Leicht, schwimmt auf Blut, brennt heftig |
| Magensäure | Ätzt Fleisch, Sehnen, Schorf, Wucherung und (langsam) Knochen; verbraucht sich dabei und gibt Ätzdampf ab; leuchtet |
| Wucherung | Wächst in Fleisch, frisst Blut, setzt Sporen frei; brennt |
| Sporen | Gas; infizieren Fleisch und Sehnen, entzünden sich explosionsartig |
| Feuer, Rauch, Ätzdampf | Steigen auf und vergehen; Feuer leuchtet |

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
- Alle Soundeffekte werden beim Start synthetisiert (`src/sounds.py`), es gibt keine
  Audiodateien. Ohne Audiogerät bleibt das Spiel stumm.
- Das Bewegungsgefühl und die Zauberstab-Regeln orientieren sich an Noita. Code, Grafiken und
  Texte von Noita werden nicht verwendet.

## Projektstruktur

```
py-noita-claude/
├── native/              # Rust-Kern: Simulation, Rendern, Licht (keine Abhängigkeiten)
├── src/
│   ├── main.py          # Fenster, Eingabe, Kamera, Zeichnen
│   ├── run.py           # Ein Lauf: Tiefen, Kampf, Beute, Ausgang, Sieg/Tod
│   ├── depths.py        # Die vier Tiefen und ihre Eigenschaften
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
│   ├── loot.py          # Prozedurale Augmentationen, Gegenstände in der Welt
│   ├── inventory.py     # Augmentationen und Beutel, Umbau-Logik
│   ├── editor.py        # Umbau-Bildschirm (pygame)
│   ├── editor_layout.py # Umbau-Layout (rein geometrisch, testbar)
│   ├── perks.py         # Perks
│   ├── menus.py         # Titel und Pause
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
