"""지도와 거리 행렬에서 같은 경로를 대응시켜 보여준다."""

import math

import pygame

from ..core import colors
from .graph import GraphVisualizer


class FloydWarshallVisualizer(GraphVisualizer):
    inspected_fill = (33, 48, 63)
    skipped_hatch = (135, 144, 156)

    def __init__(self, title="Floyd-Warshall", **kwargs):
        super().__init__(title, **kwargs)
        self.set_message_layout("bottom")

    def _graph_bounds(self):
        return 94, 163, 830, 750 if self.hidden else 561

    def setup(self, data):
        self.hidden = getattr(self, "hidden", False)
        super().setup(data)
        self.directed = getattr(data, "directed", False)
        self.vertex_radius = 19 if len(self.vertices) < 10 else 13
        self.dist = self.next_hop = None
        self.active = self.hovered = self.via_vertex = None
        self.scan_cell = None
        self.hovered_vertex = None
        self.updated = False
        self.finished = False
        self.history = []
        self.initial_dist = None
        self.selected_phase = None
        self.table_x, self.table_y = 952, 122
        self._size_matrix()
        self.msg_phase("거리 행렬")
        self.msg_action("그래프를 읽었다.")
        self.msg_detail("행은 출발 정점, 열은 도착 정점이다.")

    def _size_matrix(self):
        height = 665 if self.hidden else 500
        self.cell = min(66, 623 / (len(self.vertices) + 1), height / (len(self.vertices) + 1))

    def _handle_key(self, key, mod=0):
        if key == pygame.K_RETURN and getattr(self, "finished", False):
            return
        if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_PERIOD, pygame.K_KP_PERIOD):
            self.selected_phase = None
        if key != pygame.K_h or not hasattr(self, "dist"):
            return super()._handle_key(key, mod)
        self.hidden = not self.hidden
        self.vertices = self._normalize_vertices(self.data.vertices, getattr(self.data, "positions", None))
        self._size_matrix()
        self._update_hover(pygame.mouse.get_pos())

    def _running_hint(self):
        return super()._running_hint() + "  H: 설명  |  일시정지 중 k 클릭: 이전 단계"

    def _action_hint(self):
        return super()._action_hint() + "  H: 설명  |  k 클릭: 이전 단계"

    def _draw_messages(self):
        if self.hidden:
            self.text(self.messages["hint"], 80, 850, 17, colors.TEXT_MUTED)
        else:
            super()._draw_messages()

    def initialize(self, dist, next_hop):
        self.dist, self.next_hop = dist, next_hop
        self.initial_dist = [row[:] for row in dist]
        self.msg_action("대각선을 0으로 두고 직접 간선의 비용을 기록한다.")
        self.msg_detail("직접 연결되지 않은 칸은 ∞이다. 이후 우회 경로를 찾을 수 있다.")
        self.wait(1100)
        self.section_end()

    def begin_phase(self, k):
        self.selected_phase = None
        self.via_vertex = k
        self.active = None
        self.scan_cell = None
        self.updated = False
        self.msg_phase(f"중간 정점 k = {k}")
        self.msg_action(f"#{k}를 거치는 경로를 검사한다.")
        self.msg_detail("현재 거리와 중간 정점을 거치는 두 거리의 합을 비교한다.")
        self.wait(600)

    @staticmethod
    def _comparison_skip_reason(i, j, k):
        if k is None:
            return ""
        if i == j:
            return "i = j: 출발과 도착이 같은 대각선 칸"
        if i == k:
            return "i = k: 출발 정점이 중간 정점과 같음"
        if j == k:
            return "j = k: 도착 정점이 중간 정점과 같음"
        return ""

    def _live_phase(self):
        if self.selected_phase is None and self.via_vertex == len(self.history):
            return self.via_vertex
        return None

    def compare(self, i, j, k, via):
        self.scan_cell = (i, j)
        if (not self.running_to_section and not self.is_max_speed()
                and not self._comparison_skip_reason(i, j, k)):
            self.active = (i, j)
            self.updated = False
            shorter = via < self.dist[i][j]
            self.msg_action(f"d[{i}][{j}] = {self._number(self.dist[i][j])}   |   "
                            f"d[{i}][{k}] + d[{k}][{j}] = {self._number(via)}")
            if shorter:
                self.msg_detail("경유할 때의 합이 더 작다.")
            elif via == math.inf:
                self.msg_detail("중간 정점을 거치는 경로가 없어 거리를 유지한다.")
            else:
                self.msg_detail("경유해도 더 짧아지지 않는다.")
            self.wait(700 if shorter else 250)

    def update_distance(self):
        if not self.running_to_section and not self.is_max_speed() and self.active:
            i, j = self.active
            self.updated = True
            self.msg_action(f"d[{i}][{j}]를 {self.dist[i][j]:g}로 갱신했다.")
            self.wait(450)

    def end_phase(self):
        # 다음 단계가 현재 행렬을 제자리에서 바꾸므로 행까지 복사한다.
        self.history.append(([row[:] for row in self.dist], [row[:] for row in self.next_hop]))
        self.active = None
        self.scan_cell = None
        self.updated = False
        self.msg_action(f"k = {self.via_vertex} 단계 완료")
        self.msg_detail(f"0부터 {self.via_vertex}까지의 정점을 중간에 거치는 경로를 고려했다.")
        self.draw()
        self.section_end()

    def finish(self):
        self.active = self.via_vertex = None
        self.scan_cell = None
        self.finished = True
        self.msg_phase("완료")
        self.msg_action("모든 정점 쌍의 거리를 계산했다.")
        self.msg_detail("행렬의 칸에 마우스를 올리면 실제 경로를 지도에서 볼 수 있다.")
        self.draw()

    @staticmethod
    def _number(value):
        return "∞" if value == math.inf else f"{value:g}"

    def _path(self, start, end):
        dist, next_hop = self._display_matrices()
        if (next_hop[start][end] is None
                or any(dist[k][k] < 0 and dist[start][k] < math.inf
                       and dist[k][end] < math.inf for k in range(len(self.vertices)))):
            return []
        path = [start]
        while start != end:
            start = next_hop[start][end]
            if start is None or start in path:
                return []
            path.append(start)
        return path

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.running_to_section and (self.paused or self.finished):
                completed = len(self.history)
                visible = completed + (self.via_vertex == completed)
                for k in range(visible):
                    if pygame.Rect(self.view.rect(*self._phase_button(k))).collidepoint(event.pos):
                        self.selected_phase = k if k < completed else None
                        self._update_hover(event.pos)
                        return
        super().handle_event(event)

    def _display_matrices(self):
        if self.selected_phase is not None:
            return self.history[self.selected_phase]
        return self.dist, self.next_hop

    def _displayed_phase(self):
        if self.selected_phase is not None:
            return self.selected_phase
        if self.finished and self.history:
            return len(self.history) - 1
        return self.via_vertex

    def _previous_dist(self):
        k = self._displayed_phase()
        if k is None:
            return None
        return self.initial_dist if k == 0 else self.history[k - 1][0]

    def _phase_button(self, k):
        size = min(38, self.cell - 3)
        return self.table_x - 32 - size / 2, self.table_y + (k + 1.5) * self.cell - size / 2, size, size

    def _draw_phases(self):
        self.centered_text("k", self.table_x - 32, self.table_y + self.cell / 2, 20, colors.YELLOW, True)
        completed = len(self.history)
        current = self.via_vertex
        visible = max(completed, current + 1 if current is not None else 0)
        x, _, w, _ = self._phase_button(0)
        height = (visible + 1) * self.cell
        pygame.draw.rect(self.screen, colors.YELLOW,
                         self.view.rect(x - 5, self.table_y, w + 10, height),
                         max(1, self.view.length(2)), border_radius=self.view.length(5))
        displayed = self.selected_phase
        if displayed is None:
            displayed = completed - 1 if self.finished and completed else current
        for k in range(visible):
            x, y, w, h = self._phase_button(k)
            selected = k == displayed
            in_progress = k == current and k >= completed
            color = colors.ORANGE if in_progress else colors.YELLOW if selected else colors.TEXT_MUTED
            fill = (67, 55, 31) if selected or in_progress else colors.PANEL
            self.rect(x, y, w, h, fill, color, radius=3)
            self.centered_text(k, x + w / 2, y + h / 2, 16, color, True)

    def _update_hover(self, pos):
        self.hovered = self.hovered_vertex = None
        size = self.cell
        count = len(self.vertices)
        if self.dist is not None:
            for i in range(-1, count):
                for j in range(-1, count):
                    if i == j == -1:
                        continue
                    if pygame.Rect(self.view.rect(self.table_x + (j + 1) * size,
                                                  self.table_y + (i + 1) * size, size, size)).collidepoint(pos):
                        self.hovered = (i, j)
                        return
        for index, vertex in enumerate(self.vertices):
            x, y = self.view.point(vertex["x"], vertex["y"])
            if math.hypot(pos[0] - x, pos[1] - y) <= self.view.length(self.vertex_radius):
                self.hovered_vertex = index
                return

    def _hover_info(self):
        if self.hovered is not None:
            i, j = self.hovered
            if i < 0 or j < 0:
                index = max(i, j)
                axis = "도착 열" if i < 0 else "출발 행"
                return f"{axis}: #{index} {self.vertices[index]['name']}"
            start, end = self.vertices[i]["name"], self.vertices[j]["name"]
            dist, _ = self._display_matrices()
            reason = self._comparison_skip_reason(i, j, self._live_phase())
            if reason:
                return f"{start} → {end}  |  거리 {self._number(dist[i][j])}\n비교 연출 생략: {reason}"
            path = self._path(i, j)
            if not path:
                return f"{start} → {end}: 경로 없음" if dist[i][j] == math.inf else f"{start} → {end}: 경로를 표시할 수 없음"
            route = " → ".join(f"#{node}" for node in path)
            value = dist[i][j]
            previous = self._previous_dist()
            detail = f"거리 {self._number(value)}"
            if previous is not None and value < previous[i][j]:
                k = self._displayed_phase()
                left, right = previous[i][k], previous[k][j]
                old = self._number(previous[i][j])
                detail = f"{old} → ({self._number(left)} + {self._number(right)} = {self._number(value)})"
            return f"{start} → {end}  |  {detail}\n{route}"
        if self.hovered_vertex is not None:
            index = self.hovered_vertex
            return f"정점 #{index}: {self.vertices[index]['name']}"
        return ""

    def _edge(self, u, v, color, width, reverse=False, weight=None):
        a, b = self.vertices[u], self.vertices[v]
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]
        length = math.hypot(dx, dy)
        if length <= 2 * self.vertex_radius:
            return
        dx, dy = dx / length, dy / length
        offset = 7 if reverse else 0
        ax, ay = a["x"] + dx * self.vertex_radius - dy * offset, a["y"] + dy * self.vertex_radius + dx * offset
        bx, by = b["x"] - dx * self.vertex_radius - dy * offset, b["y"] - dy * self.vertex_radius + dx * offset
        pygame.draw.line(self.screen, color, self.view.point(ax, ay), self.view.point(bx, by),
                         max(1, self.view.length(width)))
        if self.directed:
            pygame.draw.polygon(self.screen, color, [
                self.view.point(bx, by),
                self.view.point(bx - 11 * dx + 4 * dy, by - 11 * dy - 4 * dx),
                self.view.point(bx - 11 * dx - 4 * dy, by - 11 * dy + 4 * dx),
            ])
        if weight is not None and len(self.vertices) <= 8:
            gap = 10 if reverse else 0
            self.centered_text(weight, (ax + bx) / 2 - dy * gap, (ay + by) / 2 + dx * gap, 15, colors.TEXT_MUTED)

    def draw_content(self):
        if not self.vertices:
            return
        self.text("Floyd-Warshall", 65, 35, 42, bold=True)
        self.text("방향 그래프" if self.directed else "무방향 그래프", 80, 108, 22, colors.BLUE, True)
        self.text("거리 행렬", self.table_x, 84, 22, colors.BLUE, True)
        directed_edges = {(u, v) for u, v, _ in self.edges} if self.directed else set()
        for u, v, w in self.edges:
            self._edge(u, v, colors.BORDER, 2, (v, u) in directed_edges, w)
        hovered_pair = self.hovered if self.hovered is not None and min(self.hovered) >= 0 else None
        active = self.active if self.selected_phase is None else None
        displayed_k = self.via_vertex if self.selected_phase is None else self.selected_phase
        pair = hovered_pair or active
        if self.dist is not None and pair is not None:
            i, j = pair
            k = self.via_vertex
            segments = [(i, j, colors.ORANGE)]
            if hovered_pair is None and not self.updated:
                segments += [(i, k, colors.BLUE), (k, j, colors.GREEN)]
            elif hovered_pair is None and self.updated:
                segments = [(i, j, colors.GREEN)]
            for start, end, color in segments:
                path = self._path(start, end)
                for u, v in zip(path, path[1:]):
                    self._edge(u, v, color, 4, (v, u) in directed_edges)
        hover_vertices = {index for index in (self.hovered or ()) if index >= 0}
        hover_vertices.add(self.hovered_vertex)
        for index, vertex in enumerate(self.vertices):
            x, y = vertex["x"], vertex["y"]
            color = colors.ORANGE if index in hover_vertices else colors.YELLOW if index == displayed_k else colors.TEXT
            center = self.view.point(x, y)
            radius = max(1, self.view.length(self.vertex_radius))
            pygame.draw.circle(self.screen, colors.PANEL, center, radius)
            pygame.draw.circle(self.screen, color, center, radius, max(1, self.view.length(2)))
            self.centered_text(index, x, y, 16 if radius >= 10 else 13, color, True)
            self.centered_text(vertex["name"], x, y + self.vertex_radius + 10, 15, colors.TEXT_MUTED)
        if self.dist is not None:
            self._draw_matrix()
            self._draw_phases()
        info = self._hover_info()
        if info:
            self._draw_wrapped_text(info, 80, 784 if self.hidden else 596, 825, 16,
                                    colors.ORANGE, True, 20)

    def _draw_skipped_hatch(self, x, y, size):
        cell = pygame.Rect(self.view.rect(x, y, size - 1, size - 1)).inflate(-4, -4)
        if cell.width <= 0 or cell.height <= 0:
            return
        for offset in range(0, cell.width + cell.height - 1, max(4, self.view.length(8))):
            start = max(0, offset - cell.height + 1)
            end = min(offset, cell.width - 1)
            pygame.draw.line(self.screen, self.skipped_hatch,
                             (cell.x + start, cell.y + offset - start),
                             (cell.x + end, cell.y + offset - end))

    def _draw_matrix(self):
        dist, _ = self._display_matrices()
        previous = self._previous_dist()
        active = self.active if self.selected_phase is None else None
        displayed_k = self.via_vertex if self.selected_phase is None else self.selected_phase
        scan_cell = self.scan_cell if self.selected_phase is None else None
        live_k = self._live_phase()
        size = self.cell
        count = len(self.vertices)
        for i in range(-1, count):
            for j in range(-1, count):
                if i == j == -1:
                    continue
                border = colors.BORDER
                fill = colors.PANEL_DARK
                ink = colors.TEXT
                skipped = False
                if i == -1 or j == -1:
                    index = max(i, j)
                    label = str(index)
                    fill, ink = ((29, 48, 69), colors.BLUE) if i == -1 else ((30, 57, 49), colors.GREEN)
                    if index == displayed_k:
                        border = colors.YELLOW
                else:
                    label = self._number(dist[i][j])
                    skipped = bool(self._comparison_skip_reason(i, j, live_k))
                    if previous is not None and dist[i][j] < previous[i][j]:
                        ink = colors.GREEN
                    if not skipped and scan_cell is not None and (i, j) < scan_cell:
                        fill = self.inspected_fill
                    if active:
                        u, v = active
                        k = self.via_vertex
                        if (i, j) == (u, v):
                            border = colors.GREEN if self.updated else colors.ORANGE
                        elif (i, j) == (u, k):
                            border = colors.BLUE
                        elif (i, j) == (k, v):
                            border = colors.GREEN
                if ((i, j) == self.hovered or (i == -1 and self.hovered and j == self.hovered[1])
                        or (j == -1 and self.hovered and i == self.hovered[0])
                        or ((i == -1 or j == -1) and max(i, j) == self.hovered_vertex)):
                    border = colors.ORANGE
                x, y = self.table_x + (j + 1) * size, self.table_y + (i + 1) * size
                self.rect(x, y, size - 1, size - 1, fill, border, radius=2)
                if skipped:
                    self._draw_skipped_hatch(x, y, size)
                self.centered_text(label, x + size / 2, y + size / 2,
                                   min(21, max(11, int(size / 2))), ink, True)
