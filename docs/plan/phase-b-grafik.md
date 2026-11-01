# Phase B – Grafik-Werkzeug und Stil

Gemeinsam für alle Grafik-Karten (G1–G5 und Sprites in Phase C):

- Lesen: Bibel 01 ganz (7 KB) und **nur** den Abschnitt der Bibel, der das Motiv beschreibt.
- Eine Grafik-Karte = **ein Motiv** (eine Quelldatei `assets/sprites/<kategorie>/<key>.py`).
- Ablauf: Quelle schreiben → `uv run python -m tools.sprites check <kategorie>/<key>` → `build` → `sheet <kategorie>` → Kontaktbogen `build/sheets/<kategorie>.png` dem Nutzer zeigen.
- Fertig, wenn: `check` sauber und der Nutzer den Kontaktbogen freigegeben hat. Bis zur Freigabe Status „wartet auf Abnahme“.
- Nicht: Spielcode ändern (das machen die Einbau-Karten).

## G0 Werkzeug

### G0.01 Paletten als Daten

- Art: Daten · Größe: S · Hängt ab von: –
- Lesen: V8; Bibel 01 „Hauptpalette“; Bibel 03 je Universum „Teilpalette“
- Dateien: `tools/__init__.py` (falls fehlt), `tools/palette.py` (neu), `tests/test_sprite_tool.py` (neu)
- Tun: `PALETTE` (Hauptpalette, Schlüssel genau wie Bibel) und `PALETTES[<universum>]` mit Schlüsseln `u1`, `u2`, … in Bibel-Reihenfolge.
- Test: alle Werte gültiges `#RRGGBB`; `ink == "#1C1420"`.
- Hinweis: `src/tools.py` existiert schon (Skripte). Der neue Ordner heißt `tools/` auf oberster Ebene; ist das in `pyproject.toml` nicht paketiert, ist das gewollt (Werkzeug, nicht Spiel).

### G0.02 Quelle laden und prüfen

- Art: Code · Größe: S · Hängt ab von: G0.01
- Lesen: V8; Bibel 01 „Dateiformat“, „Animation“ (Pflichtzustände)
- Dateien: `tools/sprites.py` (neu), `tests/test_sprite_tool.py`, `tests/data/sprites/test_blob.py` (neu, 6×6, `idle` 2 Frames, `hurt` 1, `death` 3)
- Tun: `load_source(path) -> SourceSprite` (per `importlib` ausführen), `check(source, universe: str | None) -> list[str]` mit allen Prüfungen aus V8. Pflichtzustände: `idle`, `hurt`, `death`; `move` wenn nicht `STATIC = True`; `windup`+`attack` wenn `ATTACKS = True` (beides optionale Konstanten der Quelle, in V8 so ergänzt).
- Test: Testquelle sauber; je ein kaputter Fall pro Prüfung.

### G0.03 PNG + JSON erzeugen

- Art: Code · Größe: S · Hängt ab von: G0.02
- Lesen: V5 (JSON), V8
- Dateien: `tools/sprites.py`, Test
- Tun: `build(source) -> (Surface, dict)`; Frames nebeneinander in Zustandsreihenfolge; schreibt `assets/sprites_png/<kategorie>/<key>.png/.json`; `glow` je Frame. CLI `build [<kategorie>[/<key>]]`.
- Test: JSON von `test_blob` stimmt (Frames, Zustände, Anker); PNG-Größe = 6 Frames × 6 px.

### G0.04 Kontaktbogen

- Art: Code · Größe: M · Hängt ab von: G0.03
- Lesen: Bibel 01 „Abnahme“
- Tun: CLI `sheet <kategorie>` → `build/sheets/<kategorie>.png`: je Motiv eine Zeile mit allen Frames in 1× und 4×, auf drei Gründen (#1C1420, #E6E2E8, gedimmt 30 %), Beschriftung Schlüssel + Zustand.
- Test: Bildgröße wächst mit Motivanzahl; Datei entsteht.

### G0.05 Silhouettenbogen und Beispielmotiv

- Art: Code + Grafik · Größe: S · Hängt ab von: G0.04
- Tun: CLI `sheet <kategorie> --silhouette` (alle deckenden Pixel in `ink` auf `n5`); erstes echtes Motiv `assets/sprites/effekte/funke.py` (Flux-Funke-Effekt, 5×5, `idle` 3 Frames, leuchtet).
- Fertig, wenn: Nutzer hat beide Bögen gesehen.

### G0.06 Prüfung aller Quellen im Testlauf

- Art: Code · Größe: S · Hängt ab von: G0.02
- Dateien: `tests/test_sprite_sources.py` (neu)
- Tun: parametrisierter Test über alle `assets/sprites/**/*.py`: `check` liefert keine Fehler; zu jeder Quelle existiert ein aktuelles PNG (Änderungszeit Quelle ≤ PNG), sonst Hinweis „`tools.sprites build` vergessen“.

## G1 Figuren

| Karte | Motiv (Datei) | Lesen (Bibel 04) |
| --- | --- | --- |
| G1.01 | `figuren/cloita.py` – `idle`, `run`, `jump`, `fall`, `hurt` | „Cloita“ Aussehen + Zustandstabelle |
| G1.02 | `figuren/cloita.py` – `float`, `kick`, `drink`, `death` ergänzen | dito |
| G1.03 | `figuren/cloita.py` – `swim`, `tiny_scared` ergänzen | dito |
| G1.04 | `figuren/cloita_aim.py` – Überlagerung „Brille unten“ | dito |
| G1.05 | `figuren/klonita.py` – `idle`, `run`, `jump`, `wave` | „Klonita“ |
| G1.06 | `figuren/klonita.py` – `point`, `carry`, `hug`, `feed` | dito |
| G1.07 | `figuren/klonita.py` – `knocked`, `getup`, `cover_ears`, `swim` | dito |
| G1.08 | `figuren/exp_<key>.py` – je sichtbares Selbstexperiment eine Überlagerung (eine Karte je Überlagerung, Liste in Bibel 04 „Sichtbare Selbstexperimente“) | dito |

Alle G1-Karten: Art Grafik, Größe S, hängen von G0.05 ab und jeweils von der vorigen Karte desselben Motivs.

### G1.09 Einbau Spielfigur

- Art: Code · Größe: M · Hängt ab von: G1.01, T6.05
- Lesen: `build_player_sprites` in `src/rendering.py`; `src/player.py`
- Dateien: `src/player.py` (Feld `state`: `idle`/`run`/`jump`/`fall`/`float`/`hurt`/`death` aus Bewegung ableiten), `src/rendering.py`, Test für die Ableitung
- Tun: Spieler zeichnet `figuren/cloita`, falls vorhanden; Überlagerung `cloita_aim` beim Zielen; sonst alter Weg.
- Test: Zustand aus Geschwindigkeit/Bodenkontakt.

## G2 UI

| Karte | Motiv | Lesen |
| --- | --- | --- |
| G2.01 | `ui/logo.py` | Bibel 08 „Logo und Titel“ |
| G2.02 | `ui/icon_flux.py`, `icon_gold`, `icon_herz`, `icon_jetpack` (eine Datei je Icon, eine Karte für alle vier) | Bibel 08 „Neue UI-Icons“ |
| G2.03 | `icon_siegel`, `icon_rang`, `icon_takt`, `icon_atem` | dito |
| G2.04 | `icon_probe`, `icon_bauplan`, `icon_experiment`, `icon_splitter` | dito |
| G2.05 | `icon_anker`, `icon_portal`, `icon_klonita`, `icon_haendler` | dito |
| G2.06 | `ui/sprechblase.py` (9-Slice-Rahmen mit Spitze) | Bibel 08 „Sprechblasen“ |

Icons sind statisch (`STATIC = True`, nur `idle` 1 Frame, `hurt`/`death` entfallen für Kategorie `ui` – Ausnahme in G0.02 berücksichtigen: Kategorien `ui`, `module`, `waffenteile` brauchen nur `idle`).

## G3 Waffenteile

| Karte | Motive (`waffenteile/`) |
| --- | --- |
| G3.01 | `gehaeuse_kurz`, `gehaeuse_mittel`, `gehaeuse_lang` |
| G3.02 | `lauf_einfach`, `lauf_doppel`, `lauf_dreifach` |
| G3.03 | `muendung_spitz`, `muendung_trichter`, `muendung_sieb` |
| G3.04 | `tank_klein`, `tank_mittel`, `tank_gross` (leuchten) |
| G3.05 | `griff_pistole`, `griff_kurbel`, `griff_handschuh` |
| G3.06 | `zier_klebeband`, `zier_antenne`, `zier_wackelauge`, `zier_gluehbirne`, `zier_schraubenzieher` |

Lesen: Bibel 06 „Aussehen aus Teilen“. Jede Teil-Quelle hat zusätzlich `MOUNT = (x, y)` (Andockpunkt) – in V8 als optionale Konstante.

### G3.07 Zusammenbau-Logik

- Art: Code · Größe: S · Hängt ab von: G3.01–G3.06
- Dateien: `src/weapon_parts.py` (neu, headless), Test
- Tun: `parts_for(spec: WandSpec, seed: int) -> tuple[str, ...]` nach Tabelle Bibel 06.
- Test: Plätze 2/6/10 → kurz/mittel/lang; Mischen → Klebeband.

### G3.08 Zusammenbau zeichnen + Vorschau

- Art: Code · Größe: M · Hängt ab von: G3.07, T6.03
- Dateien: `src/rendering.py` (`draw_augmentation` nutzt Teile, falls Bögen da), `tools/weapon_preview.py` (20 Zufallswaffen → `build/sheets/waffen.png`)
- Fertig, wenn: Nutzer hat die Vorschau freigegeben.

## G4 Modul-Icons

- G4.01–G4.06: je 10 Icons der 60 Basismodule aus Bibel 06 (Reihenfolge der Tabellen: Geschosse 1–10, 11–20, 21–24 + Aufsätze 1–6, Aufsätze 7–16, Aufsätze 17–22 + Zünder 4, Füllungen 10). Art Grafik, Größe M (10 statische 16×16-Icons).
- G4.07 Einbau: `src/icons.py` nutzt Bogen `module/<key>`, falls vorhanden; Familien-Generator (grep `family` in `src/icons.py`) färbt Rahmen nach Kategorie (Bibel 06 „Kategorien“). Art Code, Größe M.

## G5 Gegenstände

- G5.01 `gold_muenze`, `gold_haufen_s/m/l` · G5.02 `kolben`, `modul` (Kassette) · G5.03 `lebenskapsel`, `fundkiste` · G5.04 `erinnerungssplitter`, `wackelportal`, `anker` · G5.05 `bauplan_splitter`, `dienstausweis` · G5.06–G5.07 die 12 Proben (je 6; 7×7 Welt + 12×12 Icon als Zustand `icon`).
- Lesen: Bibel 07 „Gegenstände in der Welt“, „Proben“. Art Grafik, Größe S–M.
- G5.08 Einbau: `draw_pickups` in `src/rendering.py` nutzt Bögen `gegenstaende/<key>`, falls vorhanden. Art Code, Größe S.
