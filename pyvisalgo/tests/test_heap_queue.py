"""실제 heapq 결과와 표시용 복사본 및 중복 원소 대응을 검사한다."""

import copy
import heapq
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.visualizers.heap_queue import HeapQueueVisualizer


class HeapQueueTests(unittest.TestCase):
    def setUp(self):
        self.vis = HeapQueueVisualizer(config_path="/tmp/heap-queue-test.json")
        self.vis.font_scale = 1
        self.vis.wait = lambda *args: self.vis.draw()
        self.vis.speed = 999999

    def tearDown(self):
        pygame.quit()

    def test_all_datasets_match_real_heapq(self):
        root = Path(__file__).resolve().parents[2]
        datasets = json.loads((root / "src/w09_ch4_greedy/data/ch4_0_heap.json").read_text())["datasets"]
        for entry in datasets:
            data = SimpleNamespace(**entry["data"])
            convert = tuple if data.element_type == "tuple" else copy.deepcopy
            heap = [convert(v) for v in data.array]
            pushes = [convert(v) for v in data.pushes]
            if data.element_type == "negated":
                heap = [-v for v in heap]
                pushes = [-v for v in pushes]
            expected = sorted(heap + pushes)[:data.pop_count]
            self.vis.setup(data, heap)
            initial = copy.deepcopy(heap)
            heapq.heapify(heap)
            self.assertEqual(self.vis.values, initial)
            self.vis.heapify(heap)
            for value in pushes:
                heapq.heappush(heap, value)
                self.vis.push(heap, value)
                self.assertEqual(self.vis.values, heap)
            for _ in range(data.pop_count):
                value = heapq.heappop(heap)
                self.vis.pop(heap, value)
                self.assertEqual(self.vis.values, heap)
                self.assertIsNone(self.vis.motion)
            self.assertEqual(self.vis.returned, expected)
            self.vis.setup(data, initial)
            self.assertEqual(self.vis.returned, [])
            self.assertIsNone(self.vis.focus)

    def test_equal_lists_are_matched_once_and_pop_excludes_root(self):
        mapping = self.vis.match_positions([[1], [1], [2]], [[1], [2]], popped=True)
        self.assertEqual(mapping, {1: 0, 2: 1})

    def test_empty_heap_and_enter_complete_transition(self):
        data = SimpleNamespace(array=[1], pushes=[], element_type="int")
        self.vis.setup(data, [1])
        self.vis.running_to_section = True
        self.vis.heapify([1])
        self.assertFalse(self.vis.running_to_section)
        self.vis.pop([], 1)
        self.assertEqual(self.vis.values, [])
        self.assertEqual(self.vis.returned, [1])

    def test_motion_frames_and_two_window_sizes(self):
        data = SimpleNamespace(array=[5, 2, 7], pushes=[1], element_type="int")
        self.vis.setup(data, data.array)
        self.vis.motion = ([5, 2, 7], [2, 5, 7], {0: 1, 1: 0, 2: 2}, False, 0.5)
        for width, height in [(1280, 720), (1600, 900)]:
            self.vis.screen = pygame.display.set_mode((width, height))
            self.vis.view.resize(width, height)
            self.vis.draw()
        self.assertGreater(len(set(pygame.image.tobytes(self.vis.screen, "RGB"))), 10)

    def test_push_and_pop_show_each_parent_child_step(self):
        data = SimpleNamespace(array=[2, 5, 3, 9, 8, 7, 6], pushes=[1], element_type="int")
        heap = data.array.copy()
        self.vis.setup(data, heap)
        steps = []
        original_swap = self.vis._swap

        def record(source, destination, label):
            steps.append((source, destination, label))
            original_swap(source, destination, label)

        self.vis._swap = record
        heapq.heappush(heap, 1)
        self.vis.push(heap, 1)
        self.assertEqual([(a, b) for a, b, _ in steps], [(7, 3), (3, 1), (1, 0)])
        self.assertTrue(all(label == "up-heap ↑" for _, _, label in steps))
        steps.clear()
        value = heapq.heappop(heap)
        self.vis.pop(heap, value)
        self.assertEqual([(a, b) for a, b, _ in steps], [(0, 1), (1, 3)])
        self.assertTrue(all(label == "down-heap ↓" for _, _, label in steps))
        self.assertEqual(self.vis.values, heap)
        self.assertIsNone(self.vis.travel)
        self.assertEqual(self.vis.comparing, set())


if __name__ == "__main__":
    unittest.main()
