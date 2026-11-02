"""분할 배낭의 정렬·이동·절단과 빠른 진행 상태를 검사한다."""

import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.visualizers.knapsack import FractionalKnapsackVisualizer


class KnapsackDrawingTests(unittest.TestCase):
    def setUp(self):
        self.vis = FractionalKnapsackVisualizer(width=1280, height=720,
                                                config_path="/tmp/knapsack-test.json")
        self.vis.font_scale = 1
        self.vis.speed = 999999
        self.vis.wait = lambda *args: self.vis.draw()

    def tearDown(self):
        pygame.quit()

    def test_all_datasets_and_reset(self):
        source = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/data/ch4_5_knapsack_greedy.json"
        for entry in json.loads(source.read_text())["datasets"]:
            data = SimpleNamespace(**entry["data"])
            v = self.vis
            v.setup(data)
            self.assertEqual(v.packed, [])
            ranked = sorted(range(len(data.items)), key=lambda i: data.items[i][1] / data.items[i][0], reverse=True)
            for i, (w, value) in enumerate(data.items):
                v.measure(i, value / w)
            v.sort_items(ranked)
            self.assertEqual(v.order, ranked)
            remaining = data.capacity
            for i in ranked:
                if remaining <= 0:
                    break
                amount = min(remaining, data.items[i][0])
                v.take(i, amount)
                remaining -= amount
                self.assertIsNone(v.motion)
                self.assertIsNone(v.cut)
            v.finish()
            self.assertTrue(v.finished)
            self.assertAlmostEqual(sum(w for _, w in v.packed), min(data.capacity, sum(w for w, _ in data.items)))

    def test_animation_frames_and_enter_boundary(self):
        v = self.vis
        v.setup(SimpleNamespace(items=[[30, 120], [10, 60], [20, 100]], capacity=50))
        v.speed = 1
        frames = []
        v.wait = lambda *args: (v.draw(), frames.append(dict(v.motion) if v.motion else None))
        v.sort_items([1, 2, 0])
        v.take(1, 10)
        v.take(2, 20)
        v.take(0, 20)
        self.assertTrue(any(m and m["kind"] == "sort" and 0 < m["t"] < 1 for m in frames))
        self.assertTrue(any(m and m["kind"] == "take" and 0 < m["t"] < 1 for m in frames))
        v.setup(SimpleNamespace(items=[[30, 120], [10, 60]], capacity=20))
        v._handle_key(pygame.K_RETURN)
        v.sort_items([1, 0])
        self.assertFalse(v.running_to_section)
        self.assertEqual(v.packed, [])
        v.take(1, 10)
        v.take(0, 10)
        self.assertEqual(v.selected, {1: 10, 0: 10})

    def test_invalid_amount_and_input(self):
        v = self.vis
        for items, capacity in [([[0, 1]], 1), ([[1, -1]], 1), ([[1, 1]], -1)]:
            with self.assertRaises(ValueError):
                v.setup(SimpleNamespace(items=items, capacity=capacity))
        v.setup(SimpleNamespace(items=[[10, 50]], capacity=5))
        with self.assertRaises(ValueError):
            v.take(0, 6)


if __name__ == "__main__":
    unittest.main()
