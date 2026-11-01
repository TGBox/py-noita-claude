# Bestätigtes Zielbild: Atomarer Umsetzungsplan & Schnittstellen-Verträge

Stand: 2026-11-01 · Status: Bestätigt (`interview-me`)

## Kern-Aussagen

- **Ergebnis:** Modulare, lückenlose Schnittstellen-Verträge unter `docs/plan/vertraege/` (mit Master-Index und Spezifikation in `docs/plan/vertraege.md`) sowie in reine **S-Karten** zerlegte Phasenpläne (`docs/plan/phase-a-fundament.md` bis `docs/plan/phase-g-abnahme.md`), die 100 % der MVP-Bibel (`docs/bibel/`) abdecken und Abweichungen zum bestehenden T1–T4-Code über Vorab-Korrekturkarten auflösen.
- **Nutzer:** Projektleiter/Abnehmer und kostengünstige, schnelle Sprachmodelle im isolierten Einzelkarten-Betrieb.
- **Warum jetzt:** Die neuen Dokumente in `docs/plan/` enthalten noch Vertragslücken (Event-Payloads, Save/Load, Phase-D/E/F-Schnittstellen), Schlüssel-/Typkonflikte zu `src/` (`Pickup`, `catalog.py`, `Block.rarity`, `Records.discover`) und zu komplexe M-/Sammelkarten.
- **Erfolgskriterium:** Jede Karte hat S-Zuschnitt (≤ 60–80 geänderte Zeilen, max. 1–2 Zieldateien, `< 15 KB` Lesekontext, mindestens eine eigene `test_<id_lower>_*`-Testfunktion in `tests/spec/`), alle Signaturen, Übergabeparameter und JSON-Formate sind eindeutig typisiert, und bisher offene Detailpunkte (Blattlaus-Futter, Krypta-Strömung, Händler-Sonderregeln, 15 Trink-Schübe) sind vorab verbindlich festgelegt.
- **Rahmenbedingung:** `docs/plan/` bleibt die einzige kanonische Quelle (keine Duplikate unter `tasks/`); die 6 MVP-Universen der Bibel (`fleischwelt`, `aktenhalde`, `glibbria`, `kruemelreich`, `sporenklub`, `abtei`) sind aktiver Kanon (`len(UNIVERSES) == 6`); Rust-Kern (`native`), `pyproject.toml` und `CHANGELOG.md` bleiben unangetastet.
- **Nicht im Umfang (Out of scope):** Für das ausführende Modell sind `tests/` und `docs/` während der Karten-Abarbeitung schreibgeschützt (die Vorab-Spezifikationstests unter `tests/spec/` und die Modul-Gerüste in `src/`/`tools/` wurden vorab als Verifikations-Harness angelegt); keine Post-MVP-Inhalte (Musik, `rule_reverse_gravity`), keine Git-Commits.
