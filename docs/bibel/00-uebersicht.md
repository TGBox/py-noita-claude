# Cloita Interdimensional – Inhalts- und Grafikbibel

Stand: 2026-11-01. Gilt für die **erste spielbare Fassung** (MVP). Alles, was danach kommt, steht als Pool-Liste in Kapitel 03 und als Merkliste in Kapitel 09.

Diese Bibel ist die verbindliche Vorlage für Inhalte, Texte und Grafik. Agenten arbeiten sie kapitelweise ab. Was hier nicht steht, wird nicht erfunden, sondern als offene Frage notiert (Kapitel 09, „Offene Fragen“).

## Kapitel

| Datei | Inhalt | Wer braucht es |
|---|---|---|
| `00-uebersicht.md` | Zweck, Begriffe, Namensregeln | alle |
| `01-stil.md` | Grafikstil, Paletten, Größen, Animation, Dateiformat, Abnahme | Grafik |
| `02-systeme.md` | Lauf-Aufbau, Regel- und Verhaltensbibliothek, Materialien, Wirtschaft, Begleiterin, Behörde | Code, Inhalte |
| `03-universen.md` | Die 6 MVP-Universen im Detail, Pool für später | Inhalte, Grafik |
| `04-figuren.md` | Cloita, Klonita, Händler, Behörden-Agenten, böse Ichs (Optik) | Grafik, Texte |
| `05-gegner.md` | Einheimische, große Kreaturen, Zwischengegner, böse Ichs (Kampf) | Code, Grafik |
| `06-waffen-und-module.md` | Waffenrahmen, 60 Basismodule, Familien, Flüssigkeits-Schübe | Code, Grafik |
| `07-gegenstaende-und-werkstatt.md` | Gegenstände, Proben, Selbstexperimente, Werkstatt, Minispiele | Code, Grafik |
| `08-ui-und-texte.md` | Oberfläche, Icons, Logo, Tonfall, Textmengen | Grafik, Texte |
| `09-arbeitspakete.md` | Reihenfolge, Pakete mit Abnahmekriterien, „Nicht vergessen“, offene Fragen | alle |

## Grundidee in drei Sätzen

Die verrückte Wissenschaftlerin **Cloita** jagt durch zufällige Universen ihr **böses Ich**, das jedes Mal aus einer anderen Welt stammt. Jedes Universum hat eigene **Regeln**, Materialien und Bewohner, aber alles läuft über dieselbe Pixel-Physik, in der alles mit allem reagiert. Zwischen den Universen liegt ihre **Werkstatt**; begleitet wird sie von **Klonita**, einer misslungenen, viel zu netten Klonkopie.

## Ton

Absurde Komik zuerst, mit viel schwarzem Humor: Die Welten sind bunt und albern, die Folgen deiner Taten oft grausam-komisch. Niemand kommentiert ernst, was passiert – außer Klonita, die alles herzerwärmend findet. Eigene Figuren und Begriffe; keine Anleihen an Namen, Figuren, Designs oder Sprüche bestehender Serien.

## Begriffe: alt → neu

Der harte Schnitt benennt fast alles um. Die Engine bleibt; die Tabelle zeigt, was im Code welchem neuen Begriff entspricht.

| Bisher (Code / Biohorror) | Neu (Spiel) | Code-Schlüssel neu (Vorschlag) |
|---|---|---|
| Augmentation (Stab) | **Waffe** | `weapon` (Klasse `Wand` darf intern bleiben) |
| Baustein | **Modul** | `module` |
| Drüse (Form) | **Geschoss** | `Category.FORM` → Anzeige „Geschoss“ |
| Mutation (Modifikator) | **Aufsatz** | `Category.MODIFIER` → „Aufsatz“ |
| Nerv (Auslöser) | **Zünder** | `Category.TRIGGER` → „Zünder“ |
| Sekret (Nutzlast) | **Füllung** | `Category.PAYLOAD` → „Füllung“ |
| Mana | **Flux** | `flux` |
| Blutperlen | **Gold** | `gold` |
| Tiefe / Stufe | **Universum** | `universe` |
| Sanktum | **Werkstatt** | `workshop` |
| Wächter (Boss einer Tiefe) | **Zwischengegner** | `mid_boss` |
| Das Herz | **Böses Ich** | `evil_self` |
| Perk / Perk-Altar | **Selbstexperiment** / **Experimentierliege** | `experiment` |
| Herzklumpen | **Lebenskapsel** | `life_capsule` |
| Brutkokon | **Fundkiste** | `crate` |
| Urauge (Geheimnis) | **Erinnerungssplitter** | `memory_shard` |
| Weltenportal (Parallelwelt) | **Wackelportal** | `wobble_portal` |
| Kodex | **Archiv** | `archive` |
| Phiole | **Kolben** | `flask` (Code darf bleiben) |
| Beutel | **Rucksack** (Fächer) | unverändert |
| Neues Spiel+ | **Noch einmal, nur schlimmer** (Anzeige), intern NG+ | unverändert |

## Namensregeln

- **Code-Schlüssel:** englisch oder deutsch ohne Umlaute, `snake_case`, eindeutig über alle Kategorien. Beispiel: `aktenfresser`, `rule_bounce`, `mod_funkenwerfer`.
- **Anzeigenamen:** Deutsch, mit Umlauten, kurz (max. 22 Zeichen), gern mit Wortwitz. Keine Namen realer Personen, Marken oder fremder Werke.
- **Beschreibungen:** ein Satz Wirkung, optional ein zweiter Satz Humor. Max. 120 Zeichen.
- **Sprites:** Dateiname = Code-Schlüssel.

## Was erhalten bleibt (nicht neu bauen, nur umbenennen oder anpassen)

Falling-Sand-Engine mit Rust-Kern, Licht, Reaktionstabelle, Starrkörper-Brocken, Härtestufen, Waffen-Deck-Mechanik (Mehrfachwurf, Zünder, Ladungen, Familien), Rucksack mit Stapeln und Sortierung, Kolben (gießen, füllen, trinken, werfen, wechseln), Treten, Mauszeiger-Infos, frei belegbare Steuerung und Controller, Speichern jederzeit, Lauf-Protokoll, Sandbox mit Gottmodus und Modulbuch, Optionen, Archiv, Statistik, Parallelwelten.
