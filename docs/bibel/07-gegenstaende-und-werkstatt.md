# 07 – Gegenstände und Werkstatt

## Gegenstände in der Welt

| Schlüssel | Name | Größe | Aussehen | Wirkung |
| --- | --- | --- | --- | --- |
| `gold_muenze` | Gold | 3×3 | runde Münze, Glanzpixel | wird beim Berühren eingesammelt |
| `gold_haufen_s/m/l` | Goldhaufen | 5×3 / 7×4 / 9×5 | Münzstapel | 10–40 × Rang |
| `kolben` | Kolben | 7×9 | Rundkolben aus Glas mit Korken, Füllstand in Materialfarbe | wie bisher die Phiole |
| `waffe` | Waffe | 12–20×5–8 | aus Teilen (Kapitel 06) | aufheben |
| `modul` | Modul | 7×7 | kleine Kassette in Kategorienfarbe mit dem Icon-Motiv (vereinfacht); unbekannte glitzern golden | aufheben |
| `lebenskapsel` | Lebenskapsel | 8×10 | Kapsel mit grüner, pulsierender Flüssigkeit (`life`), leuchtet | +20 max. Leben, volle Heilung |
| `fundkiste` | Fundkiste | 10×9 | Holzkiste mit „Absender: unbekannt“, wackelt | öffnen: Gold + 1–3 Gegenstände |
| `erinnerungssplitter` | Erinnerungssplitter | 8×8 | schwebender Spiegelsplitter, zeigt flackernd Cloitas Gesicht | Geheimnis je Universum; alle 6 + Sieg = wahres Ende |
| `wackelportal` | Wackelportal | 20×24 | instabiles, zitterndes Portal mit Schrift „AUSSER BETRIEB“ | in die nächste Parallelwelt |
| `anker` | Ankerpunkt | 16×16 | Metallsockel mit Flux-Spule, summt | hier öffnet die Waffe das Portal zur Werkstatt |
| `bauplan_splitter` | Bauplan-Splitter | 7×7 | eingerissenes Blaupausen-Stück | für Fabrikator-Bauten Seltenheit 3+ |
| `dienstausweis` | Dienstausweis | 6×5 | Behördenausweis mit Siegel | Archiv-Fundstück fürs Metaziel |

## Proben (für den Fabrikator)

Zwei je Universum. Fallen von Einheimischen, großen Kreaturen und Zwischengegnern oder liegen in Fundkisten. Alle 7×7 als Gegenstand und 12×12 als Icon im Rucksack (eigene Leiste „Proben“).

| Schlüssel | Name | Universum | Aussehen |
| --- | --- | --- | --- |
| `probe_gallenstein` | Gallenstein | Fleischwelt | grüngelber, kantiger Stein |
| `probe_wucherung` | Wucherungsableger | Fleischwelt | lila Knolle mit Äderchen im Glas |
| `probe_stempelkissen` | Stempelkissen | Aktenhalde | lila Kissen in Blechdose |
| `probe_formular` | Formular B-38 | Aktenhalde | drei zusammengeheftete Blätter |
| `probe_glibberkern` | Glibberkern | Glibbria | leuchtend grüne Kugel |
| `probe_brauseperle` | Brauseperle | Glibbria | rosa Perle mit Bläschen |
| `probe_zuckerkristall` | Riesenzuckerkristall | Krümelreich | weißer Würfel, größer als Cloitas Hand |
| `probe_ameisenduft` | Ameisenduft-Ampulle | Krümelreich | Ampulle mit rotem Nebel |
| `probe_leuchtspore` | Leuchtspore im Glas | Sporenklub | Glas mit türkisem Licht |
| `probe_plattennadel` | Plattennadel | Sporenklub | goldene Nadel |
| `probe_glockensplitter` | Glockensplitter | Versunkene Abtei | Bronzescherbe |
| `probe_kerzenstumpf` | Kerzenstumpf mit Gesicht | Versunkene Abtei | Wachsstumpf mit eingedrücktem Gesicht |

Rucksack: eigene Leiste mit 12 Plätzen für Proben (stapelbar bis 99), getrennt von den Modulen.

## Selbstexperimente (bisher Perks)

An der **Experimentierliege** der Werkstatt wählt Cloita eines von drei Experimenten, das sie an sich selbst durchführt (gilt für den Rest des Laufs). Die alten Perks werden umbenannt; einige ändern Cloitas Aussehen (Kapitel 04).

| Schlüssel | Name | Bisher | Wirkung | Sichtbar |
| --- | --- | --- | --- | --- |
| `asbesthaut` | Asbesthaut | feuerfest | Feuer schadet nicht | grauer Hautton |
| `saeurefest` | Säureresistente Leber | saeurehaut | Säure und Dämpfe schaden nicht | – |
| `zweites_herz` | Zweites Herz | zaehes_fleisch | +50 maximales Leben | – |
| `jetpacksohlen` | Verbesserte Jetpack-Sohlen | leichte_knochen | 50 % länger schweben | größere Funken |
| `airbag` | Eingebauter Airbag | panzerplatten | Explosionen verletzen kaum | – |
| `vampirismus_light` | Vampirismus light | blutdurst | Jeder Kill heilt 6 | – |
| `uebertaktet` | Übertaktet | schnelle_druesen | Waffen 25 % schneller | Augen leuchten |
| `saeurespucker` | Säurespeichel | saeureblut | Bei Treffern spritzt Säure um dich | `froschzunge` |
| `backup_bewusstsein` | Backup-Bewusstsein | zweiter_puls | einmal pro Lauf Wiederbelebung | – |
| `dritter_arm` | Dritter Arm | flinke_haende | Waffen überall umbauen | `dritter_arm` |
| `wutchip` | Wut-Chip | wutdruesen | +30 % Schaden | – |
| `goldmagnet` | Goldmagnet-Implantat | perlenmagnet | Gold fliegt dir zu | – |
| `dauerflug` | Dauerflug | dauerflug | Schweben lädt in der Luft | – |
| `filterlunge` | Filterlunge | gaslunge | Gase schaden nicht | – |
| `rutschfest` | Rutschfeste Socken | schleimlaeufer | Klebrig und Schleim bremsen nicht | – |
| `blutsauger` | Blutsauger | blutsauger | Blut heilt (6 je Schluck) | – |
| `feilscherin` | Gespaltene Zunge | feilscher | Händler 1/3 billiger | – |
| `kiemen` | Kiemen | neu | keine Atemnot unter Wasser | `kiemen` |
| `leuchthaar` | Leuchthaar | neu | du bist eine Lichtquelle (Radius 80) | `leuchthaar` |
| `klonbindung` | Klonbindung | neu | Klonita zeigt doppelt so oft Geheimnisse | – |

Icon je Experiment 16×16 (runde Spritze/Pille-Form mit Symbol).

## Die Werkstatt

Eine feste, handgebaute Karte (ca. 640×360, eine Bildschirmbreite, kein Scrollen). Sicherer Ort: keine Gegner, volle Heilung beim Betreten, Speicherpunkt.

**Aussehen:** Cloitas Kellerlabor in einer Lücke zwischen den Universen: Ziegelwände mit Rissen, durch die Sterne schimmern, Kabelsalat, eine Couch mit Klonitas Kuscheltieren, Tafel voller Formeln (und einer Einkaufsliste), ein Kühlschrank mit Proben.

**Stationen** (je ein Sprite mit `idle` 2–4 Frames und `use` 2–4 Frames):

| Schlüssel | Name | Größe | Funktion | Aussehen |
| --- | --- | --- | --- | --- |
| `ws_portal` | Portalrahmen | 40×48 | Weiter ins nächste Universum (zeigt dessen Namen und Regel als Vorschau) | Torbogen aus Schrott und Spulen, Flux-Wirbel |
| `ws_werkbank` | Werkbank | 48×28 | Waffen umbauen (öffnet den Rucksack im Umbau-Modus) | Tisch mit Schraubstock, Lötkolben |
| `ws_fabrikator` | Fabrikator | 40×40 | Module aus Bauplänen bauen | Kasten mit Trichter oben, Ausgabeschacht unten, raucht |
| `ws_liege` | Experimentierliege | 48×24 | Selbstexperimente wählen (3 zur Wahl, neu würfeln gegen Gold) | OP-Liege mit Spritzen-Roboterarm |
| `ws_haendler` | Händlerplatz | 2× 32×32 | Händler aus besuchten Universen (Kapitel 04) | Teppich und Klapptisch |
| `ws_zapfhahn` | Schnapszapfanlage | 16×24 | Flux-Schnaps in den Kolben (10 Gold) | Zapfhahn an der Wand, Fass |
| `ws_automat` | Physik-o-Mat | 24×36 | Minispiel Rätsel | Spielautomat mit Glasscheibe |
| `ws_schiessstand` | Schießstand | 64×24 | Minispiel Zielschießen | Bahn mit Pappfiguren der Behörde |
| `ws_archiv` | Archivschrank | 24×32 | Archiv (Kodex) ansehen | Aktenschrank, eine Schublade klemmt |
| `ws_couch` | Klonitas Couch | 40×18 | Klonita sitzt hier, wenn man in der Werkstatt ist; ansprechen = Spruch | Couch mit Kuscheltieren |

## Minispiele

Beide nutzen die vorhandene Physik. Einsatz Gold, Belohnung Gold, Proben oder Schübe. Höchstens **ein Versuch je Minispiel und Werkstatt-Besuch**.

**Physik-o-Mat (`minigame_automat`)** – Einsatz 30 Gold

- Ein kleines Feld (160×120) in einem Rahmen; Cloita hat eine feste Waffe und 10 Sekunden.
- Rätsel (zufällig eines von):
  1. *Füll das Glas:* Wasser in einem Becken oben soll in ein Glas unten fließen; nur durch Sprengen und Graben.
  2. *Rette die Vase:* einen Turm sprengen, ohne dass die Vase zerbricht.
  3. *Zünde die Kerze:* über Öl, Papier und Wasser eine Kerze entzünden.
  4. *Ameisenstraße:* Zucker so verteilen, dass die Ameisen ins Ziel laufen.
- Belohnung: 80 Gold oder eine Probe nach Wahl.

**Schießstand (`minigame_schiessstand`)** – Einsatz 20 Gold

- 30 Sekunden mit der eigenen Waffe auf auftauchende Pappfiguren (Agenten: treffen; Klonita-Pappfiguren: nicht treffen, sonst Abzug).
- Belohnung je Punkte: Schub für das nächste Universum (Flux +20 %, Schaden +10 % oder Lauftempo +10 %).

**Herausforderungen in Universen (`challenge_*`)** – ein Einheimischer je Universum bittet um etwas (Textblase, Annehmen mit E):

| Universum | Herausforderung | Belohnung |
| --- | --- | --- |
| Fleischwelt | „Bring mir 3 Gallensteine, ich sammle sie.“ | Lebenskapsel |
| Aktenhalde | „Stempel 5 Formulare ab, bevor die Prüfung kommt.“ (Formulare liegen herum, mit E stempeln) | 150 Gold |
| Glibbria | „Bring meine Kuh heil über den Sirupsee.“ (Glibberkuh muss geführt werden) | Modul Seltenheit 3 |
| Krümelreich | „Füttere die Blattläuse, ohne dass die Ameisen dich sehen.“ | Proben ×2 |
| Sporenklub | „Tanz mit mir!“ (5 Sprünge genau auf dem Beat) | Neonsaft-Kolben + 80 Gold |
| Versunkene Abtei | „Läute die Glocke dreimal, ohne den Kraken zu wecken.“ | Selbstexperiment-Neuwurf gratis |

## Rucksack-Änderungen

- Leisten: Waffen (4), Module (48, stapelbar wie jetzt), Kolben (4), **Proben (12, neu)**.
- Bezeichnungen umstellen (Kapitel 00).
- Modulbuch der Sandbox bleibt (heißt „Modulbuch“).
