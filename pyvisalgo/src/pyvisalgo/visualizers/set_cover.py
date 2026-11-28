"""미포함 원소와 각 후보가 새로 덮을 원소를 함께 표시한다."""

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class SetCoverVisualizer(BaseVisualizer):
    graph_extra_height = 0
    candidate_left = 690

    def setup(self, data):
        self.msg_clear()
        self.set_data_info(data)
        self.data = data
        self.universe = sorted(set(data.universe))
        self.subsets = [sorted(set(s)) for s in data.subsets]
        self.uncovered = set(self.universe)
        self.gains = {}
        self.chosen = []
        self.best = None
        self.counting = None
        self.current_element = None
        self.tallies = {}
        self.msg_phase("집합 커버")
        self.msg_action(self._setup_action())
        self.wait(900)

    def _setup_action(self):
        return "전체 집합을 덮을 부분집합을 고른다."

    def compare(self, gains, best=None):
        self.gains = gains
        self.best = None
        self.tallies = {}
        self.msg_phase("교집합 세기")
        self.msg_detail("아직 덮지 않은 원소만 하나씩 센다.")
        for index, new_elements in gains.items():
            if self.stopped():
                return
            if self.running_to_section or self.is_max_speed():
                break
            self.counting = index
            self.tallies[index] = 0
            self.msg_action(f"{self._candidate_label(index)}이 새로 덮는 원소를 센다.")
            self.wait(220)
            for value in sorted(new_elements):
                if self.stopped():
                    return
                if self.running_to_section or self.is_max_speed():
                    break
                self.current_element = value
                self.tallies[index] += 1
                self.wait(260)
            self.tallies[index] = len(new_elements)
            self.current_element = None
        if self.stopped():
            return
        self.counting = None
        self.tallies = {index: len(elements) for index, elements in gains.items()}
        if best is None:
            self.msg_action("후보마다 새로 덮는 원소를 모두 셌다.")
            self.wait(850)
            self.section_end()
            return
        self.best = best if gains[best] else None
        self.msg_phase("후보 비교")
        self.msg_action(f"현재 미포함 원소를 {self._candidate_label(best)}이 가장 많이 덮는다: {len(gains[best])}개."
                        if self.best is not None else "새로 덮을 수 있는 원소가 없다.")
        self.msg_detail("오른쪽 숫자는 집합의 전체 크기가 아니라 미포함 원소와의 교집합 크기이다.")
        self.wait(1150)

    def select(self, best, uncovered):
        covered = self.uncovered - uncovered
        self.chosen.append(best)
        self.uncovered = set(uncovered)
        self.gains = {}
        self.tallies = {}
        self.best = None
        self.msg_phase("집합 선택")
        self.msg_action(f"{self._candidate_label(best)} 선택: {', '.join(map(self._element_label, sorted(covered)))}을 새로 덮었다.")
        self.msg_detail("이미 덮은 원소는 다음 후보를 평가할 때 다시 세지 않는다.")
        self.wait(950)
        self.section_end()

    def finish(self, uncovered):
        self.msg_phase("결과")
        if uncovered:
            self.msg_action(f"끝까지 덮지 못한 원소: {', '.join(map(self._element_label, sorted(uncovered)))}")
        else:
            self.msg_action(f"부분집합 {len(self.chosen)}개로 전체를 덮었다.")
        optimum = getattr(self.data, "optimal_cover", None)
        if optimum is not None:
            names = ", ".join(self._candidate_label(i) for i in optimum)
            self.msg_detail(f"{names}만 골라도 전체가 덮인다. 탐욕 선택이 항상 최소 개수를 보장하지는 않는다.")
        self.draw()
        self.section_end()

    def _candidate_label(self, index):
        return f"S{index + 1}"

    def _element_label(self, value):
        return str(value)

    def _visible_elements(self, subset):
        return subset

    def _element(self, value, x, y, size, color):
        self.rect(x, y, size, size, colors.PANEL, color, radius=4)
        label = self._element_label(value)
        font_size = min(22, int(size * 0.55))
        if isinstance(value, tuple):
            font_size = min(font_size, int((size - 4) / (0.7 * len(label))))
        self.centered_text(label, x + size / 2, y + size / 2, font_size, color, True)

    def _draw_universe(self):
        self.text("전체 집합", 80, 128, 24, colors.BLUE, True)
        self.text(f"남은 원소: {len(self.uncovered)}개", 80, 175, 22)
        highlight = self.gains.get(self.best, set())
        for i, value in enumerate(self.universe):
            x, y = 80 + i % 8 * 65, 222 + i // 8 * 65
            color = colors.YELLOW if value in highlight or value == self.current_element else colors.TEXT if value in self.uncovered else colors.BORDER
            self._element(value, x, y, 52, color)

    def draw_content(self):
        if not hasattr(self, "universe"):
            return
        self.text(self.title, 65, 35, 42, bold=True)
        self._draw_universe()
        selected_top = 455 + self.graph_extra_height
        self.text("선택한 집합", 80, selected_top, 24, colors.GREEN, True)
        for index, selected in enumerate(self.chosen):
            x, y = 80 + index % 7 * 77, selected_top + 42 + index // 7 * 54
            self._element(self._candidate_label(selected), x, y, 52, colors.GREEN)
        self._draw_candidates()

    def _draw_candidates(self):
        self.text("후보 부분집합", self.candidate_left + 5, 128, 24, colors.BLUE, True)
        self.right_text("새로 덮는 수", 1515, 131, 20, colors.TEXT_MUTED)
        columns = 2 if len(self.subsets) > 14 else 1
        rows = max(1, (len(self.subsets) + columns - 1) // columns)
        width = (1520 - self.candidate_left) / columns
        row = min(57, 445 / rows)
        for i, subset in enumerate(self.subsets):
            x = self.candidate_left + (i // rows) * width
            y = 175 + (i % rows) * row
            selected = i in self.chosen
            active = i in (self.best, self.counting)
            accent = colors.GREEN if selected else colors.YELLOW if active else colors.BORDER
            self.rect(x, y, width - (5 if columns > 1 else 0), row - 5, colors.PANEL_DARK, accent, radius=5)
            self.centered_text(self._candidate_label(i), x + 32, y + (row - 5) / 2, 20, accent if selected or active else colors.TEXT, True)
            elements = self._visible_elements(subset)
            size = min(row - 11, (width - 140) / max(1, len(elements)) - 5, 40)
            for j, value in enumerate(elements):
                marked = i == self.best or (i == self.counting and value == self.current_element)
                color = colors.BORDER if value not in self.uncovered else colors.YELLOW if marked else colors.TEXT
                self._element(value, x + 72 + j * (size + 5), y + (row - 5 - size) / 2, size, color)
            count = "선택" if selected else str(self.tallies.get(i, "-"))
            self.centered_text(count, x + width - (34 if columns > 1 else 60), y + (row - 5) / 2,
                               18 if columns > 1 else 20, accent if selected or active else colors.TEXT, True)


class CitySetCoverVisualizer(SetCoverVisualizer):
    graph_width = 560

    def setup(self, data):
        self.vertices = getattr(data, "vertices", data.universe)
        super().setup(data)

    def _target_label(self):
        return "지점"

    def _edge_style(self, u, v, candidate, highlight):
        other = v if u == candidate else u if v == candidate else None
        emphasized = other is not None and (other in highlight or other == self.current_element)
        return (colors.YELLOW, 3) if emphasized else (colors.BORDER, 2)

    def _city_covered(self, city):
        return city not in self.uncovered

    def _graph_label(self):
        return "학교를 세울 지점"

    def _draw_universe(self):
        self.text(self._graph_label(), 80, 128, 24, colors.BLUE, True)
        self.text(f"아직 덮지 못한 {self._target_label()}: {len(self.uncovered)}개", 80, 175, 22)
        height = 226 + self.graph_extra_height
        self.rect(80, 210, self.graph_width, height, colors.PANEL_DARK, colors.BORDER, radius=5)
        x_scale = (self.graph_width - 60) / 100
        y_scale = (height - 51) / 100
        points = {city: (110 + x * x_scale, 235 + y * y_scale)
                  for city, (x, y) in zip(self.vertices, self.data.positions)}
        active = self.counting if self.counting is not None else self.best
        candidate = self.vertices[active] if active is not None else None
        highlight = self.gains.get(self.best, set())
        selected = {self.vertices[i] for i in self.chosen}
        radius_size = 10 if len(points) > 14 else 15
        for u, v in self.data.edges:
            color, width = self._edge_style(u, v, candidate, highlight)
            pygame.draw.line(self.screen, color,
                             self.view.point(*points[u]), self.view.point(*points[v]),
                             max(1, self.view.length(width)))
        for city, (x, y) in points.items():
            if city in selected:
                self.rect(x - radius_size - 4, y - radius_size, 2 * radius_size + 8, 2 * radius_size,
                          colors.GREEN, colors.GREEN, radius=4)
                self.centered_text(city, x, y, radius_size + 3, colors.BACKGROUND, True)
                continue
            active_city = city == candidate or city in highlight or city == self.current_element
            covered = self._city_covered(city)
            color = colors.YELLOW if active_city else colors.BORDER if covered else colors.TEXT
            fill = colors.BACKGROUND if covered else colors.PANEL
            center = self.view.point(x, y)
            radius = max(1, self.view.length(radius_size))
            pygame.draw.circle(self.screen, fill, center, radius)
            pygame.draw.circle(self.screen, color, center, radius, max(1, self.view.length(2)))
            self.centered_text(city, x, y, radius_size + 2, color, True)


class CoverComparisonVisualizer(CitySetCoverVisualizer):
    candidate_left = 820
    graph_width = 710
    mode = "vertices"
    explanation_hidden = False

    @property
    def cover_edges(self):
        return self.mode != "vertices"

    def setup(self, data):
        self.matching = []
        super().setup(data)

    def match_edge(self, edge):
        self.current_element = edge
        self.msg_phase("극대 매칭")
        self.msg_action(f"아직 덮지 못한 간선 {self._element_label(edge)}를 고른다.")
        self.msg_detail("이 간선의 양 끝 정점을 커버에 넣는다.")
        self.wait(850)
        if self.stopped():
            return

        self.matching.append(edge)
        self.chosen.extend(self.vertices.index(vertex) for vertex in edge)
        endpoints = set(edge)
        covered = {other for other in self.uncovered if not endpoints.isdisjoint(other)}
        self.uncovered.difference_update(covered)
        self.current_element = None
        self.msg_action(f"{self._element_label(edge)}의 양 끝 정점을 선택해 간선 {len(covered)}개를 덮었다.")
        self.msg_detail("파란색은 매칭에 넣은 간선이고 초록색은 함께 덮인 간선이다.")
        self.wait(950)
        self.section_end()

    def finish_matching(self):
        self.msg_phase("극대 매칭 결과")
        self.msg_action(f"매칭 간선 {len(self.matching)}개의 끝점 {len(self.chosen)}개로 모든 간선을 덮었다.")
        self.msg_detail(f"최적해도 매칭 간선마다 끝점이 하나씩 필요하다. 최적해는 적어도 {len(self.matching)}개다.")
        self.draw()
        self.section_end()

    @property
    def graph_extra_height(self):
        return 180 if self.explanation_hidden else 0

    def _handle_key(self, key, mod=0):
        if key == pygame.K_h:
            self.explanation_hidden = not self.explanation_hidden
        elif key == pygame.K_v and not self.stopped():
            self.requested_action = "toggle_cover"
        elif key == pygame.K_m and not self.stopped():
            self.requested_action = "toggle_matching"
        else:
            super()._handle_key(key, mod)

    def _candidate_label(self, index):
        return str(self.vertices[index])

    def _element_label(self, value):
        if isinstance(value, tuple):
            return "–".join(map(str, value))
        return super()._element_label(value)

    def _visible_elements(self, subset):
        if self.cover_edges:
            return [edge for edge in subset if edge in self.uncovered]
        return super()._visible_elements(subset)

    def _setup_action(self):
        if self.cover_edges:
            return "교차로에 CCTV를 설치해 연결된 골목길을 모두 비춘다."
        return "학교를 세워 해당 지점과 이웃 지점을 덮는다."

    def _graph_label(self):
        return "CCTV를 설치할 교차로" if self.cover_edges else super()._graph_label()

    def _target_label(self):
        return "간선" if self.cover_edges else "정점"

    def _edge_style(self, u, v, candidate, highlight):
        if not self.cover_edges:
            return super()._edge_style(u, v, candidate, highlight)
        edge = (u, v)
        if edge in highlight or edge == self.current_element:
            return colors.YELLOW, 4
        if edge in self.matching:
            return colors.BLUE, 5
        if edge not in self.uncovered:
            return colors.GREEN, 3
        return colors.BORDER, 2

    def _city_covered(self, city):
        return not self.cover_edges and super()._city_covered(city)

    def _draw_candidates(self):
        if self.mode != "matching":
            super()._draw_candidates()
            return
        self.text("매칭에 넣은 간선", self.candidate_left + 5, 128, 24, colors.BLUE, True)
        self.text("아직 덮지 못한 간선", self.candidate_left + 5, 305, 24, colors.TEXT, True)
        for edges, top, color in ((self.matching, 175, colors.BLUE), (sorted(self.uncovered), 352, colors.TEXT)):
            for i, edge in enumerate(edges):
                x = self.candidate_left + i % 12 * 57
                y = top + i // 12 * 52
                accent = colors.YELLOW if edge == self.current_element else color
                self._element(edge, x, y, 46, accent)

    def draw_content(self):
        super().draw_content()
        if hasattr(self, "universe"):
            mode_label = "극대 매칭" if self.mode == "matching" else f"정점 → {self._target_label()}"
            self.text(mode_label, 80, 92, 22, colors.YELLOW, True)
            self.text("[V] 커버 전환   [M] 극대 매칭", 285, 92, 20, colors.TEXT_MUTED)
            graph_action = "축소" if self.explanation_hidden else "확대"
            self.text(f"[H] 그래프 {graph_action}", 630, 92, 20, colors.TEXT_MUTED)

    def _draw_messages(self):
        if not self.explanation_hidden:
            super()._draw_messages()
