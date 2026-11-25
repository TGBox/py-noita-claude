"""Contract V20: the 7 Physik-o-Mat puzzles (Cards E07, E08)."""

from __future__ import annotations

import math
import random
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from src import materials as mat
from src.economy import PHYSIK_STAKE
from src.reactions import Reaction
from src.samples import SAMPLES
from src.world import BORDER

from . import NEXT_BOOST_KEYS, Minigame, MinigameResult

PUZZLE_KEYS: tuple[str, ...] = (
    "glas_fuellen",
    "vase_retten",
    "kerze_zuenden",
    "ameisenstrasse",
    "lava_water",
    "acid_gold",
    "oil_fire",
)
EXPANSION_PUZZLE_KEYS: tuple[str, ...] = ("electricity_water",)
ALL_PUZZLE_KEYS: tuple[str, ...] = (*PUZZLE_KEYS, *EXPANSION_PUZZLE_KEYS)

PHYSIK_SET = mat.MaterialSet(
    "physik_o_mat",
    (
        *mat.BASE_KEYS,
        "magma",
        "acid",
        "enamel",
        "papier",
        "zucker",
        "goldboden",
        "kerzenwachs",
    ),
    reactions=(
        Reaction("magma", "water", "rock", "steam", 0.5),
        Reaction("acid", "dirt", "smoke", "air", 0.15),
        Reaction("fire", "oil", "fire", "fire", 0.35),
        Reaction("fire", "kerzenwachs", "fire", "fire", 0.3),
    ),
)


@contextmanager
def _physik_materials() -> Iterator[None]:
    """Temporarily activate PHYSIK_SET without leaking ids into the running game."""
    prev = mat.ACTIVE
    mat.activate(PHYSIK_SET)
    try:
        yield
    finally:
        if prev is not None:
            mat.activate(prev)


class PhysikPuzzle(Minigame):
    def __init__(self, key: str, seed: int = 0) -> None:
        self.key = key
        self.stake = PHYSIK_STAKE
        self.time_limit = 20.0
        self.rng = random.Random(seed)
        self.custom_state: dict[str, Any] = {}
        self.goal_de: str = ""
        self.allowed_tools: tuple[str, ...] = ("blast", "dig", "ignite", "pour")
        self.tool_charges: dict[str, int] = {}
        self.blocked_zones: list[tuple[int, int, int, int]] = []
        self.zone_labels: list[tuple[str, int, int]] = []
        self.feedback_de: str = ""
        self.feedback_timer: float = 0.0
        self.palette: list[tuple[int, int, int]] = []
        self.mat_ids: dict[str, int] = {}

        with _physik_materials():
            super().__init__(seed=seed)
            self._setup_puzzle()
            self.palette = [m.color for m in mat.MATERIALS]
            self.mat_ids = dict(mat.MAT_ID)

    def make_win_result(self) -> MinigameResult:
        roll = self.rng.random()
        if roll < 0.333:
            gold = self.stake * 2
            return MinigameResult(
                completed=True, won=True, reward_gold=gold, message_de=f"Rätsel gelöst! +{gold} Gold"
            )
        if roll < 0.666:
            u_samples = sorted(k for k, s in SAMPLES.items() if s.universe_key != "allgemein")
            chosen_sample = self.rng.choice(u_samples)
            return MinigameResult(
                completed=True,
                won=True,
                reward_sample=chosen_sample,
                message_de="Rätsel gelöst! 1x Universums-Probe",
            )
        boost = self.rng.choice(NEXT_BOOST_KEYS)
        return MinigameResult(
            completed=True, won=True, next_boost=boost, message_de=f"Rätsel gelöst! Schub: {boost}"
        )

    def _in_blocked_zone(self, cx: int, cy: int) -> bool:
        return any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1 in self.blocked_zones)

    def _set_feedback(self, text: str) -> None:
        self.feedback_de = text
        self.feedback_timer = 1.6

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        if action == "wait":
            return
        if action not in self.allowed_tools:
            self._set_feedback("Dieses Werkzeug ist hier gesperrt.")
            return
        if self.tool_charges.get(action, 0) <= 0:
            self._set_feedback("Keine Ladungen mehr!")
            return
        cx, cy = int(cursor[0]), int(cursor[1])
        if self._in_blocked_zone(cx, cy):
            self._set_feedback("Sperrzone! Hier nicht erlaubt.")
            return
        if self.key == "oil_fire" and action == "ignite" and cx >= 56:
            self._set_feedback("Nur links am ersten Docht zünden!")
            return

        self.tool_charges[action] -= 1
        with _physik_materials():
            if action == "blast":
                self.world.explode(cx, cy, 8)
                if self.key == "vase_retten":
                    vx, vy = self.custom_state["vase_pos"]
                    if math.hypot(cx - vx, cy - vy) <= 18.0:
                        self.custom_state["vase_alive"] = False
                        self.finished = True
                        self.result = MinigameResult(
                            completed=True, won=False, message_de="Die Vase ist zerbrochen!"
                        )
            elif action == "dig":
                self.world.dig(cx, cy, 4, force=False)
            elif action == "ignite":
                self.world.splash(cx, cy, 3, mat.FIRE)
            elif action == "pour":
                pour_mat = self.custom_state.get("pour_mat", mat.MAT_ID["water"])
                pour_r = self.custom_state.get("pour_radius", 3)
                self.world.splash(cx, cy, pour_r, pour_mat)

    def _setup_puzzle(self) -> None:
        w = self.world
        w.reset()
        water = mat.MAT_ID["water"]
        dirt = mat.MAT_ID["dirt"]
        rock = mat.MAT_ID["rock"]
        enamel = mat.MAT_ID["enamel"]
        bedrock = mat.BEDROCK
        papier = mat.MAT_ID["papier"]
        wax = mat.MAT_ID["kerzenwachs"]
        sugar = mat.MAT_ID["zucker"]
        magma = mat.MAT_ID["magma"]
        acid = mat.MAT_ID["acid"]
        gold = mat.MAT_ID["goldboden"]
        oil = mat.MAT_ID["oil"]

        if self.key == "glas_fuellen":
            self.title_de = "Füll das Glas"
            self.goal_de = "Leite das Wasser ins Glas – nicht in den Abfluss!"
            self.allowed_tools = ("dig", "blast")
            self.tool_charges = {"dig": 6, "blast": 2}
            # Top water basin held by dirt floor
            w.fill_rect(22, 8, 25, 32, bedrock)
            w.fill_rect(73, 8, 76, 32, bedrock)
            w.fill_rect(22, 8, 76, 10, bedrock)
            w.fill_rect(25, 11, 73, 27, water)
            w.fill_rect(25, 27, 73, 31, dirt)
            # Sloped dirt chute leading right into an open drain unless opened directly over glass
            for dx in range(25, 118):
                ramp_y = 42 + (dx - 25) // 4
                w.fill_rect(dx, ramp_y, dx + 1, ramp_y + 3, dirt)
            # Drain walls on far right
            w.fill_rect(120, 62, 123, 118, bedrock)
            # Enamel glass in the center-left
            w.fill_rect(48, 82, 51, 112, enamel)
            w.fill_rect(83, 82, 86, 112, enamel)
            w.fill_rect(48, 110, 86, 113, enamel)
            self.blocked_zones = [(46, 80, 88, 115)]
            self.zone_labels = [("Glas", 67, 75), ("Abfluss", 136, 104)]

        elif self.key == "vase_retten":
            self.title_de = "Rette die Vase"
            self.goal_de = "Sprenge den Felsturm, ohne die Vase zu zerbrechen!"
            self.allowed_tools = ("blast", "dig")
            self.tool_charges = {"blast": 4, "dig": 5}
            w.fill_rect(16, 100, 144, 106, bedrock)
            # Rock tower on the left
            w.fill_rect(55, 56, 64, 100, rock)
            self.custom_state["initial_rock"] = w.count(rock)
            # Delicate enamel vase on pedestal on the right
            w.fill_rect(104, 96, 118, 100, bedrock)
            w.fill_rect(107, 84, 115, 96, enamel)
            w.fill_rect(109, 86, 113, 94, mat.AIR)
            w.fill_rect(108, 81, 114, 84, enamel)
            self.custom_state["initial_vase"] = w.count(enamel)
            self.custom_state["vase_pos"] = (111, 89)
            self.custom_state["vase_alive"] = True
            self.blocked_zones = [(98, 76, 124, 102)]
            self.zone_labels = [("Turm", 59, 44), ("Vase", 111, 72)]

        elif self.key == "kerze_zuenden":
            self.title_de = "Zünde die Kerze"
            self.goal_de = "Leite das Wasser links um, dann zünde die Schnur an!"
            self.allowed_tools = ("dig", "ignite")
            self.tool_charges = {"dig": 6, "ignite": 2}
            # Bedrock ceiling/protection around the candle chamber on the right
            w.fill_rect(116, 54, 144, 57, bedrock)
            w.fill_rect(141, 54, 144, 92, bedrock)
            w.fill_rect(116, 89, 144, 92, bedrock)
            w.fill_rect(116, 54, 119, 71, bedrock)
            w.fill_rect(116, 78, 119, 92, bedrock)
            # Candle inside protected chamber
            w.fill_rect(126, 66, 134, 88, wax)
            # Continuous thick paper fuse from x=60 to x=126
            w.fill_rect(60, 72, 126, 77, papier)
            w.fill_rect(60, 77, 116, 80, bedrock)
            # Upper water basin on the left pouring down a dirt aqueduct onto the fuse at x=75
            w.fill_rect(16, 12, 19, 34, bedrock)
            w.fill_rect(16, 12, 42, 15, bedrock)
            w.fill_rect(19, 15, 42, 32, water)
            w.fill_rect(19, 32, 42, 35, bedrock)
            for dx in range(42, 74):
                cy = 32 + (dx - 42) * 20 // 32
                w.fill_rect(dx, cy, dx + 1, cy + 4, dirt)
                w.fill_rect(dx, cy - 8, dx + 1, cy, water if dx < 60 else mat.AIR)
            self.blocked_zones = [(114, 52, 146, 94)]
            self.zone_labels = [("Zündpunkt", 64, 62), ("Kerze", 130, 48)]

        elif self.key == "ameisenstrasse":
            self.title_de = "Ameisenstraße"
            self.goal_de = "Schütte eine Zuckerspur als Brücke bis zum Ameisennest!"
            self.allowed_tools = ("pour",)
            self.tool_charges = {"pour": 24}
            self.custom_state["pour_mat"] = sugar
            self.custom_state["pour_radius"] = 5
            # Left plateau & right plateau with a pit in between
            w.fill_rect(4, 88, 52, 118, bedrock)
            w.fill_rect(108, 88, 156, 118, bedrock)
            w.fill_rect(52, 108, 108, 118, bedrock)
            # Small sugar mound at nest
            w.fill_rect(126, 83, 136, 88, sugar)
            self.custom_state["ants"] = [[16.0, 86.0], [22.0, 86.0], [28.0, 86.0], [34.0, 86.0], [40.0, 86.0]]
            self.zone_labels = [("Nest", 131, 74)]

        elif self.key == "lava_water":
            self.title_de = "Lava-Brücke"
            self.goal_de = "Lass Wasser auf die Lava fließen, um eine Steinbrücke zu bauen!"
            self.allowed_tools = ("dig", "blast")
            self.tool_charges = {"dig": 6, "blast": 2}
            # Lower magma basin
            w.fill_rect(34, 82, 37, 108, bedrock)
            w.fill_rect(123, 82, 126, 108, bedrock)
            w.fill_rect(34, 106, 126, 109, bedrock)
            w.fill_rect(37, 84, 123, 106, magma)
            # Upper water reservoir held by dirt floor
            w.fill_rect(44, 14, 47, 46, bedrock)
            w.fill_rect(113, 14, 116, 46, bedrock)
            w.fill_rect(44, 14, 116, 17, bedrock)
            w.fill_rect(47, 17, 113, 41, water)
            w.fill_rect(47, 41, 113, 46, dirt)
            self.blocked_zones = [(32, 78, 128, 110)]
            self.zone_labels = [("Lava", 80, 96)]

        elif self.key == "acid_gold":
            self.title_de = "Säure-Tresor"
            self.goal_de = "Öffne das Säurebecken – die Säure ätzt den Tresordeckel auf!"
            self.allowed_tools = ("dig", "blast")
            self.tool_charges = {"dig": 5, "blast": 2}
            # Protected vault with dirt lid over gold
            w.fill_rect(70, 74, 74, 108, bedrock)
            w.fill_rect(98, 74, 102, 108, bedrock)
            w.fill_rect(70, 104, 102, 108, bedrock)
            w.fill_rect(74, 84, 98, 104, gold)
            w.fill_rect(74, 74, 98, 82, dirt)
            self.custom_state["initial_lid"] = 24 * 8
            # Upper acid tank behind acid-proof enamel with a breakable rock plug
            w.fill_rect(68, 14, 71, 45, enamel)
            w.fill_rect(101, 14, 104, 45, enamel)
            w.fill_rect(68, 14, 104, 17, enamel)
            w.fill_rect(71, 39, 80, 44, enamel)
            w.fill_rect(92, 39, 101, 44, enamel)
            w.fill_rect(80, 39, 92, 44, rock)
            w.fill_rect(71, 17, 101, 39, acid)
            self.blocked_zones = [(66, 68, 106, 112)]
            self.zone_labels = [("Tresor", 86, 94)]

        elif self.key == "oil_fire":
            self.title_de = "Docht-Kette"
            self.goal_de = "Verbinde alle drei Dochte mit Öl und zünde links einmal an!"
            self.allowed_tools = ("pour", "ignite")
            self.tool_charges = {"pour": 24, "ignite": 1}
            self.custom_state["pour_mat"] = oil
            self.custom_state["pour_radius"] = 4
            self.custom_state["lit_wicks"] = set()
            # Shallow bedrock trough containing 3 wax wicks
            w.fill_rect(22, 90, 138, 96, bedrock)
            w.fill_rect(22, 82, 25, 90, bedrock)
            w.fill_rect(135, 82, 138, 90, bedrock)
            for wx in (34, 78, 122):
                w.fill_rect(wx, 78, wx + 4, 90, wax)
            self.blocked_zones = []
            self.zone_labels = [("1", 36, 71), ("2", 80, 71), ("3", 124, 71)]

        elif self.key == "electricity_water":
            self.title_de = "Stromkreis"
            self.goal_de = "Schließe die Wasserbrücke zwischen beiden Elektroden!"
            self.allowed_tools = ("pour",)
            self.tool_charges = {"pour": 24}
            self.custom_state["pour_mat"] = water
            self.custom_state["pour_radius"] = 5
            # Left copper-style electrode + right sensor electrode separated by a dry basin
            w.fill_rect(26, 86, 134, 92, enamel)
            w.fill_rect(26, 72, 30, 86, bedrock)
            w.fill_rect(130, 72, 134, 86, bedrock)
            w.fill_rect(30, 76, 46, 86, gold)
            w.fill_rect(114, 76, 130, 86, gold)
            self.blocked_zones = []
            self.zone_labels = [("Pol +", 38, 66), ("Pol -", 122, 66)]

        w.wake_all()

    def _tick_ants(self, dt: float) -> None:
        w = self.world
        sugar = self.mat_ids["zucker"]
        ants: list[list[float]] = self.custom_state["ants"]
        for ant in ants:
            ax, ay = ant[0], ant[1]
            ix, iy = int(ax), int(ay)
            # Gravity
            if iy + 1 < w.height - BORDER and w.get(ix, iy + 1) == mat.AIR:
                ant[1] = min(float(w.height - BORDER - 1), ay + 32.0 * dt)
                continue
            # Ants need sugar ahead once they approach the pit edge
            has_sugar_ahead = False
            for sx in range(max(BORDER, ix + 1), min(w.width - BORDER, ix + 18)):
                for sy in range(max(BORDER, iy - 8), min(w.height - BORDER, iy + 10)):
                    if w.get(sx, sy) == sugar:
                        has_sugar_ahead = True
                        break
                if has_sugar_ahead:
                    break
            if ax >= 46.0 and not has_sugar_ahead:
                continue
            nx = int(ax + 1)
            if nx >= w.width - BORDER - 2:
                continue
            # Check step-up (up to 4 px) or drop (up to 3 px)
            moved = False
            for dy in (0, -1, -2, -3, -4, 1, 2, 3):
                ty = iy + dy
                if BORDER <= ty < w.height - BORDER - 1 and w.get(nx, ty) == mat.AIR:
                    below = w.get(nx, ty + 1)
                    if below != mat.AIR:
                        ant[0] = min(134.0, ax + 28.0 * dt)
                        ant[1] = float(ty)
                        moved = True
                        break
            if not moved and has_sugar_ahead and w.get(nx, iy) == mat.AIR:
                # Step into shallow depression filled with sugar nearby
                ant[0] = min(134.0, ax + 22.0 * dt)

    def tick(self, dt: float) -> None:
        if self.feedback_timer > 0.0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
            if self.feedback_timer == 0.0:
                self.feedback_de = ""

        if self.key == "ameisenstrasse":
            self._tick_ants(dt)
        elif self.key == "vase_retten" and self.custom_state.get("vase_alive", True):
            init_vase = max(1, self.custom_state.get("initial_vase", 1))
            curr_vase = self.world.count(self.mat_ids["enamel"])
            if curr_vase < init_vase * 0.85:
                self.custom_state["vase_alive"] = False
                self.finished = True
                self.result = MinigameResult(
                    completed=True, won=False, message_de="Die Vase ist zerbrochen!"
                )
        elif self.key == "oil_fire":
            w = self.world
            wax = self.mat_ids["kerzenwachs"]
            fire = self.mat_ids["fire"]
            lit: set[int] = self.custom_state["lit_wicks"]
            for idx, wx in enumerate((34, 78, 122)):
                if idx in lit:
                    continue
                for y in range(74, 91):
                    for x in range(wx - 2, wx + 6):
                        c = w.get(x, y)
                        if c == fire or (c == wax and w.life[y * w.width + x] > 0):
                            lit.add(idx)
                            break
                    if idx in lit:
                        break

    def check_win(self) -> bool:
        w = self.world
        if self.key == "glas_fuellen":
            water = self.mat_ids["water"]
            water_count = sum(
                1 for y in range(84, 110) for x in range(52, 83) if w.get(x, y) == water
            )
            return water_count >= 50

        if self.key == "vase_retten":
            init_rock = max(1, self.custom_state.get("initial_rock", 1))
            curr_rock = w.count(self.mat_ids["rock"])
            return bool(self.custom_state.get("vase_alive", True)) and curr_rock <= init_rock * 0.25

        if self.key == "kerze_zuenden":
            wax = self.mat_ids["kerzenwachs"]
            fire = self.mat_ids["fire"]
            for y in range(62, 89):
                for x in range(124, 136):
                    c = w.get(x, y)
                    if c == fire or (c == wax and w.life[y * w.width + x] > 0):
                        return True
            return False

        if self.key == "ameisenstrasse":
            ants = self.custom_state.get("ants", [])
            return sum(1 for ax, ay in ants if ax >= 112.0 and ay <= 90.0) >= 3

        if self.key == "lava_water":
            rock = self.mat_ids["rock"]
            solid_bridge = sum(
                1 for y in range(74, 108) for x in range(36, 124) if w.get(x, y) == rock
            )
            return solid_bridge >= 35

        if self.key == "acid_gold":
            dirt = self.mat_ids["dirt"]
            remaining = sum(
                1 for y in range(74, 82) for x in range(74, 98) if w.get(x, y) == dirt
            )
            init_lid = max(1, self.custom_state.get("initial_lid", 192))
            return remaining <= init_lid * 0.40

        if self.key == "oil_fire":
            return len(self.custom_state.get("lit_wicks", set())) >= 3

        if self.key == "electricity_water":
            water = self.mat_ids["water"]
            bridged_cols = sum(
                1
                for x in range(46, 114)
                if any(w.get(x, y) == water for y in range(74, 86))
            )
            return bridged_cols >= 58

        return False


def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame:
    """Create a Physik-o-Mat puzzle."""
    if puzzle_key is None:
        rng = random.Random(seed)
        puzzle_key = rng.choice(PUZZLE_KEYS)
    return PhysikPuzzle(puzzle_key, seed=seed)


def solve_actions(puzzle_key: str) -> list[tuple[str, tuple[int, int]]]:
    """Valid non-cheating solution (action, cursor) for tests and verification."""
    if puzzle_key == "glas_fuellen":
        return [("dig", (58, 29)), ("dig", (64, 29)), ("dig", (60, 52)), ("dig", (66, 54))]
    if puzzle_key == "vase_retten":
        return [
            ("blast", (59, 62)),
            ("blast", (59, 73)),
            ("blast", (59, 84)),
            ("blast", (59, 95)),
        ]
    if puzzle_key == "kerze_zuenden":
        return [
            ("dig", (47, 36)),
            ("dig", (51, 39)),
            ("wait", (0, 0)),
            ("wait", (0, 0)),
            ("wait", (0, 0)),
            ("ignite", (63, 74)),
        ]
    if puzzle_key == "ameisenstrasse":
        actions: list[tuple[str, tuple[int, int]]] = []
        for x in range(52, 110, 5):
            actions.append(("pour", (x, 98)))
            actions.append(("pour", (x, 90)))
        return actions
    if puzzle_key == "lava_water":
        return [("blast", (80, 43)), ("dig", (72, 43))]
    if puzzle_key == "acid_gold":
        return [("blast", (86, 41)), ("dig", (86, 41))]
    if puzzle_key == "oil_fire":
        actions = [("pour", (x, 86)) for x in range(39, 124, 5)]
        actions.append(("ignite", (36, 86)))
        return actions
    if puzzle_key == "electricity_water":
        actions = [("pour", (x, 82)) for x in range(48, 114, 4)]
        actions.extend([("pour", (x, 82)) for x in range(50, 112, 6)])
        return actions
    return []
