# Atomarer Umsetzungsplan (`py-noita-claude`)

Dieser Ordner enthält den **vollständigen, in 151 reine S-Karten zerlegten Implementierungsplan** für die Fertigstellung von `py-noita-claude` gemäß der Design-Bibel ([docs/bibel/00-uebersicht.md](../bibel/00-uebersicht.md)) und dem [ADR zu atomaren Aufgabenkarten](../adr/2026-11-01-atomare-aufgabenkarten.md).

---

## 1. Grundprinzipien für ausführende Modelle

1. **Nur Größe S & schreibgeschützte Vorab-Tests (`tests/spec/`):** Jede der **151 Karten** (`A01`–`G13`; die IDs `B06`, `B10`, `B13`, `C07`, `C08`, `C13`, `D07`–`D09` sind entfallen) ist so zugeschnitten, dass ein einzelnes kostengünstiges Modell sie in einem Durchgang fehlerfrei umsetzen kann:
   - **Umfang:** maximal `60–80` geänderte/neue Code-Zeilen pro Karte.
   - **Dateien:** `1–2` Zieldateien ausschließlich unter `src/` oder `tools/`.
   - **Vorab geschriebene Abnahmetests:** Alle Abnahmetests für sämtliche Karten (`A01`–`G10`) existieren bereits vorab unter [`tests/spec/`](../../tests/spec) (`test_phase_a.py` bis `test_phase_g.py`). Ausführende Modelle schreiben **keine** eigenen Tests und dürfen Dateien unter `tests/` **niemals** editieren!
   - **Kontext-Budget:** unter `15 KB` Lese-Kontext (jede Karte verweist gezielt auf die benötigte Teil-Vertragsdatei unter [`docs/plan/vertraege/`](vertraege) und ihre Testfunktion in `tests/spec/`).
   - **Keine offenen Designfragen:** Alle Schlüssel-, Geometrie-, Formel- und Sonderregel-Entscheidungen sind vorab in den Verträgen `V0`–`V23` festgelegt.
2. **Pflicht-Workflow pro Karte:**
   - Lies die im Feld **Zu lesender Kontext** genannten Dateien sowie die zur Karte gehörende Testfunktion `test_<id_klein>_*` in `tests/spec/test_phase_<x>.py` (z. B. `test_a01_` in `tests/spec/test_phase_a.py`).
   - Implementiere exakt die im Feld **Aufgabe** beschriebenen Signaturen und Regeln in den **Ziel-Dateien** unter `src/` bzw. `tools/` (**ignoriere** dort genannte `tests/...`-Pfade als Schreibziel — Tests sind Read-Only!).
   - Führe zur Abnahme den Spec-Test der Karte aus: `uv run pytest tests/spec/test_phase_<x>.py -k <id_klein> -q` (z. B. `uv run pytest tests/spec/test_phase_a.py -k a01 -q`) sowie den Regressionslauf `uv run pytest --ignore=tests/spec -q`.
   - Prüfe den Code-Stil mit `uv run ruff check src tools`.
3. **Tabu-Dateien (`Never`):** `tests/` (inkl. `tests/spec/`), `pyproject.toml`, `CHANGELOG.md` und der Rust-Kern unter `native/` werden **niemals** verändert.

---

## 2. Spezifikation & Schnittstellen-Verträge (`V0`–`V23`)

- **Master-Spezifikation & Vertrags-Index:** [vertraege.md](vertraege.md)
- **8 modulare Vertragsdateien (`< 10 KB` je Datei):**
  1. [v00-migration-und-schluessel.md](vertraege/v00-migration-und-schluessel.md) — `V0a`–`V0d` (Kanonische `probe_*`- & `Region.key`-Namen der 6 MVP-Universen, `Block.rarity_tier`, `World.take_destroyed_cells()`, Vorab-Entscheidungen)
  2. [v01-verhalten-und-wegsuche.md](vertraege/v01-verhalten-und-wegsuche.md) — `V1`–`V4b` (`BehaviourContext`, `Ability`, 20 Fähigkeiten, Haltungen, FSM, A*-Pfadsuche, Fraktionen, Status-Timer & Flaschen-Trinkeffekte)
  3. [v05-sprites-und-teile.md](vertraege/v05-sprites-und-teile.md) — `V5`–`V8b` (`SheetMeta`, `Animator`, `SheetCache`, `ProcRig`/`Chain`/`Legs`/`Tentacle`, Paletten & Sprite-Regeln, Waffenteile)
  4. [v09-universen-und-ereignisse.md](vertraege/v09-universen-und-ereignisse.md) — `V9`, `V10`, `V13`, `V14` (`Level`-Struktur mit `(x0, y0, x1, y1)`-Rechtecken, Generator-Helfer für die 6 MVP-Universen, 6 Hauptevents + Sekundärereignisse, 6 Prüfungen, Playtest-Bot)
  5. [v11-gegenstaende-und-ereignisbus.md](vertraege/v11-gegenstaende-und-ereignisbus.md) — `V11`, `V12` (17 Proben: 12 Universums-Proben + 5 Allgemein-Proben in `src/samples.py`, Inventar-Slots, einheitliches `Pickup`, `Run.emit` & Payload-Tabelle aller 24 Events)
  6. [v15-behoerde-und-bosse.md](vertraege/v15-behoerde-und-bosse.md) — `V15`–`V17` (`Wanted` & 4 Agenten-Spezies, `BossPhase`/`BossScript`, 6 Universums-Zwischengegner `weltenherz`..`abt_kieme`, 3 Böse Ichs + Kaiserin-Handel, Hauptquartier & `"ober_cloita"`)
  7. [v18-werkstatt-und-wirtschaft.md](vertraege/v18-werkstatt-und-wirtschaft.md) — `V18`–`V20` (`640×360`-Werkstatt & 12 Stationen + `STATION_ALIASES`, Preisformeln, 6 Händler `Herr Pansen`..`Bruder Flosse` inkl. Sonderregeln, Fabrikator, 8 Physik-o-Mat-Rätsel + Schießstand)
  8. [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md) — `V21`–`V23` (Klonita-Zustandsmaschine, 4 Hilfen & 3 Macken, Sprüche für die 6 MVP-Universen, `SpeechBubble` & Menüs, `Records.discover`, Rang-Formel, Save/Load-Schema & Alias-Tabellen)

---

## 3. Phasen-Übersicht & Karten-Zählung (151 S-Karten)

Die Pool-Universen `schrott`, `kuchen` und `spule` gehören nicht zum MVP; sie werden in Phase J der Erweiterung gebaut (`docs/erweiterung/03-universen-erweiterung.md`).

| Phase | Datei | Karten | Anzahl | Inhalt & Meilenstein |
| --- | --- | --- | --- | --- |
| **Phase A** | [phase-a-fundament.md](phase-a-fundament.md) | `A01`–`A30` | **30 S** | Schlüssel-Migration (`V0a`–`V0e`), 8 neue Füllungen, 9 ausgemusterte Alt-Füllungen, 17 Proben & Pickup-Vereinheitlichung, Event-Bus, Status-Timer & Trank-Effekte, A*-Pfadsuche, Fraktionen, Fähigkeiten, Kreaturen-FSM, Sprite-/Rig-/Waffenteil-/Generator-Fundament |
| **Phase B** | [phase-b-grafik.md](phase-b-grafik.md) | `B01`–`B36` | **33 S** | Alle Sprite-Sheets + JSON-Metadaten in kleinen Paketen (`charaktere/`, `kreaturen/` der 6 MVP-Universen + Großkreaturen, `bosse/`, `waffen/`, `zauber/`, `gegenstaende/`, `umgebung/`, `partikel/`) sowie Renderer-Integration in `src/rendering.py` |
| **Phase C** | [phase-c-kreaturen.md](phase-c-kreaturen.md) | `C01`–`C17` | **14 S** | Alle 24 regulären Kreaturen der 6 MVP-Universen + 2 Großkreaturen (`trampolinwal`, `kirchenkrake`), 6 Unter-Zwischenbosse, 6 Haupt-Zwischengegner (`weltenherz`..`abt_kieme`), 4 Behörden-Agenten, 3 Böse Ichs, Rat, `"ober_cloita"`, Projektil-Statuseffekte, Drops & Elementar-Resistenzen |
| **Phase D** | [phase-d-universen.md](phase-d-universen.md) | `D01`–`D29` | **26 S** | Materialsätze (`D17`–`D21`) und alle 6 MVP-Universums-Generatoren (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`), `worldgen`-Dispatch, 6 Universums-Events (`src/events.py`; Sekundärereignisse → Phase 2, J07), alle 6 Prüfungen + 6 Universums-Herausforderungen (`src/challenges.py`, `D22`–`D29`), deterministischer Playtest-Bot (`src/bot.py`) |
| **Phase E** | [phase-e-werkstatt.md](phase-e-werkstatt.md) | `E01`–`E16` | **16 S** | `640×360`-Werkstatt & 12 Stationen, Wirtschaftsformeln & Goldader-Drops, 6 Händler (`Herr Pansen`..`Bruder Flosse`) mit allen Sonderregeln, Fabrikator, 7 Physik-o-Mat-Rätsel + Schießstand, Experimentierliege, Werkstatt-Menüs & Trainings-Attrappe |
| **Phase F** | [phase-f-behoerde-bosse-klonita.md](phase-f-behoerde-bosse-klonita.md) | `F01`–`F19` | **19 S** | Fahndungssystem (`Wanted`) & Agenten-Spawns, mehrphasige Boss-Skripte für alle 6 Universums-Zwischengegner, 3 Böse Ichs mit Echos, Heimatwelten & Endkampf, Kaiserin-Angebot (böses Ende), 3-stufiges Hauptquartier & `"ober_cloita"`, Klonita-Begleiterin (Hilfen + Bibel-Aktionen Zeigen/Tragen/Umarmen, 6 Macken) & Sprechblasen |
| **Phase G** | [phase-g-abnahme.md](phase-g-abnahme.md) | `G01`–`G13` | **13 S** | HUD-Erweiterung, Sprechblasen- & Boss-Banner-Rendering, Hover-Infos, `Records` & 5-Reiter-Archiv, Endbildschirm mit Rang-Abrechnung, vollständiges Save/Load-Schema, Menü-Tastatursteuerung & Bot-Vollabnahme über alle 6 MVP-Universen, Modul-Anzeigenamen nach Bibel 06 (`G11`–`G13`) |

---

## 4. Abhängigkeits- & Parallelisierungs-Graph

```mermaid
flowchart TD
    A["Phase A: Fundament (A01–A30)"]
    B["Phase B: Prozedurale Grafik (B01–B36)"]
    C["Phase C: Kreaturen & Boss-Specs (C01–C17)"]
    D["Phase D: Materialsätze, Universen, Events, Challenges & Bot (D01–D29)"]
    E["Phase E: Werkstatt, Wirtschaft, Händler & Minispiele (E01–E16)"]
    F["Phase F: Behörde, Boss-Phasen, Böse Ichs, HQ & Klonita (F01–F19)"]
    G["Phase G: HUD, Archiv, Save/Load & Vollabnahme (G01–G13)"]

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

1. **Sequentieller Start in Phase A (`A01`–`A30`):** Schafft alle Schnittstellen, Datenklassen und Migrations-Anpassungen.
2. **Parallele Stränge nach Phase A:**
   - **Grafik-Strang (`B01`–`B36`)** kann nach `A22`/`A23` komplett unabhängig abgearbeitet werden.
   - **Kreaturen-Strang (`C01`–`C17`)** startet direkt nach `A15`.
   - **Universen-Strang (`D01`–`D21`)** startet nach `A25`; jeder Generator braucht vorher seinen Materialsatz (`D17`–`D21`, Aktenhalde hat ihn schon).
   - **Werkstatt-Grundlagen (`E01`–`E09`)** starten direkt nach `A04`.
3. **Integration (`E10`–`E16` und `F01`–`F19`):** Verbindet Werkstatt, Händler, Fahndung, mehrphasige Bosse, Böse Ichs, Hauptquartier und Klonita mit `Run`.
4. **Abschluss & Abnahme (`G01`–`G10`):** Vervollständigt UI, Archiv, Save/Load und führt in `G10` die End-to-End-Vollabnahme über alle 6 MVP-Universen durch.

## 5. Bekannte Nachbesserungen nach dem MVP

### Figuren-Grafik (`B01`–`B19`, Stand 2026-11-07)

Die Sheets erfüllen `V8` (eigene Silhouette, echte Bewegung), sind aber nur **MVP-Platzhalter** und deutlich schwächer als gewünscht. Vor einem Release werden sie überarbeitet; Grundlage ist eine Sichtprüfung durch den Nutzer, nicht nur die Tests.

- **Bewegung umgeht die Regel:** Statt Beine, Flügel oder Tentakel zu bewegen, wird oft ein Frame gestaucht und der letzte geschrumpft (z. B. `weltenherz`, `sporenherz`, `boese_gute`, `mutter_glibber`, `glibberteiler`, `ober_cloita`).
- **Noch Klötze mit Augen:** `aktenfresser`, `glibberteiler`, `harzspucker`, `agent_drohne`, `npc_glibberhaendler`, `npc_ameisenhehler`.
- **Wenig Binnendetail:** Gesichter, Muster und Materialwirkung fehlen weitgehend; eine Palette pro Universum lässt die Kreaturen einer Welt farblich verschwimmen.
- **Gut gelungen, als Maßstab:** `aktenwolf`, `kirchenkrake`, `glockenqualle`, `orgelaal`, `blutegel`, `abt_kieme`, `oberstempler`, `trampolinwal`, `npc_kuester`.

Vorgehen später: eigene Karten je Gruppe, mit Vorschaubildern (alle Frames vergrößert nebeneinander) zur Abnahme durch den Nutzer.
