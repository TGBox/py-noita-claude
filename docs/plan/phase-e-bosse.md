# Phase E – Bosse, Endkampf, Behörde

Lesen für alle Karten: der jeweilige Abschnitt aus Bibel 05. Bosse sind `CreatureSpec` mit `boss=True` und einem **Phasen-Skript**.

## B0 Phasen-Rahmen (vor B1)

### B0.01 Phasen-Skript

- Art: Code · Größe: M · Hängt ab von: T5.21
- Dateien: `src/bosses/__init__.py` (neu), `tests/test_bosses.py` (neu)
- Tun: `BossPhase(name, until_hp_share, enter(boss, run), update(boss, run, dt))`; `BossScript(phases)` wechselt bei Leben ≤ 66 % / 33 % (Bibel 05 „Zwischengegner“), `emit("boss_phase", ...)`; Phasenwechsel = 1 s unverwundbar + Zustand `phase_change`.
- Test: Dummy-Boss durchläuft 3 Phasen in Reihenfolge.

### B0.02 Bossplatz einbinden

- Art: Code · Größe: S · Hängt ab von: B0.01, W1.04, U0.12
- Tun: Auf Bossplatz spawnt der Zwischengegner in `Level.arena`; Anker lässt sich erst nach seinem Tod benutzen; Gold W2.02, 1 Bauplan-Splitter.
- Test: Anker gesperrt, nach Tod frei.

### B0.03 Boss-Sprechblase oben

- Art: Code · Größe: S · Hängt ab von: B0.01
- Lesen: Bibel 08 „Sprechblasen“
- Tun: `Run.boss_line(text)` zeigt Text am oberen Rand 3 s.

## B1–B3 Zwischengegner

Je Boss dieselbe Kartenfolge (Art Code, Größe S–M, außer Sprites):

| Schritt | Inhalt |
| --- | --- |
| Bx.y.1 | Werte (`CreatureSpec`), Arena-Anpassung im Heimat-Generator |
| Bx.y.2 | Phase 1 |
| Bx.y.3 | Phase 2 |
| Bx.y.4 | Phase 3 |
| Bx.y.5 | Körper aus Teilen (`PartLayout`), falls Bibel „aus Teilen“ sagt |
| Bx.y.6 | Sprites (Grafik, je Teil eine Karte) |
| Bx.y.7 | Test: Bot-Kampf im Gottmodus mit festem Schaden – alle 3 Phasen erreicht, kein Absturz |

| Boss | Karten-ID | Heimat (hängt ab von) |
| --- | --- | --- |
| Oberstempler | B1.1.1–B1.1.7 | U2.16 |
| Mutter Glibber | B1.2.1–B1.2.7 | U3.16, T5.16 (Teilen) |
| DJ Myzel | B2.1.1–B2.1.7 | U5.16 |
| Abt Kieme | B2.2.1–B2.2.7 | U6.16 |
| Ameisenkönigin | B3.1.1–B3.1.7 | U4.16 |
| Weltenherz | B3.2.1–B3.2.7 | U1.16 |

## B4 Böse Ichs

### B4.01 Heimat-Generator je böses Ich

- Art: Code · Größe: M je Ich (3 Karten B4.01a/b/c) · Hängt ab von: U0.03
- Tun: 1280×720-Sonderwelt; `boese_kaiserin` mit Material `goldboden` (rutschig, eigener Mini-Satz), `boese_gute` mit umgekehrter Dunkelheit (Licht schadet), `boese_omega` Fabrikhalle mit Fließbändern.

### B4.02 Gegnerwaffe mit Modulen

- Art: Code · Größe: S · Hängt ab von: T5.13
- Tun: böses Ich trägt eine echte `WandSpec`; nach Sieg fällt sie als Pickup (erbeutbare Waffe).

### B4.03–B4.05 Phasen je böses Ich

- Je Ich eine Karte mit 4 Phasen (Art Code, Größe M) auf Basis B0.01 (4 Phasen statt 3: Grenzen 75/50/25 %).

### B4.06 Verhandlung der Kaiserin und böses Ende

- Art: Code · Größe: S · Hängt ab von: B4.03
- Tun: Phase 2 Angebot (Ja/Nein-Menü); Ja → Lauf endet, Archiv-Eintrag „Böses Ende“.

### B4.07 Sieg und Ende

- Art: Code · Größe: S · Hängt ab von: B4.03–B4.05, W1.04
- Tun: Sieg-Bildschirm, NG+-Angebot (vorhandene `new_game_plus`, Faktor +0,6), Archiv.

### B4.08 Sprites böse Ichs

- Art: Grafik · je Ich 1–3 Karten · Lesen: Bibel 04 „Böse Ichs (Optik)“.

## B5 Behörde

B5.01–B5.04 werden **vor U2** gebraucht.

### B5.01 Fahndungsstufe

- Art: Code · Größe: S · Hängt ab von: T5.21
- Lesen: V15; Bibel 02 „Fahndungsstufe“
- Dateien: `src/authority.py` (neu), `src/run.py` (Feld `wanted`, Speichern), `tests/test_authority.py` (neu)
- Test: Grenzen 0–5; 5000 Zellen → +0,5; Werkstatt −1.

### B5.02 Auslöser

- Art: Code · Größe: S · Hängt ab von: B5.01
- Tun: Hörer auf `kill` (neutral/passiv +0,25), `trader_killed` (+1), `cells_destroyed` (Kern meldet zerstörte Zellen – grep `destroyed` in `src/world.py`; fehlt die Zählung, eigene Karte B5.02a), `steal` im Laden (+2).

### B5.03 Agenten

- Art: Daten · Größe: S · Hängt ab von: T5.21
- Tun: 3 `CreatureSpec` aus Bibel 05 „Behörden-Agenten“ (Faktion `authority`), `spawn_agents` (am Rand der Simulationszone, außer Sicht).

### B5.04 Agenten nach Stufe

- Art: Code · Größe: S · Hängt ab von: B5.02, B5.03
- Tun: beim Betreten eines Universums `agent_count()` Agenten; Typen nach Stufe (V15).

### B5.05 Drohne markiert

- Art: Code · Größe: S · Hängt ab von: B5.03
- Tun: `agent_drohne` markiert Cloita 10 s → alle Agenten kennen ihre Position (`hunt` ohne Sicht).

### B5.06 Durchsagen

- Art: Text · Größe: S · Tun: Durchsagen-Texte (Bibel 08) bei Stufenwechsel.

### B5.07 Dienstausweis

- Art: Code · Größe: S · Hängt ab von: U0.08, B5.03
- Tun: seltener Drop `dienstausweis` → Archiv-Fundstück.

### B5.08 HUD-Sterne

- Art: Code · Größe: S · Hängt ab von: B5.01, G2.03
- Tun: Sterne neben dem Gold (`src/hud.py`).

### B5.09 Agenten-Sprites

- Art: Grafik · 3 Karten · Lesen: Bibel 04 „Behörden-Agenten“.

## B6 Wahres Ende

### B6.01 Erinnerungssplitter zählen

- Art: Code · Größe: S · Hängt ab von: U0.08
- Tun: `Run.memory_shards` (0–6); `true_ending()` = 6 Splitter und böses Ich besiegt (vorhandene Funktion anpassen).

### B6.02 Portal zum Hauptquartier

- Art: Code · Größe: S · Hängt ab von: B6.01, B4.07
- Tun: statt Sieg-Bildschirm Portal zu `enter_headquarters()`.

### B6.03 Stufe 1 „Die Anhörung“

- Art: Code · Größe: M · Hängt ab von: B6.02, B5.03
- Tun: Arena mit Pult, 5 Räte, Agentenwellen, Formular-Regen (Bibel 05 „Wahres Ende“).

### B6.04 Stufe 2 „Die bösen Ichs“

- Art: Code · Größe: M · Hängt ab von: B6.03, B4.03–B4.05
- Tun: die zwei nicht besiegten Ichs nacheinander mit verkürzter Phasenfolge (2 Phasen).

### B6.05 Stufe 3 „Ober-Cloita“

- Art: Code · Größe: M · Hängt ab von: B6.04, T6.07
- Tun: `ober_cloita` (96×96 aus Teilen, 6000 Leben, 3 Phasen mit Angriffen der Ichs, letzte gemischt).

### B6.06 Abspann und Archiv

- Art: Code + Text · Größe: S · Tun: Text-Abspann, Archiv-Eintrag „Wahres Ende“, Ober-Cloita im Archiv sichtbar; ab 3 Siegen Splitter-Hinweise im Archiv.
