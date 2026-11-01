# Phase C — Kreaturen, Bosse & Agenten-Grundkörper (17 atomare S-Karten: `C01`–`C17`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_c.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Kreaturen-Einträge folgen `V1`–`V4` aus [v01-verhalten-und-wegsuche.md](vertraege/v01-verhalten-und-wegsuche.md) und `V0d` aus [v00-migration-und-schluessel.md](vertraege/v00-migration-und-schluessel.md).

---

## C01 — Kreaturen Universum 1 (`fleischwelt`: 4 reguläre Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `A15`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/bibel/05-gegner.md`, `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c01`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `fleischwelt` (`faction="fleischwelt"` / `"parasiten"`, `drops_sample="probe_gallenstein"` bzw. `"probe_wucherung"`):
     - `"madenwurm"` / `"zottenwurm"` (`walk`/`swim`, `hostile`, `Ability("split", "worm")`, `Ability("eat_material", "flesh")`)
     - `"blutfliege"` / `"gallenblase"` (`fly`, `hostile`, `Ability("suicide_explosion", "acid", 16.0)`)
     - `"saeurespucker"` (`walk`, `hostile`, `Ability("spit_material", "acid")`)
     - `"bandwurm_kopf"` (`walk`, `hostile`, `Ability("split", "worm")`)
- **Akzeptanzkriterien:**
  - Alle `fleischwelt`-Spezies aus `UNIVERSES["fleischwelt"].creatures` sind in `SPECIES` vorhanden, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 60 Simulations-Ticks in `EnemyManager.update` ohne Fehler.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c01 -q && uv run pytest --ignore=tests/spec -q`

---

## C02 — Kreaturen Universum 2 (`aktenhalde`: 4 reguläre Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C01`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c02`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `aktenhalde` (`faction="aktenhalde"` / `"behoerde"`, `drops_sample="probe_stempelkissen"` bzw. `"probe_formular"`):
     - `"papierfresser"` / `"aktenfresser"` (`walk`, `neutral`/`peaceful`, `Ability("eat_cells", "paper")`)
     - `"heftklammer_krabbe"` / `"stempelkaefer"` (`walk`, `hostile`, `Ability("shield_front", "shield")`, `Ability("aura", "stamp_tax", 32.0)`)
     - `"paragraphenreiter"` (`fly`, `hostile`, `Ability("summon", "stempelkaefer", 2.0)`)
     - `"kaffeegolem"` (`walk`, `hostile`, `Ability("morph", "enraged", 0.5)`)
- **Akzeptanzkriterien:**
  - Alle `aktenhalde`-Spezies aus `UNIVERSES["aktenhalde"].creatures` existieren in `SPECIES` mit den spezifizierten Haltungen und Fähigkeiten.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c02 -q && uv run pytest --ignore=tests/spec -q`

---

## C03 — Kreaturen Universum 3 (`glibbria`: 4 reguläre Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C02`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c03`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `glibbria` (`faction="glibbria"` / `"zirkus"`, `drops_sample="probe_glibberkern"` bzw. `"probe_brauseperle"`):
     - `"glibber_slime"` / `"quallenhund"` (`walk`, `hostile`, `Ability("split", "jelly")`, `Ability("leave_trail", "jelly")`)
     - `"brause_geist"` / `"zuckerwatte_wolke"` (`fly`, `passive`/`shy`, `Ability("suicide_explosion", "jelly", 16.0)`, `Ability("aura", "slow", 40.0)`)
     - `"trampolin_frosch"` (`walk`, `neutral`, `Ability("reflect", "bounce")`)
     - `"konfetti_kanone"` (`walk`, `hostile`, Salven-Schuss im Takt)
- **Akzeptanzkriterien:**
  - Alle `glibbria`-Spezies aus `UNIVERSES["glibbria"].creatures` existieren in `SPECIES` und funktionieren im 60-Tick-Simulationstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c03 -q && uv run pytest --ignore=tests/spec -q`

---

## C04 — Kreaturen Universum 4 (`kruemelreich`: 4 reguläre Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C03`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c04`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `kruemelreich` (`faction="kruemelreich"` / `"insekten"`, `drops_sample="probe_zuckerkristall"` bzw. `"probe_ameisenduft"`):
     - `"ameisen_soldat"` / `"ameisensoldat"` (`walk`, `hostile`, `Ability("call_reinforcements", "ameisen")`, `Ability("shield_front", "shield")`)
     - `"blattlaus"` (`walk`, `passive`/`peaceful`, `Ability("eat_material", "sugar")`, setzt beim Spawn `giver = True` gemäß `V0d`)
     - `"arbeiterameise"` (`walk`, `neutral`, `Ability("steal", "gold")`)
     - `"harzspucker"` (`walk`, `hostile`, `Ability("spit_material", "resin")`, `Ability("aura", "slow", 32.0)`)
- **Akzeptanzkriterien:**
  - Alle `kruemelreich`-Spezies aus `UNIVERSES["kruemelreich"].creatures` existieren in `SPECIES`; eine gespawnte `"blattlaus"` hat `giver == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c04 -q && uv run pytest --ignore=tests/spec -q`

---

## C05 — Kreaturen Universum 5 (`sporenklub`: 4 reguläre Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C04`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c05`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `sporenklub` (`faction="sporenklub"` / `"pilze"`, `drops_sample="probe_leuchtspore"` bzw. `"probe_plattennadel"`):
     - `"bass_pilz"` / `"tuersteherpilz"` (`walk`, `neutral`/`territorial`, `Ability("pulse_shockwave", "spore", 36.0)`, bestechbar für 20 Gold gemäß `V0d`)
     - `"sporen_motte"` / `"leuchtmotte"` (`fly`, `passive`/`peaceful`, `Ability("leave_trail", "spore")`, `Ability("aura", "heal_allies", 44.0)`)
     - `"sporenwerfer"` (`walk`, `hostile`, `Ability("aura", "poison", 36.0)`)
     - `"kappenschleicher"` (`walk`, `passive`/`shy`, `Ability("split", "myzel")`)
- **Akzeptanzkriterien:**
  - Alle `sporenklub`-Spezies aus `UNIVERSES["sporenklub"].creatures` existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c05 -q && uv run pytest --ignore=tests/spec -q`

---

## C06 — Kreaturen Universum 6 (`abtei`: 4 reguläre Spezies) in `src/enemies.py` (`V0d`, `V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C05`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c06`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 regulären Kreaturen für `abtei` (`faction="abtei"` / `"tiefsee"`, `drops_sample="probe_glockensplitter"` bzw. `"probe_kerzenstumpf"`):
     - `"chor_fisch"` / `"moenchsfisch"` (`swim`, `neutral`/`territorial`, Schall-Projektil, profitiert ab 3 Fischen vom Chor-Buff gemäß `V0d`)
     - `"kerzen_qualle"` / `"glockenqualle"` (`swim`, `passive`/`peaceful`, `Ability("aura", "shock", 36.0)`)
     - `"korallenwaechter"` (`walk`, `neutral`, `Ability("reflect", "shell")`)
     - `"weihrauch_aal"` (`swim`, `hostile`, `Ability("burrow", "sand")`)
- **Akzeptanzkriterien:**
  - Alle 24 regulären Kreaturen-Schlüssel der 6 MVP-Universen (`UNIVERSES`) existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c06 -q && uv run pytest --ignore=tests/spec -q`

---

## C07 — Pool-Kreaturen 1 (`schrott`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C06`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c07`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen des Pool-Universums `schrott` (`faction="schrott"`, `drops_sample="probe_rost"`):
     - `"rostkaefer"` (`walk`, `territorial`, `Ability("eat_material", "rust")`)
     - `"schweissimp"` (`fly`, `hostile`, Feuer-Schuss, `Ability("teleport", "fire")`)
     - `"magnetwurm"` (`walk`, `hostile`, `Ability("burrow", "")`)
     - `"schrottgolem"` (`walk`, `territorial`, `Ability("reflect", "shield")`)
- **Akzeptanzkriterien:**
  - Alle 4 `schrott`-Spezies existieren in `SPECIES` und funktionieren im 60-Tick-Simulationstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c07 -q && uv run pytest --ignore=tests/spec -q`

---

## C08 — Pool-Kreaturen 2 (`kuchen`: 4 Spezies) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C07`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c08`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen des Pool-Universums `kuchen` (`faction="backwerk"`, `drops_sample="probe_zucker"`):
     - `"zuckerspinne"` (`walk`, `hostile`, verschießt klebrigen Sirup, `Ability("aura", "slow", 30.0)`)
     - `"kerzenkobold"` (`walk`, `hostile`, Feuerball-Schuss, `Ability("kamikaze", "fire", 14.0)`)
     - `"marzipanschwein"` (`walk`, `shy`, `Ability("eat_material", "dough")`)
     - `"baiser_geist"` (`fly`, `territorial`, `Ability("teleport", "blink")`)
- **Akzeptanzkriterien:**
  - Alle 4 `kuchen`-Spezies existieren in `SPECIES` und funktionieren im Simulationstest.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c08 -q && uv run pytest --ignore=tests/spec -q`

---

## C09 — Pool-Kreaturen 3 (`spule`: 4 Spezies) & 2 Großkreaturen (`trampolinwal`, `kirchenkrake`) (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C08`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/bibel/05-gegner.md`, `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c09`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Kreaturen des Pool-Universums `spule` (`faction="automaten"`, `drops_sample="probe_spule"`): `"funkenhornisse"`, `"spulenkrabbe"`, `"kupferschlange"`, `"kondensator_geist"`.
  2. Registriere außerdem die 2 Großkreaturen aus der Bibel (`docs/bibel/05-gegner.md` §3): `"trampolinwal"` (`glibbria`, `passive`, prallt Projektile nach oben ab) und `"kirchenkrake"` (`abtei`, `swim`, `hostile`, `Ability("grab_pull", "tentacle")`).
- **Akzeptanzkriterien:**
  - Alle Kreaturen-Schlüssel aus `UNIVERSES` und `POOL_UNIVERSES` sowie `"trampolinwal"` und `"kirchenkrake"` sind vollständig in `SPECIES` registriert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c09 -q && uv run pytest --ignore=tests/spec -q`

---

## C10 — Zwischenbosse Teil 1 (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C09`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c10`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die Sub-Zwischenbosse (`is_mid_boss=True`, `sample_chance=1.0`, `hp` im Bereich `140..200`):
     - `"pfuetzenwurm"` (`fleischwelt`, `Ability("burrow", "flesh")`, Säure-Salve)
     - `"aktenwolf"` (`aktenhalde`, `Ability("morph", "alpha", 0.5)`, `Ability("aura", "stamp_tax", 42.0)`)
     - `"manege_clown"` (`glibbria`, `Ability("split", "clown")`, Hüpf-Bomben)
     - `"harzgeneral"` (`kruemelreich`, `Ability("summon", "ameisensoldat", 2.0)`, Harz-Salve)
     - `"sporenherz"` (`sporenklub`, `Ability("summon", "sporenwerfer", 2.0)`, `Ability("aura", "poison", 48.0)`)
- **Akzeptanzkriterien:**
  - Alle 5 Zwischenbosse sind mit `is_mid_boss == True` in `SPECIES` registriert und überstehen 60 Simulations-Ticks.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c10 -q && uv run pytest --ignore=tests/spec -q`

---

## C11 — Zwischenbosse Teil 2 (`abtei` & Pool-Universen `schrott`, `kuchen`, `spule`) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C10`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c11`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die restlichen 4 Zwischenbosse (`is_mid_boss=True`, `sample_chance=1.0`):
     - `"glockenwaechter"` (`abtei`, `Ability("aura", "shock", 50.0)`, Schall-Nova)
     - `"gabelstapler_krabbe"` (`schrott`, `Ability("steal", "wand")`, `Ability("reflect", "shield")`)
     - `"marzipan_ritter"` (`kuchen`, `Ability("reflect", "sugar_shield")`, Lanzen-Stoß)
     - `"spulenmeister"` (`spule`, `Ability("teleport", "spark")`, Kettenblitz-Schuss)
- **Akzeptanzkriterien:**
  - Alle `u.mid_boss`-Schlüssel aus `UNIVERSES` und `POOL_UNIVERSES` sind in `SPECIES` vorhanden und haben `is_mid_boss == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c11 -q && uv run pytest --ignore=tests/spec -q`

---

## C12 — Universums-Hauptbosse Teil 1 (6 MVP-Universen aus der Bibel) (`V1b`, `V16`)

- **Größe:** S
- **Abhängigkeiten:** `C11`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c12`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 6 kanonischen MVP-Universums-Hauptbosse (`is_boss=True`, `hp` im Bereich `320..460`, `drops_sample="probe_kern"`, `sample_chance=1.0`):
     - `"weltenherz"` (Alias `"pfuetzenkoenig"`, `fleischwelt`)
     - `"oberstempler"` (Alias `"oberamtsrat"`, `aktenhalde`)
     - `"mutter_glibber"` (Alias `"zirkusdirektor"`, `glibbria`)
     - `"ameisenkoenigin"` (Alias `"koenigin_mandibula"`, `kruemelreich`)
     - `"dj_myzel"` (Alias `"muttermyzel"`, `sporenklub`)
     - `"abt_kieme"` (Alias `"abt_nautilus"`, `abtei`)
- **Akzeptanzkriterien:**
  - Alle 6 `u.boss`-Schlüssel aus `UNIVERSES.values()` (sowie ihre Aliase) sind mit `is_boss == True` und `drops_sample == "probe_kern"` in `SPECIES` registriert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c12 -q && uv run pytest --ignore=tests/spec -q`

---

## C13 — Universums-Hauptbosse Teil 2 (Pool-Bosse `schrottpresse`, `hochzeitstorte`, `transformator`) (`V1b`, `V16`)

- **Größe:** S
- **Abhängigkeiten:** `C12`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c13`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 3 Pool-Universums-Endbosse (`is_boss=True`, `drops_sample="probe_kern"`, `sample_chance=1.0`): `"schrottpresse"`, `"hochzeitstorte"`, `"transformator"`.
- **Akzeptanzkriterien:**
  - Alle `u.boss`-Schlüssel aus `UNIVERSES` und `POOL_UNIVERSES` sind in `SPECIES` vorhanden und haben `is_boss == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c13 -q && uv run pytest --ignore=tests/spec -q`

---

## C14 — Behörden-Agenten, Böse Ichs & `"ober_cloita"` in `src/enemies.py` (`V15`, `V17`)

- **Größe:** S
- **Abhängigkeiten:** `C13`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`, `V17`), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c14`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`):
     - die 4 Behörden-Agenten (`faction="behoerde"`): `"agent_streife"` (sowie Alias `"agent_sachbearbeiter"`), `"agent_drohne"` (`fly`), `"agent_vollstrecker"` (`Ability("reflect", "briefcase")`), `"agent_abteilungsleiter"` (`Ability("summon", "agent_sachbearbeiter", 1.0)`)
     - die 3 Bösen Ichs (`faction="boese_ichs"`, `is_boss=True`): `"boese_kaiserin"`, `"boese_gute"`, `"boese_omega"`
     - den Hauptquartier-Endboss `"ober_cloita"` (`faction="behoerde"`, `is_boss=True`, `hp=650.0`).
- **Akzeptanzkriterien:**
  - Alle Behörden-Agenten, Bösen Ichs und `"ober_cloita"` sind in `SPECIES` vorhanden und lassen sich über `EnemyManager.spawn` instanziieren.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c14 -q && uv run pytest --ignore=tests/spec -q`

---

## C15 — Kreaturen-Projektil-Effekte (Stempel, Sirup, Harz, Schall, Blitz) in `src/projectiles.py` (`V4b`)

- **Größe:** S
- **Abhängigkeiten:** `A08`, `C14`
- **Ziel-Dateien:** `src/projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4b`), `src/projectiles.py`, `tests/spec/test_phase_c.py` (`-k c15`)
- **Aufgabe:**
  1. Erweitere die Treffer-Behandlung feindlicher Projektile in `src/projectiles.py`:
     - Projektile von `"stempelkaefer"`, `"agent_streife"`, `"agent_sachbearbeiter"`, `"oberstempler"` oder `"oberamtsrat"` setzen auf dem getroffenen Ziel `body.stamped_bad = max(body.stamped_bad, 10.0)`.
     - Projektile von `"zuckerspinne"` oder `"harzspucker"` setzen `body.sticky = max(body.sticky, 5.0)`.
     - Projektile von `"funkenhornisse"`, `"spulenmeister"` oder `"transformator"` setzen `body.charged = max(body.charged, 4.0)`.
- **Akzeptanzkriterien:**
  - Treffer durch ein Projektil mit `owner_species="agent_sachbearbeiter"` setzt `player.body.stamped_bad >= 10.0`; Treffer mit `owner_species="harzspucker"` setzt `player.body.sticky >= 5.0`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c15 -q && uv run pytest --ignore=tests/spec -q`

---

## C16 — Proben-, Gold- & Teilungs-Auszahlung beim Kreaturen-Tod in `src/run.py` (`V1`, `V11`, `V12`)

- **Größe:** S
- **Abhängigkeiten:** `A07`, `C14`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`), `docs/plan/vertraege/v11-gegenstaende-und-ereignisbus.md` (`V11`, `V12`), `src/run.py`, `tests/spec/test_phase_c.py` (`-k c16`)
- **Aufgabe:**
  1. Aktualisiere die Todes-Schleife für Kreaturen in `Run.update` (`src/run.py`):
     - Spawnt für jede getötete Kreatur ein `"gold"`-Pickup (`amount = max(1, int(c.spec.hp / 12))`) und mit Wahrscheinlichkeit `c.spec.sample_chance` (bei Bossen/Zwischenbossen immer `1.0`) ein `"sample"`-Pickup (`item_key = c.spec.drops_sample or self.universe.sample_key`).
     - Verarbeitet `out_events` aus `EnemyManager.update`: Bei `"split"` werden 2 Nachkommen mit `generation = c.generation + 1` und skalierter Größe/HP (`SPLIT_SIZES`) gespawnt; bei `"steal_return"` wird das gestohlene `c.carrying`-Pickup am Todesort fallengelassen; bei `"summon"` werden die beschworenen Kreaturen gespawnt.
- **Akzeptanzkriterien:**
  - Tod einer Kreatur mit `sample_chance=1.0` erzeugt ein `"sample"`-Pickup mit dem passenden `item_key`.
  - Tod einer Kreatur mit `Ability("split", ...)` und `generation == 0` spawnt genau 2 kleinere Kreaturen mit `generation == 1`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c16 -q && uv run pytest --ignore=tests/spec -q`

---

## C17 — Schwachstellen- & Resistenz-Multiplikatoren (`weak_material` / `resist_material`) (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C14`
- **Ziel-Dateien:** `src/enemies.py`, `src/projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/enemies.py`, `src/projectiles.py`, `tests/spec/test_phase_c.py` (`-k c17`)
- **Aufgabe:**
  1. Hinterlege sinnvolle `weak_material`- und `resist_material`-Einträge auf den Kreaturen-Spezifikationen in `src/enemies.py` (z. B. `fleischwelt` resistent gegen `"acid"`; `aktenhalde` schwach gegen `"fire"`; `sporenklub`/`myzel` schwach gegen `"fire"`, resistent gegen `"spore"`).
  2. Wende beim Projektil-Treffer (`src/projectiles.py`) und Welt-Kontakt (`src/enemies.py`) `1.5×` Schaden bei `trail == spec.weak_material` und `0.5×` Schaden bei `trail == spec.resist_material` an.
- **Akzeptanzkriterien:**
  - Ein Feuer-Projektil (`trail="fire"`) verursacht an `"kerzenkobold"` (`resist_material="fire"`) `0.5×` Schaden und an `"sporenwerfer"` (`weak_material="fire"`) `1.5×` Schaden.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c17 -q && uv run pytest --ignore=tests/spec -q`
