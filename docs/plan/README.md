# Atomarer Umsetzungsplan (`py-noita-claude`)

Dieser Ordner enthält den **vollständigen, in 134 reine S-Karten zerlegten Implementierungsplan** für die Fertigstellung von `py-noita-claude` gemäß der Design-Bibel ([docs/bibel/00-uebersicht.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/bibel/00-uebersicht.md)) und dem [ADR zu atomaren Aufgabenkarten](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/adr/2026-11-01-atomare-aufgabenkarten.md).

---

## 1. Grundprinzipien für ausführende Modelle

1. **Nur Größe S:** Jede der **134 Karten** (`A01`–`G10`) ist so zugeschnitten, dass ein einzelnes kostengünstiges Modell sie in einem Durchgang fehlerfrei umsetzen kann:
   - **Umfang:** maximal `60–80` geänderte/neue Code-Zeilen pro Karte.
   - **Dateien:** `1–2` Zieldateien + `1` Testdatei.
   - **Kontext-Budget:** unter `15 KB` Lese-Kontext (jede Karte verweist gezielt auf die benötigte Teil-Vertragsdatei unter [`docs/plan/vertraege/`](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/)).
   - **Keine offenen Designfragen:** Alle Schlüssel-, Geometrie-, Formel- und Sonderregel-Entscheidungen sind vorab in den Verträgen `V0`–`V23` festgelegt.
2. **Pflicht-Workflow pro Karte:**
   - Lies nur die im Feld **Zu lesender Kontext** genannten Dateien.
   - Implementiere exakt die im Feld **Aufgabe** beschriebenen Signaturen und Regeln.
   - Schreibe oder erweitere die genannte Testdatei und führe den Befehl unter **Verifikation** aus (`uv run pytest ... -q && uv run pytest -q`).
   - Prüfe den Code-Stil mit `uv run ruff check src tests tools`.
3. **Tabu-Dateien:** `pyproject.toml`, `CHANGELOG.md` und der Rust-Kern unter `native/` werden **niemals** verändert.

---

## 2. Spezifikation & Schnittstellen-Verträge (`V0`–`V23`)

- **Master-Spezifikation & Vertrags-Index:** [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md)
- **8 modulare Vertragsdateien (`< 10 KB` je Datei):**
  1. [v00-migration-und-schluessel.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v00-migration-und-schluessel.md) — `V0a`–`V0d` (Kanonische `probe_*`- & `Region.key`-Namen, `Block.rarity_tier`, `World.take_destroyed_cells()`, Vorab-Entscheidungen)
  2. [v01-verhalten-und-wegsuche.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v01-verhalten-und-wegsuche.md) — `V1`–`V4b` (`BehaviourContext`, `Ability`, Haltungen, FSM, A*-Pfadsuche, 11 Fraktionen, Status-Timer & alle 15 Flaschen-Trinkeffekte)
  3. [v05-sprites-und-teile.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v05-sprites-und-teile.md) — `V5`–`V8b` (`SheetMeta`, `Animator`, `SheetCache`, `ProcRig`/`Chain`/`Legs`/`Tentacle`, Paletten & Sprite-Regeln, Waffenteile)
  4. [v09-universen-und-ereignisse.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v09-universen-und-ereignisse.md) — `V9`, `V10`, `V13`, `V14` (`Level`-Struktur mit `(x0, y0, x1, y1)`-Rechtecken, Generator-Helfer, 9 Sekundärereignisse, 6 Prüfungen, Playtest-Bot)
  5. [v11-gegenstaende-und-ereignisbus.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md) — `V11`, `V12` (14 Proben in `src/samples.py`, Inventar-Slots, einheitliches `Pickup`, `Run.emit` & Payload-Tabelle aller 24 Events)
  6. [v15-behoerde-und-bosse.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v15-behoerde-und-bosse.md) — `V15`–`V17` (`Wanted` & 3 Agenten-Spezies, `BossPhase`/`BossScript`, 9 Universums-Endbosse, 3 Böse Ichs + Kaiserin-Handel, Hauptquartier & `"ober_cloita"`)
  7. [v18-werkstatt-und-wirtschaft.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md) — `V18`–`V20` (`640×360`-Werkstatt & 10 Stationen, Preisformeln, 6 Händler inkl. Sonderregeln, Fabrikator, 4 Physik-o-Mat-Rätsel + Schießstand)
  8. [v21-klonita-ui-und-speichern.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v21-klonita-ui-und-speichern.md) — `V21`–`V23` (Klonita-Zustandsmaschine, 4 Hilfen & 3 Macken, `SpeechBubble` & Menüs, `Records.discover`, Rang-Formel, Save/Load-Schema & Alias-Tabellen)

---

## 3. Phasen-Übersicht & Karten-Zählung (134 S-Karten)

| Phase | Datei | Karten | Anzahl | Inhalt & Meilenstein |
| --- | --- | --- | --- | --- |
| **Phase A** | [phase-a-fundament.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-a-fundament.md) | `A01`–`A26` | **26 S** | Schlüssel-Migration (`V0a`–`V0d`), Proben & Pickup-Vereinheitlichung, Event-Bus, Status-Timer & 15 Trank-Effekte, A*-Pfadsuche, Fraktionen, 10 Fähigkeiten, Kreaturen-FSM, Sprite-/Rig-/Waffenteil-/Generator-Fundament |
| **Phase B** | [phase-b-grafik.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-b-grafik.md) | `B01`–`B36` | **36 S** | Alle Sprite-Sheets + JSON-Metadaten in kleinen Paketen (`charaktere/`, `kreaturen/` je Universum, `bosse/`, `waffen/`, `zauber/`, `gegenstaende/`, `umgebung/`, `partikel/`) sowie Renderer-Integration in `src/rendering.py` |
| **Phase C** | [phase-c-kreaturen.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-c-kreaturen.md) | `C01`–`C17` | **17 S** | Alle 36 Universums-Kreaturen (in 9 Universums-Paketen), 9 Zwischenbosse, 9 Endbosse, 3 Behörden-Agenten, 3 Böse Ichs, `"ober_cloita"`, Projektil-Statuseffekte, Drops & Elementar-Resistenzen |
| **Phase D** | [phase-d-universen.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-d-universen.md) | `D01`–`D16` | **16 S** | Alle 9 Universums-Generatoren (`src/universes/gen/*.py`), `worldgen`-Dispatch, alle 9 Sekundärereignisse (`src/events.py`), alle 6 Prüfungen (`src/challenges.py`), deterministischer Playtest-Bot (`src/bot.py`) |
| **Phase E** | [phase-e-werkstatt.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-e-werkstatt.md) | `E01`–`E15` | **15 S** | `640×360`-Werkstatt & 10 Stationen, Wirtschaftsformeln & Goldader-Drops, 6 Händler mit allen Sonderregeln, Fabrikator, 4 Physik-o-Mat-Rätsel + Schießstand, Werkstatt-Menüs & Trainings-Attrappe |
| **Phase F** | [phase-f-behoerde-bosse-klonita.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-f-behoerde-bosse-klonita.md) | `F01`–`F14` | **14 S** | Fahndungssystem (`Wanted`) & Agenten-Spawns, mehrphasige Boss-Skripte für alle 9 Endbosse, 3 Böse Ichs + Kaiserin-Handel, 3-stufiges Hauptquartier & `"ober_cloita"`, Klonita-Begleiterin & Sprechblasen |
| **Phase G** | [phase-g-abnahme.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/phase-g-abnahme.md) | `G01`–`G10` | **10 S** | HUD-Erweiterung, Sprechblasen- & Boss-Banner-Rendering, Hover-Infos, `Records` & 5-Reiter-Archiv, Endbildschirm mit Rang-Abrechnung, vollständiges Save/Load-Schema, Menü-Tastatursteuerung & Bot-Vollabnahme |

---

## 4. Abhängigkeits- & Parallelisierungs-Graph

```mermaid
flowchart TD
    A["Phase A: Fundament (A01–A26)"]
    B["Phase B: Prozedurale Grafik (B01–B36)"]
    C["Phase C: Kreaturen & Boss-Specs (C01–C17)"]
    D["Phase D: Universen, Events, Challenges & Bot (D01–D16)"]
    E["Phase E: Werkstatt, Wirtschaft, Händler & Minispiele (E01–E15)"]
    F["Phase F: Behörde, Boss-Phasen, Böse Ichs, HQ & Klonita (F01–F14)"]
    G["Phase G: HUD, Archiv, Save/Load & Vollabnahme (G01–G10)"]

    A --> B
    A --> C
    A --> D
    A --> E
    C --> F
    D --> E
    E --> F
    B --> G
    D --> G
    E --> G
    F --> G
```

### Empfohlene Abarbeitungsreihenfolge

1. **Sequentieller Start in Phase A (`A01`–`A26`):** Schafft alle Schnittstellen, Datenklassen und Migrations-Anpassungen.
2. **Parallele Stränge nach Phase A:**
   - **Grafik-Strang (`B01`–`B36`)** kann nach `A22`/`A23` komplett unabhängig abgearbeitet werden.
   - **Kreaturen-Strang (`C01`–`C17`)** startet direkt nach `A15`.
   - **Universen-Strang (`D01`–`D16`)** startet direkt nach `A25`.
   - **Werkstatt-Grundlagen (`E01`–`E09`)** starten direkt nach `A04`.
3. **Integration (`E10`–`E15` und `F01`–`F14`):** Verbindet Werkstatt, Händler, Fahndung, mehrphasige Bosse, Böse Ichs, Hauptquartier und Klonita mit `Run`.
4. **Abschluss & Abnahme (`G01`–`G10`):** Vervollständigt UI, Archiv, Save/Load und führt in `G10` die End-to-End-Vollabnahme über alle 9 Universen durch.
