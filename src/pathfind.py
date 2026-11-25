"""Contract V3: Grid A* pathfinding for walk, fly, and swim (Card A10)."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src import materials as mat

if TYPE_CHECKING:
    from .world import World

PATH_CACHE_TTL: float = 0.4
MAX_PATH_EXPANSIONS: int = 160


@dataclass
class PathCacheEntry:
    path: list[tuple[int, int]] = field(default_factory=list)
    goal: tuple[int, int] = (0, 0)
    updated_at: float = -999.0


@dataclass
class PathFollower:
    """Stateful path-following helper wrapping PathCacheEntry (Contract V3)."""

    loco: str = "walk"
    cache: PathCacheEntry = field(default_factory=PathCacheEntry)

    def step(
        self,
        world: World,
        start_x: float,
        start_y: float,
        goal_x: float,
        goal_y: float,
        now: float = 0.0,
    ) -> tuple[float, float]:
        return next_waypoint(
            world, start_x, start_y, goal_x, goal_y, self.loco, self.cache, now=now
        )


def find_path(
    world: World,
    start: tuple[int, int],
    goal: tuple[int, int],
    loco: str,
    max_expansions: int = MAX_PATH_EXPANSIONS,
) -> list[tuple[int, int]]:
    """Compute a coarse grid path from start to goal cell for loco ('walk', 'fly', 'swim')."""
    start_node = (start[0] // NODE_SIZE, start[1] // NODE_SIZE)
    goal_node = (goal[0] // NODE_SIZE, goal[1] // NODE_SIZE)

    def heuristic(node: tuple[int, int]) -> int:
        return abs(node[0] - goal_node[0]) + abs(node[1] - goal_node[1])

    open_heap: list[tuple[int, int, tuple[int, int]]] = [(heuristic(start_node), 0, start_node)]
    cost_so_far: dict[tuple[int, int], int] = {start_node: 0}
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    closed: set[tuple[int, int]] = set()
    best = start_node
    expansions = 0
    reached = False
    while open_heap and expansions < max_expansions:
        _, _, node = heapq.heappop(open_heap)
        if node in closed:
            continue
        closed.add(node)
        expansions += 1
        if heuristic(node) < heuristic(best):
            best = node
        if node == goal_node:
            reached = True
            break
        for dx, dy in _NEIGHBOURS:
            nxt = (node[0] + dx, node[1] + dy)
            if nxt in closed:
                continue
            step = _node_cost(world, nxt, loco, start_node, goal_node)
            if step is None:
                continue
            new_cost = cost_so_far[node] + step
            if new_cost < cost_so_far.get(nxt, 1 << 30):
                cost_so_far[nxt] = new_cost
                came_from[nxt] = node
                heapq.heappush(open_heap, (new_cost + heuristic(nxt), new_cost, nxt))

    end_node = goal_node if reached else best
    nodes = [end_node]
    while nodes[-1] != start_node:
        nodes.append(came_from[nodes[-1]])
    nodes.reverse()
    path = [start]
    path.extend(_node_center(n) for n in nodes[1:-1])
    if reached:
        if len(nodes) > 1 or goal != start:
            path.append(goal)
    elif len(nodes) > 1:
        path.append(_node_center(end_node))
    return path


NODE_SIZE = 4
_NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _node_center(node: tuple[int, int]) -> tuple[int, int]:
    return (NODE_SIZE * node[0] + 2, NODE_SIZE * node[1] + 2)


def _node_cost(
    world: World,
    node: tuple[int, int],
    loco: str,
    start_node: tuple[int, int],
    goal_node: tuple[int, int],
) -> int | None:
    """Cost of entering ``node`` or None if impassable; the middle cell decides.

    Walkers climb at most one node per step because the search moves one node at a time.
    """
    nx, ny = node
    if nx < 0 or ny < 0 or nx * NODE_SIZE >= world.width or ny * NODE_SIZE >= world.height:
        return None
    if node == start_node or node == goal_node:
        return 1
    cx, cy = _node_center(node)
    kind = mat.KIND[world.get(cx, cy)]
    if loco == "swim":
        return 1 if kind == mat.LIQUID else None
    if loco == "fly":
        if kind in (mat.EMPTY, mat.GAS):
            return 1
        return 3 if kind == mat.LIQUID else None
    if kind not in (mat.EMPTY, mat.GAS):
        return None
    below = mat.KIND[world.get(cx, cy + NODE_SIZE)]
    return 1 if below in (mat.SOLID, mat.POWDER) else None


def next_waypoint(
    world: World,
    start_x: float,
    start_y: float,
    goal_x: float,
    goal_y: float,
    loco: str,
    cache: PathCacheEntry,
    now: float = 0.0,
) -> tuple[float, float]:
    """Return the next world-pixel waypoint towards (goal_x, goal_y), updating cache if stale."""
    start = (int(start_x), int(start_y))
    goal = (int(goal_x), int(goal_y))
    moved = abs(goal[0] - cache.goal[0]) + abs(goal[1] - cache.goal[1]) >= NODE_SIZE * 2
    if not cache.path or moved or now - cache.updated_at >= PATH_CACHE_TTL:
        cache.path = find_path(world, start, goal, loco)
        cache.goal = goal
        cache.updated_at = now
    # skip waypoints we are already standing on
    while len(cache.path) > 1 and (
        abs(cache.path[0][0] - start[0]) + abs(cache.path[0][1] - start[1]) <= NODE_SIZE
    ):
        cache.path.pop(0)
    target = cache.path[0]
    return (float(target[0]), float(target[1]))
