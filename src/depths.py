"""The stages of a run: deeper into the organism, harder, richer, with bosses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Depth:
    key: str
    name_de: str
    # material amounts relative to the base level layout
    bone_dust: float = 1.0
    blood: float = 1.0
    tallow: float = 1.0
    acid: float = 1.0
    growth: float = 1.0
    bridges: float = 1.0
    mucus: float = 0.0
    magma: float = 0.0  # pools of Glutblut
    pus: float = 0.0  # pools of Eiter
    cavity_scale: float = 1.0  # size of the organ cavities
    alveoli: float = 0.0  # clusters of thin-walled air sacs (spongy lung tissue)
    wall: str = "fleisch"  # "fleisch": flesh with bone ribs, "knochen": bone with flesh veins
    # population and loot
    walkers: int = 10
    flyers: int = 5
    spitters: int = 0
    bloats: int = 0
    wands: int = 3
    extra: tuple[tuple[str, int], ...] = ()  # further creatures: (species key, count)
    blocks: int = 8
    ambient: float = 0.3  # base brightness (0 = pitch black, 1 = fully lit)
    boss: str | None = None  # creature key of the boss guarding this depth
    final: bool = False  # killing the boss wins the run


DEPTHS: tuple[Depth, ...] = (
    Depth(
        "schlund", "Der Schlund", acid=0.5, growth=0.5, walkers=9, flyers=4, ambient=0.3,
        extra=(("egel", 3), ("talgsack", 3), ("sporensack", 2)),
    ),
    Depth(
        "magen", "Der Magen", acid=2.6, tallow=1.4, growth=0.6,
        walkers=11, flyers=8, spitters=3, bloats=2, blocks=10, boss="magenwurm", ambient=0.25,
        extra=(("saeurespucker", 4), ("egel", 3), ("saeuresack", 4), ("talgsack", 3)),
    ),
    Depth(
        "knochenmark", "Das Knochenmark", wall="knochen", boss="knochenfresser", bone_dust=2.6, blood=2.0, tallow=1.8,
        acid=0.6, growth=0.4, bridges=0.6, walkers=10, flyers=6, spitters=8, bloats=3, blocks=10,
        ambient=0.27,
        extra=(
            ("saeurespucker", 3), ("nervenknoten", 2), ("egel", 4), ("talgsack", 4),
        ),
    ),
    Depth(
        "gedaerm", "Das Gedärm", blood=1.6, growth=3.0, bridges=1.5, pus=1.0,
        walkers=13, flyers=8, spitters=5, bloats=7, blocks=10, boss="brutmutter", ambient=0.2,
        extra=(
            ("brandmade", 4), ("egel", 6), ("saeurespucker", 2), ("sporensack", 4),
            ("talgsack", 3),
        ),
    ),
    Depth(
        "leber", "Die Leber", blood=0.8, acid=1.8, growth=2.2, tallow=1.2, pus=2.2,
        bridges=0.8, cavity_scale=0.85, walkers=12, flyers=7, spitters=4, bloats=4, blocks=10,
        ambient=0.22,
        extra=(
            ("saeurespucker", 5), ("egel", 5), ("saeuresack", 4), ("talgsack", 2),
            ("schleimkriecher", 1), ("gestaltwandler", 2),
        ),
    ),
    Depth(
        "lunge", "Die Lunge", blood=0.6, acid=0.4, growth=1.6, tallow=0.5, bridges=2.0,
        mucus=1.0, cavity_scale=1.45, alveoli=1.0,
        walkers=8, flyers=10, spitters=5, bloats=9, blocks=10, ambient=0.24, boss="atem",
        extra=(
            ("schleimkriecher", 4), ("augenblase", 3), ("egel", 4), ("sporensack", 5),
        ),
    ),
    Depth(
        "herzkammer", "Die Herzkammer", blood=2.4, acid=1.0, growth=1.2, magma=1.0,
        walkers=9, flyers=7, spitters=4, bloats=4, wands=2, blocks=8, boss="herz", final=True,
        extra=(
            ("brandmade", 3), ("augenblase", 3), ("nervenknoten", 3), ("talgsack", 3),
            ("saeuresack", 3), ("gestaltwandler", 2),
        ),
        ambient=0.16,
    ),
)  # fmt: skip


# Alternative biomes per stage of the descent: every run picks one per stage, so a
# run can lead through the stomach or the rumen, the marrow or the spinal cord.
VARIANTS: dict[str, tuple[Depth, ...]] = {
    "schlund": (
        Depth(
            "speiseroehre", "Die Speiseröhre", acid=0.6, growth=0.4, bridges=2.2,
            cavity_scale=0.8, walkers=8, flyers=6, ambient=0.3,
            extra=(("egel", 4), ("talgsack", 2)),
        ),
        Depth(
            "zahnhoehle", "Die Zahnhöhle", wall="knochen", bone_dust=2.0, acid=0.3,
            growth=0.3, walkers=10, flyers=3, spitters=2, ambient=0.32,
            extra=(("egel", 2), ("talgsack", 3)),
        ),
    ),
    "magen": (
        Depth(
            "pansen", "Der Pansen", acid=2.0, growth=2.0, tallow=1.0, mucus=0.5,
            walkers=12, flyers=7, spitters=2, bloats=4, blocks=10, boss="magenwurm",
            ambient=0.25, extra=(("saeurespucker", 3), ("sporensack", 3), ("saeuresack", 2)),
        ),
    ),
    "knochenmark": (
        Depth(
            "rueckenmark", "Das Rückenmark", wall="knochen", bridges=3.5, bone_dust=1.4,
            blood=1.4, walkers=9, flyers=7, spitters=6, bloats=3, blocks=10,
            boss="knochenfresser", ambient=0.26,
            extra=(("nervenknoten", 4), ("egel", 4), ("sporensack", 2)),
        ),
    ),
    "gedaerm": (
        Depth(
            "blinddarm", "Der Blinddarm", pus=2.4, growth=3.2, blood=1.0, bridges=1.0,
            cavity_scale=0.9, walkers=12, flyers=8, spitters=4, bloats=8, blocks=10,
            boss="brutmutter", ambient=0.2,
            extra=(("brandmade", 3), ("egel", 5), ("sporensack", 5)),
        ),
    ),
    "leber": (
        Depth(
            "niere", "Die Niere", acid=2.2, mucus=0.8, pus=0.8, growth=1.0, cavity_scale=1.1,
            walkers=10, flyers=8, spitters=4, bloats=5, blocks=10, ambient=0.23,
            extra=(("saeurespucker", 4), ("schleimkriecher", 2), ("gestaltwandler", 2)),
        ),
        Depth(
            "milz", "Die Milz", blood=3.2, magma=0.4, growth=1.4, walkers=13, flyers=6,
            spitters=4, bloats=4, blocks=10, ambient=0.21,
            extra=(("brandmade", 4), ("egel", 6), ("talgsack", 3), ("gestaltwandler", 1)),
        ),
    ),
    "lunge": (
        Depth(
            "bronchien", "Die Bronchien", mucus=1.6, alveoli=1.6, growth=1.2, bridges=2.4,
            walkers=6, flyers=11, spitters=4, bloats=10, blocks=10, ambient=0.25, boss="atem",
            extra=(("schleimkriecher", 3), ("augenblase", 4), ("sporensack", 5)),
        ),
    ),
}


# A second wave of variants, so the descent has more than thirty different biomes.
MORE_VARIANTS: dict[str, tuple[Depth, ...]] = {
    "schlund": (
        Depth(
            "rachen", "Der Rachen", blood=1.4, growth=0.6, mucus=0.4, cavity_scale=1.2,
            walkers=10, flyers=5, ambient=0.3, extra=(("egel", 3), ("sporensack", 2)),
        ),
        Depth(
            "kehlkopf", "Der Kehlkopf", wall="knochen", bridges=2.6, bone_dust=1.2,
            walkers=8, flyers=6, spitters=1, ambient=0.31, extra=(("egel", 3), ("talgsack", 2)),
        ),
        Depth(
            "zungengrund", "Der Zungengrund", tallow=2.0, growth=0.8, blood=1.2,
            walkers=11, flyers=4, ambient=0.29, extra=(("talgsack", 4), ("egel", 2)),
        ),
    ),
    "magen": (
        Depth(
            "labmagen", "Der Labmagen", acid=3.2, pus=0.6, growth=0.4, walkers=10, flyers=9,
            spitters=3, bloats=2, blocks=10, boss="magenwurm", ambient=0.24,
            extra=(("saeurespucker", 5), ("saeuresack", 4)),
        ),
        Depth(
            "magenpfoertner", "Der Magenpförtner", acid=2.0, tallow=2.0, bridges=2.0,
            cavity_scale=0.9, walkers=12, flyers=6, spitters=4, blocks=10, boss="magenwurm",
            ambient=0.25, extra=(("saeurespucker", 3), ("talgsack", 4), ("egel", 3)),
        ),
    ),
    "knochenmark": (
        Depth(
            "beckenhoehle", "Die Beckenhöhle", wall="knochen", cavity_scale=1.4, blood=1.8,
            tallow=1.4, walkers=12, flyers=6, spitters=5, bloats=3, blocks=10,
            boss="knochenfresser", ambient=0.27, extra=(("saeurespucker", 3), ("talgsack", 4)),
        ),
        Depth(
            "schaedel", "Der Schädel", wall="knochen", bone_dust=3.0, pus=0.6, bridges=1.0,
            walkers=9, flyers=8, spitters=7, bloats=3, blocks=10, boss="knochenfresser",
            ambient=0.25, extra=(("nervenknoten", 3), ("augenblase", 2), ("egel", 3)),
        ),
    ),
    "gedaerm": (
        Depth(
            "duenndarm", "Der Dünndarm", blood=1.2, growth=2.4, bridges=2.8, cavity_scale=0.85,
            walkers=14, flyers=8, spitters=4, bloats=6, blocks=10, boss="brutmutter",
            ambient=0.21, extra=(("brandmade", 3), ("egel", 6), ("talgsack", 3)),
        ),
        Depth(
            "wurmfortsatz", "Der Wurmfortsatz", pus=2.8, growth=2.6, cavity_scale=0.8,
            bridges=0.6, walkers=13, flyers=6, spitters=3, bloats=8, blocks=10,
            boss="brutmutter", ambient=0.18,
            extra=(("schleimkriecher", 2), ("egel", 6), ("gestaltwandler", 1)),
        ),
        Depth(
            "dickdarm", "Der Dickdarm", pus=1.4, tallow=1.6, growth=2.0, cavity_scale=1.25,
            walkers=12, flyers=7, spitters=5, bloats=7, blocks=10, boss="brutmutter",
            ambient=0.19, extra=(("schleimkriecher", 2), ("sporensack", 4), ("saeuresack", 2)),
        ),
    ),
    "leber": (
        Depth(
            "gallenblase_biom", "Die Gallenblase", acid=3.0, mucus=0.6, cavity_scale=1.3,
            walkers=9, flyers=9, spitters=3, bloats=4, blocks=10, ambient=0.24,
            extra=(("saeurespucker", 5), ("saeuresack", 5), ("gestaltwandler", 1)),
        ),
        Depth(
            "bauchspeicheldruese", "Die Bauchspeicheldrüse", acid=1.6, pus=1.6, growth=2.0,
            bridges=1.6, walkers=12, flyers=7, spitters=4, bloats=5, blocks=10, ambient=0.22,
            extra=(("brandmade", 3), ("gestaltwandler", 2), ("sporensack", 3)),
        ),
        Depth(
            "nebenniere", "Die Nebenniere", magma=0.6, tallow=1.8, acid=1.0, walkers=11,
            flyers=8, spitters=5, bloats=4, blocks=10, ambient=0.2,
            extra=(("brandmade", 5), ("talgsack", 4), ("gestaltwandler", 1)),
        ),
        Depth(
            "lymphknoten", "Der Lymphknoten", mucus=1.4, pus=1.2, alveoli=0.6, walkers=10,
            flyers=8, spitters=3, bloats=6, blocks=10, ambient=0.23,
            extra=(("schleimkriecher", 3), ("egel", 5), ("gestaltwandler", 1)),
        ),
    ),
    "lunge": (
        Depth(
            "zwerchfell", "Das Zwerchfell", wall="knochen", mucus=1.0, bridges=3.0,
            cavity_scale=1.3, walkers=7, flyers=10, spitters=5, bloats=8, blocks=10,
            boss="atem", ambient=0.25, extra=(("augenblase", 4), ("nervenknoten", 2)),
        ),
        Depth(
            "luftroehre", "Die Luftröhre", mucus=2.0, alveoli=0.8, bridges=2.0,
            cavity_scale=0.9, walkers=6, flyers=12, spitters=4, bloats=9, blocks=10,
            boss="atem", ambient=0.26, extra=(("schleimkriecher", 3), ("sporensack", 6)),
        ),
    ),
    "herzkammer": (
        Depth(
            "herzvorhof", "Der Herzvorhof", blood=3.0, magma=1.4, growth=1.0, walkers=10,
            flyers=7, spitters=4, bloats=4, wands=2, blocks=8, boss="herz", final=True,
            ambient=0.17,
            extra=(("brandmade", 4), ("augenblase", 3), ("nervenknoten", 3), ("talgsack", 3)),
        ),
    ),
}
for _stage, _extra in MORE_VARIANTS.items():
    VARIANTS[_stage] = VARIANTS.get(_stage, ()) + _extra


def biome_count() -> int:
    return len(DEPTHS) + sum(len(options) for options in VARIANTS.values())


def choose_route(rng) -> tuple[Depth, ...]:
    """One biome per stage: the main one or one of its variants."""
    return tuple(rng.choice((depth, *VARIANTS.get(depth.key, ()))) for depth in DEPTHS)


def depth_by_key(key: str) -> Depth | None:
    for depth in DEPTHS:
        if depth.key == key:
            return depth
    for options in VARIANTS.values():
        for depth in options:
            if depth.key == key:
                return depth
    return None
