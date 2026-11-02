"""크루스칼 학생 코드와 선택/제외 시각화의 회귀 검사."""

import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pyvisalgo as va
from pyvisalgo.core import colors


class KruskalTests(unittest.TestCase):
    def test_recursive_return_without_shortcut_keeps_roots(self):
        roots = [0, 0, 1, 2]
        vis = va.visualizer("kruskal")
        vis.setup(SimpleNamespace(vertices=list("ABCD"), edges=[]), roots)
        vis.wait = lambda *args: vis.draw()
        for vertex in (3, 2, 1, 0):
            vis.root_enter(vertex, roots)
        vis.root_return(0, 0, roots, is_root=True)
        for vertex in (1, 2, 3):
            vis.root_return(vertex, 0, roots, shortcut=False)
            self.assertIn("반환", vis.messages["action"])
            self.assertIn("바꾸지 않는다", vis.messages["detail"])
        self.assertEqual(vis.root_values, [0, 0, 1, 2])
        self.assertEqual(roots, [0, 0, 1, 2])
        self.assertFalse(vis.root_stack)

    def test_shortcut_return_highlights_only_changed_values(self):
        roots = [0, 0, 1, 2]
        vis = va.visualizer("kruskal")
        vis.setup(SimpleNamespace(vertices=list("ABCD"), edges=[]), roots)
        vis.wait = lambda *args: vis.draw()
        for vertex in (3, 2, 1, 0):
            vis.root_enter(vertex, roots)
        vis.root_return(0, 0, roots, is_root=True)
        for vertex in (1, 2, 3):
            roots[vertex] = 0
            vis.root_return(vertex, 0, roots)
            self.assertEqual(vis.root_changed, set() if vertex == 1 else {vertex})
        self.assertEqual(vis.root_values, [0, 0, 0, 0])
        self.assertFalse(vis.root_stack)



    def test_enter_does_not_leave_persistent_progress_log(self):
        vis = va.visualizer("kruskal")
        vis.setup(SimpleNamespace(vertices=list("AB"), edges=[[0, 1, 1]]))
        vis._run_to_section()
        self.assertTrue(vis.running_to_section)
        self.assertNotIn("다음 구간까지 진행", vis.log_lines)

    def test_union_shows_before_and_after_selected_edge(self):
        vis = va.visualizer("kruskal")
        vis.setup(SimpleNamespace(vertices=list("AB"), edges=[[0, 1, 1]]), [0, 1])
        vis.selected_edges.add((0, 1))
        snapshots = []

        def render(*args):
            vis.draw()
            snapshots.append((list(vis.root_values), vis.union_change, set(vis.selected_edges)))

        vis.wait = render
        vis.union_roots(0, 1, [0, 0])
        self.assertEqual(snapshots[0], ([0, 1], (1, 1, 0, False), {(0, 1)}))
        self.assertEqual(snapshots[1], ([0, 0], (1, 1, 0, True), {(0, 1)}))
        self.assertEqual(vis.root_changed, {1})
        vis.section_end()
        self.assertFalse(vis.running_to_section)
        self.assertNotIn("다음 구간까지 진행", vis.log_lines)


    def test_collecting_blue_edges_leaves_gray_originals(self):
        data = SimpleNamespace(vertices=list("ABC"), edges=[[0, 1, 1], [1, 2, 2]])
        vis = va.visualizer("kruskal")
        vis.setup(data)
        self.assertEqual(vis._edge_color(0, 1), colors.BLUE)
        self.assertEqual(vis._edge_color(1, 2), colors.BLUE)
        vis.edge_motion = (0, .5)
        self.assertEqual(vis._edge_color(0, 1), colors.BORDER)
        self.assertEqual(vis._edge_color(1, 2), colors.BLUE)
        vis.collected = 1
        vis.edge_motion = None
        self.assertEqual(vis._edge_color(0, 1), colors.BORDER)
        vis.draw()
        vis.collected = 2
        vis.collection_finished = True
        self.assertEqual(vis._edge_color(1, 2), colors.BORDER)
        vis.setup(data)
        self.assertEqual(vis._edge_color(0, 1), colors.BLUE)


    def test_city_hover_distinguishes_target_and_root_without_compression(self):
        data = SimpleNamespace(vertices=list("ABCD"), edges=[[0, 1, 1], [1, 2, 2], [2, 3, 3]])
        roots = [0, 0, 1, 2]
        vis = va.visualizer("kruskal")
        vis.setup(data, roots)

        def hover(vertex):
            pos = vis.view.point(*vis._screen_point(vertex))
            vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, buttons=(0, 0, 0)))
            vis.draw()

        hover(3)
        self.assertEqual(vis.hovered_city, 3)
        self.assertEqual(vis._hovered_root(), 0)
        self.assertEqual(vis.root_values, roots)
        self.assertEqual(roots, [0, 0, 1, 2])
        hover(0)
        self.assertEqual(vis._hovered_root(), vis.hovered_city)
        x, y = vis._screen_point(0)
        self.assertEqual(tuple(vis.screen.get_at(vis.view.point(x - 14, y)))[:3], colors.ORANGE)
        # 창 배율에 따른 반올림 오차를 고려해 테두리 주변 픽셀을 검사합니다.
        ring_pixels = [tuple(vis.screen.get_at(vis.view.point(x + dx, y - radius)))[:3]
                       for dx in range(-2, 3) for radius in range(23, 28)]
        self.assertIn(colors.YELLOW, ring_pixels)
        vis.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=vis.view.point(10, 10), buttons=(0, 0, 0)))
        self.assertIsNone(vis.hovered_city)
        self.assertIsNone(vis._hovered_root())


    def test_hidden_explanation_expands_only_root_panel(self):
        vis = va.visualizer("kruskal")
        data = SimpleNamespace(vertices=[str(i) for i in range(18)], edges=[])
        vis.setup(data)
        vis.draw()
        self.assertEqual(vis.root_table_rows, 8)
        self.assertEqual(len(vis.hits), 8)
        vis._toggle_explanation()
        vis.draw()
        self.assertEqual(vis.root_table_rows, 18)
        self.assertEqual(len(vis.hits), 18)
        self.assertLess(max(rect[1] + rect[3] for rect, _ in vis.hits), 610)
        vis._toggle_explanation()
        vis.draw()
        self.assertEqual(vis.root_table_rows, 8)
        self.assertEqual(len(vis.hits), 8)
        self.assertEqual(vis.root_values, list(range(18)))


    def test_mst_progress_remains_visible_with_hidden_explanation(self):
        vis = va.visualizer("kruskal")
        vis.setup(SimpleNamespace(vertices=list("ABC"), edges=[[0, 1, 1], [1, 2, 2]]))
        original_text = vis.text
        labels = []

        def record(label, x, y, size, color=colors.TEXT, *args, **kwargs):
            if "선택한 간선" in str(label) and "|" in str(label):
                labels.append((label, x, y, color))
            original_text(label, x, y, size, color, *args, **kwargs)

        vis.text = record
        vis.draw()
        self.assertEqual(labels[-1][0], "정점 3개 | 선택한 간선 0 / 2개")
        vis.selected_edges = {(0, 1)}
        vis._toggle_explanation()
        vis.draw()
        self.assertEqual(labels[-1][0], "정점 3개 | 선택한 간선 1 / 2개")
        self.assertLess(labels[-1][1], vis.fit_button[0])
        self.assertLess(labels[-1][2], 70)
        vis.selected_edges.add((1, 2))
        vis.draw()
        self.assertEqual(labels[-1][0], "정점 3개 | 선택한 간선 2 / 2개")
        self.assertEqual(labels[-1][3], colors.GREEN)


if __name__ == "__main__":
    unittest.main()
