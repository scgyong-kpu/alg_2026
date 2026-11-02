"""완성된 Kruskal 학생 코드와 시각화 연결의 통합 검사."""

import contextlib
import io
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import pyvisalgo as va
from pyvisalgo.core.visualizer import BaseVisualizer


SOURCE = Path(__file__).resolve().parents[2] / "src/w09_ch4_greedy/ch4_1_mst_kruskal.py"


class KruskalStudentTests(unittest.TestCase):
    def setUp(self):
        self.functions = runpy.run_path(str(SOURCE))
        self.kruskal = self.functions["kruskal"]
        self.vis = Mock()
        self.vis.stopped.return_value = False
        self.kruskal.__globals__["vis"] = self.vis

    def test_all_datasets_and_original_preservation(self):
        path = SOURCE.parent / "data/ch4_1_mst_kruskal.json"
        datasets = json.loads(path.read_text())["datasets"]
        for entry, expected in zip(datasets, (25, 32, 1809, 2224, 2556)):
            with self.subTest(dataset=entry["name"]):
                data = entry["data"]
                original = [edge[:] for edge in data["edges"]]
                mst, cost = self.kruskal(len(data["vertices"]), data["edges"])
                self.assertEqual(cost, expected)
                self.assertEqual(len(mst), len(data["vertices"]) - 1)
                self.assertEqual(data["edges"], original)

    def test_cycle_rejection_early_stop_and_selection_before_union(self):
        edges = [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (0, 3, 9)]
        self.assertEqual(self.kruskal(4, edges), ([(0, 1, 1), (1, 2, 2), (2, 3, 4)], 7))
        self.vis.reject_edge.assert_called_once_with(0, 2, 3)
        self.assertEqual(self.vis.check_roots.call_count, 4)
        events = [call[0] for call in self.vis.method_calls if call[0] in ("select_edge", "union_roots")]
        self.assertEqual(events, ["select_edge", "union_roots"] * 3)

    def test_disconnected_graph_zero_weight_and_single_vertex(self):
        self.assertEqual(self.kruskal(4, [(0, 1, 0), (2, 3, 2)]), ([(0, 1, 0), (2, 3, 2)], 2))
        self.assertEqual(self.kruskal(1, []), ([], 0))
        self.assertEqual(self.kruskal.__globals__["roots"], [0])

    def test_shortcut_reduces_next_search_without_changing_root(self):
        roots = [0, 0, 1, 2]
        get_root = self.functions["getRoot"]
        get_root.__globals__["roots"] = roots
        self.assertEqual(get_root(3), 0)
        self.assertEqual(roots, [0, 0, 0, 0])
        self.assertEqual(self.vis.root_enter.call_count, 4)
        self.vis.reset_mock()
        self.assertEqual(get_root(3), 0)
        self.assertEqual(self.vis.root_enter.call_count, 2)

    def test_main_distinguishes_mst_and_forest(self):
        for count, edges, expected in (
            (3, [[0, 1, 1], [1, 2, 2]], "최소 신장 트리 비용: 3"),
            (4, [[0, 1, 1], [2, 3, 2]], "최소 신장 숲 비용: 3"),
        ):
            with self.subTest(count=count):
                data = SimpleNamespace(vertices=list(map(str, range(count))), edges=edges)
                output = io.StringIO()
                with patch.object(va, "running", side_effect=[True, False]), \
                        patch.object(va, "next_data", return_value=data), \
                        patch.object(BaseVisualizer, "wait", lambda vis, *args: vis.draw()), \
                        patch.object(BaseVisualizer, "is_max_speed", return_value=True), \
                        contextlib.redirect_stdout(output):
                    runpy.run_path(str(SOURCE), run_name="__main__")
                self.assertIn(expected, output.getvalue())


if __name__ == "__main__":
    unittest.main()
