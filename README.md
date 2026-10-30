# Cloita

Ein düsteres Falling-Sand-Roguelite in Python, inspiriert von Noita: Du steigst in einen
lebenden Organismus hinab. Jeder Pixel ist simuliert und kann mit allem reagieren:
Blut gerinnt, Säure ätzt, Wucherungen kriechen durch Fleisch, Sporen entzünden sich.

Ziel (in Arbeit): sich durch mehrere Bosskämpfe bis zum Herzen durchschlagen und es zerstören.

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
| **W / Leertaste** | Springen; in der Luft gedrückt halten zum Schweben (begrenzte Energie) |
| **Linke Maus** | Zauberstab: Funkenblitz, der beim Aufprall explodiert |
| **Rechte Maus** | Sandbox: Material malen |
| **Mittlere Maus** | Sandbox: Radieren |
| **1-9, 0** | Material: Knochenstaub, Blut, Talg, Magensäure, Fleisch, Knochen, Sehnen, Feuer, Wucherung, Sporen |
| **Mausrad** | Pinselgröße |
| **R** | Wiederbeleben |
| **N** | Neue zufällige Welt |
| **F11** | Vollbild umschalten |
| **ESC** | Beenden |

## Materialien und Reaktionen

| Material | Verhalten |
|----------|-----------|
| Fleisch | Feste Wand; verkohlt im Feuer zu Schorf, blutet bei Explosionen |
| Knochen | Hart; zerfällt bei Explosionen teils zu Knochenstaub |
| Knochenstaub | Pulver, rutscht und häuft sich |
| Sehnen | Brücken; brennen langsam ab |
| Blut | Flüssigkeit; löscht Feuer (wird dabei zu Schorf), gerinnt an der Luft |
| Talg | Leicht, schwimmt auf Blut, brennt heftig |
| Magensäure | Ätzt Fleisch, Sehnen, Schorf, Wucherung und (langsam) Knochen; verbraucht sich dabei und gibt Ätzdampf ab |
| Wucherung | Wächst in Fleisch, frisst Blut, setzt Sporen frei; brennt |
| Sporen | Gas; infizieren Fleisch und Sehnen, entzünden sich explosionsartig |
| Feuer, Rauch, Ätzdampf | Steigen auf und vergehen |

Reaktionen stehen als Tabelle in `src/reactions.py`. Eine neue Wechselwirkung ist eine Zeile.

## Technik

- Sichtbarer Ausschnitt: 640x360 Weltpixel, verzerrungsfrei auf Fenster oder Vollbild skaliert.
- Welt: 1280x720 Zellen, aufgeteilt in 16x16-Chunks. Ruhende Chunks schlafen, und
  simuliert wird nur ein Bereich um die Kamera.
- Die Zellsimulation läuft in einem kleinen Rust-Kern ohne externe Pakete (`native/`), der per
  `ctypes` direkt auf den Python-Puffern arbeitet. Alle Material- und Reaktionsdaten
  kommen aus Python.
- Feste 60 Simulationsschritte pro Sekunde, unabhängig von der Framerate.

## Projektstruktur

```
py-noita-claude/
├── assets/
├── native/              # Rust-Simulationskern (cdylib, keine Abhängigkeiten)
│   └── src/lib.rs
├── src/
│   ├── main.py          # Game-Loop & Einstiegspunkt
│   ├── settings.py      # Auflösung, FPS, Konstanten
│   ├── materials.py     # Materialien und ihre Eigenschaften
│   ├── reactions.py     # Reaktionstabelle
│   ├── native.py        # Lädt und baut den Rust-Kern
│   ├── world.py         # Weltpuffer, Malen, Explosionen, Kollision
│   ├── worldgen.py      # Prozedurale Organismus-Level
│   ├── player.py        # Spielfigur, Kollision, Schweben
│   ├── wand.py          # Zauberstab und Funkenblitz
│   ├── texture.py       # Marmorierte Materialtextur
│   ├── rendering.py     # Welt -> pygame-Oberfläche, Sprites
│   ├── viewport.py      # Virtuelle Auflösung / Letterboxing
│   ├── tools.py         # Format, Lint, Rust-Build
│   └── build.py         # PyInstaller-Build
└── tests/
```
