"""작은 입력의 가능한 전체 선택과 마지막 분할을 열거하여 탐욕 결과와 비교한다."""

import copy
import itertools
import json
from pathlib import Path
import random
import runpy
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/ch4_5_knapsack_greedy.py"


def reference_value(items, capacity):
    best = 0
    for mask in itertools.product((False, True), repeat=len(items)):
        weight = sum(w for (w, _), take in zip(items, mask) if take)
        if weight > capacity:
            continue
        value = sum(v for (_, v), take in zip(items, mask) if take)
        best = max(best, value)
        for (w, v), take in zip(items, mask):
            if not take:
                best = max(best, value + v * min(w, capacity - weight) / w)
    return best


class KnapsackStudentTests(unittest.TestCase):
    def setUp(self):
        self.solve = runpy.run_path(str(SOURCE))["knapsack"]
        self.vis = Mock()
        self.vis.stopped.return_value = False
        self.solve.__globals__["vis"] = self.vis

    def check_result(self, items, capacity):
        self.vis.reset_mock()
        before = copy.deepcopy(items)
        selected, total = self.solve(items, capacity)
        self.assertEqual(items, before)
        self.assertEqual(len(selected), len(items))
        self.assertLessEqual(sum(selected), capacity + 1e-9)
        self.assertTrue(all(0 <= amount <= w for amount, (w, _) in zip(selected, items)))
        self.assertLessEqual(sum(0 < amount < w for amount, (w, _) in zip(selected, items)), 1)
        self.assertAlmostEqual(total, sum(v * amount / w for amount, (w, v) in zip(selected, items)))
        self.assertAlmostEqual(total, reference_value(items, capacity))
        return selected, total

    def test_datasets(self):
        path = SOURCE.parent / "data/ch4_5_knapsack_greedy.json"
        for entry in json.loads(path.read_text())["datasets"]:
            with self.subTest(name=entry["name"]):
                self.check_result(**entry["data"])
        self.assertEqual(self.check_result([[30, 120], [10, 60], [20, 100]], 50), ([20, 10, 20], 240))

    def test_small_random_inputs(self):
        rng = random.Random(260901)
        for _ in range(80):
            items = [[rng.randint(1, 20), rng.randint(0, 100)] for _ in range(6)]
            self.check_result(items, rng.randint(0, 100))

    def test_equal_ratios_and_edge_cases(self):
        self.assertEqual(self.check_result([[10, 50], [20, 100]], 15)[0], [10, 5])
        self.assertEqual(self.check_result([], 10), ([], 0))
        self.assertEqual(self.check_result([[5, 10]], 0), ([0], 0))
        self.assertEqual(self.check_result([[5, 10]], 10), ([5], 10))
        self.vis.stopped.return_value = True
        self.assertIsNone(self.solve([[5, 10]], 10))


if __name__ == "__main__":
    unittest.main()
