"""Kruskal의 간선을 가중치에 비례하는 세로선으로 모아 정렬한다."""

import pygame

from ..core import colors
from .graph_representation import GraphRepresentationVisualizer, graph_representations
from ..core.visualizer import BaseVisualizer


class KruskalVisualizer(GraphRepresentationVisualizer):
    panel_left = 1245
    panel_width = 275
    @property
    def root_table_rows(self):
        return 18 if self.hidden else 8

    @property
    def root_row_height(self):
        return 24 if self.hidden else 30

    def setup(self, data, roots=None):
        super().setup(data)
        self.plane_rect = (45, 140, 1140, 260)
        self.fit_button = (1139, 148, 32, 32)
        self.reset_plane()
        self.bar_edges = list(self.edges)
        self.bar_slots = list(range(len(self.edges)))
        self.collected = 0
        self.collection_finished = False
        self.edge_indices = {tuple(sorted(edge[:2])): i for i, edge in enumerate(self.bar_edges)}
        self.edge_motion = None
        self.sorting = False
        self.selected_edges = set()
        self.return_motion = None
        self.current_edge = None
        self.rejected_edges = set()
        self.root_values = list(range(len(self.names))) if roots is None else list(roots)
        self.root_focus = None
        self.root_changed = set()
        self.root_stack = []
        self.root_trace = []
        self.root_results = []
        self.root_scroll = 0
        self.union_change = None
        self.hovered_city = None

    def _handle_key(self, key, mod=0):
        if key != pygame.K_TAB:
            super()._handle_key(key, mod)

    def _action_hint(self):
        return "L: 배치  H: 설명  휠: 확대/축소  정점 드래그: 배치  빈 곳 드래그: 이동  R: 재실행  D: 데이터  Esc: 종료"

    def _running_hint(self):
        return "Space: 일시정지  .: 한 단계  Enter: 다음 구간  L: 배치  H: 설명  D: 데이터  R: 재실행  Esc: 종료"

    def _reveal_active(self):
        # 오른쪽은 더 이상 간선 목록이 아니므로 간선 순번으로 스크롤하지 않습니다.
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            x, _ = self._logical_mouse(pygame.mouse.get_pos())
            if x >= self.panel_left - 20:
                self.root_scroll = max(0, min(max(0, len(self.names) - self.root_table_rows), self.root_scroll - event.y))
                return
        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            point = self._logical_mouse(event.pos)
            self.hovered_city = None
            if self.plane_screen_rect().collidepoint(event.pos):
                candidates = [(pygame.Vector2(point).distance_to(self._screen_point(vertex)), vertex)
                              for vertex in range(len(self.names))]
                distance, vertex = min(candidates)
                if distance <= 23:
                    self.hovered_city = vertex
                    self.hovered = ("vertex", vertex)
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.hovered_city = None
            self.hovered = None

    def _hovered_root(self):
        if self.hovered_city is None:
            return None
        # 마우스 확인은 경로를 따라가기만 합니다. 경로 압축이나 배열 갱신은 하지 않습니다.
        root = self.hovered_city
        while self.root_values[root] != root:
            root = self.root_values[root]
        return root

    def _draw_messages(self):
        if self.hidden:
            self.text("H: 설명 표시   L: 배치   휠: 확대/축소   정점 드래그: 배치   빈 곳 드래그: 이동",
                      45, 862, 18, colors.TEXT_MUTED)
        else:
            BaseVisualizer._draw_messages(self)

    def _reveal_root(self, vertex):
        self.root_scroll = max(0, min(max(0, len(self.names) - self.root_table_rows),
                                      vertex - self.root_table_rows // 2))

    def start(self, roots):
        """알고리즘의 초기 집합 배열과 준비 안내를 표시한다."""
        self.root_values = list(roots)
        self.msg_phase("Kruskal: 그래프 준비")
        self.msg_action("모든 정점을 연결할 간선을 선택할 준비를 한다.")
        self.msg_detail("가벼운 간선부터 검사하며, 사이클을 만들지 않는 간선만 선택한다.")
        self.msg_stats(f"정점 {len(roots)}개 / 선택한 간선 0개 / 현재 비용 0")
        self.wait(1000)

    def begin_edge(self, u, v):
        self.active = self.current_edge = tuple(sorted((u, v)))
        self.root_results = []
        self.root_trace = []
        self.root_changed = set()
        self.union_change = None

    def root_enter(self, vertex, roots):
        if not self.root_stack:
            self.root_trace = []
        self.root_values = list(roots)
        frame = {"vertex": vertex, "depth": len(self.root_stack), "result": None}
        self.root_stack.append(frame)
        self.root_trace.append(frame)
        self.root_focus = vertex
        self.root_changed = set()
        self._reveal_root(vertex)
        self.msg_phase("Union-Find: 재귀 호출")
        self.msg_action(f"getRoot({vertex}): roots[{vertex}] = {roots[vertex]}를 확인한다.")
        self.msg_detail("자기 자신이면 루트다. 그렇지 않으면 기록된 정점으로 재귀 호출한다.")
        self.wait(700)

    def root_return(self, vertex, root, roots, is_root=False, shortcut=True):
        before = self.root_values[vertex]
        self.root_values = list(roots)
        self.root_focus = vertex
        self.root_changed = {vertex} if before != roots[vertex] else set()
        frame = self.root_stack[-1]
        frame["result"] = root
        self._reveal_root(vertex)
        self.msg_phase("Union-Find: 루트 발견" if is_root else
                       "Union-Find: 리턴과 경로 압축" if shortcut else "Union-Find: 재귀 반환")
        if is_root:
            self.msg_action(f"roots[{vertex}] == {vertex}: 루트 {root}를 반환한다.")
            self.msg_detail("이 값이 이전 재귀 호출로 차례로 돌아간다.")
        elif not shortcut:
            self.msg_action(f"getRoot({vertex})가 루트 {root}를 반환한다.")
            self.msg_detail(f"roots[{vertex}] = {roots[vertex]}는 바꾸지 않는다. 이번에는 반환만 한다.")
        else:
            self.msg_action(f"roots[{vertex}] = {root}를 기록하고 {root}를 반환한다.")
            self.msg_detail(f"shortcut: {before} → {root}" if before != root else
                            "이미 루트를 직접 가리키므로 기록해도 값은 그대로다.")
        self.wait(900)
        self.root_stack.pop()
        if not self.root_stack:
            self.root_results.append((vertex, root))
            self.root_results = self.root_results[-2:]

    def union_roots(self, root_u, root_v, roots):
        changed = {i for i, value in enumerate(roots) if self.root_values[i] != value}
        vertex = next(iter(changed), None)
        if vertex is None:
            return
        before, after = self.root_values[vertex], roots[vertex]
        self.root_changed = set()
        self.root_focus = vertex
        self._reveal_root(vertex)
        self.root_trace = []
        self.union_change = (vertex, before, after, False)
        self.msg_phase("Union-Find: 집합 합치기")
        self.msg_path("")
        self.msg_action(f"간선을 확정했으므로 대표 {root_u}와 {root_v}의 집합을 합친다.")
        self.msg_detail(f"변경 전: roots[{vertex}] = {before}. 대표 {vertex}가 대표 {after}를 가리키게 한다.")
        self.wait(1000)
        # 학생 코드의 갱신 결과를 변경 전 상태와 분리해서 보여줍니다.
        self.root_values = list(roots)
        self.root_changed = changed
        self.union_change = (vertex, before, after, True)
        self.msg_action(f"roots[{vertex}]를 {before}에서 {after}로 바꿨다.")
        self.msg_detail("두 집합이 하나가 되었다. 다음 간선부터는 합쳐진 집합을 기준으로 검사한다.")
        self.wait(1200)
        self.section_end()

    def _toggle_explanation(self):
        super()._toggle_explanation()
        x, y, width, height = self.plane_rect
        self.plane_rect = (x, y, 1140, height - 220)
        self.fit_button = (1139, y + 8, 32, 32)
        self.reset_plane()
        if self.root_focus is not None:
            self._reveal_root(self.root_focus)
        else:
            self.root_scroll = min(self.root_scroll, max(0, len(self.names) - self.root_table_rows))

    def _bar_segment(self, edge, slot):
        count = len(self.bar_edges)
        x = 85 + (slot + .5) * 1055 / max(1, count)
        baseline = 785 if self.hidden else 570
        maximum = max((abs(w) for _, _, w in self.bar_edges), default=1) or 1
        height = 110 * abs(edge[2]) / maximum
        return (x, baseline - height), (x, baseline)

    def _animate(self, update, milliseconds):
        # wait에서 이벤트를 처리하며, 빠르게 진행할 때도 끝 위치를 확정합니다.
        for frame in range(31):
            if self.stopped():
                return
            progress = frame / 30
            if self.running_to_section or self.is_max_speed():
                progress = 1
            update(progress * progress * (3 - 2 * progress))
            self.wait(milliseconds / 30)
            if progress == 1:
                return

    def sort_edges(self, sorted_edges):
        """학생 코드가 정렬한 결과를 받아 표시하며 입력은 변경하지 않는다."""
        self.msg_phase("Kruskal: 간선 정렬")
        for index, (u, v, weight) in enumerate(self.bar_edges):
            if self.stopped():
                return
            self.active = tuple(sorted((u, v)))
            self.msg_action(f"#{u}와 #{v}의 간선을 아래로 모은다.")
            self.msg_detail(f"파란 간선이 아래로 이동한다. 원래 자리에는 회색 간선이 남는다. 가중치는 {weight}이다.")
            self._animate(lambda t: setattr(self, "edge_motion", (index, t)), 650)
            self.collected = index + 1
            self.edge_motion = None
        self.collection_finished = True
        self.active = None
        self.msg_action("모든 간선을 아래로 모았다.")
        self.msg_detail("다음 구간에서 간선을 가중치 오름차순으로 정렬한다.")
        # 수집 중 Enter를 눌러도 정렬 애니메이션까지 건너뛰지 않습니다.
        self.section_end()
        if self.stopped():
            return
        self.wait(800)
        self.msg_action("간선을 가중치 오름차순으로 정렬한다.")
        self.msg_detail("같은 가중치의 간선은 입력 순서를 유지한다. 아직 간선을 선택하지는 않는다.")
        ranks = {tuple(sorted((u, v))): i for i, (u, v, _) in enumerate(sorted_edges)}
        targets = [ranks[tuple(sorted((u, v)))] for u, v, _ in self.bar_edges]
        starts = list(self.bar_slots)
        self.sorting = True
        self._animate(lambda t: setattr(self, "bar_slots", [a + (b - a) * t
                      for a, b in zip(starts, targets)]), 1200)
        self.bar_slots = targets
        self.edges = [tuple(edge) for edge in sorted_edges]
        self.forms = graph_representations(len(self.names), self.edges)
        self.sorting = False
        self.wait(800)
        self.section_end()

    def select_edge(self, u, v, weight, total_cost):
        """선택한 간선을 아래 후보 줄에서 원래 그래프로 이동한다."""
        key = tuple(sorted((u, v)))
        index = next(i for i, edge in enumerate(self.bar_edges)
                     if tuple(sorted(edge[:2])) == key)
        self.active = key
        self.current_edge = key
        self._reveal_active()
        self.msg_phase("Kruskal: 간선 선택")
        self.msg_action(f"#{u}와 #{v}의 간선(가중치 {weight})을 선택한다.")
        self.msg_detail("가중치가 작은 순서로 간선을 선택해 연결 비용을 누적한다.")
        self._animate(lambda t: setattr(self, "return_motion", (index, t)), 900)
        self.return_motion = None
        if self.stopped():
            return
        self.selected_edges.add(key)
        self.msg_stats(f"정점 {len(self.names)}개 / 선택한 간선 {len(self.selected_edges)}개 / 현재 비용 {total_cost}")
        self.wait(800)
        self.section_end()

    def check_roots(self, u, v, root_u, root_v, roots):
        self.active = self.current_edge = tuple(sorted((u, v)))
        self._reveal_active()
        self.msg_phase("Kruskal: 사이클 검사")
        self.msg_action(f"#{u}의 대표 {root_u}와 #{v}의 대표 {root_v}를 비교한다.")
        self.msg_detail("대표가 같으면 이미 연결되어 있으므로 이 간선을 추가하면 사이클이 생긴다.")
        self.root_values = list(roots)
        self.msg_path(f"getRoot({u}) = {root_u} / getRoot({v}) = {root_v}")
        self.wait(1000)

    def reject_edge(self, u, v, weight):
        self.active = self.current_edge = tuple(sorted((u, v)))
        self._reveal_active()
        self.rejected_edges.add(self.current_edge)
        self.msg_phase("Kruskal: 간선 제외")
        self.msg_action(f"#{u}와 #{v}의 간선(가중치 {weight})을 건너뛴다.")
        self.msg_detail("두 정점은 이미 같은 집합이다. 사이클을 만드는 간선은 빨간색으로 남긴다.")
        self.wait(1200)
        self.section_end()

    def finish_mst(self, count, mst, total_cost):
        self.active = self.current_edge = None
        self.msg_phase("Kruskal: 결과")
        if len(mst) == count - 1:
            self.msg_action(f"최소 신장 트리를 완성했다. 최소 비용은 {total_cost}이다.")
            self.msg_detail("사이클 없이 모든 정점을 연결하는 간선 n-1개를 선택했다.")
        else:
            self.msg_action("연결되지 않은 그래프이므로 전체 최소 신장 트리는 없다.")
            self.msg_detail(f"각 연결 요소의 최소 신장 트리인 최소 신장 숲을 구했다. 비용 합은 {total_cost}이다.")
        self.msg_stats(f"정점 {count}개 / 선택한 간선 {len(mst)}개 / 현재 비용 {total_cost}")
        self.msg_path("")

    def _edge_color(self, u, v):
        if not self.collection_finished:
            index = self.edge_indices[tuple(sorted((u, v)))]
            moving = self.edge_motion is not None and self.edge_motion[0] == index
            return colors.BLUE if index >= self.collected and not moving else colors.BORDER
        return super()._edge_color(u, v)

    def _draw_graph(self):
        super()._draw_graph()
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        for u, v, weight in self.edges:
            key = tuple(sorted((u, v)))
            if key not in self.selected_edges and key not in self.rejected_edges:
                continue
            color = colors.RED if key in self.rejected_edges else colors.GREEN
            a, b = self._screen_point(u), self._screen_point(v)
            length = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** .5
            if length > 44:
                start = tuple(x + (y - x) * 22 / length for x, y in zip(a, b))
                end = tuple(y + (x - y) * 22 / length for x, y in zip(a, b))
                pygame.draw.line(self.screen, color, self.view.point(*start),
                                 self.view.point(*end), self.view.length(4))
            x, y = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            self.rect(x - 22, y - 14, 44, 28, colors.BACKGROUND, color, radius=4)
            self.centered_text(weight, x, y, 18, color)
        self.screen.set_clip(previous)

    def _draw_hovered_city(self):
        root = self._hovered_root()
        if root is None:
            return
        previous = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        x, y = self._screen_point(self.hovered_city)
        pygame.draw.circle(self.screen, colors.ORANGE, self.view.point(x, y), self.view.length(21))
        self.centered_text(self.hovered_city, x, y, 22, colors.BACKGROUND, bold=True)
        # 같은 도시여도 배경색과 바깥 원 테두리가 함께 보입니다.
        x, y = self._screen_point(root)
        pygame.draw.circle(self.screen, colors.YELLOW, self.view.point(x, y),
                           self.view.length(26), self.view.length(3))
        self.screen.set_clip(previous)

    def draw_content(self):
        super().draw_content()
        if not self.hidden:
            pygame.draw.rect(self.screen, colors.BACKGROUND, self.view.rect(45, 20, 850, 100))
            self.text("Kruskal: Minimum Spanning Tree", 45, 25, 32, bold=True)
            self.text("간선의 가중치를 비교한다. 화면상의 거리는 사용하지 않는다.", 45, 83, 20, colors.TEXT_MUTED)
        self._draw_bars()
        self._draw_hovered_city()
        self._draw_mst_progress()

    def _draw_mst_progress(self):
        count = len(self.names)
        selected = len(self.selected_edges)
        target = count - 1
        label = f"정점 {count}개 | 선택한 간선 {selected} / {target}개"
        size = 19
        width = self.font(size).size(label)[0] / self.view.scale
        button_x, button_y, _, _ = self.fit_button
        x, y = button_x - width - 24, button_y + 5
        pygame.draw.rect(self.screen, colors.BACKGROUND,
                         self.view.rect(x - 8, y - 4, width + 16, 32))
        self.text(label, x, y, size, colors.GREEN if selected == target else colors.TEXT)

    def _draw_representation(self):
        x = self.panel_left
        trace_top = 610 if self.hidden else 414
        trace_y = 648 if self.hidden else 449
        results_y = 790 if self.hidden else 586
        self.text("Union-Find", x, 30, 26, bold=True)
        hovered_root = self._hovered_root()
        if hovered_root is None:
            self.text("roots[i]: 다음 정점", x, 76, 18, colors.TEXT_MUTED)
        else:
            self.text(f"대상 #{self.hovered_city} / 루트 #{hovered_root}", x, 76, 18, colors.YELLOW)
            self._reveal_root(hovered_root)
        self.mono_text("i", x + 18, 112, 20, colors.BLUE)
        self.mono_text("roots[i]", x + 115, 112, 20, colors.BLUE)
        for row, vertex in enumerate(range(self.root_scroll, min(len(self.names), self.root_scroll + self.root_table_rows))):
            y = 143 + row * self.root_row_height
            color = (colors.YELLOW if vertex in self.root_changed else
                     colors.ORANGE if vertex == self.root_focus else colors.BORDER)
            self.rect(x, y, self.panel_width, self.root_row_height - 2, colors.PANEL, color, radius=0)
            font_size = 18 if self.hidden else 19
            text_top = y + (2 if self.hidden else 3)
            self.mono_text(f"#{vertex}", x + 18, text_top, font_size, colors.TEXT)
            value = str(self.root_values[vertex])
            if self.union_change is not None and self.union_change[0] == vertex and self.union_change[3]:
                value = f"{self.union_change[1]} -> {self.union_change[2]}"
            self.mono_text(value, x + 115, text_top, font_size,
                           color if color != colors.BORDER else colors.TEXT)
            self.hits.append(((x, y, self.panel_width, self.root_row_height - 2), ("vertex", vertex)))
            if vertex == hovered_root:
                pygame.draw.circle(self.screen, colors.YELLOW, self.view.point(x - 12, y + (self.root_row_height - 2) / 2),
                                   self.view.length(7), self.view.length(2))
            if vertex == self.hovered_city:
                pygame.draw.circle(self.screen, colors.ORANGE, self.view.point(x - 12, y + (self.root_row_height - 2) / 2),
                                   self.view.length(5))
        self.text("union: 집합 합치기" if self.union_change is not None else "재귀 호출 / 반환",
                  x, trace_top, 20, colors.BLUE, bold=True)
        if self.union_change is not None:
            vertex, before, after, done = self.union_change
            self.mono_text(f"roots[{vertex}] = {after}", x, trace_y, 20,
                           colors.YELLOW if done else colors.ORANGE)
            self.text(f"변경 전: {before}", x, trace_y + 37, 19, colors.TEXT_MUTED)
            self.text(f"변경 후: {after}" if done else f"연결할 대표: {after}", x, trace_y + 69, 19,
                      colors.YELLOW if done else colors.TEXT_MUTED)
        for offset, frame in enumerate(self.root_trace[-5:]):
            result = frame["result"]
            label = f"getRoot({frame['vertex']})"
            if result is not None:
                label += f" = {result}"
            indent = min(frame["depth"] * 14, 56)
            self.mono_text(label, x + indent, trace_y + offset * 24, 18,
                           colors.GREEN if result is not None else colors.ORANGE)
        for index, (vertex, root) in enumerate(self.root_results):
            self.mono_text(f"getRoot({vertex}) = {root}", x, results_y + index * 24, 18, colors.GREEN)

    def _draw_bars(self):
        for index, edge in enumerate(self.bar_edges):
            if tuple(sorted(edge[:2])) == self.current_edge:
                # 간선이 그래프로 이동한 뒤에도 후보 줄의 현재 위치를 남깁니다.
                _, (x, y) = self._bar_segment(edge, self.bar_slots[index])
                points = [(x - 8, y + 46), (x, y + 32), (x + 8, y + 46)]
                pygame.draw.polygon(self.screen, colors.ORANGE,
                                    [self.view.point(px, py) for px, py in points])
            if tuple(sorted(edge[:2])) in self.selected_edges:
                continue
            moving = self.edge_motion is not None and self.edge_motion[0] == index
            if index >= self.collected and not moving:
                continue
            hot = moving or self._highlight(edge[0], edge[1])
            color = colors.BLUE if moving else colors.ORANGE if hot else colors.BLUE
            rejected = tuple(sorted(edge[:2])) in self.rejected_edges
            if rejected:
                color = colors.RED
            a, b = self._bar_segment(edge, self.bar_slots[index])
            returning = self.return_motion is not None and self.return_motion[0] == index
            if returning:
                _, t = self.return_motion
                u, v, _ = edge
                end_a, end_b = self._screen_point(u), self._screen_point(v)
                a = tuple(x + (y - x) * t for x, y in zip(a, end_a))
                b = tuple(x + (y - x) * t for x, y in zip(b, end_b))
            if moving:
                _, t = self.edge_motion
                u, v, _ = edge
                start_a, start_b = self._screen_point(u), self._screen_point(v)
                a = tuple(x + (y - x) * t for x, y in zip(start_a, a))
                b = tuple(x + (y - x) * t for x, y in zip(start_b, b))
            pygame.draw.line(self.screen, color, self.view.point(*a), self.view.point(*b),
                             self.view.length(6 if hot else 4))
            self.centered_text(edge[2], a[0], a[1] - 15, 18,
                               colors.RED if rejected else colors.BLUE if moving else colors.ORANGE if hot else colors.TEXT)
            if not moving and not returning:
                self.centered_text(f"{edge[0]}-{edge[1]}", b[0], b[1] + 19, 16,
                                   colors.RED if rejected else colors.ORANGE if hot else colors.TEXT_MUTED)
