# Technische Spezifikation & Schnittstellen-Verträge (`V0`–`V23`)

Dieses Dokument ist die **verbindliche technische Spezifikation (Single Source of Truth)** und der **Vertrags-Index** für die atomare Umsetzung von `py-noita-claude` gemäß der Design-Bibel ([docs/bibel/00-uebersicht.md](../bibel/00-uebersicht.md)) und dem [ADR zu atomaren Aufgabenkarten](../adr/2026-11-01-atomare-aufgabenkarten.md).

Um das Kontextbudget kleiner/kostengünstiger Sprachmodelle (`< 15 KB` pro Aufgabenkarte) strikt einzuhalten, sind die detaillierten Python-Signaturen, Datenstrukturen und Übergabeparameter in **8 thematische Vertragsdateien** unter [`docs/plan/vertraege/`](vertraege) aufgeteilt. Jede Aufgabenkarte in `phase-a-fundament.md` bis `phase-g-abnahme.md` referenziert genau die Vertragsdatei(en), die sie benötigt.

---

## 1. Zielsetzung & Geltungsbereich (Objective)

1. **Nahtlose Kombinierbarkeit:** Alle Module (Universums-Generatoren, Kreaturen-KI, Fraktionen, Sprites/Rigging, Werkstatt-Hub, Wirtschaft, Behörden-Fahndung, Boss-Phasen, Klonita-Begleiterin, UI und Persistenz) greifen über explizite, typisierte Python-Schnittstellen (`V0`–`V23`) ohne implizite Annahmen ineinander.
2. **Bibel-Konformität als Kanon:** Wo bisherige Planungsdokumente oder früherer Bestands-Code von der Design-Bibel abwichen, setzt die Spezifikation die Design-Bibel vollständig durch und definiert in `V0a`–`V0d` explizite Migrations- und Vorab-Entscheidungen.
3. **100 % Atomare S-Karten:** Jede Aufgabenkarte in den Phasen `A` bis `G` hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien + `1` Testdatei, `0` offene Designfragen).

---

## 2. Tech-Stack & Ausführbare Kommandos

- **Sprache & Laufzeit:** Python `>= 3.11` (verwaltet über `uv`, passend zu `pyproject.toml`).
- **Bibliotheken:** `pygame-ce` (`import pygame`), Python-Standardbibliothek (`dataclasses`, `math`, `random`, `json`, `pathlib`, `typing`, `collections`).
- **Optionaler Beschleuniger:** Rust/ctypes-Kern (`noita_core.dll`/`libnoita_core.so` in `native/`) mit vollständigem reinem Python-Fallback in [`src/world.py`](../../src/world.py).
- **Verbindliche Prüfkommandos nach jeder S-Karte:**
  - Einzeltest zur Karte: `uv run pytest tests/spec/test_phase_<x>.py -k <id_klein> -q`
  - Regressionslauf der Bestands-Suite: `uv run pytest --ignore=tests/spec -q`
  - Gesamte Test-Suite: `uv run pytest -q`
  - Linter & Formatierung: `uv run ruff check src tools` und `uv run ruff format --check src tools`
  - Sprite-Generator (für Grafik-Karten): `uv run python -m tools.sprites`

---

## 3. Projektstruktur & Modul-Landkarte

```text
src/
├── universes/
│   ├── model.py          # Universe, Region, RuleEffect, CreatureSpawn, UniverseTheme
│   ├── catalog.py        # Die 6 MVP-Universen (V0a: kanonische probe_*-Keys & Region-Order) + POOL_UNIVERSES
│   ├── plan.py           # RunPlan (Alias UniversePlan: 6-Universen-Abfolge mit 2er-Portalwahl)
│   └── gen/              # NEU (V9): __init__.py, common.py + 6 MVP-Universums-Generatoren
├── bosses/               # NEU (V16–V17): __init__.py (6 Universums-Zwischengegner), evil_selves.py, headquarters.py
├── minigames/            # NEU (V20): __init__.py, physik_o_mat.py, schiessstand.py
├── behaviour.py          # NEU (V1): BehaviourContext, Ability, 20 Fähigkeiten & Handler
├── pathfind.py           # NEU (V3): A*-Pfadsuche (walk, fly, swim) mit Budget, PathFollower & Cache
├── factions.py           # NEU (V4): Fraktionen, Hass-Matrix, Blutfehden (Grudges, hostile, are_hostile)
├── sprites.py            # NEU (V5): SheetMeta, Animator, JSON-Metadaten-Loader (load_meta / load_sheet_meta)
├── sprite_render.py      # NEU (V6): SheetCache, blit_frame, glow_points
├── procbody.py           # NEU (V7): Chain, Legs, Tentacle, PartSpec, PartLayout, ProcRig
├── weapon_parts.py       # NEU (V8b): Modulare Waffenteile & Slot-Layout (gehaeuse_*, lauf_*, ...)
├── samples.py            # NEU (V11): Sample, SAMPLES (17 Proben: 12 Universums- + 5 Allgemein-Proben) + Aliase
├── events.py             # NEU (V10): 6 Universums-Hauptevents + Sekundärereignisse (EventSpec, Event)
├── challenges.py         # NEU (V13): 6 Universums-Aufträge + 6 Schrein-Prüfungen (ChallengeSpec, Challenge)
├── bot.py                # NEU (V14): Deterministischer Playtest-Bot (run_bot, run_full)
├── authority.py          # NEU (V15): Wanted (0..5 Sterne), 4 Behörden-Agenten-Typen
├── workshop.py           # NEU (V18): 640×360-Werkstatt-Hub & 12 Stationen (+ STATION_ALIASES)
├── economy.py            # NEU (V19): Gold-, Preis- und Reroll-Formeln
├── traders.py            # NEU (V19): 6 Händler-Persönlichkeiten (Herr Pansen .. Bruder Flosse) & Sonderregeln
├── fabricator.py         # NEU (V20): Zauberblock-Herstellung aus Proben + Gold + Bauplänen
├── klonita.py            # NEU (V21): Klonita-Begleiterin (Zustände, 4 Hilfen, 3 Macken)
├── klonita_lines.py      # NEU (V21): Deutsche Kommentar-Datenbank (für die 6 MVP-Universen + Trigger)
└── (Bestandsmodule)      # world.py, materials.py, enemies.py, player.py, body.py, spells.py,
                          # loot.py, inventory.py, flask.py, projectiles.py, rules.py,
                          # records.py, hover.py, hud.py, menus.py, rendering.py, run.py
```

---

## 4. Code-Stil & Namenskonventionen

- **Sprachregel:** Alle Bezeichner (Variablen, Funktionen, Klassen, Dateinamen, Enum-/Dict-Keys für interne Zustände) und Code-Kommentare sind auf **Englisch**. Alle für Spielende sichtbaren Texte (`name`, `subtitle`, `description`, `greeting_de`, Sprechblasen, HUD, Menüs) sowie alle Planungs-/Bibel-Dokumente unter `docs/` sind auf **Deutsch** (mit korrekten Umlauten `ä, ö, ü, ß`).
- **Typisierung:** Jede Datei beginnt mit `from __future__ import annotations`. Alle öffentlichen Funktionen, Methoden und `@dataclass`-Felder tragen vollständige Typ-Annotationen (`tuple[...]`, `list[...]`, `dict[...]`, `X | None`).
- **Vorbild-Muster (unveränderliche Spezifikations-Dataclasses + reine Funktionen):**

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeSpec:
    key: str
    name: str
    description: str
    reward_gold: int
    reward_samples: int = 2
    reward_perk: bool = False
    time_limit: float = 0.0
```

---

## 5. Test-Strategie (Vorab-Abnahmetests / Red-Green-Harness)

- **Vorab geschriebene Spec-Tests (`tests/spec/`):** Alle Abnahmetests für die Phasen `A` bis `G` wurden **vorab** durch ein starkes Modell gegen die Verträge `V0`–`V23` erstellt und liegen unter `tests/spec/` (`test_phase_a.py` bis `test_phase_g.py`).
- **`tests/` ist schreibgeschützt (Read-Only für ausführende Modelle):** Ausführende Modelle dürfen Dateien unter `tests/` **niemals** verändern, abschwächen oder löschen. Jede S-Karte ändert ausschließlich Produktionscode unter `src/` bzw. `tools/`.
- **Headless-Ausführung:** Alle Unit- und Integrations-Tests unter `tests/` laufen ohne Grafikfenster (`SDL_VIDEODRIVER=dummy` bzw. reine Daten-/Oberflächen-Tests).
- **Determinismus:** Zufallsabhängige Tests übergeben immer ein explizites `random.Random(seed)` oder einen festen `seed: int`.
- **1-zu-1-Kartenabsicherung:** Jede S-Karte wird über ihren spezifischen Spec-Test `uv run pytest tests/spec/test_phase_<x>.py -k <id_klein> -q` sowie den Regressionslauf der Bestands-Suite `uv run pytest --ignore=tests/spec -q` abgenommen.

---

## 6. Drei-Stufen-Grenzen (Always / Ask First / Never)

### Always (Immer ohne Rückfrage ausführen)

- Vor dem Bearbeiten einer S-Karte die in der Karte verlinkte Vertragsdatei unter `docs/plan/vertraege/`, die zugehörige Testfunktion in `tests/spec/` und die genannten Zieldateien lesen.
- Nach jeder Änderung den karten-spezifischen Spec-Test (`uv run pytest tests/spec/test_phase_<x>.py -k <id_klein> -q`), die Bestands-Suite (`uv run pytest --ignore=tests/spec -q`) und `uv run ruff check src tools` ausführen.
- Rückwärtskompatibilität bestehender Signaturen (über Default-Parameter / Keyword-Only-Argumente wie in `EnemyManager.update` oder `Pickup.__post_init__`) wahren, damit kein bestehender Test bricht.

### Ask First (Vorab Rückfrage stellen)

- Änderungen an einer Vertragssignatur in `docs/plan/vertraege/v*.md`, falls sich während der Implementierung ein unvorhergesehener Konflikt zeigt.
- Hinzufügen neuer Dateien außerhalb der im Plan benannten Modul-Landkarte.

### Never (Niemals tun)

- **Niemals** Dateien unter `tests/` (weder bestehende Tests noch `tests/spec/`) editieren, auskommentieren oder mit `@pytest.mark.skip` versehen!
- **Niemals** `pyproject.toml`, `CHANGELOG.md` oder den Rust-Code unter `native/` verändern.
- **Niemals** `git commit`, `git push` oder destruktive Git-Befehle ohne ausdrücklichen Nutzerwunsch ausführen.
- **Niemals** bestehende Audio-Events in `Run.events: list[str]` durch das neue Gameplay-Event-System `Run.emit` überschreiben.
- **Niemals** Platzhalter-Grafiken (einfarbige Rechtecke) in `tools/sprites.py` erzeugen; alle Sprites folgen den Paletten- und Schattierungsregeln aus `V8`.

---

## 7. Vertrags-Index (`V0` bis `V23`)

Jede Vertragsdatei ist unter `10 KB` groß und definiert alle Typen, Signaturen, Konstanten und Invarianten ihres Teilbereichs:

| Datei | Enthaltene Verträge | Abgedeckte Module & Schnittstellen |
| --- | --- | --- |
| [v00-migration-und-schluessel.md](vertraege/v00-migration-und-schluessel.md) | `V0a`, `V0b`, `V0c`, `V0d` | Kanonische `probe_*`-Keys & `Region.key`-Reihenfolge der 6 MVP-Universen in `src/universes/catalog.py`; `Block.rarity_tier` (`1..3`) in `src/spells.py`; `World.take_destroyed_cells()` & `gold_vein` in `src/world.py`; Vorab-Entscheidungen (`blattlaus` → `"zucker"` + Honig-Drop, `krypta`-Strömung, `glow`-JSON-Schema, `tuersteherpilz`-Bestechung, `moenchsfisch`-Chor) |
| [v01-verhalten-und-wegsuche.md](vertraege/v01-verhalten-und-wegsuche.md) | `V1`, `V1a`, `V1b`, `V1c`, `V2`, `V3`, `V4`, `V4b` | `src/behaviour.py` (`BehaviourContext`, `Ability`, 20 Fähigkeiten & Handler); 4 Haltungen (`hostile`, `neutral`, `passive`, `trader` + Aliase); erweiterte `CreatureSpec` & `Creature` + abwärtskompatibles `EnemyManager.update`; Zustandsmaschine & Telegrafie; `src/pathfind.py` (A*, `PathFollower`, `next_waypoint`); `src/factions.py` (Fraktionen & Blutfehden `Grudges`); alle Status-Timer auf `Body` & alle Flaschen-Trinkeffekte in `src/flask.py` |
| [v05-sprites-und-teile.md](vertraege/v05-sprites-und-teile.md) | `V5`, `V6`, `V7`, `V8`, `V8b` | `src/sprites.py` (`SheetMeta`, `Animator`, `load_meta` / `load_sheet_meta`); `src/sprite_render.py` (`SheetCache`, `blit_frame`, `glow_points`); `src/procbody.py` (`Chain`, `Legs`, `Tentacle`, `PartSpec`, `PartLayout`, `ProcRig`); `tools/palette.py` & `tools/sprites.py`; `src/weapon_parts.py` (`WeaponPartPlacement`, `parts_for`, `layout_for`) |
| [v09-universen-und-ereignisse.md](vertraege/v09-universen-und-ereignisse.md) | `V9`, `V10`, `V13`, `V14` | `Level`-Erweiterung (inkl. `(x0, y0, x1, y1)`-Konvention & `Run._mirror_level`), `src/universes/gen/__init__.py` & `common.py` (inkl. `"top_split"` & `"islands"` für die 6 MVP-Universen); `src/events.py` (6 Hauptevents + Sekundärereignisse); `src/challenges.py` (6 Universums-Aufträge + 6 Schrein-Prüfungen); `src/bot.py` (`BotReport`, `run_bot`, `run_full`) |
| [v11-gegenstaende-und-ereignisbus.md](vertraege/v11-gegenstaende-und-ereignisbus.md) | `V11`, `V12` | `src/samples.py` (`Sample`, `SAMPLES`, 17 Proben: 12 Universums-Proben + 5 Allgemein-Proben + `SAMPLE_ALIASES`), Proben-Slots in `src/inventory.py`, vereinheitlichtes `Pickup` (`kind`, `item_key`, `amount`) in `src/loot.py`; `Run.emit(name, **data)` & vollständige Payload-Tabelle aller 24 Gameplay-Ereignisse |
| [v15-behoerde-und-bosse.md](vertraege/v15-behoerde-und-bosse.md) | `V15`, `V16`, `V17` | `src/authority.py` (`Wanted`, `0..5` Sterne, 4 Agenten-Spezies `agent_streife`..`agent_abteilungsleiter`, `spawn_agents`); `src/bosses/__init__.py` (`BossPhase`, `BossScript`, 3- und 4-Phasen-Schwellen, 6 Universums-Zwischengegner `weltenherz`..`abt_kieme`); `src/bosses/evil_selves.py` (3 Böse Ichs, Signatur-Stäbe, Kaiserin-Handel) & `src/bosses/headquarters.py` (3-stufiges Hauptquartier & `"ober_cloita"`) |
| [v18-werkstatt-und-wirtschaft.md](vertraege/v18-werkstatt-und-wirtschaft.md) | `V18`, `V19`, `V20` | `src/workshop.py` (`640×360`-Hub & alle 12 Stationen `ws_portal`..`ws_well` + `STATION_ALIASES`); `src/economy.py` (Gold- & Preisformeln) & `src/traders.py` (6 Händler: `Herr Pansen`, `Frau Abheft`, `Wobbel`, `Krümel-Karl`, `DJ Lamelle`, `Bruder Flosse` mit `home_universe` in `fleischwelt`..`abtei`); `src/fabricator.py` & `src/minigames/` (8 Physik-o-Mat-Rätsel + Schießstand) |
| [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md) | `V21`, `V22`, `V23` | `src/klonita.py` & `src/klonita_lines.py` (Zustände, `[K]`-Toggle, Auto-Trigger, 4 Hilfen, 3 Macken, Sprüche für die 6 MVP-Universen); `SpeechBubble`, HUD-Erweiterung, Menü-Modi, Hover-Infos; `Records`-Erweiterung, Rang-Formel, rückwärtskompatibles Live-Save-Schema & `MODULE_ALIASES`/`PERK_ALIASES` |

---

## 8. Fähigkeits-Landkarte & Phasen-Zuordnung (Capability Map)

| Phase | Datei | Kern-Fähigkeiten | Benötigte Verträge |
| --- | --- | --- | --- |
| **Phase A** | [phase-a-fundament.md](phase-a-fundament.md) | Vorab-Migration (`V0a`–`V0d`), Proben & Pickup-Vereinheitlichung, Ereignisbus, Status-Timer & Flascheneffekte, Pfadsuche, Fraktionen, Verhaltens-Fähigkeiten, Kreaturen-Zustandsmaschine, Sprite-/Animator-/Prozedural-Rig-Fundament | `V0a`–`V0d`, `V1`–`V8b`, `V11`, `V12` |
| **Phase B** | [phase-b-grafik.md](phase-b-grafik.md) | Farbpaletten & Zeichen-Primitiven, Charakter-/Begleiter-/Agenten-/Händler-Sprites, alle Kreaturen-Sheets (in 3er-Packs), Bosse, Waffenteile, 35 Zauber-Icons (in 7er-Packs), Gegenstands-Icons (in 7er-Packs), Umgebungs-Props (in 6er/7er-Packs), 12 Partikel-Sheets, Renderer-Anbindung | `V5`–`V8b`, `V11`, `V18` |
| **Phase C** | [phase-c-kreaturen.md](phase-c-kreaturen.md) | Alle 24 regulären Kreaturen (je 4 pro MVP-Universum), 2 große Kreaturen, 6 Unter-Zwischenbosse, 6 Zwischengegner-Grundkörper, 4 Behörden-Agenten, 3 Böse Ichs, Ober-Cloita, Projektil-Sonderformen & Kreaturen-Interaktionen (Bestechung, Blattlaus-Melken, Chor) | `V0d`, `V1`–`V4b`, `V15`–`V17` |
| **Phase D** | [phase-d-universen.md](phase-d-universen.md) | `Level`-Erweiterung & Generator-Hilfen (`common.py`), alle 6 MVP-Universums-Generatoren (je 3 Regionen + Boss-Arenen + Schrein/Händler-Nische), Weltregel-Erweiterungen (Strömung, Takt, Rutschigkeit, Sprung-Luftkosten), 6 Universums-Events + Sekundärereignisse, Herausforderungen, Playtest-Bot | `V0a`, `V0d`, `V9`, `V10`, `V13`, `V14` |
| **Phase E** | [phase-e-werkstatt.md](phase-e-werkstatt.md) | `640×360`-Werkstatt-Generator & 12 Stationen, Wirtschaft & Gold-Drops, 6 Händler mit allen Sonderregeln, Fabrikator, 8 Physik-o-Mat-Rätsel + Schießstand, Portal-Auswahl-, Fabrikator- & Händler-Menüs, Werkstatt-Ablauf in `Run` | `V11`, `V12`, `V18`–`V20`, `V22` |
| **Phase F** | [phase-f-behoerde-bosse-klonita.md](phase-f-behoerde-bosse-klonita.md) | Fahndungslevel & Agenten-Spawns, mehrphasige Boss-Skripte für alle 6 Universums-Zwischengegner (`weltenherz`, `oberstempler`, `mutter_glibber`, `ameisenkoenigin`, `dj_myzel`, `abt_kieme`), Begegnungen mit den 3 Bösen Ichs (inkl. Kaiserin-Handel), 3-stufiges Hauptquartier & Wahres Ende, Klonita-Begleiterin & Sprechblasen | `V12`, `V15`–`V17`, `V21`, `V22` |
| **Phase G** | [phase-g-abnahme.md](phase-g-abnahme.md) | HUD-Erweiterung (Gold, Sterne, Proben, Event-Banner), Entdeckungs-Archiv (5 Reiter), Hover-Infos, vollständige Save/Load-Serialisierung & Alias-Tabellen, Rang-Abrechnung, Bot-Vollabnahme über alle 6 MVP-Universen | `V14`, `V22`, `V23` |

---

## 9. Erfolgskriterien (Success Criteria)

1. Jede Schnittstelle zwischen `src/`-Modulen ist in `docs/plan/vertraege/v*.md` mit exakten Feldnamen, Typen und Rückgabewerten spezifiziert.
2. Alle 4 vormals widersprüchlichen Bestands-Stellen (`V0a` Sample-/Regions-Keys, `V0b` `Block.rarity_tier`, `V0c` `World.take_destroyed_cells`, `V11`/`V23` `Pickup` & `Records.discover`) haben rückwärtskompatible Verträge.
3. Jede Mechanik aus `docs/bibel/` (alle Flüssigkeits-Schübe, alle 6 Händler-Eigenheiten, alle 20 Verhaltens-Fähigkeiten, Kreaturen-Sonderinteraktionen, 3 Böse Ichs + Kaiserin-Handel, 3-stufiges Hauptquartier) ist vertraglich abgedeckt.
4. Keine Aufgabenkarte in den Phasen `A` bis `G` überschreitet die Größe **S** (`<= 60–80` Zeilen Code-Änderung, `1–2` Zieldateien + Test, `< 15 KB` zu lesender Kontext).
