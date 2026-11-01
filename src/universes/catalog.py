"""The six MVP universes (bible chapter 03), mid-bosses and evil selves (chapter 05).

Only the data that the bible fixes is filled in; generators, creatures and texts follow
universe by universe in Phase C (``ready`` turns True there). Until a universe has its
own material set it borrows the organism set ("koerper").
"""

from __future__ import annotations

from typing import Any

from src.universes.model import Region, Universe


class _UniverseCatalogTuple(tuple[Universe, ...]):
    """Tuple of Universe instances that also supports dict-like lookup by universe key."""

    def keys(self):
        return BY_KEY.keys()

    def values(self):
        return BY_KEY.values()

    def items(self):
        return BY_KEY.items()

    def get(self, key: str, default: Universe | None = None) -> Universe | None:
        return BY_KEY.get(key, default)

    def __getitem__(self, key: int | slice | str) -> Any:  # type: ignore[override]
        if isinstance(key, str):
            return BY_KEY[key]
        return super().__getitem__(key)


UNIVERSES: tuple[Universe, ...] = (
    Universe(
        "fleischwelt", "Fleischwelt",
        "Ein Universum, das nur aus einem einzigen, sehr großen und sehr hungrigen Lebewesen "
        "besteht.",
        rule="rule_living_walls", shape="quadrat", ambient=0.28, material_set="koerper",
        regions=(
            Region("schlund", "Schlund"), Region("magen", "Magen"),
            Region("knochenmark", "Knochenmark"),
        ),
        natives=("fleischmade", "blutegel"), event="verdauung",
        samples=("gallenstein", "wucherungsableger"),
        music_de="tiefe Drones, Herzschlag",
        arena_de="runde Knochenhalle mit Fleischboden, der nachwächst",
        klonita_de=("Hörst du das? Ich glaube, die Welt hat Hunger.",),
        ready=True,
    ),
    Universe(
        "aktenhalde", "Aktenhalde",
        "Hier wurde vor Äonen ein Antrag gestellt. Er wird noch bearbeitet.",
        rule="rule_paperwork", shape="breit", ambient=0.55, material_set="aktenhalde",
        regions=(
            Region("registratur", "Registratur"), Region("grossraumbuero", "Großraumbüro"),
            Region("archivkeller", "Archivkeller"),
        ),
        natives=("aktenfresser", "stempler"), event="pruefung",
        samples=("stempelkissen", "formular_b38"),
        music_de="Schreibmaschinen-Rhythmus, Fahrstuhlmusik in Moll",
        arena_de="großer Sitzungssaal mit Tischen als Plattformen, Papierboden",
        klonita_de=("So viel Papier! Wollen wir allen einen Brief schreiben?",),
    ),
    Universe(
        "glibbria", "Glibbria",
        "Ein Planet aus Wackelpudding. Alles federt. Niemand stirbt am Fall – nur an allem "
        "anderen.",
        rule="rule_bounce", shape="inseln", ambient=0.6, material_set="koerper",
        regions=(
            Region("geleehuegel", "Gelee-Hügel"), Region("sirupkueste", "Sirupküste"),
            Region("kaugummihoehlen", "Kaugummi-Höhlen"),
        ),
        natives=("huepfling", "glibberteiler"), big="trampolinwal", event="brauseregen",
        samples=("glibberkern", "brauseperle"),
        music_de="fröhlicher Synthesizer mit schiefen Tönen, Tempo hoch",
        arena_de="große Gelee-Schüssel, Wände federn",
    ),
    Universe(
        "kruemelreich", "Krümelreich",
        "Du bist etwa so groß wie ein Brotkrümel. Das Brot ist größer. Die Ameisen auch.",
        rule="rule_tiny", shape="breit", ambient=0.7, material_set="koerper",
        regions=(
            Region("fliesenwueste", "Fliesenwüste"),
            Region("unter_dem_kuehlschrank", "Unter dem Kühlschrank", (("ambient", 0.2),)),
            Region("ameisenbau", "Ameisenbau", (("ambient", 0.2),)),
        ),
        natives=("ameisenkrieger", "blattlaus"), event="riesenschritt",
        samples=("riesenzuckerkristall", "ameisenduft"),
        music_de="Pizzicato-Streicher, Grillenzirpen",
        arena_de="Teetasse (Rand als Wände, Teesatz am Boden)",
    ),
    Universe(
        "sporenklub", "Sporenklub",
        "Die Party läuft seit 400 Jahren. Die Pilze wollen nicht, dass sie aufhört.",
        rule="rule_beat", shape="quadrat", ambient=0.15, material_set="koerper",
        regions=(
            Region("tanzflaeche", "Tanzfläche"), Region("hinterzimmer", "Hinterzimmer"),
            Region("lautsprechertuerme", "Lautsprechertürme"),
        ),
        natives=("tuersteherpilz", "sporenschnorrer"), event="bass_drop",
        samples=("leuchtspore_im_glas", "plattennadel"),
        music_de="Four-on-the-floor mit verzerrtem Bass, 120 BPM",
        arena_de="Hauptbühne mit DJ-Pult und Lautsprechertürmen",
    ),
    Universe(
        "abtei", "Versunkene Abtei",
        "Die Mönche haben ein Schweigegelübde abgelegt. Dann haben sie Kiemen bekommen.",
        rule="rule_flooded", shape="hoch", ambient=0.35, material_set="koerper",
        regions=(
            Region("glockenturm", "Glockenturm"), Region("kirchenschiff", "Kirchenschiff"),
            Region("krypta", "Krypta"),
        ),
        natives=("moenchsfisch", "orgelaal"), big="kirchenkrake", event="glockenschlag",
        samples=("glockensplitter", "kerzenstumpf"),
        music_de="Orgel-Drone, Unterwasser-Gluckern, gregorianisches Summen",
        arena_de="Kirchenschiff mit Luftblase unter der Kuppel",
    ),
)  # fmt: skip

BY_KEY: dict[str, Universe] = {u.key: u for u in UNIVERSES}
UNIVERSES = _UniverseCatalogTuple(UNIVERSES)


# Mid-bosses per rank: (boss key, home universe). Bible chapter 02 / 05.
MID_BOSSES: dict[int, tuple[tuple[str, str], ...]] = {
    1: (("oberstempler", "aktenhalde"), ("mutter_glibber", "glibbria")),
    2: (("dj_myzel", "sporenklub"), ("abt_kieme", "abtei")),
    3: (("ameisenkoenigin", "kruemelreich"), ("weltenherz", "fleischwelt")),
}

# The three evil selves; the seed picks one for the final fight in its own home world.
EVIL_SELVES: tuple[str, ...] = ("boese_kaiserin", "boese_gute", "boese_omega")
