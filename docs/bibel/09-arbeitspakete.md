# 09 – Arbeitspakete, Merkliste, offene Fragen

## Reihenfolge

```text
Phase A  Fundament (Technik)        T1 … T6       → Spiel läuft mit 1 Test-Universum
Phase B  Grafik-Werkzeug + Stil     G0, G1         → Kontaktbogen-Werkzeug, Figuren abgenommen
Phase C  Universen nacheinander     U1 … U6        → je Universum: Daten + Grafik + Gegner + Texte
Phase D  Werkstatt, Wirtschaft      W1 … W4
Phase E  Bosse, Endkampf, Behörde   B1 … B4
Phase F  Umbenennung, Texte, UI     R1 … R4
Phase G  Abnahme                    Q1 … Q3
```

Erst wenn Phase A steht, lohnt es sich, Grafik in großer Menge zu erzeugen. Universen werden **einzeln vollständig** fertig gemacht (vertikaler Schnitt), nicht alle Grafiken zuerst.

## Regeln für Agenten

- Jedes Paket arbeitet auf einem eigenen Zweig bzw. eigenem Arbeitsbaum; nichts committen, das macht der Nutzer.
- CHANGELOG.md und die Version in pyproject.toml **nie** anfassen.
- Code: Englisch (Bezeichner, Kommentare); Spieltexte: Deutsch.
- Nach jedem Paket: `uv run ruff check .` sauber, alle Tests grün, neue Logik mit Tests (headless, ohne pygame).
- Grafik-Pakete liefern Quelle + erzeugte PNGs + Kontaktbogen; die Abnahme macht der Nutzer.
- Was nicht in der Bibel steht: nicht erfinden, sondern unten bei „Offene Fragen“ eintragen.

## Phase A – Fundament

| Paket | Inhalt | Abnahme |
| --- | --- | --- |
| **T1 Materialsätze** | Grundmaterialien (11) + Materialsatz je Universum (max. 10); Palette, Reaktionstabelle und Rust-Kern beim Betreten neu laden; Materialien in Kolben, Modulen, Speicherständen per Schlüssel statt ID | Test: zwei Universen mit verschiedenen Materialien hintereinander; Speichern/Laden über den Wechsel |
| **T2 Größere Welten** | Weltgröße je Universum (Form-Tabelle Kapitel 02); Kamera, Simulation, Wegsuche, Splitter-Aufräumen, Speichern (komprimiert) angepasst; Ladebildschirm | Messung: Generierung < 3 s, Bildzeit wie bisher (p99 < 16 ms), Speicherstand < 2 MB |
| **T3 Universum als Daten** | `src/universes/` mit Datenklasse (Felder Kapitel 03), Generator-Parameter je Teilgebiet, Lauf-Aufbau mit Rängen und Werkstatt-Zwischenstopps, Seed-Auswahl | Test: Lauf mit 6 Universen, jedes genau einmal, Ränge korrekt |
| **T4 Regelbibliothek** | Haken für die 6 MVP-Regeln (`living_walls`, `paperwork`, `bounce`, `tiny`, `beat`, `flooded`) inkl. Atem-Status und Takt | je Regel ein Test, der die Wirkung misst |
| **T5 Verhaltensbibliothek** | Haltungen + Fähigkeiten aus Kapitel 02 als kombinierbare Bausteine; Wegsuche für `hunt`/`retaliate`; Fraktionen; Ausholen als Pflichtzustand | je Fähigkeit ein Test (headless) |
| **T6 Sprite-Laufzeit** | Laden der PNG-Bögen + JSON; Zustandsautomat für Animationen; prozedurale Körper aus Teilen (Segmente, Beine, Tentakel); Leuchtpixel als Lichtquellen | Testbild mit 1 einfachem und 1 zusammengesetzten Sprite |

## Phase B – Grafik-Werkzeug und Stil

| Paket | Inhalt | Abnahme |
| --- | --- | --- |
| **G0 Werkzeug** | `tools/sprites.py`: rendert Quellen → PNG + JSON, prüft Größe und Palette, erzeugt Kontaktbogen (1×, 4×, dunkel/hell/gedimmt) und Silhouettenbogen | Lauf über eine Beispielquelle |
| **G1 Figuren** | Cloita, Klonita (alle Zustände Kapitel 04), Überlagerungen der Selbstexperimente | Kontaktbogen freigegeben |
| **G2 UI** | Logo, Icons (Kapitel 08), Sprechblasen-Rahmen | Kontaktbogen freigegeben |
| **G3 Waffenteile** | alle Teile (Kapitel 06), Zusammenbau-Vorschau mit 20 zufälligen Waffen | freigegeben |
| **G4 Modul-Icons** | 60 Basis-Icons, Familien-Generator angepasst | freigegeben |
| **G5 Gegenstände** | alle aus Kapitel 07 inkl. Proben | freigegeben |

## Phase C – Universen (je ein vollständiges Paket)

Jedes Paket **U1–U6** enthält:

1. Datendatei (alle Felder aus Kapitel 03),
2. Materialien mit Reaktionen und Tests,
3. Generator-Parameter für die Teilgebiete, Anker, Schatzkammer, Erinnerungssplitter, Lebenskapsel,
4. Einheimische und ggf. große Kreatur: Sprites (Kategorie `kreaturen`), Verhalten, Werte, Geräusche,
5. Ereignis,
6. Proben,
7. Notiz zur Musik-Stimmung (Musik kommt erst nach dem MVP),
8. Herausforderung (Kapitel 07),
9. Klonita-Sprüche und Mauszeiger-Texte,
10. Arena für Zwischengegner.

| Paket | Universum | Hängt ab von |
| --- | --- | --- |
| U1 | Fleischwelt (Umbau des Bestehenden; dient als Referenz) | T1–T6 |
| U2 | Aktenhalde | U1 |
| U3 | Glibbria | U1 |
| U4 | Krümelreich | U1 |
| U5 | Sporenklub | U1 |
| U6 | Versunkene Abtei | U1 |

Abnahme je Universum: ein Bot-Lauf durch das Universum auf allen drei Rängen ohne Absturz, Ausgang erreichbar (Wegsuche), Kontaktbogen der Kreaturen freigegeben, ein Spieltest des Nutzers.

## Phase D – Werkstatt und Wirtschaft

| Paket | Inhalt |
| --- | --- |
| W1 | Werkstatt-Karte, Stationen (Sprites + Funktion), Portal mit Vorschau, Heilung, Speicherpunkt |
| W2 | Gold statt Blutperlen überall, Preise (Kapitel 02), Händler (6 NPCs), Ausrauben + Folgen |
| W3 | Proben-Leiste, Baupläne im Archiv, Fabrikator mit 3 Bauten je Besuch, Bauplan-Splitter |
| W4 | Minispiele: Physik-o-Mat (4 Rätsel), Schießstand; Herausforderungen in Universen |

## Phase E – Bosse, Endkampf, Behörde

| Paket | Inhalt |
| --- | --- |
| B1 | Zwischengegner Rang 1 (Oberstempler, Mutter Glibber) mit Phasen |
| B2 | Rang 2 (DJ Myzel, Abt Kieme) |
| B3 | Rang 3 (Ameisenkönigin, Weltenherz) |
| B4 | 3 böse Ichs mit Heimatwelten, erbeutbare Waffe, Enden (Sieg, böses Ende bei der Kaiserin) |
| B5 | Behörde: Agenten (3 Typen), Fahndungsstufe, Durchsagen, Dienstausweise |
| B6 | Wahres Ende: Hauptquartier, Rat der bösen Ichs (3 Stufen), Verschmelzung zur Ober-Cloita, Abspann |

## Phase F – Umbenennung, Texte, Oberfläche

| Paket | Inhalt |
| --- | --- |
| R1 | Begriffe im Code und in allen Texten (Kapitel 00), Module umbenennen (Kapitel 06), Selbstexperimente (Kapitel 07) |
| R2 | HUD, Menüs, Rucksack, Archiv, Pausemenü, Tod-Bildschirm, Ladebildschirm (Kapitel 08) |
| R3 | Klonita (Folgen, Fähigkeiten, Sprechblasen, alle Sprüche) |
| R4 | README neu schreiben (Spiel, Steuerung, Universen); Protokoll-Ereignisse auf neue Begriffe |

## Phase G – Abnahme

| Paket | Inhalt |
| --- | --- |
| Q1 | Bot-Läufe: 20 Seeds × kompletter Lauf (Werkstatt → 6 Universen → böses Ich), keine Abstürze, alle Ausgänge erreichbar |
| Q2 | Leistung: Bildzeit je Universum (Logik + Licht), Weltgenerierung, Speicherstand-Größe |
| Q3 | Spieltest durch den Nutzer mit Protokoll; Balance-Runde |

## Merkliste: nicht vergessen

## **Bestehendes, das beim Umbau nicht verloren gehen darf**

- [ ] Steuerung: frei belegbar, Controller, Pausenübersicht nur für das aktive Gerät
- [ ] Speichern jederzeit (Welt komprimiert, einmal gültig, Rückfall aufs letzte Werkstatt-Speichern) – Speicherformat wird neu: alte Spielstände sauber ablehnen
- [ ] Archiv/Statistik: **neu beginnen**; alte `records.json`, `lauf.json` werden beim ersten Start von Cloita Interdimensional ignoriert (neuer Dateiname, z. B. `archiv.json`, `spielstand.json`); `steuerung.json` und `optionen.json` bleiben gültig
- [ ] Lauf-Protokoll: neue Ereignisse (Universum, Rang, Fahndung, Händler beraubt, Fabrikator, Minispiel, Klonita-Hinweis)
- [ ] Sandbox (nur aus dem Hauptmenü): Gottmodus, Modulbuch, Universum wählen statt Tiefe
- [ ] Härtestufen, Splitter-Aufräumen, Einmauer-Schutz, Treten, Geschosse durch Flüssigkeiten
- [ ] Mauszeiger-Infos für alle neuen Kreaturen, Materialien, Gegenstände, Stationen
- [ ] Rucksack: Stapel, Sortierung (Kriterien), Rechtsklick/Doppelklick, Ablegen; neue Proben-Leiste
- [ ] Kolben: mehrere, wechseln, gießen als Sprühstrahl, füllen mit S; Material per Schlüssel
- [ ] Unbekannte Module glitzern; Neu-Markierung im Tooltip
- [ ] Parallelwelten (Wackelportal), NG+ („Noch einmal, nur schlimmer“)
- [ ] Musik im MVP **abschalten** (vorhandene prozedurale Musik deaktivieren, Option „Musik“ ausblenden); Soundeffekte je Kreatur bleiben
- [ ] Optionen bleiben, ggf. neue (Klonita-Sprüche an/aus, Sprechblasen-Häufigkeit)
- [ ] Leistung: Simulation nur um die Kamera, Bildzeit-Budget 16,7 ms

## **Neu und leicht zu übersehen**

- [ ] Ladebildschirm (größere Welten)
- [ ] Atem-Leiste und Takt-Anzeige nur in passenden Universen
- [ ] Fahndungsstufe sinkt in der Werkstatt
- [ ] Händler-Preise steigen nach Raub für den ganzen Lauf
- [ ] Klonita blockiert keine eigenen Geschosse; wird nie dauerhaft „tot“
- [ ] Erbeutete Waffe des bösen Ichs
- [ ] Erinnerungssplitter: 6 pro Lauf → wahres Ende
- [ ] Wegsuche für Kreaturen (Gegenwehr außer Sicht)
- [ ] Gold als Gegenstand, Goldadern melden zerstörte Zellen
- [ ] Sandbox-Modulbuch, Gottmodus und Universum-Auswahl testen
- [ ] Taste „Klonita rufen / wegschicken“ (Standard K, Pad: linker Stick) in `keybinds.py`; Klonita erscheint von selbst an den Punkten aus Kapitel 02
- [ ] Wahl zwischen zwei Universen am Portalrahmen, inkl. Vorschau (Regel, Rang, Zwischengegner)
- [ ] Rang-Steigerung jeder Regel (Tabelle Kapitel 02)

## Nach dem MVP (Rückstand)

- Musik (pro Universum eine Stimmung, Werkstatt, Bosse) – zuerst prozedural, später ggf. echte Stücke
- Pool-Universen aus Kapitel 03 (18 Stück), jedes als eigenes U-Paket
- Zweite Regel je Universum
- `rule_reverse_gravity` (Kern: umkehrbare Fallrichtung)
- Universen überlagern (V5), Risse (V6)
- Weitere böse Ichs (Ziel: 8), weitere Zwischengegner (Ziel: 4 je Rang)
- Mehr Händler, mehr Minispiele, mehr Herausforderungen
- Voller Crafting-Baum (falls gewünscht)

## Entschiedene Fragen (2026-11-01)

1. Archiv und Statistik aus Biohorror-Zeiten werden **verworfen**.
2. Taste „Klonita rufen / wegschicken“: **ja**; Klonita erscheint außerdem an bestimmten Punkten von selbst.
3. Am Portal wählt man aus **zwei Vorschlägen**.
4. Wahres Ende: **mehrstufiger Kampf gegen die alternativen Ichs, die am Ende verschmelzen** (Rat der bösen Ichs, Kapitel 05).
5. Universumsregeln werden **mit dem Rang stärker**.
6. **Keine Musik** im MVP; kommt in einer späteren Runde.

## Offene Fragen

Keine. Neue Fragen hier eintragen.
