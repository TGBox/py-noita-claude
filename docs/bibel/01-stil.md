# 01 – Grafikstil

## Grundsätze

1. **Lesbarkeit vor Detail.** Das Spiel zeigt 640×360 Weltpixel; ein Weltpixel ist eine Materialzelle. Jedes Motiv muss in **1-facher Größe** auf dunklem *und* hellem Grund erkennbar sein.
2. **Silhouetten-Test.** Jede Kreatur ist als reine schwarze Silhouette von allen anderen Kreaturen ihres Universums und von der Spielfigur unterscheidbar.
3. **Ankündigen statt überraschen.** Jeder Angriff hat eine sichtbare Ausholbewegung (mindestens 0,4 s), die sich in Pose *und* Farbe zeigt.
4. **Komik in der Form.** Übergroße Augen, falsche Proportionen, Alltagsgegenstände am falschen Ort. Keine Gags, die nur mit Text funktionieren.
5. **Eine Physik, viele Welten.** Universen unterscheiden sich über Teilpaletten und Formen, nicht über einen anderen Zeichenstil.

## Technik der Sprites

- Sprites sind **Pixelraster im Code** (Python-Dateien mit Zeichenreihen und einer Palette), aus denen ein Werkzeug PNG-Bögen und Metadaten rendert. Der Code ist die Quelle; PNGs sind erzeugt und werden nicht von Hand bearbeitet.
- Große Figuren (Zwischengegner, große Kreaturen, böse Ichs) bestehen aus **Teilen** (Rumpf, Kopf, Glieder, Panzer, Augen), die das Spiel zur Laufzeit zusammensetzt und bewegt (prozedurale Körper). Jedes Teil ist ein eigenes kleines Sprite.

## Größen

| Klasse | Sprite-Größe (B×H) | Trefferbox | Hinweis |
| --- | --- | --- | --- |
| Cloita | 14×24 | 8×18 (wie bisher) | Waffe wird separat am Schulterpunkt gezeichnet |
| Klonita | 14×24 | 8×18 | gleiche Proportionen, weichere Formen |
| Normale Kreatur | 10–24 × 8–24 | Sprite minus 1–2 px Rand | etwa spielergroß, kleine Schwärmer ab 6 px |
| Große Kreatur | 30–60 × 24–48 | eigene Box je Teil | aus Teilen |
| Zwischengegner | 48–110 × 40–90 | je Teil | aus Teilen, mit Phasen-Varianten |
| Böses Ich | 16×26 Kern + Effektteile | 10×20 | wie Cloita gebaut, aber andere Silhouette |
| NPC (Händler, Agent) | 12–18 × 18–26 | wie normale Kreatur | |
| Gegenstand in der Welt | 5–12 × 5–12 | Aufhebe-Radius 26 px | schwebt bzw. liegt |
| Modul-Icon | 16×16 | – | Rahmenfarbe = Kategorie |
| Waffe in der Welt | 12–20 × 5–8 | – | aus Waffenteilen zusammengesetzt |
| UI-Icon | 8×8 bis 16×16 | – | wird skaliert |
| Werkstatt-Station | 24–64 × 24–48 | – | statisch mit 2–4 Frames Leerlauf |

## Kontur und Licht

- **Außenkontur:** 1 px in `ink` (#1C1420) um die ganze Silhouette von Figuren, Kreaturen und Gegenständen. Ausnahme: Leucht- und Geisterwesen (Kontur in ihrer dunkelsten Eigenfarbe).
- **Innenlinien:** nie schwarz, immer die dunkelste Stufe der jeweiligen Farbrampe.
- **Licht von links oben.** Jede Farbe hat eine Rampe aus *Licht, Grund, Schatten* (+ optional ein Glanzpixel).
- **Leuchtende Teile** (Augen, Flux, Neon) werden in den Metadaten als `glow` markiert; das Spiel macht sie zu Lichtquellen.
- Im Spiel werden Kreaturen zusätzlich mit einem schwachen hellen Rand gezeichnet (vorhandene Technik), damit sie in der Dunkelheit sichtbar bleiben. Die Kontur im Sprite ersetzt diesen Rand nicht.

## Hauptpalette

Alle Sprites verwenden nur Farben aus der Hauptpalette plus der Teilpalette ihres Universums. Namen sind die Schlüssel im Code.

| Gruppe | Schlüssel | Hex |
| --- | --- | --- |
| Tinte | `ink` | #1C1420 |
| Neutral | `n1` `n2` `n3` `n4` `n5` | #2E2836 #4A4452 #77707E #A9A3AE #E6E2E8 |
| Haut | `skin_l` `skin` `skin_d` | #F2CCA8 #E0A982 #B67A5C |
| Cloitas Haar | `hair_l` `hair` `hair_d` | #FF9A4A #EC6E34 #B34424 |
| Laborkittel | `coat_l` `coat` `coat_d` | #F6F7F2 #D6DCD8 #9AA6A8 |
| Kleidung | `cloth` `cloth_d` | #8C46AA #5E2C78 |
| Flux (Energie) | `flux_l` `flux` `flux_d` | #B4FFF0 #3CE6C8 #1C9488 |
| Gold | `gold_l` `gold` `gold_d` | #FFF09A #F2C230 #A87A14 |
| Gefahr | `danger_l` `danger` `danger_d` | #FF8A7A #E83A3A #9A1E28 |
| Behörde | `agent_l` `agent` `agent_d` | #9AA4C8 #5A6490 #333A5C |
| Metall | `metal_l` `metal` `metal_d` | #C8CED6 #8A94A2 #545C6A |
| Klonita | `clone_l` `clone` `clone_d` | #FFE0EC #F6B4CC #D07EA0 |
| Leben (grün) | `life_l` `life` `life_d` | #B8F59A #6CD25A #3A8A3C |

Teilpaletten der Universen stehen in Kapitel 03 (je 8–12 Farben).

## Animation

- Standard 8 Bilder/s, schnelle Bewegungen 12 Bilder/s.
- Grundblick nach **rechts**; das Spiel spiegelt.
- Zustände und Mindest-Framezahlen:

| Zustand | Schlüssel | Frames | Pflicht für |
| --- | --- | --- | --- |
| Ruhe | `idle` | 2–4 | alle |
| Bewegung | `move` | 4–6 | alle beweglichen |
| Ausholen | `windup` | 2–3 | alle mit Angriff |
| Angriff | `attack` | 2–3 | alle mit Angriff |
| Treffer | `hurt` | 1 | alle |
| Tod | `death` | 3–5 | alle (danach Brocken/Material über die Physik) |
| Sonderzustand | frei benannt | 2–6 | laut Kapitel 05 (z. B. `flee`, `dig`, `steal`, `split`) |

- **Ausholen:** Pose ändern *und* ein Akzent in `danger` oder in der Eigenfarbe des Angriffs.
- **Treffer:** die ganze Silhouette einen Frame in `n5` (weiß) – das Spiel kann das auch selbst; der Frame ist optional.

## Dateiformat

```text
assets/sprites/<kategorie>/<key>.py        # Quelle: Palette-Zuordnung + Frames
assets/sprites_png/<kategorie>/<key>.png   # erzeugt: Bogen, Frames nebeneinander
assets/sprites_png/<kategorie>/<key>.json  # erzeugt: Metadaten
```

Kategorien: `figuren`, `kreaturen`, `bosse`, `boese_ichs`, `npc`, `gegenstaende`, `module`, `waffenteile`, `werkstatt`, `ui`, `effekte`.

Quelldatei (Beispiel):

```python
"""Aktenfresser – Bürokratenwelt. Gräbt sich durch Papier."""

PALETTE = {"o": "ink", "a": "paper_l", "A": "paper", "z": "n1", "r": "danger"}
SIZE = (20, 17)
ANCHOR = (10, 16)          # Fußpunkt (Bodenkontakt) im Sprite
HITBOX = (2, 1, 16, 16)    # x, y, b, h relativ zum Sprite
GLOW = ["r"]               # Zeichen, die leuchten
FPS = {"idle": 4, "move": 8, "windup": 8, "attack": 10, "hurt": 1, "death": 8}
FRAMES = {
    "idle": [[...], [...]],   # je Frame eine Liste gleich langer Zeichenreihen; "." = durchsichtig
    "move": [...],
    ...
}
```

Metadaten (erzeugt):

```json
{"key": "aktenfresser", "frame_w": 20, "frame_h": 17, "anchor": [10, 16],
 "hitbox": [2, 1, 16, 16], "states": {"idle": [0, 2, 4], "move": [2, 4, 8]},
 "glow": [[x, y], ...]}
```

`states` gibt je Zustand *(erstes Frame, Anzahl, Bilder pro Sekunde)* an.

## Abnahme

Für jede Kategorie erzeugt das Werkzeug einen **Kontaktbogen**:

- alle Motive in 1-facher und 4-facher Größe,
- auf dunklem Grund (#1C1420), hellem Grund (#E6E2E8) und einer gedimmten Spielszene (Licht 30 %),
- alle Animationszustände als Reihe,
- darunter Name und Größe.

Ein Motiv ist **abgenommen**, wenn:

1. es die Größenregel einhält und nur erlaubte Farben verwendet (prüft das Werkzeug automatisch),
2. es den Silhouetten-Test besteht (Werkzeug erzeugt Silhouettenbogen),
3. Ausholen und Angriff auf dem Kontaktbogen klar unterscheidbar sind,
4. die Beschreibung aus Kapitel 03–07 erkennbar umgesetzt ist,
5. der Nutzer den Bogen freigegeben hat.
