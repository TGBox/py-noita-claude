# Phase A – Fundament (offen: T5, T6)

T1–T4 sind erledigt (siehe `docs/bibel/09-arbeitspakete.md`, „Stand Phase A“).

## T5 Verhaltensbibliothek

Gemeinsam für alle T5-Karten – Lesen: `vertraege.md` V1, V2 (und V3/V4, wo genannt); Bibel 02 „Verhaltensbibliothek“. Test-Hilfe aus T5.02 benutzen.

### T5.01 Felder in CreatureSpec und Creature

- Art: Code · Größe: S · Hängt ab von: –
- Lesen: V1b, V1c; `src/enemies.py` Zeilen 20–60 und `Creature.__init__`
- Dateien: `src/enemies.py`, `tests/test_behaviour.py` (neu)
- Tun:
  1. Felder aus V1b mit Standardwerten an `CreatureSpec` anhängen.
  2. Felder aus V1c (ohne `abilities`, `steer_to`) in `Creature.__init__` setzen.
  3. `Creature.hurt` um `source=None` erweitern; `last_hit_from = source`, wenn gegeben.
- Test: bestehende Kreatur bekommt Standardwerte; `hurt(5, source=(1, 2))` setzt `last_hit_from`.
- Fertig, wenn: alle alten Tests grün.
- Nicht: Verhalten ändern.

### T5.02 Modul `behaviour.py` mit Registry und Test-Hilfe

- Art: Code · Größe: S · Hängt ab von: T5.01
- Lesen: V1
- Dateien: `src/behaviour.py` (neu), `tests/behaviour_helpers.py` (neu), `tests/test_behaviour.py`
- Tun:
  1. `STANCES`, `ABILITY_KEYS`, `BehaviourContext`, `Ability` (Basis mit leeren Haken), `ABILITIES`, `register`, `build_abilities` laut V1. Unbekannter Schlüssel in `spec.abilities` → `ValueError` mit Schlüsselname.
  2. `build_abilities` ergänzt `retaliate`, wenn Haltung ≠ `passive` und nicht genannt (nur wenn `retaliate` registriert ist).
  3. In `tests/behaviour_helpers.py`: `make_world(w=200, h=120)` (Welt mit Boden aus Fels), `make_ctx(world, creatures, player)`, `make_creature(**spec_overrides)`.
- Test: Registry-Dekorator, `ValueError`, Ergänzung von `retaliate`.
- Fertig, wenn: Hilfen werden von T5.05+ benutzt.
- Nicht: einzelne Fähigkeiten.

### T5.03 Zustände und Ausholen

- Art: Code · Größe: S · Hängt ab von: T5.01
- Lesen: V2
- Dateien: `src/enemies.py`, `tests/test_behaviour.py`
- Tun: `set_state`, `begin_attack(kind)`, Zustandsuhr in `update` (`state_time += dt`), Übergänge `windup → attack → idle` laut V2; `hurt` setzt `hurt` 0,15 s, außer im `windup`. Konstante `MIN_WINDUP = 0.4`; `spec.windup` darunter wird angehoben.
- Test: Schaden erst nach ≥ 0,4 s; `hurt` unterbricht `windup` nicht.
- Nicht: alten Nahkampf umstellen (passiert in T5.13).

### T5.04 update_behaviour und steer_to

- Art: Code · Größe: M · Hängt ab von: T5.02, T5.03
- Lesen: V1 (Reihenfolge), V1a; `Creature.update`, `_crawl`, `_fly`
- Dateien: `src/enemies.py`, `src/behaviour.py`, `tests/test_behaviour.py`
- Tun:
  1. `Creature.steer_to(x, y, dt)`: setzt Richtung und ruft die vorhandene Lauf-/Fluglogik (aus `_crawl`/`_fly` herausziehen, nicht kopieren).
  2. `update_behaviour` laut V1: Haltung/Aggro (V1a), Fähigkeiten, Bewegungsziel, sonst Umherwandern (`_wander`).
  3. In `Creature.update`: Wenn `spec.abilities` nicht leer → neuer Pfad (`update_behaviour`), sonst alter Pfad unverändert. `Creature` braucht dafür den Kontext: `EnemyManager.update` baut einen `BehaviourContext` je Bild und übergibt ihn (optionaler Parameter `ctx=None`).
  4. `ctx.events` am Ende von `EnemyManager.update` zurückgeben (zweiter Rückgabewert nur, wenn ein neuer Parameter `with_events=True` gesetzt ist; sonst Verhalten wie bisher).
- Test: Kreatur mit `abilities=("melee",)` und Haltung `passive` greift nie an (Dummy-Fähigkeit registrieren).
- Nicht: `run.py` ändern (T5.21).

### T5.05 Wegsuche

- Art: Code · Größe: M · Hängt ab von: –
- Lesen: V3; `mat.BLOCKS_BODY` in `src/materials.py`
- Dateien: `src/pathfind.py` (neu), `tests/test_pathfind.py` (neu)
- Tun: `find_path` (A*, `heapq`), `PathFollower` laut V3.
- Test: Weg um eine Wand; kein Weg in eine geschlossene Kammer → `None`; `max_nodes` begrenzt (Laufzeit < 50 ms auf 400×300).
- Nicht: Kreaturen anbinden.

### T5.06 Fraktionen und Groll

- Art: Code · Größe: S · Hängt ab von: T5.01
- Lesen: V4; Bibel 02 „Fraktionen“
- Dateien: `src/factions.py` (neu), `tests/test_factions.py` (neu)
- Test: Tabelle aller Paare; Groll macht zwei Einheimische feindlich; `to_data`/`from_data` Rundreise.
- Nicht: Kreaturen kämpfen lassen (T5.20).

### T5.07 Fähigkeit `melee`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: Bei Berührung (`MELEE_REACH`) und `aggro`: `begin_attack("melee")`; beim Übergang zu `attack` Schaden `spec.melee_damage * power`, Abklingzeit `spec.melee_cooldown`. Wunsch-Ziel: Spieler.
- Test: Treffer erst nach Ausholen; Abklingzeit eingehalten.

### T5.08 Fähigkeit `hunt`

- Art: Code · Größe: S · Hängt ab von: T5.04, T5.05
- Tun: `aggro` → `wants_move` liefert nächsten Wegpunkt von `PathFollower` zum Spieler; ohne Sicht weiter zur letzten bekannten Position (`MEMORY`). „Geruch“: im MVP = letzte bekannte Position.
- Test: Kreatur hinter einer Wand findet den Weg (Abstand nimmt über 3 s ab).

### T5.09 Fähigkeit `retaliate`

- Art: Code · Größe: S · Hängt ab von: T5.08
- Tun: `on_hurt` mit `source` → Ziel = `source`, `aggro=True`; folgt dem Weg zur Quelle auch ohne Sicht, bis 8 s vergangen oder Spieler gesehen.
- Test: Treffer mit `source` hinter einer Wand → Kreatur bewegt sich dorthin.

### T5.10 Fähigkeit `pack`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: wird ein Mitglied (gleiche `group_id`, ≠ 0) getroffen oder aggro, werden alle im Umkreis 300 px `aggro`.
- Test: drei Kreaturen, eine getroffen → alle aggro; andere Gruppe bleibt ruhig.

### T5.11 Fähigkeit `flee`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: bei `fleeing` oder Spieler < Parameter `flee_distance` (Standard 80): Wunsch-Ziel = Punkt weg vom Spieler.
- Test: Abstand wächst.

### T5.12 Fähigkeit `graze`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Lesen: V1 `GRAZE_MATERIAL`
- Tun: wandert, entfernt alle 0,5 s eine Zelle `GRAZE_MATERIAL[spec.key]` in Reichweite 3 px, wächst bis 120 % Breite/Höhe (Zähler, Größe nur um 1 px je 20 Bissen).
- Test: Materialzellen nehmen ab.

### T5.13 Fähigkeit `ranged`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Lesen: `Creature._attack` (vorhandene Muster-Waffen)
- Tun: vorhandenes Muster-Schießen in eine Fähigkeit verschieben, mit `windup` davor. Alter Pfad ruft weiter die alte Funktion.
- Test: Schuss erst nach Ausholen; Reichweite `spec.ranged_range`.

### T5.14 Fähigkeit `dig`

- Art: Code · Größe: S · Hängt ab von: T5.08
- Parameter: `dig_hardness` (Standard 1).
- Tun: wie `spec.burrows`, aber nur Material mit `mat.HARDNESS <= dig_hardness`; Zustand `dig` beim Graben. Wegsuche behandelt grabbares Material als frei (Parameter `diggable_hardness` an `find_path` **nicht** ergänzen – stattdessen direkt auf das Ziel zugraben, wenn kein Weg).
- Test: gräbt durch weiches Material, nicht durch hartes.

### T5.15 Fähigkeit `steal`

- Art: Code · Größe: S · Hängt ab von: T5.11
- Tun: bei Berührung: `ctx.events.append(("steal", {"creature": id}))`, setzt `carrying=True`, danach `fleeing`. Bei Tod oder Tritt: Event `("steal_return", ...)`. Was gestohlen wird, entscheidet `Run` (T5.21).
- Test: Ereignis kommt einmal; danach flieht sie.

### T5.16 Fähigkeit `split`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Parameter: `split_threshold` (Standard 0,5 der max. Leben), `split_generations` (2).
- Tun: Leben fällt unter Schwelle → Ereignis `("split", {"key", "x", "y", "generation"})`, Kreatur stirbt ohne Beute. `EnemyManager` erzeugt zwei Kinder mit 60 % Größe (eigene `CreatureSpec` per `dataclasses.replace`).
- Test: Generation 2 teilt sich nicht mehr.

### T5.17 Fähigkeiten `shield`, `armor`, `reflect`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: nur `on_hurt`. `armor`: Schaden ×0,25, wenn `cause` eine durchschlagende Geschossart enthält (Liste `PIERCING` in `behaviour.py`, aus `src/spells.py` die Formen mit Durchschlag übernehmen). `shield`: Treffer aus der Blickrichtung (Skalarprodukt > 0) → 0. `reflect`: Ereignis `("reflect", {...})`, Schaden 0 (Zurückwerfen macht `Run`).
- Test: je ein Fall.

### T5.18 Fähigkeiten `summon`, `stationary`, `transform`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: `summon` nutzt vorhandene `spec.summon*`-Felder als Ereignis `("summon", ...)` statt `self.summons` (alter Pfad bleibt). `stationary`: `wants_move` nie, Geschwindigkeit 0. `transform`: vorhandene Verwandlungs-Technik als Fernangriff mit Ausholen (Lesen: `Run._resolve_polymorphs`).
- Test: je ein Fall.

### T5.19 Haltung `trader` und `passive`

- Art: Code · Größe: S · Hängt ab von: T5.04
- Tun: V1a umsetzen inkl. Ereignis `trader_hurt`; `trader`-Kreaturen bewegen sich nicht und sind nie aggro.
- Test: Treffer erzeugt Ereignis; kein Angriff.

### T5.20 Kreaturen gegeneinander

- Art: Code · Größe: M · Hängt ab von: T5.06, T5.09
- Lesen: `src/projectiles.py` Zeile ~300 (`victim.hurt`)
- Dateien: `src/projectiles.py`, `src/enemies.py`, `tests/test_behaviour.py`
- Tun: Geschosse tragen die Art des Schützen (`owner_species`); trifft ein Einheimischer einen anderer Art → `grudges.add`; `hostile()` erlaubt dann Angriffe untereinander (Ziel = nächste feindliche Kreatur statt Spieler). `source` an `hurt` übergeben.
- Test: Kollateraltreffer → Streit.

### T5.21 Einbau in Run

- Art: Code · Größe: M · Hängt ab von: T5.04, T5.15, T5.16, T5.18, T5.20
- Lesen: V12; in `src/run.py` per grep: `self.enemies.update`, `_on_death`, `summons`
- Dateien: `src/run.py`, `tests/test_run.py`
- Tun:
  1. `Run.emit` und `listeners` laut V12 (ruft `_log`).
  2. Kreatur-Ereignisse aus `EnemyManager` weiterreichen; `summon`, `split`, `steal` (nimmt aktiven Kolben, sonst zufälliges Modul aus dem Rucksack; Rückgabe bei `steal_return`), `reflect` (Geschoss umdrehen) behandeln.
  3. `Run.grudges` speichern/laden.
- Test: Diebin nimmt Kolben, Tod gibt ihn zurück; Speichern/Laden mit Groll.
- Fertig, wenn: T5 im Status von 09 auf erledigt.

## T6 Sprite-Laufzeit

Hängt am Werkzeug G0 (Phase B), weil Testbögen daraus entstehen. Reihenfolge: G0.01–G0.03 → T6.

### T6.01 SheetMeta und load_meta

- Art: Code · Größe: S · Hängt ab von: G0.03
- Lesen: V5; Bibel 01 „Dateiformat“
- Dateien: `src/sprites.py` (neu), `tests/test_sprites.py` (neu), `tests/data/sprites/test_blob.json` (neu, von Hand)
- Test: Laden, fehlende Pflichtfelder → `ValueError`; `find_meta` → `None` bei fehlender Datei.

### T6.02 Animator

- Art: Code · Größe: S · Hängt ab von: T6.01
- Lesen: V5; Bibel 01 „Animation“
- Test: Schleife bei `idle`; `attack` endet mit `done=True` auf letztem Frame; unbekannter Zustand → `idle`.

### T6.03 SheetCache und blit_frame

- Art: Code · Größe: S · Hängt ab von: T6.01
- Lesen: V6
- Dateien: `src/sprite_render.py` (neu), `tests/test_sprite_render.py` (neu; `SDL_VIDEODRIVER=dummy`, wie andere pygame-Tests)
- Test: Pixel an Ankerposition stimmt; `flip` spiegelt.

### T6.04 Leuchtpixel als Lichtquellen

- Art: Code · Größe: S · Hängt ab von: T6.03
- Lesen: V6 `glow_points`; im Licht-Code (`src/rendering.py`, grep `light`) die Stelle, an der Geschosse/Glut Licht beitragen
- Dateien: `src/sprite_render.py`, `src/rendering.py`, Test
- Test: `glow_points` liefert gespiegelte Koordinaten korrekt.

### T6.05 Kreatur zeichnet Bogen, falls vorhanden

- Art: Code · Größe: M · Hängt ab von: T6.02, T6.03, T5.03
- Lesen: `draw_creatures` in `src/rendering.py`
- Dateien: `src/rendering.py`, `src/enemies.py` (Feld `animator: Animator | None`, gesetzt in `__init__` über `find_meta("kreaturen", spec.key)`, sonst `find_meta("bosse", ...)`)
- Tun: `Animator.set_state(creature.state)` je Bild; mit Bogen `blit_frame`, sonst alter Weg; Treffer-Blitzen (weiß) über Maske beibehalten.
- Test: Kreatur ohne Bogen zeichnet wie vorher (Test vorhanden bleibt grün); mit Testbogen wird `blit_frame` aufgerufen (Monkeypatch).

### T6.06 Chain und Tentacle

- Art: Code · Größe: S · Hängt ab von: –
- Lesen: V7
- Dateien: `src/procbody.py` (neu), `tests/test_procbody.py` (neu)
- Test: Abstände zwischen Punkten = `spacing` (±0,5); Tentakel bewegt sich über Zeit.

### T6.07 Legs

- Art: Code · Größe: S · Hängt ab von: T6.06
- Test: Füße bleiben stehen, bis Abstand > `stride`, dann versetzen; Füße landen auf festem Boden.

### T6.08 Testbild

- Art: Code · Größe: S · Hängt ab von: T6.05, T6.07, G0.05
- Dateien: `tools/sprite_demo.py` (neu)
- Tun: rendert 1 einfachen Bogen (aus G0.05) und 1 zusammengesetzten Körper (Chain mit 6 Segmenten) in `build/sprite_demo.png`.
- Fertig, wenn: Nutzer hat das Bild gesehen; T6 im Status von 09 auf erledigt.
