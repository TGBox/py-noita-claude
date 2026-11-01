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
            Region("schlund", "Schlund"), Region("zotten", "Zotten"),
            Region("pfuetze", "Pfütze"),
        ),
        natives=("madenwurm", "blutfliege", "saeurespucker", "bandwurm_kopf"),
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
            Region("wartezone", "Wartezone"), Region("registratur", "Registratur"),
            Region("chefbueros", "Chefbüros"),
        ),
        natives=("papierfresser", "heftklammer_krabbe", "paragraphenreiter", "kaffeegolem"),
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
            Region("zelt", "Zelt"), Region("backstage", "Backstage"),
            Region("manege", "Manege"),
        ),
        natives=("glibber_slime", "brause_geist", "trampolin_frosch", "konfetti_kanone"),
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
            Region("oberbau", "Oberbau"),
            Region("gaenge", "Gänge", (("ambient", 0.2),)),
            Region("thronsaal", "Thronsaal", (("ambient", 0.2),)),
        ),
        natives=("ameisen_soldat", "blattlaus", "arbeiterameise", "harzspucker"),
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
            Region("kappenwald", "Kappenwald"), Region("sporennebel", "Sporennebel"),
            Region("wurzelherz", "Wurzelherz"),
        ),
        natives=("bass_pilz", "sporen_motte", "sporenwerfer", "kappenschleicher"),
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
            Region("schiff", "Schiff"), Region("kreuzgang", "Kreuzgang"),
            Region("krypta", "Krypta", (("current_vx", 28.0),)),
        ),
        natives=("chor_fisch", "kerzen_qualle", "korallenwaechter", "weihrauch_aal"),
        big="kirchenkrake", event="glockenschlag",
        samples=("probe_glockensplitter", "probe_kerzenstumpf"),
        sample_key="probe_glockensplitter",
        mid_boss="glockenwaechter",
        boss="abt_kieme",
        music_de="Orgel-Drone, Unterwasser-Gluckern, gregorianisches Summen",
        arena_de="Kirchenschiff mit Luftblase unter der Kuppel",
    ),
)  # fmt: skip

# Post-MVP pool universes (bible chapter 03, "Der Pool für später") + legacy aliases.
POOL_UNIVERSES: dict[str, Universe] = {
    "schrott": Universe(
        "schrott", "Der Große Schrott",
        "Rostige Zahnräder, tropfendes Öl und ewige Funken.",
        rule="rule_conductivity", shape="quadrat", ambient=0.45, material_set="koerper",
        regions=(
            Region("halde", "Halde"), Region("schmelze", "Schmelze"),
            Region("kernwerk", "Kernwerk"),
        ),
        natives=("rostkaefer", "schweissimp", "magnetwurm", "schrottgolem"),
        samples=("probe_rost", "probe_knochen"),
        sample_key="probe_rost",
        mid_boss="gabelstapler_krabbe",
        boss="schrottpresse",
    ),
    "kuchen": Universe(
        "kuchen", "Die Kuchenkruste",
        "Zuckerguss-Brücken über heißen Karamell-Seen.",
        rule="rule_sugar_crust", shape="quadrat", ambient=0.65, material_set="koerper",
        regions=(
            Region("glasur", "Glasur"), Region("biskuit", "Biskuit"),
            Region("boden", "Boden"),
        ),
        natives=("zuckerspinne", "kerzenkobold", "marzipanschwein", "baiser_geist"),
        samples=("probe_zucker", "probe_zuckerkristall"),
        sample_key="probe_zucker",
        mid_boss="marzipan_ritter",
        boss="hochzeitstorte",
    ),
    "spule": Universe(
        "spule", "Die Summende Spule",
        "Kupfertürme, Kondensatoren und wandernde Lichtbögen.",
        rule="rule_conductivity", shape="hoch", ambient=0.5, material_set="koerper",
        regions=(
            Region("spulenwald", "Spulenwald"), Region("kondensator", "Kondensator"),
            Region("kern", "Kern"),
        ),
        natives=("funkenhornisse", "spulenkrabbe", "kupferschlange", "kondensator_geist"),
        samples=("probe_spule", "probe_aether"),
        sample_key="probe_spule",
        mid_boss="spulenmeister",
        boss="transformator",
    ),
}

BY_KEY: dict[str, Universe] = {u.key: u for u in UNIVERSES}
UNIVERSE_ALIASES: dict[str, str] = {
    "magen": "fleischwelt",
    "amt": "aktenhalde",
    "glibber": "glibbria",
    "ameisen": "kruemelreich",
    "myzel": "sporenklub",
}
ALL_UNIVERSES: dict[str, Universe] = {
    **POOL_UNIVERSES,
    **BY_KEY,
    **{alias: BY_KEY[target] for alias, target in UNIVERSE_ALIASES.items()},
}
UNIVERSES = _UniverseCatalogTuple(UNIVERSES)


# Mid-bosses per rank: (boss key, home universe). Bible chapter 02 / 05.
MID_BOSSES: dict[int, tuple[tuple[str, str], ...]] = {
    1: (("oberstempler", "aktenhalde"), ("mutter_glibber", "glibbria")),
    2: (("dj_myzel", "sporenklub"), ("abt_kieme", "abtei")),
    3: (("ameisenkoenigin", "kruemelreich"), ("weltenherz", "fleischwelt")),
}

# The three evil selves; the seed picks one for the final fight in its own home world.
EVIL_SELVES: tuple[str, ...] = ("boese_kaiserin", "boese_gute", "boese_omega")
