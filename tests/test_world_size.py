"""Bigger worlds per universe (work package T2)."""

import json
import time
import unittest
from dataclasses import replace

from src import materials as mat
from src.run import Controls, Run
from src.universes.model import SHAPES


def _run_with_size(size: tuple[int, int], seed: int = 4) -> tuple[Run, float]:
    run = Run(seed=seed)
    run.route = (run.route[0], replace(run.route[1], size=size), *run.route[2:])
    start = time.perf_counter()
    run.enter_depth(1)
    return run, time.perf_counter() - start


class TestWorldSize(unittest.TestCase):
    def tearDown(self) -> None:
        mat.activate(mat.DEFAULT_SET)

    def test_every_shape_generates_and_scales_its_population(self) -> None:
        small = Run(seed=4)
        small.enter_depth(1)
        base = len(small.enemies.creatures)
        for size in SHAPES.values():
            run, seconds = _run_with_size(size)
            self.assertEqual((run.world.width, run.world.height), size)
            self.assertLess(seconds, 6.0)  # target < 3 s on a desktop, CI is slower
            self.assertGreater(run.area_scale, 2.5)
            self.assertGreater(len(run.enemies.creatures), base * 2)
            x, y = run.level.exit
            self.assertTrue(0 < x < size[0] and 0 < y < size[1])

    def test_a_big_world_saves_small_and_loads_again(self) -> None:
        run, _ = _run_with_size(SHAPES["breit"])
        for _ in range(30):
            run.update(1 / 60, Controls(move=1))
        data = run.save_state()
        self.assertLess(len(json.dumps(data)), 2_000_000)
        other = Run(seed=1)
        other.restore(data)
        self.assertEqual((other.world.width, other.world.height), SHAPES["breit"])
        self.assertEqual(bytes(other.world.grid), bytes(run.world.grid))

    def test_sanctum_and_next_depth_return_to_the_default_size(self) -> None:
        run, _ = _run_with_size(SHAPES["hoch"])
        run.enter_sanctum()
        self.assertEqual((run.world.width, run.world.height), run.default_size)
        run.enter_depth(2)
        self.assertEqual((run.world.width, run.world.height), run.default_size)

    def test_sandbox_cycles_size_and_material_set(self) -> None:
        run = Run(seed=2)
        seen = {run.cycle_world_size() for _ in range(len(SHAPES) + 1)}
        self.assertEqual(seen, {run.default_size, *SHAPES.values()})
        self.assertEqual(run.cycle_material_set(), "aktenhalde")
        self.assertEqual(run.world.material_set, "aktenhalde")
        self.assertEqual(run.cycle_material_set(), "koerper")

    def test_generation_hook_is_called_with_the_name(self) -> None:
        run = Run(seed=3)
        names: list[str] = []
        run.on_generate = names.append
        run.enter_depth(0)
        self.assertEqual(names, [run.route[0].name_de])


if __name__ == "__main__":
    unittest.main()
