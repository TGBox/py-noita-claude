# 08 – Oberfläche und Texte

## Logo und Titel

- **Logo:** „CLOITA“ groß in dicken Pixel-Buchstaben (`hair`-Orange mit `ink`-Kontur), darunter „INTERDIMENSIONAL“ kleiner in `flux`, leicht schief, als hätte jemand es nachträglich angeklebt. Ein Portal-Wirbel hinter dem „O“. Größe: 160×48 Pixel (wird skaliert), 4 Frames (Wirbel dreht sich).
- **Titelbild:** Cloita steht in der Werkstatt-Tür, Klonita winkt im Hintergrund; hinter ihnen ein offenes Portal. Als Szene aus vorhandenen Sprites zusammengesetzt (keine Extra-Grafik nötig). Im MVP ohne Musik, nur Werkstatt-Geräusche (Summen, Tropfen).
- **Untertitel** wechselt zufällig (10 Sprüche), z. B. „Ein Multiversum. Unendlich viele Probleme.“, „Jetzt mit 30 % weniger Moral.“, „Keine Klonkopie wurde beim Testen ernsthaft verletzt.“

## Oberfläche umbenennen

| Element | Neu |
| --- | --- |
| Lebensbalken | bleibt, Symbol Herz |
| Schweben | Symbol Jetpack-Sohle statt Flügel |
| Mana-Balken | **Flux**, Symbol türkiser Blitz im Kreis, Balken in `flux` |
| Blutperlen | **Gold**, Symbol Münze, Zahl in `gold` |
| Tiefe x/7 | **Universum x/6** + Rang-Symbol (1–3 Sterne in `n4`) |
| Fahndungsstufe | **neu:** 0–5 Siegel-Symbole neben dem Gold |
| Takt (Sporenklub) | **neu:** kleiner pulsierender Punkt neben der Fluxleiste |
| Atem (Abtei) | **neu:** Luftblasen-Leiste über Cloitas Kopf, nur unter Wasser |
| Augmentation | **Waffe** (Panel unten links) |
| Phiole | **Kolben** (Panel unten rechts) |
| Pausemenü „Dieser Lauf“ | Universum, Rang, Gold, Experimente, Erinnerungssplitter x/6, Fahndungsstufe |
| Kodex | **Archiv** (Kategorien: Module, Kreaturen, Universen, Böse Ichs, Fundstücke; alte Biohorror-Daten werden verworfen, Archiv beginnt leer) |

## Neue UI-Icons (8×8 bis 16×16)

`icon_flux`, `icon_gold`, `icon_herz`, `icon_jetpack`, `icon_siegel` (Fahndung), `icon_rang`, `icon_takt`, `icon_atem`, `icon_probe`, `icon_bauplan`, `icon_experiment`, `icon_splitter`, `icon_anker`, `icon_portal`, `icon_klonita` (für Sprechblasen), `icon_haendler`.

## Sprechblasen

- Klonita und Händler sprechen in **Sprechblasen** über ihrem Kopf (Panel-Stil aus `ui.py`, kleiner, mit Spitze). Max. 60 Zeichen, 3 s sichtbar, höchstens alle 8 s ein neuer Spruch.
- Böse Ichs und Zwischengegner sprechen größer, am oberen Bildschirmrand.

## Tonfall

- **Absurd zuerst:** Die Welt nimmt ihre eigene Absurdität ernst (Behörde, Formulare, Pilzclub).
- **Schwarzer Humor:** Tod und Zerstörung sind komisch, nie grausam ausgemalt. Opfer sind Pilze, Gelee, Akten – Realitätsbezug zu Gewalt gegen Menschen vermeiden.
- **Cloita:** trocken, genervt, genial, kurz angebunden. Duzt alle.
- **Klonita:** überschwänglich, lieb, missversteht Gefahr, verniedlicht alles („kleiner Freund“, „Hihi!“), entschuldigt sich für Cloita.
- Keine Zitate, Sprüche oder Running Gags aus bestehenden Serien, Filmen oder Spielen.

## Textmengen (MVP)

| Wer / Was | Anlässe | Sprüche je Anlass | Summe (ca.) |
| --- | --- | --- | --- |
| Klonita | Universum betreten (allgemein) | 8 | 8 |
| Klonita | Universum betreten (je Universum) | 3 | 18 |
| Klonita | Cloita nimmt Schaden | 6 | 6 |
| Klonita | Cloita tötet passive/neutrale Kreatur | 6 | 6 |
| Klonita | Klonita wird getroffen / steht auf | 6 + 6 | 12 |
| Klonita | Zeigt auf Geheimnis | 5 | 5 |
| Klonita | Ereignis kündigt sich an (je Universum) | 2 | 12 |
| Klonita | Zwischengegner erscheint / besiegt | 4 + 4 | 8 |
| Klonita | Werkstatt (Couch ansprechen) | 12 | 12 |
| Klonita | Cloita trinkt (je Flüssigkeit-Gruppe gut/schlecht) | 4 + 4 | 8 |
| Klonita | Händler beraubt | 3 | 3 |
| Klonita | Cloita stirbt | 5 | 5 |
| Klonita | gerufen / weggeschickt | 5 + 5 | 10 |
| Klonita | erscheint von selbst (wenig Leben, Splitter, Bosskampf) | 3 je | 9 |
| Rat der bösen Ichs / Ober-Cloita | Auftritt, je Stufe, Verschmelzung, Tod | 8 | 8 |
| Cloita | Antworten auf Klonita (optional, selten) | – | 15 |
| Händler | Begrüßung, Kauf, zu wenig Gold, Abschied, beraubt | 1 je × 6 Händler | 30 |
| Zwischengegner | Auftritt, Phasenwechsel ×2, Tod | 4 je × 6 | 24 |
| Böse Ichs | Auftritt, 3 Phasen, Tod, Sonderangebot (Kaiserin) | 6 je × 3 | 18 |
| Behörde | Durchsagen (Aktenhalde, Fahndung steigt) | 10 | 10 |
| Mauszeiger-Texte | jede Kreatur, jedes Material, jeder Gegenstand | 1–2 Sätze | ≈ 120 |
| Module | Name + Beschreibung (60 Basis + Familientexte) | – | ≈ 80 |
| Selbstexperimente | Name + Wirkung | – | 20 |
| Ladebildschirm-Tipps | allgemein | – | 25 |
| Tod-Bildschirm | „Du bist gestorben“-Varianten mit Ursache | – | 15 |
| Archiv | Eintrag je Universum, Kreatur, böses Ich | 2–3 Sätze | ≈ 40 |

Beispiele, die den Ton festlegen:

- Klonita, Universum betreten (Aktenhalde): „So viel Papier! Wollen wir allen einen Brief schreiben?“
- Klonita, Cloita tötet einen Hüpfling: „Er wollte doch nur hüpfen …“
- Klonita, getroffen: „Au! Das war bestimmt keine Absicht!“
- Klonita, steht auf: „Mir geht's gut! Mir geht's immer gut!“
- Cloita, selten: „Klonita, das ist ein Fleischfresser.“ – Klonita: „Und ich bin aus Fleisch! Wir haben so viel gemeinsam!“
- Türsteherpilz: „Name steht nicht auf der Liste. 20 Gold, und ich hab dich nie gesehen.“
- Tod durch eigene Kraterbombe: „Du hast dich selbst wegrationalisiert.“

## Mauszeiger-Texte

Gleiche Technik wie jetzt (`hover.py`). Jede Kreatur bekommt: Name, Haltung („neutral – greift an, wenn du sie ärgerst“), eine Zeile Verhalten, Schwäche, Beute. Jedes Material: Art, Härte, Wirkung, ein Witz-Halbsatz.

## Ladebildschirm

Beim Wechsel ins Universum (Weltgenerierung dauert länger als bisher): Universumsname groß, Pitch, Regel mit Symbol, ein zufälliger Tipp, Klonita-Sprite tanzt (Ladeanimation).
