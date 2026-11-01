# Phase C — Kreaturen, Bosse & Agenten-Grundkörper (17 atomare S-Karten: `C01`–`C17`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien + `1` Testdatei, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md). Alle Kreaturen-Einträge folgen `V1`–`V4` aus [v01-verhalten-und-wegsuche.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v01-verhalten-und-wegsuche.md) und `V0d` aus [v00-migration-und-schluessel.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v00-migration-und-schluessel.md).

---

## C01 — Kreaturen Universum 1 (`schrott`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `A15`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/bibel/05-kreaturen-und-ki.md`, `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `schrott` (`faction="schrott"`, `drops_sample="probe_rost"`):
     - `"rostkaefer"` (`walk`, `territorial`, `Ability("eat_material", "rust")`)
     - `"schweissimp"` (`fly`, `hostile`, Feuer-Schuss, `Ability("teleport", "fire")`)
     - `"magnetwurm"` (`walk`, `hostile`, `Ability("burrow", "")`)
     - `"schrottgolem"` (`walk`, `territorial`, `Ability("reflect", "shield")`)
- **Akzeptanzkriterien:**
  - Alle 4 `schrott`-Spezies aus `UNIVERSES["schrott"].creatures` sind in `SPECIES` vorhanden, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 60 Simulations-Ticks in `EnemyManager.update` ohne Fehler.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k schrott -q && uv run pytest -q`

---

## C02 — Kreaturen Universum 2 (`myzel`: 4 Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C01`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `myzel` (`faction="pilze"`, `drops_sample="probe_pilz"`):
     - `"sporenwerfer"` (`walk`, `hostile`, Sporen-Schuss, `Ability("aura", "poison", 36.0)`)
     - `"leuchtmotte"` (`fly`, `peaceful`, `Ability("aura", "heal_allies", 44.0)`)
     - `"kappenschleicher"` (`walk`, `shy`, `Ability("split", "myzel")`)
     - `"tuersteherpilz"` (`walk`, `territorial`, hohe HP, bestechbar für 20 Gold gemäß `V0d`)
- **Akzeptanzkriterien:**
  - Alle 4 `myzel`-Spezies aus `UNIVERSES["myzel"].creatures` existieren in `SPECIES` mit den spezifizierten Haltungen und Fähigkeiten.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k myzel -q && uv run pytest -q`

---

## C03 — Kreaturen Universum 3 (`magen`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C02`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `magen` (`faction="parasiten"`, `drops_sample="probe_saft"`):
     - `"saeurespucker"` (`walk`, `hostile`, Säure-Bogenschuss, immun gegen Säure)
     - `"zottenwurm"` (`swim`, `territorial`, `Ability("eat_material", "flesh")`)
     - `"gallenblase"` (`fly`, `hostile`, `Ability("kamikaze", "acid", 16.0)`)
     - `"bandwurm_kopf"` (`walk`, `hostile`, `Ability("split", "worm")`)
- **Akzeptanzkriterien:**
  - Alle 4 `magen`-Spezies aus `UNIVERSES["magen"].creatures` existieren in `SPECIES` und funktionieren im 60-Tick-Simulationstest.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k magen -q && uv run pytest -q`

---

## C04 — Kreaturen Universum 4 (`amt`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C03`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `amt` (`faction="behoerde"`, `drops_sample="probe_papier"`):
     - `"stempelkaefer"` (`walk`, `territorial`, Stempel-Nahkampf, `Ability("aura", "stamp_tax", 32.0)`)
     - `"aktenfresser"` (`walk`, `peaceful`, `Ability("eat_material", "paper")`)
     - `"paragraphenreiter"` (`fly`, `hostile`, Paragraphen-Strahl, `Ability("summon", "stempelkaefer", 2.0)`)
     - `"kaffeegolem"` (`walk`, `territorial`, verschießt heißen Dampf/Schlamm, `Ability("morph", "enraged", 0.5)`)
- **Akzeptanzkriterien:**
  - Alle 4 `amt`-Spezies aus `UNIVERSES["amt"].creatures` existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k amt -q && uv run pytest -q`

---

## C05 — Kreaturen Universum 5 (`kuchen`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C04`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `kuchen` (`faction="backwerk"`, `drops_sample="probe_zucker"`):
     - `"zuckerspinne"` (`walk`, `hostile`, verschießt klebrigen Sirup, `Ability("aura", "slow", 30.0)`)
     - `"kerzenkobold"` (`walk`, `hostile`, Feuerball-Schuss, `Ability("kamikaze", "fire", 14.0)`)
     - `"marzipanschwein"` (`walk`, `shy`, `Ability("eat_material", "dough")`)
     - `"baiser_geist"` (`fly`, `territorial`, `Ability("teleport", "blink")`)
- **Akzeptanzkriterien:**
  - Alle 4 `kuchen`-Spezies aus `UNIVERSES["kuchen"].creatures` existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k kuchen -q && uv run pytest -q`

---

## C06 — Kreaturen Universum 6 (`abtei`: 4 Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C05`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `abtei` (`faction="tiefsee"`, `drops_sample="probe_salz"`):
     - `"moenchsfisch"` (`swim`, `territorial`, Schall-Projektil, profitiert ab 3 Fischen vom Chor-Buff gemäß `V0d`)
     - `"glockenqualle"` (`swim`, `peaceful`, `Ability("aura", "shock", 36.0)`)
     - `"korallenwaechter"` (`walk`, `territorial`, `Ability("reflect", "shell")`)
     - `"weihrauch_aal"` (`swim`, `hostile`, `Ability("burrow", "sand")`)
- **Akzeptanzkriterien:**
  - Alle 4 `abtei`-Spezies aus `UNIVERSES["abtei"].creatures` existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k abtei -q && uv run pytest -q`

---

## C07 — Kreaturen Universum 7 (`ameisen`: 4 Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C06`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `ameisen` (`faction="insekten"`, `drops_sample="probe_harz"`):
     - `"arbeiterameise"` (`walk`, `territorial`, Gruppen-Aggro, `Ability("steal", "gold")`)
     - `"ameisensoldat"` (`walk`, `hostile`, starker Biss + Säure-Schuss, `Ability("morph", "guard", 0.5)`)
     - `"harzspucker"` (`walk`, `hostile`, klebriger Harz-Schuss, `Ability("aura", "slow", 32.0)`)
     - `"blattlaus"` (`walk`, `peaceful`, `Ability("eat_material", "sugar")`, setzt beim Spawn `giver = True` gemäß `V0d`)
- **Akzeptanzkriterien:**
  - Alle 4 `ameisen`-Spezies aus `UNIVERSES["ameisen"].creatures` existieren in `SPECIES`; eine gespawnte `"blattlaus"` hat `giver == True`.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k ameisen -q && uv run pytest -q`

---

## C08 — Kreaturen Universum 8 (`spule`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C07`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `spule` (`faction="automaten"`, `drops_sample="probe_spule"`):
     - `"funkenhornisse"` (`fly`, `hostile`, schneller Blitz-Schuss, `Ability("teleport", "spark")`)
     - `"spulenkrabbe"` (`walk`, `territorial`, `Ability("reflect", "magnetic")`)
     - `"kupferschlange"` (`walk`, `hostile`, `Ability("aura", "shock", 38.0)`)
     - `"kondensator_geist"` (`fly`, `hostile`, `Ability("kamikaze", "spark", 18.0)`)
- **Akzeptanzkriterien:**
  - Alle 4 `spule`-Spezies aus `UNIVERSES["spule"].creatures` existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k spule -q && uv run pytest -q`

---

## C09 — Kreaturen Universum 9 (`glibber`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C08`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_creatures_catalog.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen für `glibber` (`faction="zirkus"`, `drops_sample="probe_bunt"`):
     - `"quallenhund"` (`walk`, `hostile`, Glibber-Sprung, `Ability("split", "jelly")`)
     - `"zuckerwatte_wolke"` (`fly`, `shy`, `Ability("aura", "slow", 40.0)`)
     - `"trampolin_frosch"` (`walk`, `territorial`, reflektiert von oben kommende Projektile, `Ability("reflect", "bounce")`)
     - `"konfetti_kanone"` (`walk`, `hostile`, Salven-Schuss im Takt)
- **Akzeptanzkriterien:**
  - Alle 36 Kreaturen-Schlüssel aus `[c.species for u in UNIVERSES.values() for c in u.creatures]` sind vollständig in `SPECIES` registriert.
- **Verifikation:** `uv run pytest tests/test_creatures_catalog.py -k all_36 -q && uv run pytest -q`

---

## C10 — Zwischenbosse Teil 1 (`schrott`, `myzel`, `magen`, `amt`, `kuchen`) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C09`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_boss_specs.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die ersten 5 Zwischenbosse (`is_mid_boss=True`, `sample_chance=1.0`, `hp` im Bereich `140..200`):
     - `"gabelstapler_krabbe"` (`schrott`, `Ability("steal", "wand")`, `Ability("reflect", "shield")`)
     - `"sporenherz"` (`myzel`, `Ability("summon", "sporenwerfer", 2.0)`, `Ability("aura", "poison", 48.0)`)
     - `"pfuetzenwurm"` (`magen`, `Ability("burrow", "flesh")`, Säure-Salve)
     - `"aktenwolf"` (`amt`, `Ability("morph", "alpha", 0.5)`, `Ability("aura", "stamp_tax", 42.0)`)
     - `"marzipan_ritter"` (`kuchen`, `Ability("reflect", "sugar_shield")`, Lanzen-Stoß)
- **Akzeptanzkriterien:**
  - Alle 5 Zwischenbosse sind mit `is_mid_boss == True` in `SPECIES` registriert und überstehen 60 Simulations-Ticks.
- **Verifikation:** `uv run pytest tests/test_boss_specs.py -k mid_part1 -q && uv run pytest -q`

---

## C11 — Zwischenbosse Teil 2 (`abtei`, `ameisen`, `spule`, `glibber`) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C10`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_boss_specs.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die restlichen 4 Zwischenbosse (`is_mid_boss=True`, `sample_chance=1.0`):
     - `"glockenwaechter"` (`abtei`, `Ability("aura", "shock", 50.0)`, Schall-Nova)
     - `"harzgeneral"` (`ameisen`, `Ability("summon", "ameisensoldat", 2.0)`, Harz-Salve)
     - `"spulenmeister"` (`spule`, `Ability("teleport", "spark")`, Kettenblitz-Schuss)
     - `"manege_clown"` (`glibber`, `Ability("split", "clown")`, Hüpf-Bomben)
- **Akzeptanzkriterien:**
  - Alle 9 `u.mid_boss`-Schlüssel aus `UNIVERSES.values()` sind in `SPECIES` vorhanden und haben `is_mid_boss == True`.
- **Verifikation:** `uv run pytest tests/test_boss_specs.py -k mid_part2 -q && uv run pytest -q`

---

## C12 — Endboss-Spezifikationen Teil 1 (`schrottpresse`, `muttermyzel`, `pfuetzenkoenig`, `oberamtsrat`, `hochzeitstorte`) (`V1b`, `V16`)

- **Größe:** S
- **Abhängigkeiten:** `C11`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_boss_specs.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die ersten 5 Universums-Endbosse (`is_boss=True`, `hp` im Bereich `320..460`, `drops_sample="probe_kern"`, `sample_chance=1.0`): `"schrottpresse"`, `"muttermyzel"`, `"pfuetzenkoenig"`, `"oberamtsrat"`, `"hochzeitstorte"`.
- **Akzeptanzkriterien:**
  - Alle 5 Endbosse sind mit `is_boss == True` und `drops_sample == "probe_kern"` in `SPECIES` registriert.
- **Verifikation:** `uv run pytest tests/test_boss_specs.py -k end_part1 -q && uv run pytest -q`

---

## C13 — Endboss-Spezifikationen Teil 2 (`abt_nautilus`, `koenigin_mandibula`, `transformator`, `zirkusdirektor`) (`V1b`, `V16`)

- **Größe:** S
- **Abhängigkeiten:** `C12`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_boss_specs.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/universes/catalog.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die restlichen 4 Universums-Endbosse (`is_boss=True`, `drops_sample="probe_kern"`, `sample_chance=1.0`): `"abt_nautilus"`, `"koenigin_mandibula"`, `"transformator"`, `"zirkusdirektor"`.
- **Akzeptanzkriterien:**
  - Alle 9 `u.boss`-Schlüssel aus `UNIVERSES.values()` sind in `SPECIES` vorhanden und haben `is_boss == True`.
- **Verifikation:** `uv run pytest tests/test_boss_specs.py -k end_part2 -q && uv run pytest -q`

---

## C14 — Behörden-Agenten, Böse Ichs & `"ober_cloita"` in `src/enemies.py` (`V15`, `V17`)

- **Größe:** S
- **Abhängigkeiten:** `C13`
- **Ziel-Dateien:** `src/enemies.py`, `tests/test_boss_specs.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`, `V17`), `src/enemies.py`
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`):
     - die 3 Behörden-Agenten (`faction="behoerde"`): `"agent_sachbearbeiter"`, `"agent_vollstrecker"` (`Ability("reflect", "briefcase")`), `"agent_abteilungsleiter"` (`Ability("summon", "agent_sachbearbeiter", 1.0)`)
     - die 3 Bösen Ichs (`faction="boese_ichs"`, `is_boss=True`): `"boese_kaiserin"`, `"boese_gute"`, `"boese_omega"`
     - den Hauptquartier-Endboss `"ober_cloita"` (`faction="behoerde"`, `is_boss=True`, `hp=650.0`).
- **Akzeptanzkriterien:**
  - Alle 7 Spezial-Spezies sind in `SPECIES` vorhanden und lassen sich über `EnemyManager.spawn` instanziieren.
- **Verifikation:** `uv run pytest tests/test_boss_specs.py -k agents_and_evil -q && uv run pytest -q`

---

## C15 — Kreaturen-Projektil-Effekte (Stempel, Sirup, Harz, Schall, Blitz) in `src/projectiles.py` (`V4b`)

- **Größe:** S
- **Abhängigkeiten:** `A08`, `C14`
- **Ziel-Dateien:** `src/projectiles.py`, `tests/test_creature_projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4b`), `src/projectiles.py`
- **Aufgabe:**
  1. Erweitere die Treffer-Behandlung feindlicher Projektile in `src/projectiles.py`:
     - Projektile von `"stempelkaefer"`, `"agent_sachbearbeiter"` oder `"oberamtsrat"` setzen auf dem getroffenen Ziel `body.stamped_bad = max(body.stamped_bad, 10.0)`.
     - Projektile von `"zuckerspinne"` oder `"harzspucker"` setzen `body.sticky = max(body.sticky, 5.0)`.
     - Projektile von `"funkenhornisse"`, `"spulenmeister"` oder `"transformator"` setzen `body.charged = max(body.charged, 4.0)`.
- **Akzeptanzkriterien:**
  - Treffer durch ein Projektil mit `owner_species="agent_sachbearbeiter"` setzt `player.body.stamped_bad >= 10.0`; Treffer mit `owner_species="harzspucker"` setzt `player.body.sticky >= 5.0`.
- **Verifikation:** `uv run pytest tests/test_creature_projectiles.py -q && uv run pytest -q`

---

## C16 — Proben-, Gold- & Teilungs-Auszahlung beim Kreaturen-Tod in `src/run.py` (`V1`, `V11`, `V12`)

- **Größe:** S
- **Abhängigkeiten:** `A07`, `C14`
- **Ziel-Dateien:** `src/run.py`, `tests/test_creature_drops.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`, `V12`), `src/run.py`
- **Aufgabe:**
  1. Aktualisiere die Todes-Schleife für Kreaturen in `Run.update` (`src/run.py`):
     - Spawnt für jede getötete Kreatur ein `"gold"`-Pickup (`amount = max(1, int(c.spec.hp / 12))`) und mit Wahrscheinlichkeit `c.spec.sample_chance` (bei Bossen/Zwischenbossen immer `1.0`) ein `"sample"`-Pickup (`item_key = c.spec.drops_sample or self.universe.sample_key`).
     - Verarbeitet `out_events` aus `EnemyManager.update`: Bei `"split"` werden 2 Nachkommen mit `generation = c.generation + 1` und skalierter Größe/HP (`SPLIT_SIZES`) gespawnt; bei `"steal_return"` wird das gestohlene `c.carrying`-Pickup am Todesort fallengelassen; bei `"summon"` werden die beschworenen Kreaturen gespawnt.
- **Akzeptanzkriterien:**
  - Tod einer Kreatur mit `sample_chance=1.0` erzeugt ein `"sample"`-Pickup mit dem passenden `item_key`.
  - Tod einer Kreatur mit `Ability("split", ...)` und `generation == 0` spawnt genau 2 kleinere Kreaturen mit `generation == 1`.
- **Verifikation:** `uv run pytest tests/test_creature_drops.py -q && uv run pytest -q`

---

## C17 — Schwachstellen- & Resistenz-Multiplikatoren (`weak_material` / `resist_material`) (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C14`
- **Ziel-Dateien:** `src/enemies.py`, `src/projectiles.py`, `tests/test_creature_weaknesses.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/enemies.py`, `src/projectiles.py`
- **Aufgabe:**
  1. Hinterlege sinnvolle `weak_material`- und `resist_material`-Einträge auf den Kreaturen-Spezifikationen in `src/enemies.py` (z. B. `schrott` schwach gegen `"acid"`, resistent gegen `"smoke"`; `kuchen` schwach gegen `"fire"`; `myzel` schwach gegen `"fire"`, resistent gegen `"spore"`).
  2. Wende beim Projektil-Treffer (`src/projectiles.py`) und Welt-Kontakt (`src/enemies.py`) `1.5×` Schaden bei `trail == spec.weak_material` und `0.5×` Schaden bei `trail == spec.resist_material` an.
- **Akzeptanzkriterien:**
  - Ein Feuer-Projektil (`trail="fire"`) verursacht an `"kerzenkobold"` (`resist_material="fire"`) `0.5×` Schaden und an `"sporenwerfer"` (`weak_material="fire"`) `1.5×` Schaden.
- **Verifikation:** `uv run pytest tests/test_creature_weaknesses.py -q && uv run pytest -q`
