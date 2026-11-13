# Phase A — Fundament (30 atomare S-Karten: `A01`–`A30`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_a.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md).

---

## A01 — Kanonische Proben- & Regions-Schlüssel der 6 MVP-Universen in `catalog.py` angleichen (`V0a`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/universes/catalog.py`, `src/universes/model.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0a`), `src/universes/catalog.py`, `tests/spec/test_phase_a.py` (`-k a01`)
- **Aufgabe:**
  1. Stelle sicher, dass `UNIVERSES` in `src/universes/catalog.py` exakt die **6 MVP-Universen** (`"fleischwelt"`, `"aktenhalde"`, `"glibbria"`, `"kruemelreich"`, `"sporenklub"`, `"abtei"`) enthält (`len(UNIVERSES) == 6`) und `ALL_UNIVERSES` nur diese 6 enthält (Pool-Universen kommen erst in Phase J).
  2. Aktualisiere die `samples`-Tupel (je 2 `probe_*`-Schlüssel pro Universum) und `sample_key` (`samples[0]`) gemäß `V0a` (`("probe_gallenstein", "probe_wucherung")`, `("probe_stempelkissen", "probe_formular")`, `("probe_glibberkern", "probe_brauseperle")`, `("probe_zuckerkristall", "probe_ameisenduft")`, `("probe_leuchtspore", "probe_plattennadel")`, `("probe_glockensplitter", "probe_kerzenstumpf")`).
  3. Stelle sicher, dass die 3 `Region`-Einträge jedes der 6 MVP-Universen exakt die Schlüssel und die Reihenfolge `(regions[0], regions[1], regions[2])` aus der Tabelle in `V0a` tragen und `abtei` in `regions[2]` (`"krypta"`) `params=(("ambient", 0.15), ("current_vx", 28.0))` erhält.
- **Akzeptanzkriterien:**
  - `len(UNIVERSES) == 6`; für alle 6 Universen in `UNIVERSES` beginnen beide Einträge in `u.samples` und `u.sample_key` mit `"probe_"`.
  - `[r.key for r in UNIVERSES[k].regions]` entspricht für alle 6 MVP-Universen exakt der Tabelle in `V0a`.
  - `UNIVERSES["abtei"].regions[2].param("current_vx") == 28.0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a01 -q && uv run pytest --ignore=tests/spec -q`

---

## A02 — `Block.rarity_tier` (`1..3`) & `MODULE_ALIASES` in `src/spells.py` (`V0b`, `V23`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/spells.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0b`), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V23`), `docs/bibel/06-waffen-und-module.md` („Geschosse“, „Aufsätze“, „Zünder“), `src/spells.py`, `tests/spec/test_phase_a.py` (`-k a02`)
- **Aufgabe:**
  1. `Block` hat bereits das Feld `rarity_tier: int = 1`. Ändere **keinen** einzelnen `Block(...)`-Eintrag. Füge direkt unter der Zeile `BLOCKS = BLOCKS + tuple(_families())` ein (mit `import dataclasses` oben in der Datei):

     ```python
     TIER3_BLOCKS: frozenset[str] = frozenset({
         "sprengkern", "knochenbombe", "achterkreis", "dreifach",
         "zielsuche", "kettenfunke", "schwerelos", "blutpreis",
     })


     def _tier(block: Block) -> int:
         if block.key in TIER3_BLOCKS:
             return 3
         return 2 if block.rarity == FAMILY_RARITY else 1


     BLOCKS = tuple(dataclasses.replace(b, rarity_tier=_tier(b)) for b in BLOCKS)
     ```

  2. Ersetze den Platzhalter `blocks_of_tier(tier: int) -> list[str]` (Schlüssel aller Blöcke mit dieser Stufe) und fülle das vorhandene `MODULE_ALIASES` mit einer Zeile je Eintrag der Tabellen „Geschosse“, „Aufsätze“ und „Zünder“ aus Bibel 06: `"<Schlüssel>": "<Bisher>"`. `resolve_block_key` ist schon fertig.
- **Akzeptanzkriterien:**
  - Jeder Eintrag in `BLOCKS.values()` hat `rarity_tier in (1, 2, 3)`.
  - `blocks_of_tier(1)`, `blocks_of_tier(2)` und `blocks_of_tier(3)` sind jeweils nicht leer und disjunkt; ihre Vereinigung umfasst alle `BLOCKS`-Schlüssel.
  - `MODULE_ALIASES` bildet jeden Bibel-06-Schlüssel mit „Bisher“-Eintrag auf einen Schlüssel in `BLOCKS` ab, z. B. `resolve_block_key("flux_funke") == "funke"`; unbekannte Schlüssel bleiben unverändert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a02 -q && uv run pytest --ignore=tests/spec -q`

---

## A03 — `World.take_destroyed_cells()` & `gold_vein`-Zählung in `src/world.py` (`V0c`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/world.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0c`), `src/world.py`, `tests/spec/test_phase_a.py` (`-k a03`)
- **Aufgabe:**
  1. Füge auf `World` in `src/world.py` die Zähler `_destroyed_cells: int = 0` und `_destroyed_gold_vein_cells: int = 0` hinzu.
  2. Erhöhe in `carve_circle` und `explode` bei jeder Umwandlung einer festen Zelle (`MAT_SOLID[old_mat] != 0` und `old_mat != MAT_ID["bedrock"]`) zu Luft/Rauch/Feuer/Funken `_destroyed_cells += 1` und bei `old_mat == MAT_ID["gold_vein"]` zusätzlich `_destroyed_gold_vein_cells += 1`.
  3. Implementiere `take_destroyed_cells(self) -> int` und `take_destroyed_gold_vein_cells(self) -> int`, die jeweils den aktuellen Zählerstand zurückgeben und ihn auf `0` zurücksetzen.
- **Akzeptanzkriterien:**
  - `world.explode(...)` auf Stein- und `"gold_vein"`-Zellen erhöht beide Zähler exakt um die zerstörten Feststoff-Zellen.
  - Ein zweiter unmittelbarer Aufruf von `take_destroyed_cells()` bzw. `take_destroyed_gold_vein_cells()` liefert `0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a03 -q && uv run pytest --ignore=tests/spec -q`

---

## A04 — Proben-Katalog (`src/samples.py`) & Inventar-Proben-Slots (`V11`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/samples.py`, `src/inventory.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `src/inventory.py`, `tests/spec/test_phase_a.py` (`-k a04`)
- **Aufgabe:**
  1. Erstelle `src/samples.py` mit `SAMPLE_SLOTS = 12`, `SAMPLE_STACK = 99`, `Sample`, `SAMPLE_ALIASES` und dem vollständigen Dictionary `SAMPLES` (alle 17 Proben aus `V11`: 12 Universums-Proben + 5 allgemeine Proben).
  2. Ergänze auf `Inventory` in `src/inventory.py` das Feld `samples: list[tuple[str, int] | None]` sowie die Methoden `add_sample`, `sample_count`, `total_samples` und `take_samples` exakt nach `V11`.
- **Akzeptanzkriterien:**
  - Alle 12 Universums-Proben (`u.samples` aus `src/universes/catalog.py`) und die 5 allgemeinen Proben sind in `SAMPLES` enthalten (`len(SAMPLES) == 17`).
  - `add_sample` stapelt bis `99` pro Slot über maximal `12` Slots und gibt die tatsächlich aufgenommene Menge zurück.
  - `take_samples` zieht nur ab, wenn alle geforderten Proben vollständig vorhanden sind (atomare Prüfung).
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a04 -q && uv run pytest --ignore=tests/spec -q`

---

## A05 — Vereinheitlichtes `Pickup`-Schema in `src/loot.py` (`V11`)

- **Größe:** S
- **Abhängigkeiten:** `A04`
- **Ziel-Dateien:** `src/loot.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `src/loot.py`, `tests/spec/test_phase_a.py` (`-k a05`)
- **Aufgabe:**
  1. Erweitere `Pickup` in `src/loot.py` um `kind: str = ""`, `item_key: str = ""`, `amount: int = 0` und implementiere `__post_init__`, sodass alte Konstruktor-Aufrufe (`Pickup(x, y, pearls=5)`, `Pickup(x, y, block="funke")`, `Pickup(x, y, heart=25)`) automatisch `kind`, `item_key`, `amount` setzen und umgekehrt neue Aufrufe (`Pickup(x, y, kind="block", item_key="funke")`, `Pickup(x, y, kind="sample", item_key="probe_gallenstein", amount=2)`, `Pickup(x, y, kind="gold", amount=15)`) die Legacy-Felder synchron halten.
  2. Ergänze eine Hilfsfunktion `pickup_sprite_key(p: Pickup) -> str`, die den Sprite-Schlüssel aus der Tabelle in `V11` liefert.
- **Akzeptanzkriterien:**
  - Alle bestehenden Pickup-Tests laufen unverändert grün.
  - Für alle 18 `kind`-Werte aus `V11` liefert `pickup_sprite_key(p)` den spezifizierten Schlüssel.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a05 -q && uv run pytest --ignore=tests/spec -q`

---

## A06 — Neue Pickup-Arten in `Run._pick_up` & Save/Load (`src/run.py`) (`V11`)

- **Größe:** S
- **Abhängigkeiten:** `A05`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`), `src/run.py` (Zeilen 150–230, 740–797, 1510–1560), `tests/spec/test_phase_a.py` (`-k a06`)
- **Aufgabe:**
  1. Initialisiere auf `Run` in `src/run.py` die neuen Zähler `self.gold: int = 0`, `self.memory_shards: int = 0`, `self.blueprint_shards: int = 0`, `self.badges: int = 0`.
  2. Erweitere `Run._pick_up`, `_pickup_data` und `_pickup_from` um die neuen `Pickup.kind`-Typen (`"gold"`, `"sample"`, `"life_capsule"`, `"memory_shard"`, `"blueprint_shard"`, `"crate"`, `"badge"`, `"formular_stempel"`) gemäß `V11`.
- **Akzeptanzkriterien:**
  - Aufheben von `"gold"` erhöht `run.gold`, Aufheben von `"sample"` legt die Probe in `run.inventory.samples` ab (und lässt sie liegen, falls alle 12 Slots voll sind).
  - `3` eingesammelte `"blueprint_shard"` setzen `run.blueprint_shards` um `3` herab und rufen `records.discover("blueprint", ...)` auf.
  - `_pickup_from(_pickup_data(p))` stellt `kind`, `item_key` und `amount` verlustfrei wieder her.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a06 -q && uv run pytest --ignore=tests/spec -q`

---

## A07 — Gameplay-Ereignisbus `Run.emit` & `Run.listeners` in `src/run.py` (`V12`)

- **Größe:** S
- **Abhängigkeiten:** `A06`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V12`), `src/run.py` (Zeilen 160–240, 820–960, 1510–1560), `tests/spec/test_phase_a.py` (`-k a07`)
- **Aufgabe:**
  1. Ergänze auf `Run` `self.listeners: list[Callable[[str, dict[str, Any]], None]] = []`, `self.emitted_events: list[tuple[str, dict[str, Any]]] = []` und `emit(self, name: str, **data: Any) -> None` gemäß `V12`, ohne `self.events: list[str]` (Audio-Cues) zu verändern.
  2. Leere `self.emitted_events` zu Beginn von `Run.update` und feuere die Basis-Events `"kill"`, `"hurt_player"`, `"pickup"`, `"sample"`, `"gold"`, `"cells_destroyed"` an den entsprechenden Stellen in `Run`.
- **Akzeptanzkriterien:**
  - `run.events` enthält weiterhin ausschließlich Audio-Cue-Strings.
  - Registrierte Funktionen in `run.listeners` empfangen `(name, payload)` mit den Pflicht-Schlüsseln aus `V12`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a07 -q && uv run pytest --ignore=tests/spec -q`

---

## A08 — Neue Status-Timer auf `Body` & Bewegungseffekte in `Player` (`V4b`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/body.py`, `src/player.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4b`), `src/body.py`, `src/player.py`, `tests/spec/test_phase_a.py` (`-k a08`)
- **Aufgabe:**
  1. Füge auf `Body` in `src/body.py` die 13 Timer-Felder aus `V4b` Abschnitt 1 hinzu (`drunk`, `sticky`, `stamped_good`, `stamped_bad`, `marked_time`, `frozen`, `charged`, `befogged`, `refresh_time`, `lubed_time`, `fizzy_time`, `haste_time`, `ink_sight`; jeweils `float = 0.0`) und dekrementiere sie in `Body.step_timers(dt, world)` bis `0.0`.
  2. Ergänze `Body.damage_factor()` laut `V4b` und in `Player.update` (`src/player.py`) die Modifikatoren für `frozen > 0` (keine Bewegung, `0.3×` Fallgeschwindigkeit), `sticky > 0` (`0.55×` Lauf, `0.65×` Sprung), `fizzy_time > 0` (`1.5×` Sprung), `haste_time > 0` (`1.3×` Lauf) und `drunk > 0` (leichtes Wanken).
- **Akzeptanzkriterien:**
  - Alle 13 Timer laufen über `step_timers` sauber bis `0.0` ab.
  - `damage_factor()` ist `1.2` bei `stamped_good`, `0.8` bei `stamped_bad`, sonst `1.0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a08 -q && uv run pytest --ignore=tests/spec -q`

---

## A09 — Die 14 Trink-Schübe aus Bibel 06 in `src/flask.py` (`V4b`)

- **Größe:** S
- **Abhängigkeiten:** `A08`
- **Ziel-Dateien:** `src/flask.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4b`), `docs/bibel/06-waffen-und-module.md` („Flüssigkeiten: Schübe beim Trinken“), `src/flask.py`, `tests/spec/test_phase_a.py` (`-k a09`)
- **Aufgabe:**
  1. Ersetze in `src/flask.py` die Trink-Wirkungen (`DRINK_EFFECTS`, `Flask.drink`) durch genau die 14 Einträge der Tabelle in `V4b` Abschnitt 2. Keine Flüssigkeit heilt; Blut heilt nur mit `blood_heals=True`.
- **Akzeptanzkriterien:**
  - Für jeden der 14 Schlüssel setzt `drink` exakt den Timer bzw. Schaden aus `V4b`, gibt einen nicht leeren deutschen Text zurück und verbraucht einen Schluck.
  - `hp` steigt nach keinem Trank, außer bei `"blood"` mit `blood_heals=True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a09 -q && uv run pytest --ignore=tests/spec -q`

---

## A10 — A*-Pfadsuche für `walk`, `fly` und `swim` (`src/pathfind.py`) (`V3`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/pathfind.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V3`), `src/world.py`, `tests/spec/test_phase_a.py` (`-k a10`)
- **Aufgabe:**
  1. Erstelle `src/pathfind.py` mit `PATH_CACHE_TTL = 0.4`, `MAX_PATH_EXPANSIONS = 160`, `PathCacheEntry`, `find_path(world, start, goal, loco, max_expansions=160)` und `next_waypoint(world, start_px, goal_px, loco, cache, now)` exakt nach `V3`.
  2. Halte dich bei der Passierbarkeit der Knoten und der Rückgabe genau an die Regeln in `V3` (Mittelzelle des Knotens entscheidet; Start- und Zielknoten immer erlaubt; letzter Punkt ist genau das Ziel).
- **Akzeptanzkriterien:**
  - `find_path` umgeht für `"fly"` eine Steinmauer mit Öffnung, findet für `"swim"` Wege durch Wasserbecken und bleibt für `"walk"` auf begehbaren Böden.
  - `find_path` terminiert bei unerreichbarem Ziel nach höchstens `max_expansions` Knoten und gibt den Pfad zum nächstgelegenen besuchten Knoten zurück.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a10 -q && uv run pytest --ignore=tests/spec -q`

---

## A11 — Fraktions-Matrix & Blutfehden (`src/factions.py`) (`V4`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/factions.py`, `src/projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4`), `src/projectiles.py`, `tests/spec/test_phase_a.py` (`-k a11`)
- **Aufgabe:**
  1. Erstelle `src/factions.py` mit den Konstanten `SPIELER` … `BOESE_ICHS`, `UNIVERSE_FACTIONS`, `NATIVE_FACTIONS`, `FACTIONS` (genau 11) und `HATE_MATRIX` **wörtlich aus `V4`** sowie `are_hostile`, `record_grudge` und `hostile` nach den Regeln in `V4`.
  2. Ergänze auf `Projectile` in `src/projectiles.py` die optionalen Felder `owner_species: str = ""` und `source_pos: tuple[float, float] | None = None` (abwärtskompatibel).
- **Akzeptanzkriterien:**
  - `len(FACTIONS) == 11`; Einheimische desselben Universums sind friedlich, verschiedener Universen verfeindet (`are_hostile("pilze", "insekten")`).
  - `are_hostile("behoerde", "spieler")` ist `True`, `are_hostile("behoerde", "boese_ichs")` ist `False`.
  - `are_hostile("haendler", "spieler")` ist ohne Groll `False` und nach `record_grudge(grudges, "haendler", "spieler")` in beide Richtungen `True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a11 -q && uv run pytest --ignore=tests/spec -q`

---

## A12 — `BehaviourContext`, `Ability` & Fähigkeiten Teil 1 (`split`, `morph`, `Reflect`, `steal`, `eat_material`) (`V1`)

- **Größe:** S
- **Abhängigkeiten:** `A05`
- **Ziel-Dateien:** `src/behaviour.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/loot.py`, `src/enemies.py`, `tests/spec/test_phase_a.py` (`-k a12`)
- **Aufgabe:**
  1. Erstelle `src/behaviour.py` mit `PIERCING_FORMS`, `GRAZE_MATERIAL` (inkl. `"blattlaus": "zucker"`), `SPLIT_SIZES`, `Ability` und `BehaviourContext` gemäß `V1`.
  2. Implementiere in `src/behaviour.py` die Verhaltens-Helfer für die ersten 5 Fähigkeiten: `handle_split_on_death`, `handle_morph_check`, `handle_reflect_projectiles`, `handle_steal_pickup` und `handle_eat_material` (inkl. Honig-/Pilz-/Gold-Drop beim Grasen). Nutze nur vorhandene Attribute: `Pickup` (`src/loot.py`) und Kreaturen (`src/enemies.py`) haben `x` und `y` in Weltpixeln; Abstände mit `math.hypot` berechnen. Erfinde keine Methoden wie `distance_to`.
- **Akzeptanzkriterien:**
  - `handle_split_on_death` erzeugt ein `"split"`-Event für `generation < 2` und keines für `generation >= 2`.
  - `handle_reflect_projectiles` kehrt feindliche Projektile (`form not in PIERCING_FORMS`) im Radius `24 px` um und setzt `from_player = True`.
  - `handle_steal_pickup` nimmt ein nahes Gold-/Proben-Pickup in `creature.carrying` auf; `handle_eat_material` wandelt 1 Nachbarzelle aus `GRAZE_MATERIAL` in Luft um und heilt die Kreatur.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a12 -q && uv run pytest --ignore=tests/spec -q`

---

## A13 — Verhaltens-Fähigkeiten Teil 2 (`aura`, `teleport`, `summon`, `kamikaze`, `burrow`, `chorus`) (`V1`, `V0d`)

- **Größe:** S
- **Abhängigkeiten:** `A12`
- **Ziel-Dateien:** `src/behaviour.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/behaviour.py`, `tests/spec/test_phase_a.py` (`-k a13`)
- **Aufgabe:**
  1. Ergänze in `src/behaviour.py` die Helfer für die restlichen 5 Fähigkeiten (`handle_aura`, `handle_teleport`, `handle_summon`, `handle_kamikaze`, `handle_burrow`) sowie den `moenchsfisch`-Chor-Bonus (`apply_chorus_buff` für `>= 3` `"moenchsfisch"` im Radius `90 px` gemäß `V0d`) und die Dispatcher-Funktion `tick_abilities(creature, ctx)`.
- **Akzeptanzkriterien:**
  - `handle_aura` trägt den konfigurierten Statuseffekt (`"slow"`, `"poison"`, `"heal_allies"`, `"stamp_tax"`, `"shock"`) im Radius `param_float` auf Ziele auf.
  - `handle_teleport` versetzt die Kreatur auf eine freie Luftzelle in `40..110 px` Abstand.
  - `handle_kamikaze` zündet bei Distanz `<= 16 px` eine Explosion und setzt `creature.body.hp = 0`.
  - `apply_chorus_buff` erhöht ab 3 nahen `"moenchsfisch"` deren Projektil-Schaden um `+50 %`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a13 -q && uv run pytest --ignore=tests/spec -q`

---

## A14 — Erweiterte `CreatureSpec`, `Creature`-Felder & Haltungen (`V1a`, `V1b`, `V1c`)

- **Größe:** S
- **Abhängigkeiten:** `A11`, `A13`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1a`, `V1b`, `V1c`), `src/enemies.py` (Zeilen 1–260), `tests/spec/test_phase_a.py` (`-k a14`)
- **Aufgabe:**
  1. Erweitere `CreatureSpec` in `src/enemies.py` mit sicheren Default-Werten um `stance: str = "hostile"`, `faction: str = "wildnis"`, `abilities: tuple[Ability, ...] = ()`, `windup_time: float = 0.25`, `recover_time: float = 0.20`, `weak_material: str = ""`, `resist_material: str = ""`, `drops_sample: str = ""`, `sample_chance: float = 0.35`, `is_mid_boss: bool = False`.
  2. Erweitere `Creature` um die Laufzeitfelder aus `V1c` (`state`, `state_timer`, `aggro`, `group_id`, `home`, `generation`, `carrying`, `morphed`, `bribed`, `giver`, `ability_cooldowns`, `path_cache`, `anim_state`, `anim_time`, `pending_shot`) sowie eine Hilfsfunktion `evaluate_stance(creature, ctx) -> bool`, die nach `V1a` entscheidet, ob die Kreatur angreift, flieht (`"flee"`) oder friedlich bleibt (`"idle"`/`"patrol"`), inklusive Gruppen-Aggro über `group_id` und `bribed == True`.
- **Akzeptanzkriterien:**
  - Eine `"peaceful"`-Kreatur ohne `aggro` greift nicht an; nach Schaden wird `aggro = True` für alle Kreaturen derselben `group_id` im Radius `140 px` gesetzt.
  - Eine `"shy"`-Kreatur wechselt bei Spieler-Distanz `< 90 px` in `"flee"`.
  - Eine `"territorial"`-Kreatur mit `bribed == True` greift den Spieler nicht an.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a14 -q && uv run pytest --ignore=tests/spec -q`

---

## A15 — Kreaturen-Zustandsmaschine, Telegrafie & Fraktionskampf in `EnemyManager.update` (`V2`, `V1c`)

- **Größe:** S
- **Abhängigkeiten:** `A10`, `A14`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1c`, `V2`), `src/enemies.py` (Zeilen 250–545), `tests/spec/test_phase_a.py` (`-k a15`)
- **Aufgabe:**
  1. Implementiere in `src/enemies.py` `begin_attack(creature, target)` und `poll_attack_ready(creature, dt)` für den Ablauf `"windup"` → `"attack"` → `"recover"` gemäß `V2`.
  2. Erweitere `EnemyManager.update` rückwärtskompatibel um `*, grudges: set[tuple[str, str]] | None = None, on_beat: bool = True, out_events: list[tuple[str, dict[str, object]]] | None = None` gemäß `V1c`: Kreaturen wählen als Ziel den nächsten feindlichen Akteur (Spieler oder verfeindete Kreatur laut `are_hostile`), nutzen `tick_abilities` und verzögern ihren Schuss über `begin_attack`/`poll_attack_ready`.
- **Akzeptanzkriterien:**
  - Alle bestehenden Aufrufe `enemies.update(dt, world, player, projectiles)` ohne Keyword-Argumente laufen weiterhin fehlerfrei.
  - Vor jedem Schuss durchläuft eine Kreatur für `spec.windup_time` Sekunden den Zustand `"windup"`.
  - Zwei Kreaturen verfeindeter Fraktionen (`"pilze"` vs. `"insekten"`) bekämpfen sich gegenseitig.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a15 -q && uv run pytest --ignore=tests/spec -q`

---

## A16 — Kreaturen-Sonderinteraktionen in `Run` (`tuersteherpilz`-Bestechung & `blattlaus`-Melken) (`V0d`)

- **Größe:** S
- **Abhängigkeiten:** `A07`, `A15`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/run.py`, `tests/spec/test_phase_a.py` (`-k a16`)
- **Aufgabe:**
  1. Ergänze in `Run` (`src/run.py`) beim Kick (`_kick`): Trifft der Kick eine lebende Kreatur mit `c.spec.giver == True` (z. B. `"blattlaus"`), stirbt sie nicht und nimmt keinen Schaden, sondern spawnt bei `c.ability_cooldowns.get("milk", 0.0) <= 0.0` `4` Pixel `"honey"` (bzw. ein kleines Heil-/Honig-Tröpfchen) und setzt den Cooldown `"milk"` auf `8.0 s`.
  2. Ergänze eine Methode `Run.try_interact_creature(self) -> bool` (aufgerufen bei `[E]`): Steht eine nicht-feindliche `"tuersteherpilz"`-Kreatur (`bribed == False`) innerhalb von `32 px` und hat die Spielerin `self.gold >= 20`, zieht dies `20` Gold ab, setzt `c.bribed = True`, `c.aggro = False` und feuert `self.emit("bribe", species=c.species, cost=20)`.
- **Akzeptanzkriterien:**
  - Kick auf eine Kreatur mit `giver=True` spawnt `"honey"` in der Welt und setzt `ability_cooldowns["milk"] = 8.0`.
  - `try_interact_creature()` bei `"tuersteherpilz"` und `gold >= 20` reduziert `gold` um `20` und setzt `bribed = True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a16 -q && uv run pytest --ignore=tests/spec -q`

---

## A17 — Sprite-Metadaten & `Animator` (`src/sprites.py`) (`V5`, `V0d`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `tests/spec/test_phase_a.py` (`-k a17`)
- **Aufgabe:**
  1. Erstelle `src/sprites.py` mit `AnimSpec`, `GlowPoint`, `SheetMeta`, `load_sheet_meta(json_path: Path) -> SheetMeta` und `Animator` (`play`, `update`, `frame_rect`) exakt nach `V5` und dem JSON-Schema aus `V0d`.
- **Akzeptanzkriterien:**
  - `load_sheet_meta` liest `frame_size`, `anchor`, `anims` und `glow` (als Liste von Dicts) fehlerfrei ein.
  - `Animator.update(dt)` schaltet bei `loop=True` zyklisch durch die Frames und hält bei `loop=False` auf dem letzten Frame (`finished == True`) an, bis `next_anim` übernimmt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a17 -q && uv run pytest --ignore=tests/spec -q`

---

## A18 — `SheetCache`, `blit_frame` & `glow_points` (`src/sprite_render.py`) (`V6`)

- **Größe:** S
- **Abhängigkeiten:** `A17`
- **Ziel-Dateien:** `src/sprite_render.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V6`), `src/sprites.py`, `tests/spec/test_phase_a.py` (`-k a18`)
- **Aufgabe:**
  1. Erstelle `src/sprite_render.py` mit `ASSET_ROOT`, `SheetCache`, `blit_frame` (inkl. Horizontalspiegelung bei `flip_x`, Rotation bei `angle_deg != 0.0`, weißem Flash-Overlay bei `flash > 0.0` und Farbton-Multiplikation bei `tint`) sowie `glow_points(meta, world_x, world_y, flip_x=False)` gemäß `V6`.
  2. Falls eine PNG/JSON-Datei noch nicht auf der Platte existiert, liefert `SheetCache.get(category, name)` ein deterministisches Fallback-Surface (`16×16` transparent mit sichtbarem Umriss) + Standard-`SheetMeta`, damit Headless-Tests niemals wegen fehlender Assets abstürzen.
- **Akzeptanzkriterien:**
  - `blit_frame` zeichnet ein Test-Sheet korrekt an `(world_x - cam_x, world_y - cam_y)` unter Berücksichtigung von `anchor` und `flip_x`.
  - `glow_points` spiegelt die X-Offsets bei `flip_x=True` exakt um den Ankerpunkt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a18 -q && uv run pytest --ignore=tests/spec -q`

---

## A19 — Prozedurale Glieder: `Chain`, `Legs` & `Tentacle` (`src/procbody.py` Teil 1) (`V7`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`), `tests/spec/test_phase_a.py` (`-k a19`)
- **Aufgabe:**
  1. Erstelle `src/procbody.py` und implementiere den ersten Teil von `V7`:
     - `Chain`: Segmente mit festem Abstand `spacing`, die dem Kopf `(head_x, head_y)` weich folgen.
     - `Legs`: `count` Beinpaare mit Dreiecks-/Bogen-Schrittzyklus (`step_height`, `stride`), die `(hip_x, hip_y, foot_x, foot_y)`-Tupel liefern.
     - `Tentacle`: `segments`-gliedriger Sinusbogen mit Phasenverschiebung `phase` und Amplitude `amp`.
- **Akzeptanzkriterien:**
  - `Chain.update` hält den euklidischen Abstand benachbarter Segmente auf `<= spacing + 1e-4`.
  - `Legs.update` liefert genau `count` Bein-Tupel; bei `vx != 0` modulieren die Fußpunkte vertikal um bis zu `step_height`.
  - `Tentacle.points` liefert `segments + 1` Punkte beginnend bei `(root_x, root_y)`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a19 -q && uv run pytest --ignore=tests/spec -q`

---

## A20 — Mehrteilige Körper: `PartSpec`, `PartLayout` & `ProcRig` (`src/procbody.py` Teil 2) (`V7`)

- **Größe:** S
- **Abhängigkeiten:** `A19`
- **Ziel-Dateien:** `src/procbody.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V7`), `src/procbody.py`, `tests/spec/test_phase_a.py` (`-k a20`)
- **Aufgabe:**
  1. Ergänze in `src/procbody.py` `PartSpec`, `PartLayout` und `ProcRig` (`update`, `world_parts`, `recoil`, `destroy_part`) gemäß `V7`.
  2. Implementiere außerdem einen Katalog `RIG_LAYOUTS: dict[str, PartLayout]` für mehrteilige Bosse und Großkreaturen (mit einem Default-Fallback-Layout aus `"rumpf"` + `"kopf"`).
- **Akzeptanzkriterien:**
  - `ProcRig.world_parts` sortiert die Teile aufsteigend nach `z_order` und spiegelt `offset_x` bei `flip_x=True`.
  - `destroy_part("arm_links")` blendet dieses Teil in `world_parts` aus; `recoil("kopf", 3.0)` versetzt das Teil temporär und klingt über `update(dt, ...)` wieder auf `0` ab.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a20 -q && uv run pytest --ignore=tests/spec -q`

---

## A21 — Farbpaletten & Shading-Helfer (`tools/palette.py`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `tools/palette.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8`), `src/universes/catalog.py`, `tests/spec/test_phase_a.py` (`-k a21`)
- **Aufgabe:**
  1. Erstelle `tools/palette.py` mit `OUTLINE_DARK = (18, 14, 24, 255)`, `PaletteRamp` (`shadow`, `mid`, `light`, `highlight`, `rim`), `make_ramp(base_rgb: tuple[int, int, int]) -> PaletteRamp`, `UNIVERSE_PALETTES: dict[str, dict[str, PaletteRamp]]` für alle 6 MVP-Universen (`"fleischwelt"`, `"aktenhalde"`, `"glibbria"`, `"kruemelreich"`, `"sporenklub"`, `"abtei"`) + Pool-Universen sowie `ENTITY_PALETTES` für Spielerin, Klonita, Behörde und Händler gemäß `V8`.
- **Akzeptanzkriterien:**
  - Für jedes der 6 MVP-Universen in `UNIVERSES` existieren in `UNIVERSE_PALETTES` mindestens die Rampen `"primary"`, `"secondary"`, `"accent"` und `"glow"`.
  - In jeder `PaletteRamp` steigt die Helligkeit streng monoton von `shadow` über `mid` und `light` bis `highlight`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a21 -q && uv run pytest --ignore=tests/spec -q`

---

## A22 — Prozedurales Sprite-Framework & JSON-Exporter (`tools/sprites.py`) (`V8`)

- **Größe:** S
- **Abhängigkeiten:** `A17`, `A21`
- **Ziel-Dateien:** `tools/sprites.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V5`, `V8`), `tools/palette.py`, `tests/spec/test_phase_a.py` (`-k a22`)
- **Aufgabe:**
  1. Erstelle `tools/sprites.py` mit einem leichtgewichtigen, Pygame-kompatiblen Pixel-Canvas (`PixelCanvas`), Zeichen-Primitiven (`draw_shaded_ellipse`, `draw_shaded_rect`, `draw_segment_line`, `apply_dark_outline`, `add_dither`), der Sheet-Bau-Hilfe `save_sheet(category, name, frames, *, anchor, anims, glow=(), out_dir=ASSET_ROOT)` (schreibt `<name>.png` + `<name>.json`) und dem CLI-Einstiegspunkt `build_all(out_dir: Path = ASSET_ROOT) -> list[Path]`.
- **Akzeptanzkriterien:**
  - `apply_dark_outline` umrandet alle nicht-transparenten Pixel sauber mit `OUTLINE_DARK`.
  - Ein mit `save_sheet` geschriebenes Paar aus `.png` und `.json` lässt sich direkt über `load_sheet_meta` (`src/sprites.py`) einlesen und hat `> 20 %` nicht-transparente Pixel sowie `>= 5` verschiedene Farben im ersten Frame.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a22 -q && uv run pytest --ignore=tests/spec -q`

---

## A23 — Modulare Waffenteile & Slot-Layout (`src/weapon_parts.py`) (`V8b`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/weapon_parts.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v05-sprites-und-teile.md` (`V8b`), `docs/bibel/06-waffen-und-module.md` („Aussehen aus Teilen“), `src/wand.py` (`WandSpec`), `tests/spec/test_phase_a.py` (`-k a23`)
- **Aufgabe:**
  1. Implementiere in `src/weapon_parts.py` `parts_for(wand)` und `layout_for(wand)` nach der Regel-Tabelle in `V8b` (`WEAPON_PART_KEYS` und `PART_ORDER` stehen schon im Gerüst).
- **Akzeptanzkriterien:**
  - `parts_for` liefert genau 6 Teile, je eins pro Gruppe in `PART_ORDER`, alle aus `WEAPON_PART_KEYS`, gewählt nach den Schwellen in `V8b`.
  - `layout_for` liefert die Teile in derselben Reihenfolge mit streng aufsteigendem `offset_x`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a23 -q && uv run pytest --ignore=tests/spec -q`

---

## A24 — `Level`-Datenstruktur & `Run._mirror_level` erweitern (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A01`
- **Ziel-Dateien:** `src/worldgen.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/worldgen.py` (Zeilen 1–40), `src/run.py` (Zeilen 495–525), `tests/spec/test_phase_a.py` (`-k a24`)
- **Aufgabe:**
  1. Erweitere `Level` in `src/worldgen.py` mit Default-Werten um `universe_key: str = "fleischwelt"`, `mid_boss_arena: tuple[int, int, int, int] = (0, 0, 0, 0)`, `boss_arena: tuple[int, int, int, int] = (0, 0, 0, 0)`, `trader_nook: tuple[int, int, int, int] | None = None`, `challenge_shrine: tuple[int, int, int, int] | None = None`, `regions: list[tuple[str, tuple[int, int, int, int]]] = field(default_factory=list)` und `destructible_props: list[tuple[str, int, int]] = field(default_factory=list)` gemäß `V9`.
  2. Aktualisiere `Run._mirror_level` in `src/run.py`, sodass alle neuen `(x0, y0, x1, y1)`-Rechtecke (`arena`, `secret`, `vault`, `mid_boss_arena`, `boss_arena`, `trader_nook`, `challenge_shrine`, `regions`) sowie `destructible_props` horizontal an `w = self.world.width` gespiegelt werden (`(w - 1 - x1, y0, w - 1 - x0, y1)`).
- **Akzeptanzkriterien:**
  - Bestehende `Level(...)`-Aufrufe mit nur 5 Positions-Argumenten funktionieren unverändert.
  - `Run._mirror_level` erhält für jedes Rechteck die Invariante `x0 < x1` und spiegelt `destructible_props` auf `(w - 1 - x, y)`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a24 -q && uv run pytest --ignore=tests/spec -q`

---

## A25 — Generator-Dispatcher & Topologie-Helfer (`src/universes/gen/`) (`V9`)

- **Größe:** S
- **Abhängigkeiten:** `A24`
- **Ziel-Dateien:** `src/universes/gen/__init__.py`, `src/universes/gen/common.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/worldgen.py`, `tests/spec/test_phase_a.py` (`-k a25`)
- **Aufgabe:**
  1. Erstelle `src/universes/gen/common.py` mit den gemeinsamen Geometrie- und Platzierungshelfern aus `V9`: `region_bands(width, height, topology)` (für `"vertical"`, `"horizontal"`, `"concentric"`, `"columns"`, `"top_split"`, `"islands"`), `carve_room`, `carve_tunnel`, `fill_basin`, `place_trader_nook`, `place_challenge_shrine`, `place_boss_arenas` und `scatter_props`.
  2. Erstelle `src/universes/gen/__init__.py` mit `GENERATORS: dict[str, Callable[[World, Universe, int, int], Level]]` und `generate_universe(world, universe, depth, seed) -> Level` (nutzt registrierte Generatoren oder einen sauberen Fallback über `common.py`, bis alle 9 Spezial-Generatoren in Phase D eingehängt sind).
- **Akzeptanzkriterien:**
  - `region_bands(960, 540, topology)` liefert für alle 6 Topologie-Arten genau 3 gültige `(x0, y0, x1, y1)`-Rechtecke innerhalb der Weltgrenzen.
  - `place_boss_arenas`, `place_trader_nook` und `place_challenge_shrine` schneiden begehbare Luftkammern frei und geben gültige `(x0, y0, x1, y1)`-Rechtecke zurück.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a25 -q && uv run pytest --ignore=tests/spec -q`

---

## A26 — Regionen-Erkennung & Strömungsregel (`current_vx`) in `Run` (`V0d`, `V9`)

- **Größe:** S
- **Abhängigkeiten:** `A01`, `A25`
- **Ziel-Dateien:** `src/rules.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V9`), `src/rules.py`, `src/run.py` (Zeilen 460–510, 820–880), `tests/spec/test_phase_a.py` (`-k a26`)
- **Aufgabe:**
  1. Erweitere `apply_player_rules` in `src/rules.py` um das optionale Keyword-Argument `region: Region | None = None`: Wenn `region is not None`, wende `current_vx = region.param("current_vx", 0.0)` bei `player.in_liquid(world)` als horizontale Zusatzbeschleunigung `player.body.vx += current_vx * dt * 3.0` an.
  2. Aktualisiere `Run._region_at(x, y)` in `src/run.py`, sodass zuerst `self.level.regions` (`(region_key, (x0, y0, x1, y1))`) geprüft wird und – falls kein Treffer vorliegt – auf das bisherige Drittel-Verhalten zurückgefallen wird.
- **Akzeptanzkriterien:**
  - In der Region `"krypta"` (`abtei`) erfährt eine Spielerin im Wasser eine positive Horizontalbeschleunigung durch `current_vx == 28.0`.
  - `Run._region_at` findet über `level.regions` auch für `"horizontal"`-, `"concentric"`- und `"islands"`-Topologien die korrekte `Region`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a26 -q && uv run pytest --ignore=tests/spec -q`

## A27 — Die 8 neuen Füllungen aus Bibel 06 in `src/spells.py` (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/spells.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`), `docs/bibel/06-waffen-und-module.md` („Füllungen“), `tests/spec/test_phase_a.py` (`-k a27`), `tests/test_spells.py` (`test_category_fields_are_consistent`)
- **Aufgabe:**
  1. Ergänze auf `Block` die Felder `from_flask: bool = False` und `local_material: bool = False` und lege die 8 neuen Füllungen aus der Tabelle in `V0e` an (Mana und Werte wie die vorhandenen `sekret_*`-Blöcke, Beschreibung aus Bibel 06). Trage `fuellung_feuer` und `fuellung_rauch` als Aliase in `MODULE_ALIASES` ein.
- **Akzeptanzkriterien:**
  - Alle 10 Bibel-Füllungen lassen sich über `resolve_block_key` als `Category.PAYLOAD`-Block finden; die 6 Material-Füllungen tragen das Material aus `V0e`.
  - `fuellung_kolben` hat `material=None` und `from_flask=True`, `fuellung_lokal` hat `material=None` und `local_material=True`. Der Bestandstest `tests/test_spells.py` (`test_category_fields_are_consistent`) lässt das bereits zu – nicht ändern, nur grün halten.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a27 -q && uv run pytest --ignore=tests/spec -q`

---

## A28 — Sonderfüllungen „Kolbenfüllung“ & „Lokalkolorit“ (`resolve_payload_material`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A27`
- **Ziel-Dateien:** `src/spells.py`, `src/wand.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`), `src/wand.py`, `src/flask.py`, `tests/spec/test_phase_a.py` (`-k a28`)
- **Aufgabe:**
  1. Implementiere `resolve_payload_material` in `src/spells.py` laut `V0e` und rufe sie in `src/wand.py` beim Zusammenstellen eines Schusses statt `block.material` auf (Kolben in der Hand und aktiver Materialsatz werden durchgereicht).
     *(Plan-Korrektur 2026-11-07: Das Material wird nicht in `src/wand.py`, sondern in `src/projectiles.py` gelesen. Der Einbau in den Schuss ist deshalb Karte `A30`; A28 liefert nur die Funktion.)*
- **Akzeptanzkriterien:**
  - Kolbenfüllung liefert das Kolbenmaterial und verbraucht 10 Zellen; ohne Kolben `"water"`.
  - Lokalkolorit liefert ein Universumsmaterial des aktiven Satzes, nie ein Grundmaterial.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a28 -q && uv run pytest --ignore=tests/spec -q`

---

## A29 — Organische Alt-Füllungen: 3 behalten, 9 ausmustern (`Block.retired`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A02`
- **Ziel-Dateien:** `src/spells.py`, `src/loot.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`, „Organische Alt-Füllungen“), `docs/bibel/06-waffen-und-module.md` („Organische Füllungen“), `tests/spec/test_phase_a.py` (`-k a29`)
- **Aufgabe:**
  1. Ergänze `Block.retired: bool = False`, setze es bei den 9 Blöcken aus der Tabelle und gib `sekret_blut`, `sekret_saeure`, `sekret_glut` Namen und Beschreibung aus Bibel 06. Lass `blocks_of_tier` (`src/spells.py`) und `random_block` (`src/loot.py`) `retired`-Blöcke überspringen.
- **Akzeptanzkriterien:**
  - Die 9 ausgemusterten Blöcke stehen weiter in `BLOCKS`, kommen aber in 2000 Zügen von `random_block` und in `blocks_of_tier` nie vor; die 3 behaltenen kommen weiter vor.
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a29 -q && uv run pytest --ignore=tests/spec -q`

---

## A30 — Sonderfüllungen im echten Schuss (`ProjectileSystem.payload_resolver`) (`V0e`)

- **Größe:** S
- **Abhängigkeiten:** `A28`
- **Ziel-Dateien:** `src/projectiles.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0e`, „Sonderfüllungen“), `src/projectiles.py` (`build`, `ProjectileSystem.__init__`, `ProjectileSystem.spawn`), `src/run.py` nur `Run.__init__` (Zeile mit `self.projectiles = ProjectileSystem()`) und `Run._cast` – die Datei ist sehr groß, gezielt suchen und gezielt ändern, `tests/spec/test_phase_a.py` (`-k a30`)
- **Aufgabe:**
  1. `src/projectiles.py`: `build(shot, x, y, angle, team=PLAYER_TEAM, resolve=None)` bekommt den optionalen Parameter `resolve: Callable[[Block], str | None] | None`. In der Schleife über `shot.modifiers` gilt `key = resolve(block) if resolve is not None else block.material`; ist `key` nicht `None`, wird `material = mat.id_of(key)`.
  2. `ProjectileSystem.__init__` legt `self.payload_resolver: Callable[[Block], str | None] | None = None` an. `spawn` reicht ihn nur bei `team == PLAYER_TEAM` an `build` weiter (Kreaturen leeren nie den Kolben der Spielerin).
  3. `src/run.py`: Neue Methode `Run._resolve_payload(self, block) -> str | None`, die `resolve_payload_material(block, self.flask, tuple(mat.KEYS), mat.BASE_KEYS, self.rng)` zurückgibt. Direkt nach `self.projectiles = ProjectileSystem()` in `Run.__init__`: `self.projectiles.payload_resolver = self._resolve_payload`.
- **Akzeptanzkriterien:**
  - Ein Schuss der Spielerin mit Kolbenfüllung trägt das Kolbenmaterial und verbraucht `FLASK_PAYLOAD_CELLS`; ohne Kolben trägt er `"water"`.
  - Ein Kreaturen-Schuss mit Kolbenfüllung verändert den Kolben nicht.
  - Lokalkolorit liefert ein Material des aktiven Satzes, das kein Grundmaterial ist (gibt es keins: `"water"`).
- **Verifikation:** `uv run pytest tests/spec/test_phase_a.py -k a30 -q && uv run pytest --ignore=tests/spec -q`

---
