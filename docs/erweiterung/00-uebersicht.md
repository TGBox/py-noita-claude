# Cloita Interdimensional – Erweiterungs-Bibel: Entfesselte Wissenschaft

Stand: 2026-11-02. Gilt für den **zweiten Ausbau-Lauf (Post-MVP / Phasen H–M)**.
Dieses Dokumentenpaket ist vollständig **vom MVP-Plan abgekapselt**. Es baut auf dem abgenommenen Fundament der Phasen A–G auf und fügt tiefgründige Noita-artige Systemmechaniken, Alchemie, Endgame-Geheimnisse und sechs neue absurde Universen hinzu.

---

## 1. Übersicht der Kapitel

| Datei | Inhalt | Fokus |
| --- | --- | --- |
| `00-uebersicht.md` | Leitidee, Entkopplungsprinzip, Glossar & Noita-Äquivalente | Architektur & Überblick |
| `01-modul-mathematik.md` | Erweiterte Deck-Mathematik, Wand-Wrapping, Kopier-Protokolle, Klon-Splitter, Orbit-Satelliten | Waffen- & Zaubersystem |
| `02-alchemie-und-kessel.md` | Geheim-Alchemie (Wundertonikum & Midas-Schmelze), Destillierkessel, Phiolen-Synthese, globale Realitäts-Flimmern (Fungal Shifts) | Physik- & Alchemiesystem |
| `03-universen-erweiterung.md` | Die 6 neuen Universen (`schrott`, `kuchen`, `spule`, `uhrwerkwueste`, `suppenmeer`, `freizeitpark`) mit Materialien, Kreaturen & Bossen | Content & Weltenbau |
| `04-klonita-assistenz.md` | Klonita als aktive Labor-Assistentin, Klonita-Selbstexperimente, Rucksack-Erweiterung, Reaktionskaskaden | Begleiter-Mechanik |
| `05-behoerdenalarm-und-endgame.md` | Behörden-Großalarm (S.O.K.O. Paragraf bei Werkstatt-Vandalismus), Wackel-Parallelwelten, Kosmische Quest (Schwarze Kaffee-Sonne) | Endgame & Geheimnisse |

---

## 2. Leitidee: Entfesselte Wissenschaft

Während der MVP den stabilen, sauberen Spielfluss etabliert, sprengt die Erweiterung die Grenzen des Labors:

1. **Unbegrenzte Kombinationsmacht:** Spielerinnen können Waffen bauen, die sich selbst rekursiv aufrufen, Geschosse in Fraktale zerlegen oder den gesamten Bildschirm mit physikalischen Kettenreaktionen fluten.
2. **Experimentelle Unberechenbarkeit:** Alchemie ist nicht mehr nur statisches Mischen am Zapfhahn, sondern eine kosmische Naturgewalt. Wer unvorsichtig mit Sporen experimentiert oder Kessel überhitzt, riskiert, dass sich weltweites Wasser in Säure oder feste Aktenberge in kochenden Brausesirup verwandeln.
3. **Konsequenzen für Frevel:** Wer die Heiligkeit der interdimensionalen Werkstatt verletzt (z.B. durch Sprengung der Sicherheitsbarrieren), bekommt es mit den gefürchtetsten Sonderermittlern der Behörde zu tun.
4. **Kosmische Dimensionen:** Jenseits der sechs Kernwelten warten unendliche, instabile Parallelwelten voller verzerrter Klonitas und das ultimative Ziel: die Erschaffung einer kosmischen Schwarzen Kaffee-Sonne zur ewigen Beseitigung aller Fristen und Mahnungen.

---

## 3. Entkopplungs-Architektur zum MVP

- **Keine Rückwärts-Inkompatibilität:** Alle bestehenden 60 Basismodule, 6 Basis-Universen und 12 Werkstatt-Stationen bleiben in ihrer Funktion zu 100 % erhalten.
- **Modulares Aufsetzen:** Die neuen Mechanismen werden als Subsysteme und Komponenten ergänzt (`src/wand_evaluator.py`, `src/alchemy_advanced.py`, `src/reality_shift.py`, `src/parallel_worlds.py`).
- **Sequenzielle Phasenfolge:** Der MVP endet mit Phase G (Abnahme). Die Erweiterung beginnt mit **Phase H** (`tasks/plan_erweiterung.md`, `tasks/todo_erweiterung.md`), sodass niemals konkurrierende Aufgaben existieren.

---

## 4. Glossar: Noita-Referenz → Cloita-Erweiterung

| Noita-Konzept | Cloita-Erweiterung | Code-Schlüssel | Bedeutung / Humor-Dreh |
| --- | --- | --- | --- |
| Wand Wrapping | **Modul-Rückgriff** | `deck_wrap` | Wenn ein Zieh-Befehl am Ende der Waffe ankommt, greift er wieder auf ungenutzte Module am Anfang zu. |
| Greek Letters (Alpha, Omega, Tau...) | **Kopier-Protokolle** | `proto_alpha`, `proto_omega`, `proto_zeta` | Wissenschaftliche Ausführungsprotokolle, die den ersten/letzten/beliebigen Zauber kopieren (auch ohne Ladung). |
| Divide By (2, 3, 4, 10) | **Klon-Splitter** | `split_duo`, `split_trio`, `split_dekade` | Zersplittert das nachfolgende Modul in rekursive Miniaturkopien mit steigender Flux-Last. |
| Larpa / Orbit Modifiers | **Satelliten-Funken / Spiegelschwarm** | `mod_satellit`, `mod_larpa_chaos` | Geschosse spawnen während des Flugs orbitierende oder regnende Begleitgeschosse. |
| Lively Concoction | **Wundertonikum** | `wundertonikum` | Seed-abhängiges Geheimrezept aus 3 Flüssigkeiten; regeneriert kontinuierlich Leben. |
| Draught of Midas | **Midas-Schmelze** | `midas_schmelze` | Seed-abhängiges Gemisch; löst jede feste Materie in reines Gold auf. |
| Fungal Reality Shift | **Realitäts-Flimmern / Sporen-Rausch** | `reality_shift` | Drogen-/Partikel-Überlastung wandelt weltweit ein Material permanent in ein anderes um. |
| Stevari / Scott (Gods Angered) | **S.O.K.O. Paragraf / Chef-Prüfer** | `soko_paragraf`, `chef_pruefer` | Erscheint sofort, wenn Werkstattwände oder Schutzkammern mutwillig beschädigt werden. |
| Parallel Worlds (East/West) | **Wackel-Parallelwelten** | `wobble_east`, `wobble_west` | Unendliche Kopien der Universen hinter toxischen Barrieren mit korrumpierten Mutanten. |
| Sun Quest / Moon Quest | **Schwarze Kaffee-Sonne** | `quest_coffee_sun` | Mehretappige Endgame-Quest zur Erschaffung eines gravitativ kochenden Kaffeekerns. |
| Cauldron Room | **Der Verlassene Kesselraum** | `cauldron_room` | Geheimraum mit uraltem Destillierkessel für Phiolen-Transmutationen. |
