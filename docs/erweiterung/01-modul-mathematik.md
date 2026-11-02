# 01 – Modul-Mathematik & Deck-Evaluation

Dieses Kapitel beschreibt die tiefe Zaubermathematik für die Erweiterung (Phasen H–M). Es baut auf der Modulmechanik aus `docs/bibel/06-waffen-und-module.md` auf und adaptiert Noitas berühmtes Deck-Zieh- und Rekursionssystem für Cloitas verrückte Wissenschafts-Welt.

---

## 1. Das Cast-Zustandsmodell (Wand Evaluation Engine)

Jeder Abzug einer Waffe initialisiert einen `CastContext`:

```python
@dataclass
class CastContext:
    deck: list[ModuleInstance]       # Aktuell noch ziehbare Module
    hand: list[ModuleInstance]       # In diesem Einzelschuss versammelte Module
    discard: list[ModuleInstance]    # Bereits gefeuerte oder abgelegte Module
    wrap_occurred: bool = False      # Ob in diesem Schuss bereits gewrappt wurde
    draw_count: int = 1              # Verbleibende Zieh-Befehle
    recursion_depth: int = 0         # Schutz gegen Endlosschleifen (max. 8)
    flux_cost_multiplier: float = 1.0
```

### Die Zieh-Phase (The Draw Cycle)

1. Ein Abzug verbraucht `shots_per_trigger` und setzt `draw_count`.
2. Module werden nacheinander von links nach rechts aus `deck` gezogen und in `hand` verschoben.
3. **Aufsätze (`MODIFIER`)** modifizieren den `CastState` (Schaden, Streuung, Geschwindigkeit, Materialspuren) und ziehen automatisch das nächste Modul (`draw_count += 0`, bleibt bei aktuellem Ziehvorgang).
4. **Zünder (`TRIGGER`)** packen alle nachfolgend gezogenen Module in ihre interne Nutzlast-Warteschlange.
5. **Geschosse (`FORM`)** reduzieren `draw_count -= 1`.

---

## 2. Modul-Rückgriff (Deck-Wrapping)

Wenn `draw_count > 0` ist, aber das `deck` leer ist:

- **Prüfung:** Wurde in diesem Schuss bereits gewrappt (`wrap_occurred == True`)?
  - Wenn **Ja**: Der Ziehvorgang bricht sauber ab.
  - Wenn **Nein**:
    - Alle bisher in `discard` befindlichen Module werden zurück in `deck` verschoben.
    - `wrap_occurred = True`.
    - Das Ziehen wird fortgesetzt, beginnend bei Index 0!

> [!NOTE] Die wissenschaftliche Konsequenz (Wrapping-Maschinengewehr)
> Ein Aufsatz (z.B. `mod_beschleuniger`) oder Zünder am Ende einer Waffe zieht ungenutzte Geschosse vom Anfang des Decks erneut. Dadurch verdoppelt sich die Feuerrate, und Nachladezeiten können drastisch gedrückt werden.

---

## 3. Die Kopier-Protokolle (Noita-Greek-Letters Äquivalente)

Kopier-Protokolle sind extrem seltene Module (Seltenheit 4), die im geheimen Forschungs-Bunker oder von Behörden-Prüfern droppen. Sie greifen direkt in den Modulspeicher zu und feuern Kopien – **auch wenn das Zielmodul 0 Ladungen hat**!

| Schlüssel | Name | Flux-Kosten | Beschreibung | Wissenschaftlicher Klon-Effekt |
| --- | --- | --- | --- | --- |
| `proto_alpha` | Protokoll Alpha | 30 | Kopiert das allererste Modul im Waffenrahmen. | Liest Slot 0 der Waffe aus. Ignoriert Ladungszähler. |
| `proto_gamma` | Protokoll Gamma | 30 | Kopiert das letzte Modul im Waffenrahmen. | Ideal, um mächtige Einmal-Bomben am Ende endlos zu zünden. |
| `proto_tau` | Protokoll Tau | 45 | Kopiert die nächsten 2 nachfolgenden Module. | Erzeugt ein Doppelgänger-Paar im aktuellen Schuss. |
| `proto_omega` | Protokoll Omega | 80 | Kopiert sämtliche Module der Waffe auf einmal. | Zündet die gesamte Waffe als ein gigantisches Schuss-Paket. |
| `proto_zeta` | Protokoll Zeta | 50 | Kopiert ein zufälliges Geschoss aus einer anderen getragenen Waffe. | Verlinkt die Waffen im Holster; erzeugt unberechenbare Kombos. |
| `proto_mu` | Protokoll Mu | 60 | Wendet alle Aufsätze der Waffe auf das nächste Geschoss an. | Sammelt jeden Modifikator im Deck ein und stapelt sie auf einen Schlag. |

---

## 4. Klon-Splitter (Divide By 2, 3, 4, 10)

Klon-Splitter teilen ein nachfolgendes Modul in mehrere Iterationen auf.

| Schlüssel | Name | Multiplikator | Schadens-Kompensation | Max. Rekursion |
| --- | --- | --- | --- | --- |
| `split_duo` | Klon-Splitter: Duo | 2× | -15 % Direktschaden | 8 |
| `split_trio` | Klon-Splitter: Trio | 3× | -30 % Direktschaden | 6 |
| `split_quadro` | Klon-Splitter: Quadro | 4× | -45 % Direktschaden | 4 |
| `split_dekade` | Klon-Splitter: Dekade | 10× | -75 % Direktschaden | 2 |

### Rekursions-Sicherheitsregel (Stack Overflow Prevention)

Wird ein `split_*` auf einen anderen `split_*` angewendet, multiplizieren sich die Kopien exponentiell ($2 \times 3 \times 4 = 24$ Iterationen).

- Sobald `recursion_depth >= 8`, bricht der Interpreter ab und spuckt ein winziges Wölkchen `qualm` mit einem leisen Piepton aus.
- Dadurch sind absurde Noita-Kaskaden möglich, ohne dass die Framerate einbricht.

---

## 5. Satelliten- und Chaos-Aufsätze (Larpa / Orbit / Boomerang)

| Schlüssel | Name | Kategorie | Effekt |
| --- | --- | --- | --- |
| `mod_satellit` | Satelliten-Koppelung | `MODIFIER` | Das Hauptgeschoss wird von zwei Miniatur-Kopien umkreist (25 % Schaden, rotieren im 15-px-Radius). |
| `mod_larpa_chaos` | Entropie-Larpa | `MODIFIER` | Das Geschoss spuckt im Flug jede Sekunde 3 zufällige Kopien seiner selbst in alle Himmelsrichtungen. |
| `mod_larpa_treffer` | Aufprall-Eruption | `MODIFIER` | Beim Einschlag an Wänden oder Gegnern schießen 4 Kopien im 45°-Winkel nach oben ab. |
| `mod_bumerang_magnet` | Heimweh-Feld | `MODIFIER` | Geschosse fliegen in weitem Bogen zurück zu Cloita und bilden eine kreisende Abwehrzone. |
| `mod_materie_wandler` | Phasen-Konverter | `MODIFIER` | Geschoss löscht beim Flug weiche Feststoffe in 3 px Radius (zerfrisst Wände). |
| `mod_ketten_blitz` | Funken-Leiter | `MODIFIER` | Geschoss erzeugt Lichtbögen zu allen nassen oder metallischen Objekten im Umkreis von 40 px. |

---

## 6. Neue experimentelle Zünder

| Schlüssel | Name | Zündbedingung |
| --- | --- | --- |
| `trig_ablaufdatum` | Zünder: Verfallsdatum | Explodiert nach exakt 45 Ticks in der Luft und setzt Nutzlast frei. |
| `trig_feindkontakt_kette` | Zünder: Ansteckung | Zündet beim Feindkontakt und pflanzt ein Miniatur-Modul ein, das nach 1 s beim Feind erneut zündet. |
| `trig_stoffwechsel` | Zünder: Material-Hunger | Zündet genau in dem Moment, in dem das Geschoss Flüssigkeit (Wasser, Säure, Tinte) berührt. |
| `trig_abprall` | Zünder: Flummifeder | Zündet bei jedem Abprallen an einer Wand, verbraucht aber nicht das Hauptgeschoss (bis zu 3 Zündungen!). |
