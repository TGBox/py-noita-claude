# py-noita-claude

A python game adaptation of Noita, written with claude.

## Framework
Entwickelt mit **Pygame-ce (Community Edition)**.

## Steuerung & Features
| Taste | Aktion |
|-------|--------|
| **A / D** (oder Pfeile) | Laufen |
| **W / Leertaste** | Springen; in der Luft gedrückt halten zum Schweben (begrenzte Energie) |
| **Linke Maus** | Zauberstab: Funkenblitz, der beim Aufprall explodiert |
| **Rechte Maus** | Sandbox-Pinsel (Material malen) |
| **1-8** | Material: Sand, Wasser, Öl, Stein, Holz, Lava, Feuer, Radierer |
| **Mausrad** | Pinselgröße |
| **R** | Wiederbeleben |
| **N** | Neue zufällige Welt |
| **F11** | Vollbild umschalten |
| **ESC** | Beenden |

Die Welt ist ein Zellraster (640x360), in dem jede Zelle ein Material ist. Sand fällt,
Wasser fließt, Öl schwimmt auf Wasser, Holz und Öl brennen, Wasser löscht Feuer und
Lava + Wasser ergibt Stein. Die Simulation läuft mit festen 60 Ticks pro Sekunde,
unabhängig von der Framerate; ruhende Bereiche (Chunks) werden übersprungen.

## Schnellstart

Voraussetzung: [uv](https://docs.astral.sh/uv/)

```bash
# Abhängigkeiten synchronisieren
uv sync

# Spiel starten
uv run main

# Tests ausführen
uv run test

# Code formatieren & prüfen
uv run format
uv run lint

# Standalone-Executable bauen (PyInstaller)
uv run build
```

## Projektstruktur
```
py-noita-claude/
├── assets/
│   ├── audio/        # Sound-Effekte und Musik
│   └── sprites/      # Texturen, Sprites und Grafiken
├── src/
│   ├── __init__.py
│   ├── main.py       # Game-Loop & Einstiegspunkt
│   ├── settings.py   # Auflösung, FPS, Konstanten
│   ├── materials.py  # Materialien und Eigenschaftstabellen
│   ├── world.py      # Falling-Sand-Simulation (ohne pygame, testbar)
│   ├── worldgen.py   # Prozedurale Höhlen
│   ├── player.py     # Spielfigur, Kollision, Schweben
│   ├── wand.py       # Zauberstab und Funkenblitz
│   ├── viewport.py   # Virtuelle Auflösung / Letterboxing
│   ├── rendering.py  # Raster -> pygame-Oberfläche
│   ├── tools.py      # Format & Lint Helfer
│   └── build.py      # PyInstaller Build-Skript
└── tests/
    ├── test_game.py  # Einstellungen
    ├── test_world.py # Simulation
    ├── test_player.py
    └── test_misc.py  # Viewport, Zauberstab, Weltgenerierung
```