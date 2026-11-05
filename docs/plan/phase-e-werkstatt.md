# Phase E — Werkstatt, Wirtschaft, Händler, Fabrikator & Minispiele (16 atomare S-Karten: `E01`–`E16`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien; schreibgeschützter Vorab-Test in `tests/spec/test_phase_e.py`, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](vertraege.md). Alle Karten folgen `V18`–`V20` aus [v18-werkstatt-und-wirtschaft.md](vertraege/v18-werkstatt-und-wirtschaft.md) und `V22` aus [v21-klonita-ui-und-speichern.md](vertraege/v21-klonita-ui-und-speichern.md). Am 2026-11-04 gegen Bibel 02, 04 und 07 abgeglichen.

---

## E01 — Werkstatt-Generator & 12 Stationen (`src/workshop.py`) (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `A03`
- **Ziel-Dateien:** `src/workshop.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Die Werkstatt“), `src/world.py`, `tests/spec/test_phase_e.py` (`-k e01`)
- **Aufgabe:**
  1. Fülle `STATIONS` mit den 12 Stationen aus der Tabelle in `V18` (Schlüssel, Name, `rect`, `prompt_de`) und implementiere `generate_workshop(world)` sowie `station_at(layout, cell_x, cell_y, radius=10)`. `layout.stations` nimmt auch die Schlüssel aus `STATION_ALIASES` an.
- **Akzeptanzkriterien:**
  - Alle 12 Stationen haben Namen und Größe aus Bibel 07; `station_at` findet jede Station an ihrem Mittelpunkt.
  - `generate_workshop(World(640, 360))` legt festen Boden ab `y = 210`, Wasser unter `"ws_well"` und Luft am `spawn` an.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e01 -q && uv run pytest --ignore=tests/spec -q`

---

## E02 — Gold- & Preisformeln (`src/economy.py`) (`V19` §1)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/economy.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19` §1), `docs/bibel/02-systeme.md` („Wirtschaft (Gold)“), `tests/spec/test_phase_e.py` (`-k e02`)
- **Aufgabe:**
  1. Implementiere alle Funktionen aus `V19` §1 (`creature_gold`, `mid_boss_gold`, `boss_gold`, `pile_gold`, `crate_gold`, `module_price`, `weapon_price`, `fabricator_gold`, `experiment_reroll_price`) mit den Tabellen am Dateianfang.
- **Akzeptanzkriterien:**
  - Alle Werte liegen in den Spannen aus Bibel 02 (z. B. `boss_gold(2) == 350`, `weapon_price(3) == 300`, `experiment_reroll_price(2) == 400`).
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e02 -q && uv run pytest --ignore=tests/spec -q`

---

## E03 — Gold-Drops von Kreaturen, Bossen & Goldadern in `src/run.py` (`V0c`, `V19` §1)

- **Größe:** S
- **Abhängigkeiten:** `A03`, `A07`, `E02`, `D10`, `C16`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0c`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19` §1), `src/run.py`, `tests/spec/test_phase_e.py` (`-k e03`)
- **Aufgabe:**
  1. Lass besiegte Kreaturen in `Run.update` ein `"gold"`-Pickup fallen: `creature_gold(rank, rng)`, `big=True` für große Kreaturen, `mid_boss_gold(rank)` bei `spec.is_mid_boss`, `boss_gold(rank)` bei Zwischengegnern (`spec.is_boss` und Art steht in `MID_BOSSES`). `rank = self.plan.rank`.
  2. Wandle zerstörte `"gold_vein"`-Zellen (`self.world.take_destroyed_gold_vein_cells()`) um: je `6` Zellen ein `"gold"`-Pickup mit `amount = 5`; ab `18` Zellen in einem Schritt zu `25 %` zusätzlich eine `"probe_gold"`.
- **Akzeptanzkriterien:**
  - Ein besiegter Zwischengegner auf Rang 2 lässt `350` Gold fallen; gesprengte Goldadern erzeugen `"gold"`-Pickups.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e03 -q && uv run pytest --ignore=tests/spec -q`

---

## E04 — Händler-Katalog & Angebote (`src/traders.py` Teil 1) (`V19` §2)

- **Größe:** S
- **Abhängigkeiten:** `A02`, `A04`, `A29`, `E02`
- **Ziel-Dateien:** `src/traders.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19` §2), `docs/bibel/04-figuren.md` („Händler“), `src/spells.py`, `tests/spec/test_phase_e.py` (`-k e04`)
- **Aufgabe:**
  1. Fülle `TRADERS` mit den 6 Händlern aus `V19` §2 (Begrüßung und Eigenheit auf Deutsch, Ton nach Bibel 08) und implementiere `traders_for_workshop(visited)` und `generate_offers(trader, stage, rng, *, price_factor=1.0)` nach der Sortimentsregel jedes Händlers.
- **Akzeptanzkriterien:**
  - Jeder Händler liefert genau 4 Angebote aus seiner Kategorie; Frau Abheft rechnet `+10` Gold auf, Krümel-Karl bietet Proben-Tausch, Bruder Flosse nur gesegnete Waffen.
  - `traders_for_workshop(["fleischwelt", "aktenhalde", "glibbria"])` liefert Wobbel und Frau Abheft.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e04 -q && uv run pytest --ignore=tests/spec -q`

---

## E05 — Kauf & Händler-Sonderregeln (`src/traders.py` Teil 2) (`V19` §2)

- **Größe:** S
- **Abhängigkeiten:** `E04`
- **Ziel-Dateien:** `src/traders.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19` §2), `src/traders.py`, `src/inventory.py`, `tests/spec/test_phase_e.py` (`-k e05`)
- **Aufgabe:**
  1. Implementiere `buy_offer(run, trader, offer, *, use_samples=False)`: Takt-Pflicht bei DJ Lamelle, Proben-Tausch über `run.inventory.take_samples`, Gold-Abzug mit `run.price_factor`, Segen von Bruder Flosse auf die gekaufte Waffe, Modul bzw. Waffe in den Rucksack; zu wenig Gold liefert `(False, "Zu wenig Gold.")`.
- **Akzeptanzkriterien:**
  - Ein Kauf bei Frau Abheft kostet Modulpreis + 10; Krümel-Karl nimmt mit `use_samples=True` 2 Proben statt Gold; DJ Lamelle verkauft neben dem Takt nicht.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e05 -q && uv run pytest --ignore=tests/spec -q`

---

## E06 — Fabrikator & Rezepte (`src/fabricator.py`) (`V20` §1)

- **Größe:** S
- **Abhängigkeiten:** `A02`, `A04`, `E02`, `G04`
- **Ziel-Dateien:** `src/fabricator.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §1), `docs/bibel/02-systeme.md` („Fabrikator“), `src/spells.py`, `src/samples.py`, `tests/spec/test_phase_e.py` (`-k e06`)
- **Aufgabe:**
  1. Implementiere `build_cost(block_key, stage=1)`, `Fabricator.can_build(run, block_key)` und `Fabricator.craft(run, block_key)` nach `V20` §1 (Bauplan-Pflicht, Proben je Kategorie, Zusatzprobe und Splitter nach Seltenheit, Gold, 3 Bauten je Besuch).
- **Akzeptanzkriterien:**
  - Ohne Bauplan liefert `can_build` `False`; ein Zünder braucht 2 Universums-Proben, ein Stufe-3-Modul zusätzlich einen Bauplan-Splitter.
  - Nach 3 Bauten blockiert `can_build` bis `reset_visit()`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e06 -q && uv run pytest --ignore=tests/spec -q`

---

## E07 — Minispiel-Basis & Physik-o-Mat Teil 1 (`glas_fuellen`, `vase_retten`, `kerze_zuenden`, `ameisenstrasse`) (`V20` §2)

- **Größe:** S
- **Abhängigkeiten:** `D19`, `D17`
- **Ziel-Dateien:** `src/minigames/__init__.py`, `src/minigames/physik_o_mat.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §2), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Minispiele“), `src/world.py`, `src/materials.py`, `tests/spec/test_phase_e.py` (`-k e07`)
- **Aufgabe:**
  1. Implementiere `Minigame.step` (Zeit, Ablauf nach `time_limit` mit `won=False`) und den Materialsatz `"physik_o_mat"` aus `V20` §2.
  2. Baue in `src/minigames/physik_o_mat.py` die ersten 4 Rätsel der Tabelle mit ihren Aktionen, Siegbedingungen und `solve_actions`; `make_physik_puzzle` wählt bei `None` ein Rätsel aus dem Seed.
- **Akzeptanzkriterien:**
  - Für jedes der 4 Rätsel führt `solve_actions(key)` innerhalb von 150 Schritten à `0.1 s` zum Sieg; Nichtstun endet nach `time_limit` mit `won == False`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e07 -q && uv run pytest --ignore=tests/spec -q`

---

## E08 — Physik-o-Mat Teil 2 (`lava_water`, `acid_gold`, `oil_fire`) (`V20` §2)

- **Größe:** S
- **Abhängigkeiten:** `E07`
- **Ziel-Dateien:** `src/minigames/physik_o_mat.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §2), `src/minigames/physik_o_mat.py`, `tests/spec/test_phase_e.py` (`-k e08`)
- **Aufgabe:**
  1. Ergänze die übrigen 3 Rätsel aus `PUZZLE_KEYS` mit Aufbau, Siegbedingung und `solve_actions`. Belohnung bei Sieg laut `V20` §2 (rng: Gold, Probe oder Schub).
- **Akzeptanzkriterien:**
  - Alle 7 Rätsel in `PUZZLE_KEYS` sind mit `solve_actions` lösbar; jede Belohnung ist `60` Gold, eine Universums-Probe oder ein Schub aus `NEXT_BOOST_KEYS`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e08 -q && uv run pytest --ignore=tests/spec -q`

---

## E09 — Schießstand (`src/minigames/schiessstand.py`) (`V20` §2)

- **Größe:** S
- **Abhängigkeiten:** `E07`
- **Ziel-Dateien:** `src/minigames/schiessstand.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §2), `src/minigames/__init__.py`, `tests/spec/test_phase_e.py` (`-k e09`)
- **Aufgabe:**
  1. Implementiere `SchiessstandMinigame`: feste Zielfolge aus dem Seed (24 Agenten, 6 Klonitas, je `1.5 s` sichtbar), Treffer im Radius 8, Punkte (`+1` Agent, `−3` Klonita), Ende nach `30 s` mit Belohnung laut `V20` §2.
- **Akzeptanzkriterien:**
  - Nur Agenten zu treffen bringt `>= 8` Punkte und einen Schub; jeder Klonita-Treffer zieht 3 Punkte ab.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e09 -q && uv run pytest --ignore=tests/spec -q`

---

## E10 — Werkstatt-Modus & Direkt-Stationen in `Run` (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `E01`, `E06`, `E02`
- **Ziel-Dateien:** `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `src/workshop.py`, `src/run.py`, `tests/spec/test_phase_e.py` (`-k e10`)
- **Aufgabe:**
  1. Ergänze auf `Run` `in_workshop`, `workshop_layout`, `fabricator`, `couch_used`, `minigames_played: set[str]`, `experiment_picked`, `experiment_rerolls`, `next_boost`, `price_factor`, `menu_mode` und `enter_workshop()` mit allem, was `V18` „Betreten“ verlangt.
  2. Implementiere `interact_station()` für alle 12 Stationen laut Tabelle in `V18` (Couch, Zapfanlage für `ZAPF_PRICE` Gold, Brunnen, Werkbank, Schredder sowie das Setzen von `menu_mode` für Portal, Fabrikator, Händler, Archiv, Liege; Minispiele übernimmt `E14`).
- **Akzeptanzkriterien:**
  - Nach `enter_workshop()` ist die Spielerin voll geheilt und steht am `spawn`; die Couch heilt genau einmal je Besuch `+35 %`.
  - Die Zapfanlage füllt den Kolben mit `"fluxschnaps"` und kostet 10 Gold; der Brunnen füllt kostenlos `"water"`.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e10 -q && uv run pytest --ignore=tests/spec -q`

---

## E11 — Portal-Auswahl (`"portal_select"`) & Weiterreise über `RunPlan` (`V9`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `D10`, `E10`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/universes/plan.py` (`RunPlan`), `src/menus.py`, `src/run.py`, `tests/spec/test_phase_e.py` (`-k e11`)
- **Aufgabe:**
  1. Ergänze `Run.choose_next_universe(index)`: `offer = self.plan.choose(index)`, dann das Universum `offer.universe` mit `boss_slot = offer.boss is not None` laden, `in_workshop = False` und einen aktiven `next_boost` für dieses Universum anwenden (`"flux"`: `mana_regen` aller Waffen `+20 %`; `"damage"`: Schaden `+10 %`; `"speed"`: Lauftempo `+10 %`). Beim Verlassen eines Universums über den Ankerpunkt geht es in die Werkstatt; nach dem 6. Universum bietet das Portal nur die Heimatwelt des bösen Ichs (`F18`).
  2. Ergänze `draw_portal_select_menu(surface, font, small_font, offers, selected_index)` mit Name, Regel, Rang und wartendem Zwischengegner je Vorschlag (Bibel 02 „Wahl am Portal“).
- **Akzeptanzkriterien:**
  - `choose_next_universe(1)` startet das zweite Angebot; liegt ein Zwischengegner an, erscheint er (`boss_slot=True`); ein `next_boost` gilt genau für dieses Universum.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e11 -q && uv run pytest --ignore=tests/spec -q`

---

## E12 — Fabrikator-Menü (`"fabricator"`) in `src/menus.py` & `src/run.py` (`V20` §1, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `E06`, `E10`, `G04`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §1), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/fabricator.py`, `src/menus.py`, `tests/spec/test_phase_e.py` (`-k e12`)
- **Aufgabe:**
  1. Ergänze `draw_fabricator_menu(surface, font, small_font, run, selected_index)` (alle Baupläne mit Kosten in Gold, Proben und Splittern, Status aus `can_build`, verbleibende Bauten) und `Run.craft_selected_recipe(block_key)`, das `fabricator.craft` aufruft und bei voller Modul-Leiste das Modul als Pickup vor die Spielerin legt.
- **Akzeptanzkriterien:**
  - `craft_selected_recipe("funke")` mit Bauplan, Probe und Gold legt `"funke"` in den Rucksack und erhöht `builds_this_visit` um 1.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e12 -q && uv run pytest --ignore=tests/spec -q`

---

## E13 — Händlerplatz & Händler-Menü (`"trader"`) (`V19` §2, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `E05`, `E10`, `E11`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19` §2), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/traders.py`, `src/menus.py`, `tests/spec/test_phase_e.py` (`-k e13`)
- **Aufgabe:**
  1. Besetze in `enter_workshop()` `run.traders = traders_for_workshop(self.plan.visited)` auf `layout.trader_slots` und erzeuge je Händler `run.trader_offers[trader.key] = generate_offers(...)` (Stufe des nächsten Universums). Ergänze `Run.buy_trader_offer(trader_key, index, *, use_samples=False)`.
  2. Ergänze `draw_trader_menu(surface, font, small_font, run, trader_key, selected_index)` mit Begrüßung, Eigenheit, Preisen und `[T]` für den Proben-Tausch.
- **Akzeptanzkriterien:**
  - Vor dem ersten Universum steht kein Händler da; nach zwei besuchten Universen stehen genau deren 2 Heimat-Händler mit je 4 Angeboten da.
  - `buy_trader_offer` entfernt das gekaufte Angebot.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e13 -q && uv run pytest --ignore=tests/spec -q`

---

## E14 — Minispiele an `ws_automat` & `ws_schiessstand` in `Run` (`V20` §2)

- **Größe:** S
- **Abhängigkeiten:** `E08`, `E09`, `E10`
- **Ziel-Dateien:** `src/run.py`, `src/menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20` §2), `src/minigames/__init__.py`, `src/run.py`, `tests/spec/test_phase_e.py` (`-k e14`)
- **Aufgabe:**
  1. Starte an `"ws_automat"` ein Rätsel (`make_physik_puzzle(None, seed)`) und an `"ws_schiessstand"` den Schießstand: nur mit genug Gold, Einsatz sofort abziehen, je Minispiel 1 Versuch je Besuch (`minigames_played`), `menu_mode = "minigame"`.
  2. Ergänze `Run.step_minigame(dt, action=None, cursor=(80, 60))` (zahlt Belohnung aus: Gold, Probe in den Rucksack, `next_boost`) und `draw_minigame_overlay` in `src/menus.py`.
- **Akzeptanzkriterien:**
  - Ein gewonnener Schießstand setzt `run.next_boost`; ein zweiter Versuch im selben Besuch wird abgelehnt; der Einsatz ist abgezogen.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e14 -q && uv run pytest --ignore=tests/spec -q`

---

## E15 — Trainings-Attrappe in der Werkstatt (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `E10`
- **Ziel-Dateien:** `src/workshop.py`, `src/run.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Trainings-Attrappe“), `src/run.py`, `tests/spec/test_phase_e.py` (`-k e15`)
- **Aufgabe:**
  1. Spawne in `enter_workshop()` an `layout.target_dummy_pos` die unsterbliche Attrappe: `c = run.enemies.spawn("made", …)` mit `c.species = "trainings_attrappe"` und `c.spec = dataclasses.replace(c.spec, key="trainings_attrappe", name_de="Trainings-Attrappe", stance="peaceful", speed=0, stationary=True, melee_damage=0, hp=9999)` (bewegt sich nicht, greift nie an), die erlittenen Schaden sofort zurückheilt, ihn als Sprechblase zeigt (`run.say("Attrappe", f"{int(dmg)} Schaden", …)`) und in `run.dummy_damage_total` aufsummiert.
- **Akzeptanzkriterien:**
  - Ein Treffer auf die Attrappe erhöht `run.dummy_damage_total`, ohne dass sie stirbt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e15 -q && uv run pytest --ignore=tests/spec -q`

---

## E16 — Experimentierliege: 3 Selbstexperimente & Neuwurf (`V18`, `V19` §1)

- **Größe:** S
- **Abhängigkeiten:** `E10`
- **Ziel-Dateien:** `src/run.py`, `src/menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`, `V19` §1), `docs/bibel/07-gegenstaende-und-werkstatt.md` („Selbstexperimente“), `src/perks.py`, `src/run.py`, `tests/spec/test_phase_e.py` (`-k e16`)
- **Aufgabe:**
  1. Ergänze `Run.experiment_offers: list[str]` (3 noch nicht gewählte Perks aus `PERKS`, gezogen beim ersten Benutzen der Liege je Besuch), `Run.pick_experiment(index)` (wendet `apply_perk` an, höchstens 1 je Besuch) und `Run.reroll_experiments()` (kostet `experiment_reroll_price(self.experiment_rerolls)`, Zähler für den ganzen Lauf; ein Gratis-Neuwurf aus der Abtei-Herausforderung `run.inventory.rerolls` wird zuerst verbraucht).
  2. Ergänze `draw_experiment_menu(surface, font, small_font, run, selected_index)` mit Bibel-Namen und Wirkung der 3 Experimente.
- **Akzeptanzkriterien:**
  - Die Liege bietet 3 verschiedene Experimente; der erste Neuwurf kostet 100 Gold, der zweite 200; nach einer Wahl ist die Liege bis zum nächsten Besuch gesperrt.
- **Verifikation:** `uv run pytest tests/spec/test_phase_e.py -k e16 -q && uv run pytest --ignore=tests/spec -q`

---
