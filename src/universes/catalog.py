"""The six MVP universes (bible chapter 03), mid-bosses and evil selves (chapter 05).

Only the data that the bible fixes is filled in; generators, creatures and texts follow
universe by universe in Phase C/D (``ready`` turns True there). Until a universe has its
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
        return ALL_UNIVERSES.get(key, default)

    def __getitem__(self, key: int | slice | str) -> Any:  # type: ignore[override]
        if isinstance(key, str):
            return ALL_UNIVERSES[key]
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
        natives=("fleischmade", "blutegel", "saeurespucker", "zottenwurm"),
        event="verdauung",
        samples=("probe_gallenstein", "probe_wucherung"),
        sample_key="probe_gallenstein",
        mid_boss="pfuetzenwurm",
        boss="weltenherz",
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
        natives=("aktenfresser", "stempler", "paragraphenreiter", "kaffeegolem"),
        event="pruefung",
        samples=("probe_stempelkissen", "probe_formular"),
        sample_key="probe_stempelkissen",
        mid_boss="aktenwolf",
        boss="oberstempler",
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
            Region("gelee_huegel", "Geleehügel"), Region("kaugummi_hoehlen", "Kaugummihöhlen"),
            Region("sirupkueste", "Sirupküste"),
        ),
        natives=("huepfling", "glibberteiler", "zuckerwatte_wolke", "konfetti_kanone"),
        big="trampolinwal", event="brauseregen",
        samples=("probe_glibberkern", "probe_brauseperle"),
        sample_key="probe_glibberkern",
        mid_boss="manege_clown",
        boss="mutter_glibber",
        music_de="fröhlicher Synthesizer mit schiefen Tönen, Tempo hoch",
        arena_de="große Gelee-Schüssel, Wände federn",
    ),
    Universe(
        "kruemelreich", "Krümelreich",
        "Du bist etwa so groß wie ein Brotkrümel. Das Brot ist größer. Die Ameisen auch.",
        rule="rule_tiny", shape="breit", ambient=0.7, material_set="koerper",
        regions=(
            Region("fliesenwueste", "Fliesenwüste"),
            Region("unter_kuehlschrank", "Unter Kühlschrank", (("ambient", 0.2),)),
            Region("ameisenbau", "Ameisenbau", (("ambient", 0.2),)),
        ),
        natives=("ameisenkrieger", "blattlaus", "arbeiterameise", "harzspucker"),
        event="riesenschritt",
        samples=("probe_zuckerkristall", "probe_ameisenduft"),
        sample_key="probe_zuckerkristall",
        mid_boss="harzgeneral",
        boss="ameisenkoenigin",
        music_de="Pizzicato-Streicher, Grillenzirpen",
        arena_de="Teetasse (Rand als Wände, Teesatz am Boden)",
    ),
    Universe(
        "sporenklub", "Sporenklub",
        "Die Party läuft seit 400 Jahren. Die Pilze wollen nicht, dass sie aufhört.",
        rule="rule_beat", shape="quadrat", ambient=0.15, material_set="koerper",
        regions=(
            Region("lautsprechertuerme", "Lautsprechertürme"), Region("tanzflaeche", "Tanzfläche"),
            Region("hinterzimmer", "Hinterzimmer"),
        ),
        natives=("tuersteherpilz", "sporenschnorrer", "sporenwerfer", "leuchtmotte"),
        event="bass_drop",
        samples=("probe_leuchtspore", "probe_plattennadel"),
        sample_key="probe_leuchtspore",
        mid_boss="sporenherz",
        boss="dj_myzel",
        music_de="Four-on-the-floor mit verzerrtem Bass, 120 BPM",
        arena_de="Hauptbühne mit DJ-Pult und Lautsprechertürmen",
    ),
    Universe(
        "abtei", "Versunkene Abtei",
        "Die Mönche haben ein Schweigegelübde abgelegt. Dann haben sie Kiemen bekommen.",
        rule="rule_flooded", shape="hoch", ambient=0.35, material_set="koerper",
        regions=(
            Region("glockenturm", "Glockenturm"), Region("kirchenschiff", "Kirchenschiff"),
            Region("krypta", "Krypta", (("ambient", 0.15), ("current_vx", 28.0))),
        ),
        natives=("moenchsfisch", "orgelaal", "glockenqualle", "korallenwaechter"),
        big="kirchenkrake", event="glockenschlag",
        samples=("probe_glockensplitter", "probe_kerzenstumpf"),
        sample_key="probe_glockensplitter",
        mid_boss="glockenwaechter",
        boss="abt_kieme",
        music_de="Orgel-Drone, Unterwasser-Gluckern, gregorianisches Summen",
        arena_de="Kirchenschiff mit Luftblase unter der Kuppel",
    ),
)  # fmt: skip

BY_KEY: dict[str, Universe] = {u.key: u for u in UNIVERSES}
# Only the six MVP universes. The pool universes of the expansion (schrott, kuchen, spule, ...)
# are added in Phase J (docs/erweiterung/03-universen-erweiterung.md).
ALL_UNIVERSES: dict[str, Universe] = dict(BY_KEY)
UNIVERSES = _UniverseCatalogTuple(UNIVERSES)


# Mid-bosses per rank: (boss key, home universe). Bible chapter 02 / 05.
MID_BOSSES: dict[int, tuple[tuple[str, str], ...]] = {
    1: (("oberstempler", "aktenhalde"), ("mutter_glibber", "glibbria")),
    2: (("dj_myzel", "sporenklub"), ("abt_kieme", "abtei")),
    3: (("ameisenkoenigin", "kruemelreich"), ("weltenherz", "fleischwelt")),
}

# The three evil selves; the seed picks one for the final fight in its own home world.
EVIL_SELVES: tuple[str, ...] = ("boese_kaiserin", "boese_gute", "boese_omega")
