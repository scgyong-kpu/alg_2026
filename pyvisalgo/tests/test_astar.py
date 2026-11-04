"""A* 전용 표시와 부모 시각화 재사용을 검사한다."""

import copy
import json
import os
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.visualizers.astar import AStarVisualizer
from pyvisalgo.visualizers.dijkstra import DijkstraVisualizer


class AStarDrawingTests(unittest.TestCase):
    def setUp(self):
        self.vis = AStarVisualizer(width=1280, height=720, config_path="/tmp/astar-test.json")
        self.vis.font_scale = 1
        self.vis.speed = 999999
        self.data = SimpleNamespace(vertices=list("ABCD"), edges=[[0, 1, 10], [0, 2, 3], [2, 1, 4], [1, 3, 5]],
                                    positions=[[0, 0], [400, 150], [250, -150], [800, 0]])
        self.h = [10, 5, 7, 0]
        self.vis.setup(self.data, 0, 3, self.h)
        self.messages = []

        def draw(*args):
            self.vis.draw()
            self.messages.append(dict(self.vis.messages))
            text = " ".join(self.vis.messages.values())
            for unwanted in ["Prim:", "Dijkstra:", "MST", "내륙"]:
                self.assertNotIn(unwanted, text)

        self.vis.wait = draw

    def tearDown(self):
        pygame.quit()

    def events(self):
        v = self.vis
        self.assertIsInstance(v, DijkstraVisualizer)
        v.add_candidate(0, 0, 0, {0: [10, 0, 0]}, starting=True)
        v.take_candidate(0, 0, 0, {})
        weights = {1: [15, 10, 0], 2: [10, 3, 0]}
        v.add_candidate(1, 10, 0, {1: weights[1]})
        v.add_candidate(2, 3, 0, weights)
        self.assertEqual(v.heap[0], (10, 2, 0))
        del weights[2]
        v.take_candidate(2, 3, 0, weights)
        v.show_neighbors(2, {0: 3, 1: 4})
        v.inspect_edge(2, 0, 3)
        v.ignore_inland(2, 0)
        v.inspect_edge(2, 1, 4)
        weights[1] = [12, 7, 2]
        original = copy.deepcopy(weights)
        v.update_candidate(1, 10, 0, 7, 2, weights)
        self.assertEqual(weights, original)
        self.assertEqual(v.heap, [(12, 1, 2)])
        v.keep_candidate(1, 7, 2, 10, 0)
        v.take_candidate(1, 7, 2, {})
        v.add_candidate(3, 12, 1, {3: [12, 12, 1]})
        v.take_candidate(3, 12, 1, {})
        v.finish_search()

    def test_priority_cost_and_final_path(self):
        self.events()
        self.assertEqual(self.vis.distances, {0: 0, 2: 3, 1: 7, 3: 12})
        self.assertEqual(self.vis.final_path, [0, 2, 1, 3])
        self.assertTrue(self.vis.found)
        self.assertTrue(any("g 3 + h 7 = f 10" in m["action"] for m in self.messages))

    def test_animation_and_fast_forward(self):
        self.vis.speed = 1
        self.events()
        self.vis.setup(self.data, 0, 3, self.h)
        self.vis.running_to_section = True
        self.vis.add_candidate(0, 0, 0, {0: [10, 0, 0]}, starting=True)
        self.assertFalse(self.vis.running_to_section)
        self.assertIsNone(self.vis.motion)
        self.assertIsNone(self.vis.value_change)

    def test_hover_hidden_resize_and_mode_restart(self):
        self.events()
        for width, height in [(1280, 720), (1600, 900)]:
            self.vis.screen = pygame.display.set_mode((width, height))
            self.vis.view.resize(width, height)
            self.vis.draw()
            cx, cy = self.vis._inland_position(self.vis.inland.index(1))
            self.vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=self.vis.view.point(cx, cy + 29),
                                                   rel=(0, 0), buttons=(0, 0, 0)))
            self.assertEqual(self.vis._hovered_path(), [0, 2, 1])
            self.vis._toggle_explanation()
            self.vis.draw()
            self.vis._toggle_explanation()
        self.vis._handle_key(pygame.K_a)
        self.assertFalse(self.vis.use_heuristic)
        self.assertEqual(self.vis.requested_action, "restart")
        self.vis.requested_action = None
        self.vis.setup(self.data, 0, 3, [0] * 4)
        self.assertEqual(self.vis.distances, {})
        self.assertEqual(self.vis.final_path, [])
        self.assertFalse(self.vis.finished)
        self.assertFalse(self.vis.use_heuristic)

    def test_early_finish_does_not_mark_unvisited_unreachable(self):
        self.vis.add_candidate(0, 0, 0, {0: [10, 0, 0]}, starting=True)
        self.vis.take_candidate(0, 0, 0, {})
        self.vis.finish_search()
        self.assertFalse(self.vis.found)
        self.assertEqual(self.vis.distances, {0: 0})
        self.assertNotIn("∞", " ".join(self.vis.messages.values()))

    def test_goal_finish_preserves_pending_candidates(self):
        self.vis.add_candidate(0, 0, 0, {0: [10, 0, 0]}, starting=True)
        self.vis.take_candidate(0, 0, 0, {})
        self.vis.add_candidate(2, 3, 0, {2: [10, 3, 0]})
        self.vis.take_candidate(2, 3, 0, {})
        self.vis.add_candidate(1, 7, 2, {1: [12, 7, 2]})
        self.vis.take_candidate(1, 7, 2, {})
        self.vis.add_candidate(3, 12, 1, {3: [12, 12, 1]})
        self.vis.take_candidate(3, 12, 1, {})
        self.vis.finish_search()
        self.assertTrue(self.vis.found)
        self.assertIn("아직 탐색하지 않은", self.vis.messages["detail"])
        self.assertEqual(self.vis.comparison_runs[self.vis.comparison_key][True], 4)
        # 같은 문제의 다른 모드 결과는 재실행 뒤에도 비교 표에 남습니다.
        self.vis.use_heuristic = False
        self.vis.setup(self.data, 0, 3, [0] * 4)
        self.assertEqual(self.vis.comparison_runs[self.vis.comparison_key][True], 4)

    def test_grid_map_bounds_path_hover_and_pan_only_layout(self):
        root = Path(__file__).resolve().parents[2]
        source = root / "src/w09_ch4_greedy/ch4_4_astar.py"
        entries = json.loads((source.parent / "data/ch4_4_astar.json").read_text())["datasets"]
        data = SimpleNamespace(**next(e["data"] for e in entries if "grid" in e["data"]))
        ns = runpy.run_path(str(source))
        h = ns["straight_line_heuristics"](data.coordinates, data.goal)
        self.vis.setup(data, data.start, data.goal, h)
        ns["astar"].__globals__["vis"] = self.vis
        path, cost = ns["astar"](len(data.vertices), data.edges, data.start, data.goal, h)
        self.vis.finish_search()
        self.assertEqual(path, self.vis.final_path)
        self.assertEqual(cost, 140)
        original = list(self.vis.positions)
        self.vis._handle_key(pygame.K_l)
        self.assertEqual(self.vis.positions, original)
        for hidden in [False, True]:
            if hidden:
                self.vis._toggle_explanation()
            self.vis.draw()
            half = self.vis.grid["step_cost"] * self.vis.scale / 2
            left, top, width, height = self.vis.plane_rect
            for x, y in [self.vis._grid_point(0, 0), self.vis._grid_point(8, 5)]:
                self.assertGreaterEqual(x - half, left)
                self.assertLessEqual(x + half, left + width)
                self.assertGreaterEqual(y - half, top)
                self.assertLessEqual(y + half, top + height)
            index = self.vis.inland.index(path[3])
            cx, cy = self.vis._inland_position(index)
            self.vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=self.vis.view.point(cx, cy),
                                                   rel=(0, 0), buttons=(0, 0, 0)))
            self.assertEqual(self.vis._hovered_path(), path[:4])

    def test_numeric_map_tiles_and_code_toggle(self):
        root = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy"
        convert = runpy.run_path(str(root / "data_map.py"))["map_to_graph"]
        entries = json.loads((root / "data/ch4_4_astar.json").read_text())["datasets"]
        d = next(e["data"] for e in entries if e["name"].startswith("숫자 맵:"))
        data = convert(SimpleNamespace(**d))
        ns = runpy.run_path(str(root / "ch4_4_astar.py"))
        h = ns["straight_line_heuristics"](data.coordinates, data.goal)
        self.vis.setup(data, data.start, data.goal, h)
        ns["astar"].__globals__["vis"] = self.vis
        path, cost = ns["astar"](len(data.vertices), data.edges, data.start, data.goal, h)
        self.vis.finish_search()
        self.vis.draw()
        self.assertEqual(set(self.vis.tile_images), {1, 2, 3, 4, 11, 12, 13, 14})
        pictures = pygame.image.tobytes(self.vis.screen, "RGB")
        self.vis._handle_key(pygame.K_m)
        self.vis.draw()
        self.assertTrue(self.vis.show_map_details)
        self.assertNotEqual(pictures, pygame.image.tobytes(self.vis.screen, "RGB"))
        self.assertEqual(self.vis.final_path, path)
        self.assertEqual(self.vis.distances[data.goal], cost)
        self.assertEqual(self.vis.requested_action, None)
        self.vis._toggle_explanation()
        self.vis.draw()

    def test_cell_scores_record_update_reset_and_toggle(self):
        self.events()
        self.assertEqual(self.vis._cell_scores(1), (7, 5, 12))
        self.assertEqual(self.vis._cell_scores(3), (12, 0, 12))
        self.vis.value_change = {"vertex": 1, "old_cost": 15, "cost": 12, "progress": .25}
        self.assertEqual(self.vis._cell_scores(1), (10, 5, 15))
        self.vis.value_change["progress"] = .75
        self.assertEqual(self.vis._cell_scores(1), (7, 5, 12))
        self.vis.value_change = None
        # 격자 데이터에서만 M을 처리합니다. 번호와 점수는 함께 켜고 끕니다.
        self.vis.grid = {"rows": ["...."], "cells": [[0, 0], [1, 0], [2, 0], [3, 0]], "step_cost": 10}
        old_path = list(self.vis.final_path)
        self.assertFalse(self.vis.show_map_details)
        self.vis._handle_key(pygame.K_m)
        self.assertTrue(self.vis.show_map_details)
        self.assertEqual(self.vis.final_path, old_path)
        self.assertIsNone(self.vis.requested_action)
        self.vis._handle_key(pygame.K_m)
        self.assertFalse(self.vis.show_map_details)
        self.vis.setup(self.data, 0, 3, self.h)
        self.assertEqual(self.vis.scores, {})
        self.assertIsNone(self.vis._cell_scores(2))

    def test_cell_corner_labels_stay_in_separate_quadrants(self):
        from pyvisalgo.core import colors
        for side in [30, 80]:
            boxes = [self.vis._draw_cell_corner(label, colors.TEXT, 300, 300, side, corner)
                     for label, corner in [("#123", "topleft"), ("g150", "topright"),
                                           ("h70", "bottomleft"), ("f220", "bottomright")]]
            center = self.vis.view.point(300, 300)
            self.assertLess(boxes[0].right, center[0])
            self.assertGreater(boxes[1].left, center[0])
            self.assertLess(boxes[0].bottom, center[1])
            self.assertGreater(boxes[2].top, center[1])
            for i, box in enumerate(boxes):
                for other in boxes[i + 1:]:
                    self.assertFalse(box.colliderect(other))

    def test_tentative_path_follows_best_open_candidate_and_updates(self):
        v = self.vis
        v.add_candidate(0, 0, 0, {0: [10, 0, 0]}, starting=True)
        v.take_candidate(0, 0, 0, {})
        weights = {1: [15, 10, 0], 2: [10, 3, 0]}
        v.add_candidate(1, 10, 0, {1: weights[1]})
        v.add_candidate(2, 3, 0, weights)
        self.assertEqual(v.tentative_path(), [0, 2])
        v.take_candidate(2, 3, 0, {1: [15, 10, 0]})
        self.assertEqual(v.tentative_path(), [0, 1])
        v.update_candidate(1, 10, 0, 7, 2, {1: [12, 7, 2]})
        self.assertEqual(v.tentative_path(), [0, 2, 1])
        self.assertEqual(v._visible_tentative_path(), [0, 2, 1])
        v.show_map_details = True
        self.assertEqual(v._visible_tentative_path(), [])
        v.show_map_details = False
        v.hovered = ("vertex", 2)
        self.assertEqual(v._visible_tentative_path(), [])
        v.hovered = None
        v.finished = True
        self.assertEqual(v._visible_tentative_path(), [])
        v.setup(self.data, 0, 3, self.h)
        self.assertEqual(v.tentative_path(), [])
        self.assertEqual(v.candidate_origins, {})


if __name__ == "__main__":
    unittest.main()
