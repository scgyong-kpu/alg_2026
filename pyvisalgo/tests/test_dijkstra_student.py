"""Dijkstra 학생 코드의 누적 거리와 경로를 독립적인 거리 계산과 비교한다."""

import copy
import json
from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/ch4_3_dijkstra.py"


class DijkstraStudentTests(unittest.TestCase):
    def setUp(self):
        self.dijkstra = runpy.run_path(str(SOURCE))["dijkstra"]
        self.vis = Mock()
        self.vis.stopped.return_value = False
        self.dijkstra.__globals__["vis"] = self.vis

    def test_cumulative_distance_and_path_updates(self):
        distances, previous = self.dijkstra(4, [(0, 1, 10), (0, 2, 3), (2, 1, 4), (1, 3, 5)])
        self.assertEqual(distances, [0, 7, 3, 12])
        self.assertEqual(previous, [None, 2, 0, 1])
        self.assertTrue(self.vis.update_candidate.called)

    def test_all_datasets_and_all_start_vertices(self):
        entries = json.loads((SOURCE.parent / "data/ch4_1_mst_kruskal.json").read_text())["datasets"]
        for entry in entries:
            data = entry["data"]
            n = len(data["vertices"])
            before = copy.deepcopy(data)
            for start in range(n):
                expected = [float("inf")] * n
                expected[start] = 0
                for _ in range(n - 1):
                    for u, v, weight in data["edges"]:
                        expected[v] = min(expected[v], expected[u] + weight)
                        expected[u] = min(expected[u], expected[v] + weight)
                distances, previous = self.dijkstra(n, data["edges"], start)
                self.assertEqual(distances, expected)
                graph = {v: {} for v in range(n)}
                for u, v, weight in data["edges"]:
                    graph[u][v] = graph[v][u] = weight
                for vertex in range(n):
                    seen = set()
                    cost = 0
                    current = vertex
                    while previous[current] is not None:
                        self.assertNotIn(current, seen)
                        seen.add(current)
                        cost += graph[current][previous[current]]
                        current = previous[current]
                    self.assertEqual(current, start)
                    self.assertEqual(cost, distances[vertex])
            self.assertEqual(data, before)

    def test_unreachable_zero_weight_and_single_vertex(self):
        self.assertEqual(self.dijkstra(4, [(0, 1, 0), (2, 3, 3)]),
                         ([0, 0, float("inf"), float("inf")], [None, 0, None, None]))
        self.assertEqual(self.dijkstra(1, []), ([0], [None]))

    def test_negative_weights_and_invalid_start(self):
        with self.assertRaisesRegex(ValueError, "음수"):
            self.dijkstra(2, [(0, 1, -1)])
        with self.assertRaisesRegex(ValueError, "시작"):
            self.dijkstra(2, [(0, 1, 1)], start=2)


if __name__ == "__main__":
    unittest.main()
