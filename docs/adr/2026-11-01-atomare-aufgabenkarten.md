# ADR 2026-11-01: Umsetzung über atomare Aufgabenkarten und feste Verträge

## Kontext

Die Pakete in `docs/bibel/09-arbeitspakete.md` (T5 … Q3) sind so groß, dass jedes Paket ein starkes Modell mit viel Kontext braucht (ganze Bibel, große Teile von `run.py`). Das kostet viele Token und führt bei parallel arbeitenden Agenten zu abweichenden Schnittstellen.

## Erwogene Optionen

1. Pakete so lassen, nur ein günstigeres Modell nehmen – scheitert an fehlendem Kontext und uneinheitlichen Lösungen.
2. Pakete in kleinere Schritte teilen, Schnittstellen aber offen lassen – Teilschritte passen später nicht zusammen.
3. **Verträge zuerst festlegen (`docs/plan/vertraege.md`), dann Pakete in Karten der Größe S/M schneiden, jede mit genauer Lese- und Dateiliste.**

## Entscheidung

Option 3. Die Verträge legen Klassen, Funktionssignaturen, Datenfelder und Ereignisnamen fest; Karten verweisen nur auf Vertragsabschnitte und Bibelabschnitte. Für die sechs Universen gibt es eine Vorlage (UX) plus je Universum eine Werte-Tabelle statt sechs ausgeschriebener Pläne.

## Folgen

- Positiv: Eine Karte braucht typischerweise < 15 KB Kontext; kleine Modelle können Daten-, Text- und S-Karten übernehmen; Karten ohne gemeinsame Dateien laufen parallel.
- Positiv: Das Spiel bleibt nach jeder Karte lauffähig (neue Felder mit Standardwerten, alter Codepfad bleibt, bis die Ersatzkarte fertig ist).
- Nachteil: Vertragsänderungen sind teuer (alle abhängigen Karten prüfen) und bleiben einem großen Modell vorbehalten.
- Nachteil: Etwas Übergangscode (alte Pfade, Aliase) lebt länger; W1.08 und R1.12 räumen ihn auf.
