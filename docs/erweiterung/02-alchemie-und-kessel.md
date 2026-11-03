# 02 – Alchemie, Kessel & Realitäts-Flimmern

Dieses Kapitel beschreibt das Alchemie- und Physiksystem für die Erweiterung (Phasen H–M), abgestimmt auf die harten Material- und Balancing-Grenzen der Falling-Sand-Engine.

---

## 1. Engine-Rahmen: 11 Grund- + 10 Universums-Materialien

Die 8-Bit-Farbpalette der Engine fasst maximal 21 Materialien gleichzeitig. Daraus ergeben sich zwingende Regeln:

1. **Lokale Alchemie:** Geheimrezepte basieren auf den 11 überall gültigen Grundmaterialien (`water`, `oil`, `sand`, `dirt`, `steam` etc.) kombiniert mit den bis zu 10 lokalen Materialien des gerade aktiven Universums.
2. **Keine Heilung ohne Experiment:** Gemäß Bibel Kap. 02 heilt keine Flüssigkeit die Lebensleiste, solange kein passendes Selbstexperiment aktiv ist.
3. **Gold ist kein Material:** Reines Gold existiert im Spiel nur als Gegenstand (`gold_muenze`). Feste Verwandlungen erzeugen daher das offizielle Bibel-Material **`gold_vein` (Golderz-Ader)**, das beim Abbau reguläre Münzen fallen lässt.

---

## 2. Seed-basierte Geheimrezepte

In jedem Durchlauf (`RunPlan.seed`) generiert die Engine zwei geheime Dreier-Kombinationen aus den im Universum vorkommenden Stoffen:

```python
@dataclass
class SecretAlchemyRecipes:
    schutztonikum_zutaten: tuple[str, str, str]  # z. B. ("water", "brausesirup", "oil")
    midas_schmelze_zutaten: tuple[str, str, str] # z. B. ("sand", "tinte", "aktendeckel")
```

### Die zwei Elixiere

1. **Schutztonikum (`schutztonikum`):**
   - **Farbe:** Funkelndes Cyan (#40FFE0), sprudelt sanft nach oben.
   - **Wirkung (Bibel-konform):** Trinken verleiht einen **temporären Energieschild (absorbiert 40 Schaden)** und verdoppelt die Flux-Regeneration für 25 Sekunden.
   - **Synergie mit Selbstexperiment:** Hat Cloita das Experiment `blutsauger` oder `alchemie_magen` aktiv, heilt das Tonikum zusätzlich 20 Lebenspunkte!
   - **Reaktion:** Treffen alle drei Zutaten im 3×3-Radius aufeinander, verwandelt sich die Flüssigkeit unter einem Harfenton in Schutztonikum.

2. **Midas-Schmelze (`midas_schmelze`):**
   - **Farbe:** Flammendes Reingold (#FFD700) mit Goldpartikeln.
   - **Wirkung:** Berührt feste Materie (Fels, Papier, Glibber, Knochen) und verwandelt sie in **`gold_vein` (Golderz-Adern)**!
   - **Balancing:** Spielerinnen können das erzeugte Erz sprengen oder abbauen, um Goldmünzen zu gewinnen. Es entstehen keine unkontrollierten Millionen-Gegenstände, die den Speicher überlasten.

---

## 3. Der Verlassene Kesselraum (`cauldron_room`)

In den Universen ab Rang 2 kann Cloita auf geheime Alchemie-Labore stoßen:

- **Aussehen:** Ein uralter Kupferdestillator mit drei Einfülltrichtern über einem Feuerrost.
- **Funktion:**
  - Cloita kann bis zu 3 verschiedene Kolben (Standard-Fassungsvermögen: je 300 Zellen) hineingießen.
  - Wird der Rost mit Feuer erhitzt, kocht das Gemisch 5 Sekunden lang.
  - **Erfolg:** Bei passenden Zutaten stößt der Kessel fertiges Schutztonikum, Midas-Schmelze oder seltene Proben aus.
  - **Fehlschlag:** Eine Fontäne aus harmlos stinkendem Rauch (`smoke`) schießt an die Decke. Klonita kichert: „Das hat gekitzelt in der Nase!“

---

## 4. Dynamische Kolben-Physik (300 Zellen)

Kolben (`kolben`, Fassungsvermögen 300 Zellen gem. `src/flask.py`) reagieren nun dynamisch auf Druck:

- **Druckaufbau:** Werden zwei unverträgliche Reagenzien (z. B. Magensäure + Brausesirup) im Kolben gemischt, beginnt der Korken zu zittern.
- **Wurfbomben:** Ein geschüttelter oder überdruckter Kolben zerspringt beim Aufprall in einer aerosolischen Druckwelle (Radius 50 px).
- **Trinken:** Gibt die normalen Bibel-Schübe (z. B. Wasser = Flux schneller, Öl = weniger Verzögerung).

---

## 5. Realitäts-Flimmern (Sporen-Rausch / Transmutation)

Das Realitäts-Flimmern ist die kontrollierte, physikalisch saubere Fassung der globalen Transmutation.

### Auslöser

- Verzehr von `probe_leuchtspore` im Sporenklub oder Kesselüberlastung.

### Der Prozess

1. **Vision (8 Sekunden):** Wellenförmige Bildverzerrung; Klonita ruft: *„Cloita! Warum tanzen die Farben?!“*
2. **Gültige Transmutation:**
   - Ein Quellmaterial $M_{\text{quelle}}$ wird im aktiven Universum durch ein Zielmaterial $M_{\text{ziel}}$ ersetzt.
   - **Zulässige Paare:** Nur Stoffe, die im **aktuellen Materialsatz des Universums** oder im Grundsatz existieren!
   - *Beispiele:*
     - Aktenhalde: `papier` $\to$ `aktendeckel` (alles wird feuerfest)
     - Fleischwelt: `magensaeure` $\to$ `water` (Säurebecken werden harmlos)
     - Glibbria: `glibber` $\to$ `sand` (die Welt verliert ihre Federkraft)
3. **Grenzen:** Maximal 3 Realitäts-Shifts pro Durchlauf; mindestens 180 Sekunden Abklingzeit.
