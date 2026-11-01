# Bestätigtes Zielbild: Atomarer Umsetzungsplan & Schnittstellen-Verträge

Stand: 2026-11-01 · Status: Bestätigt (`interview-me`)

## Kern-Aussagen

- **Ergebnis:** Modulare, lückenlose Schnittstellen-Verträge unter `docs/plan/vertraege/` (mit Master-Index und Spezifikation in `docs/plan/vertraege.md`) sowie in reine **S-Karten** zerlegte Phasenpläne (`docs/plan/phase-a-fundament.md` bis `docs/plan/phase-g-abnahme.md`), die 100 % der MVP-Bibel (`docs/bibel/`) abdecken und Abweichungen zum bestehenden T1–T4-Code über Vorab-Korrekturkarten auflösen.
- **Nutzer:** Projektleiter/Abnehmer und kostengünstige, schnelle Sprachmodelle im isolierten Einzelkarten-Betrieb.
- **Warum jetzt:** Die neuen Dokumente in `docs/plan/` enthalten noch Vertragslücken (Event-Payloads, Save/Load, Phase-D/E/F-Schnittstellen), Schlüssel-/Typkonflikte zu `src/` (`Pickup`, `catalog.py`, `Block.rarity`, `Records.discover`) und zu komplexe M-/Sammelkarten.
- **Erfolgskriterium:** Jede Karte hat S-Zuschnitt (≤ 60–80 geänderte Zeilen, max. 1–2 Zieldateien + Test, `< 15 KB` Lesekontext), alle Signaturen, Übergabeparameter und JSON-Formate sind eindeutig typisiert, und bisher offene Detailpunkte (Blattlaus-Futter, Krypta-Strömung, Händler-Sonderregeln, 15 Trink-Schübe) sind vorab verbindlich festgelegt.
- **Rahmenbedingung:** `docs/plan/` bleibt die einzige kanonische Quelle (keine Duplikate unter `tasks/`); die Bibel schlägt Plan-Abkürzungen; Rust-Kern (`native`), `pyproject.toml` und `CHANGELOG.md` bleiben unangetastet.
- **Nicht im Umfang (Out of scope):** Keine Änderungen an `src/` oder `tests/` während der Spezifikations- und Planungsphase, keine Post-MVP-Inhalte (Musik, 18 Pool-Universen, `rule_reverse_gravity`), keine Git-Commits.
