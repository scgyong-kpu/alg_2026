"""연결 데이터와 화면 배치를 분리한 무방향 가중 그래프 수업 예제."""

import math
import random
import time
from types import SimpleNamespace

import pygame

from ..core import colors
from .plane import PlaneVisualizer


REPRESENTATIONS = ("edge_list", "adj_matrix", "adj_list")
TITLES = ("Edge List", "Adjacency Matrix", "Adjacency List")


def normalize_edges(count, source, representation, absent=None):
    """단순 무방향 그래프를 간선 목록으로 복사한다. 입력은 수정하지 않는다."""
    if count < 1:
        raise ValueError("정점이 하나 이상 필요합니다.")
    if representation == "edge_list":
        entries = list(source)
    elif representation == "adj_matrix":
        if len(source) != count or any(len(row) != count for row in source):
            raise ValueError("인접 행렬은 정점 수와 같은 정사각 행렬이어야 합니다.")
        entries = [(u, v, w) for u, row in enumerate(source)
                   for v, w in enumerate(row) if w != absent]
    elif representation == "adj_list":
        if set(source) != set(range(count)):
            raise ValueError("고립된 정점도 인접 목록의 key에 포함해야 합니다.")
        entries = [(u, v, w) for u, neighbors in source.items()
                   for v, w in neighbors.items()]
    else:
        raise ValueError(f"알 수 없는 그래프 표현: {representation}")

    edges = {}
    for u, v, weight in entries:
        if not isinstance(u, int) or not isinstance(v, int) or not (0 <= u < count and 0 <= v < count):
            raise ValueError("간선의 정점 index가 범위를 벗어났습니다.")
        if u == v:
            raise ValueError("이 예제는 자기 루프가 없는 단순 그래프를 사용합니다.")
        if not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("가중치는 유한한 수여야 합니다.")
        key = tuple(sorted((u, v)))
        if key in edges and edges[key] != weight:
            raise ValueError("같은 무방향 간선의 가중치가 서로 다릅니다.")
        edges[key] = weight
    return [(u, v, weight) for (u, v), weight in edges.items()]


def graph_representations(count, edges):
    """한 그래프의 세 표현을 만든다. 간선 없음은 None, 가중치 0은 0이다."""
    matrix = [[None for _ in range(count)] for _ in range(count)]
    neighbors = {u: {} for u in range(count)}
    for u, v, weight in edges:
        matrix[u][v] = matrix[v][u] = weight
        neighbors[u][v] = neighbors[v][u] = weight
    return list(edges), matrix, neighbors


class GraphRepresentationVisualizer(PlaneVisualizer):
    plane_rect = (45, 140, 865, 480)
    fit_button = (864, 148, 32, 32)
    panel_left = 970
    panel_width = 550

    def setup(self, data, source=None, representation="edge_list", absent=None):
        self.set_data_info(data)
        self.data = data
        self.names = list(data.vertices)
        self.edges = normalize_edges(len(self.names), data.edges if source is None else source,
                                     representation, absent)
        self.forms = graph_representations(len(self.names), self.edges)
        self.mode = REPRESENTATIONS.index(representation)
        self.layout = 0
        self.layouts = self._make_layouts(getattr(data, "positions", None))
        self.positions = list(self.layouts[0])
        self.layout_motion = None
        self.vertex_drag = None
        self.active = None
        self.selected_vertex = None
        self.hovered = None
        self.hits = []
        self.scroll_row = 0
        self.hidden = False
        self.plane_rect = (45, 140, 865, 480)
        self.fit_button = (864, 148, 32, 32)
        self.reset_plane()
        self.msg_phase("그래프 표현")
        self.msg_action("정점과 간선으로 같은 그래프를 표현한다.")
        self.msg_detail("화면의 좌표와 선 길이는 연결 정보나 가중치가 아니다.")
        self.msg_stats(f"정점 {len(self.names)}개 / 간선 {len(self.edges)}개 / 무방향")

    def _make_layouts(self, supplied):
        count = len(self.names)
        circle = [(500 + 420 * math.cos(-math.pi / 2 + 2 * math.pi * i / count),
                   350 + 280 * math.sin(-math.pi / 2 + 2 * math.pi * i / count))
                  for i in range(count)]
        if supplied is not None:
            if len(supplied) != count or any(len(point) != 2 for point in supplied):
                raise ValueError("정점마다 화면 배치 좌표가 하나씩 필요합니다.")
            xs, ys = zip(*supplied)
            scale = min(800 / max(1, max(xs) - min(xs)), 500 / max(1, max(ys) - min(ys)))
            original = [(500 + (x - (min(xs) + max(xs)) / 2) * scale,
                         350 + (y - (min(ys) + max(ys)) / 2) * scale) for x, y in supplied]
        else:
            original = [(140 + (i % 4) * 240, 570 - (i // 4) * 240) for i in range(count)]
        rng = random.Random(2609)
        shuffled = list(range(count))
        rng.shuffle(shuffled)
        scattered = [(circle[i][0] + rng.uniform(-30, 30),
                      circle[i][1] + rng.uniform(-25, 25)) for i in shuffled]
        return original, circle, scattered

    def _screen_point(self, index):
        x, y = self.positions[index]
        return self.origin_x + (x - self.min_x) * self.scale, self.origin_y - (y - self.min_y) * self.scale

    def _fit_positions(self, positions):
        self.fit_plane([SimpleNamespace(x=x, y=y) for x, y in positions])

    def reset_plane(self):
        """저장된 초기 범위 대신, 지금 배치된 모든 정점을 화면에 맞춘다."""
        self.layout_motion = None
        self.vertex_drag = None
        self._fit_positions(self.positions)
        self.plane_motion_time = time.monotonic()

    def _toggle_explanation(self):
        # 보고 있던 중심과 상대 확대 배율을 유지한 채 그래프 영역만 확장한다.
        x, y, w, h = self.plane_rect
        cx = self.min_x + (x + w / 2 - self.origin_x) / self.scale
        cy = self.min_y + (self.origin_y - y - h / 2) / self.scale
        zoom = self.plane_zoom
        self.hidden = not self.hidden
        self.plane_rect = (45, 25, 865, 815) if self.hidden else (45, 140, 865, 480)
        x, y, w, h = self.plane_rect
        self.fit_button = (x + w - 46, y + 8, 32, 32)
        self._fit_positions(self.positions)
        self.plane_zoom = zoom
        self.scale *= zoom
        self.origin_x = x + w / 2 - (cx - self.min_x) * self.scale
        self.origin_y = y + h / 2 + (cy - self.min_y) * self.scale
        self._clamp_plane()

    def set_representation(self, mode):
        self.mode = REPRESENTATIONS.index(mode)
        self.scroll_row = 0

    def show_edge(self, u, v):
        self.active = tuple(sorted((u, v)))
        self.selected_vertex = None
        self._reveal_active()
        self.msg_action(f"정점 #{u}와 #{v}를 연결하는 간선을 읽는다.")
        self.msg_detail("무방향 간선 하나는 행렬과 인접 목록에 양방향으로 저장된다.")
        self.wait(950)

    def show_vertex(self, u):
        self.active = None
        self.selected_vertex = u
        self.scroll_row = max(0, u - 7)
        self.msg_action(f"정점 #{u}의 이웃 {len(self.forms[2][u])}개를 확인한다.")
        self.msg_detail("행렬은 행 전체를, 인접 목록은 저장된 이웃만 살펴본다.")
        self.wait(1200)

    def _reveal_active(self):
        if self.active is None:
            return
        if self.mode == 0:
            row = next(i for i, edge in enumerate(self.edges) if edge[:2] == self.active)
        else:
            row = self.active[0]
        self.scroll_row = max(0, row - 7)

    def _running_hint(self):
        return "Space: 일시정지  .: 한 단계  Enter: 다음 표현  Tab: 표현  L: 배치  H: 설명  D: 데이터  R: 재실행  Esc: 종료"

    def _action_hint(self):
        return "Tab: 표현  L: 배치  H: 설명  휠: 확대/축소  정점 드래그: 배치  빈 곳 드래그: 이동  R: 재실행  D: 데이터  Esc: 종료"

    def _handle_key(self, key, mod=0):
        if key == pygame.K_TAB:
            self.mode = (self.mode + 1) % 3
            self._reveal_active()
        elif key == pygame.K_l:
            self.layout = (self.layout + 1) % len(self.layouts)
            self.layout_motion = (list(self.positions), self.layouts[self.layout], 0.0, time.monotonic())
            self.vertex_drag = None
            # 이동의 시작 위치와 도착 위치를 모두 담는 카메라를 사용한다.
            self._fit_positions(self.positions + self.layouts[self.layout])
        elif key == pygame.K_h:
            self._toggle_explanation()
        else:
            super()._handle_key(key, mod)

    def _animate_layout(self):
        if self.layout_motion is None:
            return
        start, end, elapsed, last = self.layout_motion
        now = time.monotonic()
        if not self.paused:
            elapsed += (now - last) * self.speed
        progress = 1 if self.running_to_section or self.is_max_speed() else min(1, elapsed / 1.2)
        eased = progress * progress * (3 - 2 * progress)
        self.positions = [(x + (tx - x) * eased, y + (ty - y) * eased)
                          for (x, y), (tx, ty) in zip(start, end)]
        if progress == 1:
            self.positions = list(end)
        self.layout_motion = None if progress == 1 else (start, end, elapsed, now)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            point = self._logical_mouse(event.pos)
            # 화면 맞춤 버튼이 정점이나 간선보다 항상 우선하여 클릭을 받는다.
            if pygame.Rect(self.view.rect(*self.fit_button)).collidepoint(event.pos):
                self.reset_plane()
                self.msg_log("현재 정점 배치에 화면을 맞춤")
                return
            for rect, target in self.hits:
                if pygame.Rect(rect).collidepoint(point):
                    self._select(target)
                    return
            for u in range(len(self.names)):
                x, y = self._screen_point(u)
                if math.dist(point, (x, y)) < 23:
                    self.vertex_drag = u
                    self.layout_motion = None
                    self.selected_vertex = u
                    self.active = None
                    return
            if self.plane_screen_rect().collidepoint(event.pos):
                for u, v, _ in self.edges:
                    a, b = pygame.Vector2(self._screen_point(u)), pygame.Vector2(self._screen_point(v))
                    segment = b - a
                    if segment.length_squared() == 0:
                        continue
                    t = max(0, min(1, (pygame.Vector2(point) - a).dot(segment) / segment.length_squared()))
                    if pygame.Vector2(point).distance_to(a + t * segment) < 9:
                        self.active = (u, v)
                        self.selected_vertex = None
                        self._reveal_active()
                        return
        elif event.type == pygame.MOUSEMOTION:
            point = self._logical_mouse(event.pos)
            self.hovered = next((target for rect, target in self.hits
                                 if pygame.Rect(rect).collidepoint(point)), None)
            if self.vertex_drag is not None and event.buttons[0]:
                x, y = point
                left, top, width, height = self.plane_rect
                x = max(left + 30, min(left + width - 30, x))
                y = max(top + 35, min(top + height - 40, y))
                self.positions[self.vertex_drag] = (self.min_x + (x - self.origin_x) / self.scale,
                                                     self.min_y + (self.origin_y - y) / self.scale)
                return
        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.WINDOWFOCUSLOST:
            self.vertex_drag = None
        elif event.type == pygame.MOUSEWHEEL:
            x, y = self._logical_mouse(pygame.mouse.get_pos())
            if x >= self.panel_left - 20:
                rows = len(self.edges) if self.mode == 0 else len(self.names)
                self.scroll_row = max(0, min(max(0, rows - 8), self.scroll_row - event.y))
                return
        super().handle_event(event)

    def _select(self, target):
        kind, value = target
        if kind == "mode":
            self.mode = value
            self.scroll_row = 0
        elif kind == "vertex":
            self.selected_vertex = value
            self.active = None
        elif kind == "edge":
            self.active = value
            self.selected_vertex = None
        elif kind == "absent":
            self.active = None
            self.selected_vertex = None
            self.msg_action(f"정점 #{value[0]}와 #{value[1]} 사이에는 간선이 없다.")

    def _highlight(self, u, v):
        target = self.hovered or (("edge", self.active) if self.active is not None else
                                  ("vertex", self.selected_vertex))
        kind, value = target
        return (kind == "edge" and value == tuple(sorted((u, v)))) or (kind == "vertex" and value in (u, v))

    def _draw_messages(self):
        if self.hidden:
            self.text("H: 설명 표시   Tab: 표현   L: 배치   휠: 확대/축소   정점 드래그: 배치   빈 곳 드래그: 이동",
                      45, 862, 18, colors.TEXT_MUTED)
        else:
            super()._draw_messages()

    def draw_content(self):
        self._animate_layout()
        self.hits = []
        if not self.hidden:
            self.text("Graph Representation", 45, 25, 36, bold=True)
            self.text(("지정 배치", "원형 배치", "섞은 배치")[self.layout], 45, 83, 22, colors.BLUE)
            self.text(f"|V| = {len(self.names)}    |E| = {len(self.edges)}", 340, 83, 22, colors.TEXT_MUTED)
        self._draw_graph()
        self._draw_representation()
        self.draw_plane_controls()

    def _edge_color(self, u, v):
        return colors.ORANGE if self._highlight(u, v) else colors.BORDER

    def _draw_graph(self):
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        for u, v, weight in self.edges:
            hot = self._highlight(u, v)
            color = self._edge_color(u, v)
            a, b = self._screen_point(u), self._screen_point(v)
            pygame.draw.line(self.screen, color,
                             self.view.point(*a), self.view.point(*b), self.view.length(4 if hot else 2))
            # 가중치는 화면상의 선 길이와 무관한 입력값이다.
            x, y = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            self.rect(x - 22, y - 14, 44, 28, colors.BACKGROUND,
                      color, radius=4)
            self.centered_text(weight, x, y, 18, color if color != colors.BORDER else colors.TEXT)
        for u, label in enumerate(self.names):
            x, y = self._screen_point(u)
            hot = self.selected_vertex == u or (self.active is not None and u in self.active)
            pygame.draw.circle(self.screen, colors.PANEL, self.view.point(x, y), self.view.length(21))
            pygame.draw.circle(self.screen, colors.ORANGE if hot else colors.BLUE,
                               self.view.point(x, y), self.view.length(21), self.view.length(2))
            self.centered_text(u, x, y, 22, bold=True)
            self.centered_text(label, x, y + 34, 18, colors.TEXT_MUTED)
        self.screen.set_clip(previous)

    def _draw_representation(self):
        for i, label in enumerate(("Edges", "Matrix", "List")):
            step = (self.panel_width + 5) / 3
            x = self.panel_left + i * step
            self.rect(x, 30, step - 10, 42, colors.PANEL if i == self.mode else colors.BACKGROUND,
                      colors.BLUE if i == self.mode else colors.BORDER, radius=4)
            self.centered_text(label, x + (step - 10) / 2, 51, 18 if self.panel_width < 400 else 22)
            self.hits.append(((x, 30, step - 10, 42), ("mode", i)))
        self.text(TITLES[self.mode], self.panel_left, 95, 22 if self.panel_width < 400 else 26, bold=True)
        note = "무방향 / 가중치 0도 간선 / ·: 간선 없음"
        if self.panel_width < 400:
            self.text("무방향 / 가중치 0도 간선", self.panel_left, 134, 17, colors.TEXT_MUTED)
            self.text("·: 간선 없음", self.panel_left, 158, 17, colors.TEXT_MUTED)
        else:
            self.text(note, self.panel_left, 134, 18, colors.TEXT_MUTED)
        if self.mode == 1:
            self._draw_matrix()
        else:
            self._draw_rows()

    def _draw_rows(self):
        rows = len(self.edges) if self.mode == 0 else len(self.names)
        for visible, row in enumerate(range(self.scroll_row, min(rows, self.scroll_row + 8))):
            y = 195 + visible * 52
            if self.mode == 0:
                u, v, w = self.edges[row]
                hot = self._highlight(u, v)
                self.rect(self.panel_left, y, self.panel_width, 44, colors.PANEL if hot else colors.BACKGROUND,
                          colors.ORANGE if hot else colors.BORDER, radius=4)
                self.mono_text(f"#{row:<3}  ({u}, {v}, {w})", self.panel_left + 14, y + 7,
                               18 if self.panel_width < 400 else 23)
                self.hits.append(((self.panel_left, y, self.panel_width, 44), ("edge", (u, v))))
            else:
                self.text(f"{row}:", self.panel_left, y + 7, 22, colors.BLUE, True)
                self.hits.append(((self.panel_left - 7, y, 48, 44), ("vertex", row)))
                neighbors = list(self.forms[2][row].items())
                if not neighbors:
                    self.mono_text("{}", self.panel_left + 50, y + 7, 22, colors.TEXT_MUTED)
                cell_width = min(122, (self.panel_width - 50) / max(1, len(neighbors)))
                for i, (v, w) in enumerate(neighbors):
                    x = self.panel_left + 50 + i * cell_width
                    hot = self._highlight(row, v)
                    self.rect(x, y, cell_width - 5, 44, colors.PANEL if hot else colors.BACKGROUND,
                              colors.ORANGE if hot else colors.BORDER, radius=4)
                    self._fit_text(f"{v}: {w}", x + 4, y + 10, cell_width - 13, 21)
                    self.hits.append(((x, y, cell_width - 5, 44), ("edge", tuple(sorted((row, v))))))
        self.text(f"{min(rows, self.scroll_row + 1)}~{min(rows, self.scroll_row + 8)} / {rows}",
                  self.panel_left, 616, 18, colors.TEXT_MUTED)

    def _fit_text(self, value, x, y, width, size):
        while size > 10 and self.font(size).size(value)[0] > self.view.length(width):
            size -= 1
        self.text(value, x, y, size)

    def _draw_matrix(self):
        count = len(self.names)
        available = self.panel_width - 50
        cell = min(44, available / count)
        x0, y0 = self.panel_left + 40, 200
        columns = min(count, int(available / cell))
        rows = min(count - self.scroll_row, int(420 / cell))
        for v in range(columns):
            self.centered_text(v, x0 + (v + .5) * cell, y0 - 22, 18, colors.BLUE)
        for offset in range(rows):
            u = self.scroll_row + offset
            self.centered_text(u, x0 - 22, y0 + (offset + .5) * cell, 18, colors.BLUE)
            for v in range(columns):
                x, y = x0 + v * cell, y0 + offset * cell
                weight = self.forms[1][u][v]
                hot = self._highlight(u, v)
                self.rect(x, y, cell - 2, cell - 2, colors.PANEL if hot else colors.BACKGROUND,
                          colors.ORANGE if hot else colors.BORDER, radius=0)
                self.centered_text("·" if weight is None else weight, x + (cell - 2) / 2,
                                   y + (cell - 2) / 2, 17, colors.TEXT_MUTED if weight is None else colors.TEXT)
                target = ("absent", (u, v)) if weight is None else ("edge", tuple(sorted((u, v))))
                self.hits.append(((x, y, cell - 2, cell - 2), target))
        self.text(f"행 {self.scroll_row}~{self.scroll_row + rows - 1} / {count}개",
                  self.panel_left, 616, 18, colors.TEXT_MUTED)
