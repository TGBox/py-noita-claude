# Phase D – Werkstatt und Wirtschaft

Lesen für alle W-Karten: Bibel 07 „Die Werkstatt“ und den in der Karte genannten Abschnitt. Die heutige Werkstatt heißt im Code noch `sanctum` (`generate_sanctum`, `Run.enter_sanctum`).

## W1 Werkstatt und Lauf-Ablauf

### W1.01 Werkstatt-Layout als Daten

- Art: Daten · Größe: S · Hängt ab von: –
- Dateien: `src/workshop.py` (neu), `tests/test_workshop.py` (neu)
- Tun: `WORKSHOP_SIZE = (640, 360)`; `STATIONS: tuple[Station, ...]` mit `key`, `name_de`, `size`, `pos` (Fußpunkt) für alle 10 Stationen aus Bibel 07; `Station.rect`.
- Test: keine Überlappung, alle innerhalb der Karte, Abstand zum Boden 0.

### W1.02 Werkstatt-Karte erzeugen

- Art: Code · Größe: M · Hängt ab von: W1.01
- Lesen: `generate_sanctum`, `SanctumLayout` in `src/worldgen.py`
- Dateien: `src/worldgen.py`, `src/workshop.py`, Test
- Tun: `generate_workshop(world) -> WorkshopLayout` (640×360, Boden + Wände aus `bedrock`, Plattformen für Stationen). `generate_sanctum` ruft künftig `generate_workshop` (alter Name bleibt als Alias bis R1).
- Test: jede Station steht auf festem Boden; Spieler-Spawn frei.

### W1.03 Stationen ansprechen

- Art: Code · Größe: S · Hängt ab von: W1.02
- Dateien: `src/workshop.py` (`station_at(x, y, reach=24) -> Station | None`), `src/run.py` (Taste E → `emit("station", key=...)`), Test
- Nicht: was die Station tut (eigene Karten).

### W1.04 Lauf über RunPlan

- Art: Code · Größe: M · Hängt ab von: U0.05, W1.03
- Lesen: `src/universes/plan.py`; `Run.new_run`, `_descend`, `enter_sanctum`
- Dateien: `src/run.py`, `tests/test_run.py`
- Tun: `Run.plan: RunPlan` (Seed aus Lauf); Ablauf Werkstatt → Universum → Werkstatt; Ankerpunkt öffnet Portal zur Werkstatt (vorhandenes Ausgangs-Portal); nach 6 Universen → `enter_evil_home()` (Platzhalter: Sieg, bis B4); Plan speichern/laden.
- Test: 6 Wechsel, jedes Universum einmal, Ränge 1,1,2,2,3,3.

### W1.05 Portalrahmen mit zwei Vorschlägen

- Art: Code · Größe: M · Hängt ab von: W1.04
- Lesen: `RunPlan.offers`, `Offer`; `src/menus.py` (vorhandenes Auswahl-Menü als Muster, z. B. Perk-Altar)
- Dateien: `src/menus.py`, `src/run.py`, Test für die Menü-Logik (ohne Zeichnen)
- Tun: Station `ws_portal` öffnet Auswahl mit Name, Regel (`describe_de`), Rang, Zwischengegner ja/nein und wer.
- Test: Auswahl 2 → `plan.choose(1)`.

### W1.06 Heilen, Speichern, Fahndung in der Werkstatt

- Art: Code · Größe: S · Hängt ab von: W1.04, B5.01
- Tun: beim Betreten volle Heilung, Speicherpunkt (vorhandenes Werkstatt-Speichern), `wanted.on_workshop()`.
- Test: alle drei Wirkungen.

### W1.07 Zapfanlage

- Art: Code · Größe: S · Hängt ab von: W1.03, W2.01
- Tun: `ws_zapfhahn`: 10 Gold → aktiver Kolben mit `fluxschnaps` gefüllt.
- Test: Gold sinkt, Kolben voll; ohne Gold nichts.

### W1.08 Alte Tiefen entfernen

- Art: Code · Größe: M · Hängt ab von: W1.04, alle U*.16
- Lesen: `src/depths.py`, Verwendungen per grep `DEPTHS`, `enter_depth`
- Tun: `enter_depth`, Tiefen-Route und Sandbox-Tiefenwahl entfernen; Sandbox nutzt U0.06. `src/depths.py` nur noch für Parallelwelten-Daten, falls nötig, sonst löschen.
- Fertig, wenn: kein Import von `DEPTHS` außerhalb von Tests; Tests angepasst.

### W1.09 Werkstatt-Stationen: Sprites

- Art: Grafik · je Station eine Karte (10) · Hängt ab von: G0.05
- Lesen: Bibel 07 Stationen-Tabelle. Zustände `idle` 2–4, `use` 2–4, `STATIC` nicht gesetzt.

## W2 Gold, Preise, Händler

### W2.01 Gold als Gegenstand

- Art: Code · Größe: M · Hängt ab von: U0.08
- Lesen: `scatter_pearls`, `_collect_pearls`, `PEARL_COLOR`; Bibel 02 „Wirtschaft“
- Dateien: `src/loot.py`, `src/run.py`, Test
- Tun: `Run.gold` (Speicherfeld; Lesen alter `pearls` als Gold beim Laden), Pickups `gold_muenze`/`gold_haufen_*`, Einsammeln bei Berührung.
- Nicht: Anzeige umbenennen (R2).

### W2.02 Gold-Mengen je Rang

- Art: Daten · Größe: S · Hängt ab von: W2.01
- Dateien: `src/economy.py` (neu), Test
- Tun: Tabellen aus Bibel 02 „Wirtschaft“ als Funktionen `creature_gold(spec, rank, rng)`, `pile_gold(rank, rng)`, `crate_gold(rank, rng)`, `mid_boss_gold(rank)`.

### W2.03 Preise

- Art: Daten · Größe: S · Hängt ab von: W2.02
- Dateien: `src/economy.py`, `src/loot.py` (`block_price`, `wand_price` delegieren), Test
- Tun: Ausgaben-Tabelle Bibel 02; Faktor `price_factor` (1,0; nach Raub 1,5) als Parameter.

### W2.04 Händler-Daten

- Art: Daten · Größe: S · Hängt ab von: T5.19
- Lesen: Bibel 04 „Händler“
- Dateien: `src/traders.py` (neu), Test
- Tun: 6 Händler (`npc_*`), Universum, Spezialität (Kategorie), 5 Sprüche (Bibel 08) als `CreatureSpec` mit Haltung `trader`.

### W2.05 Händlerplatz in der Werkstatt

- Art: Code · Größe: M · Hängt ab von: W2.04, W1.04
- Tun: bis zu 2 Händler aus besuchten Universen am `ws_haendler`; Angebot (Module der Spezialität, Preise W2.03); Kauf mit E (vorhandene Laden-Logik `price_of`, `can_afford` weiterverwenden).
- Test: nur besuchte Universen; max. 2.

### W2.06 Ausrauben und Folgen

- Art: Code · Größe: S · Hängt ab von: W2.05, B5.01
- Tun: Händler getötet → `trader_killed`, Preise ×1,5 für den Lauf (`Run.price_factor`), Fahndung +1; Diebstahl im Laden (Gegenstand ohne Bezahlung aufheben) +2.
- Test: beide Fälle.

### W2.07 Händler-Sprites

- Art: Grafik · 6 Karten (`npc/<key>.py`, `idle` 4, `talk` 2) · Lesen: Bibel 04 „Händler“.

## W3 Proben, Baupläne, Fabrikator

### W3.01 Baupläne im Archiv

- Art: Code · Größe: S · Hängt ab von: –
- Lesen: `Records.discover` in `src/records.py`
- Tun: jedes erhaltene Modul → `discover("blueprint", key)`; `Records.blueprints() -> frozenset[str]`.

### W3.02 Bau-Kosten

- Art: Daten · Größe: S · Hängt ab von: W2.03, U0.08
- Lesen: Bibel 02 „Fabrikator“; Bibel 06 Seltenheit
- Dateien: `src/fabricator.py` (neu), Test
- Tun: `build_cost(module_key) -> (gold, samples: dict[str, int], needs_shard: bool)`; Füllung mit Universumsmaterial braucht Probe dieses Universums.

### W3.03 Fabrikator bauen

- Art: Code · Größe: S · Hängt ab von: W3.01, W3.02
- Tun: `Fabricator.build(run, key) -> str | None` (Fehlertext oder None); max. 3 Bauten je Werkstatt-Besuch (Zähler zurück bei `enter_workshop`).
- Test: 4. Bau verweigert; fehlende Probe verweigert.

### W3.04 Fabrikator-Menü

- Art: Code · Größe: M · Hängt ab von: W3.03, W1.03
- Dateien: `src/menus.py`, Test der Menü-Logik
- Tun: Liste der Baupläne mit Kosten, ausgegraut wenn unbezahlbar.

### W3.05 Bauplan-Splitter

- Art: Code · Größe: S · Hängt ab von: U0.08, W3.03
- Tun: Pickup `bauplan_splitter` (selten in Kisten, 1 von jedem Zwischengegner); Zähler `Run.blueprint_shards`.

## W4 Minispiele

### W4.01 Minispiel-Rahmen

- Art: Code · Größe: M · Hängt ab von: W1.03
- Dateien: `src/minigames/__init__.py` (neu), `src/run.py`, Test
- Tun: `Minigame` mit `stake`, `start(run)`, `update(run, dt) -> bool` (fertig), `reward(run)`; ein Versuch je Minispiel und Werkstatt-Besuch; Feld 160×120 als eigene kleine `World`.

### W4.02–W4.05 Physik-o-Mat-Rätsel

- Je Rätsel eine Karte (Art Code, Größe M): „Füll das Glas“, „Rette die Vase“, „Zünde die Kerze“, „Ameisenstraße“ (braucht U4.06). Lesen: Bibel 07 „Minispiele“. Jede Karte: Aufbau des Felds, Gewinnbedingung als Funktion, Test mit gelöster und ungelöster Welt.

### W4.06 Schießstand

- Art: Code · Größe: M · Hängt ab von: W4.01
- Tun: 30 s, Pappfiguren (Agent +1, Klonita −2) tauchen auf; Belohnung: Schub fürs nächste Universum nach Punkten (`Run.next_boost`).

### W4.07 Schub anwenden

- Art: Code · Größe: S · Hängt ab von: W4.06
- Tun: `next_boost` beim Betreten des nächsten Universums anwenden, beim Verlassen löschen.
