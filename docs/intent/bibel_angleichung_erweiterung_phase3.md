# Statement of Intent: Bibel-Angleichung für Erweiterung & Phase 3

Stand: 2026-11-03  
Status: Bestätigt durch den Nutzer

---

## 1. Zielbild & Motivation

Vollständige Überarbeitung und Bereinigung der Planungs- und Spezifikationsdokumente für:

1. **Erweiterung (Phasen H–M):** `docs/erweiterung/` (Noita-Zaubermathematik, Alchemie, 6 Pool-Universen)
2. **Phase 3 (Phasen N–U):** `docs/phase3_absurditaet/` (Worldbuilding, Gadgets, TV, Zitadelle, Satire-Universen)

Beide Ausbaustufen müssen zu 100 % konform mit den Parametern der Basis-Bibel (`docs/bibel/`), den physikalischen Grenzen der Falling-Sand-Engine und dem real existierenden Code sein. Der anarchische, bitterböse Charme und die spielerische Tiefe bleiben vollständig erhalten, während Widersprüche, Regelbrüche und Plagiate fremder Serien beseitigt werden.

---

## 2. Zielgruppe & Kernnutzen

- **Spielerinnen:** Erleben nach Abschluss des MVP einen nahtlosen Übergang in astronomische Noita-Kombinatorik, tiefgründige Alchemie und satirisch-absurdes Worldbuilding.
- **Entwickler & Coding-Agenten:** Erhalten widerspruchsfreie, technisch machbare Spezifikationen, die direkt in Code und atomare Tests umsetzbar sind, ohne an harten Engine-Grenzen zu zerschellen.

---

## 3. Verbindliche Erfolgs-Kriterien

1. **100 % Original-Lore (Bibel Kap. 00 & 08):**
   - Keine Zitate, 1:1-Charaktere oder Plagiate aus *Rick and Morty* (kein Pickle Rick, kein Butter-Robot, kein Meeseeks, keine Two Brothers).
   - Alle Gadgets, Dialoge und Medien sind eigenständige Cloita-Erfindungen mit trockenem, sarkastischem Wissenschafts-Humor.
2. **Klonita-Schutz (Bibel Kap. 02 & 04):**
   - Klonita ist und bleibt Cloitas einziger, körperlich unzerstörbarer Ur-Klon.
   - Keine Klonita-Massenproduktion, kein „Verschleiß-Zähler“, kein Tod von Klonita.
   - Der finstere narrative Gegenpart ist kein böser Klon, sondern ein **Böses Ich** (eine abtrünnige, verbitterte Parallel-Cloita).
3. **Flüssigkeiten & Heilung (Bibel Kap. 02 & 06):**
   - Keine Flüssigkeit heilt Lebenspunkte ohne ein aktives Selbstexperiment (wie `blutsauger`).
   - Wundertonikum gewährt stattdessen einen temporären Schutzschild, Flux-Aufladung oder Status-Bereinigung.
4. **Physikalische Materialgrenzen (Bibel Kap. 02):**
   - Pro Universum sind strikt maximal 11 Grundmaterialien + 10 Universumsmaterialien aktiv.
   - Geheimrezepte basieren auf dem aktiven Universumssatz + Grundmaterialien.
   - Midas verwandelt Feststoffe in das offizielle Bibel-Material `gold_vein` (Golderz), statt unkontrolliert Gegenstände zu spawnen.
   - Realitäts-Flimmern tauscht nur Materialien aus, die im geladenen Materialsatz existieren.
5. **Werkstatt-Unantastbarkeit & Behörden-Alarm:**
   - Werkstattwände bestehen aus unzerstörbarem `bedrock`.
   - Der Behörden-Großalarm (S.O.K.O. Paragraf) wird durch mutwilligen Vandalismus an Werkstatt-Stationen (z. B. Überlastung des Akten-Schredders, Tresor-Knacken) ausgelöst, nicht durch Wandbohren.
6. **Bestehende Engine-Architektur nutzen:**
   - Modul-Rückgriff (Wand-Wrapping) erweitert `src/wand.py` direkt (wo `wrapped` bereits existiert), statt einen doppelten Evaluator zu bauen.
   - Kolbengröße ist standardmäßig 300 Zellen (gemäß `flask.py`).
7. **Gameplay & Spielspaß zuerst:**
   - Verzicht auf unspielbare oder morbide Gimmicks (keine Nudel-Transformation aus Suizid-Motiven, kein unspielbarer Splitscreen bei Quantenwelten).

---

## 4. Bindende Beschränkungen (Constraints)

- **Unantastbarkeit des MVP:** Das MVP-Fundament (`docs/bibel/`, `docs/plan/`, `tasks/plan.md`, `tasks/todo.md`, Phasen A–G) bleibt zu 100 % unverändert.
- **Repository-Integrität:** `CHANGELOG.md` und `pyproject.toml` werden niemals modifiziert.
- **Namenskonventionen:** Code englisch (`snake_case`), UI und Spieltexte deutsch (kurz, mit Umlauten).

---

## 5. Explizit nicht im Scope (Out of Scope)

- Keine Übernahme von Markennamen, Dialogzitaten oder 1:1-Konzepten externer TV-Serien.
- Keine Klonita-Massenlegebatterie oder Klonita-Opferung.
- Keine physikalische Verschiebung ganzer Wand-Gitter oder Splitscreen-Simulationen im Rust-Kern.
- Keine Heilwirkung von Flüssigkeiten ohne Selbstexperiment.
