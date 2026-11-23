"""Prim, MST 왕복 순회, 중복 정점의 지름길 처리를 이어서 보여준다."""

import math
from types import SimpleNamespace

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer
from .plane import PlaneVisualizer
from .prim import PrimVisualizer
from .graph_representation import normalize_edges


class MstTspVisualizer(PrimVisualizer):
    estimated_color = (219, 135, 205)
    mst_dim_color = (66, 86, 72)
    algorithm_name = "MST-TSP"
    heading = "TSP using MST"
    description = "MST를 왕복한 뒤 중복 방문을 건너뛰어 도시를 한 번씩 방문한다."

    def setup(self, data, start=0):
        # 입력 가중치를 우선하고 존재하지 않는 간선만 좌표로 추정한다.
        points = data.positions
        geometric = [(u, v, math.dist(points[u], points[v]))
                     for u in range(len(points)) for v in range(u + 1, len(points))]
        supplied = getattr(data, "edges", None)
        edges = geometric if supplied is None else normalize_edges(len(points), supplied, "edge_list")
        self.has_input_edges = supplied is not None
        self.input_edges = {(u, v): weight for u, v, weight in edges}
        self.distances = [[math.dist(a, b) for b in points] for a in points]
        for u, v, weight in edges:
            self.distances[u][v] = self.distances[v][u] = weight
        display = SimpleNamespace(**vars(data))
        display.edges = edges
        super().setup(display, start)
        self.phase = "mst"
        self.fast_forward_mst = False
        self.mst_finished = False
        self.walk_finished = False
        self.walk = []
        self.route = []
        self.tree = {}
        self.stack = []
        self.travel_motion = None
        self.vehicle_vertex = start
        self.vehicle_edge = None
        self.vehicle_visited = set()
        self.shortcut_motion = None
        self.shortcut_ready_index = None
        self.token_index = None
        self.token_scroll = 0
        self.tree_scroll = 0
        self.show_complete = False
        self.walk_cost = 0
        self.route_cost = 0
        self._update_stats()

    def _running_hint(self):
        return BaseVisualizer._running_hint(self) + "  Shift+Enter: MST 완성까지  H: 설명  E: 전체 간선"

    def _action_hint(self):
        return BaseVisualizer._action_hint(self) + "  H: 설명  E: 전체 간선"

    def _handle_key(self, key, mod=0):
        if (key == pygame.K_RETURN and mod & pygame.KMOD_SHIFT
                and self.phase == "mst" and not self.mst_finished):
            self.fast_forward_mst = True
            self.running_to_section = True
            self.pause_after_section = True
            self.paused = False
            self.step_requested = False
        elif key == pygame.K_h:
            self._toggle_explanation()
        elif key == pygame.K_e:
            self.show_complete = not self.show_complete
        else:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_PERIOD):
                self.fast_forward_mst = False
            BaseVisualizer._handle_key(self, key, mod)

    def section_end(self):
        # MST까지 건너뛰는 동안에는 Prim 개별 동작의 구간 끝을 통과한다.
        if self.fast_forward_mst:
            return
        super().section_end()

    def _toggle_explanation(self):
        super()._toggle_explanation()
        self._resize_plane()

    def _resize_plane(self):
        expanded = self.phase in ("shortcut", "done")
        width = 1510 if expanded else 1195
        height = (650 if self.hidden else 420) if expanded else (575 if self.hidden else 360)
        self.plane_rect = (45, 25 if self.hidden else 140, width, height)
        self.fit_button = (45 + width - 46, self.plane_rect[1] + 8, 32, 32)
        self.reset_plane()

    def _draw_messages(self):
        if self.hidden:
            self.text("H: 설명 표시   Shift+Enter: MST 완성까지   E: 전체 간선   휠: 확대/축소·목록   드래그: 이동",
                      45, 866, 18, colors.TEXT_MUTED)
        else:
            self.rect(45, 730, 1510, 125, colors.PANEL_DARK, colors.BORDER, radius=6)
            self.text(self.messages["phase"], 65, 744, 21, colors.BLUE, True)
            self._fit_text(self.messages["dataset"], 430, 746, 1100, 18)
            self._fit_text(self.messages["action"], 65, 777, 1460, 24)
            self._fit_text(self.messages["detail"], 65, 817, 1460, 20)
            self._fit_text(self.messages["hint"], 45, 868, 1510, 17)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            point = self._logical_mouse(event.pos)
            self.hovered = next((target for rect, target in self.hits
                                 if pygame.Rect(rect).collidepoint(point)), None)
            if self.hovered is None and self.plane_screen_rect().collidepoint(event.pos):
                self.hovered = next((("vertex", u) for u in range(len(self.names))
                                     if math.dist(point, self._screen_point(u)) < 24), None)
        if event.type == pygame.MOUSEWHEEL:
            x, y = self._logical_mouse(pygame.mouse.get_pos())
            if x >= self.panel_left - 20 and self.phase in ("mst", "walk"):
                if self.phase == "mst":
                    self.candidate_scroll = max(0, min(max(0, len(self.heap) - self.candidate_rows),
                                                      self.candidate_scroll - event.y))
                else:
                    self.tree_scroll = max(0, min(max(0, len(self.names) - 12),
                                                 self.tree_scroll - event.y))
                return
            if y >= self.sequence_top and self.phase != "mst":
                self.token_scroll = max(0, min(self._max_token_scroll(), self.token_scroll - event.y))
                return
        # 배치 변경은 허용하지 않는다. 없는 간선의 추정값은 원래 좌표를 사용한다.
        PlaneVisualizer.handle_event(self, event)

    @property
    def sequence_top(self):
        if self.phase in ("shortcut", "done"):
            return 710 if self.hidden else 595
        return 640 if self.hidden else 535

    def _update_stats(self):
        if getattr(self, "phase", "mst") == "mst":
            super()._update_stats()
        else:
            self.msg_stats(f"MST {self.total_cost:,.2f} / 왕복 {self.walk_cost:,.2f} / 순회 {self.route_cost:,.2f}")

    def _added_messages(self, vertex, cost, origin, starting):
        self.msg_phase("MST: 후보 추가")
        self.msg_action(f"#{vertex}를 비용 {cost:,.2f}, 출발점 #{origin}인 후보로 등록한다.")
        self.msg_detail("시작점은 비용 0으로 등록한다." if starting else "입력 간선의 가중치를 연결 비용으로 쓴다." if self.has_input_edges else
                        "도시 사이의 직선거리를 연결 비용으로 쓴다.")

    def _taken_messages(self, vertex, cost, origin):
        self.msg_phase("MST: 최소 후보 확정")
        self.msg_action(f"비용 {cost:,.2f}인 #{vertex}를 내륙으로 확정한다.")
        self.msg_detail("시작점은 간선을 추가하지 않는다." if vertex == origin else
                        f"#{origin} - #{vertex}를 MST에 추가한다.")

    def _inspection_messages(self, origin, vertex, distance):
        self.msg_phase("MST: 이웃 검사")
        self.msg_action(f"#{origin}에서 #{vertex}까지의 거리 {distance:,.2f}를 검사한다.")
        self.msg_detail("내륙 여부와 기존 후보의 연결 비용을 확인한다.")

    def _comparison_messages(self, vertex, old_cost, old_origin, cost, origin):
        self.msg_phase("MST: 연결 비용 비교")
        self.msg_action(f"#{vertex}: #{old_origin}에서 {old_cost:,.2f} / #{origin}에서 {cost:,.2f}")
        self.msg_detail("현재 내륙에서 더 짧게 연결할 수 있는 쪽을 고른다.")

    def _updated_messages(self, vertex, old_cost, cost, origin):
        self.msg_action(f"#{vertex}의 연결 비용을 {old_cost:,.2f}에서 {cost:,.2f}로 갱신한다.")
        self.msg_detail(f"출발점도 #{origin}로 바꾼다.")

    def _kept_messages(self, vertex, old_cost, old_origin, cost):
        self.msg_action(f"새 비용 {cost:,.2f}가 기존 비용 {old_cost:,.2f}보다 작지 않으므로 유지한다.")
        self.msg_detail(f"#{vertex}의 출발점 #{old_origin}를 유지한다.")

    def _draw_candidate_cell(self, entry, index, position, hot=False):
        cost, vertex, origin = entry
        super()._draw_candidate_cell((f"{cost:,.1f}", vertex, origin), index, position, hot)

    def _draw_replaced_value(self, old, new, x, y, width):
        if isinstance(old, (int, float)):
            old = f"{old:,.1f}"
        if isinstance(new, (int, float)):
            new = f"{new:,.1f}"
        super()._draw_replaced_value(old, new, x, y, width)

    def finish_mst(self, count, mst, total_cost):
        self.mst_finished = True
        self.total_cost = total_cost
        self.current_vertex = self.focus_vertex = None
        self.active = self.comparison = None
        self.msg_phase("MST 완성")
        self.msg_action(f"정점 {count}개를 간선 {len(mst)}개로 연결했다. 비용은 {total_cost:,.2f}이다.")
        self.msg_detail("이 트리의 간선을 갈 때와 돌아올 때 한 번씩 지난다.")
        self._update_stats()
        self.wait(1200)
        if self.fast_forward_mst:
            self.fast_forward_mst = False
            self.running_to_section = True
            self.pause_after_section = True
        self.section_end()

    def begin_walk(self, tree, start):
        self.phase = "walk"
        self.walk_finished = False
        self.tree = {u: list(neighbors) for u, neighbors in tree.items()}
        self.walk = [start]
        self.route = []
        self.stack = [start]
        self.current_vertex = start
        self.vehicle_vertex = start
        self.vehicle_edge = None
        self.vehicle_visited = {start}
        self.focus_vertex = None
        self.walk_cost = 0
        self.token_scroll = 0
        self.msg_phase("MST 왕복 순회")
        self.msg_action(f"시작점 #{start}에서 MST의 이웃을 따라 이동한다.")
        self.msg_detail("남은 이웃 중 첫 방문할 도시를 우선한다. 이동한 방향만 목록에서 지운다.")
        self._update_stats()
        self.wait(1000)
        self.section_end()

    def _animate(self, motion, duration=850):
        for frame in range(31):
            if self.stopped():
                break
            t = 1 if self.running_to_section or self.is_max_speed() else frame / 30
            motion["progress"] = t * t * (3 - 2 * t)
            self.wait(duration / 30)
            if t == 1:
                break

    def _move_vehicle(self, u, v):
        self.vehicle_vertex = u
        self.vehicle_edge = (u, v)
        motion = {"u": u, "v": v, "progress": 0, "tour": self.phase != "walk"}
        self.travel_motion = motion
        try:
            self._animate(motion)
        finally:
            self.vehicle_vertex = v
            self.current_vertex = v
            if motion["progress"] >= 1 and not self.stopped():
                self.vehicle_visited.add(v)
            self.travel_motion = None

    def travel(self, u, v, walk, remaining, cost, returning=False):
        self.tree = {vertex: list(neighbors) for vertex, neighbors in remaining.items()}
        self.focus_vertex = v
        self.active = tuple(sorted((u, v)))
        self.msg_phase("MST 왕복 순회: " + ("돌아오기" if returning else "내려가기"))
        self.msg_action(f"#{u}에서 #{v}로 {'되돌아간다' if returning else '이동한다'}.")
        self.msg_detail(f"#{u}의 목록에서 #{v}를 지운다. 반대 방향은 그쪽으로 이동할 때 지운다.")
        try:
            self._move_vehicle(u, v)
        finally:
            self.walk = list(walk)
            self.walk_cost = cost
            self.current_vertex = v
            self.travel_motion = None
            self._reveal_token(len(self.walk) - 1)
            self._update_stats()
        self.wait(300)
        self.section_end()

    def finish_walk(self, walk, cost):
        self.walk_finished = True
        self.walk = list(walk)
        self.walk_cost = cost
        self.active = None
        self.focus_vertex = None
        self.msg_phase("왕복 순회 완성")
        self.msg_action(f"왕복 거리 {cost:,.2f} = 2 × MST 비용 {self.total_cost:,.2f}")
        self.msg_detail("시작점으로 돌아왔다. 이제 이미 방문한 정점을 건너뛴다.")
        self._update_stats()
        self.wait(1500)
        self.section_end()

    def begin_shortcut(self, walk):
        self.phase = "shortcut"
        self._resize_plane()
        self.walk = list(walk)
        self.route = []
        self.route_cost = 0
        self.token_index = None
        self.token_scroll = 0
        self.shortcut_ready_index = None
        self.vehicle_vertex = walk[0] if walk else self.start_vertex
        self.vehicle_edge = None
        self.vehicle_visited = {self.vehicle_vertex}
        self.msg_phase("지름길 만들기")
        self.msg_action("방문 순서를 왼쪽부터 읽으며 처음 방문한 도시만 남긴다.")
        self.msg_detail("없는 간선은 좌표로 추정한다. 삼각부등식이 성립할 때만 거리가 늘어나지 않는다.")
        self.wait(1000)
        self.section_end()

    def shortcut_step(self, index, route, skipped=False, after=None):
        self.token_index = index
        self._reveal_token(index)
        vertex = self.walk[index]
        self.focus_vertex = vertex
        self.msg_phase("지름길: " + ("중복 방문 제외" if skipped else "첫 방문 유지"))
        self.msg_action(f"#{vertex}는 " + ("이미 방문했으므로 건너뛴다." if skipped else "처음 방문하므로 남긴다."))
        self.msg_detail("회색 항목은 최종 순회에서 제외한 방문이다.")
        motion = None
        if skipped and 0 < index < len(self.walk) - 1:
            u, w = self.walk[index - 1], self.walk[index + 1]
            old = self._distance(u, vertex) + self._distance(vertex, w)
            direct = self._distance(u, w)
            motion = {"u": u, "v": vertex, "w": w, "index": index, "progress": 0}
            relation = "≥" if old >= direct else "<"
            source = "좌표 추정" if self._is_estimated(u, w) else "입력 간선"
            self.msg_detail(f"{self._distance(u, vertex):,.2f} + {self._distance(vertex, w):,.2f} = {old:,.2f} {relation} {direct:,.2f} ({source})")
            self.shortcut_motion = motion
        try:
            if motion is not None:
                self._animate(motion, 1100)
            else:
                self.route = list(route)
                self.shortcut_ready_index = None
                if len(route) >= 2 and self.vehicle_vertex != route[-1]:
                    self._move_vehicle(route[-2], route[-1])
                self.wait(700)
        finally:
            self.route = list(route)
            if after is not None:
                self.walk = list(after)
                self.shortcut_ready_index = index - 1
            self.route_cost = self._path_cost(route)
            self.shortcut_motion = None
            self._update_stats()
        if skipped and after is not None and route and not self.stopped():
            target = self.walk[index]
            # 다음 도시도 이미 방문했다면 최종 목적지가 정해질 때까지 기다린다.
            if target not in route:
                self._move_vehicle(route[-1], target)
        self.section_end()

    def show_shortcut(self, before, index, after, route):
        # 삭제 직전 순서의 양옆 도시를 연결하여 지름길을 보여준다.
        self.walk = list(before)
        self.shortcut_step(index, route, skipped=True, after=after)
        self.walk = list(after)
        self.token_index = None
        self._reveal_token(min(index, len(self.walk) - 1))

    def finish_tour(self, route, cost):
        self.phase = "done"
        self.route = list(route)
        self.route_cost = cost
        self.token_index = None
        self.current_vertex = self.focus_vertex = None
        self.active = None
        self.msg_phase("TSP 근사 순회 완성")
        self.msg_action(f"도시 {len(self.names)}개를 한 번씩 방문하고 시작점으로 돌아왔다. 거리 {cost:,.2f}")
        if self.has_input_edges:
            self.msg_detail("입력 가중치와 좌표 추정값을 함께 사용했다. 삼각부등식이 성립하지 않으면 2배 근사를 보장하지 않는다.")
        else:
            self.msg_detail(f"MST {self.total_cost:,.2f} ≤ 최적 순회 ≤ 이번 순회 {cost:,.2f} ≤ 2 × MST {2 * self.total_cost:,.2f}")
        self._update_stats()

    def close_tour(self, route):
        self.msg_phase("시작점으로 돌아가기")
        self.msg_action(f"마지막 도시 #{route[-2]}에서 시작점 #{route[-1]}로 돌아간다.")
        source = "없는 간선이므로 좌표로 추정" if self._is_estimated(route[-2], route[-1]) else "입력 간선의 가중치 사용"
        self.msg_detail(f"거리 {self._distance(route[-2], route[-1]):,.2f}: {source}.")
        try:
            self._move_vehicle(route[-2], route[-1])
        finally:
            self.route = list(route)
            self.travel_motion = None
        self.section_end()

    def _distance(self, u, v):
        return self.distances[u][v]

    def _is_estimated(self, u, v):
        return u != v and tuple(sorted((u, v))) not in self.input_edges

    def _path_cost(self, path):
        return sum(self._distance(u, v) for u, v in zip(path, path[1:]))

    def _line_segment(self, u, v, lane=0):
        if u == v:
            return None
        a, b = pygame.Vector2(self._screen_point(u)), pygame.Vector2(self._screen_point(v))
        delta = b - a
        if delta.length() < 1:
            return None
        direction = delta.normalize()
        # 화면의 y축은 아래로 증가한다. 이쪽 차선으로 왕복하면 간선을 시계방향으로 감싼다.
        offset = pygame.Vector2(direction.y, -direction.x) * lane
        trim = min(22, delta.length() / 4)
        return a + direction * trim + offset, b - direction * trim + offset

    def _line(self, u, v, color, width=3, arrow=False, alpha=255, lane=0):
        segment = self._line_segment(u, v, lane)
        if segment is None:
            return
        if self._is_estimated(u, v):
            color = self.estimated_color
        a, b = segment
        direction = (b - a).normalize()
        layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA) if alpha < 255 else self.screen
        ink = (*color, alpha) if alpha < 255 else color
        pygame.draw.line(layer, ink, self.view.point(*a), self.view.point(*b), self.view.length(width))
        if arrow:
            middle = a.lerp(b, .6)
            normal = pygame.Vector2(-direction.y, direction.x)
            pygame.draw.polygon(layer, ink, [self.view.point(*middle),
                                self.view.point(*(middle - direction * 13 + normal * 6)),
                                self.view.point(*(middle - direction * 13 - normal * 6))])
        if alpha < 255:
            self.screen.blit(layer, (0, 0))

    def _walk_segments(self):
        hidden = set()
        if self.shortcut_motion is not None:
            index = self.shortcut_motion.get("index")
            if index is not None:
                hidden = {index - 1, index}
        for index, (u, v) in enumerate(zip(self.walk, self.walk[1:])):
            if index not in hidden:
                selected = self.phase != "walk" and (index < len(self.route) - 1 or
                                                       index == self.shortcut_ready_index)
                yield u, v, colors.YELLOW if selected else colors.BLUE

    def _arrow_directions(self):
        path = self.walk if self.phase in ("walk", "shortcut") else self.route
        directions = set(zip(path, path[1:]))
        if self.travel_motion is not None:
            directions.add((self.travel_motion["u"], self.travel_motion["v"]))
        return directions

    def _lane_offset(self, u, v, directions=None):
        if directions is None:
            directions = self._arrow_directions()
        return 7 if u != v and (v, u) in directions else 0

    def _shortcut_geometry(self, motion):
        u, v, w = motion["u"], motion["v"], motion["w"]
        t = motion["progress"]
        directions = self._arrow_directions()
        first = self._line_segment(u, v, lane=self._lane_offset(u, v, directions))
        second = self._line_segment(v, w, lane=self._lane_offset(v, w, directions))
        index = motion.get("index")
        if index is not None:
            after = self.walk[:index] + self.walk[index + 1:]
            after_directions = set(zip(after, after[1:]))
        else:
            after_directions = directions - {(u, v), (v, w)} | {(u, w)}
        direct = self._line_segment(u, w, lane=self._lane_offset(u, w, after_directions))
        vertex = pygame.Vector2(self._screen_point(v))
        start = first[0] if first is not None else pygame.Vector2(self._screen_point(u))
        end = second[1] if second is not None else pygame.Vector2(self._screen_point(w))
        target_a, target_b = direct if direct is not None else (pygame.Vector2(self._screen_point(u)),) * 2
        length_a, length_b = start.distance_to(vertex), vertex.distance_to(end)
        ratio = length_a / max(1e-9, length_a + length_b)
        bend_target = target_a.lerp(target_b, ratio)
        return start.lerp(target_a, t), vertex.lerp(bend_target, t), end.lerp(target_b, t)

    def _draw_shortcut_motion(self):
        motion = self.shortcut_motion
        a, bend, b = self._shortcut_geometry(motion)
        t = motion["progress"]
        color = colors.BLUE
        if t == 1:
            color = self.estimated_color if self._is_estimated(motion["u"], motion["w"]) else colors.YELLOW
        pygame.draw.lines(self.screen, color, False,
                          [self.view.point(*p) for p in (a, bend, b)], self.view.length(4))
        # 두 화살촉을 줄이면서 펴진 경로 위의 한 화살촉으로 합친다.
        layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        def arrow(start, end, alpha, fraction=.6):
            delta = end - start
            if delta.length() < 1 or alpha <= 0:
                return
            direction = delta.normalize()
            normal = pygame.Vector2(-direction.y, direction.x)
            tip = start.lerp(end, fraction)
            pygame.draw.polygon(layer, (*color, round(255 * alpha)),
                                [self.view.point(*tip),
                                 self.view.point(*(tip - direction * 13 + normal * 6)),
                                 self.view.point(*(tip - direction * 13 - normal * 6))])

        arrow(a, bend, 1 - t)
        arrow(bend, b, 1 - t)
        first_length, second_length = a.distance_to(bend), bend.distance_to(b)
        position = .6 * (first_length + second_length)
        if position <= first_length:
            arrow(a, bend, t, position / max(1e-9, first_length))
        else:
            arrow(bend, b, t, (position - first_length) / max(1e-9, second_length))
        self.screen.blit(layer, (0, 0))

    def _draw_vehicle(self):
        if self.phase == "mst":
            return
        position = pygame.Vector2(self._screen_point(self.vehicle_vertex))
        heading = 0
        if self.vehicle_edge is not None:
            u, v = self.vehicle_edge
            delta = pygame.Vector2(self._screen_point(v)) - self._screen_point(u)
            if delta.length_squared():
                heading = -math.degrees(math.atan2(delta.y, delta.x))
        if self.travel_motion is not None:
            motion = self.travel_motion
            u, v = motion["u"], motion["v"]
            segment = self._line_segment(u, v, self._lane_offset(u, v))
            if segment is not None:
                a, b = segment
                position = a.lerp(b, motion["progress"])
                delta = b - a
                heading = -math.degrees(math.atan2(delta.y, delta.x))
        # 위에서 본 탑차: 큰 흰 짐칸, 분리된 주황 운전석, 앞 유리와 네 바퀴.
        truck = pygame.Surface((48, 34), pygame.SRCALPHA)
        outline = (28, 34, 42)
        for x in (10, 34):
            for y in (3, 25):
                pygame.draw.rect(truck, outline, (x, y, 7, 6), border_radius=2)
        pygame.draw.rect(truck, colors.WHITE, (4, 6, 25, 22), border_radius=2)
        pygame.draw.rect(truck, outline, (4, 6, 25, 22), 2, border_radius=2)
        pygame.draw.line(truck, colors.TEXT_MUTED, (9, 9), (9, 25), 1)
        pygame.draw.rect(truck, colors.ORANGE, (30, 8, 14, 18), border_radius=3)
        pygame.draw.rect(truck, outline, (30, 8, 14, 18), 2, border_radius=3)
        pygame.draw.rect(truck, colors.BLUE, (37, 11, 4, 12), border_radius=1)
        for y in (10, 21):
            pygame.draw.rect(truck, colors.YELLOW, (43, y, 3, 3))
        truck = pygame.transform.smoothscale(truck, (self.view.length(39), self.view.length(28)))
        truck = pygame.transform.rotate(truck, heading)
        self.screen.blit(truck, truck.get_rect(center=self.view.point(*position)))

    def _draw_graph(self):
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        # 원래 입력 간선은 항상 배경에 남기고 추정 간선과 구별한다.
        for u, v, _ in self.edges:
            self._line(u, v, colors.BORDER, 1, alpha=130 if self.has_input_edges or self.show_complete else 45)
        if self.show_complete:
            for u in range(len(self.names)):
                for v in range(u + 1, len(self.names)):
                    if self._is_estimated(u, v):
                        self._line(u, v, self.estimated_color, 1, alpha=70)
        faded_mst = self.walk_finished or self.phase in ("shortcut", "done")
        for u, v in self.selected_edges:
            if faded_mst:
                self._line(u, v, self.mst_dim_color, 1,
                           alpha=130 if self.has_input_edges or self.show_complete else 45)
            else:
                self._line(u, v, colors.GREEN, 3)
        if self.phase == "mst":
            for _, vertex, origin in self.heap:
                if vertex != origin:
                    self._line(origin, vertex, colors.BLUE, 2)
            for vertex in self.preview_neighbors:
                self._line(self.current_vertex, vertex, colors.ORANGE, 2)
            if self.active is not None:
                self._line(*self.active, colors.ORANGE, 4)
            self._draw_connection_change()
        elif self.phase in ("walk", "shortcut"):
            directions = self._arrow_directions()
            for u, v, color in self._walk_segments():
                self._line(u, v, color, 3, arrow=True, lane=self._lane_offset(u, v, directions))
        else:
            directions = self._arrow_directions()
            for u, v in zip(self.route, self.route[1:]):
                self._line(u, v, colors.YELLOW, 4, arrow=True, lane=self._lane_offset(u, v, directions))
        if self.shortcut_motion is not None:
            self._draw_shortcut_motion()
        for u, label in enumerate(self.names):
            x, y = self._screen_point(u)
            hot = self.hovered == ("vertex", u) or u == self.focus_vertex
            color = colors.ORANGE if hot else colors.GREEN if u in self.inland else colors.BLUE
            visited = u in self.vehicle_visited
            pygame.draw.circle(self.screen, colors.GREEN if visited else colors.PANEL,
                               self.view.point(x, y), self.view.length(21))
            pygame.draw.circle(self.screen, color, self.view.point(x, y), self.view.length(21), self.view.length(3))
            self.centered_text(u, x, y, 20, colors.BACKGROUND if visited else color, True)
            self.centered_text(label, x, y + 34, 16, colors.TEXT_MUTED)
            if u == self.start_vertex:
                pygame.draw.circle(self.screen, colors.YELLOW, self.view.point(x, y), self.view.length(26), self.view.length(2))
        if self.travel_motion is not None:
            motion = self.travel_motion
            lane = self._lane_offset(motion["u"], motion["v"])
            color = colors.YELLOW if motion.get("tour") else colors.ORANGE
            self._line(motion["u"], motion["v"], color, 5, arrow=True, lane=lane)
        self._draw_vehicle()
        self.screen.set_clip(previous)

    def _draw_tree(self):
        self.text("MST 남은 이웃", self.panel_left, 30, 25, bold=True)
        self.text("현재 정점" if self.phase == "walk" else "왕복 순회 완료",
                  self.panel_left, 82, 18, colors.TEXT_MUTED)
        if self.phase == "walk":
            self.text(f"#{self.current_vertex}", self.panel_left, 110, 20, colors.ORANGE)
        for row, u in enumerate(range(self.tree_scroll, min(len(self.names), self.tree_scroll + 12))):
            y = 160 + row * 34
            hot = u == self.current_vertex or self.hovered == ("vertex", u)
            self.rect(self.panel_left, y, self.panel_width, 30, colors.PANEL,
                      colors.ORANGE if hot else colors.BORDER, radius=4)
            self._fit_text(f"#{u}: " + (", ".join(map(str, self.tree.get(u, []))) or "없음"),
                           self.panel_left + 8, y + 5, self.panel_width - 16, 18)
            self.hits.append(((self.panel_left, y, self.panel_width, 30), ("vertex", u)))

    def _max_token_scroll(self):
        return max(0, math.ceil(len(self.walk) / self.token_columns) - 2)

    @property
    def token_columns(self):
        return max(1, int((self.plane_rect[2] - 44) // 52) + 1)

    def _reveal_token(self, index):
        self.token_scroll = max(0, min(self._max_token_scroll(), index // self.token_columns - 1))

    def _token_position(self, index):
        row, col = divmod(index, self.token_columns)
        return 45 + col * 52, self.sequence_top + 35 + (row - self.token_scroll) * 39

    def _token_state(self, index):
        x, y = self._token_position(index)
        alpha = 1
        motion = self.shortcut_motion
        if motion is not None and motion.get("index") is not None:
            removed = motion["index"]
            t = motion["progress"]
            if index == removed:
                y += 28 * t
                alpha = 1 - t
            elif index > removed:
                target_x, target_y = self._token_position(index - 1)
                x += (target_x - x) * t
                y += (target_y - y) * t
        return x, y, alpha

    def _draw_token(self, vertex, x, y, color, alpha):
        cell = pygame.Surface((self.view.length(44), self.view.length(31)), pygame.SRCALPHA)
        pygame.draw.rect(cell, colors.PANEL, cell.get_rect(), border_radius=self.view.length(4))
        pygame.draw.rect(cell, color, cell.get_rect(), self.view.length(2), self.view.length(4))
        label = self.font(19).render(str(vertex), True, color)
        cell.blit(label, label.get_rect(center=cell.get_rect().center))
        cell.set_alpha(round(255 * alpha))
        self.screen.blit(cell, self.view.point(x, y))

    def _draw_sequences(self):
        y = self.sequence_top
        self.text("왕복 순서" if self.phase == "walk" else "방문 순서", 45, y, 22, colors.BLUE, True)
        previous = self.screen.get_clip()
        self.screen.set_clip(previous.clip(self.view.rect(45, y + 33, self.plane_rect[2], 85)))
        seen = set()
        for index, vertex in enumerate(self.walk):
            duplicate = vertex in seen
            seen.add(vertex)
            x, top, alpha = self._token_state(index)
            if top + 31 <= y + 33 or top >= y + 118 or alpha <= 0:
                continue
            closing = self.phase == "done" and index == len(self.walk) - 1
            color = (colors.ORANGE if index == self.token_index else colors.YELLOW if closing else
                     colors.TEXT_MUTED if duplicate else colors.BLUE)
            self._draw_token(vertex, x, top, color, alpha)
            if alpha == 1:
                self.hits.append(((x, top, 44, 31), ("vertex", vertex)))
        self.screen.set_clip(previous)

    def _draw_progress(self):
        label = (f"정점 {len(self.names)} | MST {self.total_cost:,.2f} | "
                 f"왕복 {self.walk_cost:,.2f} | 순회 {self.route_cost:,.2f}")
        self.text(label, 55, self.plane_rect[1] + 4, 17, colors.TEXT_MUTED)

    def draw_content(self):
        self.hits = []
        if not self.hidden:
            self.text(self.heading, 45, 25, 32, bold=True)
            self.text(self.description, 45, 83, 21, colors.TEXT_MUTED)
        legend_y = self.plane_rect[1] + self.plane_rect[3] + 5
        for x, label, color in ((45, "입력 간선", colors.BORDER), (245, "MST", colors.GREEN),
                                (405, "순회", colors.YELLOW), (565, "좌표 추정 간선", self.estimated_color)):
            pygame.draw.line(self.screen, color, self.view.point(x, legend_y + 10),
                             self.view.point(x + 28, legend_y + 10), self.view.length(3))
            self.text(label, x + 36, legend_y, 17, colors.TEXT_MUTED)
        self._draw_graph()
        if self.phase == "mst":
            self._draw_candidates()
            self._draw_inland()
        else:
            if self.phase == "walk":
                self._draw_tree()
            self._draw_sequences()
        self._draw_progress()
        self.draw_plane_controls()
