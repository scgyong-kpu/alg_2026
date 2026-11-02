"""heapdict를 이용한 Prim 학생 코드의 결과와 이웃 처리를 검사한다."""

import copy
import json
from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/ch4_2_mst_prim.py"


class PrimStudentTests(unittest.TestCase):
    def setUp(self):
        self.prim = runpy.run_path(str(SOURCE))["prim"]
        self.vis = Mock()
        self.vis.stopped.return_value = False
        self.prim.__globals__["vis"] = self.vis

    def test_all_datasets_and_start_vertices(self):
        entries = json.loads((SOURCE.parent / "data/ch4_1_mst_kruskal.json").read_text())["datasets"]
        for entry, expected in zip(entries, (25, 32, 1809, 2224, 2556), strict=True):
            data = entry["data"]
            before = copy.deepcopy(data)
            count = len(data["vertices"])
            for start in range(count):
                with self.subTest(dataset=entry["name"], start=start):
                    mst, cost = self.prim(count, data["edges"], start)
                    self.assertEqual(cost, expected)
                    self.assertEqual(len(mst), count - 1)
            self.assertEqual(data, before)

    def test_all_neighbor_cases(self):
        edges = [(0, 1, 10), (0, 2, 3), (0, 3, 12), (2, 1, 4), (2, 3, 20), (1, 3, 5)]
        self.assertEqual(self.prim(4, edges), ([(0, 2, 3), (2, 1, 4), (1, 3, 5)], 12))
        self.assertEqual(self.vis.add_candidate.call_count, 4)
        self.assertEqual(self.vis.update_candidate.call_count, 2)
        self.assertTrue(self.vis.ignore_inland.called)
        self.assertTrue(self.vis.keep_candidate.called)

    def test_zero_equal_and_negative_costs(self):
        mst, cost = self.prim(4, [(0, 1, 0), (0, 2, 2), (1, 2, 2), (1, 3, -1), (2, 3, 2)])
        self.assertEqual(len(mst), 3)
        self.assertEqual(cost, 1)
        self.assertTrue(self.vis.keep_candidate.called)

    def test_disconnected_single_and_stopped(self):
        edges = [(0, 1, 2), (2, 3, 3)]
        self.assertEqual(self.prim(4, edges, 0), ([(0, 1, 2)], 2))
        self.assertEqual(self.prim(4, edges, 2), ([(2, 3, 3)], 3))
        self.assertEqual(self.prim(1, []), ([], 0))
        self.vis.stopped.return_value = True
        self.assertEqual(self.prim(4, edges), ([], 0))


if __name__ == "__main__":
    unittest.main()
