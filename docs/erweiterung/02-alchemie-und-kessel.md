# 02 – Alchemie, Kessel & Realitäts-Flimmern

Dieses Kapitel beschreibt das erweiterte Alchemie- und Physiksystem für die Erweiterung (Phasen H–M). Es adaptiert Noitas geheime Alchemie-Rezepte (Lively Concoction / Midas) und die unberechenbaren Realitäts-Verschiebungen (Fungal Shifts) in den Kosmos von Cloitas Labor-Chaos.

---

## 1. Seed-basierte Geheimrezepte (Alchemistische Präkursoren)

In jedem Durchlauf (`RunPlan.seed`) generiert die Engine zwei geheime Dreier-Kombinationen aus dem globalen Flüssigkeits- und Pulverpool:

```python
@dataclass
class SecretAlchemyRecipes:
    wundertonikum_zutaten: tuple[str, str, str]  # z.B. ("blut", "brausesirup", "tinte")
    midas_schmelze_zutaten: tuple[str, str, str] # z.B. ("magensaeure", "kaugummi", "asche")
```

### Die zwei Elixiere

1. **Wundertonikum (`wundertonikum`):**
   - **Farbe:** Funkelndes Türkis-Cyan (#40FFE0), sprudelt sanft nach oben.
   - **Wirkung:** Berührung heilt 4 LP pro Sekunde; Trinken heilt 25 LP und verleiht 30 Sekunden lang Lebensregeneration.
   - **Reaktion:** Wenn alle drei geheimen Zutaten im selben Pixel-Radius (3×3) aufeinandertreffen, verwandelt sich die gesamte Flüssigkeit unter einem wohlklingenden Harfenton in Wundertonikum.

2. **Midas-Schmelze (`midas_schmelze`):**
   - **Farbe:** Flammendes Reingold (#FFD700) mit goldenen Funkenpartikeln.
   - **Wirkung:** Löst bei Kontakt jedes feste Material (Fleisch, Fels, Papier, Glibber, Knochen) innerhalb von Millisekunden in reine Goldmünzen und Goldpixel auf!
   - **Gefahr:** Berührt Cloita die Schmelze ohne Schutzanzug, erleidet sie 50 Schaden und Klonita ruft: „Werd nicht zur Statue, wir haben keinen Platz im Regal!“

---

## 2. Der Verlassene Kesselraum (`cauldron_room`)

In den Tiefen von Universen ab Rang 2 (insbesondere in geheimen Seitenkammern) kann Cloita auf den **Verlassenen Kesselraum** stoßen:

- **Aussehen:** Ein uralter Kupferdestillator mit drei Trichteröffnungen und einem zapfbaren Auslasshahn über einem Feuerrost.
- **Funktion:**
  - Cloita kann bis zu 3 verschiedene Kolben in die Trichter entleeren.
  - Wird der Rost darunter mit Feuer (z.B. Funken oder brennendes Papier) erhitzt, beginnt der Kessel 5 Sekunden lang bedrohlich zu pfeifen.
  - **Erfolg:** Bei passenden Zutaten füllt der Auslasshahn automatisch einen leeren Kolben mit *Wundertonikum*, *Midas-Schmelze* oder hochreinem *Reaktions-Beschleuniger*.
  - **Fehlschlag:** Eine gewaltige Fontäne aus ätzendem Schaum oder stinkendem Qualm schießt an die Decke. Klonita hustet: „Riecht wie Omas Keller, nur giftiger.“

---

## 3. Dynamische Kolben-Synthese & Wurfbomben

Kolben (`kolben`) erhalten in der Erweiterung physikalische Innenraum-Simulation:

- **Cocktail-Mischung:** Kolben fassen bis zu 1000 Einheiten Material. Werden zwei reagierende Stoffe eingefüllt (z.B. Magensäure + Brausesirup), steigt der **Druck** im Kolben (sichtbar am pulsierenden Korken).
- **Druckbombe:** Wird ein überdruckter Kolben geworfen (`Rechtsklick`), zerspringt er beim Aufprall in einer aerosolischen Druckwelle, die das Gemisch über 60 Pixel verteilt.
- **Gas-Kondensation:** Werden heiße Gase (z.B. Weihrauch oder Sporendampf) unter Wasser in einen Kolben gezogen, kondensieren sie zu zähflüssigen Konzentraten.

---

## 4. Realitäts-Flimmern (Fungal Reality Shifts)

Das Realitäts-Flimmern ist die mächtigste und riskanteste Alchemie-Mechanik des Spiels.

### Auslöser

1. **Verzehr von Leuchtsporen:** Mehrfacher Verzehr von `probe_leuchtspore` oder Trinken von Sporenextrakt im Sporenklub.
2. **Katalysator-Überlastung:** Sprengung eines Destillierkessels oder Kurzschluss an einer Flux-Spule.
3. **Selbstexperiment:** Das Experiment `quanten_sinne` an der Liege.

### Der Shift-Prozess

1. **Die Vision (10 Sekunden):**
   - Der Bildschirm verzieht sich in einer wellenförmigen psychedelischen Verzerrung.
   - Alle Farbpaletten wechseln für kurze Zeit in Neon-Inversion.
   - Ein weltweites Dröhnen ertönt.
   - Klonita bricht in Panik oder Begeisterung aus: „Cloita! Warum riecht der Felsen nach Erdbeeren?!“
2. **Die Transmutation:**
   - Ein Quellmaterial $M_{\text{quelle}}$ wird global für alle existierenden und zukünftig generierten Chunks in ein Zielmaterial $M_{\text{ziel}}$ umgewandelt.
   - **Kolben-Fokus (50 % Wahrscheinlichkeit):** Wenn Cloita während des Shifts einen Kolben in der Hand hält, wird das Material im Kolben entweder als $M_{\text{quelle}}$ oder als $M_{\text{ziel}}$ gewählt!

### Transmutations-Tabelle (Beispiele)

| Quellmaterial | Mögliches Zielmaterial | Spielerische Auswirkung |
| --- | --- | --- |
| `magensaeure` | `brausesirup` | Säureseen werden zu harmlosen Trampolin-Gewässern! |
| `wasser` | `magensaeure` | Der Alptraum-Run: Die gesamte Abtei und alle Pfützen werden tödlich. |
| `blut` | `wundertonikum` | Jeder Treffer an Feinden heilt die Umgebung – der Heilige Gral der Alchemie! |
| `papier` | `lava` | Die Aktenhalde verbrennt im Bruchteil einer Sekunde in einem Armageddon. |
| `glibber` | `gold` | Glibbria zerfällt in Milliarden schwere Goldmünzen. |

> [!CAUTION] Shift-Limit & Cooldown
> Um irreversible Spielabstürze oder sofortige Frustration zu vermeiden:
>
> - Mindestens 180 Sekunden Abklingzeit zwischen zwei Realitäts-Flimmern.
> - Maximal 5 globale Shifts pro Durchlauf.
> - Verschiebungen werden im Archiv unter „Realitäts-Protokoll“ dokumentiert.
