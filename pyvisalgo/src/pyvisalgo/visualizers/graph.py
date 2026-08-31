import math

import pygame

from pyvisalgo.core import colors
from pyvisalgo.core.visualizer import BaseVisualizer


class GraphVisualizer(BaseVisualizer):
    def __init__(self, title="Graph", **kwargs):
        super().__init__(title, **kwargs)
        self.set_message_layout("side")
        self.vertices = []
        self.edges = []
        self.edge_states = {}
        self.edge_labels = {}
        self.vertex_states = {}
        self.vertex_radius = 28

    def setup(self, data):
        self.set_data_info(data)
        self.data = data
        self.vertices = self._normalize_vertices(getattr(data, "vertices", []))
        self.edges = [tuple(edge) for edge in getattr(data, "edges", [])]
        self.edge_states = {}
        self.edge_labels = {}
        self.vertex_states = {}

    def set_vertex_state(self, vertex, state):
        if state is None:
            self.vertex_states.pop(vertex, None)
        else:
            self.vertex_states[vertex] = state

    def set_edge_state(self, u, v, state):
        key = self._edge_key(u, v)
        if state is None:
            self.edge_states.pop(key, None)
        else:
            self.edge_states[key] = state

    def set_edge_label(self, u, v, label, color=None):
        key = self._edge_key(u, v)
        if label is None:
            self.edge_labels.pop(key, None)
        else:
            self.edge_labels[key] = (str(label), color or colors.TEXT)

    def draw_content(self):
        self.text(self.title, 24, 18, 42, colors.TEXT, True)
        self._draw_edges()
        self._draw_vertices()

    def _normalize_vertices(self, vertices):
        if not vertices:
            return []

        normalized = []
        count = len(vertices)
        has_all_coords = all(isinstance(vertex, dict) and "x" in vertex and "y" in vertex for vertex in vertices)
        for index, vertex in enumerate(vertices):
            if isinstance(vertex, dict):
                label = vertex.get("name", vertex.get("label", str(index)))
                x = vertex.get("x")
                y = vertex.get("y")
            else:
                label = str(vertex)
                x = None
                y = None

            if x is None or y is None:
                left, top, right, bottom = self._graph_bounds()
                center_x = (left + right) / 2
                center_y = (top + bottom) / 2
                radius_x = (right - left) * 0.42
                radius_y = (bottom - top) * 0.42
                angle = -math.pi / 2 + 2 * math.pi * index / count
                x = center_x + radius_x * math.cos(angle)
                y = center_y + radius_y * math.sin(angle)
            normalized.append({"name": label, "x": float(x), "y": float(y)})

        if has_all_coords:
            self._fit_vertices(normalized)
        return normalized

    def _fit_vertices(self, vertices):
        left, top, right, bottom = self._graph_bounds()
        min_x = min(vertex["x"] for vertex in vertices)
        max_x = max(vertex["x"] for vertex in vertices)
        min_y = min(vertex["y"] for vertex in vertices)
        max_y = max(vertex["y"] for vertex in vertices)
        width = max_x - min_x
        height = max_y - min_y
        if width <= 0 or height <= 0:
            return

        scale = min((right - left) / width, (bottom - top) / height)
        graph_width = width * scale
        graph_height = height * scale
        offset_x = left + (right - left - graph_width) / 2
        offset_y = top + (bottom - top - graph_height) / 2

        for vertex in vertices:
            vertex["x"] = offset_x + (vertex["x"] - min_x) * scale
            vertex["y"] = offset_y + (vertex["y"] - min_y) * scale

    def _graph_bounds(self):
        if self.message_layout == "side":
            return 70, 125, 1065, 665
        return 220, 170, 1380, 545

    def _draw_edges(self):
        for u, v in self.edges:
            state = self.edge_states.get(self._edge_key(u, v), "normal")
            color = {
                "candidate": colors.YELLOW,
                "removed": colors.BORDER,
                "used": colors.RED,
                "dfs": colors.ORANGE,
                "blocked": colors.RED,
            }.get(state, colors.GREEN)
            width = 5 if state in ("used", "dfs") else 3
            self._draw_edge(u, v, color, width)
            self._draw_edge_label(u, v)

    def _draw_vertices(self):
        for index, vertex in enumerate(self.vertices):
            state = self.vertex_states.get(index, "normal")
            fill = {
                "current": (82, 55, 30),
                "candidate": (78, 68, 28),
                "visited": (35, 72, 52),
                "finished": (38, 71, 105),
            }.get(state, colors.PANEL)
            border = {
                "current": colors.ORANGE,
                "candidate": colors.YELLOW,
                "visited": colors.GREEN,
                "finished": colors.BLUE,
            }.get(state, colors.BORDER)
            point = self.view.point(vertex["x"], vertex["y"])
            pygame.draw.circle(self.screen, fill, point, self.view.length(self.vertex_radius))
            pygame.draw.circle(self.screen, border, point, self.view.length(self.vertex_radius), self.view.length(3))
            self.centered_text(index, vertex["x"], vertex["y"], 24, colors.TEXT, True)
            self.centered_text(vertex["name"], vertex["x"], vertex["y"] + 42, 18, colors.TEXT_MUTED)

    def _draw_edge(self, u, v, color, width):
        start = self.vertices[u]
        end = self.vertices[v]
        pygame.draw.line(
            self.screen,
            color,
            self.view.point(start["x"], start["y"]),
            self.view.point(end["x"], end["y"]),
            self.view.length(width),
        )

    def _draw_edge_label(self, u, v):
        label = self.edge_labels.get(self._edge_key(u, v))
        if label is None:
            return

        start = self.vertices[u]
        end = self.vertices[v]
        mid_x = (start["x"] + end["x"]) / 2
        mid_y = (start["y"] + end["y"]) / 2
        text, color = label
        radius = 24
        pygame.draw.circle(self.screen, colors.PANEL_DARK, self.view.point(mid_x, mid_y), self.view.length(radius))
        pygame.draw.circle(self.screen, color, self.view.point(mid_x, mid_y), self.view.length(radius), self.view.length(3))
        self.centered_text(text, mid_x, mid_y, 22, color, True)

    def _edge_key(self, u, v):
        return tuple(sorted((u, v)))
