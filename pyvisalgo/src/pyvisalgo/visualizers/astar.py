"""Dijkstra의 후보 애니메이션을 재사용하는 목적지 기반 A* 시각화."""

import math
from pathlib import Path
from types import SimpleNamespace

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer
from .dijkstra import DijkstraVisualizer
from .plane import PlaneVisualizer


class AStarVisualizer(DijkstraVisualizer):
    algorithm_name = "A*"
    heading = "A*: Goal-Directed Search"
    description = "g: 지금까지의 실제 비용   h: 남은 비용 추정   f = g + h: 후보 선택 기준"
    panel_left = 1160
    panel_width = 360
    cost_heading = ""
    origin_heading = ""
    cost_offset = 64
    origin_offset = 294

    def __init__(self, *args, **kwargs):
        self.use_heuristic = True
        self.comparison_runs = {}
        self.show_map_details = False
        self.tile_images = {}
        self.tile_scaled = {}
        super().__init__(*args, **kwargs)

    def setup(self, data, start, goal, heuristics):
        self.grid = getattr(data, "grid", None)
        self.goal_vertex = goal
        self.heuristics = list(heuristics)
        self.final_path = []
        self.found = False
        self.focus_formula = None
        self.scores = {}
        self.candidate_origins = {}
        self.best_candidate = None
        self.comparison_key = (tuple(data.vertices), tuple(tuple(e) for e in data.edges), start, goal)
        if not 0 <= goal < len(data.vertices) or len(heuristics) != len(data.vertices):
            raise ValueError("목적지와 휴리스틱 배열의 크기를 확인하세요.")
        if any(not math.isfinite(h) or h < 0 for h in heuristics):
            raise ValueError("휴리스틱은 유한한 음수가 아닌 수여야 합니다.")
        super().setup(data, start)
        self.plane_rect = (45, 140, 1055, 325 if self.grid else 360)
        self.fit_button = (1054, 148, 32, 32)
        self.reset_plane()

    def _handle_key(self, key, mod=0):
        if key == pygame.K_m and self.grid:
            self.show_map_details = not self.show_map_details
            return
        if key == pygame.K_l and self.grid:
            return  # 격자와 벽은 하나의 지도이므로 정점만 따로 재배치하지 않습니다.
        if key == pygame.K_a:
            self.use_heuristic = not self.use_heuristic
            self.requested_action = "restart"
        else:
            super()._handle_key(key, mod)

    def _toggle_explanation(self):
        super()._toggle_explanation()
        self.plane_rect = (45, 25, 1055, 650) if self.hidden else (45, 140, 1055, 325 if self.grid else 360)
        self.fit_button = (1054, self.plane_rect[1] + 8, 32, 32)
        self.reset_plane()

    def _make_layouts(self, supplied):
        if self.grid:
            # 장애물의 칸 좌표와 정점 좌표를 같은 고정 좌표계에 둡니다.
            return [list(map(tuple, supplied)) for _ in range(3)]
        return super()._make_layouts(supplied)

    def _fit_positions(self, positions):
        if not self.grid:
            return super()._fit_positions(positions)
        # 정점 중심뿐 아니라 지도 바깥 테두리와 장애물 칸 전체를 포함합니다.
        step = self.grid["step_cost"]
        rows = self.grid["rows"]
        left, right = -step / 2, (len(rows[0]) - .5) * step
        top, bottom = step / 2, -(len(rows) - .5) * step
        self.fit_plane([SimpleNamespace(x=x, y=y) for x, y in
                        [(left, bottom), (right, top)]])

    def handle_event(self, event):
        if not self.grid:
            return super().handle_event(event)
        # 격자에서는 정점 이동 대신 지도를 통째로 pan/zoom합니다.
        if event.type == pygame.MOUSEWHEEL:
            x, _ = self._logical_mouse(pygame.mouse.get_pos())
            if x >= self.panel_left - 20:
                self.candidate_scroll = max(0, min(max(0, len(self.heap) - self.candidate_rows),
                                                  self.candidate_scroll - event.y))
                return
        PlaneVisualizer.handle_event(self, event)
        if event.type == pygame.MOUSEMOTION:
            point = self._logical_mouse(event.pos)
            self.hovered = next((target for rect, target in reversed(self.hits)
                                 if pygame.Rect(rect).collidepoint(point)), None)

    @property
    def inland_top(self):
        if self.grid:
            return 705 if self.hidden else 505
        return super().inland_top

    def _inland_position(self, index):
        if not self.grid:
            return super()._inland_position(index)
        columns = max(1, math.ceil(min(len(self.names), 32) / 2))
        step = min(64, 1000 / columns)
        index -= self._inland_offset()
        return 70 + (index % columns) * step, self.inland_top + 42 + (index // columns) * 54

    def _inland_offset(self):
        extra = int(self.motion is not None and self.motion["kind"] == "take")
        return max(0, len(self.inland) + extra - 32)

    def _running_hint(self):
        return "Space: 일시정지  .: 한 단계  Enter: 다음 동작  A: A*/h=0  M: 번호·g/h/f  H: 설명  D: 데이터  Esc: 종료"

    def _action_hint(self):
        if self.grid:
            return "R: 재실행  D: 다음 데이터  A: A*/h=0  M: 번호·g/h/f  H: 설명  Esc: 종료"
        return "R: 재실행  D: 다음 데이터  A: A*/h=0 전환  H: 설명  L: 배치  Esc: 종료"

    def _setup_messages(self, start):
        self.msg_phase("A*: 준비")
        self.msg_action(f"시작점 #{start}에서 목적지 #{self.goal_vertex}까지의 최단 경로를 구한다.")
        self.msg_detail("최소 f 후보로 목적지를 꺼낼 때 종료한다. 처음 발견했을 때 종료하지 않는다.")

    def _update_stats(self):
        self.msg_stats(f"탐색 {len(self.inland)}개 / 후보 {len(self.heap)}개")

    def _animate_heap(self, weights, vertex, kind):
        self.candidate_origins = {v: entry[2] for v, entry in weights.items()}
        # 표시용 heap의 동률 순서가 아니라 실제 후보의 [f, g, 이전 정점]을 비교합니다.
        self.best_candidate = min(weights, key=lambda v: weights[v]) if weights else None
        for key, (f, g, origin) in weights.items():
            self.scores[key] = (g, self.heuristics[key], f)
        # 실제 후보는 [f, g, 이전 정점]. 부모 애니메이션에는 [f, 이전 정점]을 전달한다.
        # self.heap은 표시용 배열이며 heapdict의 실제 내부 순서와는 독립적이다.
        super()._animate_heap({v: [f, origin] for v, (f, g, origin) in weights.items()}, vertex, kind)

    def _record_confirmation(self, vertex, cost, origin, total_cost):
        super()._record_confirmation(vertex, cost, origin, total_cost)
        h = self.heuristics[vertex]
        self.scores[vertex] = (cost, h, cost + h)

    def _formula(self, vertex, g):
        h = self.heuristics[vertex]
        return f"g {g:g} + h {h:g} = f {g + h:g}"

    def _added_messages(self, vertex, cost, origin, starting):
        self.focus_formula = (vertex, cost)
        self.msg_phase("A*: " + self.operation)
        self.msg_action(f"#{vertex}를 후보로 등록한다. " + self._formula(vertex, cost))
        self.msg_detail("시작점의 실제 비용 g는 0이다." if starting else
                        f"이전 정점은 #{origin}. 추정치 h는 후보 선택에만 쓰고 실제 경로 비용에 더하지 않는다.")

    def _taken_messages(self, vertex, cost, origin):
        self.focus_formula = (vertex, cost)
        self.operation = "최소 f 후보 꺼내기"
        self.msg_phase("A*: " + self.operation)
        self.msg_action(f"#{vertex}를 꺼낸다. " + self._formula(vertex, cost))
        self.msg_detail("목적지를 최소 f 후보로 꺼냈으므로 최단 경로를 완성한다." if vertex == self.goal_vertex else
                        "일관적인 휴리스틱을 사용하므로 꺼낸 정점의 g는 최단 거리이다.")

    def _inspection_messages(self, origin, vertex, distance):
        g = self.distances[origin] + distance
        self.focus_formula = (vertex, g)
        self.msg_phase("A*: 이웃 검사")
        self.msg_action(f"#{origin} → #{vertex}: 새 g = {self.distances[origin]:g} + {distance:g} = {g:g}")
        self.msg_detail(self._formula(vertex, g) + " / 후보 개선 여부는 f가 아니라 실제 비용 g로 비교한다.")

    def _neighbor_messages(self, vertex, neighbors):
        self.msg_phase("A*: 주변점 확인")
        self.msg_action(f"#{vertex}의 이웃 {len(neighbors)}개를 검사한다.")
        self.msg_detail("확정한 점: 무시 / 없거나 더 짧은 g: 등록·갱신 / 그 외: 유지")

    def _ignored_messages(self, vertex):
        self.operation = "이미 확정: 무시"
        self.msg_phase("A*: " + self.operation)
        self.msg_action(f"#{vertex}의 g는 이미 확정되었으므로 무시한다.")
        self.msg_detail("일관적인 휴리스틱을 전제로 닫힌 정점을 다시 열지 않는 버전이다.")

    def _comparison_messages(self, vertex, old_cost, old_origin, cost, origin):
        self.focus_formula = (vertex, cost)
        relation = "<" if cost < old_cost else "=" if cost == old_cost else ">"
        self.msg_phase("A*: 실제 비용 g 비교")
        self.msg_action(f"#{vertex}: 새 g {cost:g} {relation} 기존 g {old_cost:g}")
        self.msg_detail(self._formula(vertex, cost) + f" / 이전 정점 #{old_origin}와 새 경유점 #{origin}")

    def _updated_messages(self, vertex, old_cost, cost, origin):
        self.msg_phase("A*: 후보 갱신")
        self.msg_action(f"#{vertex}의 g를 {old_cost:g}에서 {cost:g}로, 이전 정점을 #{origin}로 바꾼다.")
        self.msg_detail(self._formula(vertex, cost) + " / 새 f에 맞춰 후보 heap의 위치도 바뀐다.")

    def _kept_messages(self, vertex, old_cost, old_origin, cost):
        self.msg_phase("A*: 기존 후보 유지")
        self.msg_action(f"새 g {cost:g}가 기존 g {old_cost:g}보다 작지 않아 유지한다.")
        self.msg_detail(f"#{vertex}의 기존 이전 정점 #{old_origin}도 유지한다.")

    def _animate_update_values(self, vertex, old_cost, old_origin, cost, origin):
        h = self.heuristics[vertex]
        super()._animate_update_values(vertex, old_cost + h, old_origin, cost + h, origin)

    def _draw_candidate_cell(self, entry, index, position, hot=False):
        f, vertex, origin = entry
        h = self.heuristics[vertex]
        x, y = position
        color = colors.ORANGE if hot else colors.BLUE
        changing = self.value_change is not None and self.value_change["vertex"] == vertex
        self.text(f"[{index}]", x - 36, y + 6, 14, colors.TEXT_MUTED)
        self.rect(x, y, self.panel_width, self.cell_height, colors.PANEL,
                  colors.GREEN if changing else color, radius=4)
        self.mono_text(f"#{vertex}", x + 10, y + 4, 18, color)
        self.mono_text(f"{h:g}", x + 140, y + 4, 18, colors.TEXT_MUTED)
        if changing:
            change = self.value_change
            self._draw_replaced_value(f"{change['old_cost'] - h:g}", f"{change['cost'] - h:g}", x + 64, y + 4, 72)
            self._draw_replaced_value(f"{change['old_cost']:g}", f"{change['cost']:g}", x + 210, y + 4, 76)
            self._draw_replaced_value(f"#{change['old_origin']}", f"#{change['origin']}", x + 294, y + 4, 60)
        else:
            for label, offset, tint in ((f"{f - h:g}", 64, colors.TEXT),
                                         (f"{f:g}", 210, colors.YELLOW),
                                         (f"#{origin}", 294, colors.TEXT_MUTED)):
                self.mono_text(label, x + offset, y + 4, 18, tint)

    def _draw_candidates(self):
        super()._draw_candidates()
        for label, offset in (("g", 64), ("h", 140), ("f", 210), ("이전", 294)):
            self.text(label, self.panel_left + offset, 110, 17, colors.TEXT_MUTED)
        # 후보 목록 아래의 여백을 사용하여 다음 선택 기준을 따로 표시한다.
        if not self.hidden and self.finished:
            results = self.comparison_runs.get(self.comparison_key, {})
            self.text("같은 시작점·목적지의 탐색 수", self.panel_left, 535, 19, colors.BLUE)
            for mode, label, y in ((True, "A*", 570), (False, "h=0", 600)):
                result = results.get(mode)
                text = f"{label}: {result}개" if result is not None else f"{label}: 아직 실행하지 않음"
                self.text(text, self.panel_left, y, 18, colors.TEXT)
        elif not self.hidden and self.focus_formula is not None:
            vertex, g = self.focus_formula
            self.text(f"#{vertex}의 후보 우선순위", self.panel_left, 535, 20, colors.BLUE)
            self._fit_text(self._formula(vertex, g), self.panel_left, 570, self.panel_width, 22)

    def _hovered_path(self):
        hovered = super()._hovered_path()
        return hovered or self.final_path

    def tentative_path(self):
        """현재 최소 f인 열린 후보까지 발견한 경로. 목적지 최단 경로의 확정은 아니다."""
        vertex = self.best_candidate
        path, seen = [], set()
        while vertex is not None and vertex not in seen:
            path.append(vertex)
            seen.add(vertex)
            if vertex == self.start_vertex:
                return path[::-1]
            if vertex in self.candidate_origins:
                vertex = self.candidate_origins[vertex]
            else:
                vertex = self.predecessors.get(vertex)
        return []

    def _visible_tentative_path(self):
        # 마우스로 지정한 확정 경로 및 종료 후 최종 경로는 실선으로 우선 표시합니다.
        if self.show_map_details or self.finished or super()._hovered_path():
            return []
        return self.tentative_path()

    def _draw_tentative_path(self):
        path = self._visible_tentative_path()
        for u, v in zip(path, path[1:]):
            a, b = pygame.Vector2(self._screen_point(u)), pygame.Vector2(self._screen_point(v))
            delta = b - a
            length = delta.length()
            if length == 0:
                continue
            direction = delta / length
            # 타일 그림 위에서도 보이도록 어두운 외곽선과 밝은 점선을 겹쳐 그립니다.
            for offset in range(0, math.ceil(length), 16):
                start = a + direction * offset
                end = a + direction * min(offset + 10, length)
                pygame.draw.line(self.screen, colors.BACKGROUND, self.view.point(*start),
                                 self.view.point(*end), self.view.length(8))
                pygame.draw.line(self.screen, colors.YELLOW, self.view.point(*start),
                                 self.view.point(*end), self.view.length(4))
        if path:
            pygame.draw.circle(self.screen, colors.YELLOW, self.view.point(*self._screen_point(path[-1])),
                               self.view.length(7), self.view.length(2))

    def _draw_graph(self):
        if self.grid:
            return self._draw_grid_graph()
        super()._draw_graph()
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        for vertex, label, color in ((self.start_vertex, "S", colors.YELLOW),
                                     (self.goal_vertex, "G", colors.ORANGE)):
            x, y = self._screen_point(vertex)
            pygame.draw.circle(self.screen, color, self.view.point(x, y), self.view.length(29), self.view.length(3))
            self.text(label, x - 36, y - 43, 19, color, bold=True)
        self.screen.set_clip(previous)

    def _grid_point(self, x, y):
        step = self.grid["step_cost"]
        return self.origin_x + (x * step - self.min_x) * self.scale, self.origin_y - (-y * step - self.min_y) * self.scale

    def _map_tile(self, code, size):
        if not self.tile_images:
            atlas = pygame.image.load(Path(__file__).resolve().parents[1] / "assets/map_tiles.png").convert()
            width, height = atlas.get_size()
            for index, value in enumerate((1, 2, 3, 4, 11, 12, 13, 14)):
                col, row = index % 4, index // 4
                left, right = round(col * width / 4), round((col + 1) * width / 4)
                top, bottom = round(row * height / 2), round((row + 1) * height / 2)
                self.tile_images[value] = atlas.subsurface((left, top, right - left, bottom - top)).copy()
        key = code, size
        if key not in self.tile_scaled:
            if len(self.tile_scaled) > 128:
                self.tile_scaled.clear()
            self.tile_scaled[key] = pygame.transform.smoothscale(self.tile_images[code], (size, size))
        return self.tile_scaled[key]

    def _draw_map_tile(self, code, x, y, side, tint=None):
        rect = pygame.Rect(self.view.rect(x - side / 2 + 1, y - side / 2 + 1, side - 2, side - 2))
        self.screen.blit(self._map_tile(code, max(1, rect.width)), rect.topleft)
        if tint is not None:
            layer = pygame.Surface(rect.size, pygame.SRCALPHA)
            layer.fill((*tint, 65))
            self.screen.blit(layer, rect.topleft)
        pygame.draw.rect(self.screen, tint or colors.BORDER, rect, self.view.length(1))

    def _cell_scores(self, vertex):
        if vertex not in self.scores:
            return None
        g, h, f = self.scores[vertex]
        if self.value_change is not None and self.value_change["vertex"] == vertex:
            change = self.value_change
            # 갱신 중에는 후보 목록의 값 교체 시점과 맞추어 새 g/f를 표시합니다.
            f = change["cost"] if change["progress"] >= .5 else change["old_cost"]
            g = f - h
        return g, h, f

    def _draw_cell_scores(self, vertex, x, y, side):
        # 좌상: 정점 번호, 우상: g, 좌하: h, 우하: f.
        # 발견하지 않은 정점은 번호만 표시하여 h를 이미 계산한 것으로 오해하지 않게 합니다.
        self._draw_cell_corner(f"#{vertex}", colors.TEXT, x, y, side, "topleft")
        scores = self._cell_scores(vertex)
        if scores is None:
            return
        for name, value, color, corner in zip(("g", "h", "f"), scores,
                                             (colors.TEXT, colors.BLUE, colors.YELLOW),
                                             ("topright", "bottomleft", "bottomright")):
            self._draw_cell_corner(f"{name}{value:g}", color, x, y, side, corner)

    def _draw_cell_corner(self, label, color, x, y, side, corner):
        rendered = self.font(min(18, side * .2), True).render(label, True, color)
        max_width = max(1, self.view.length(side / 2 - 6))
        max_height = max(1, self.view.length(side * .28))
        scale = min(1, max_width / rendered.get_width(), max_height / rendered.get_height())
        if scale < 1:
            rendered = pygame.transform.smoothscale(rendered, (max(1, round(rendered.get_width() * scale)),
                                                              max(1, round(rendered.get_height() * scale))))
        dx = -side / 2 + 3 if "left" in corner else side / 2 - 3
        dy = -side / 2 + 3 if "top" in corner else side / 2 - 3
        box = rendered.get_rect(**{corner: self.view.point(x + dx, y + dy)})
        layer = pygame.Surface(box.size, pygame.SRCALPHA)
        layer.fill((*colors.BACKGROUND, 205))
        self.screen.blit(layer, box.topleft)
        self.screen.blit(rendered, box)
        return box

    def _draw_grid_graph(self):
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        side = self.grid["step_cost"] * self.scale
        path = self._hovered_path()
        path_edges = {frozenset((a, b)) for a, b in zip(path, path[1:])}
        candidates = {vertex for _, vertex, _ in self.heap}
        cells = {tuple(cell): v for v, cell in enumerate(self.grid["cells"])}
        tiles = self.grid.get("tiles")
        for row, line in enumerate(self.grid["rows"]):
            for col, char in enumerate(line):
                x, y = self._grid_point(col, row)
                rect = self.view.rect(x - side / 2 + 1, y - side / 2 + 1, side - 2, side - 2)
                code = tiles[row][col] if tiles else None
                if char == " ":
                    continue
                if char == "#":
                    if code is not None:
                        self._draw_map_tile(code, x, y, side)
                        continue
                    pygame.draw.rect(self.screen, (65, 70, 80), rect)
                    for offset in (-0.2, 0.2):
                        pygame.draw.line(self.screen, colors.BORDER,
                                         self.view.point(x - side * .3, y + side * offset - side * .15),
                                         self.view.point(x + side * .3, y + side * offset + side * .15), self.view.length(2))
                    continue
                vertex = cells[(col, row)]
                fill, border = colors.PANEL_DARK, colors.BORDER
                if vertex in self.distances:
                    fill, border = (28, 65, 48), colors.GREEN
                elif vertex in candidates:
                    fill, border = (28, 48, 69), colors.BLUE
                if vertex in path:
                    fill, border = (74, 65, 28), colors.YELLOW
                if code is not None:
                    self._draw_map_tile(code, x, y, side, border if border != colors.BORDER else None)
                else:
                    pygame.draw.rect(self.screen, fill, rect)
                    pygame.draw.rect(self.screen, border, rect, self.view.length(1))
        for u, v, _ in self.edges:
            if frozenset((u, v)) in path_edges or self._highlight(u, v):
                color = colors.YELLOW if frozenset((u, v)) in path_edges else colors.ORANGE
                pygame.draw.line(self.screen, color, self.view.point(*self._screen_point(u)),
                                 self.view.point(*self._screen_point(v)), self.view.length(4))
        self._draw_connection_change()
        self._draw_tentative_path()
        for vertex in range(len(self.names)):
            x, y = self._screen_point(vertex)
            if self.show_map_details:
                self._draw_cell_scores(vertex, x, y, side)
            color = colors.TEXT_MUTED
            if vertex in candidates:
                color = colors.BLUE
            if vertex in self.distances:
                color = colors.GREEN
            if vertex in path:
                color = colors.YELLOW
            marker = ""
            if vertex == self.start_vertex:
                marker, color = "S", colors.YELLOW
            if vertex == self.goal_vertex:
                marker, color = "G", colors.ORANGE
            if vertex == self.start_vertex == self.goal_vertex:
                marker = "S/G"
            if marker:
                size = min(18, max(10, side * .23))
                rendered = self.font(size, True).render(marker, True, color)
                max_width = self.view.length(side * .6)
                if rendered.get_width() > max_width:
                    factor = max_width / rendered.get_width()
                    rendered = pygame.transform.smoothscale(rendered, (max_width, max(1, round(rendered.get_height() * factor))))
                box = rendered.get_rect(center=self.view.point(x, y))
                pygame.draw.rect(self.screen, colors.BACKGROUND, box.inflate(self.view.length(4), 0))
                self.screen.blit(rendered, box)
            if vertex in (self.focus_vertex, self.current_vertex) or self.hovered == ("vertex", vertex):
                pygame.draw.rect(self.screen, colors.ORANGE,
                                 self.view.rect(x - side / 2 + 3, y - side / 2 + 3, side - 6, side - 6), self.view.length(3))
            hit = pygame.Rect(x - side / 2, y - side / 2, side, side).clip(pygame.Rect(self.plane_rect))
            if hit.width and hit.height:
                self.hits.append((tuple(hit), ("vertex", vertex)))
        self.screen.set_clip(previous)

    def _draw_inland(self):
        path = self._hovered_path()
        if path:
            labels = [f"#{v}" for v in path]
            if len(labels) > 12:
                labels = labels[:5] + ["…"] + labels[-5:]
            label = "경로: " + " → ".join(labels)
            label += f"   |   실제 비용 g = {self.distances[path[-1]]:g}"
            self._fit_text(label, 45, self.inland_top - 32, 1055, 21)
        elif self.grid:
            tentative = self._visible_tentative_path()
            if tentative:
                self._fit_text(f"점선: 현재 최소 f 후보 #{tentative[-1]}까지의 경로 (아직 목적지 경로로 확정되지 않음)",
                               45, self.inland_top - 32, 1055, 20)
        self.text(f"탐색한 정점: {len(self.inland)} / {len(self.names)}", 45, self.inland_top, 24, colors.GREEN, True)
        for index, vertex in enumerate(self.inland):
            if self.grid and index < self._inland_offset():
                continue
            cx, cy = self._inland_position(index)
            color = colors.YELLOW if vertex in path else colors.GREEN
            pygame.draw.circle(self.screen, colors.PANEL, self.view.point(cx, cy), self.view.length(19))
            pygame.draw.circle(self.screen, color, self.view.point(cx, cy), self.view.length(19), self.view.length(2))
            self.centered_text(vertex, cx, cy, 19, color)
            self.centered_text(f"{self.distances[vertex]:g}", cx, cy + 29, 17, color)
            self.hits.append(((cx - 24, cy - 23, 48, 68), ("vertex", vertex)))

    def _draw_progress(self):
        mode = "A*" if self.use_heuristic else "h=0 (Dijkstra)"
        label = f"{mode} | #{self.start_vertex} → #{self.goal_vertex} | 탐색 {len(self.inland)}개"
        button_x, button_y, _, _ = self.fit_button
        width = self.font(18).size(label)[0] / self.view.scale
        self.text(label, button_x - width - 20, button_y + 5, 18, colors.GREEN)

    def _draw_messages(self):
        if self.grid:
            if self.hidden:
                self.text("H: 설명 표시   A: A*/h=0 전환   M: 정점 번호·g/h/f   휠: 확대/축소   드래그: 지도 이동",
                          45, 866, 18, colors.TEXT_MUTED)
            else:
                BaseVisualizer._draw_messages(self)
            return
        super()._draw_messages()
        if self.hidden:
            self.text("A: A*/h=0 전환", 1145, 866, 18, colors.TEXT_MUTED)

    def draw_content(self):
        super().draw_content()
        if not self.hidden and self.grid and "tiles" in self.grid:
            self._fit_text("1 초원  2 모래  3 잔디  4 나무블록  |  11 돌  12 나무  13 석상  14 뱀  |  0 없음",
                           45, 113, 1045, 17)
            movement = getattr(self.data, "movement", {})
            if movement:
                diagonal = movement.get("diagonal", False)
                rule = "대각선 불가" if not diagonal else "대각선 가능 / 코너커팅 " + ("허용" if movement.get("corner_cutting") else "금지")
                self._fit_text(rule + f" / h: {getattr(self.data, 'heuristic', 'euclidean')}",
                               45, self.plane_rect[1] + 4, 760, 17)

    def finish_search(self):
        self.finished = True
        self.current_vertex = self.focus_vertex = None
        self.active = self.comparison = None
        self.found = self.goal_vertex in self.distances
        self.comparison_runs.setdefault(self.comparison_key, {})[self.use_heuristic] = len(self.inland)
        self.final_path = self.path_to(self.goal_vertex) if self.found else []
        self.operation = "목적지 도착" if self.found else "경로 없음"
        self.msg_phase("A*: 결과")
        if self.found:
            self.msg_action(f"목적지 #{self.goal_vertex}까지의 최단 비용은 {self.distances[self.goal_vertex]:g}이다.")
            self.msg_detail("목적지를 꺼내 종료했다. 아직 탐색하지 않은 정점을 도달 불가로 표시하지 않는다.")
        else:
            self.msg_action("후보가 소진되었다. 목적지까지의 경로가 없다.")
            self.msg_detail("시작점에서 도달 가능한 정점을 모두 검사했지만 목적지를 찾지 못했다.")
        self._update_stats()
