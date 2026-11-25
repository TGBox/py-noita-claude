# Phase C — Kreaturen, Bosse & Agenten-Grundkörper (14 atomare S-Karten: `C01`–`C17`; `C07`, `C08`, `C13` entfallen)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_c.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Kreaturen-Einträge folgen `V1`–`V4` aus [v01-verhalten-und-wegsuche.md](vertraege/v01-verhalten-und-wegsuche.md) und `V0d` aus [v00-migration-und-schluessel.md](vertraege/v00-migration-und-schluessel.md).

---

> Die Pool-Universen `schrott`, `kuchen` und `spule` (früher `C07`, `C08`, `C13` und Teile von `C09`/`C11`) sind nach Phase J verschoben (`docs/erweiterung/03-universen-erweiterung.md`, `tasks/todo_erweiterung.md` J01–J03). Die frei gewordenen IDs werden nicht neu vergeben.

## C01 — Kreaturen Fleischwelt (`fleischwelt`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `A15`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/bibel/05-gegner.md` (Abschnitt „Fleischwelt“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c01`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `fleischwelt` mit `faction="parasiten"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_gallenstein" / "probe_wucherung". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"fleischmade"` (`walk`, `hostile`, `Ability("melee")`, `Ability("hunt")`; springt Hindernisse an)
     - `"blutegel"` (`walk`, `hostile`, `Ability("melee")`, `Ability("hunt")`; `hangs=True`, saugt 2/s solange festgesaugt)
     - `"saeurespucker"` (`walk`, `hostile`, `Ability("ranged", "acid")`; `resist_material="acid"`, `weak_material="fire"`)
     - `"zottenwurm"` (`walk`, `neutral`, `Ability("graze", "flesh")`, `Ability("burrow", "flesh")`, `Ability("melee")`)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["fleischwelt"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c01 -q && uv run pytest --ignore=tests/spec -q`

---

## C02 — Kreaturen Aktenhalde (`aktenhalde`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C01`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/bibel/05-gegner.md` (Abschnitt „Aktenhalde“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c02`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `aktenhalde` mit `faction="akten"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_stempelkissen" / "probe_formular". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"aktenfresser"` (`walk`, `neutral`, `Ability("dig", "papier")`, `Ability("melee")`, `Ability("pack")`; `weak_material="fire"`)
     - `"stempler"` (`walk`, `neutral`, `Ability("melee")`, `Ability("summon", "agent_streife", 1.0)`, `Ability("aura", "stamp_tax", 32.0)`)
     - `"paragraphenreiter"` (`fly`, `hostile`, `Ability("ranged", "paragraph")`, `Ability("summon", "stempler", 1.0)`)
     - `"kaffeegolem"` (`walk`, `neutral`, `Ability("melee")`, `Ability("ranged", "steam")`, `Ability("morph", "enraged", 0.5)`)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["aktenhalde"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c02 -q && uv run pytest --ignore=tests/spec -q`

---

## C03 — Kreaturen Glibbria (`glibbria`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C02`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/bibel/05-gegner.md` (Abschnitt „Glibbria“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c03`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `glibbria` mit `faction="gelee"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_glibberkern" / "probe_brauseperle". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"huepfling"` (`walk`, `passive`, `Ability("flee")`, `Ability("graze", "zuckerguss")`; `group_size=(3, 6)`)
     - `"glibberteiler"` (`walk`, `hostile`, `Ability("melee")`, `Ability("hunt")`, `Ability("split", "glibber")`, `Ability("armor")`; Größen aus `SPLIT_SIZES`)
     - `"zuckerwatte_wolke"` (`fly`, `passive`, `Ability("flee")`, `Ability("aura", "slow", 40.0)`)
     - `"konfetti_kanone"` (`walk`, `hostile`, `Ability("ranged", "confetti")`, `Ability("reflect", "bounce")`)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["glibbria"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c03 -q && uv run pytest --ignore=tests/spec -q`

---

## C04 — Kreaturen Krümelreich (`kruemelreich`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C03`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `docs/bibel/05-gegner.md` (Abschnitt „Krümelreich“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c04`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `kruemelreich` mit `faction="insekten"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_zuckerkristall" / "probe_ameisenduft". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"ameisenkrieger"` (`walk`, `hostile`, `Ability("pack")`, `Ability("hunt")`, `Ability("melee")`, `Ability("dig", "brosel")`, `Ability("ranged", "acid")`; `group_size=(4, 8)`)
     - `"blattlaus"` (`walk`, `passive`, `Ability("graze", "zucker")`; setzt beim Spawn `giver = True` gemäß `V0d`)
     - `"arbeiterameise"` (`walk`, `neutral`, `Ability("pack")`, `Ability("steal", "gold")`, `Ability("dig", "brosel")`)
     - `"harzspucker"` (`walk`, `hostile`, `Ability("ranged", "resin")`, `Ability("aura", "slow", 32.0)`)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["kruemelreich"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
  - Eine gespawnte `"blattlaus"` hat `giver == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c04 -q && uv run pytest --ignore=tests/spec -q`

---

## C05 — Kreaturen Sporenklub (`sporenklub`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C04`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `docs/bibel/05-gegner.md` (Abschnitt „Sporenklub“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c05`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `sporenklub` mit `faction="pilze"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_leuchtspore" / "probe_plattennadel". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"tuersteherpilz"` (`walk`, `neutral`, `Ability("stationary")`, `Ability("shield", "front")`, `Ability("melee")`; bestechbar für 20 Gold gemäß `V0d`)
     - `"sporenschnorrer"` (`walk`, `hostile`, `Ability("steal", "flask")`, `Ability("flee")`, `Ability("split", "spore")`)
     - `"sporenwerfer"` (`walk`, `hostile`, `Ability("ranged", "spore")`, `Ability("aura", "poison", 36.0)`; `weak_material="fire"`)
     - `"leuchtmotte"` (`fly`, `passive`, `Ability("flee")`, `Ability("aura", "heal_allies", 44.0)`; leuchtet)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["sporenklub"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c05 -q && uv run pytest --ignore=tests/spec -q`

---

## C06 — Kreaturen Versunkene Abtei (`abtei`: 4 Einheimische) in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C05`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V4`), `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0d`), `docs/bibel/05-gegner.md` (Abschnitt „Versunkene Abtei“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c06`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 4 Einheimischen von `abtei` mit `faction="tiefsee"` (`UNIVERSE_FACTIONS`, `V4`) und `drops_sample` abwechselnd "probe_glockensplitter" / "probe_kerzenstumpf". Leben, Tempo, Schaden und Ausholzeit (`windup_time`) stehen in Bibel 05:
     - `"moenchsfisch"` (`swim`, `neutral`, `Ability("pack")`, `Ability("ranged", "bubble")`; Chor-Buff ab 3 Fischen gemäß `V0d`)
     - `"orgelaal"` (`swim`, `hostile`, `Ability("hunt")`, `Ability("ranged", "shock")`, `Ability("burrow", "sand")`; außerhalb von Wasser zappelt er hilflos)
     - `"glockenqualle"` (`swim`, `passive`, `Ability("aura", "shock", 36.0)`; leuchtet)
     - `"korallenwaechter"` (`walk`, `neutral`, `Ability("shield", "front")`, `Ability("reflect", "shell")`, `Ability("melee")`)
- **Akzeptanzkriterien:**
  - Alle 4 Spezies aus `UNIVERSES["abtei"].creatures` sind in `SPECIES` registriert, lassen sich über `EnemyManager.spawn` erzeugen und überstehen 20 Simulations-Ticks ohne Fehler.
  - Damit sind alle 24 Einheimischen der 6 MVP-Universen registriert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c06 -q && uv run pytest --ignore=tests/spec -q`

---

## C09 — Großkreaturen `trampolinwal` & `kirchenkrake` in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C06`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1`–`V2`), `docs/plan/vertraege/v09-universen-und-ereignisse.md` (`V13b`, Kirchenkrake), `docs/bibel/05-gegner.md`, `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c09`)
- **Aufgabe:**
  1. Registriere die 2 Großkreaturen aus der Bibel (`docs/bibel/05-gegner.md` §3): `"trampolinwal"` (`glibbria`, `passive`, prallt Projektile nach oben ab) und `"kirchenkrake"` (`abtei`, `swim`, `hostile`, `Ability("grab_pull", "tentacle")`).
  2. Ergänze den Lärmzähler der `"kirchenkrake"` laut `V13b`: `Creature.noise_level: float = 0.0`, `EnemyManager.on_noise(x, y, radius, out_events)` (+40 für schlafende Kraken im Umkreis `200 px`), Abbau um `10` pro Sekunde in `EnemyManager.update`, Aufwachen bei `>= 100` mit Ereignis `("creature_woke", {"species": "kirchenkrake"})`.
- **Akzeptanzkriterien:**
  - `"trampolinwal"` (`faction="gelee"`) und `"kirchenkrake"` (`faction="tiefsee"`) sind in `SPECIES` registriert und lassen sich spawnen.
  - Drei Lärm-Ereignisse kurz hintereinander wecken die Krake, drei Ereignisse mit je 5 s Pause nicht.
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
     - `"harzgeneral"` (`kruemelreich`, `Ability("summon", "ameisenkrieger", 2.0)`, Harz-Salve)
     - `"sporenherz"` (`sporenklub`, `Ability("summon", "sporenwerfer", 2.0)`, `Ability("aura", "poison", 48.0)`)
- **Akzeptanzkriterien:**
  - Alle 5 Zwischenbosse sind mit `is_mid_boss == True` in `SPECIES` registriert und überstehen 60 Simulations-Ticks.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c10 -q && uv run pytest --ignore=tests/spec -q`

---

## C11 — Unter-Zwischenboss Teil 2 (`glockenwaechter`) & Vollständigkeitsprüfung in `src/enemies.py` (`V1b`)

- **Größe:** S
- **Abhängigkeiten:** `C10`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c11`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) den letzten Unter-Zwischenboss (`is_mid_boss=True`, `sample_chance=1.0`):
     - `"glockenwaechter"` (`abtei`, `Ability("aura", "shock", 50.0)`, Schall-Nova)
- **Akzeptanzkriterien:**
  - Alle 6 `u.mid_boss`-Schlüssel aus `UNIVERSES` sind in `SPECIES` vorhanden und haben `is_mid_boss == True`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c11 -q && uv run pytest --ignore=tests/spec -q`

---

## C12 — Universums-Hauptbosse Teil 1 (6 MVP-Universen aus der Bibel) (`V1b`, `V16`)

- **Größe:** S
- **Abhängigkeiten:** `C11`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V1b`), `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V16`), `src/universes/catalog.py`, `tests/spec/test_phase_c.py` (`-k c12`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) die 6 kanonischen MVP-Universums-Hauptbosse (`is_boss=True`, `hp` im Bereich `320..460`, `drops_sample="probe_kern"`, `sample_chance=1.0`):
     - `"weltenherz"` (`fleischwelt`)
     - `"oberstempler"` (`aktenhalde`)
     - `"mutter_glibber"` (`glibbria`)
     - `"ameisenkoenigin"` (`kruemelreich`)
     - `"dj_myzel"` (`sporenklub`)
     - `"abt_kieme"` (`abtei`)
- **Akzeptanzkriterien:**
  - Alle 6 `u.boss`-Schlüssel aus `UNIVERSES.values()` sind mit `is_boss == True` und `drops_sample == "probe_kern"` in `SPECIES` registriert.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c12 -q && uv run pytest --ignore=tests/spec -q`

---

## C14 — Behörden-Agenten, böse Ichs, Rat & `"ober_cloita"` in `src/enemies.py` (`V15`, `V17`)

- **Größe:** S
- **Abhängigkeiten:** `C12`
- **Ziel-Dateien:** `src/enemies.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v15-behoerde-und-bosse.md` (`V15`, `V17`), `docs/bibel/05-gegner.md` („Behörden-Agenten“, „Böse Ichs“, „Wahres Ende“), `src/enemies.py`, `tests/spec/test_phase_c.py` (`-k c14`)
- **Aufgabe:**
  1. Registriere in `SPECIES` (`src/enemies.py`) mit Leben aus Bibel 05:
     - die 4 Agenten (`faction="behoerde"`): `"agent_streife"` 45 (Alias `"agent_sachbearbeiter"`), `"agent_drohne"` 15 (`flying`), `"agent_vollstrecker"` 120 (`Ability("reflect", "briefcase")`), `"agent_abteilungsleiter"` 160 (`flying`, `Ability("summon", "agent_streife", 1.0)`),
     - die 3 bösen Ichs (`faction="boese_ichs"`, `is_boss=True`): `"boese_kaiserin"` 3500, `"boese_gute"` 3200, `"boese_omega"` 3800,
     - `"ratsmitglied"` 90 (`faction="behoerde"`, `ranged`, Agenten-Optik mit Robe) und `"ober_cloita"` 6000 (`faction="behoerde"`, `is_boss=True`, 96×96).
- **Akzeptanzkriterien:**
  - Alle genannten Arten stehen mit den Leben aus Bibel 05 in `SPECIES` und lassen sich über `EnemyManager.spawn` erzeugen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c14 -q && uv run pytest --ignore=tests/spec -q`

---

## C15 — Kreaturen-Projektil-Effekte (Stempel, Harz, Strom) in `src/projectiles.py` (`V4b`)

- **Größe:** S
- **Abhängigkeiten:** `A08`, `C14`
- **Ziel-Dateien:** `src/projectiles.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v01-verhalten-und-wegsuche.md` (`V4b`), `src/projectiles.py`, `tests/spec/test_phase_c.py` (`-k c15`)
- **Aufgabe:**
  1. Erweitere die Treffer-Behandlung feindlicher Projektile in `src/projectiles.py`:
     - Projektile von `"stempler"`, `"agent_streife"`, `"agent_sachbearbeiter"` oder `"oberstempler"` setzen auf dem getroffenen Ziel `body.stamped_bad = max(body.stamped_bad, 10.0)`.
     - Projektile von `"harzspucker"` oder `"harzgeneral"` setzen `body.sticky = max(body.sticky, 5.0)`.
     - Projektile von `"orgelaal"`, `"glockenqualle"` oder `"glockenwaechter"` setzen `body.charged = max(body.charged, 4.0)`.
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
  1. Prüfe bzw. ergänze `weak_material` / `resist_material` auf den Spezifikationen in `src/enemies.py` nach Bibel 05 („Schwäche“, „immun“): u. a. `saeurespucker` `resist_material="acid"`; `fleischmade`, `aktenfresser`, `sporenwerfer`, `glibberteiler` `weak_material="fire"`. Nur Materialschlüssel aus `src/materials.py` verwenden.
  2. Wende beim Projektil-Treffer (`src/projectiles.py`) und Welt-Kontakt (`src/enemies.py`) `1.5×` Schaden bei `trail == spec.weak_material` und `0.5×` Schaden bei `trail == spec.resist_material` an.
- **Akzeptanzkriterien:**
  - Ein Feuer-Projektil (`trail="fire"`) verursacht an `"sporenwerfer"` (`weak_material="fire"`) `1.5×` Schaden; ein Säure-Projektil (`trail="acid"`) an `"saeurespucker"` (`resist_material="acid"`) `0.5×` Schaden.
- **Verifikation:** `uv run pytest tests/spec/test_phase_c.py -k c17 -q && uv run pytest --ignore=tests/spec -q`
