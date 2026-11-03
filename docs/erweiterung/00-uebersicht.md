# Cloita Interdimensional – Erweiterungs-Bibel: Entfesselte Wissenschaft

Stand: 2026-11-03 (Bereinigt gemäß Statement of Intent). Gilt für den **zweiten Ausbau-Lauf (Post-MVP / Phasen H–M)**.
Dieses Dokumentenpaket ist vollständig **vom MVP-Plan abgekapselt**. Es baut auf dem abgenommenen Fundament der Phasen A–G auf und fügt Noita-artige Systemmechaniken, Alchemie, Endgame-Geheimnisse und sechs neue Universen hinzu – unter strikter Einhaltung aller Bibel-Parameter und Engine-Grenzen.

---

## 1. Übersicht der Kapitel

| Datei | Inhalt | Fokus |
| --- | --- | --- |
| `00-uebersicht.md` | Leitidee, Entkopplungsprinzip & System-Regeln | Architektur & Überblick |
| `01-modul-mathematik.md` | Deck-Evaluation in `wand.py`: Modul-Rückgriff, Kopier-Protokolle, Klon-Splitter, Orbit-Aufsätze | Waffen- & Modulsystem |
| `02-alchemie-und-kessel.md` | Geheim-Alchemie (Schutztonikum & Golderz-Schmelze), Destillierkessel, 300-Zellen-Kolben, Realitäts-Flimmern | Physik- & Alchemiesystem |
| `03-universen-erweiterung.md` | Die 6 Pool-Universen (`schrott`, `kuchen`, `spule`, `uhrwerkwueste`, `suppenmeer`, `freizeitpark`) mit Rang 1–3 Steigerung | Content & Weltenbau |
| `04-klonita-assistenz.md` | Klonita als Labor-Assistentin: Liegen-Modifikationen, Rucksack-Slot, Reaktionskaskaden (Klonita bleibt unzerstörbar!) | Begleiter-Mechanik |
| `05-behoerdenalarm-und-endgame.md` | Behörden-Großalarm bei Stations-Sabotage, Wackel-Parallelwelten, Kosmische Quest (Schwarze Kaffee-Sonne) | Endgame & Geheimnisse |

---

## 2. Leitidee: Entfesselte Wissenschaft

Während der MVP den stabilen, sauberen Spielfluss etabliert, erweitert Phase 2 das Repertoire um maximale Bautiefe:

1. **Mathematische Kombinationsmacht:** Spielerinnen können Waffen bauen, die Module rekursiv aufrufen, Geschosse aufspalten oder den Bildschirm mit physikalischen Kettenreaktionen fluten – sicher abgefangen durch Rekursionsgrenzen (`max_depth = 8`).
2. **Physikalisch saubere Alchemie:** Alchemie respektiert die Palette von 11 Grund- + maximal 10 Universums-Materialien. Reaktionen und Transmutationen finden innerhalb des aktiven Materialsatzes statt; Reingold entsteht als abbaubares `gold_vein`-Erz.
3. **Flüssigkeiten heilen nicht ohne Experiment:** Auch das seltene Schutztonikum verleiht temporäre Schilde oder Flux-Schübe; direkte Lebensregeneration bleibt dem Bibel-Selbstexperiment `blutsauger` / `alchemie_magen` vorbehalten.
4. **Respekt vor dem Fundament:** Die Werkstatt bleibt aus unzerstörbarem `bedrock` erbaut. Der Behörden-Großalarm (S.O.K.O. Paragraf) wird nicht durch Wandbohren, sondern durch mutwillige Sabotage an den Werkstatt-Stationen ausgelöst.

---

## 3. Entkopplungs-Architektur zum MVP

- **Volle Abwärtskompatibilität:** Alle 60 Basismodule, 6 Basis-Universen und 12 Werkstatt-Stationen bleiben unverändert erhalten.
- **Erweiterung von `src/wand.py`:** Die in `_Draw.next()` bereits vorhandene `wrapped`-Logik wird um Noita-artige Kopier- und Splitter-Befehle ergänzt, ohne doppelte Evaluatoren einzuführen.
- **Sequenzielle Phasenfolge:** Der MVP endet mit Phase G. Die Erweiterung setzt mit **Phase H** an (`tasks/plan_erweiterung.md`, `tasks/todo_erweiterung.md`).
