# ADR 2026-11-02: Bibel-Erweiterung »Cloita Interdimensional: Entfesselte Wissenschaft« (Phasen H–M)

## Status

Angenommen (im `/grill-me`- und `/idea-refine`-Prozess am 2026-11-02).

## Kontext

Die ursprüngliche Bibel (`docs/bibel/`) und der bestehende Umsetzungsplan (`tasks/plan.md`, `tasks/todo.md`, `docs/plan/`) definieren das solide Fundament des MVP (Phasen A–G, 6 Universen, 60 Module, 12 Werkstatt-Stationen, Basis-Verhalten, Behörden-Eskalation).

Zur Bereicherung des Spiels um tiefgründige Noita-artige Mechaniken (komplexe Zaubermathematik, Deck-Wrapping, Kopier-Protokolle, globale Alchemie-Verschiebungen / Fungal Shifts, Kessel-Brauen, Parallelwelten, Behörden-Großalarm bei Werkstatt-Vandalismus sowie 6 neue absurde Universen) soll eine umfassende Design-Bibel für spätere Implementierungs-Runs geschaffen werden.

Dabei gilt die strikte Vorgabe: **Vollständige Kapselung**. Der laufende MVP-Plan darf durch diese Konzeptionierung in keiner Weise gestört, modifiziert oder blockiert werden.

## Erwogene Optionen

1. **Direkte Erweiterung der bestehenden Bibel-Dateien:**
   - *Vorteil:* Alles an einem Ort.
   - *Nachteil:* Erzeugt massive Merge-Konflikte und Verwirrung für Agenten, die parallel am MVP (Phasen A–G) arbeiten. Testverträge und Karten-Zuweisungen würden verschwimmen.

2. **Kompakter One-Pager / Notizensammlung:**
   - *Vorteil:* Wenig Schreibaufwand.
   - *Nachteil:* Zu vage für nachfolgende Implementierungs-Agenten; Noita-artige Zaubermathematik und Alchemieregeln erfordern exakte mathematische und algorithmische Spezifikationen.

3. **Vollständig isoliertes Erweiterungsverzeichnis (`docs/erweiterung/`) mit sequenziellem Anschlussplan (`tasks/plan_erweiterung.md` & `tasks/todo_erweiterung.md`, Phasen H–M):**
   - *Vorteil:* 100 % konfliktfrei zum MVP. Der MVP-Lauf (A–G) schließt sauber ab. Nach Abnahme des MVP setzt der Erweiterungsplan nahtlos an Phase G an, ohne Altes umzubauen, sondern durch saubere Komposition und modulare Plugins zu erweitern.
   - *Nachteil:* Getrennte Dokumentenverwaltung (wird durch klare Querverweise und standardisierte Kapitelstruktur gelöst).

## Entscheidung

Wir wählen **Option 3**.

1. Sämtliche Erweiterungskonzepte werden in `docs/erweiterung/` in 6 dedizierten Kapiteln (`00-uebersicht.md` bis `05-behoerdenalarm-und-endgame.md`) abgelegt.
2. Der Umsetzungsplan wird in `tasks/plan_erweiterung.md` und `tasks/todo_erweiterung.md` als Phasen **H bis M** modelliert.
3. Die bestehende Codebasis und die aktuellen Pläne (`tasks/plan.md`, `tasks/todo.md`, `docs/bibel/`, `docs/plan/`) bleiben unangetastet.

## Konsequenzen

- **Positiv:** Maximale Planungs- und Ausführungssicherheit für Entwickler und Agenten.
- **Positiv:** Vollständige Schärfung aller witzigen Noita-Mechaniken (Wand-Wrapping, Alpha/Omega, Fungal Shift, Kessel, Stevari-Parallele, Parallelwelten, 6 neue Welten) vor Code-Beginn.
- **Positiv:** Ermöglicht TDD-Entwicklung der Erweiterung mit eigenen Spec-Tests (`tests/spec_erweiterung/`), sobald Phase G des MVP abgenommen ist.
