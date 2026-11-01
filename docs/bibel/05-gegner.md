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
- Haltung `neutral`; `melee`, `summon` (ruft bei Angriff 1 Agent), `retaliate`.
- Leben 30, Tempo 30.
- Verhalten: kommt auf Cloita zu, wenn sie nah ist, und stempelt sie (Ausholen: hebt den Riesenstempel, 0,6 s). Zufällig **„Genehmigt“** (Status gut) oder **„Abgelehnt“** (Status schlecht, 5 Schaden). Wird er angegriffen, stempelt er nur noch „Abgelehnt“ und ruft einen Agenten.
- Aussehen: kleines, gebücktes Wesen aus Stempelkissen mit dünnen Beinen und einem riesigen Holzstempel als Arm; Brille auf der Nasenspitze.
- Sonderzustand `stamp` (3).
- Tod: Stempelfarbe spritzt.

### Glibbria

**Hüpfling (`huepfling`)** – 10×10
- Haltung `passive`; `flee`, `graze` (frisst Zuckerguss), Gruppen von 3–6.
- Leben 12; springt ständig; bei Gefahr springt er hoch davon.
- Lässt beim Tod Brauseperlen (Gold-Ersatz: 3 Gold) und Sirup.
- Aussehen: runde, glasige Geleekugel mit zwei Kulleraugen und Grübchen-Lächeln; in ihm schwimmt eine Erdbeere.
- Sonderzustand `squash` (2, beim Landen platt).
- Bedeutung: harmlos, aber wer sie tötet, bekommt Fahndung (+0,25) und Klonita ist traurig.

**Glibberteiler (`glibberteiler`)** – 18×14 → 12×10 → 8×7
- Haltung `hostile`; `melee`, `hunt`, `split` (2 Generationen), `armor` gegen durchschlagende Geschosse (gleitet um sie herum).
- Leben 40 (Teile: 20, 10), Sprungangriff 9 (Ausholen: wird flach und zittert, 0,5 s).
- Aussehen: grimmiger, rot-grüner Geleeklumpen mit zu kleinen Zähnen und wütenden Augenbrauen.
- Tod der kleinsten Stufe: Glibber-Fleck.
- Schwäche: Feuer (Glibber schmilzt), Explosionen erzeugen aber neue Teile.

### Krümelreich

**Ameisenkrieger (`ameisenkrieger`)** – 18×12
- Haltung `hostile`; `pack`, `hunt` (folgt Zucker- und Duftspuren, auch dem Ameisenduft-Kolben), `melee`, `dig` (Brösel, Krümel).
- Leben 22, Tempo 70, Biss 7, Gruppen von 4–8. Spritzt aus der Ferne Ameisensäure (`ranged`, Ausholen: Hinterleib nach vorn gekrümmt, 0,5 s).
- Aussehen: rote Ameise mit Helm aus einer Fingerhut-Hälfte, Zahnstocher-Speer, große Mandibeln.
- Tod: zerfällt in Chitinbrocken.

**Blattlaus (`blattlaus`)** – 12×10
- Haltung `passive`; `graze` (frisst Pflanzenmaterial), wird von Ameisen beschützt (greift man eine Blattlaus an, werden alle Ameisen im Umkreis feindlich).
- Leben 10. **Treten** melkt sie: sie lässt Honigtau (Honig) fallen.
- Aussehen: dicke, hellgrüne Laus mit Babyface und kleinem Melkeimer-Muster auf dem Rücken.

### Sporenklub

**Türsteherpilz (`tuersteherpilz`)** – 18×24
- Haltung `neutral`; `stationary`, `shield` (vorne), `melee`, `retaliate`.
- Leben 80. Steht in engen Durchgängen. Spricht Cloita an: „Name steht nicht auf der Liste.“ Gegen 20 Gold (E) tritt er beiseite. Angriff: Stoß 15 mit Rückstoß (Ausholen: krempelt die Lamellen hoch, 0,6 s).
- Aussehen: breiter Fliegenpilz mit Sonnenbrille, Muskelarmen und Klemmbrett; Lamellen wie ein Bart.
- Schwäche: von hinten verwundbar (Schild nur vorne).

**Sporenschnorrer (`sporenschnorrer`)** – 10×14
- Haltung `hostile`; `steal` (Kolben in der Hand oder ein zufälliges Modul aus dem Rucksack), `flee`.
- Leben 18, sehr schnell (110). Schleicht sich an, schnappt sich etwas (Ausholen: reibt sich die Hände, 0,4 s) und rennt davon. Tötet man ihn, fällt das Gestohlene heraus; nach 30 s verschwindet er mit der Beute in einem Pilzloch.
- Aussehen: dünner, grinsender Pilz mit Kapuze, viel zu langen Fingern und einer leuchtenden Glatze.
- Sonderzustände `steal` (3), `carry` (4).

### Versunkene Abtei

**Mönchsfisch (`moenchsfisch`)** – 14×16
- Haltung `neutral`; `pack` (Chor), `ranged` (Blasenstrahl), `retaliate`.
- Leben 28. Singt in Gruppen: solange 3+ singen, bekommen alle Kreaturen im Umkreis +25 % Schaden (sichtbar als Notensymbole). Angriff: Blase, die Cloita einschließt und langsam nach oben trägt (Ausholen: plustert die Kiemen auf, 0,5 s).
- Aussehen: Fisch in brauner Kutte mit Kapuze, Tonsur aus Schuppen, faltet die Flossen.
- Schwäche: Strom.

**Orgelaal (`orgelaal`)** – 28×6 (Segmente)
- Haltung `hostile`; `hunt` im Wasser, `ranged` (Stromstoß im Wasser, Ausholen: Körper leuchtet von hinten nach vorne auf, 0,7 s).
- Leben 35. Schwimmt nur im Wasser; außerhalb zappelt er hilflos.
- Aussehen: langer Aal aus Orgelpfeifen-Segmenten, Mund wie ein Blasebalg.
- Prozedurale Segmente (5 Teile).

## Große Kreaturen

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

## Behörden-Agenten (Kampf)

| Schlüssel | Leben | Verhalten | Angriff (Ausholen) |
|---|---|---|---|
| `agent_streife` | 45 | `hostile`, `hunt`, `ranged`, `pack`, `retaliate` | Formularblitz 8 (zieht Klemmbrett, 0,4 s); verfolgt über Wegsuche |
| `agent_vollstrecker` | 120 | `hostile`, `shield`, `melee`, `armor` | Stempelschlag 20 mit Druckwelle (hebt den Stempel, 0,8 s) |
| `agent_drohne` | 15 | `hostile`, fliegt, `summon` | markiert Cloita 10 s (Scheinwerfer an, 0,5 s); alle Agenten kennen dann ihre Position |

Beute: Gold 15 / 40 / 5, Agenten lassen gelegentlich einen „Dienstausweis“ fallen (Archiv-Fundstück fürs Metaziel).

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

Alle bösen Ichs tragen irgendwo das Siegel der Behörde (Hinweis aufs Metaziel). Nach dem Sieg: Waffe des bösen Ichs, 1 Erinnerungssplitter, Archiv-Eintrag.
