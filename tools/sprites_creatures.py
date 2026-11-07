"""Contract V8: Regular creature sprite builders across all 9 universes (Cards B06..B14)."""

from __future__ import annotations

from pathlib import Path

from src.sprite_render import ASSET_ROOT
from src.universes.catalog import ALL_UNIVERSES
from tools.palette import UNIVERSE_PALETTES
from tools.sprites import (
    PixelCanvas,
    apply_dark_outline,
    draw_shaded_ellipse,
    draw_shaded_rect,
    save_sheet,
)


def _draw_creature_frame(
    species: str,
    u_key: str,
    offset_y: int = 0,
    action: bool = False,
) -> PixelCanvas:
    pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["sporenklub"])
    
    # Custom sizes & shapes per species if needed, standard default 20x20
    w, h = 20, 20
    if species in ("fleischmade", "blutegel", "blattlaus"):
        w, h = 18, 14
    elif species in ("zottenwurm", "aktenwolf", "pfuetzenwurm"):
        w, h = 24, 20
    elif species in ("kaffeegolem", "korallenwaechter", "tuersteherpilz"):
        w, h = 22, 24
    elif species in ("leuchtmotte", "glockenqualle", "zuckerwatte_wolke"):
        w, h = 20, 20

    c = PixelCanvas(w, h)
    
    # Body
    body_x1 = 3
    body_y1 = 4 + offset_y
    body_x2 = w - 4
    body_y2 = h - 4 + offset_y
    draw_shaded_rect(c, body_x1, body_y1, body_x2, body_y2, pal["primary"])
    
    # Head / Feature ellipse
    cx = w // 2
    cy = max(4, h // 2 - 2 + offset_y)
    draw_shaded_ellipse(c, cx, cy, min(cx - 2, 5), min(cy - 2, 4), pal["secondary"])
    
    # Accent markings / eyes / features
    draw_shaded_rect(c, cx - 3, cy, cx + 3, cy + 2, pal["accent"])
    
    # Glow / weapon / action detail
    if action:
        draw_shaded_rect(c, cx - 2, body_y2 - 3, cx + 2, body_y2, pal["glow"])
        c.set_px(cx, body_y2 - 1, (255, 255, 255, 255))
    else:
        c.set_px(cx, cy, pal["glow"].highlight)

    apply_dark_outline(c)
    return c


def build_creature_sheets(
    out_dir: Path = ASSET_ROOT,
    universe_key: str | None = None,
) -> list[Path]:
    """Build kreaturen/<species>.{png,json} for universe_key (or all universes if None)."""
    targets = [universe_key] if universe_key else list(ALL_UNIVERSES.keys())
    paths: list[Path] = []

    for u_key in targets:
        if u_key not in ALL_UNIVERSES:
            continue
        u = ALL_UNIVERSES[u_key]
        pal = UNIVERSE_PALETTES.get(u_key, UNIVERSE_PALETTES["sporenklub"])
        
        for spawn in u.creatures:
            species = spawn.species
            
            idle_frames = [_draw_creature_frame(species, u_key, y) for y in (0, 1, 0, -1)]
            walk_frames = [_draw_creature_frame(species, u_key, y) for y in (0, -1, 0, 1)]
            windup_frames = [_draw_creature_frame(species, u_key, -1, True), _draw_creature_frame(species, u_key, 0, True)]
            attack_frames = [_draw_creature_frame(species, u_key, 1, True), _draw_creature_frame(species, u_key, 0, False)]
            hurt_frames = [_draw_creature_frame(species, u_key, 1), _draw_creature_frame(species, u_key, 0)]
            
            anims = {
                "idle": idle_frames,
                "walk": walk_frames,
                "windup": windup_frames,
                "attack": attack_frames,
                "hurt": hurt_frames,
            }

            # Optional/universe-specific states
            if species == "blutegel":
                anims["hang"] = [_draw_creature_frame(species, u_key, -1)]
                anims["latched"] = [_draw_creature_frame(species, u_key, 0, True)]
            elif species == "fleischmade":
                anims["burrow_out"] = [_draw_creature_frame(species, u_key, 2), _draw_creature_frame(species, u_key, 0)]
            elif species == "aktenfresser":
                anims["dig"] = [_draw_creature_frame(species, u_key, 1, True), _draw_creature_frame(species, u_key, 2, True)]
            elif species == "stempler":
                anims["stamp"] = [_draw_creature_frame(species, u_key, -2, True), _draw_creature_frame(species, u_key, 2, True)]
            elif species == "orgelaal":
                anims["swim"] = [_draw_creature_frame(species, u_key, y) for y in (-1, 0, 1, 0)]
            elif species == "harzspucker":
                anims["shoot"] = [_draw_creature_frame(species, u_key, 0, True), _draw_creature_frame(species, u_key, 1, True)]
            elif species == "huepfling":
                anims["squash"] = [_draw_creature_frame(species, u_key, 2), _draw_creature_frame(species, u_key, -2)]
            elif species == "glibberteiler":
                anims["split"] = [_draw_creature_frame(species, u_key, 0, True), _draw_creature_frame(species, u_key, 1, True)]

            first = idle_frames[0]
            anchor = (first.width // 2, first.height - 2)

            glow = []
            if species in ("leuchtmotte", "sporenwerfer", "harzspucker", "glockenqualle"):
                glow = [{"offset": [first.width // 2, first.height // 2], "color": list(pal["glow"].highlight[:3]), "radius": 12}]

            p, j = save_sheet(
                "kreaturen",
                species,
                anims,
                anchor=anchor,
                fps={"idle": 4.0, "walk": 6.0, "windup": 6.0, "attack": 8.0, "hurt": 8.0},
                glow=glow,
                out_dir=out_dir,
            )
            paths.extend([p, j])

    return paths


