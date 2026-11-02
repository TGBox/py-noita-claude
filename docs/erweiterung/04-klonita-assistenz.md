# 04 – Klonita als Labor-Assistentin

Dieses Kapitel beschreibt den mechanischen und narrativen Ausbau von Cloitas misslungener Klon-Kopie **Klonita** für die Erweiterung (Phasen H–M). Aus der reinen Begleiterin wird eine voll integrierte, anpassbare Labor-Assistentin.

---

## 1. Klonita-Selbstexperimente (Werkstatt-Liege)

Neben den Experimenten an Cloita selbst schaltet die Erweiterung an der Experimentierliege (`ws_liege`) einen zweiten Reiter frei: **Assistentinnen-Modifikation**. Hier kann Cloita Klonita pro Besuch um ein Upgrade ergänzen:

| Schlüssel | Name | Mechanischer Effekt | Optische Veränderung | Klonita-Reaktion |
| --- | --- | --- | --- | --- |
| `klonita_schwebe` | Antigrav-Propeller | Klonita schwebt per Propeller-Rucksack; ignoriert Bodengefahren (Lava, Säure, Stacheln). | Kleiner Messing-Propeller auf dem Kopf. | „Guck mal Cloita, ich bin ein Hubschrauber! Wusch!“ |
| `klonita_packesel` | Labor-Ranzen | Schaltet 2 zusätzliche Kolben-Plätze und 4 Proben-Plätze frei, die Klonita trägt. | Klobiger Leder-Rucksack mit klirrenden Phiolen. | „Ich passe ganz doll auf, dass nichts zerbricht! *Klirr* ... Upsi.“ |
| `klonita_feuerwehr` | Lösch-Sprühkopf | Sobald Cloita Feuer fängt oder brennt, spritzt Klonita sofort 100 Einheiten Wasser auf sie. | Feuerwehrhelm und Mini-Gartenschlauch. | „Tatütata! Die Feuerwehr ist da!“ |
| `klonita_funkenkamm` | Statischer Schockkamm | Alle 25 s elektrisiert Klonita den nächsten angreifenden Nahkämpfer für 2 s Lähmung. | Haare stehen wild zu allen Seiten ab. | „Bitz! Das kitzelt in den Zehen!“ |
| `klonita_bioleuchte` | Phosphor-Dauerwelle | Klonitas Haare fluoreszieren; erhellt dunkle Biome (Abtei, Schrott) im 80-px-Radius. | Türkis leuchtende Haarpracht. | „Ich bin eine Glühbirne! Eine hübsche Glühbirne!“ |

---

## 2. Dialog- und Reaktionskaskaden

Klonita reagiert über kontextuelle Sprechblasen dynamisch auf komplexe Systemzustände der Erweiterung:

### Beim Destillierkessel & Alchemie-Experimenten

- **Wenn Zutaten kochen:** „Es blubbert so schön! Darf ich den Schaum löffeln?“
- **Bei drohender Kesselexplosion:** „Cloita? Warum wird der Kessel so rot? Soll der zittern?!“
- **Bei geglücktem Wundertonikum:** „Ooooh, das glitzert wie Feenstaub! Schmeckt bestimmt nach Kaugummi!“
- **Bei Midas-Schmelze:** „Alles ist Gold! Sogar der Käfer da drüben! Kann ich den behalten?“

### Beim Realitäts-Flimmern (Sporen-Rausch / Fungal Shift)

- **Start des Shifts:** „Wooooah... Cloita! Die Decke tanzt Walzer!“
- **Wenn Säure zu Brause wird:** „Juhu! Wir baden in Limonade! Das Leben ist schön!“
- **Wenn Papier zu Lava wird:** „Das Büro brennt! Das ist bestimmt schlecht für den Urlaubsantrag!“
- **Wenn Wasser zu Gift wird:** „Igitt, wer hat in die Pfütze gespuckt?!“

### In den neuen Universen

- **Der Große Schrott:** „Hier liegt bestimmt mein alter Dreirad-Lenker! Ich geh mal wühlen!“
- **Die Kuchenkruste:** „Ich hab den Boden angeleckt. Er schmeckt nach Vanille und ein ganz kleines bisschen nach Asche!“
- **Die Summende Spule:** „Meine Zunge schmeckt nach 9-Volt-Batterie! Willst du mal probieren?“
- **Die Uhrwerkwüste:** „Tick... tack... tick... Cloita, warum laufen wir auf einmal so laaaangsam?“
- **Das Endlose Suppenmeer:** „Guck mal! Die Nudel da drüben hat ein 'H' und ein 'I' gelegt! Sie sagt Hallo!“
- **Freizeitpark Endzeit:** „Können wir Riesenrad fahren?! Bitte, bitte, bitte! Nur drei Runden!“

---

## 3. Begegnungen mit Parallelwelt-Klonitas

In den Wackel-Parallelwelten jenseits der Universums-Barrieren existieren feindliche oder traumatisierte Doppelgängerinnen:

1. **Die Bürokratie-Klonita (`klonita_akten`):**
   - Trägt Brille und Aktenordner; verlangt von Cloita Einreiseformulare.
   - Klonita ruft: „Oh mein Gott! Ich mit Brille! Sieht super schlau aus, aber warum schießt du mit Büroklammern auf uns?!“
2. **Die Schatten-Klonita (`klonita_schatten`):**
   - Korrumpiert durch dunkle Sporen; wirft explosive Füllungen.
   - Klonita versucht, sie zu trösten: „Nicht weinen, böses Ich! Wir haben noch Kekse in der Werkstatt!“
3. **Pazifistische Bekehrung:**
   - Besiegt man eine Parallel-Klonita nicht mit Gewalt, sondern schüttet *Wundertonikum* über sie, beruhigt sie sich und droppt seltene Proben oder ein Kopier-Protokoll (`proto_tau`).
