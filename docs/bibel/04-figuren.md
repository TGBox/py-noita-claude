# 04 – Figuren

## Cloita (Spielfigur, `cloita`)

**Geschichte:** Cloita war die brillanteste und rücksichtsloseste Wissenschaftlerin ihres Heimat-Universums. Bei einem Experiment mit dem Multiversum erschuf sie aus Versehen einen Durchgang, durch den eine andere Cloita kam – eine, die all ihre schlechten Eigenschaften hatte und keine der guten (sie selbst würde sagen: „Welche guten?“). Diese andere Cloita übernahm ihre Welt, ihr Labor und ihren Namen. Seither springt Cloita mit einer zusammengeschraubten Waffe von Universum zu Universum, um ihr böses Ich zu finden und zu vernichten. Dass es unendlich viele böse Cloitas gibt, hat sie noch nicht ganz verdaut.

**Persönlichkeit (für Texte):** genial, ungeduldig, sarkastisch, hält Moral für eine Rechenungenauigkeit. Mag Klonita mehr, als sie zugibt.

**Aussehen (14×24):**

- Wildes, abstehendes Haar in `hair` (Orange), eine Strähne steht wie eine Antenne hoch.
- Schutzbrille mit runden Gläsern in `flux_l` auf der Stirn; schiebt sie beim Zielen herunter (Frame-Variante `aim`).
- Zu großer, fleckiger Laborkittel (`coat`) mit Brandloch am Saum und einem Kolben in der Brusttasche.
- Darunter lila Pulli (`cloth`), dunkle Hose (`n2`), schwere Stiefel (`n1`).
- Gesichtsausdruck: leicht genervtes Grinsen; beim Treffer zusammengekniffene Augen.

**Animationen:**

| Zustand | Frames | Beschreibung |
| --- | --- | --- |
| `idle` | 4 | atmet, Haarsträhne wippt, tippt alle 3 s mit dem Fuß |
| `run` | 6 | Kittel flattert nach hinten |
| `jump` | 2 | Knie angezogen |
| `fall` | 2 | Arme hoch, Kittel nach oben |
| `float` | 4 | Schweben: kleine Flux-Funken unter den Stiefeln (Jetpack-Sohlen) |
| `aim` | 1 | Brille unten (Überlagerung, kombinierbar mit allen Zuständen) |
| `kick` | 3 | Tritt nach vorn |
| `drink` | 3 | Kolben an den Mund, Kopf zurück |
| `hurt` | 1 | zusammengezuckt |
| `death` | 5 | fällt um, Brille fliegt weg; danach übernimmt die Physik (Brocken, Blut) |
| `swim` | 4 | für `rule_flooded` |
| `tiny_scared` | 2 | nur Krümelreich: kurzes Erschrecken beim Riesenschritt |

**Waffe:** wird separat gezeichnet, am Schulterpunkt (wie bisher) zur Maus gedreht. Teile siehe Kapitel 06.

**Sichtbare Selbstexperimente:** Manche Selbstexperimente ändern Cloitas Aussehen (Überlagerungen, je 14×24, nur die geänderten Pixel):

- `asbesthaut`: grauer, rissiger Hautton
- `froschzunge`: Zunge hängt heraus
- `dritter_arm`: kleiner dritter Arm am Rücken, winkt
- `leuchthaar`: Haar leuchtet (`glow`)
- `kiemen`: Kiemenschlitze am Hals

## Klonita (Begleiterin, `klonita`)

**Geschichte:** Cloitas erster Versuch, sich selbst zu klonen, um doppelt so viel zu arbeiten. Das Ergebnis ist körperlich unzerstörbar und unermesslich stark – und unermesslich nett. Klonita liebt alle Lebewesen, auch die, die gerade versuchen, sie zu fressen. Cloita hat dreimal versucht, sie zu „entsorgen“; Klonita hat es jedes Mal für ein Spiel gehalten.

**Persönlichkeit:** herzlich, naiv, begeistert von allem, nennt Gegner „kleiner Freund“, entschuldigt sich bei Wänden, die Cloita sprengt. Hat sich selbst einen Namen gegeben („Klonita, weil ich ein Klon bin! Und weil es nett klingt!“).

**Aussehen (14×24):**

- Gleiche Proportionen wie Cloita, aber weicher: runde Schultern, kein Kittel.
- Gleiches Haar, aber gekämmt und mit einer Schleife (`clone_d`).
- Rosa Strickpulli mit aufgesticktem Herz (`clone`), Latzhose (`clone_d`), Hausschuhe mit Hasenohren.
- Riesige, glänzende Augen (2×2 Glanzpixel), immer lächelnd.
- Eine kaum sichtbare Naht am Hals (Klon-Narbe) in `skin_d`.

**Animationen:**

| Zustand | Frames | Beschreibung |
| --- | --- | --- |
| `idle` | 4 | wiegt sich hin und her, summt (Notensymbol als Effekt) |
| `run` | 6 | hüpfend |
| `jump` | 2 | |
| `point` | 2 | zeigt mit ausgestrecktem Arm (Hinweis auf Geheimnis) |
| `carry` | 4 | trägt einen Gegenstand über dem Kopf |
| `hug` | 3 | umarmt eine Kreatur (über der Kreatur gezeichnet) |
| `feed` | 3 | hält etwas hin |
| `knocked` | 3 | fällt um, Sternchen über dem Kopf |
| `getup` | 3 | steht auf, klopft sich ab |
| `wave` | 2 | winkt (bei Ankunft in einem Universum) |
| `cover_ears` | 2 | hält sich die Ohren zu (Explosionen, Glocke) |
| `swim` | 4 | |

## Händler (Werkstatt, `npc_*`)

Pro besuchtem Universum kann ein Händler in der Werkstatt auftauchen (bis zu 2 gleichzeitig). MVP: ein Händler je Universum.

| Schlüssel | Name | Universum | Aussehen (12–18 × 18–26) | Spezialität |
| --- | --- | --- | --- | --- |
| `npc_magenhaendler` | Herr Pansen | Fleischwelt | Wandelnder Magen mit Melone (Hut) und Monokel, Tentakel als Arme | Füllungen aus Fleischwelt-Materialien |
| `npc_sachbearbeiterin` | Frau Abheft | Aktenhalde | Aktenordner mit Brille, Ärmelschoner, Stempel als Hand | Zünder; verlangt eine „Bearbeitungsgebühr“ (+10 Gold) |
| `npc_glibberhaendler` | Wobbel | Glibbria | Grüner Gelee-Würfel mit Strohhut, Dinge schwimmen in ihm | Aufsätze; hüpft beim Reden |
| `npc_ameisenhehler` | Krümel-Karl | Krümelreich | Ameise mit Trenchcoat und Sonnenbrille, öffnet den Mantel zum Verkaufen | Proben-Tausch, billige gestohlene Module |
| `npc_dj` | DJ Lamelle | Sporenklub | Pilz mit Kopfhörern, die Lamellen leuchten im Takt | Geschosse; verkauft nur auf dem Beat |
| `npc_kuester` | Bruder Flosse | Versunkene Abtei | Mönchsfisch in Kutte, Taucherhelm aus Glas | Waffen; segnet sie (zufälliger kleiner Bonus) |

Jeder Händler hat `idle` (4 Frames) und `talk` (2 Frames) sowie 5 Sprüche (Kapitel 08).

## Behörden-Agenten (`agent_*`)

Die Behörde ordnet das Multiversum – angeblich. Ihre Agenten sind identisch aussehende Beamte in Anzügen, deren Gesichter hinter einer glatten Maske mit dem Behördensiegel verborgen sind (später: unter der Maske steckt jeweils eine Cloita).

| Schlüssel | Name | Größe | Aussehen | Rolle |
| --- | --- | --- | --- | --- |
| `agent_streife` | Streifenagent | 12×22 | grauer Anzug (`agent`), Maske mit Siegel (Kreis mit Auge), Aktenkoffer | Grundtyp, schießt Formularblitze |
| `agent_vollstrecker` | Vollstrecker | 16×24 | breiter, Mantel, Schulterlampe, schwerer Stempel als Waffe | ab Fahndungsstufe 3, Schild aus Panzerglas |
| `agent_drohne` | Aktendrohne | 10×8 | fliegender Aktenkoffer mit Propeller und Kameraauge | ab Stufe 2, markiert Cloita (alle Agenten wissen dann, wo sie ist) |

Gemeinsames Merkmal: das **Siegel der Behörde** (Kreis, darin ein Auge mit Stempelrand). Das Siegel taucht auch bei den bösen Ichs versteckt auf (Hinweis aufs Metaziel).

## Böse Ichs (Optik)

Alle drei sind erkennbar Cloita (Haar, Statur), aber jede mit eigener Silhouette und Farbwelt. Kampf in Kapitel 05.

| Schlüssel | Name | Herkunft | Aussehen |
| --- | --- | --- | --- |
| `boese_kaiserin` | Kaiserin Cloita | ein Universum, das sie erobert hat | Rüstung aus Gold (`gold`), Umhang, Krone mit Antenne, Haar zu einem riesigen Turm frisiert; Leibwächter-Klone |
| `boese_gute` | Die Gütige Cloita | ein Sekten-Universum | Weiße Kutte, Heiligenschein aus Flux (`flux_l`, leuchtend), lächelt wie Klonita – aber mit leeren Augen; schwebt |
| `boese_omega` | Cloita-Ω | ein Maschinen-Universum | Halb Roboter: ein Arm ist eine Kanone, ein Auge ein roter Sensor (`danger`), Kabel statt Haar an einer Seite; Drohnen umkreisen sie |

Jedes böse Ich: 16×26 Kern-Sprite mit `idle`, `move`, `windup` (je Angriff), `attack`, `hurt`, `phase` (Übergang), `death` (5 Frames + großer Effekt), dazu Effektteile (Umhang, Heiligenschein, Drohnen) als eigene Sprites.
