# ADR 2026-11-03: Phase-3-Worldbuilding »Absurdität, Zynismus & Multiversums-Satire« (Phasen N–S)

## Status

Angenommen (im `/grill-me`- und `/ideate`-Prozess am 2026-11-03).

## Kontext

Der MVP (`docs/bibel/`, Phasen A–G) liefert das technische und spielerische Kernfundament. Die Phase-2-Erweiterung (`docs/erweiterung/`, Phasen H–M) vertieft die Noita-artige Zaubermathematik und Alchemie.

Um dem Spiel den unverkennbaren Charme, den tiefschwarzen Humor, die existenzielle Wucht und die satirische Absurdität von Werken wie *Rick and Morty* einzuhauchen, bedarf es einer gezielten dritten Ausbaustufe. Auf Basis von 18.000+ gecrawlten Wiki-Seiten wurden die Kernmotive (Zitadelle unendlicher Doppelgänger, Klon-Ausbeutung, interdimensionales Kabelfernsehen, existenzielle Klon-Krisen, parasitäre Pseudo-Erinnerungen und absurde Notfall-Gadgets wie der gefälschte Säurebottich oder die Gurken-Flucht) in eigenständige, rechtssichere Spielmechaniken und Lore für Cloita und Klonita transformiert.

## Erwogene Optionen

1. **Einarbeitung in die Phase-2-Dokumente (`docs/erweiterung/`):**
   - *Nachteil:* Vermischt physikalisch-systemische Zaubermathematik (Noita-Fokus) mit narrativem Worldbuilding und Satire-Features. Erzeugt unübersichtliche Riesen-Pläne.
2. **Kompaktes Skript-Buch nur für Dialoge:**
   - *Nachteil:* Lässt die spielbaren Gadgets (Säurebottich, Röhrenglotze, Zitadelle, Herr Fleißig) außen vor; verschenkt Gameplay-Potenzial.
3. **Isolierte Phase 3 in `docs/phase3_absurditaet/` mit Aufgabenplan `tasks/plan_phase3.md` und `tasks/todo_phase3.md` (Phasen N bis S):**
   - *Vorteil:* Vollständige Kapselung aller drei Schichten (MVP A–G $\to$ System-Erweiterung H–M $\to$ Worldbuilding & Satire N–S). Jede Schicht kann unabhängig von dedizierten Agenten-Runs implementiert werden.

## Entscheidung

Wir wählen **Option 3**.

1. Alle Konzepte werden in `docs/phase3_absurditaet/` in 6 Kapiteln (`00-uebersicht.md` bis `05-parasiten-und-zynismus-dialoge.md`) verankert.
2. Der technische Umsetzungsplan wird in `tasks/plan_phase3.md` und `tasks/todo_phase3.md` als Phasen **N bis S** strukturiert.
3. Sämtliche Figuren und Begriffe bleiben eigenständig, unverwechselbar und urheberrechtlich unbedenklich (z.B. *Revoluzzer-Klonita* statt Evil Morty, *Herr Fleißig* statt Meeseeks, *Röhrenglotze* statt Interdimensional Cable).

## Konsequenzen

- **Positiv:** Klare Dreistufen-Architektur ohne gegenseitige Abhängigkeiten oder Blockaden.
- **Positiv:** Massiver Gewinn an Humor, Spieltiefe, Immersion und Wiederspielwert.
- **Positiv:** Einfache Zuordnung für nachfolgende Modell-Läufe durch atomare S-Karten.
