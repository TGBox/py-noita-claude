# 02 – Systeme

## Aufbau eines Laufs

```text
Werkstatt → Universum A (Rang 1) → Werkstatt → Universum B (Rang 1, Zwischengegner Rang 1)
          → Werkstatt → Universum C (Rang 2) → Werkstatt → Universum D (Rang 2, Zwischengegner Rang 2)
          → Werkstatt → Universum E (Rang 3) → Werkstatt → Universum F (Rang 3, Zwischengegner Rang 3)
          → Werkstatt → Heimat des bösen Ichs (Endkampf)
```

- **6 Universen + Endkampf** pro Lauf, jedes Universum höchstens einmal.
- **Wahl am Portal:** Vor jedem Universum zeigt der Portalrahmen in der Werkstatt **zwei Vorschläge** (Name, Regel, Rang, ob ein Zwischengegner wartet und welcher); Cloita wählt einen. Der Seed bestimmt die Vorschläge:
  - *Freier Platz* (erstes Universum eines Rangs): zwei zufällige, noch nicht besuchte Universen. Wählt man dabei die Heimat eines Zwischengegners dieses Rangs, kämpft man dort **nicht** gegen ihn; der Rang endet dann im anderen.
  - *Bossplatz* (zweites Universum eines Rangs): die noch nicht besuchten Heimat-Universen der Zwischengegner dieses Rangs (ein oder zwei Vorschläge).
  - Mit mehr Universen im Pool gelten dieselben Regeln, die freien Plätze ziehen dann aus allen übrigen.
- **Rang** bestimmt Gegnerzahl, Gegnerstärke (Faktor 1,0 / 1,5 / 2,2), Beutequalität (Stufe 1–2 / 3–4 / 5–6) **und die Stärke der Universumsregel** (Spalte „Rang-Steigerung“ unten). Jedes Universum muss auf allen Rängen spielbar sein.
- **Zwischengegner:** am Ende des zweiten Universums jedes Rangs. Er bewacht den Ankerpunkt; erst nach seinem Tod lässt sich das Portal öffnen. Jeder Zwischengegner hat ein **Heimat-Universum** und kämpft in dessen Arena mit dessen Regel und Materialien (Kapitel 05). Welcher es wird, entscheidet die Wahl am Bossplatz (siehe oben). Im MVP kommt so jedes der 6 Universen genau einmal vor.

  | Rang | Zwischengegner (Heimat) |
  | --- | --- |
  | 1 | Oberstempler (Aktenhalde), Mutter Glibber (Glibbria) |
  | 2 | DJ Myzel (Sporenklub), Abt Kieme (Versunkene Abtei) |
  | 3 | Ameisenkönigin (Krümelreich), Weltenherz (Fleischwelt) |

  Mit mehr Universen im Pool werden die freien Plätze aus allen übrigen Universen gezogen.
- **Böses Ich:** Der Seed wählt eines der drei für den Endkampf. Es kämpft in seinem eigenen Heimat-Universum (kleine Sonderwelt je böses Ich). Zusätzlich können die beiden anderen Bösen Ichs als optionale Begegnungen (Echos/Späherinnen) in den versteckten Geheimräumen (`secret`) der Universen ab Rang 2 angetroffen werden (inkl. Verhandlungsoption bei der Kaiserin, Kapitel 05).
- **Ausgang:** In jedem Universum liegt am Ende ein **Ankerpunkt**. Dort öffnet Cloitas Waffe genau ein Portal zur Werkstatt; sonst ist sie eine normale Waffe.
- **Parallelwelten (Wackelportal):** wie bisher über eine versteckte Schatzkammer. Führt in eine gespiegelte oder dunklere, härtere Fassung desselben Laufs.
- **„Noch einmal, nur schlimmer“** (NG+) nach dem Sieg: neue Universen-Reihenfolge, Gegnerfaktor +0,6 je Runde.
- **Wahres Ende = die Behörde:** Wer in einem Lauf alle 6 Erinnerungssplitter findet (oder alternativ mindestens 3 Dienstausweise der Behörde erbeutet bzw. Fahndungsstufe 4+ erreicht) und das böse Ich besiegt, sieht, dass dessen Waffe das Siegel der Behörde trägt. Statt des normalen Siegs öffnet sich ein Portal zum **Hauptquartier der Behörde**: ein mehrstufiger Endkampf gegen den **Rat der bösen Ichs**, die am Ende zur **Ober-Cloita** verschmelzen (Kapitel 05). Das ersetzt das bisher getrennt geplante Metaziel. Ab 3 Siegen erscheinen im Archiv Hinweise, dass die Splitter wichtig sind.

## Weltgröße

- Heute: 1280×720 Zellen pro Tiefe. **Neu: etwa 4-fache Fläche**, Form je Universum:

| Form | Größe (Zellen) | Beispiel |
| --- | --- | --- |
| Breit | 3072×1024 | Bürokratenwelt (endlose Aktenregale) |
| Hoch | 1280×2560 | Kathedrale (Turm nach unten) |
| Quadrat | 2048×1536 | Fleischwelt |
| Inseln | 2560×1280 mit großen Luftanteilen | Schleimplanet |

- Simuliert wird weiter nur ein Bereich um die Kamera (vorhandene Technik). Weltgenerierung, Speichern (komprimiert) und Wegsuche müssen auf die neue Größe gemessen werden (Arbeitspaket T2).

## Regelbibliothek

Jedes Universum hat **genau eine Hauptregel** (im MVP) aus dieser Bibliothek; später sind zwei möglich. Regeln sind Datensätze mit Parametern; der Code bietet für jede einen Haken.

| Schlüssel | Name | Wirkung | Parameter | Technik |
| --- | --- | --- | --- | --- |
| `rule_living_walls` | Alles lebt | Weiches Gewebe wächst langsam nach (Löcher schließen sich), Wände bluten bei Treffern | Nachwachsrate, Material | periodischer Wachstumsschritt im Kern (Reaktion „Luft neben Fleisch → Fleisch“ mit kleiner Chance) |
| `rule_paperwork` | Papierkrieg | Fast alles Feste ist Papier: brennt extrem schnell, Feuer breitet sich weit aus | Brennbarkeit-Faktor | Materialwerte des Universums |
| `rule_bounce` | Gummiwelt | Geschosse prallen +2-mal mehr ab, Fallen verursacht keinen Schaden, Sprünge federn | Abpraller, Sprungfaktor | Geschoss-Bounce-Bonus, Spieler-Physik |
| `rule_tiny` | Winzig | Du bist auf Ameisengröße geschrumpft: Gegenstände der Welt sind riesig, Schwerkraft wirkt halb so stark, Wasser bildet große, zähe Tropfen | Schwerkraft-Faktor | globale Schwerkraft für Körper und Geschosse |
| `rule_beat` | Bass | Alle 0,5 s ein Beat: Licht flackert, Kreaturen bewegen sich im Takt, Geschosse, die auf dem Beat abgefeuert werden, treffen 25 % härter | Takt, Bonus | Taktgeber in `Run`, Licht-Modulation |
| `rule_flooded` | Geflutet | Große Teile stehen unter Wasser: Auftrieb, Feuer erlischt, Strom breitet sich im Wasser aus, Luft wird knapp (Atem-Leiste) | Atemdauer | Wasser-Material, Atem-Status |
| `rule_low_gravity` | Schwerelos-ish | Schwerkraft 40 %, Pulver und Flüssigkeiten fließen langsam | Faktor | wie `rule_tiny` ohne Maßstab |
| `rule_reverse_gravity` | Kopfüber | Schwerkraft zeigt nach oben (Pulver, Flüssigkeit, Körper) | – | Kern: Fallrichtung umkehrbar (größerer Eingriff, nach MVP) |
| `rule_darkness` | Finsternis | Kein Umgebungslicht; nur Lichtquellen | – | Licht-Parameter |
| `rule_rain` | Dauerregen | Es regnet ein Material (Wasser, Säure, Sirup …) | Material, Dichte | Zellen am oberen Rand der Simulationszone |
| `rule_slowtime` | Zähe Zeit | Simulation läuft mit halber Rate, Spieler normal | Faktor | Schrittzahl pro Bild |
| `rule_hot` | Hitzewelle | Brennbares entzündet sich von selbst mit kleiner Chance, Flüssigkeiten verdampfen | Chance | Reaktionstabelle |
| `rule_cold` | Frost | Wasser gefriert zu Eis (rutschig), Feuer erlischt schneller | – | Reaktionstabelle, Reibung |
| `rule_transmute` | Wechselstube | Alle 20 s verwandelt sich ein Material im Sichtbereich in ein anderes | Intervall, Paare | Ereignis in `Run` |
| `rule_magnet` | Magnetisch | Metall zieht Metallgeschosse und -gegenstände an | Stärke | Kraftfeld auf Geschosse und Gegenstände |

MVP verwendet: `rule_living_walls`, `rule_paperwork`, `rule_bounce`, `rule_tiny`, `rule_beat`, `rule_flooded`.

**Rang-Steigerung der MVP-Regeln** (je höher der Rang, desto stärker die Regel):

| Regel | Rang 1 | Rang 2 | Rang 3 |
| --- | --- | --- | --- |
| `rule_living_walls` | Nachwachsen langsam (1 Zelle/s je 100 Randzellen) | doppelt so schnell | dreifach; nachgewachsenes Fleisch kann Geschosse schlucken |
| `rule_paperwork` | Brennbarkeit ×1,5 | ×2 | ×3, Funken entzünden Papier aus 3 px Abstand |
| `rule_bounce` | +2 Abpraller | +3 | +4, auch Gegnergeschosse prallen mehrfach |
| `rule_tiny` | Schwerkraft 50 % | 45 % | 40 %, Riesenschritt doppelt so oft |
| `rule_beat` | Takt 0,5 s, Bonus 25 % | 0,4 s, 25 % | 0,33 s, 30 %; Gegner nur auf dem Beat verwundbar für volle Wirkung |
| `rule_flooded` | Atem 15 s | 11 s | 8 s, Wasser steigt alle 60 s um 20 px |

## Verhaltensbibliothek

Verhalten sind kombinierbare Bausteine. Eine Kreatur hat eine **Haltung** (wie sie zu dir steht) und **Fähigkeiten** (was sie tut).

## **Haltungen**

| Schlüssel | Bedeutung |
| --- | --- |
| `hostile` | greift an, sobald sie dich sieht |
| `neutral` | ignoriert dich, bis sie oder ihre Gruppe getroffen wird; danach `hostile` |
| `passive` | greift nie an; flieht, wenn getroffen |
| `trader` | bietet Handel an (E); wird beraubt (getötet) → alle Händler im Lauf verlangen 50 % mehr, Behörde +1 Fahndung |

## **Fähigkeiten**

| Schlüssel | Name | Beschreibung |
| --- | --- | --- |
| `graze` | Weiden | wandert ziellos, frisst ein Material (entfernt Zellen), wächst dabei leicht |
| `pack` | Rudel | Mitglieder einer Gruppe teilen Wissen: wird eines angegriffen, kommen alle |
| `hunt` | Jagen | verfolgt dich über Wegsuche und Geruch (Blutspur, Kolben-Flüssigkeiten) |
| `retaliate` | Gegenwehr | getroffen → sucht den Schützen auch außer Sicht (Weg zur Trefferquelle) |
| `dig` | Graben | bewegt sich durch Material bis zur angegebenen Härte, frisst einen Gang |
| `steal` | Stehlen | schnappt den Kolben in der Hand oder ein Modul aus dem Rucksack und flieht; Tritt oder Tod gibt es zurück |
| `split` | Teilen | wird bei Treffern ab einer Schadensschwelle zu zwei kleineren (max. 2 Generationen) |
| `flee` | Fliehen | hält Abstand, sucht Deckung |
| `transform` | Verwandeln | trifft dich oder andere Kreaturen mit Verwandlung (wie bisher, kurz) |
| `ranged` | Fernkampf | schießt mit Muster-Waffen (vorhandene Technik) |
| `melee` | Nahkampf | Biss, Schlag, Sturz |
| `shield` | Schild | blockt Geschosse aus einer Richtung, muss umgangen werden |
| `reflect` | Spiegeln | wirft Geschosse zurück (nur bestimmte Kategorien) |
| `armor` | Panzer | nimmt von durchschlagenden Geschossen nur 25 % Schaden |
| `summon` | Rufen | holt Verstärkung (Gruppe oder Behörde) |
| `stationary` | Festsitzend | bewegt sich nicht |
| `aura` | Aura | trägt im Umkreis periodisch einen Status- oder Heil-/Schadenseffekt auf (`slow`, `poison`, `heal_allies`, `stamp_tax`, `shock`) |
| `teleport` | Kurzsprung | versetzt sich bei Gefahr oder nach dem Schuss auf eine nahe freie Luftzelle (`40–110 px`) |
| `kamikaze` | Selbstsprengung | stürzt sich auf das Ziel und zündet bei Kontakt (`≤ 16 px`) eine Elementar-Explosion |
| `burrow` | Eingraben | taucht kurzzeitig durch weiches Material ab und bricht nahe dem Ziel wieder hervor |

## **Allgemeine Regeln für alle Kreaturen**

- Jeder Angriff hat ein **Ausholen** (≥ 0,4 s, sichtbar).
- `retaliate` ist für alle Haltungen außer `passive` Standard. Fernschüsse aus sicherer Entfernung bleiben möglich, haben aber Folgen.
- Kreaturen sind **immer sichtbar** und per Mauszeiger erkennbar (wie jetzt).

## Fraktionen

| Fraktion | Verhalten zu anderen |
| --- | --- |
| Einheimische (je Universum) | untereinander friedlich; verteidigen ihr Universum |
| Behörde | jagt Cloita; greift Einheimische an, die Cloita helfen; wird von allen anderen gehasst |
| Böse Ichs | eigene Fraktion (nur im Endkampf und bei der Behörde) |

Einheimische verschiedener Arten greifen sich gegenseitig an, wenn sie von fremden Geschossen getroffen werden (Kollateralschaden erzeugt Streit).

## Fahndungsstufe (Behörde)

- 0–5 Sterne. Steigt durch: getötete neutrale oder passive Kreaturen (+0,25), getötete Händler (+1 bis +3), verletzte Händler (+1,5), große Zerstörung (Sachbeschädigung durch zerstörte Zellen), verbotene Großzauber (+0,5) und Diebstahl im Laden (+1 bis +2).
- Sinkt automatisch bei jedem Werkstatt-Besuch (Cloita taucht unter / Aktenablage) und kann zusätzlich gegen Gold am **Akten-Schredder** (`ws_shredder`) in der Werkstatt aktiv gesenkt werden.
- Ab Stufe 1 erscheinen **Agenten** in Universen (Kapitel 05): Streifenagenten (`agent_streife`), Aktendrohnen (`agent_drohne`), Vollstrecker (`agent_vollstrecker`) und ab Stufe 4 Abteilungsleiter (`agent_abteilungsleiter`).
- Anzeige: Sterne/Siegel in der HUD neben dem Gold.

## Materialien

### Grenze der Engine

Die Palette fasst heute **höchstens 21 Materialien** (8-Bit-Palette: Materialien × 3 Varianten × 4 Lichtstufen ≤ 256). Mit vielen Universen reicht das nicht. Lösung (Arbeitspaket T1): **Materialsatz je Universum** – 11 Grundmaterialien gelten überall, bis zu 10 weitere lädt jedes Universum selbst (die Material-IDs 11–20 bedeuten je Universum etwas anderes; Reaktionstabelle und Palette werden beim Betreten geladen). Kolben, Module mit Füllungen und Speicherstände speichern Materialien deshalb **per Schlüssel**, nicht per ID.

### Grundmaterialien (überall)

| ID | Schlüssel | Name | Art | Härte | Wirkung |
| --- | --- | --- | --- | --- | --- |
| 0 | `air` | Leere | – | – | – |
| 1 | `bedrock` | Weltrand | fest | unzerstörbar | Rand, Werkstatt |
| 2 | `rock` | Fels | fest | hart | allgemeiner Stein, Splitter → Sand |
| 3 | `dirt` | Erde | fest | weich | gräbt sich leicht |
| 4 | `sand` | Sand | Pulver | weich | rieselt |
| 5 | `water` | Wasser | flüssig | – | löscht Feuer, macht nass, leitet Strom |
| 6 | `oil` | Öl | flüssig | – | schwimmt, sehr brennbar, macht ölig |
| 7 | `fire` | Feuer | Glut | – | wie bisher |
| 8 | `smoke` | Rauch | Gas | – | wie bisher |
| 9 | `steam` | Dampf | Gas | – | entsteht aus Wasser + Feuer, verbrüht leicht |
| 10 | `fluxschnaps` | Flux-Schnaps | flüssig | – | nur in der Werkstatt; Trinken: Beschwipst (Kapitel 06) |

Damit bleiben je Universum **10 eigene Materialien** (IDs 11–20).

Universumsmaterialien stehen in Kapitel 03.

### Gold als Material

Gold ist **kein** Material, sondern ein Gegenstand (Münzen, Haufen), damit es nie vom Kern gelöscht wird. Goldadern in Wänden (`gold_vein`) sind ein Universumsmaterial, das beim Zerstören Münzen fallen lässt (Kern meldet zerstörte Goldzellen an `Run`).

## Heilung und Leben

- **Werkstatt:** volle Heilung bei jedem Besuch.
- **Lebenskapsel:** +20 maximales Leben und volle Heilung (1 pro Universum, versteckt).
- **Selbstexperimente** mit Heilwirkung (Kapitel 07).
- Keine Flüssigkeit heilt ohne Selbstexperiment.

## Flux (Mana)

Funktioniert wie das bisherige Mana (lädt von selbst nach, je Waffe). Anzeige als türkis leuchtende Leiste mit Flux-Symbol. Flüssigkeiten geben nur Schübe (Kapitel 06).

## Wirtschaft (Gold)

| Quelle | Menge (Rang 1 / 2 / 3) |
| --- | --- |
| Normale Kreatur | 5–10 / 10–18 / 18–30 |
| Große Kreatur | 40 / 70 / 110 |
| Zwischengegner | 200 / 350 / 500 |
| Goldhaufen in der Welt | 6–8 Haufen je Universum, 10–40 × Rang |
| Fundkiste | 20–60 × Rang + Gegenstand |
| Minispiele | siehe Kapitel 07 |

| Ausgabe | Preis |
| --- | --- |
| Modul beim Händler | 50–120 × (1 + 0,25 × Stufe) |
| Waffe beim Händler | 160 + 70 × (Stufe − 1) |
| Fabrikator-Bau | Modulpreis × 0,7 + Proben |
| Selbstexperiment neu würfeln | 100, verdoppelt sich |
| Minispiel-Einsatz | 20–50 |

## Fabrikator (Handwerk)

- Jedes Modul, das Cloita je besessen hat, wird zum **Bauplan** (dauerhaft im Archiv, also auch für spätere Läufe).
- Ein Bau kostet **Gold** und **Proben**: Geschosse 1 Probe, Aufsätze 1 Probe, Zünder 2 Proben, Füllungen 1 Probe des passenden Universums (Füllungen mit Universumsmaterial brauchen die Probe genau dieses Universums).
- Pro Werkstatt-Besuch höchstens **3 Bauten** (der Fabrikator überhitzt).
- Seltenheit 3+ (Kapitel 06) braucht zusätzlich einen **Bauplan-Splitter** (selten in Fundkisten oder von Zwischengegnern).

## Begleiterin Klonita

- **Folgt** Cloita in 20–40 px Abstand, kann laufen, springen und klettern, teleportiert nach, wenn sie zu weit zurückbleibt.
- **Unverwundbar im Spiel:** Schaden lässt sie umfallen; nach 5 s steht sie wieder auf („Au! Das war bestimmt keine Absicht!“). Sie blockiert keine Geschosse von Cloita (sie gehen durch sie durch).
- **Nützlich:**
  - *Zeigen:* steht sie still und zeigt in eine Richtung, liegt dort ein Geheimnis, eine Lebenskapsel oder ein Erinnerungssplitter (Abklingzeit 60 s).
  - *Tragen:* hebt Gegenstände auf, die Cloita nicht erreicht (rennt hin und bringt sie, 1 Gegenstand je 30 s).
  - *Umarmen:* passive und neutrale Kreaturen in ihrer Nähe bleiben friedlich, solange sie nicht getroffen werden.
  - *Auffangen:* fällt Cloita mehr als 120 px, fängt Klonita sie mit kleiner Chance (25 %) auf.
  - *Aktive Kampf- & Schutzhilfen (`assist`):*
    - `shield` (Abklingzeit 18 s): löscht ein feindliches Geschoss kurz vor Cloita (`< 28 px`) mit einem Schutzfunken.
    - `snack` (Abklingzeit 35 s): wirft Cloita bei wenig Leben (`< 35 %`) einen Heil-Snack (`+12 HP`) zu.
    - `spark` (Abklingzeit 4,5 s): verschießt einen kleinen lila Hilfsfunken (`6` Schaden) auf nahe Angreifer (`< 90 px`).
    - `cleanse` (Abklingzeit 22 s): tupft Feuer, Frost oder einen negativen Stempel (`stamped_bad`) von Cloita ab.
- **Hinderlich:**
  - *Zu nett:* Gibt sie Händlern ungefragt Trinkgeld (selten, 5–15 Gold) oder nascht bei vollem Beutel eine gewöhnliche Probe gegen 15 Gold Trostpflaster (`sample_nibble`).
  - *Füttern / Anstupsen:* Bleibt sie neben einer Kreatur stehen, gibt sie ihr manchmal etwas zu essen (die Kreatur heilt sich um 20 %), stupst aus Neugier ein glänzendes Fass an (`shiny_poke`) oder niest Funken neben Schlafenden (`loud_sneeze`).
  - *Warnung:* Sehr selten ruft sie einem Gegner „Pass auf, sie schießt gleich!“ zu (Gegner weicht einmal aus).
  - Die Nachteile sind selten genug, um zu schmunzeln, nicht zu frustrieren (Faustregel: höchstens einmal pro Universum).
- **Kommentare:** Text-Blasen über ihrem Kopf, Anlässe und Mengen in Kapitel 08.
- **Taste „Klonita rufen / wegschicken“** (frei belegbar, Standard **K**, Controller: linker Stick drücken):
  - *Rufen:* Klonita kommt sofort her (teleportiert, wenn sie weit weg ist) und folgt wieder.
  - *Wegschicken:* Klonita winkt, sagt etwas Gekränktes und setzt sich in die Werkstatt auf die Couch. Kein Folgen, keine Sprüche, keine Vor- und Nachteile, bis man sie ruft.
- **Von selbst erscheinen** (auch wenn sie weggeschickt ist, dann nur kurz, und sie geht danach wieder):
  - beim ersten Betreten jedes Universums (`enter_universe`: winkt, ein Spruch),
  - wenn Cloita unter 20–25 % Leben fällt (`player_low_hp`, einmal je Universum: „Du siehst gar nicht gut aus!“, zeigt auf die nächste Lebenskapsel, falls bekannt),
  - wenn ein Erinnerungssplitter in der Nähe ist (`memory_shard`: zeigt darauf),
  - zu Beginn jedes Zwischengegner-Kampfs und des Endkampfs (`boss_spawn`: feuert an),
  - wenn die Fahndungsstufe auf 3+ Sterne steigt (`wanted_high`) oder ein Universums-Ereignis startet (`event_start`),
  - wenn Cloita stirbt (sitzt neben ihr, Spruch auf dem Tod-Bildschirm).

## Status-Effekte

Bestehende bleiben (brennend, nass, ölig, verschleimt, vergiftet, verwandelt). Neu:

| Schlüssel | Name | Quelle | Wirkung |
| --- | --- | --- | --- |
| `drunk` | Beschwipst | Flux-Schnaps u. a. | Flux lädt 50 % schneller, Zielen schwankt |
| `sticky` | Klebrig | Kaugummi, Honig, Siegellack | Bewegung 50 %, Springen 70 % |
| `stamped` | Genehmigt / Abgelehnt | Stempler | Genehmigt: +20 % Schaden 15 s; Abgelehnt: −20 % Schaden 15 s |
| `breath` | Atemnot | `rule_flooded` | Atem-Leiste läuft ab, dann Schaden |
| `tiny` | Geschrumpft | später | – |
| `frozen` | Unterkühlt | Frost | langsamer |
| `charged` | Geladen | Strom | nächster Treffer gibt Stromschlag weiter |

## Was bleibt wie bisher (nicht vergessen beim Umbau)

Härtestufen, Splitter-Aufräumen, Einmauer-Schutz, Treten mit Taumeln, Geschosse durch Flüssigkeit, Speichern jederzeit, Protokoll mit allen Ereignissen (Schlüssel auf neue Begriffe umstellen), Sandbox mit Gottmodus und Modulbuch, Steuerung und Controller, Hover-Infos, Archiv-Freischaltungen (bekannte Module häufiger im Laden, Startgold je besiegtem Zwischengegner).
