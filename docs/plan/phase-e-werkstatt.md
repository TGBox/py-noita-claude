# Phase E — Werkstatt-Hub, Wirtschaft, Händler, Fabrikator & Minispiele (15 atomare S-Karten: `E01`–`E15`)

> Jede Karte hat die Größe **S** (`<= 60–80` geänderte Zeilen, `1–2` Zieldateien + `1` Testdatei, `< 15 KB` zu lesender Kontext).
> Master-Index: [vertraege.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege.md). Alle Werkstatt- und Wirtschafts-Module folgen `V18`–`V20` aus [v18-werkstatt-und-wirtschaft.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md) und `V22` aus [v21-klonita-ui-und-speichern.md](file:///c:/Users/DaniBani/Documents/VisualStudioCodeProjects/py-noita-claude/docs/plan/vertraege/v21-klonita-ui-und-speichern.md).

---

## E01 — Werkstatt-Generator & 10 Stationen (`src/workshop.py`) (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `A03`
- **Ziel-Dateien:** `src/workshop.py`, `tests/test_workshop.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `src/world.py`
- **Aufgabe:**
  1. Erstelle `src/workshop.py` mit `WORKSHOP_SIZE = (640, 360)`, `Station`, `WorkshopLayout`, `STATIONS` (alle 10 Stationen `"ws_portal"` bis `"ws_workbench"` mit ihren exakten Rechtecken und `sprite_key`-Werten aus `V18`), `generate_workshop(world: World) -> WorkshopLayout` und `station_at(layout, cell_x, cell_y, radius=10) -> Station | None`.
- **Akzeptanzkriterien:**
  - `generate_workshop(World(640, 360))` erzeugt eine begehbare Halle mit festem Boden ab `y = 210`, Wasser im Becken bei `"ws_well"` und Luft am `spawn`.
  - `len(layout.stations) == 10`, und `station_at` findet jede der 10 Stationen an ihrem Mittelpunkt.
- **Verifikation:** `uv run pytest tests/test_workshop.py -q && uv run pytest -q`

---

## E02 — Wirtschafts- & Preisformeln (`src/economy.py`) (`V19`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/economy.py`, `tests/test_economy.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`)
- **Aufgabe:**
  1. Erstelle `src/economy.py` mit den 7 reinen Funktionen `creature_gold`, `pile_gold`, `crate_gold`, `mid_boss_gold`, `module_price`, `weapon_price` und `reroll_price` exakt nach `V19`.
- **Akzeptanzkriterien:**
  - `module_price` und `weapon_price` steigen streng monoton mit `rarity_tier`/`wand_tier`, `depth` und `price_factor`.
  - `reroll_price(0) == 20`, `reroll_price(1) == 40`, `reroll_price(2) == 80`.
- **Verifikation:** `uv run pytest tests/test_economy.py -q && uv run pytest -q`

---

## E03 — Gold-Drops für Goldadern & Zwischenbosse in `src/run.py` (`V0c`, `V19`)

- **Größe:** S
- **Abhängigkeiten:** `A03`, `A07`, `E02`
- **Ziel-Dateien:** `src/run.py`, `tests/test_economy.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v00-migration-und-schluessel.md` (`V0c`), `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `src/run.py`
- **Aufgabe:**
  1. Nutze in `Run.update` (`src/run.py`) `creature_gold` bzw. `mid_boss_gold` (wenn `c.spec.is_mid_boss`) für den Gold-Drop besiegter Kreaturen.
  2. Prüfe in `Run.update` `gold_cells = self.world.take_destroyed_gold_vein_cells()`: Für je `6` abgebaute `"gold_vein"`-Zellen wird ein `"gold"`-Pickup (`amount = 5`) nahe der Spielerin gespawnt (und bei `>= 18` Zellen zusätzlich zu `25 %` eine `"probe_gold"`).
- **Akzeptanzkriterien:**
  - Besiegen eines Zwischenbosses auf `depth == 2` lässt ein `"gold"`-Pickup mit `mid_boss_gold(2) == 75` fallen.
  - Sprengen von `12` `"gold_vein"`-Zellen erzeugt `"gold"`-Pickups im Gesamtwert von mindestens `10` Gold.
- **Verifikation:** `uv run pytest tests/test_economy.py -k drops_and_veins -q && uv run pytest -q`

---

## E04 — Händler-Katalog & Angebotsgenerator (`src/traders.py` Teil 1) (`V19`)

- **Größe:** S
- **Abhängigkeiten:** `A02`, `A04`, `E02`
- **Ziel-Dateien:** `src/traders.py`, `tests/test_traders.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `src/spells.py`
- **Aufgabe:**
  1. Erstelle `src/traders.py` mit `TraderOffer`, `TraderSpec`, `TRADERS` (alle 6 Händler aus `V19`), `pick_trader_for_universe(universe_key, rng)` und `generate_offers(trader, depth, rng, *, price_factor=1.0, universe_sample_key="probe_rost") -> list[TraderOffer]`.
  2. Setze in `generate_offers` die Sortiments- und Preisregeln um:
     - `"npc_magenhaendler"`: organische Payloads + 1 `"heart"`.
     - `"npc_sachbearbeiterin"`: `flat_fee = 10` auf jedes Angebot aufgeschlagen.
     - `"npc_glibberhaendler"`: Modifikator-Blöcke + `"flask"` (`"jelly"`/`"honey"`).
     - `"npc_ameisenhehler"`: `price_multiplier = 0.75` und `sample_cost = ((universe_sample_key, 2),)` auf Modul-Angeboten.
     - `"npc_dj"`: Blitz-/Klang-Module.
     - `"npc_kuester"`: Schutz-Module + Zauberstab-Angebote mit `blessed = True`.
- **Akzeptanzkriterien:**
  - `len(TRADERS) == 6`; `generate_offers` liefert für jeden Händler genau `4` Angebote, die seine Sortiments-, Gebühren-, Proben-Tausch- bzw. `blessed`-Regel erfüllen.
- **Verifikation:** `uv run pytest tests/test_traders.py -k offers -q && uv run pytest -q`

---

## E05 — Händler-Kaufabwicklung & Sonderregeln (`src/traders.py` Teil 2) (`V19`)

- **Größe:** S
- **Abhängigkeiten:** `A08`, `E04`
- **Ziel-Dateien:** `src/traders.py`, `tests/test_traders.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `src/traders.py`
- **Aufgabe:**
  1. Ergänze in `src/traders.py` `buy_offer(run: Run, trader: TraderSpec, offer: TraderOffer, *, use_samples: bool = False) -> tuple[bool, str]`:
     - Prüft bei `"npc_dj"`, ob `run.in_workshop` im `0.75 s`-Takt (`int(run.time / 0.75) % 2 == 0`) bzw. im Universum `run.universe.rule.on_beat` aktiv ist; falls nicht: Rückgabe `(False, "Nicht im Takt!")`.
     - Bei `use_samples == True` und `offer.sample_cost`: zieht die Proben über `run.inventory.take_samples(...)` ab; sonst zieht es `offer.gold_cost` von `run.gold` ab (unter Berücksichtigung von `-20 %` Rabatt, falls `run.player.body.stamped_good > 0` oder `run.next_boost == "discount"`).
     - Bei `"npc_sachbearbeiterin"` setzt ein erfolgreicher Kauf `run.player.body.stamped_good = 30.0`.
     - Bei `"npc_kuester"` und `offer.blessed == True` erhält der gekaufte Zauberstab `+10 %` `mana_max` und `-10 %` `recharge`.
- **Akzeptanzkriterien:**
  - Alle 6 Händler-Sonderregeln (inkl. DJ-Taktprüfung, Ameisen-Proben-Tausch, Sachbearbeiterin-Stempel und Küster-Segen) sind durch gezielte Unit-Tests in `tests/test_traders.py` abgedeckt.
- **Verifikation:** `uv run pytest tests/test_traders.py -q && uv run pytest -q`

---

## E06 — Fabrikator & Rezept-System (`src/fabricator.py`) (`V20`)

- **Größe:** S
- **Abhängigkeiten:** `A02`, `A04`
- **Ziel-Dateien:** `src/fabricator.py`, `tests/test_fabricator.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `src/spells.py`, `src/samples.py`
- **Aufgabe:**
  1. Erstelle `src/fabricator.py` mit `MAX_BUILDS_PER_VISIT = 3`, `Recipe`, `build_cost(block_key: str) -> Recipe` und `Fabricator` (`builds_this_visit`, `reset_visit`, `can_build`, `craft(run, block_key) -> tuple[bool, str]`) gemäß `V20`.
- **Akzeptanzkriterien:**
  - `build_cost(k)` liefert für jeden Block in `BLOCKS` ein gültiges `Recipe` passend zu `BLOCKS[k].rarity_tier`.
  - Tier-1-Blöcke sind ohne Bauplan baubar; Tier-2- und Tier-3-Blöcke erfordern `block_key in run.records.blueprints`.
  - Nach `3` erfolgreichen Bauten blockiert `can_build` weitere Bauten bis `reset_visit()`.
- **Verifikation:** `uv run pytest tests/test_fabricator.py -q && uv run pytest -q`

---

## E07 — Minispiel-Basis & Physik-o-Mat Rätsel 1–2 (`lava_water`, `acid_gold`) (`V20`)

- **Größe:** S
- **Abhängigkeiten:** keine
- **Ziel-Dateien:** `src/minigames/__init__.py`, `src/minigames/physik_o_mat.py`, `tests/test_minigames.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `src/world.py`
- **Aufgabe:**
  1. Erstelle `src/minigames/__init__.py` mit `MINIGAME_WORLD_SIZE = (160, 120)`, `NEXT_BOOST_KEYS`, `MinigameResult` und der Basisklasse `Minigame` gemäß `V20`.
  2. Erstelle `src/minigames/physik_o_mat.py` mit den ersten 2 Rätseln (`"lava_water"` und `"acid_gold"`), bei denen die Spielerin per Aktion `"use"`/`"carve"` am Cursor einen Riegel öffnet und die `160×120`-Sub-`World` die physikalische Reaktion bis zur Siegbedingung ausführt.
- **Akzeptanzkriterien:**
  - Öffnen des Riegels im `"lava_water"`- und im `"acid_gold"`-Rätsel führt innerhalb von `120` Simulations-Steps zum Sieg (`result.won == True`, `reward_gold == 25`, `result.next_boost in NEXT_BOOST_KEYS`).
- **Verifikation:** `uv run pytest tests/test_minigames.py -k physik_part1 -q && uv run pytest -q`

---

## E08 — Physik-o-Mat Rätsel 3–4 (`oil_fire`, `electricity_water`) (`V20`)

- **Größe:** S
- **Abhängigkeiten:** `E07`
- **Ziel-Dateien:** `src/minigames/physik_o_mat.py`, `tests/test_minigames.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `src/minigames/physik_o_mat.py`
- **Aufgabe:**
  1. Ergänze in `src/minigames/physik_o_mat.py` die Rätsel `"oil_fire"` (Ölspur zu 3 Dochten entzünden) und `"electricity_water"` (Salzwasser-Leitung zwischen zwei Elektroden schließen) sowie die Fabrikfunktion `make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame`.
- **Akzeptanzkriterien:**
  - Alle 4 Rätsel in `PUZZLE_KEYS = ("lava_water", "acid_gold", "oil_fire", "electricity_water")` sind lösbar und laufen bei Nichtstun nach `time_limit` Sekunden sauber mit `won == False` ab.
- **Verifikation:** `uv run pytest tests/test_minigames.py -k physik_part2 -q && uv run pytest -q`

---

## E09 — Schießstand-Minispiel (`src/minigames/schiessstand.py`) (`V20`)

- **Größe:** S
- **Abhängigkeiten:** `E07`
- **Ziel-Dateien:** `src/minigames/schiessstand.py`, `tests/test_minigames.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `src/minigames/__init__.py`
- **Aufgabe:**
  1. Erstelle `src/minigames/schiessstand.py` mit `SchiessstandMinigame(Minigame)`: bewegt `5` reguläre Zielscheiben und `1` rot markierte Behörden-Attrappe; Schüsse (`action == "shoot"` auf `cursor`) treffen Scheiben im Radius `10 px`. Alle 5 Scheiben vor Ablauf von `15 s` zu treffen gewinnt (`25` Gold + `next_boost`); Treffer auf die Behörden-Attrappe beendet das Spiel mit `won == False`.
- **Akzeptanzkriterien:**
  - Gezielte Schüsse auf die 5 Zielscheiben liefern `result.won == True`; ein Treffer auf die Behörden-Attrappe liefert sofort `result.won == False`.
- **Verifikation:** `uv run pytest tests/test_minigames.py -k schiessstand -q && uv run pytest -q`

---

## E10 — Werkstatt-Modus & Direkt-Stationen (`ws_couch`, `ws_well`, `ws_shredder`, `ws_workbench`) in `Run` (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `E01`, `E06`
- **Ziel-Dateien:** `src/run.py`, `tests/test_workshop_stations.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`, `V20`), `src/workshop.py`, `src/run.py`
- **Aufgabe:**
  1. Ergänze auf `Run` (`src/run.py`) `self.in_workshop: bool = False`, `self.workshop_layout: WorkshopLayout | None = None`, `self.fabricator = Fabricator()`, `self.couch_used: bool = False`, `self.minigame_used: set[str] = set()`, `self.next_boost: str = ""`, `self.price_factor: float = 1.0`, `self.menu_mode: str = ""` sowie `enter_workshop(self) -> None` und `interact_station(self) -> str | None`.
  2. Behandle in `interact_station(self)` die Direkt-Stationen:
     - `"ws_couch"`: heilt einmal pro Besuch `+35 %` `max_hp`.
     - `"ws_well"`: füllt `self.flask` kostenlos auf `"water"` (`amount = max_amount`).
     - `"ws_workbench"`: öffnet das Zauberstab-Inventar (`self.inventory_open = True`).
     - `"ws_portal"`, `"ws_fabricator"`, `"ws_trader"`, `"ws_archive"`: setzt `self.menu_mode` auf `"portal_select"`, `"fabricator"`, `"trader"` bzw. `"archive"`.
- **Akzeptanzkriterien:**
  - `run.enter_workshop()` baut die `640×360`-Werkstatt auf, setzt die Spielerin auf `workshop_layout.spawn` und ruft `fabricator.reset_visit()` auf.
  - Interaktion an `"ws_couch"` heilt `+35 %` `max_hp` genau einmal pro Besuch; `"ws_well"` füllt die Flasche mit `"water"`.
- **Verifikation:** `uv run pytest tests/test_workshop_stations.py -q && uv run pytest -q`

---

## E11 — Portal-Auswahl-Menü (`"portal_select"`) & `UniversePlan`-Weiterschaltung (`V9`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `D10`, `E10`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`, `tests/test_workshop_menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/universes/plan.py`, `src/menus.py`, `src/run.py`
- **Aufgabe:**
  1. Ergänze auf `Run` `self.plan: UniversePlan = UniversePlan(seed)` und die Methode `choose_next_universe(self, offer_index: int) -> None`, die aus `self.plan.offers_for(self.depth)` das gewählte Universum (`0` oder `1`) via `self.plan.choose(self.depth, key)` festlegt, `self.in_workshop = False` setzt, das gewählte Universum lädt und einen eventuell aktiven `self.next_boost` (`"mana_regen"`, `"max_hp"`, `"gold_magnet"`, `"discount"`) für dieses Universum anwendet.
  2. Ergänze in `src/menus.py` `draw_portal_select_menu(surface, font, small_font, offers, selected_index)` mit deutschen Karten für beide Universums-Angebote (Name, Untertitel, Weltregel, Heimat-Probe, Endboss).
- **Akzeptanzkriterien:**
  - Beim Verlassen eines Universums (`depth < 5`) wechselt `Run` in die Werkstatt (`in_workshop == True`), und `choose_next_universe(1)` startet das zweite angebotene Universum mit aktivem `next_boost`.
- **Verifikation:** `uv run pytest tests/test_workshop_menus.py -k portal_select -q && uv run pytest -q`

---

## E12 — Fabrikator-Menü (`"fabricator"`) in `src/menus.py` & `src/run.py` (`V20`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `E06`, `E10`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`, `tests/test_workshop_menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/fabricator.py`, `src/menus.py`
- **Aufgabe:**
  1. Ergänze in `src/menus.py` `draw_fabricator_menu(surface, font, small_font, run, selected_index)` (zeigt alle Blöcke mit Tier, Rezeptkosten in Proben + Gold, Status aus `fabricator.can_build` und verbleibende Bauten `3 - builds_this_visit`).
  2. Ergänze auf `Run` `craft_selected_recipe(self, block_key: str) -> tuple[bool, str]`, das `self.fabricator.craft(self, block_key)` aufruft und den gebauten Zauberblock ins Inventar legt (oder als Pickup vor die Spielerin spawnt, falls die Modul-Leiste voll ist).
- **Akzeptanzkriterien:**
  - `craft_selected_recipe("spark")` zieht Proben und Gold ab, legt `"spark"` ins Inventar und erhöht `fabricator.builds_this_visit` um `1`.
  - `draw_fabricator_menu` rendert fehlerfrei auf ein Offscreen-Surface.
- **Verifikation:** `uv run pytest tests/test_workshop_menus.py -k fabricator -q && uv run pytest -q`

---

## E13 — Händler-Menü (`"trader"`) & Händler-Begegnungen in Werkstatt und Universum (`V19`, `V22`)

- **Größe:** S
- **Abhängigkeiten:** `E05`, `E10`
- **Ziel-Dateien:** `src/menus.py`, `src/run.py`, `tests/test_workshop_menus.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V19`), `docs/plan/vertraege/v21-klonita-ui-und-speichern.md` (`V22`), `src/traders.py`, `src/menus.py`
- **Aufgabe:**
  1. Ergänze auf `Run` `self.active_trader: TraderSpec | None = None` und `self.trader_offers: list[TraderOffer] = []` (wird beim Betreten von Werkstatt und Universum über `pick_trader_for_universe` + `generate_offers` befüllt) sowie `buy_trader_offer(self, index: int, *, use_samples: bool = False) -> tuple[bool, str]` und `reroll_trader_offers(self) -> bool`.
  2. Ergänze in `src/menus.py` `draw_trader_menu(surface, font, small_font, run, selected_index)` inklusive Anzeige von `greeting_de`, `quirk_de`, Goldpreis, optionalem Proben-Tauschpreis (`[T]`) und Reroll-Preis (`[R]`).
- **Akzeptanzkriterien:**
  - `buy_trader_offer(0)` kauft das Angebot und entfernt es aus `run.trader_offers`; `reroll_trader_offers()` zieht `reroll_price(...)` Gold ab und generiert 4 neue Angebote.
- **Verifikation:** `uv run pytest tests/test_workshop_menus.py -k trader -q && uv run pytest -q`

---

## E14 — Minispiel-Einbindung (`ws_physik_o_mat` & `ws_schiessstand`) in `src/run.py` & `src/menus.py` (`V20`)

- **Größe:** S
- **Abhängigkeiten:** `E08`, `E09`, `E10`
- **Ziel-Dateien:** `src/run.py`, `src/menus.py`, `tests/test_workshop_stations.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V20`), `src/minigames/__init__.py`, `src/run.py`
- **Aufgabe:**
  1. Ergänze auf `Run` `self.active_minigame: Minigame | None = None`: Aktivieren von `"ws_physik_o_mat"` oder `"ws_schiessstand"` in `interact_station` startet (maximal `1×` pro Werkstatt-Besuch je Station) das jeweilige Minispiel und setzt `self.menu_mode = "minigame"`.
  2. Ergänze `step_minigame(self, dt: float, action: str | None = None, cursor: tuple[int, int] = (80, 60))` auf `Run` (zahlt bei `result.won == True` `reward_gold` aus und setzt `self.next_boost = result.next_boost`) sowie `draw_minigame_overlay` in `src/menus.py`.
- **Akzeptanzkriterien:**
  - Starten und Gewinnen eines Minispiels an `"ws_physik_o_mat"` erhöht `run.gold` um `25`, setzt `run.next_boost` und sperrt die Station für den Rest desselben Werkstatt-Besuchs.
- **Verifikation:** `uv run pytest tests/test_workshop_stations.py -k minigame -q && uv run pytest -q`

---

## E15 — Trainings-Attrappe & DPS-Anzeige in der Werkstatt (`V18`)

- **Größe:** S
- **Abhängigkeiten:** `E10`
- **Ziel-Dateien:** `src/workshop.py`, `src/run.py`, `tests/test_workshop_stations.py`
- **Zu lesender Kontext:** `docs/plan/vertraege/v18-werkstatt-und-wirtschaft.md` (`V18`), `src/workshop.py`, `src/run.py`
- **Aufgabe:**
  1. Spawne in `Run.enter_workshop()` an `workshop_layout.target_dummy_pos` eine unsterbliche Trainings-Attrappe (`species="turret"` mit `stance="peaceful"`, `speed=0`, `reload=9999.0`, `max_hp=9999.0`), die bei erlittenem Schaden ihr HP sofort wieder auffüllt, den letzten Trefferschaden als Sprechblase (`Run.say("Attrappe", f"{int(dmg)} Schaden", ...)`) anzeigt und auf `Run.dummy_damage_total: float` mitzählt.
- **Akzeptanzkriterien:**
  - Ein Spieler-Projektil auf die Trainings-Attrappe in der Werkstatt erhöht `run.dummy_damage_total` um den Projektil-Schaden, ohne dass die Attrappe stirbt oder zurückschießt.
- **Verifikation:** `uv run pytest tests/test_workshop_stations.py -k dummy -q && uv run pytest -q`
