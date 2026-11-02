"""숫자 맵의 통과 가능 여부와 그래프 변환을 검사한다."""

import copy
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy"
convert = runpy.run_path(str(ROOT / "data_map.py"))["map_to_graph"]
heuristics = runpy.run_path(str(ROOT / "data_map.py"))["map_heuristics"]


class NumericMapTests(unittest.TestCase):
    def test_corner_cutting_requires_both_orthogonal_cells_open(self):
        for tiles in ([[1, 11], [11, 1]], [[1, 1], [11, 1]], [[1, 1], [1, 1]]):
            for cutting in (False, True):
                data = convert(SimpleNamespace(map=tiles, start_cell=[0, 0], goal_cell=[1, 1],
                               movement={"diagonal": True, "corner_cutting": cutting}))
                diagonal = any({u, v} == {data.start, data.goal} for u, v, _ in data.edges)
                self.assertEqual(diagonal, cutting or (tiles[0][1] == tiles[1][0] == 1))
                self.assertEqual(heuristics(data)[data.start], 14)

    def test_large_maps_share_input_and_have_distinct_optimal_costs(self):
        entries = json.loads((ROOT / "data/ch4_4_astar.json").read_text())["datasets"]
        entries = [e for e in entries if e["name"].startswith("큰 맵")]
        from unittest.mock import Mock
        search = runpy.run_path(str(ROOT / "ch4_4_astar.py"))["astar"]
        vis = Mock()
        vis.stopped.return_value = False
        search.__globals__["vis"] = vis
        costs = []
        routes = []
        for entry in entries:
            self.assertEqual(entry["data"]["map"], entries[0]["data"]["map"])
            data = convert(SimpleNamespace(**entry["data"]))
            path, cost = search(len(data.vertices), data.edges, data.start, data.goal, heuristics(data))
            self.assertTrue(path)
            costs.append(cost)
            routes.append([data.grid["cells"][v] for v in path])
        self.assertEqual(costs, [350, 290, 210])
        # 코너커팅을 허용해야만 (5,4)에서 (6,5)의 벽 틈으로 건너갑니다.
        self.assertIn((6, 9), routes[1])
        self.assertNotIn((6, 5), routes[1])
        self.assertIn(((5, 4), (6, 5)), list(zip(routes[2], routes[2][1:])))
        self.assertNotIn((6, 9), routes[2])

    def test_codes_and_graph_edges(self):
        data = SimpleNamespace(map=[[1, 2, 3, 4], [0, 11, 12, 13], [14, 1, 1, 1]],
                               start_cell=[0, 0], goal_cell=[3, 0], _dataset_name="test")
        before = copy.deepcopy(vars(data))
        graph = convert(data)
        self.assertEqual(len(graph.vertices), 7)
        self.assertEqual(graph._dataset_name, "test")
        self.assertEqual(vars(data), before)
        for u, v, cost in graph.edges:
            a, b = graph.grid["cells"][u], graph.grid["cells"][v]
            self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)
            self.assertEqual(cost, 10)
        self.assertNotIn((0, 1), graph.grid["cells"])

    def test_sample_path_avoids_all_obstacle_kinds(self):
        entries = json.loads((ROOT / "data/ch4_4_astar.json").read_text())["datasets"]
        d = next(e["data"] for e in entries if e["name"].startswith("숫자 맵:"))
        data = convert(SimpleNamespace(**d))
        ns = runpy.run_path(str(ROOT / "ch4_4_astar.py"))
        from unittest.mock import Mock
        vis = Mock()
        vis.stopped.return_value = False
        ns["astar"].__globals__["vis"] = vis
        path, cost = ns["astar"](len(data.vertices), data.edges, data.start, data.goal,
                                  ns["straight_line_heuristics"](data.coordinates, data.goal))
        self.assertTrue(path)
        self.assertEqual(cost, (len(path) - 1) * 10)
        for vertex in path:
            x, y = data.grid["cells"][vertex]
            self.assertIn(data.map[y][x], (1, 2, 3, 4))

    def test_invalid_codes_shapes_and_endpoints(self):
        for tiles, start in [([], [0, 0]), ([[1], [1, 2]], [0, 0]), ([[5]], [0, 0]),
                             ([[True]], [0, 0]), ([[1, 11]], [1, 0]), ([[1, 0]], [1, 0])]:
            with self.subTest(tiles=tiles), self.assertRaises(ValueError):
                convert(SimpleNamespace(map=tiles, start_cell=start, goal_cell=[0, 0]))


if __name__ == "__main__":
    unittest.main()
