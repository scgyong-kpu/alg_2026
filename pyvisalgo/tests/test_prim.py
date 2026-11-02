"""Prim의 후보 힙 배열과 내륙 정점 시각화를 검사한다."""

import copy
import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.visualizers.prim import PrimVisualizer


class PrimDrawingTests(unittest.TestCase):
    def setUp(self):
        self.vis = PrimVisualizer(config_path="/tmp/prim-test-config.json")
        self.vis.font_scale = 1
        self.data = SimpleNamespace(vertices=list("ABCD"),
                                    edges=[[0, 1, 9], [0, 2, 3], [0, 3, 7], [1, 2, 4], [2, 3, 12]])
        self.vis.setup(self.data)
        self.vis.wait = lambda *args: self.vis.draw()
        self.vis.is_max_speed = lambda: True

    def tearDown(self):
        pygame.quit()

    def assert_heap(self):
        heap = self.vis.heap
        for index in range(1, len(heap)):
            self.assertLessEqual(heap[(index - 1) // 2][0], heap[index][0])

    def test_candidate_events_and_inland_are_separate(self):
        weights = {0: (0, 0)}
        self.vis.add_candidate(0, 0, 0, weights, starting=True)
        self.assertEqual(self.vis.inland, [])
        self.vis.take_candidate(0, 0, 0, {}, 0)
        self.assertEqual(self.vis.inland, [0])
        weights = {1: (9, 0), 2: (3, 0), 3: (7, 0)}
        before = copy.deepcopy(weights)
        self.vis.add_candidate(1, 9, 0, weights)
        self.assert_heap()
        self.assertEqual(weights, before)
        del weights[2]
        self.vis.take_candidate(2, 3, 0, weights, 3)
        self.assertEqual(self.vis.inland, [0, 2])
        self.assertNotIn(2, [vertex for _, vertex, _ in self.vis.heap])
        weights[1] = (4, 2)
        self.vis.update_candidate(1, 9, 0, 4, 2, weights)
        self.assertIn((4, 1, 2), self.vis.heap)
        self.assert_heap()
        before_heap = list(self.vis.heap)
        self.vis.keep_candidate(3, 7, 0, 12, 2)
        self.assertEqual(self.vis.heap, before_heap)
        self.vis.ignore_inland(2, 0)
        self.assertEqual(self.vis.inland, [0, 2])

    def test_real_extraction_can_differ_from_displayed_root_on_tie(self):
        self.vis.add_candidate(1, 4, 0, {2: (4, 0), 1: (4, 0)})
        self.assertEqual(self.vis.heap[0][1], 1)
        self.vis.take_candidate(2, 4, 0, {1: (4, 0)}, 4)
        self.assertEqual(self.vis.inland, [2])
        self.assertEqual(self.vis.heap, [(4, 1, 0)])

    def test_heap_array_is_not_a_sorted_list(self):
        self.vis.add_candidate(2, 2, 0, {0: (1, 0), 1: (3, 0), 2: (2, 0)})
        self.assertEqual([cost for cost, _, _ in self.vis.heap], [1, 3, 2])
        self.assert_heap()

    def test_dense_candidates_clip_hits_and_scroll_in_both_modes(self):
        self.vis.setup(SimpleNamespace(vertices=[str(i) for i in range(18)], edges=[]))
        weights = {i: (i + 1, 0) for i in range(18)}
        self.vis.add_candidate(17, 18, 0, weights)
        self.vis.draw()
        self.assertEqual(len(self.vis.hits), 11)
        self.assertEqual(self.vis.candidate_scroll, 7)
        for rect, _ in self.vis.hits:
            self.assertGreaterEqual(rect[1], self.vis.candidate_top)
            self.assertLessEqual(rect[1] + rect[3], self.vis.candidate_top + self.vis.candidate_rows * self.vis.row_step)
            self.assertEqual(rect[0], self.vis.panel_left)
        self.vis._toggle_explanation()
        self.vis.draw()
        self.assertEqual(len(self.vis.hits), 16)
        self.assertEqual(self.vis.candidate_scroll, 2)

    def test_neighbor_preview_is_brief_and_does_not_change_graph_state(self):
        seen = []

        def render(*args):
            self.vis.draw()
            seen.append((set(self.vis.preview_neighbors), self.vis._edge_color(0, 1)))

        self.vis.wait = render
        neighbors = {1: 9, 2: 3, 3: 7}
        self.vis.inland = [0]
        self.vis.show_neighbors(0, neighbors)
        self.assertEqual(seen[0][0], {1, 2, 3})
        from pyvisalgo.core import colors
        self.assertEqual(seen[0][1], colors.ORANGE)
        self.assertFalse(self.vis.preview_neighbors)
        self.assertEqual(self.vis.inland, [0])
        self.assertEqual(neighbors, {1: 9, 2: 3, 3: 7})

    def test_update_changes_values_before_moving_to_new_heap_position(self):
        self.vis.add_candidate(1, 9, 0, {1: (9, 0), 2: (3, 0), 3: (7, 0)})
        self.vis.is_max_speed = lambda: False
        events = []

        def render(*args):
            self.vis.draw()
            if self.vis.value_change is not None:
                events.append(("value", self.vis.value_change["progress"], list(self.vis.heap)))
            elif self.vis.motion is not None:
                events.append(("move", self.vis.motion["progress"], list(self.vis.heap)))

        self.vis.wait = render
        self.vis.update_candidate(1, 9, 0, 2, 2, {1: (2, 2), 2: (3, 0), 3: (7, 0)})
        kinds = [event[0] for event in events]
        self.assertEqual(kinds, ["value"] * 31 + ["move"] * 31)
        self.assertIn((9, 1, 0), events[0][2])
        self.assertEqual(events[-1][2][0], (2, 1, 2))
        self.assertTrue(any(0 < progress < 1 for _, progress, _ in events))
        self.assertIsNone(self.vis.value_change)
        self.assertIsNone(self.vis.motion)

    def test_comparison_names_destination_and_both_origins(self):
        self.vis._compare(3, 250, 0, 240, 2)
        self.assertIn("#3까지", self.vis.messages["action"])
        self.assertIn("#0에서 출발하는 비용 250", self.vis.messages["action"])
        self.assertIn("#2에서 출발하는 비용 240", self.vis.messages["action"])
        self.vis._compare(3, 240, 0, 240, 2)
        self.assertIn("같다", self.vis.messages["action"])

    def test_fast_forward_update_finishes_both_animation_phases(self):
        self.vis.add_candidate(1, 9, 0, {1: (9, 0), 2: (3, 0)})
        self.vis.running_to_section = True
        self.vis.update_candidate(1, 9, 0, 1, 2, {1: (1, 2), 2: (3, 0)})
        self.assertEqual(self.vis.heap[0], (1, 1, 2))
        self.assertFalse(self.vis.running_to_section)
        self.assertIsNone(self.vis.value_change)
        self.assertIsNone(self.vis.motion)

    def test_inland_vertices_use_full_width_below_graph_and_candidates(self):
        self.vis.setup(SimpleNamespace(vertices=[str(i) for i in range(18)], edges=[]))
        self.vis.inland = list(range(18))
        self.vis.draw()
        centers = [self.vis._inland_position(i) for i in range(18)]
        self.assertLess(centers[0][0], self.vis.panel_left)
        self.assertGreater(centers[-1][0], 1000)
        self.assertTrue(all(y - 19 > self.vis.plane_rect[1] + self.vis.plane_rect[3] for _, y in centers))
        self.assertTrue(all(y + 46 < 640 for _, y in centers))
        self.assertEqual(len(self.vis.hits), 18)

    def test_restart_and_hidden_layout_at_two_window_sizes(self):
        self.vis.add_candidate(1, 9, 0, {1: (9, 0), 2: (3, 0)})
        snapshot = list(self.vis.heap)
        for size in ((1600, 900), (960, 640)):
            self.vis.screen = pygame.display.set_mode(size)
            self.vis.view.resize(*size)
            self.vis.draw()
            self.vis._handle_key(pygame.K_h)
            self.vis.draw()
            self.assertEqual(self.vis.heap, snapshot)
            self.assertTrue(self.vis.hidden)
            self.vis._handle_key(pygame.K_h)
            self.assertFalse(self.vis.hidden)
        self.vis.setup(self.data)
        self.assertEqual(self.vis.heap, [])
        self.assertEqual(self.vis.inland, [])
        self.assertIsNone(self.vis.motion)
        self.assertIsNone(self.vis.comparison)

    def test_enter_skips_only_current_operation_and_keeps_final_state(self):
        self.vis.running_to_section = True
        self.vis.add_candidate(1, 9, 0, {1: (9, 0)})
        self.assertFalse(self.vis.running_to_section)
        self.assertEqual(self.vis.heap, [(9, 1, 0)])
        self.assertIsNone(self.vis.motion)


if __name__ == "__main__":
    unittest.main()
