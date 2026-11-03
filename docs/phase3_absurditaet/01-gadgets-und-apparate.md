# 01 – Originäre Gadgets & Notfall-Apparate

Dieses Kapitel definiert die fünf originären Signature-Gadgets der Phase 3 (Phasen N–U). Sie liegen auf dem separaten **Gadget-Slot (Standard: Taste G)** und bieten unkonventionelle Auswege aus brenzligen Situationen.

---

## 1. Die Täuschungs-Tauchkapsel (`gadget_tauchkapsel`)

- **Schlüssel:** `gadget_tauchkapsel`
- **Typ:** Aktives Gadget (2 Ladungen je Universum).
- **Funktion:**
  - Bei Aktivierung (Taste G in oder nahe Flüssigkeiten/Pulvern) taucht Cloita in eine getarnte Mini-Kapsel ab.
  - Drei falsche Knorpel- und Knochenpartikel treiben mit einem trockenen *„Plopp“* an die Oberfläche.
  - Feinde im 200-px-Umkreis brechen ihren Angriff ab und wechseln in den Suchmodus (Dialog: *„Ziel neutralisiert. Akte schließen.“*).
  - Cloita bewegt sich 10 Sekunden lang im Schleichmodus; der erste Schuss aus der Kapsel verursacht doppelten Schaden (+100 %).

---

## 2. Der Amtshelfer-Imp (`gadget_amts_imp`)

- **Schlüssel:** `gadget_amts_imp`
- **Typ:** Aktives Gadget (3 Ladungen je Universum).
- **Herbeirufung:** Cloita drückt einen Stempel auf den Boden. Unter einem grellen violetten Blitz erscheint ein hektischer, lila Papier-Dämon:
  > *„ICH BEARBEITE DAS SOFORT! NUR NOCH DREI ANTRÄGE BIS ZUM FEIERABEND!“*
- **Verhalten:**
  - Sammelt blitzschnell im 120-px-Umkreis Gold und Proben ein und wirft sie Cloita zu.
  - Drückt entfernte Hebel oder Schalter.
  - Erreicht er seine Aufgabe, ruft er glücklich: *„FEIERABEND! EINGESTEMPELT! TSCHÜSS!“* und verpufft in Konfetti.

---

## 3. Die Kolben-Libelle (`gadget_kolben_libelle`)

- **Schlüssel:** `gadget_kolben_libelle`
- **Typ:** Passiver Labor-Begleiter (im Rucksack getragen).
- **Aussehen:** Eine filigrane Messing-Libelle mit vier summenden Flügeln und einer Pipetten-Klemme.
- **Dialog:**
  - Libelle summt monoton: *„Analyse: Kolbenfüllstand kritisch. Initiere Flüssigkeitsbeschaffung.“*
  - Cloita: *„Gut so, brav tanken.“*
- **Mechanik:**
  - Schaltet einen fliegenden Kolbenplatz frei.
  - Saugt bei Klick auf eine Flüssigkeitsansammlung selbstständig Stoffe ein und füllt Cloitas gehaltenen Kolben auf.

---

## 4. Die Notfall-Schabe (`mod_schaben_flucht`)

- **Schlüssel:** `mod_schaben_flucht`
- **Typ:** Legendäres Selbstexperiment (Seltenheit 4).
- **Mechanik:**
  - Erleidet Cloita tödlichen Schaden, zerfällt ihr Körper in Funken und sie schlüpft in einer winzigen, mechanischen Schaben-Kapsel (`schaben_cloita`, Trefferbox 8×10 px) hervor!
  - Besitzt 25 LP und kriecht mit hohem Tempo durch Schächte und enge Passagen.
  - Kann mit Mini-Greifern Funken sprühen.
  - Erreicht sie die Werkstatt, baut der Klon-Bottich Cloita unversehrt wieder zusammen.

---

## 5. Die Quanten-Schwungscheibe (`gadget_schwungscheibe`)

- **Schlüssel:** `gadget_schwungscheibe`
- **Typ:** Rucksack-Relikt.
- **Mechanik:**
  - Spendet passiv **+35 Flux pro Sekunde** für alle Waffen.
  - Nach 90 Sekunden verliert die Schwungscheibe an Drehimpuls (ein mechanisches Rasseln ertönt).
  - Ein kurzes Halten der Taste G (1 Sekunde Kurbel-Animation) zieht das Uhrwerk wieder auf.
