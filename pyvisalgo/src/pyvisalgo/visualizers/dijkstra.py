"""Prim의 후보 이동을 재사용하고 누적 거리와 최단 경로를 표시한다."""

import math

import pygame

from ..core import colors
from .prim import PrimVisualizer


class DijkstraVisualizer(PrimVisualizer):
    algorithm_name = "Dijkstra"
    heading = "Dijkstra: Shortest Paths"
    description = "시작점부터의 누적 거리가 가장 작은 후보를 꺼내 최단 거리를 확정한다."
    cost_heading = "거리"
    origin_heading = "이전"

    def setup(self, data, start=0):
        # 부모 setup에서 호출하는 통계·문구 메서드보다 먼저 초기화합니다.
        self.distances = {}
        self.predecessors = {}
        self.finished = False
        super().setup(data, start)
        if any(weight < 0 for _, _, weight in self.edges):
            raise ValueError("Dijkstra는 음수 가중치가 없는 그래프에서 사용합니다.")
        self.edge_weights = {tuple(sorted((u, v))): w for u, v, w in self.edges}

    def _setup_messages(self, start):
        self.msg_phase("Dijkstra: 준비")
        self.msg_action(f"시작점 #{start}의 거리를 0으로 준비한다.")
        self.msg_detail("가중치는 0 이상이어야 한다. 후보의 거리는 시작점부터의 누적 거리이다.")

    def _update_stats(self):
        self.msg_stats(f"확정 {len(self.inland)}/{len(self.names)} / 후보 {len(self.heap)}개")

    def _animate_heap(self, weights, vertex, kind):
        super()._animate_heap(weights, vertex, kind)
        self._update_stats()

    def _equation(self, vertex, cost, origin):
        if vertex == origin:
            return "시작점의 거리 = 0"
        weight = self.edge_weights[tuple(sorted((origin, vertex)))]
        base = self.distances[origin]
        return f"#{origin}까지 {base} + 간선 {weight} = #{vertex}까지 {cost}"

    def _added_messages(self, vertex, cost, origin, starting):
        self.msg_phase("Dijkstra: " + self.operation)
        self.msg_action(f"#{vertex}를 누적 거리 {cost}인 후보로 추가한다.")
        self.msg_detail(self._equation(vertex, cost, origin))

    def take_candidate(self, vertex, cost, origin, weights, total_cost=None):
        # 마지막 인자는 Prim과의 호출 호환용이며, 거리의 합은 결과로 사용하지 않습니다.
        super().take_candidate(vertex, cost, origin, weights, total_cost)

    def _taken_messages(self, vertex, cost, origin):
        self.operation = "최소 거리 후보 꺼내기"
        self.msg_phase("Dijkstra: 거리 확정")
        self.msg_action(f"#{vertex}의 최단 거리를 {cost}로 확정한다.")
        self.msg_detail("가중치가 0 이상이므로 남은 후보를 경유해도 더 짧아지지 않는다.")

    def _record_confirmation(self, vertex, cost, origin, total_cost):
        self.distances[vertex] = cost
        self.predecessors[vertex] = None if vertex == origin else origin

    def _inspection_messages(self, origin, vertex, distance):
        self.msg_phase("Dijkstra: 이웃 검사")
        self.msg_action(f"#{origin}에서 이웃 #{vertex}로 가는 경로를 검사한다.")
        self.msg_detail(f"현재까지 {self.distances[origin]} + 간선 {distance} = 새 누적 거리 {self.distances[origin] + distance}")

    def _neighbor_messages(self, vertex, neighbors):
        self.msg_phase("Dijkstra: 주변점 확인")
        self.msg_action(f"거리 {self.distances[vertex]}로 확정된 #{vertex}의 주변 {len(neighbors)}개 점을 확인한다.")
        self.msg_detail("이미 확정: 무시 / 새 후보: 추가 / 더 짧은 경로: 갱신 / 그 외: 유지")

    def _ignored_messages(self, vertex):
        self.operation = "이미 확정: 무시"
        self.msg_phase("Dijkstra: " + self.operation)
        self.msg_action(f"#{vertex}는 최단 거리가 이미 확정되어 무시한다.")
        self.msg_detail("확정된 정점은 후보에 다시 넣지 않는다.")

    def _comparison_messages(self, vertex, old_cost, old_origin, cost, origin):
        relation = "<" if cost < old_cost else "=" if cost == old_cost else ">"
        self.msg_phase("Dijkstra: 누적 거리 비교")
        self.msg_action(f"#{vertex}의 새 거리 {cost} {relation} 기존 거리 {old_cost}")
        self.msg_detail(self._equation(vertex, cost, origin) + f" / 기존 이전 정점 #{old_origin}")

    def _updated_messages(self, vertex, old_cost, cost, origin):
        self.msg_phase("Dijkstra: " + self.operation)
        self.msg_action(f"#{vertex}의 거리를 {old_cost}에서 {cost}로 갱신한다.")
        self.msg_detail(self._equation(vertex, cost, origin) + f" / 이전 정점 → #{origin}")

    def _kept_messages(self, vertex, old_cost, old_origin, cost):
        self.msg_phase("Dijkstra: 기존 후보 유지")
        self.msg_action(f"새 거리 {cost}가 기존 거리 {old_cost}보다 작지 않아 유지한다.")
        self.msg_detail(f"#{vertex}의 거리 {old_cost}, 이전 정점 #{old_origin}을 바꾸지 않는다.")

    def finish_paths(self):
        """확정 이벤트로 모은 거리와 이전 정점을 최종 결과로 표시한다."""
        self.current_vertex = self.focus_vertex = None
        self.active = self.comparison = None
        self.finished = True
        missing = len(self.names) - len(self.distances)
        self.operation = "도달 불가 있음" if missing else "완료"
        self.msg_phase("Dijkstra: 결과")
        self.msg_action(f"시작점 #{self.start_vertex}에서 {len(self.distances)}개 정점의 최단 거리를 구했다.")
        self.msg_detail(f"도달할 수 없는 {missing}개 정점의 거리는 ∞이다." if missing else
                        "각 거리는 시작점부터의 최단 거리이며, 거리의 합을 최소화하는 문제가 아니다.")
        self._update_stats()

    def path_to(self, vertex):
        """확정한 이전 정점을 역추적한다. 아직 확정하지 않은 정점은 경로가 없다."""
        if vertex not in self.distances:
            return []
        path = []
        while vertex is not None:
            path.append(vertex)
            vertex = self.predecessors[vertex]
        return path[::-1]

    def _hovered_path(self):
        if self.hovered is not None and self.hovered[0] == "vertex":
            return self.path_to(self.hovered[1])
        return []

    def _edge_color(self, u, v):
        if self.motion is None and self.comparison is None and self.value_change is None:
            path = self._hovered_path()
            if any({u, v} == {a, b} for a, b in zip(path, path[1:])):
                return colors.YELLOW
        return super()._edge_color(u, v)

    def _highlight(self, u, v):
        path = self._hovered_path()
        if path and self.motion is None and self.comparison is None and self.value_change is None:
            # 선택 정점의 모든 인접 간선이 아니라 실제 최단 경로의 간선만 굵게 표시합니다.
            return any({u, v} == {a, b} for a, b in zip(path, path[1:]))
        return super()._highlight(u, v)

    def _draw_graph(self):
        super()._draw_graph()
        path = self._hovered_path()
        if not path:
            return
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        for vertex in path:
            pygame.draw.circle(self.screen, colors.YELLOW, self.view.point(*self._screen_point(vertex)),
                               self.view.length(25), self.view.length(3))
        self.screen.set_clip(previous)

    def _draw_inland(self):
        path = self._hovered_path()
        if path:
            route = " → ".join(f"#{vertex}" for vertex in path)
            label = f"경로: {route}   |   최단 거리 {self.distances[path[-1]]}"
            self._fit_text(label, 45, self.inland_top - 32, 1480, 21)
        elif self.finished and self.hovered is not None and self.hovered[0] == "vertex":
            vertex = self.hovered[1]
            self.text(f"#{self.start_vertex} → #{vertex}: 도달할 수 있는 경로 없음", 45,
                      self.inland_top - 32, 21, colors.TEXT_MUTED)
        self.text(f"확정된 최단 거리: {len(self.inland)} / {len(self.names)}", 45, self.inland_top, 24, colors.GREEN, True)
        # 완료 후에는 도달 불가 정점도 함께 표시합니다. 후보가 없는 것과 구분합니다.
        vertices = self.inland + ([v for v in range(len(self.names)) if v not in self.distances]
                                  if self.finished else [])
        for index, vertex in enumerate(vertices):
            cx, cy = self._inland_position(index)
            distance = self.distances.get(vertex, math.inf)
            color = colors.GREEN if math.isfinite(distance) else colors.TEXT_MUTED
            if vertex in path:
                color = colors.YELLOW
            pygame.draw.circle(self.screen, colors.PANEL, self.view.point(cx, cy), self.view.length(19))
            pygame.draw.circle(self.screen, color, self.view.point(cx, cy), self.view.length(19), self.view.length(2))
            self.centered_text(vertex, cx, cy, 19, color)
            label = str(distance) if math.isfinite(distance) else "∞"
            self.centered_text(label, cx, cy + 29, 17, color)
            # 원뿐 아니라 바로 아래의 거리 숫자에 올려도 같은 경로를 보여줍니다.
            self.hits.append(((cx - 24, cy - 23, 48, 68), ("vertex", vertex)))

    def _draw_progress(self):
        label = f"시작점 #{self.start_vertex} | 확정 {len(self.inland)}/{len(self.names)}"
        button_x, button_y, _, _ = self.fit_button
        width = self.font(18).size(label)[0] / self.view.scale
        self.text(label, button_x - width - 20, button_y + 5, 18, colors.GREEN)
