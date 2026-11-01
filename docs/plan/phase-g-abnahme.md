# Phase G – Abnahme

## Q1 Bot-Läufe

### Q1.01 Kompletter Bot-Lauf

- Art: Code · Größe: M · Hängt ab von: U0.11, W1.04, B4.07
- Dateien: `src/bot.py` (`run_full(seed) -> list[BotReport]`), `tests/test_full_run.py` (mit `@pytest.mark.slow`)
- Tun: Werkstatt → 6 Universen → böses Ich; je Universum `run_bot`.

### Q1.02 20 Seeds

- Art: Code · Größe: S · Hängt ab von: Q1.01
- Tun: Skript `tools/bot_runs.py --seeds 20` schreibt Tabelle nach `build/bot_runs.md`.
- Fertig, wenn: 0 Abstürze, alle Anker erreichbar.

## Q2 Leistung

### Q2.01 Leistung messen

- Art: Code · Größe: S · Hängt ab von: Q1.01
- Tun: je Universum Logik p99, Lichtzeit, Generierungszeit, Speicherstand-Größe in `build/leistung.md`.
- Fertig, wenn: p99 < 16 ms, Generierung < 3 s, Speicherstand < 2 MB.

## Q3 Spieltest

### Q3.01 Spieltest

- Art: Nutzer · Tun: Spieltest mit Lauf-Protokoll; Funde als neue Karten (`Q3.xx`) in diese Datei.

### Q3.02 Balance-Runde

- Art: Daten · Größe: S je Fund · Tun: Werte aus Q3.01 anpassen, nur Zahlen.

### Q3.03 Merkliste abhaken

- Art: Code · Größe: S · Tun: jeden Punkt der Merkliste in `docs/bibel/09-arbeitspakete.md` prüfen (Test oder Spielprobe) und abhaken.
