# Critique

Du hast einiges umgebaut und dazu eine Test-Suite eingecheckt. Ich verschaffe mir zuerst den Überblick und prüfe dann Verweise, Schnittstellen und Abhängigkeiten über alle Dateien hinweg.

Gleicher Stand wie lokal (31a29a0). Ich lasse die Tests hier laufen.

Die Verträge widersprechen in mehreren Kernzahlen der Bibel: 9 statt 6 Universen, andere Haltungen, 11 Fraktionen. Ich prüfe, ob sich die Bibel geändert hat oder ob der Plan davon abweicht.

Die Bibel ist unverändert (6 Universen, 12 Proben). Jetzt schaue ich, was die Spec-Tests tatsächlich verlangen, denn die erzwingen am Ende das Verhalten.

Auffällig: Fast alle Namen, die die Tests importieren, gibt es schon in `src/`, aber rund 70 davon in keinem Vertrag. Ich schaue, ob der Code in `src/` fertig ist oder nur Gerüst.

Nein, in diesem Zustand sollte noch kein günstiges Modell mit den Karten anfangen. Formal ist der Plan sauber, inhaltlich beschreibt der größte Teil aber ein anderes Spiel als die Bibel. Außerdem verlangen die Tests teils Dinge, die die Verträge anders festlegen oder gar nicht festlegen.

Ausführen konnte ich die Tests nicht: pygame-ce ließ sich weder hier noch in der Linux-VM auf deinem Rechner installieren, und den Rust-Kern zu bauen wurde blockiert. Ich habe deshalb statisch geprüft: Karten, Verträge, Spec-Tests, Gerüste in `src/` und Bibel, gegeneinander und per Skript.

## Was stimmt

- Die Zählung stimmt: 134 Karten (26+36+17+16+15+14+10), jede Karte hat einen Testverweis.
- Es gibt keine unbekannten Abhängigkeiten, keine Vorwärtsverweise innerhalb einer Phase und keine Verweise auf V-Nummern, die nirgends definiert sind.
- Die Verträge v00, v01, v05 und v09 folgen der Bibel und sind gut. V0a legt zum Beispiel genau die 12 Bibel-Proben und die Teilgebiete fest. V0d schließt die offenen Fragen (Blattlaus, Krypta-Strömung) sinnvoll.

## Kritisch: blockiert die Umsetzung

1. **Zwei Spielwelten nebeneinander.**
   - Bibel, `catalog.py`, v00, v01, v05 und v09: 6 Universen (Fleischwelt … Abtei).
   - Alle Phasenkarten A–G, alle Spec-Tests und die Verträge v11, v15, v18 und v21: **9 erfundene Universen** (`schrott`, `myzel`, `magen`, `amt`, `kuchen`, `abtei`, `ameisen`, `spule`, `glibber`). Dazu kommen 14 Proben (`probe_rost`, `probe_salz` …), 36 Kreaturen, 9 Endbosse, Stationen wie `ws_shredder` und `ws_well` sowie böse Ichs „im Secret-Raum von Universum 2–4“.
   - Nichts davon steht in der Bibel. Das widerspricht deiner eigenen Regel in `docs/intent/` („die Bibel schlägt Plan-Abkürzungen“).

2. **Spec-Tests und Verträge widersprechen sich direkt.**
   - **A01** verlangt `probe_rost` usw., V0a verlangt `probe_gallenstein` usw.
   - **A11:** V4 legt `Grudges`/`hostile()` mit 4 Fraktionen fest. Der Test verlangt `FACTIONS` mit 11 Fraktionen, `are_hostile` und `record_grudge`. Die Karte sagt „gemäß V4“. Welche 11 Fraktionen und welche Hass-Matrix gemeint sind, steht nirgends. Das Gerüst `src/factions.py` hat sogar 13 Einträge.
   - **A10:** Der Test ruft `next_waypoint(w, x, y, x, y, "fly", cache, now=…)` auf, V3 legt `PathFollower.next_waypoint(creature, world, goal, dt)` fest.
   - **A24/D:** V9 legt `Level.regions` als Dict fest, die Tests behandeln es als Liste von Tupeln.
   - Insgesamt importieren die Spec-Tests **rund 70 Namen, die in keinem Vertrag vorkommen**, etwa `handle_kamikaze`, `handle_teleport`, `load_sheet_meta`, `make_ramp`, `PixelCanvas`, `generate_universe`, `pick_event`. Kamikaze, Teleport und Aura gibt es in der Bibel auch nicht.
   - Ein günstiges Modell bekommt also „lies V4“ und einen Test, der etwas anderes prüft. Genau das sollte der Plan verhindern.

3. **Spec-Tests und Bestandstests schließen sich aus.** `tests/test_universes.py` prüft `len(UNIVERSES) == 6`, A01 verlangt 9. Beide gelten als schreibgeschützt, und jede Karte verlangt, dass beide grün sind. Diese Karte kann niemand erfüllen.

4. **Einzelne Karten lassen sich nicht abnehmen.**
   - 17 Karten haben keinen Test, den `-k <id>` findet: B22, B23, B26, B29, B30, B33, B34, E08, E11–E14, F04, F05, F12, F13, G05. pytest meldet dann „no tests collected“.
   - Etwa 30 Tests decken mehrere Karten ab, ohne parametrisiert zu sein, zum Beispiel `test_e10_to_e15_…` oder `test_f03_to_f06_…`. Sie bleiben rot, bis die letzte Karte der Gruppe fertig ist, also lässt sich keine einzelne Karte abnehmen.

## Wichtig

1. **Die S-Regel wird oft gebrochen.** 27 Karten haben mehr als 2 Zieldateien: D01–D09 je 4, F06 sogar 5, dazu A25, E11–E14 und weitere. Bei Grafik-Karten wie „3 Kreaturen-Sheets pro Karte in 60–80 Zeilen“ ist S kaum realistisch.

2. **`vertraege.md` und `README.md` widersprechen ihren eigenen Teilverträgen und dem Code:**
   - **Haltungen:** „4 Haltungen `peaceful`, `shy`, `territorial`, `hostile`“ – v01 nutzt die Bibel-Haltungen (`hostile`, `neutral`, `passive`, `trader`).
   - **Fähigkeiten:** „10 Fähigkeiten“ – v01 hat 16.
   - **Lauf:** „UniversePlan, 5-Universen-Abfolge“ – im Code heißt die Klasse `RunPlan`, und es sind 6 Universen.
   - **Technik:** „Python ≥ 3.12“ – `pyproject.toml` sagt ≥ 3.11. „Rust/PyO3-Kern mit Python-Fallback in `world.py`“ – es ist ctypes, und einen Fallback gibt es nicht.
   - **Tests:** `vertraege.md` sagt „1–2 Zieldateien + 1 Testdatei“ und lässt ruff auch über `tests` laufen, das README verbietet, Tests anzufassen.

3. **Weitere Abweichungen von der Bibel in Gerüsten und Verträgen:**
   - **Waffenteile:** `griff_holz`, `kern_rubin` … statt Gehäuse, Lauf, Mündung, Tank, Griff, Zierteil.
   - **Rätsel:** `lava_water`, `acid_gold` … statt „Füll das Glas“, „Rette die Vase“, „Zünde die Kerze“, „Ameisenstraße“.
   - **Klonita-Anlässe:** `wanted_high` und `event_start` statt der 5 aus der Bibel.

## Kleinere Punkte

- Meine alten Dateien `phase-c-universen.md`, `phase-d-werkstatt.md`, `phase-e-bosse.md` und `phase-f-umbenennung.md` liegen noch da. Das README verweist nicht darauf, und ihre IDs `B0`–`B6` kollidieren mit den neuen Grafik-Karten `B01`–`B36`.
- V0a verweist noch auf die alten IDs (`T5.00a`, `U4.08`, `W3.02` …).
- `docs/intent/` sagt „keine Änderungen an `src/` und `tests/` während der Planung“, der Commit hat aber Gerüste und Tests angelegt. Das sollte dort nachgezogen werden.
- V0d führt neue Mechaniken ein (Türsteher-Bestechung, Chor-Buff, Honigtau). Die sollten auch in die Bibel, damit sie die einzige Quelle bleibt.

## Empfehlung

Die Ursache ist fast sicher, dass Tests, Gerüste und spätere Karten ohne Blick auf die Bibel und auf v00–v09 erzeugt wurden. Reihenfolge zum Reparieren:

1. **Kanon festhalten:** die Bibel mit ihren 6 Universen.
2. **Verträge vervollständigen:** v11, v15, v18 und v21 auf die Bibel umschreiben und jeden Namen eintragen, den ein Test nutzen soll.
3. **Erst dann neu erzeugen:** Spec-Tests und Gerüste aus den Verträgen ableiten, nicht umgekehrt. Ein Test pro Karte oder parametrisiert, und Bestandstests bewusst als „wird ersetzt“ markieren, wo sich das Verhalten ändert.
4. **Karten nachschneiden:** die mit mehr als 2 Dateien teilen und die alten Plan-Dateien löschen.

Das ist Arbeit für ein starkes Modell, damit danach die günstigen sauber arbeiten können. Ich kann das übernehmen. Sinnvoll wäre, mit Schritt 2 und den Phase-A-Tests anzufangen, weil alles andere darauf aufbaut.
