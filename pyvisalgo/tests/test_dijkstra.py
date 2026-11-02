"""Prim 애니메이션의 재사용과 Dijkstra 전용 누적 거리 표시를 검사한다."""

import copy
import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.visualizers.dijkstra import DijkstraVisualizer
from pyvisalgo.visualizers.prim import PrimVisualizer


class DijkstraDrawingTests(unittest.TestCase):
    def setUp(self):
        self.vis = DijkstraVisualizer(config_path="/tmp/dijkstra-test.json")
        self.vis.font_scale = 1
        self.vis.speed = 999999
        self.data = SimpleNamespace(vertices=list("ABCD"),
                                    edges=[[0, 1, 10], [0, 2, 3], [2, 1, 4], [1, 3, 5], [2, 3, 20]])
        self.vis.setup(self.data)
        self.frames = []

        def draw(*args):
            self.vis.draw()
            messages = dict(self.vis.messages)
            for text in messages.values():
                self.assertNotIn("Prim", text)
                self.assertNotIn("MST", text)
                self.assertNotIn("내륙", text)
            self.frames.append(messages)

        self.vis.wait = draw

    def tearDown(self):
        pygame.quit()

    def confirm_start(self):
        self.vis.add_candidate(0, 0, 0, {0: [0, 0]}, starting=True)
        self.vis.take_candidate(0, 0, 0, {})

    def run_events(self):
        self.confirm_start()
        weights = {1: [10, 0]}
        self.vis.add_candidate(1, 10, 0, weights)
        weights[2] = [3, 0]
        self.vis.add_candidate(2, 3, 0, weights)
        del weights[2]
        self.vis.take_candidate(2, 3, 0, weights)
        self.vis.show_neighbors(2, {0: 3, 1: 4, 3: 20})
        self.vis.inspect_edge(2, 0, 3)
        self.vis.ignore_inland(2, 0)
        self.vis.inspect_edge(2, 1, 4)
        weights[1] = [7, 2]
        before = copy.deepcopy(weights)
        self.vis.update_candidate(1, 10, 0, 7, 2, weights)
        self.assertEqual(weights, before)
        weights[3] = [23, 2]
        self.vis.add_candidate(3, 23, 2, weights)
        self.vis.keep_candidate(1, 7, 2, 7, 2)
        self.vis.keep_candidate(1, 7, 2, 10, 0)
        del weights[1]
        self.vis.take_candidate(1, 7, 2, weights)
        weights[3] = [12, 1]
        self.vis.update_candidate(3, 23, 2, 12, 1, weights)
        del weights[3]
        self.vis.take_candidate(3, 12, 1, weights)
        self.vis.finish_paths()

    def test_shared_animation_and_shortest_path_results(self):
        self.assertIsInstance(self.vis, PrimVisualizer)
        self.run_events()
        self.assertEqual(self.vis.distances, {0: 0, 2: 3, 1: 7, 3: 12})
        self.assertEqual(self.vis.predecessors, {0: None, 2: 0, 1: 2, 3: 1})
        self.assertEqual(self.vis.path_to(3), [0, 2, 1, 3])
        self.assertEqual(self.vis.total_cost, 0)
        self.assertEqual(self.vis.heap, [])
        self.assertTrue(any("3 + 간선 4" in frame["detail"] for frame in self.frames))
        self.assertTrue(any("7 < 기존 거리 10" in frame["action"] for frame in self.frames))

    def test_restart_and_unreachable_vertices(self):
        self.run_events()
        self.vis.setup(self.data, start=3)
        self.assertEqual(self.vis.distances, {})
        self.assertEqual(self.vis.predecessors, {})
        self.assertEqual(self.vis.inland, [])
        self.assertFalse(self.vis.finished)
        self.vis.add_candidate(3, 0, 3, {3: [0, 3]}, starting=True)
        self.vis.take_candidate(3, 0, 3, {})
        self.vis.finish_paths()
        self.vis.draw()
        self.assertIn("3개", self.vis.messages["detail"])
        self.assertEqual(self.vis.path_to(0), [])
        self.assertEqual(self.vis.path_to(3), [3])

    def test_hover_path_and_hidden_layout(self):
        from pyvisalgo.core import colors
        self.run_events()
        self.vis.hovered = ("vertex", 3)
        self.assertEqual(self.vis._edge_color(0, 2), colors.YELLOW)
        self.assertEqual(self.vis._edge_color(2, 1), colors.YELLOW)
        self.assertEqual(self.vis._edge_color(1, 3), colors.YELLOW)
        for width, height in [(1280, 720), (1600, 900)]:
            self.vis.screen = pygame.display.set_mode((width, height))
            self.vis.view.resize(width, height)
            self.vis.draw()
            self.vis._toggle_explanation()
            self.vis.draw()
            self.vis._toggle_explanation()
        self.assertEqual(self.vis.path_to(3), [0, 2, 1, 3])

    def test_animation_frames_and_fast_forward_preserve_results(self):
        self.vis.speed = 1
        self.confirm_start()
        self.vis.add_candidate(1, 10, 0, {1: [10, 0]})
        self.vis.add_candidate(2, 3, 0, {1: [10, 0], 2: [3, 0]})
        self.vis.take_candidate(2, 3, 0, {1: [10, 0]})
        self.vis.update_candidate(1, 10, 0, 7, 2, {1: [7, 2]})
        self.vis.running_to_section = True
        self.vis.take_candidate(1, 7, 2, {})
        self.assertFalse(self.vis.running_to_section)
        self.assertIsNone(self.vis.motion)
        self.assertIsNone(self.vis.value_change)
        self.assertEqual(self.vis.distances[1], 7)

    def test_bottom_hover_selects_path_and_leaving_clears_it(self):
        from pyvisalgo.core import colors
        self.run_events()
        self.vis.draw()
        saved = dict(self.vis.messages)
        cx, cy = self.vis._inland_position(self.vis.inland.index(3))
        # 마우스 이벤트는 화면 좌표로 전달합니다. 거리 숫자 위에 올립니다.
        self.vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION,
                              pos=self.vis.view.point(cx, cy + 29), rel=(0, 0), buttons=(0, 0, 0)))
        self.assertEqual(self.vis._hovered_path(), [0, 2, 1, 3])
        self.assertTrue(self.vis._highlight(0, 2))
        self.assertFalse(self.vis._highlight(2, 3))
        self.assertEqual(self.vis._edge_color(0, 2), colors.YELLOW)
        self.vis.draw()
        self.assertEqual(self.vis.messages, saved)
        self.vis._toggle_explanation()
        self.vis.draw()
        self.assertEqual(self.vis._hovered_path(), [0, 2, 1, 3])
        self.vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION,
                              pos=self.vis.view.point(1560, 700), rel=(0, 0), buttons=(0, 0, 0)))
        self.assertEqual(self.vis._hovered_path(), [])
        self.vis.draw()

    def test_negative_weight_is_rejected_and_zero_is_allowed(self):
        with self.assertRaisesRegex(ValueError, "음수"):
            self.vis.setup(SimpleNamespace(vertices=["A", "B"], edges=[[0, 1, -1]]))
        self.vis.setup(SimpleNamespace(vertices=["A", "B"], edges=[[0, 1, 0]]))
        self.confirm_start()
        self.vis.add_candidate(1, 0, 0, {1: [0, 0]})
        self.vis.take_candidate(1, 0, 0, {})
        self.assertEqual(self.vis.distances, {0: 0, 1: 0})


if __name__ == "__main__":
    unittest.main()
