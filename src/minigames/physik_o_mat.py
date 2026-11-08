"""Contract V20: the 7 Physik-o-Mat puzzles (Cards E07, E08)."""

from __future__ import annotations

import random
from typing import Any

from src import materials as mat
from src.economy import PHYSIK_STAKE
from src.samples import SAMPLES

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


class PhysikPuzzle(Minigame):
    def __init__(self, key: str, seed: int = 0) -> None:
        super().__init__(seed=seed)
        self.key = key
        self.stake = PHYSIK_STAKE
        self.time_limit = 15.0
        self.rng = random.Random(seed)
        self.custom_state: dict[str, Any] = {}
        self._setup_puzzle()

    def make_win_result(self) -> MinigameResult:
        roll = self.rng.random()
        if roll < 0.333:
            gold = self.stake * 2
            return MinigameResult(
                completed=True,
                won=True,
                reward_gold=gold,
                message_de=f"Rätsel gelöst! +{gold} Gold",
            )
        elif roll < 0.666:
            u_samples = sorted([k for k, s in SAMPLES.items() if s.universe_key != "allgemein"])
            chosen_sample = self.rng.choice(u_samples)
            return MinigameResult(
                completed=True,
                won=True,
                reward_sample=chosen_sample,
                message_de="Rätsel gelöst! 1x Universums-Probe",
            )
        else:
            boost = self.rng.choice(NEXT_BOOST_KEYS)
            return MinigameResult(
                completed=True,
                won=True,
                next_boost=boost,
                message_de=f"Rätsel gelöst! Schub: {boost}",
            )

    def on_action(self, action: str, cursor: tuple[int, int]) -> None:
        cx, cy = cursor
        if action == "blast":
            self.world.explode(cx, cy, 6)
        elif action == "dig":
            self.world.dig(cx, cy, 3, force=True)
        elif action == "ignite":
            self.world.ignite(cx, cy)
        elif action == "pour":
            pour_mat = self.custom_state.get("pour_mat", mat.MAT_ID["water"])
            self.world.fill_disc(cx, cy, 2, pour_mat)

    def _setup_puzzle(self) -> None:
        w = self.world
        w.reset()

        if self.key == "glas_fuellen":
            self.title_de = "Füll das Glas"
            # Water basin at top
            w.fill_rect(20, 10, 60, 25, mat.MAT_ID["water"])
            w.fill_rect(18, 9, 62, 10, mat.MAT_ID["stone"])
            w.fill_rect(18, 10, 20, 28, mat.MAT_ID["stone"])
            w.fill_rect(60, 10, 62, 28, mat.MAT_ID["stone"])
            w.fill_rect(20, 26, 60, 28, mat.MAT_ID["dirt"])  # breakable plug

            # Glass of enamel at bottom (40, 80 to 80, 110)
            w.fill_rect(35, 80, 38, 110, mat.MAT_ID["enamel"])  # left wall
            w.fill_rect(72, 80, 75, 110, mat.MAT_ID["enamel"])  # right wall
            w.fill_rect(35, 108, 75, 110, mat.MAT_ID["enamel"])  # bottom

        elif self.key == "vase_retten":
            self.title_de = "Rette die Vase"
            # Tower of rock
            w.fill_rect(78, 88, 82, 104, mat.MAT_ID["rock"])
            self.custom_state["initial_rock"] = w.count(mat.MAT_ID["rock"])
            self.custom_state["vase_pos"] = (120, 100)
            self.custom_state["vase_alive"] = True
            w.fill_rect(118, 98, 122, 102, mat.MAT_ID["enamel"])

        elif self.key == "kerze_zuenden":
            self.title_de = "Zünde die Kerze"
            # Tallow candle at (120, 80 to 125, 95)
            w.fill_rect(120, 80, 125, 95, mat.MAT_ID["tallow"])
            # Paper line
            w.fill_rect(40, 85, 119, 87, mat.MAT_ID["papier"])

        elif self.key == "ameisenstrasse":
            self.title_de = "Ameisenstraße"
            # Sugar target at (130, 90 to 140, 95)
            w.fill_rect(130, 90, 140, 95, mat.MAT_ID["zucker"])
            self.custom_state["ants"] = [10.0, 15.0, 20.0, 25.0, 30.0]  # x positions
            self.custom_state["ants_y"] = 90.0

        elif self.key == "lava_water":
            self.title_de = "Lava-Brücke"
            # Magma basin
            w.fill_rect(50, 80, 100, 100, mat.MAT_ID["magma"])
            # Water above behind a dirt barrier
            w.fill_rect(60, 30, 90, 50, mat.MAT_ID["water"])
            w.fill_rect(58, 51, 92, 55, mat.MAT_ID["dirt"])

        elif self.key == "acid_gold":
            self.title_de = "Säure-Tresor"
            # Dirt chamber holding gold
            w.fill_rect(90, 70, 110, 90, mat.MAT_ID["dirt"])
            w.fill_rect(95, 75, 105, 85, mat.MAT_ID["gold_vein"])
            # Acid above behind dirt plug
            w.fill_rect(90, 30, 110, 50, mat.MAT_ID["acid"])
            w.fill_rect(88, 51, 112, 54, mat.MAT_ID["dirt"])

        elif self.key == "oil_fire":
            self.title_de = "Docht-Kette"
            # 3 tallow wicks
            w.fill_rect(40, 80, 45, 90, mat.MAT_ID["tallow"])
            w.fill_rect(80, 80, 85, 90, mat.MAT_ID["tallow"])
            w.fill_rect(120, 80, 125, 90, mat.MAT_ID["tallow"])
            self.custom_state["pour_mat"] = mat.MAT_ID["oil"]

    def tick(self, dt: float) -> None:
        if self.key == "ameisenstrasse":
            # Move ants towards sugar
            ants = self.custom_state["ants"]
            for i in range(len(ants)):
                ants[i] = min(135.0, ants[i] + 100.0 * dt)

    def check_win(self) -> bool:
        w = self.world
        if self.key == "glas_fuellen":
            # Check water inside glass (39 to 71, y=81 to 107)
            water_count = 0
            water_id = mat.MAT_ID["water"]
            for y in range(81, 108):
                for x in range(39, 72):
                    if w.get(x, y) == water_id:
                        water_count += 1
            return water_count >= 40

        elif self.key == "vase_retten":
            init_rock = self.custom_state.get("initial_rock", 1)
            curr_rock = w.count(mat.MAT_ID["rock"])
            vase_alive = self.custom_state.get("vase_alive", True)
            return vase_alive and curr_rock <= init_rock * 0.20

        elif self.key == "kerze_zuenden":
            tallow_id = mat.MAT_ID["tallow"]
            fire_id = mat.FIRE
            # Check if any candle cell is burning (turned into FIRE or tallow with life > 0)
            for y in range(80, 96):
                for x in range(120, 126):
                    c = w.get(x, y)
                    if c == fire_id or (c == tallow_id and w.life[y * w.width + x] > 0):
                        return True
            return False

        elif self.key == "ameisenstrasse":
            ants = self.custom_state.get("ants", [])
            in_target = sum(1 for ax in ants if ax >= 130.0)
            return in_target >= 3

        elif self.key == "lava_water":
            # Check rock/crust cells in bridge zone
            rock_id = mat.MAT_ID["rock"]
            crust_id = mat.MAT_ID.get("crust", rock_id)
            solid_bridge = 0
            for y in range(75, 105):
                for x in range(45, 105):
                    c = w.get(x, y)
                    if c in (rock_id, crust_id):
                        solid_bridge += 1
            return solid_bridge >= 24

        elif self.key == "acid_gold":
            # Vault is open if gold is accessible (air above it or wall breached)
            dirt_id = mat.MAT_ID["dirt"]
            dirt_count = 0
            for y in range(70, 75):
                for x in range(98, 103):
                    if w.get(x, y) == dirt_id:
                        dirt_count += 1
            return dirt_count == 0

        elif self.key == "oil_fire":
            tallow_id = mat.MAT_ID["tallow"]
            fire_id = mat.FIRE
            wicks_burning = 0
            for wx in (42, 82, 122):
                burning = False
                for y in range(80, 91):
                    c = w.get(wx, y)
                    if c == fire_id or (c == tallow_id and w.life[y * w.width + wx] > 0):
                        burning = True
                        break
                if burning:
                    wicks_burning += 1
            return wicks_burning >= 3

        return False


def make_physik_puzzle(puzzle_key: str | None = None, seed: int = 0) -> Minigame:
    """Create a Physik-o-Mat puzzle."""
    if puzzle_key is None:
        rng = random.Random(seed)
        puzzle_key = rng.choice(PUZZLE_KEYS)
    return PhysikPuzzle(puzzle_key, seed=seed)


def solve_actions(puzzle_key: str) -> list[tuple[str, tuple[int, int]]]:
    """Fixed solution (action, cursor) for tests and the playtest bot."""
    if puzzle_key == "glas_fuellen":
        return [("blast", (40, 27))]
    elif puzzle_key == "vase_retten":
        return [("blast", (80, 92)), ("blast", (80, 100))]
    elif puzzle_key == "kerze_zuenden":
        return [("ignite", (122, 85))]
    elif puzzle_key == "ameisenstrasse":
        return [("dig", (80, 90))]
    elif puzzle_key == "lava_water":
        return [("blast", (75, 53))]
    elif puzzle_key == "acid_gold":
        return [("blast", (100, 52)), ("blast", (100, 72))]
    elif puzzle_key == "oil_fire":
        return [
            ("pour", (50, 85)),
            ("pour", (90, 85)),
            ("ignite", (42, 85)),
            ("ignite", (82, 85)),
            ("ignite", (122, 85)),
        ]
    return []
