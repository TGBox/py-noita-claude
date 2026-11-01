# Umsetzungsplan in Aufgabenkarten

Stand: 2026-11-01. Ersetzt die groben Pakete aus `docs/bibel/09-arbeitspakete.md` durch **kleine, isoliert umsetzbare Aufgabenkarten**. Die Bibel bleibt die inhaltliche Quelle; dieser Plan sagt nur, *wer was in welcher Reihenfolge baut*.

Ziel: Jede Karte kann von einem günstigen Modell in einer frischen Sitzung umgesetzt werden, ohne das ganze Projekt zu lesen.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `README.md` | dieses Blatt: Kartenformat, Auftragsvorlage, Reihenfolge |
| `vertraege.md` | verbindliche Schnittstellen (Klassen, Funktionen, Datenfelder), auf die sich alle Karten beziehen |
| `phase-a-fundament.md` | T5 Verhaltensbibliothek, T6 Sprite-Laufzeit |
| `phase-b-grafik.md` | G0 Sprite-Werkzeug, G1–G5 Grafik |
| `phase-c-universen.md` | U0 gemeinsamer Unterbau, U1 Fleischwelt (Referenz), Vorlage UX, U2–U6 |
| `phase-d-werkstatt.md` | W1–W4 Werkstatt, Gold, Händler, Fabrikator, Minispiele |
| `phase-e-bosse.md` | B1–B6 Zwischengegner, böse Ichs, Behörde, wahres Ende |
| `phase-f-umbenennung.md` | R1–R4 Begriffe, Oberfläche, Klonita, README |
| `phase-g-abnahme.md` | Q1–Q3 Bot-Läufe, Leistung, Spieltest |

## Kartenformat

```text
### <ID> <Titel>

- Art: Code | Daten | Text | Grafik      Größe: S | M      Hängt ab von: <IDs>
- Lesen: <genau diese Abschnitte/Dateien>
- Dateien: <genau diese Dateien ändern/anlegen>
- Tun: nummerierte Schritte
- Test: welcher Test, was er prüft
- Fertig, wenn: messbare Bedingung
- Nicht: was ausdrücklich nicht dazugehört
```

**Größen:**

- **S** – höchstens ~80 geänderte Zeilen, 1–2 Dateien plus Test. Geeignet für das kleinste Modell.
- **M** – höchstens ~200 geänderte Zeilen, bis 4 Dateien plus Test. Geeignet für ein mittleres Modell.
- Größer gibt es nicht. Wird eine Karte beim Umsetzen größer, wird sie abgebrochen und geteilt (Notiz unter „Offene Fragen“ in `docs/bibel/09-arbeitspakete.md`).

**Art → Modell (Empfehlung):**

| Art | Modell | Warum |
| --- | --- | --- |
| Daten, Text | klein | Werte aus der Bibel übertragen, Schema steht im Vertrag |
| Code S | klein | eine Funktion, klarer Test |
| Code M | mittel | mehrere Stellen, Einbau in `run.py` |
| Grafik | mittel | Pixel-Quellen brauchen räumliches Denken; Abnahme über Kontaktbogen durch den Nutzer |
| Verträge ändern, Karten neu schneiden, Review | groß | einmalig, spart danach viele Folgekosten |

## Auftragsvorlage (in die neue Sitzung kopieren)

```text
Projekt py-noita-claude. Setze genau die Aufgabenkarte <ID> aus docs/plan/<datei>.md um.

Regeln:
- Lies nur: AGENTS.md, die Karte, die in "Lesen" genannten Stellen und docs/plan/vertraege.md
  (nur die Abschnitte, auf die die Karte verweist). Lies README.md und run.py nicht ganz;
  suche darin mit grep nach den genannten Namen.
- Ändere nur die Dateien aus "Dateien". Halte die Schnittstellen aus vertraege.md exakt ein.
- Code und Kommentare englisch, Spieltexte deutsch. CHANGELOG.md und die Version in
  pyproject.toml nicht anfassen. Nicht committen.
- Danach: `uv run ruff check .` und `uv run pytest -q` müssen sauber sein.
- Fehlt dir etwas, das weder in der Karte noch in der Bibel steht: nicht erfinden,
  sondern unter "Offene Fragen" in docs/bibel/09-arbeitspakete.md eintragen und aufhören.
- Zum Schluss: Karte in der Plandatei abhaken ("- Status: erledigt (Datum)") und
  in 3 Sätzen berichten, was geändert wurde.
```

## Reihenfolge (kritischer Pfad)

```text
T5.01–T5.04 ─┬─ T5.05–T5.20 (Fähigkeiten, parallel möglich)
             └─ T5.21 Einbau in Run
G0.01–G0.05 ── T6.01–T6.08 ── G1 (Figuren)
U0.01–U0.12 ── U1 (Fleischwelt, Referenz) ── U2 … U6 (parallel möglich, je Universum seriell)
B5.01–B5.04 (Behörde-Kern) wird vor U2 gebraucht (Stempler, Ereignis „Prüfung“)
W1 ── W2 ── W3 ── W4
B1–B4 nach dem jeweiligen Heimat-Universum; B6 zuletzt
R1–R4 nach W2; Q1–Q3 zum Schluss
```

Parallel arbeiten: Karten ohne gemeinsame Datei und ohne gegenseitige Abhängigkeit dürfen gleichzeitig in getrennten Arbeitsbäumen laufen. Zwei Karten, die beide `src/run.py` ändern, nie gleichzeitig.

## Status-Pflege

Unter jeder Karte steht nach dem Umsetzen eine Zeile `- Status: erledigt (JJJJ-MM-TT)`. Fehlt sie, ist die Karte offen. Ein günstiges Modell sucht die nächste offene Karte mit `grep -L`/`grep -n "Status"` statt die Dateien ganz zu lesen.
