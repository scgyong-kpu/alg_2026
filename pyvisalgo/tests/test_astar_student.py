"""A*의 비용·경로·휴리스틱 전제와 h=0 비교를 검사한다."""

import copy
import heapq
import json
import math
from pathlib import Path
import random
import runpy
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/ch4_4_astar.py"


def reference_cost(count, edges, start, goal):
    graph = {v: {} for v in range(count)}
    for u, v, w in edges:
        graph[u][v] = graph[v][u] = w
    distances = [math.inf] * count
    distances[start] = 0
    queue = [(0, start)]
    while queue:
        g, u = heapq.heappop(queue)
        if g != distances[u]:
            continue
        if u == goal:
            return g
        for v, w in graph[u].items():
            if g + w < distances[v]:
                distances[v] = g + w
                heapq.heappush(queue, (g + w, v))
    return math.inf


class AStarStudentTests(unittest.TestCase):
    def setUp(self):
        self.module = runpy.run_path(str(SOURCE))
        self.search = self.module["astar"]
        self.heuristic = self.module["straight_line_heuristics"]
        maps = runpy.run_path(str(SOURCE.parent / "data_map.py"))
        self.convert_map = maps["map_to_graph"]
        self.map_heuristics = maps["map_heuristics"]
        self.vis = Mock()
        self.vis.stopped.return_value = False
        self.search.__globals__["vis"] = self.vis

    def assert_path(self, n, edges, start, goal, h):
        self.vis.reset_mock()
        path, cost = self.search(n, edges, start, goal, h)
        self.assertEqual(cost, reference_cost(n, edges, start, goal))
        if not math.isfinite(cost):
            self.assertEqual(path, [])
            return
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        self.assertEqual(len(path), len(set(path)))
        weights = {frozenset((u, v)): w for u, v, w in edges}
        self.assertEqual(sum(weights[frozenset((u, v))] for u, v in zip(path, path[1:])), cost)

    def test_datasets_and_start_goal_pairs(self):
        entries = json.loads((SOURCE.parent / "data/ch4_4_astar.json").read_text())["datasets"]
        for entry in entries:
            d = entry["data"]
            if "map" in d:
                from types import SimpleNamespace
                d = vars(self.convert_map(SimpleNamespace(**d)))
            before = copy.deepcopy(d)
            n = len(d["vertices"])
            goals = sorted({0, d["goal"], n - 1}) if "grid" in d else range(n)
            starts = sorted({0, d["start"], n - 1}) if "grid" in d else range(n)
            for goal in goals:
                if "map" in d:
                    h = self.map_heuristics(SimpleNamespace(**{**d, "goal": goal}))
                else:
                    h = self.heuristic(d["coordinates"], goal)
                for start in starts:
                    with self.subTest(dataset=entry["name"], start=start, goal=goal):
                        self.assert_path(n, d["edges"], start, goal, h)
                self.assert_path(n, d["edges"], d["start"], goal, [0] * n)
            self.assertEqual(d, before)

    def test_goal_discovery_does_not_end_search(self):
        edges = [[0, 2, 400], [0, 1, 100], [1, 2, 100]]
        self.assertEqual(self.search(3, edges, 0, 2, [200, 100, 0]), ([0, 1, 2], 200))
        self.vis.update_candidate.assert_called_once()
        self.assertEqual([c.args[0] for c in self.vis.take_candidate.call_args_list], [0, 1, 2])

    def test_priority_is_f_and_result_is_g(self):
        edges = [[0, 1, 2], [0, 2, 5], [1, 3, 20], [2, 3, 5]]
        path, cost = self.search(4, edges, 0, 3, [8, 10, 3, 0])
        self.assertEqual(path, [0, 2, 3])
        self.assertEqual(cost, 10)
        # g=5라도 f=8인 정점 2를 g=2, f=12인 정점 1보다 먼저 꺼냅니다.
        self.assertEqual([c.args[0] for c in self.vis.take_candidate.call_args_list], [0, 2, 3])

    def test_heuristic_reduces_search_in_direction_example(self):
        entries = json.loads((SOURCE.parent / "data/ch4_4_astar.json").read_text())["datasets"]
        d = next(e["data"] for e in entries if e["name"].startswith("방향 안내"))
        n = len(d["vertices"])
        self.search(n, d["edges"], d["start"], d["goal"], self.heuristic(d["coordinates"], d["goal"]))
        informed = self.vis.take_candidate.call_count
        self.vis.reset_mock()
        self.search(n, d["edges"], d["start"], d["goal"], [0] * n)
        self.assertLess(informed, self.vis.take_candidate.call_count)

    def test_random_geometric_graphs(self):
        rng = random.Random(260927)
        for _ in range(50):
            points = [(rng.randrange(500), rng.randrange(500)) for _ in range(12)]
            edges = [[u, v, math.ceil(math.dist(points[u], points[v])) + rng.randrange(20)]
                     for u in range(12) for v in range(u + 1, 12) if rng.random() < 0.25]
            for start, goal in [(0, 11), (4, 7), (8, 1)]:
                self.assert_path(12, edges, start, goal, self.heuristic(points, goal))

    def test_grid_paths_avoid_walls_and_use_only_cardinal_neighbors(self):
        entries = json.loads((SOURCE.parent / "data/ch4_4_astar.json").read_text())["datasets"]
        grids = [e["data"] for e in entries if "grid" in e["data"]]
        self.assertEqual(len(grids), 3)
        for d in grids:
            cells = d["grid"]["cells"]
            rows = d["grid"]["rows"]
            self.assertEqual(len(cells), sum(ch != "#" for line in rows for ch in line))
            for u, v, w in d["edges"]:
                a, b = cells[u], cells[v]
                self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)
                self.assertEqual(w, 10)
            path, cost = self.search(len(cells), d["edges"], d["start"], d["goal"],
                                     self.heuristic(d["coordinates"], d["goal"]))
            for vertex in path:
                x, y = cells[vertex]
                self.assertNotEqual(rows[y][x], "#")
            if path:
                self.assertEqual(cost, (len(path) - 1) * 10)
                a, b = cells[d["start"]], cells[d["goal"]]
                self.assertGreater(cost, (abs(a[0] - b[0]) + abs(a[1] - b[1])) * 10)
            else:
                self.assertEqual(cost, math.inf)

    def test_zero_equal_start_and_stop(self):
        self.assertEqual(self.search(3, [[0, 1, 0], [1, 2, 1]], 0, 2, [0, 0, 0]), ([0, 1, 2], 1))
        self.assertEqual(self.search(1, [], 0, 0, [0]), ([0], 0))
        self.vis.stopped.return_value = True
        self.assertEqual(self.search(1, [], 0, 0, [0]), ([], math.inf))

    def test_invalid_inputs(self):
        cases = [
            (2, [[0, 1, -1]], 0, 1, [0, 0]),
            (2, [[0, 1, math.inf]], 0, 1, [0, 0]),
            (2, [[0, 1, 1]], 2, 1, [0, 0]),
            (2, [[0, 1, 1]], 0, 1, [0]),
            (2, [[0, 1, 1]], 0, 1, [0, 1]),
            (2, [[0, 1, 1]], 0, 1, [2, 0]),
            (2, [[0, 1, 1]], 0, 1, [math.nan, 0]),
            (2, [[0, 1, 1]], 0, 1, [-1, 0]),
            (2, [[0, 1, 1], [0, 1, 2]], 0, 1, [0, 0]),
        ]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.search(*args)


if __name__ == "__main__":
    unittest.main()
