# ADR 2026-11-04: Pool-Universen nach Phase J, feste Fraktionsmatrix, Materialsatz-Karten

## Status

Angenommen (Review des MVP-Plans nach der Angleichung durch `tasks/plan.md`).

## Kontext

Nach der Angleichung waren drei Punkte offen, die eine isolierte Umsetzung durch günstige Modelle verhindert hätten:

1. Die Pool-Universen `schrott`, `kuchen` und `spule` waren doppelt geplant: im MVP (Karten B06, B10, B13, C07, C08, C13, D07–D09 und Teile weiterer Karten) und in Phase J der Erweiterung, mit abweichenden Angaben (z. B. Regel der Spule).
2. Die Fraktions-Matrix (`HATE_MATRIX`, V4) war nur als `{...}` angegeben; Karte, Vertrag und Gerüst nannten 11, 19 bzw. 13 Fraktionen.
3. Kein MVP-Karte legte die Materialsätze von Fleischwelt (endgültig), Glibbria, Krümelreich, Sporenklub und Abtei an, obwohl die Generatoren sie brauchen.

Dazu kamen Reste der früher erfundenen 9er-Welt: andere Einheimische in `catalog.py`, erfundene Teilgebiete im Test A01, Boss-„Aliase“ mit eigenen Sprites, Proben-Aliase, die in Phase J mit echten Proben kollidiert wären.

## Entscheidung

1. **Pool-Universen gehören nur in Phase J.** Einzige Quelle ist `docs/erweiterung/03-universen-erweiterung.md`; Bibel 03 verweist dorthin. Die betroffenen MVP-Karten entfallen (IDs werden nicht neu vergeben), `ALL_UNIVERSES` enthält im MVP nur die 6 Bibel-Universen.
2. **Fraktionen:** 5 Kern-Fraktionen + 6 Universums-Fraktionen (`UNIVERSE_FACTIONS`). `HATE_MATRIX` steht wörtlich in V4; Einheimische desselben Universums sind friedlich, verschiedener Universen verfeindet, Behörde und böse Ichs verbündet. Die Haltung entscheidet über Angriffe auf Cloita, nicht die Fraktion.
3. **Neue Karten D17–D21** legen die fehlenden Materialsätze nach Bibel 03 an; die Generatoren D01, D03–D06 hängen davon ab.
4. **Bibel-Namen sind verbindlich** für Einheimische, Teilgebiete, Zwischengegner und Ereignisse; erfundene Aliase ohne Bestandscode werden gestrichen (Bestands-Boss `warden` und der Agenten-Alias `agent_sachbearbeiter` bleiben).

## Konsequenzen

- Positiv: Der MVP-Plan ist kleiner (130 statt 134 Karten) und hat nur noch eine Quelle je Inhalt.
- Positiv: A11 hat keine offene Designfrage mehr; D01–D06 bauen auf existierenden Materialien.
- Nachteil: Phase J muss die drei Pool-Universen vollständig selbst schneiden (Kreaturen, Sprites, Generatoren, Fraktionen, Regel `rule_electric`).

## Nachtrag (2026-11-04): weitere Nutzerentscheidungen

- Modul-Schlüssel im Code bleiben; nur Anzeigenamen nach Bibel 06 (`G11`–`G13`). Die 8 fehlenden Füllungen und die Sonderfüllungen kommen als `A27`/`A28` dazu (`V0e`).
- Organische Alt-Füllungen: Blut, Säure und Glut bleiben; die übrigen 9 sind `retired` (`A29`).
- Klonita heilt (Snack: +15 Leben, 45 s, unter 35 %, nicht im Bosskampf). Sie kombiniert die Hilfen der Planung mit den Bibel-Aktionen Zeigen/Tragen/Umarmen und den 6 Macken (`F15`–`F17`). Es gibt keinen Fallschaden; „Auffangen“ entfällt.
- Die 6 Universums-Herausforderungen aus Bibel 07 sind MVP (`D22`–`D29`, `V13b`).
- Zwischengegner nur auf dem Bossplatz, Unter-Zwischenboss in jedem Universum.
- Die 8 sekundären Zufallsereignisse wandern nach Phase 2 (`J07`).
- Neuer Kartenstand: 147 S-Karten.
