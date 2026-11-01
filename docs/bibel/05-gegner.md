# 05 – Gegner

Werte gelten für Rang 1; Rang 2 und 3 multiplizieren Leben und Schaden (Kapitel 02). Leben der Spielfigur zum Vergleich: 100.

Jede Kreatur braucht: Sprite mit den Zuständen aus Kapitel 01 plus Sonderzustände, Mauszeiger-Text (Kapitel 08), 2–3 Geräusche (Laut, Angriff, Tod), Tod-Rückstand (Material oder Brocken).

## Einheimische (normale Kreaturen)

### Fleischwelt

**Fleischmade (`fleischmade`)** – 16×10

- Haltung `hostile`; Fähigkeiten `melee`, `hunt`, `retaliate`.
- Leben 25, Tempo 50, Biss 8 (Ausholen: bäumt sich auf, Maul öffnet sich rot, 0,4 s), springt Hindernisse an.
- Aussehen: fette, rosa-graue Made mit kleinen Stummelbeinen und einem Mund voller Menschenzähne; Speichelfaden.
- Sonderzustand `burrow_out` (2 Frames): kommt aus dem Fleisch gekrochen.
- Tod: zerplatzt zu Blut, Fleischbrocken.
- Schwäche: Feuer.

**Blutegel (`blutegel`)** – 12×6 (hängend 6×12)

- Haltung `hostile`; `melee`, `hunt`; hängt an Decken und lässt sich fallen.
- Leben 15, Biss 4 + saugt 2/s, solange festgesaugt (Treten oder Wasser löst ihn).
- Aussehen: glänzender schwarzroter Wurm mit Saugnapf voller Ringe.
- Sonderzustände `hang` (2), `latched` (2, wird auf Cloita gezeichnet).
- Schwäche: Salz/Wasser löst ihn, Feuer.

**Säurespucker (`saeurespucker`)** – 14×14

- Haltung `hostile`; `ranged` (Säure-Bogenschuss), `retaliate`; immun gegen Säure.
- Leben 32, Tempo 35, Schuss 9 (Ausholen: bläht Kehlsack grünlich auf, 0,45 s).
- Aussehen: geschwollener Magenschleim-Polyp mit Trichtermaul und gelb-grünen Säureblasen.
- Tod: zerplatzt zu Magensäure; lässt manchmal `probe_gallenstein` fallen.
- Schwäche: Feuer.

**Zottenwurm (`zottenwurm`)** – 20×8

- Haltung `neutral`; `graze` (Fleisch), `burrow`, `melee`, `retaliate`.
- Leben 38, Tempo 45, Biss 8 (Ausholen: richtet Vorderkörper auf, 0,4 s).
- Aussehen: segmentierter Darmzotten-Wurm mit feinen Sinneshärchen.
- Tod: Fleischbrocken, gelegentlich `probe_wucherung`.

### Aktenhalde

**Aktenfresser (`aktenfresser`)** – 20×17

- Haltung `neutral`; `dig` (Papier, Aktendeckel), `melee`, `retaliate`, `pack`.
- Leben 40, Tempo 35, Schlag 10 (Ausholen: Schublade/Maul klappt weit auf, 0,5 s).
- Frisst sich durch Papier und hinterlässt saubere Gänge; frisst Kolben-Flüssigkeit nicht.
- Aussehen: lebender, zerknitterter Aktenstapel mit Reißverschlussmaul, Büroklammer-Zähnen, kleinen Ordnerfüßen; ein Post-it als Zunge.
- Sonderzustand `dig` (4 Frames): Papierfetzen fliegen.
- Tod: zerfällt zu Papier und Asche; lässt manchmal ein Formular (Probe) fallen.
- Schwäche: Feuer (brennt sofort, rennt brennend herum und zündet die Regale an – gefährlich auch für Cloita).

**Stempler (`stempler`)** – 12×18

- Haltung `neutral`; `melee`, `summon` (ruft bei Angriff 1 Agent), `retaliate`, `aura` (`stamp_tax`).
- Leben 30, Tempo 30.
- Verhalten: kommt auf Cloita zu, wenn sie nah ist, und stempelt sie (Ausholen: hebt den Riesenstempel, 0,6 s). Zufällig **„Genehmigt“** (Status gut) oder **„Abgelehnt“** (Status schlecht, 5 Schaden). Wird er angegriffen, stempelt er nur noch „Abgelehnt“ und ruft einen Agenten (Alias `stempelkaefer`).
- Aussehen: kleines, gebücktes Wesen aus Stempelkissen mit dünnen Beinen und einem riesigen Holzstempel als Arm; Brille auf der Nasenspitze.
- Sonderzustand `stamp` (3).
- Tod: Stempelfarbe spritzt.

**Paragraphenreiter (`paragraphenreiter`)** – 16×20

- Haltung `hostile`; fliegt, `ranged` (Paragraphen-Strahl), `summon` (ruft Stempler/Streife), `retaliate`.
- Leben 36, Tempo 55, Strahl 9 (Ausholen: paragraphenförmiges Messinghorn leuchtet auf, 0,45 s).
- Aussehen: schwebender Bürokrat auf einem geflügelten Gesetzbuch.
- Tod: Papierfetzen, gelegentlich `probe_formular`.

**Kaffeegolem (`kaffeegolem`)** – 18×22

- Haltung `neutral`; `melee`, `ranged` (heißer Dampf/Kaffeesatz), `transform` / `morph` (überkocht unter 50 % Leben: schneller), `retaliate`.
- Leben 55, Tempo 32.
- Aussehen: klobige Kaffeemaschine auf Aktenschrank-Beinen mit brodelndem Glaskolben-Kopf.
- Tod: Dampf und Scherben, gelegentlich `probe_stempelkissen`.

### Glibbria

**Hüpfling (`huepfling`)** – 10×10

- Haltung `passive`; `flee`, `graze` (frisst Zuckerguss), Gruppen von 3–6.
- Leben 12; springt ständig; bei Gefahr springt er hoch davon.
- Lässt beim Tod Brauseperlen (Gold-Ersatz: 3 Gold) und Sirup.
- Aussehen: runde, glasige Geleekugel mit zwei Kulleraugen und Grübchen-Lächeln; in ihm schwimmt eine Erdbeere.
- Sonderzustand `squash` (2, beim Landen platt).
- Bedeutung: harmlos, aber wer sie tötet, bekommt Fahndung (+0,25) und Klonita ist traurig.

**Glibberteiler (`glibberteiler`)** – 18×14 → 12×10 → 8×7

- Haltung `hostile`; `melee`, `hunt`, `split` (2 Generationen), `armor` gegen durchschlagende Geschosse (gleitet um sie herum; Alias `quallenhund`).
- Leben 40 (Teile: 20, 10), Sprungangriff 9 (Ausholen: wird flach und zittert, 0,5 s).
- Aussehen: grimmiger, rot-grüner Geleeklumpen mit zu kleinen Zähnen und wütenden Augenbrauen.
- Tod der kleinsten Stufe: Glibber-Fleck.
- Schwäche: Feuer (Glibber schmilzt), Explosionen erzeugen aber neue Teile.

**Zuckerwattewolke (`zuckerwatte_wolke`)** – 18×14

- Haltung `passive`; fliegt, `flee`, `aura` (`slow`: verklebt Angreifer im Umkreis von 40 px).
- Leben 24, Tempo 45.
- Aussehen: schwebende, rosa-blaue Zuckerwatte mit verschlafenen Augen.
- Tod: löst sich in Schaum und `probe_brauseperle` auf.

**Konfettikanone (`konfetti_kanone`)** – 16×16

- Haltung `hostile`; `ranged` (bunte Salve), `reflect` (`bounce`: prallt Geschosse von oben ab, Alias `trampolin_frosch`), `retaliate`.
- Leben 38, Tempo 28, Salve 8 (Ausholen: bläst Backen auf, Lunte blitzt, 0,5 s).
- Aussehen: laufendes Partyhütchen-Geschütz auf Gummifüßen.
- Tod: Brausesirup und `probe_glibberkern`.

### Krümelreich

**Ameisenkrieger (`ameisenkrieger`)** – 18×12

- Haltung `hostile`; `pack`, `hunt` (folgt Zucker- und Duftspuren, auch dem Ameisenduft-Kolben), `melee`, `dig` (Brösel, Krümel).
- Leben 22, Tempo 70, Biss 7, Gruppen von 4–8. Spritzt aus der Ferne Ameisensäure (`ranged`, Ausholen: Hinterleib nach vorn gekrümmt, 0,5 s).
- Aussehen: rote Ameise mit Helm aus einer Fingerhut-Hälfte, Zahnstocher-Speer, große Mandibeln.
- Tod: zerfällt in Chitinbrocken.

**Blattlaus (`blattlaus`)** – 12×10

- Haltung `passive`; `graze` (frisst Zucker/Pflanzenmaterial), wird von Ameisen beschützt (greift man eine Blattlaus an, werden alle Ameisen im Umkreis feindlich).
- Leben 10. **Treten** melkt sie (`giver = True`): sie lässt Honigtau (Honig) fallen, ohne beim ersten Tritt zu sterben (Abklingzeit 8 s).
- Aussehen: dicke, hellgrüne Laus mit Babyface und kleinem Melkeimer-Muster auf dem Rücken.

**Arbeiterameise (`arbeiterameise`)** – 14×10

- Haltung `neutral`; `pack`, `steal` (trägt lose Goldmünzen oder Proben weg), `dig` (Brösel), `retaliate`.
- Leben 18, Tempo 65, Biss 5 (Ausholen: Mandibeln spreizen sich, 0,4 s).
- Aussehen: flinke braun-rote Ameise mit Tragekorb aus einem Kronkorken.
- Tod: lässt Getragenes und manchmal `probe_zuckerkristall` fallen.

**Harzspucker (`harzspucker`)** – 16×14

- Haltung `hostile`; `ranged` (klebriger Karamell-/Harzschuss, setzt `sticky`), `aura` (`slow`), `retaliate`.
- Leben 34, Tempo 40, Schuss 7 (Ausholen: Hinterleib leuchtet bernsteinfarben, 0,5 s).
- Aussehen: gedrungene Ameisen-Artillerie mit Harzdüse auf dem Rücken.
- Tod: Karamell-Pfütze und gelegentlich `probe_ameisenduft`.

### Sporenklub

**Türsteherpilz (`tuersteherpilz`)** – 18×24

- Haltung `neutral`; `stationary`, `shield` (vorne), `melee`, `retaliate`.
- Leben 80. Steht in engen Durchgängen. Spricht Cloita an: „Name steht nicht auf der Liste.“ Gegen 20 Gold (E) tritt er beiseite. Angriff: Stoß 15 mit Rückstoß (Ausholen: krempelt die Lamellen hoch, 0,6 s).
- Aussehen: breiter Fliegenpilz mit Sonnenbrille, Muskelarmen und Klemmbrett; Lamellen wie ein Bart.
- Schwäche: von hinten verwundbar (Schild nur vorne).

**Sporenschnorrer (`sporenschnorrer`)** – 10×14

- Haltung `hostile`; `steal` (Kolben in der Hand, Gold oder ein zufälliges Modul aus dem Rucksack), `flee`, `split` (Alias `kappenschleicher`).
- Leben 18, sehr schnell (110). Schleicht sich an, schnappt sich etwas (Ausholen: reibt sich die Hände, 0,4 s) und rennt davon. Tötet man ihn, fällt das Gestohlene heraus; nach 30 s verschwindet er mit der Beute in einem Pilzloch.
- Aussehen: dünner, grinsender Pilz mit Kapuze, viel zu langen Fingern und einer leuchtenden Glatze.
- Sonderzustände `steal` (3), `carry` (4).

**Sporenwerfer (`sporenwerfer`)** – 14×18

- Haltung `hostile`; `ranged` (Sporenkugel), `aura` (`poison` im Umkreis von 36 px), `retaliate`.
- Leben 32, Tempo 35, Schuss 8 (Ausholen: Hut zieht sich zusammen und glüht türkis, 0,45 s).
- Aussehen: bauchiger Leuchtpilz mit Katapult-Lamellen.
- Tod: Wolke aus `leuchtsporen`, gelegentlich `probe_leuchtspore`.
- Schwäche: Feuer.

**Leuchtmotte (`leuchtmotte`)** – 12×12

- Haltung `passive`; fliegt, `flee`, `aura` (`heal_allies`: heilt nahe Pilz-Kreaturen leicht).
- Leben 16, Tempo 60; spendet farbiges Club-Licht (`glow`).
- Aussehen: flauschige Neon-Motte mit Disco-Facettenaugen.
- Tod: Glitzerstaub und gelegentlich `probe_plattennadel`.

### Versunkene Abtei

**Mönchsfisch (`moenchsfisch`)** – 14×16

- Haltung `neutral`; `pack` (Chor), `ranged` (Blasenstrahl), `retaliate`.
- Leben 28. Singt in Gruppen: solange 3+ singen, bekommen alle Kreaturen im Umkreis +25 % Schaden (sichtbar als Notensymbole). Angriff: Blase, die Cloita einschließt und langsam nach oben trägt (Ausholen: plustert die Kiemen auf, 0,5 s).
- Aussehen: Fisch in brauner Kutte mit Kapuze, Tonsur aus Schuppen, faltet die Flossen.
- Schwäche: Strom.

**Orgelaal (`orgelaal`)** – 28×6 (Segmente)

- Haltung `hostile`; `hunt` im Wasser, `ranged` (Stromstoß im Wasser, Ausholen: Körper leuchtet von hinten nach vorne auf, 0,7 s), `burrow` (Alias `weihrauch_aal`).
- Leben 35. Schwimmt nur im Wasser; außerhalb zappelt er hilflos.
- Aussehen: langer Aal aus Orgelpfeifen-Segmenten, Mund wie ein Blasebalg.
- Prozedurale Segmente (5 Teile).

**Glockenqualle (`glockenqualle`)** – 14×18

- Haltung `passive`; schwimmt, `aura` (`shock` im Radius 36 px), `retaliate`.
- Leben 26, Tempo 30; glüht im Dunkeln (`glow`).
- Aussehen: durchscheinende Qualle mit einem kleinen Bronze-Klöppel im Schirm.
- Tod: lässt `probe_glockensplitter` oder Wasser fallen.

**Korallenwächter (`korallenwaechter`)** – 16×20

- Haltung `neutral`; `shield` / `reflect` (reflektiert Standardgeschosse an seiner Buntglas-Schale), `melee`, `retaliate`.
- Leben 50, Tempo 28, Stoß 11 (Ausholen: hebt Buntglas-Schild, 0,5 s).
- Aussehen: Einsiedlerkrebs in einer zerbrochenen Kirchenfenster-Rosette mit Kerzenstumpf auf dem Rücken.
- Tod: Buntglassplitter und gelegentlich `probe_kerzenstumpf`.

## Große Kreaturen & Unter-Zwischenbosse

**Trampolinwal (`trampolinwal`, Glibbria)** – 56×32, aus Teilen (Kopf, Rumpf, Schwanz, Flossen)

- Haltung `neutral`; schwebt langsam über den Inseln. Sein Rücken federt wie ein Trampolin (Cloita kann darauf springen und so hohe Stellen erreichen).
- Wird er angegriffen: `hostile`; Bauchklatscher (Ausholen: steigt hoch, Schatten am Boden wird dunkler, 1,0 s) mit großer Druckwelle (20 Schaden, schleudert alles weg); bläst Sirupfontänen.
- Leben 300. Beute: 40 Gold, Glibberkern.
- Aussehen: rosa Wal aus Gelee, durch den man die Mahlzeiten sieht (ein Fahrrad, ein Schuh), Fontäne aus Sirup.

**Kirchenkrake (`kirchenkrake`, Versunkene Abtei)** – 48×40, aus Teilen (Mantel, 6 Tentakel, Augen)

- Haltung `hostile` in ihrer Kammer, sonst schlafend (schläft, bis Lärm > Schwelle: Explosionen, Glocke).
- Tentakelschläge (Ausholen: Tentakel wird zurückgezogen und leuchtet, 0,6 s), Tintenwolke (macht dunkel), zieht Cloita unter Wasser.
- Leben 350. Beute: 40 Gold, Glockensplitter.
- Aussehen: Krake mit Glockenhelm auf dem Kopf, Tentakel halten Kerzen und Gesangbücher.

### Unter-Zwischenbosse (`is_mid_boss = True`)

Zusätzlich zur großen Kreatur bzw. in der Zwischen-Arena (`mid_boss_arena`) jedes Universums wacht ein schneller Unter-Zwischenboss (`hp` 140–200, garantiert 1 Probe + Zwischenboss-Gold):

| Schlüssel | Name | Universum | Fähigkeiten & Angriff |
| --- | --- | --- | --- |
| `pfuetzenwurm` | Pfützenwurm | Fleischwelt | `burrow` (Fleisch), Säure-Salve |
| `aktenwolf` | Aktenwolf | Aktenhalde | `transform`/`morph` (Alpha-Wut unter 50 % HP), `aura` (`stamp_tax`) |
| `manege_clown` | Glibber-Kommandant | Glibbria | `split`, Hüpf-Bomben |
| `harzgeneral` | Harzgeneral | Krümelreich | `summon` (`ameisenkrieger`), klebrige Harz-Salve |
| `sporenherz` | Sporenherz | Sporenklub | `summon` (`sporenwerfer`), `aura` (`poison`) |
| `glockenwaechter` | Glockenwächter | Versunkene Abtei | `aura` (`shock`), Schall-Nova |

## Behörden-Agenten (Kampf)

| Schlüssel | Leben | Verhalten | Angriff (Ausholen) |
| --- | --- | --- | --- |
| `agent_streife` | 45 | `hostile`, `hunt`, `ranged`, `pack`, `retaliate` (Alias `agent_sachbearbeiter`) | Formularblitz / Stempel-Projektil 8 (zieht Klemmbrett, 0,4 s); verfolgt über Wegsuche |
| `agent_drohne` | 15 | `hostile`, fliegt, `summon` | markiert Cloita 10 s (Scheinwerfer an, 0,5 s); alle Agenten kennen dann ihre Position |
| `agent_vollstrecker` | 120 | `hostile`, `shield`, `reflect`, `melee`, `armor` | Stempelschlag 20 mit Druckwelle (hebt den Stempel, 0,8 s) |
| `agent_abteilungsleiter` | 160 | `hostile`, fliegt, `summon` (`agent_streife`), `ranged` | Paragraphen-Strahl 14 (hebt Doppelstempel, 0,6 s), ab Fahndungsstufe 4 |

Beute: Gold 15 / 40 / 5, Agenten lassen gelegentlich einen „Dienstausweis“ fallen (Archiv-Fundstück mit Hinweisen aufs wahre Ende).

## Zwischengegner

Je Rang zwei, der Seed wählt einen. Jeder hat ein Heimat-Universum (Zuordnung in Kapitel 02), kämpft in dessen Arena und übernimmt dessen Regel und Materialien. Jeder hat **3 Phasen** (bei 100–66 %, 66–33 %, 33–0 % Leben), jede mit eigener Angriffsmischung und sichtbarem Phasenwechsel (kurze Pause, Brüllen, Farbwechsel). Gegen reine Fernkampf-Taktik: Jeder hat mindestens eine Mechanik, die Abstand bestraft oder Deckung verlangt.

### Rang 1

**Der Oberstempler (`oberstempler`)** – 64×56

- Riesiger Beamter aus gestapelten Schreibtischen mit einem Gesicht aus einer Wanduhr, zwei Riesenstempel-Arme.
- Leben 900.
- Phase 1: Stempelschläge auf den Boden (Ausholen 0,8 s, Schatten), hinterlassen Siegellack-Pfützen.
- Phase 2: verteilt Formulare – fliegende Papiergeschosse, die Cloita verfolgen; ruft 2 Agenten.
- Phase 3: „Akte geschlossen“: Wände aus Aktendeckeln fahren von links und rechts heran (Raum wird enger); Fernkämpfer werden eingeklemmt.
- Schwäche: Feuer (aber die Arena brennt dann mit).
- Beute: 200 Gold, Bauplan-Splitter, Stempelkissen.

**Mutter Glibber (`mutter_glibber`)** – 72×48

- Riesiger Gelee-Berg mit Krönchen; in ihr schwimmen Hüpflinge.
- Leben 800.
- Phase 1: springt und landet mit Druckwelle (Ausholen: zieht sich zusammen, 0,7 s).
- Phase 2: teilt sich bei jedem großen Treffer (bis zu 4 Kinder, je 80 Leben) – Flächenschaden ist hier nachteilig.
- Phase 3: zieht alle Kinder wieder ein und rollt durch die Arena.
- Schwäche: Feuer; Explosionen erzeugen Kinder.
- Beute: 200 Gold, Glibberkern ×2.

### Rang 2

**DJ Myzel (`dj_myzel`)** – 56×64

- Riesiger Pilz am DJ-Pult, Plattenteller als Schilde, Lautsprechertürme links und rechts.
- Leben 1400.
- Phase 1: Schallwellen im Takt (sichtbare Ringe, nur auf dem Beat ausweichen nötig).
- Phase 2: „Drop“: alle 8 Beats ein Bass-Drop, der alles hochschleudert; Tanzschwarm als Schild.
- Phase 3: zerstört das Pult und kämpft selbst, Sporenwolken (Beschwipst).
- Mechanik gegen Fernkampf: Plattenteller-Schilde reflektieren Geschosse, die nicht auf dem Beat treffen.
- Beute: 350 Gold, Bauplan-Splitter, Plattennadel.

**Abt Kieme (`abt_kieme`)** – 48×64

- Uralter Mönchsfisch auf einer schwebenden Kanzel, Orgelpfeifen auf dem Rücken.
- Leben 1300.
- Phase 1: Orgelstöße (Druckwellen durch Wasser), Chor aus Mönchsfischen.
- Phase 2: flutet die Arena schrittweise; Luftblasen sind die einzigen sicheren Orte.
- Phase 3: Glocke als Waffe: Glockenschläge elektrisieren das ganze Wasser – auf Plattformen bleiben.
- Mechanik gegen Fernkampf: Die Kanzel schirmt nach unten und vorne ab; man muss über ihn.
- Beute: 350 Gold, Glockensplitter ×2.

### Rang 3

**Die Ameisenkönigin (`ameisenkoenigin`)** – 96×56, aus Teilen (Kopf, Brust, riesiger Hinterleib)

- Liegt im Thronsaal des Baus, Hinterleib füllt die halbe Arena; Krone aus einem Ring.
- Leben 2200.
- Phase 1: legt Eier, aus denen Ameisenkrieger schlüpfen; Säurestrahl.
- Phase 2: gräbt sich durch den Bau und taucht an anderer Stelle auf (Bodenbeben als Ankündigung).
- Phase 3: Flügel – fliegt und lässt Säure regnen.
- Mechanik gegen Fernkampf: Krieger jagen den Schützen; Graben macht Distanz wertlos.
- Beute: 500 Gold, Bauplan-Splitter, Riesenzuckerkristall.

**Das Weltenherz (`weltenherz`)** – 64×64

- Das schlagende Herz der Fleischwelt (der alte Endgegner, aufgewertet), an Adern aufgehängt.
- Leben 2400.
- Phase 1: Blutfontänen im Herzschlag (Takt sichtbar, Ankündigung durch Aufblähen).
- Phase 2: Glutblut-Adern brechen in der Arena auf, Wände wachsen schneller nach (Regel verstärkt).
- Phase 3: reißt sich los und rollt/fliegt durch die Arena; ruft Fleischmaden.
- Mechanik gegen Fernkampf: Wände wachsen nach und schließen Schusslinien; nachwachsende Fleischschilde.
- Beute: 500 Gold, Gallenstein ×2.

## Böse Ichs (Endkampf)

Jedes böse Ich kämpft in einer eigenen kleinen Heimatwelt (ca. 1280×720). Es hat 4 Phasen, spricht Cloita an (Textblasen), und nutzt eine **eigene Waffe mit Modulen** (vorhandene Gegner-Muster-Technik), die man nach dem Sieg erbeutet.

**Kaiserin Cloita (`boese_kaiserin`)** – Heimat: Thronsaal aus Gold auf einem eroberten Planeten (Universumsmaterial `goldboden`: rutschig).

- Leben 3500.
- Kräfte: Leibwächter-Klone (schwächere Cloitas, `agent`-Verhalten), Goldregen (Münzen als Geschosse – man kann sie auch aufsammeln), Umhang-Sprint durch die Arena.
- Phase 4: setzt sich auf den Thron, der zur Kanone wird.
- Eigenheit: verhandelt – bietet Cloita in Phase 2 „die Hälfte des Multiversums“ an (Annehmen = Spiel endet mit bösem Ende, Archiv-Eintrag).

**Die Gütige Cloita (`boese_gute`)** – Heimat: weiße Kathedrale aus Licht (Regel `rule_darkness` umgekehrt: alles hell, Licht schadet).

- Leben 3200.
- Kräfte: heilt ihre Anhänger und sich selbst, Lichtstrahlen, „Bekehrung“ – verwandelt Kreaturen in ihre Anhänger, versucht auch Klonita zu bekehren (Klonita bleibt 10 s auf ihrer Seite, harmlos, aber traurig).
- Phase 4: Heiligenschein wird zur Sägeklinge.

**Cloita-Ω (`boese_omega`)** – Heimat: Fabrikhalle mit Fließbändern und Pressen.

- Leben 3800.
- Kräfte: Armkanone, Drohnenschwarm, Fließbänder bewegen Cloita, Pressen zermalmen.
- Phase 3: lädt ihr Bewusstsein in eine Riesenmaschine um (Arena-Boss aus Teilen).
- Phase 4: wieder klein, schnell, verzweifelt.

Alle bösen Ichs tragen irgendwo das Siegel der Behörde (Hinweis aufs wahre Ende). Nach dem Sieg: Waffe des bösen Ichs, Archiv-Eintrag.

## Wahres Ende: Der Rat der bösen Ichs (`rat`)

Nur mit allen 6 Erinnerungssplittern eines Laufs. Nach dem Sieg über das böse Ich öffnet sich das Portal zum **Hauptquartier der Behörde**: ein endloser Aktensaal, an dessen Ende der Rat tagt. Kein Werkstatt-Besuch dazwischen; Cloita wird aber voll geheilt („Die Splitter erinnern sich an dich“).

**Stufe 1 – Die Anhörung:** Ein Gremium aus 5 maskierten Behörden-Räten (Agenten-Optik mit Roben) sitzt hinter einem langen Pult. Sie schicken Wellen von Agenten und lassen Formulare regnen. Jeder Rat, der fällt, verliert die Maske: darunter eine weitere Cloita (je eine kurze Zeile: „Ich war die Cloita, die *nie* das Labor aufgeräumt hat.“).

**Stufe 2 – Die bösen Ichs:** Die drei bösen Ichs, die Cloita **nicht** im Endkampf besiegt hat (im MVP: die zwei übrigen), treten nacheinander an, jeweils mit verkürzter Phasenfolge (2 statt 4 Phasen). Das zuletzt besiegte böse Ich ist schon tot, sein Platz bleibt demonstrativ leer.

**Stufe 3 – Die Verschmelzung:** Alle besiegten Cloitas (Räte und böse Ichs) werden zu einem Fluxstrudel gesogen und verschmelzen zur **Ober-Cloita** (`ober_cloita`, ca. 96×96 aus Teilen): ein Turm aus Cloita-Köpfen, Armen mit Waffen aller Ichs, Krone der Kaiserin, Heiligenschein der Gütigen, Drohnen von Ω.

- Leben 6000, 3 Phasen; jede Phase nutzt Angriffe eines anderen Ichs, die letzte alle gemischt.
- Mechanik: Jeder abgeschlagene Kopf lässt einen Splitter fallen; Klonita sammelt sie ein und wirft sie Cloita zu (kurzer Schub). Klonita hilft hier ausnahmsweise mit – das einzige Mal im Spiel, in dem sie „kämpft“ (sie umarmt die Ober-Cloita und hält sie 3 s fest).
- Tod: Die Ober-Cloita zerfällt in unzählige kleine Cloitas, die in alle Universen davonlaufen (Schlusswitz: das Multiversum ist nicht gerettet, nur sehr viel voller).

**Ende:** Kurzer Text-Abspann über Bilder aus Sprites; Archiv-Eintrag „Wahres Ende“; danach Titel. Im Archiv wird die Ober-Cloita sichtbar.

Grafik zusätzlich: Ratsmitglied (16×26, 2 Varianten der Robe), Ratspult (Kulisse 120×32), Ober-Cloita (Teile: 6 Köpfe, 6 Arme, Rumpf, Krone, Heiligenschein, Drohnen wiederverwenden), Verschmelzungs-Effekt (8 Frames), kleine flüchtende Cloita (8×12, 4 Frames).
