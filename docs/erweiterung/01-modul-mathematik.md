# 01 – Modul-Mathematik & Deck-Evaluation

Dieses Kapitel beschreibt die Noita-inspirierte Zaubermathematik für die Erweiterung (Phasen H–M). Sie baut direkt auf der existierenden Klassenstruktur in `src/wand.py` (`_Draw` und `Wand`) und `src/spells.py` auf.

---

## 1. Die Deck-Zieh-Architektur in `src/wand.py`

In `src/wand.py` zieht die interne Klasse `_Draw` Module aus dem Deck:

```python
# Bestehende Basis in src/wand.py:
# _Draw.next() durchläuft self.order[self.index].
# Erreicht index das Ende, setzt der Code self.wrapped = True und self.index = 0.
```

In Phase H wird diese Mechanik für erweiterte Kombinatorik verfeinert:

- **Modul-Rückgriff (Deck-Wrapping):** Wenn nach Aufsätzen (`MODIFIER`) oder Zündern (`TRIGGER`) noch ein Zieh-Befehl offen ist, greift `_Draw.next()` genau einmal an den Anfang des Decks zurück (`wrapped == True`). Das verdoppelt die Feuerrate und ermöglicht zyklische Maschinengewehre.
- **Rekursions-Bremse:** `_Draw` erhält ein Feld `recursion_depth: int = 0`. Übersteigt verschachteltes Aufrufen den Wert `8`, bricht der Ziehvorgang sofort ab und erzeugt ein winziges Wölkchen `smoke`.

---

## 2. Die Kopier-Protokolle (Seltenheit 4)

Kopier-Protokolle sind seltene wissenschaftliche Algorithmen, die Module im Deck kopieren. Sie erfordern hohe Flux-Kosten, um die Balance zu wahren.

| Schlüssel | Name | Flux-Kosten | Beschreibung | Technische Wirkung |
| --- | --- | --- | --- | --- |
| `proto_alpha` | Protokoll Alpha | 35 | Kopiert das erste Modul im Waffenrahmen. | Führt Modul auf Slot 0 aus; verbraucht keine Ladung des Zielmoduls. |
| `proto_gamma` | Protokoll Gamma | 35 | Kopiert das letzte Modul im Waffenrahmen. | Ideal, um mächtige Einmal-Bomben am Ende des Decks erneut zu zünden. |
| `proto_tau` | Protokoll Tau | 45 | Kopiert die beiden nachfolgenden Module. | Erzeugt ein synchrones Doppel-Geschoss. |
| `proto_omega` | Protokoll Omega | 85 | Feuert alle Module der Waffe auf einmal ab. | Zündet das gesamte Deck in einem massiven Schuss-Paket. |
| `proto_zeta` | Protokoll Zeta | 50 | Kopiert ein zufälliges Geschoss einer anderen getragenen Waffe. | Ermöglicht waffenübergreifende Synergien. |
| `proto_mu` | Protokoll Mu | 60 | Wendet alle Aufsätze der Waffe auf das nächste Geschoss an. | Sammelt alle Modifikatoren im Deck ein und stapelt sie auf einen Schlag. |

---

## 3. Klon-Splitter (Divide By 2, 3, 4, 10)

Klon-Splitter zerlegen das nachfolgende Modul in mehrere kleinere Geschosse:

| Schlüssel | Name | Multiplikator | Schadens-Kompensation | Max. Rekursion |
| --- | --- | --- | --- | --- |
| `split_duo` | Klon-Splitter: Duo | 2× | -15 % Direktschaden | 8 |
| `split_trio` | Klon-Splitter: Trio | 3× | -30 % Direktschaden | 6 |
| `split_quadro` | Klon-Splitter: Quadro | 4× | -45 % Direktschaden | 4 |
| `split_dekade` | Klon-Splitter: Dekade | 10× | -75 % Direktschaden | 2 |

> [!IMPORTANT] Schutz vor Abstürzen
> Werden mehrere `split_*`-Module hintereinander geschaltet, multiplizieren sich die Aufrufe. Die Engine kappt bei `recursion_depth == 8` hart ab. Es werden maximal 24 Geschosse pro Einzelschuss in die Partikel-Physik übergeben, um stabile 60 FPS zu garantieren.

---

## 4. Satelliten- und Orbit-Aufsätze

| Schlüssel | Name | Kategorie | Effekt |
| --- | --- | --- | --- |
| `mod_satellit` | Satelliten-Koppelung | `MODIFIER` | Das Hauptgeschoss wird von zwei Mini-Funken umkreist (25 % Schaden, Radius 16 px). |
| `mod_larpa_chaos` | Entropie-Larpa | `MODIFIER` | Spuckt im Flug jede Sekunde 2 Miniaturkopien seiner selbst in zufällige Richtungen ab. |
| `mod_larpa_treffer` | Aufprall-Eruption | `MODIFIER` | Beim Einschlag an Wänden schießen 3 Mini-Kopien nach oben ab. |
| `mod_bumerang_magnet` | Heimkehr-Feld | `MODIFIER` | Geschosse kurven zurück zu Cloita und bilden für 3 s einen kreisenden Schild. |
| `mod_materie_wandler` | Phasen-Konverter | `MODIFIER` | Geschoss löscht beim Flug weiche Feststoffe in 2 px Radius (zerfrisst Erde/Papier). |

---

## 5. Experimentelle Zünder

| Schlüssel | Name | Zündbedingung |
| --- | --- | --- |
| `trig_ablaufdatum` | Zünder: Verfall | Explodiert nach exakt 45 Ticks in der Luft und setzt Nutzlast frei. |
| `trig_feindkontakt_kette` | Zünder: Ansteckung | Zündet beim Feindkontakt und pflanzt ein Miniatur-Modul ein, das nach 1 s erneut zündet. |
| `trig_stoffwechsel` | Zünder: Flüssigkeitskontakt | Zündet im selben Moment, in dem das Geschoss in Flüssigkeit eintaucht. |
| `trig_abprall` | Zünder: Flummifeder | Zündet bei jedem Abprallen an einer Wand (bis zu 2 Zündungen pro Geschoss). |
