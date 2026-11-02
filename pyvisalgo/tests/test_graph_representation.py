import copy
import json
import os
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pyvisalgo.core.data import Data
from pyvisalgo.visualizers.graph_representation import (
    GraphRepresentationVisualizer,
    graph_representations,
    normalize_edges,
)


class GraphDataTests(unittest.TestCase):
    def test_round_trip_preserves_zero_and_isolated_vertex(self):
        edges = [(0, 1, 0), (1, 2, 7)]
        forms = graph_representations(4, edges)
        for mode, form in zip(("edge_list", "adj_matrix", "adj_list"), forms):
            original = copy.deepcopy(form)
            self.assertEqual(normalize_edges(4, form, mode), edges)
            self.assertEqual(form, original)
        self.assertEqual(forms[1][0][1], 0)
        self.assertIsNone(forms[1][3][0])
        self.assertEqual(forms[2][3], {})

    def test_partial_matrix_can_be_shown(self):
        matrix = [[None, 7], [None, None]]
        self.assertEqual(normalize_edges(2, matrix, "adj_matrix"), [(0, 1, 7)])

    def test_invalid_graph_is_rejected(self):
        for edges in ([(0, 2, 1)], [(0, 0, 1)], [(0, 1, 2), (1, 0, 3)],
                      [(0, 1, float("nan"))]):
            with self.assertRaises(ValueError):
                normalize_edges(2, edges, "edge_list")
        with self.assertRaises(ValueError):
            normalize_edges(2, [[None]], "adj_matrix")
        with self.assertRaises(ValueError):
            normalize_edges(2, {0: {}}, "adj_list")


class GraphDrawingTests(unittest.TestCase):
    def setUp(self):
        self.vis = GraphRepresentationVisualizer(config_path="/tmp/graph-representation-test.json")
        self.vis.font_scale = 1
        path = Path(__file__).resolve().parent / "fixtures/graph_representation.json"
        self.datasets = json.loads(path.read_text())["datasets"]

    def tearDown(self):
        pygame.quit()

    def test_all_datasets_modes_and_window_sizes(self):
        for dataset in self.datasets:
            data = Data(**copy.deepcopy(dataset["data"]))
            original = copy.deepcopy(data.__dict__)
            self.vis.setup(data)
            for size in ((1600, 900), (960, 640)):
                self.vis.screen = pygame.display.set_mode(size)
                self.vis.view.resize(*size)
                for mode in ("edge_list", "adj_matrix", "adj_list"):
                    self.vis.set_representation(mode)
                    self.vis.draw()
                    self.assertGreater(len(self.vis.hits), 3)
            self.assertEqual(data.__dict__, original)

    def test_layout_and_restart_do_not_change_graph(self):
        data = Data(**self.datasets[0]["data"])
        self.vis.setup(data)
        original = copy.deepcopy((self.vis.edges, self.vis.forms))
        self.vis._handle_key(pygame.K_l)
        self.vis.running_to_section = True
        self.vis.draw()
        self.assertEqual(self.vis.positions, self.vis.layouts[1])
        self.assertEqual((self.vis.edges, self.vis.forms), original)
        self.vis.active = (0, 1)
        self.vis.selected_vertex = 2
        self.vis.setup(data)
        self.assertIsNone(self.vis.active)
        self.assertIsNone(self.vis.selected_vertex)
        self.assertIsNone(self.vis.layout_motion)

    def test_fit_button_uses_current_positions(self):
        self.vis.setup(Data(**self.datasets[0]["data"]))
        original_scale = self.vis.scale
        self.vis.positions = [(x * .5, y * .5) for x, y in self.vis.positions]
        self.vis.scale *= 3
        self.vis.plane_zoom = 3
        self.vis.origin_x += 200
        x, y, w, h = self.vis.fit_button
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                   pos=self.vis.view.point(x + w / 2, y + h / 2))
        self.vis.handle_event(event)
        self.assertAlmostEqual(self.vis.scale, original_scale * 2)
        self.assertEqual(self.vis.plane_zoom, 1)
        left, top, width, height = self.vis.plane_rect
        for i in range(len(self.vis.positions)):
            x, y = self.vis._screen_point(i)
            self.assertTrue(left + 20 <= x <= left + width - 20)
            self.assertTrue(top + 20 <= y <= top + height - 20)

    def test_h_expands_graph_and_restores_layout(self):
        self.vis.setup(Data(**self.datasets[0]["data"]))
        rect = self.vis.plane_rect
        positions = copy.deepcopy(self.vis.positions)
        before = self.vis._screen_point(0)
        self.vis._handle_key(pygame.K_h)
        self.assertTrue(self.vis.hidden)
        self.assertGreater(self.vis.plane_rect[3], rect[3])
        self.assertLess(self.vis.plane_rect[1], rect[1])
        self.assertNotEqual(self.vis._screen_point(0), before)
        self.vis.draw()
        self.assertEqual(self.vis.positions, positions)
        self.vis._handle_key(pygame.K_h)
        self.assertFalse(self.vis.hidden)
        self.assertEqual(self.vis.plane_rect, rect)
        for a, b in zip(self.vis._screen_point(0), before):
            self.assertAlmostEqual(a, b)


if __name__ == "__main__":
    unittest.main()
