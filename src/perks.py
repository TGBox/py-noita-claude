"""Perks: permanent mutations for the rest of a run, chosen at the sanctum altar."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Perk:
    key: str
    name_de: str
    description_de: str
    color: tuple[int, int, int]


PERKS: tuple[Perk, ...] = (
    Perk("feuerfest", "Feuerfeste Haut", "Feuer kann dir nichts mehr anhaben.", (255, 150, 40)),
    Perk("saeurehaut", "Säurehaut", "Magensäure und Ätzdampf verletzen dich nicht.", (140, 196, 40)),
    Perk("zaehes_fleisch", "Zähes Fleisch", "+50 maximale Lebenspunkte.", (176, 34, 48)),
    Perk("leichte_knochen", "Leichte Knochen", "Du schwebst 50 % länger.", (226, 214, 184)),
    Perk("panzerplatten", "Panzerplatten", "Explosionen verletzen dich kaum noch.", (120, 110, 104)),
    Perk("blutdurst", "Blutdurst", "Jeder getötete Gegner heilt dich um 6.", (200, 20, 40)),
    Perk("schnelle_druesen", "Schnelle Drüsen", "Augmentationen zaubern und laden 25 % schneller.", (150, 84, 172)),
    Perk("saeureblut", "Säureblut", "Wenn du verletzt wirst, spritzt ätzendes Blut um dich.", (110, 170, 40)),
    Perk("zweiter_puls", "Zweiter Puls", "Einmal pro Lauf stehst du nach dem Tod wieder auf.", (232, 196, 70)),
    Perk("flinke_haende", "Flinke Hände", "Du kannst Augmentationen überall umbauen, nicht nur im Sanktum.", (214, 190, 170)),
    Perk("wutdruesen", "Wutdrüsen", "Deine Geschosse richten 30 % mehr Schaden an.", (220, 60, 40)),
    Perk("perlenmagnet", "Perlenmagnet", "Blutperlen fliegen dir aus großer Entfernung zu.", (190, 20, 36)),
    Perk("dauerflug", "Ausdauernde Flughäute", "Deine Schwebekraft lädt sich auch in der Luft schnell auf.", (170, 200, 220)),
    Perk("gaslunge", "Gaslunge", "Sporen und Ätzdampf schaden dir nicht.", (164, 128, 160)),
    Perk("schleimlaeufer", "Schleimläufer", "Schleim bremst dich nicht mehr.", (176, 172, 120)),
    Perk("blutsauger", "Blutsauger", "Blut aus der Phiole heilt dich (6 pro Schluck).", (150, 12, 24)),
    Perk("feilscher", "Feilscher", "Im Laden zahlst du ein Drittel weniger.", (232, 180, 90)),
)  # fmt: skip

PERK_BY_KEY: dict[str, Perk] = {perk.key: perk for perk in PERKS}
