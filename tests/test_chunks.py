import unittest

from src.body import Body
from src.chunks import FallingChunks, find_loose
from src.materials import AIR, BONE, FLESH
from src.world import World

DT = 1 / 60


def world_with_hanging_block() -> World:
    """A flesh ceiling with a block hanging from it by a thin neck."""
    world = World(160, 120, seed=1)
    for y in range(2, 20):
        for x in range(2, 158):
            world.set_cell(x, y, FLESH)
    for y in range(20, 23):  # neck
        world.set_cell(80, y, FLESH)
    for y in range(23, 33):  # the block
        for x in range(74, 87):
            world.set_cell(x, y, BONE)
    return world


class TestChunks(unittest.TestCase):
    def test_cut_loose_piece_is_found(self) -> None:
        world = world_with_hanging_block()
        self.assertEqual(find_loose(world, 80, 21, 2), [])  # still attached
        for y in range(20, 23):
            world.set_cell(80, y, AIR)
        groups = find_loose(world, 80, 21, 4)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 13 * 10)

    def test_chunk_falls_crushes_and_settles(self) -> None:
        world = world_with_hanging_block()
        for y in range(20, 23):
            world.set_cell(80, y, AIR)
        chunks = FallingChunks()
        self.assertEqual(chunks.detach(world, 80, 21, 4), 1)
        self.assertEqual(world.count(BONE), 0)  # in flight
        victim = Body(78, 120 - 2 - 10, 6, 10, 100)
        for _ in range(240):
            chunks.update(world, DT, [victim])
        self.assertEqual(chunks.items, [])
        self.assertAlmostEqual(world.count(BONE), 130, delta=6)  # landed and solid again
        self.assertLess(victim.hp, 100)
        lowest = max(y for y in range(120) for x in range(74, 87) if world.get(x, y) == BONE)
        self.assertGreater(lowest, 90)

    def test_cave_walls_never_fall(self) -> None:
        from src.depths import DEPTHS
        from src.worldgen import generate_level

        world = World(1280, 720, seed=2)
        generate_level(world, DEPTHS[0])
        chunks = FallingChunks()
        before = world.count(FLESH)
        chunks.detach(world, 640, 400, 6)  # no blast happened: nothing is loose
        self.assertEqual(world.count(FLESH), before)


if __name__ == "__main__":
    unittest.main()


class TestCorpses(unittest.TestCase):
    def test_dead_maggot_leaves_a_flat_lump(self) -> None:
        from src.enemies import SPECIES, Creature
        from src.run import Controls, Run

        run = Run(17)
        cx, cy = run.player.center
        maggot = Creature(SPECIES["made"], int(cx) + 40, int(cy) - 20, run.rng)
        run.enemies.creatures = [maggot]
        maggot.hurt(1000)
        run.update(DT, Controls(aim=(cx, cy)))
        self.assertEqual(len(run.chunks.items), 1)
        cells = {(x, y) for x, y, _m in run.chunks.items[0].cells}
        for _ in range(120):
            run.update(DT, Controls(aim=(cx, cy)))
        self.assertEqual(run.chunks.items, [])
        xs = {x for x, _y in cells}
        landed = sum(
            1 for x in xs for y in range(run.world.height) if run.world.get(x, y) == FLESH
        )
        self.assertGreater(landed, 0)


class TestChunkMotion(unittest.TestCase):
    def test_overhanging_chunk_topples_off_the_ledge(self) -> None:
        from src.chunks import Chunk

        world = World(200, 120, seed=1)
        for y in range(60, 62):  # a short ledge
            for x in range(40, 60):
                world.set_cell(x, y, BONE)
        # a long bar resting on the ledge's right end, hanging far over the edge
        cells = [(x, 59, FLESH) for x in range(55, 85)]
        chunks = FallingChunks()
        chunks.items.append(Chunk(cells))
        for _ in range(300):
            chunks.update(world, DT, [])
        self.assertEqual(chunks.items, [])
        on_ledge = sum(1 for x in range(55, 85) if world.get(x, 59) == FLESH)
        self.assertLess(on_ledge, 5)  # it did not just stay balanced on the edge
        self.assertGreater(world.count(FLESH), 25)

    def test_blast_pushes_chunks_sideways(self) -> None:
        world = world_with_hanging_block()
        for y in range(20, 23):
            world.set_cell(80, y, AIR)
        chunks = FallingChunks()
        chunks.detach(world, 70, 21, 8)  # blast left of the block
        self.assertGreater(chunks.items[0].vx, 0)
