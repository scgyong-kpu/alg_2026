"""Prim 후보의 설명용 힙 배열과 확정된 내륙 정점을 표시한다."""

import heapq

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer
from .graph_representation import GraphRepresentationVisualizer


class PrimVisualizer(GraphRepresentationVisualizer):
    algorithm_name = "Prim"
    heading = "Prim: Minimum Spanning Tree"
    description = "가장 적은 비용으로 연결할 후보를 꺼내 내륙을 넓힌다."
    cost_heading = "비용"
    origin_heading = "출발"
    panel_left = 1300
    panel_width = 220
    cost_offset = 76
    origin_offset = 151
    row_step = 34
    cell_height = 30
    candidate_top = 136

    def setup(self, data, start=0):
        super().setup(data)
        self.plane_rect = (45, 140, 1195, 360)
        self.fit_button = (1194, 148, 32, 32)
        self.reset_plane()
        self.start_vertex = start
        self.heap = []
        self.inland = []
        self.selected_edges = set()
        self.total_cost = 0
        self.current_vertex = None
        self.focus_vertex = None
        self.operation = "준비"
        self.motion = None
        self.comparison = None
        self.value_change = None
        self.candidate_scroll = 0
        self.preview_neighbors = set()
        self._setup_messages(start)
        self._update_stats()

    def _setup_messages(self, start):
        self.msg_phase(self.algorithm_name + ": 준비")
        self.msg_action(f"시작점 #{start}를 비용 0인 후보로 등록한다.")
        self.msg_detail("최소 연결 비용의 후보를 꺼내 내륙으로 확정하고 그 주변을 검사한다.")

    def _running_hint(self):
        return "Space: 일시정지  .: 한 단계  Enter: 다음 동작  H: 설명  L: 배치  R: 재실행  D: 데이터  Esc: 종료"

    def _action_hint(self):
        return "R: 재실행  D: 다음 데이터  H: 설명  L: 배치  휠: 확대/축소  드래그: 이동  Esc: 종료"

    def _handle_key(self, key, mod=0):
        if key != pygame.K_TAB:
            super()._handle_key(key, mod)

    def _reveal_active(self):
        pass

    def _toggle_explanation(self):
        super()._toggle_explanation()
        self.plane_rect = (45, 25, 1195, 650) if self.hidden else (45, 140, 1195, 360)
        self.fit_button = (1194, self.plane_rect[1] + 8, 32, 32)
        self.reset_plane()
        self._reveal_candidate(self.focus_vertex)

    def _draw_messages(self):
        if self.hidden:
            self.text("H: 설명 표시   L: 배치   휠: 확대/축소   정점 드래그: 배치   빈 곳 드래그: 이동",
                      45, 866, 18, colors.TEXT_MUTED)
        else:
            BaseVisualizer._draw_messages(self)

    @property
    def candidate_rows(self):
        return 16 if self.hidden else 11

    @property
    def inland_top(self):
        return 720 if self.hidden else 535

    def _candidate_position(self, index):
        return self.panel_left, 140 + (index - self.candidate_scroll) * self.row_step

    def _inland_position(self, index):
        step = min(64, 1440 / max(1, len(self.names)))
        return 80 + index * step, self.inland_top + 55

    def _reveal_candidate(self, vertex):
        rows = len(self.heap)
        self.candidate_scroll = min(self.candidate_scroll, max(0, rows - self.candidate_rows))
        for index, (_, key, _) in enumerate(self.heap):
            if key == vertex:
                row = index
                if row < self.candidate_scroll:
                    self.candidate_scroll = row
                elif row >= self.candidate_scroll + self.candidate_rows:
                    self.candidate_scroll = row - self.candidate_rows + 1
                break

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            x, _ = self._logical_mouse(pygame.mouse.get_pos())
            if x >= self.panel_left - 20:
                rows = len(self.heap)
                self.candidate_scroll = max(0, min(max(0, rows - self.candidate_rows),
                                                  self.candidate_scroll - event.y))
                return
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION and self.plane_screen_rect().collidepoint(event.pos):
            point = pygame.Vector2(self._logical_mouse(event.pos))
            for vertex in range(len(self.names)):
                if point.distance_to(self._screen_point(vertex)) <= 23:
                    self.hovered = ("vertex", vertex)
                    break

    def _update_stats(self):
        self.msg_stats(f"내륙 {len(self.inland)}/{len(self.names)} / 간선 {len(self.selected_edges)}개 / 비용 {self.total_cost}")

    def _animate_heap(self, weights, vertex, kind):
        before = list(self.heap)
        # heapdict 내부 배열이 아니라, 공개된 후보로 다시 만든 설명용 힙입니다.
        after = [(cost, key, origin) for key, (cost, origin) in weights.items()]
        heapq.heapify(after)
        self.heap = after
        self._reveal_candidate(vertex)
        self.motion = {"before": before, "after": after, "vertex": vertex,
                       "kind": kind, "progress": 0}
        try:
            for frame in range(31):
                if self.stopped():
                    break
                t = 1 if self.running_to_section or self.is_max_speed() else frame / 30
                self.motion["progress"] = t * t * (3 - 2 * t)
                self.wait(24)
                if t == 1:
                    break
        finally:
            self.motion = None

    def add_candidate(self, vertex, cost, origin, weights, starting=False):
        self.focus_vertex = vertex
        self.operation = "시작점 추가" if starting else "새 후보 추가"
        self.comparison = None
        self._added_messages(vertex, cost, origin, starting)
        self._animate_heap(weights, vertex, "add")
        self.wait(450)
        self.section_end()

    def _added_messages(self, vertex, cost, origin, starting):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"#{vertex}를 비용 {cost}, 출발점 #{origin}인 후보로 추가한다.")
        self.msg_detail("루프 전에 시작점을 비용 0으로 등록한다." if starting else
                        "아직 후보에 없던 점이다. 현재 내륙에서 연결할 간선을 기록한다.")

    def take_candidate(self, vertex, cost, origin, weights, total_cost):
        self.focus_vertex = self.current_vertex = vertex
        self.active = None if vertex == origin else tuple(sorted((vertex, origin)))
        self.operation = "최소 비용 후보 꺼내기"
        self.comparison = None
        self._taken_messages(vertex, cost, origin)
        self._animate_heap(weights, vertex, "take")
        if not self.stopped():
            self.inland.append(vertex)
            if vertex != origin:
                self.selected_edges.add(tuple(sorted((vertex, origin))))
            self._record_confirmation(vertex, cost, origin, total_cost)
        self._update_stats()
        self.wait(650)
        self.section_end()

    def _taken_messages(self, vertex, cost, origin):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"비용 {cost}인 #{vertex}를 꺼내 내륙으로 확정한다.")
        self.msg_detail("시작점의 비용 0은 실제 간선이 아니므로 MST에 간선을 추가하지 않는다." if vertex == origin else
                        f"출발점 #{origin}에서 #{vertex}로 연결한 간선을 MST에 넣는다.")

    def _record_confirmation(self, vertex, cost, origin, total_cost):
        self.total_cost = total_cost

    def inspect_edge(self, origin, vertex, distance):
        self.focus_vertex = vertex
        self.active = tuple(sorted((origin, vertex)))
        self.operation = "이웃 검사"
        self.comparison = None
        self._inspection_messages(origin, vertex, distance)
        self._reveal_candidate(vertex)
        self.wait(450)

    def _inspection_messages(self, origin, vertex, distance):
        self.msg_phase(self.algorithm_name + ": 이웃 검사")
        self.msg_action(f"내륙 #{origin}의 이웃 #{vertex}를 검사한다. 간선 비용은 {distance}이다.")
        self.msg_detail("이미 내륙인지, 새 후보인지, 기존 후보보다 더 짧게 연결되는지 확인한다.")

    def show_neighbors(self, vertex, neighbors):
        """개별 검사 전에 이번에 살펴볼 이웃들과 간선을 함께 보여준다."""
        self.current_vertex = vertex
        self.preview_neighbors = set(neighbors)
        self.focus_vertex = None
        self.active = None
        self.comparison = None
        self.operation = "주변점 확인"
        self._neighbor_messages(vertex, neighbors)
        try:
            self.wait(1200)
            self.section_end()
        finally:
            self.preview_neighbors.clear()

    def _neighbor_messages(self, vertex, neighbors):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"방금 내륙이 된 #{vertex}의 주변 {len(neighbors)}개 점을 확인한다.")
        self.msg_detail("이미 내륙: 무시 / 새 점: 추가 / 더 짧음: 갱신 / 같거나 더 김: 기존 후보 유지")

    def ignore_inland(self, origin, vertex):
        self.operation = "이미 내륙: 무시"
        self._ignored_messages(vertex)
        self.wait(700)
        self.section_end()

    def _ignored_messages(self, vertex):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"#{vertex}는 이미 내륙이므로 무시한다.")
        self.msg_detail("확정한 정점은 후보에 다시 넣지 않는다.")

    def _compare(self, vertex, old_cost, old_origin, cost, origin):
        self.focus_vertex = vertex
        self.active = tuple(sorted((vertex, origin)))
        self._reveal_candidate(vertex)
        self.comparison = (vertex, old_cost, old_origin, cost, origin)
        self._comparison_messages(vertex, old_cost, old_origin, cost, origin)
        self.wait(1000)

    def _comparison_messages(self, vertex, old_cost, old_origin, cost, origin):
        self.msg_phase(self.algorithm_name + ": 연결 비용 비교")
        if cost < old_cost:
            self.msg_action(f"#{vertex}까지 갈 때, #{old_origin}에서 출발하는 비용 {old_cost}보다 #{origin}에서 출발하는 비용 {cost} 쪽이 더 작다.")
        elif cost == old_cost:
            self.msg_action(f"#{vertex}까지 #{old_origin}에서 가는 비용과 #{origin}에서 가는 비용은 {cost}로 같다.")
        else:
            self.msg_action(f"#{vertex}까지 #{origin}에서 가는 {cost}보다 기존 #{old_origin}에서 가는 {old_cost}가 더 작다.")
        self.msg_detail("목적지는 같다. 현재 내륙의 어느 점에서 연결할지 비교하며, 시작점부터의 누적 거리를 비교하는 것은 아니다.")

    def _animate_update_values(self, vertex, old_cost, old_origin, cost, origin):
        self.value_change = {"vertex": vertex, "old_cost": old_cost, "old_origin": old_origin,
                             "cost": cost, "origin": origin, "progress": 0}
        self._reveal_candidate(vertex)
        try:
            for frame in range(31):
                if self.stopped():
                    break
                t = 1 if self.running_to_section or self.is_max_speed() else frame / 30
                self.value_change["progress"] = t * t * (3 - 2 * t)
                self.wait(30)
                if t == 1:
                    break
        finally:
            # 값 변경을 먼저 끝내고, 같은 정점을 새 힙 위치로 옮깁니다.
            self.heap = [(cost, entry[1], origin) if entry[1] == vertex else entry for entry in self.heap]
            self.value_change = None

    def update_candidate(self, vertex, old_cost, old_origin, cost, origin, weights):
        self.operation = "더 짧음: 갱신"
        self._compare(vertex, old_cost, old_origin, cost, origin)
        self._updated_messages(vertex, old_cost, cost, origin)
        self._animate_update_values(vertex, old_cost, old_origin, cost, origin)
        self.comparison = None
        self._animate_heap(weights, vertex, "update")
        self.wait(650)
        self.section_end()

    def _updated_messages(self, vertex, old_cost, cost, origin):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"#{vertex}의 비용을 {old_cost}에서 {cost}로, 출발점을 #{origin}로 갱신한다.")
        self.msg_detail("비용과 연결 출발점을 함께 바꾼다. 같은 정점의 후보는 하나만 유지한다.")

    def keep_candidate(self, vertex, old_cost, old_origin, cost, origin):
        self.operation = "기존 후보 유지: 무시"
        self._compare(vertex, old_cost, old_origin, cost, origin)
        self._kept_messages(vertex, old_cost, old_origin, cost)
        self.wait(750)
        self.section_end()

    def _kept_messages(self, vertex, old_cost, old_origin, cost):
        self.msg_phase(self.algorithm_name + ": " + self.operation)
        self.msg_action(f"새 비용 {cost}가 기존 비용 {old_cost}보다 작지 않으므로 무시한다.")
        self.msg_detail(f"#{vertex}의 비용 {old_cost}와 출발점 #{old_origin}를 그대로 유지한다.")

    def finish_mst(self, count, mst, total_cost):
        self.current_vertex = self.focus_vertex = None
        self.active = self.comparison = None
        self.operation = "완료" if len(self.inland) == count else "도달하지 못한 점 있음"
        self.msg_phase("Prim: 결과")
        if len(self.inland) == count:
            self.msg_action(f"모든 정점이 내륙이 되었다. MST 비용은 {total_cost}이다.")
            self.msg_detail(f"간선 {len(mst)}개로 정점 {count}개를 연결했다.")
        else:
            self.msg_action("후보가 소진되었지만 아직 내륙이 아닌 정점이 있다.")
            self.msg_detail(f"전체 MST는 없다. 시작점의 연결 요소 비용은 {total_cost}이다.")
        self._update_stats()

    def _edge_color(self, u, v):
        key = tuple(sorted((u, v)))
        if self.value_change is not None:
            change = self.value_change
            if key in (tuple(sorted((change["vertex"], change["old_origin"]))),
                       tuple(sorted((change["vertex"], change["origin"])))):
                return colors.BORDER
        if self._is_preview_edge(u, v):
            return colors.ORANGE
        if self.comparison is not None:
            vertex, _, old_origin, _, origin = self.comparison
            if key == tuple(sorted((vertex, origin))):
                return colors.ORANGE
            if key == tuple(sorted((vertex, old_origin))):
                return colors.YELLOW
        if key == self.active:
            return colors.ORANGE
        if key in self.selected_edges:
            return colors.GREEN
        if any(key == tuple(sorted((vertex, origin))) for _, vertex, origin in self.heap if vertex != origin):
            return colors.BLUE
        return super()._edge_color(u, v)

    def _is_preview_edge(self, u, v):
        return ((u == self.current_vertex and v in self.preview_neighbors) or
                (v == self.current_vertex and u in self.preview_neighbors))

    def _highlight(self, u, v):
        return self._is_preview_edge(u, v) or super()._highlight(u, v)

    def _draw_graph(self):
        super()._draw_graph()
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        self._draw_connection_change()
        for vertex in self.inland:
            x, y = self._screen_point(vertex)
            pygame.draw.circle(self.screen, colors.GREEN, self.view.point(x, y), self.view.length(21))
            self.centered_text(vertex, x, y, 22, colors.BACKGROUND, bold=True)
        for vertex in self.preview_neighbors:
            pygame.draw.circle(self.screen, colors.ORANGE, self.view.point(*self._screen_point(vertex)),
                               self.view.length(27), self.view.length(3))
        for vertex, color, radius in ((self.current_vertex, colors.YELLOW, 27),
                                      (self.focus_vertex, colors.ORANGE, 24)):
            if vertex is not None:
                pygame.draw.circle(self.screen, color, self.view.point(*self._screen_point(vertex)),
                                   self.view.length(radius), self.view.length(3))
        self.screen.set_clip(previous)

    def _draw_connection_change(self):
        if self.value_change is None:
            return
        change = self.value_change
        t = change["progress"]
        vertex = change["vertex"]
        layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for origin, progress, alpha, color in ((change["old_origin"], 1, 1 - t, colors.YELLOW),
                                               (change["origin"], t, 1, colors.ORANGE)):
            a = pygame.Vector2(self._screen_point(origin))
            b = pygame.Vector2(self._screen_point(vertex))
            delta = b - a
            if delta.length() <= 44 or progress <= 0:
                continue
            direction = delta.normalize()
            start, end = a + direction * 22, b - direction * 22
            finish = start.lerp(end, progress)
            pygame.draw.line(layer, (*color, round(255 * alpha)), self.view.point(*start),
                             self.view.point(*finish), self.view.length(5))
        self.screen.blit(layer, (0, 0))

    def _draw_replaced_value(self, old, new, x, y, width):
        t = self.value_change["progress"]
        previous = self.screen.get_clip()
        clip = pygame.Rect(self.view.rect(x, y - 2, width, self.cell_height - 2))
        self.screen.set_clip(previous.clip(clip))
        for value, alpha, offset, color in ((old, 1 - t, -14 * t, colors.YELLOW),
                                            (new, t, 14 * (1 - t), colors.GREEN)):
            rendered = self.mono_font(18).render(str(value), True, color)
            rendered.set_alpha(round(255 * alpha))
            self.screen.blit(rendered, self.view.point(x, y + offset))
        self.screen.set_clip(previous)

    def _draw_candidate_cell(self, entry, index, position, hot=False):
        cost, vertex, origin = entry
        x, y = position
        color = colors.ORANGE if hot else colors.BLUE
        changing = self.value_change is not None and self.value_change["vertex"] == vertex
        if changing:
            color = colors.GREEN
        self.text(f"[{index}]", x - 36, y + 6, 14, colors.TEXT_MUTED)
        self.rect(x, y, self.panel_width, self.cell_height, colors.PANEL, color, radius=4)
        self.mono_text(f"#{vertex}", x + 10, y + 4, 18, color)
        if changing:
            change = self.value_change
            self._draw_replaced_value(change["old_cost"], change["cost"], x + self.cost_offset, y + 4, 66)
            self._draw_replaced_value(f"#{change['old_origin']}", f"#{change['origin']}", x + self.origin_offset, y + 4, 64)
        else:
            self.mono_text(str(cost), x + self.cost_offset, y + 4, 18, colors.TEXT)
            self.mono_text(f"#{origin}", x + self.origin_offset, y + 4, 18, colors.TEXT_MUTED)

    def _draw_candidates(self):
        self.text("후보 heap", self.panel_left, 30, 26, bold=True)
        self._fit_text(self.operation, self.panel_left, 74, self.panel_width, 18)
        for label, offset in (("정점", 10), (self.cost_heading, self.cost_offset), (self.origin_heading, self.origin_offset)):
            self.text(label, self.panel_left + offset, 110, 17, colors.TEXT_MUTED)
        previous = self.screen.get_clip()
        self.screen.set_clip(self.view.rect(self.panel_left - 40, self.candidate_top, self.panel_width + 40,
                                            self.candidate_rows * self.row_step))
        old = {} if self.motion is None else {entry[1]: i for i, entry in enumerate(self.motion["before"])}
        t = 1 if self.motion is None else self.motion["progress"]
        for index, entry in enumerate(self.heap):
            target = self._candidate_position(index)
            vertex = entry[1]
            if self.motion is not None:
                start = (self._candidate_position(old[vertex]) if vertex in old else
                         (self.panel_left + self.panel_width + 20, target[1]))
                position = tuple(a + (b - a) * t for a, b in zip(start, target))
            else:
                position = target
            x, y = position
            left, top = max(self.panel_left, x), max(self.candidate_top, y)
            right = min(self.panel_left + self.panel_width, x + self.panel_width)
            bottom = min(self.candidate_top + self.candidate_rows * self.row_step, y + self.cell_height)
            if right <= left or bottom <= top:
                continue
            self._draw_candidate_cell(entry, index, position, vertex == self.focus_vertex)
            self.hits.append(((left, top, right - left, bottom - top), ("vertex", vertex)))
        self.screen.set_clip(previous)
        if self.motion is not None and self.motion["kind"] == "take":
            vertex = self.motion["vertex"]
            index = old[vertex]
            start = self._candidate_position(index)
            target = self._inland_position(len(self.inland))
            start = start[0] + self.panel_width / 2, start[1] + self.cell_height / 2
            cx, cy = (a + (b - a) * t for a, b in zip(start, target))
            width = self.panel_width + (38 - self.panel_width) * t
            height = self.cell_height + (38 - self.cell_height) * t
            x, y = cx - width / 2, cy - height / 2
            self.rect(x, y, width, height, colors.PANEL, colors.GREEN, radius=4 + round(15 * t))
            self.centered_text(f"#{vertex}", x + width / 2, y + height / 2, 20, colors.GREEN)

    def _draw_inland(self):
        self.text(f"내륙: {len(self.inland)} / {len(self.names)}", 45, self.inland_top, 24, colors.GREEN, True)
        for index, vertex in enumerate(self.inland):
            cx, cy = self._inland_position(index)
            color = colors.ORANGE if vertex == self.focus_vertex else colors.GREEN
            pygame.draw.circle(self.screen, colors.PANEL, self.view.point(cx, cy), self.view.length(19))
            pygame.draw.circle(self.screen, color, self.view.point(cx, cy), self.view.length(19), self.view.length(2))
            self.centered_text(vertex, cx, cy, 19, color)
            self.centered_text(self.names[vertex], cx, cy + 31, 15, colors.TEXT_MUTED)
            self.hits.append(((cx - 19, cy - 19, 38, 38), ("vertex", vertex)))

    def _draw_progress(self):
        count, selected = len(self.names), len(self.selected_edges)
        label = f"정점 {count} | 내륙 {len(self.inland)} | 간선 {selected}/{count - 1} | 비용 {self.total_cost}"
        button_x, button_y, _, _ = self.fit_button
        width = self.font(18).size(label)[0] / self.view.scale
        self.text(label, button_x - width - 20, button_y + 5, 18,
                  colors.GREEN if len(self.inland) == count else colors.TEXT)

    def draw_content(self):
        self._animate_layout()
        self.hits = []
        if not self.hidden:
            self.text(self.heading, 45, 25, 32, bold=True)
            self.text(self.description, 45, 83, 21, colors.TEXT_MUTED)
        self._draw_graph()
        self._draw_candidates()
        self._draw_inland()
        self._draw_progress()
        self.draw_plane_controls()
