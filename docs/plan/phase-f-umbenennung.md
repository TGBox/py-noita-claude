# Phase F – Umbenennung, Texte, Oberfläche

Lesen für alle Karten: Bibel 00 „Begriffe: alt → neu“ und den genannten Abschnitt. Umbenennungen sind **reine Umbenennungen**: kein Verhalten ändern, alte Spielstand-Schlüssel beim Laden weiter annehmen.

## R1 Begriffe

| Karte | Inhalt | Art · Größe |
| --- | --- | --- |
| R1.01 | Anzeigetexte der Kategorien (Geschoss, Aufsatz, Zünder, Füllung) – grep `name_de` in `src/spells.py` für `Category` | Text · S |
| R1.02 | Mana → Flux in allen Spieltexten (grep `Mana`) | Text · S |
| R1.03 | Blutperlen → Gold in allen Spieltexten | Text · S |
| R1.04 | Tiefe/Stufe → Universum, Sanktum → Werkstatt, Wächter → Zwischengegner, Herz → Böses Ich | Text · S |
| R1.05–R1.10 | Module umbenennen nach Bibel 06, je Tabelle eine Karte: Geschosse 1–12, 13–24, Aufsätze 1–11, 12–22, Zünder + Füllungen; neue Schlüssel, alte als Alias (`MODULE_ALIASES`) für Speicherstände | Daten · S |
| R1.11 | Perks → Selbstexperimente (Bibel 07 „Selbstexperimente“): Daten in `src/perks.py`, Anzeigename | Daten · M |
| R1.12 | Code-Bezeichner `sanctum` → `workshop`, `pearls` → `gold` (Felder, Funktionen), alte Speicherfelder beim Laden lesen | Code · M |
| R1.13 | Neue Dateinamen `archiv.json`, `spielstand.json`; alte `records.json`, `lauf.json` ignorieren (Merkliste 09) | Code · S |

## R2 Oberfläche

| Karte | Inhalt | Lesen (Bibel 08) |
| --- | --- | --- |
| R2.01 | HUD: Flux-Leiste türkis, Gold, Rang, Regel; Icons aus G2 | „Oberfläche umbenennen“ |
| R2.02 | Hauptmenü + Logo | „Logo und Titel“ |
| R2.03 | Pausemenü und Steuerungs-Übersicht | „Oberfläche umbenennen“ |
| R2.04 | Rucksack: Leisten Waffen 4, Module 48, Kolben 4, Proben 12 | Bibel 07 „Rucksack-Änderungen“ |
| R2.05 | Archiv-Bildschirm | „Oberfläche umbenennen“ |
| R2.06 | Tod-Bildschirm mit Klonita-Spruch | „Textmengen“ |
| R2.07 | Ladebildschirm mit `pitch_de` | „Ladebildschirm“ |
| R2.08 | Musik abschalten, Option ausblenden | Merkliste 09 |

Alle R2-Karten: Art Code, Größe S–M, hängen von R1.01–R1.04 ab; Test = Menü-/Layout-Logik ohne Zeichnen (wie `tests/test_ui_logic.py`).

## R3 Klonita

| Karte | Inhalt | Art · Größe |
| --- | --- | --- |
| R3.01 | Kreatur `klonita`: folgt in 20–40 px, läuft/springt/klettert, teleportiert bei > 300 px; Geschosse von Cloita gehen durch | Code · M |
| R3.02 | Unverwundbar: Schaden → `knocked` 5 s, `getup`, Spruch | Code · S |
| R3.03 | Taste K rufen/wegschicken (`src/keybinds.py`, Pad linker Stick); weggeschickt → sitzt auf `ws_couch` | Code · S |
| R3.04 | Von selbst erscheinen (5 Anlässe aus Bibel 02) | Code · M |
| R3.05 | Zeigen (Geheimnis, Lebenskapsel, Splitter; 60 s Abklingzeit) | Code · S |
| R3.06 | Tragen (1 Gegenstand je 30 s) | Code · S |
| R3.07 | Umarmen (passive/neutrale bleiben friedlich) | Code · S |
| R3.08 | Auffangen (> 120 px Fall, 25 %) | Code · S |
| R3.09 | Nachteile: Trinkgeld, Füttern, Warnung (je höchstens 1× pro Universum) | Code · M |
| R3.10 | Sprechblasen (Bibel 08: 60 Zeichen, 3 s, alle 8 s) | Code · S |
| R3.11 | Alle allgemeinen Sprüche (Bibel 08 „Textmengen“) als Daten `src/klonita_lines.py` | Text · S |
| R3.12 | Optionen: Sprüche an/aus, Häufigkeit | Code · S |

## R4 Abschluss Texte

| Karte | Inhalt | Art · Größe |
| --- | --- | --- |
| R4.01 | README neu: Spiel, Steuerung, Universen (aus Bibel, kurz) | Text · M |
| R4.02 | Lauf-Protokoll auf neue Ereignisnamen (V12) | Code · S |
| R4.03 | Mauszeiger-Texte für Stationen und Gegenstände | Text · S |
