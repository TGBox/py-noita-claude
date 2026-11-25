"""Contract V8: Color ramps and universe/entity palettes (Card A21)."""

from __future__ import annotations

from dataclasses import dataclass

OUTLINE_DARK: tuple[int, int, int, int] = (18, 14, 24, 255)


@dataclass(frozen=True)
class PaletteRamp:
    shadow: tuple[int, int, int, int]
    mid: tuple[int, int, int, int]
    light: tuple[int, int, int, int]
    highlight: tuple[int, int, int, int]
    rim: tuple[int, int, int, int]


def make_ramp(base_rgb: tuple[int, int, int]) -> PaletteRamp:
    """Create a 5-stop PaletteRamp from base_rgb with monotonically increasing brightness."""
    # Erstelle eine einfache Farbpalette basierend auf der Basisfarbe
    # Die Werte werden durch Multiplikation mit Faktoren angepasst, um eine monoton steigende Helligkeit zu gewährleisten

    # Schatten (dunkelste Farbe)
    shadow = (max(0, base_rgb[0] - 40), max(0, base_rgb[1] - 40), max(0, base_rgb[2] - 40), 255)

    # Mittlere Farbe
    mid = (max(0, base_rgb[0] - 10), max(0, base_rgb[1] - 10), max(0, base_rgb[2] - 10), 255)

    # Helle Farbe
    light = (
        min(255, base_rgb[0] + 30),
        min(255, base_rgb[1] + 30),
        min(255, base_rgb[2] + 30),
        255,
    )

    # Highlight (hellste Farbe)
    highlight = (
        min(255, base_rgb[0] + 60),
        min(255, base_rgb[1] + 60),
        min(255, base_rgb[2] + 60),
        255,
    )

    # Randfarbe (ähnlich wie Highlight aber etwas dunkler)
    rim = (min(255, base_rgb[0] + 40), min(255, base_rgb[1] + 40), min(255, base_rgb[2] + 40), 255)

    return PaletteRamp(shadow, mid, light, highlight, rim)


# Farbpaletten für die MVP-Universen
UNIVERSE_PALETTES: dict[str, dict[str, PaletteRamp]] = {
    "fleischwelt": {
        "primary": make_ramp((180, 40, 40)),  # Rot für Fleischwelt
        "secondary": make_ramp((120, 20, 20)),  # Dunkleres Rot
        "accent": make_ramp((220, 60, 60)),  # Hellere Rot-Note
        "glow": make_ramp((255, 100, 100)),  # Glühende Rot-Note
    },
    "aktenhalde": {
        "primary": make_ramp((80, 100, 160)),  # Blau für Aktenhalde
        "secondary": make_ramp((40, 60, 120)),  # Dunkleres Blau
        "accent": make_ramp((120, 140, 200)),  # Hellere Blau-Note
        "glow": make_ramp((180, 200, 255)),  # Glühendes Blau
    },
    "glibbria": {
        "primary": make_ramp((160, 140, 100)),  # Braun für Glibbria
        "secondary": make_ramp((120, 100, 60)),  # Dunkleres Braun
        "accent": make_ramp((200, 180, 140)),  # Hellere Braun-Note
        "glow": make_ramp((255, 230, 180)),  # Glühendes Braun
    },
    "kruemelreich": {
        "primary": make_ramp((160, 120, 80)),  # Orange für Krümelreich
        "secondary": make_ramp((120, 80, 40)),  # Dunklere Orange
        "accent": make_ramp((200, 160, 120)),  # Hellere Orange-Note
        "glow": make_ramp((255, 200, 150)),  # Glühende Orange
    },
    "sporenklub": {
        "primary": make_ramp((100, 180, 100)),  # Grün für Sporenklub
        "secondary": make_ramp((60, 140, 60)),  # Dunkleres Grün
        "accent": make_ramp((140, 220, 140)),  # Hellere Grün-Note
        "glow": make_ramp((180, 255, 180)),  # Glühendes Grün
    },
    "abtei": {
        "primary": make_ramp((60, 80, 140)),  # Blau für Abtei
        "secondary": make_ramp((30, 50, 100)),  # Dunkleres Blau
        "accent": make_ramp((100, 120, 180)),  # Hellere Blau-Note
        "glow": make_ramp((140, 160, 220)),  # Glühendes Blau
    },
}

# Farbpaletten für Entitäten
ENTITY_PALETTES: dict[str, dict[str, PaletteRamp]] = {
    "spielerin": {
        "primary": make_ramp((180, 180, 220)),  # Hellblaues für Spielerin
        "secondary": make_ramp((140, 140, 180)),  # Mittelblau
        "accent": make_ramp((220, 220, 255)),  # Hellblau-Note
        "glow": make_ramp((255, 255, 255)),  # Weißes Licht
    },
    "klonita": {
        "primary": make_ramp((180, 220, 180)),  # Hellgrünes für Klonita
        "secondary": make_ramp((140, 180, 140)),  # Mittelgrün
        "accent": make_ramp((220, 255, 220)),  # Hellgrün-Note
        "glow": make_ramp((255, 255, 255)),  # Weißes Licht
    },
    "authority": {
        "primary": make_ramp((180, 180, 180)),  # Graues für Behörde
        "secondary": make_ramp((140, 140, 140)),  # Mittelgrau
        "accent": make_ramp((220, 220, 220)),  # Hellgrau-Note
        "glow": make_ramp((255, 255, 255)),  # Weißes Licht
    },
    "evil_kaiserin": {
        "primary": make_ramp((180, 40, 40)),  # Rot für böse Kaiserin
        "secondary": make_ramp((140, 20, 20)),  # Dunkleres Rot
        "accent": make_ramp((220, 60, 60)),  # Hellere Rot-Note
        "glow": make_ramp((255, 100, 100)),  # Glühende Rot-Note
    },
    "evil_gute": {
        "primary": make_ramp((40, 180, 40)),  # Grün für böse Gute
        "secondary": make_ramp((20, 140, 20)),  # Dunkleres Grün
        "accent": make_ramp((60, 220, 60)),  # Hellere Grün-Note
        "glow": make_ramp((100, 255, 100)),  # Glühendes Grün
    },
    "evil_omega": {
        "primary": make_ramp((180, 180, 40)),  # Gelb für böse Omega
        "secondary": make_ramp((140, 140, 20)),  # Dunkleres Gelb
        "accent": make_ramp((220, 220, 60)),  # Hellere Gelb-Note
        "glow": make_ramp((255, 255, 100)),  # Glühendes Gelb
    },
    "ober_cloita": {
        "primary": make_ramp((180, 180, 220)),  # Hellblaues für Ober-Cloita
        "secondary": make_ramp((140, 140, 180)),  # Mittelblau
        "accent": make_ramp((220, 220, 255)),  # Hellblau-Note
        "glow": make_ramp((255, 255, 255)),  # Weißes Licht
    },
}
