"""미포함 원소와 각 후보가 새로 덮을 원소를 함께 표시한다."""

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class SetCoverVisualizer(BaseVisualizer):
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
        self.msg_action("전체 집합을 덮을 부분집합을 고른다.")
        self.wait(900)

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
            self.msg_action(f"S{index + 1}이 새로 덮는 원소를 센다.")
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
        self.msg_action(f"현재 미포함 원소를 S{best + 1}이 가장 많이 덮는다: {len(gains[best])}개."
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
        self.msg_action(f"S{best + 1} 선택: {', '.join(map(str, sorted(covered)))}을 새로 덮었다.")
        self.msg_detail("이미 덮은 원소는 다음 후보를 평가할 때 다시 세지 않는다.")
        self.wait(950)
        self.section_end()

    def finish(self, uncovered):
        self.msg_phase("결과")
        if uncovered:
            self.msg_action(f"끝까지 덮지 못한 원소: {', '.join(map(str, sorted(uncovered)))}")
        else:
            self.msg_action(f"부분집합 {len(self.chosen)}개로 전체를 덮었다.")
        optimum = getattr(self.data, "optimal_cover", None)
        if optimum is not None:
            names = ", ".join(f"S{i + 1}" for i in optimum)
            self.msg_detail(f"{names}만 골라도 전체가 덮인다. 탐욕 선택이 항상 최소 개수를 보장하지는 않는다.")
        self.draw()
        self.section_end()

    def _element(self, value, x, y, size, color):
        self.rect(x, y, size, size, colors.PANEL, color, radius=4)
        self.centered_text(value, x + size / 2, y + size / 2, min(22, int(size * 0.55)), color, True)

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
        self.text("후보 부분집합", 695, 128, 24, colors.BLUE, True)
        self.right_text("새로 덮는 수", 1515, 131, 20, colors.TEXT_MUTED)
        self.text("선택한 집합", 80, 455, 24, colors.GREEN, True)
        for index, selected in enumerate(self.chosen):
            x, y = 80 + index % 7 * 77, 497 + index // 7 * 54
            self._element(f"S{selected + 1}", x, y, 52, colors.GREEN)
        columns = 2 if len(self.subsets) > 14 else 1
        rows = max(1, (len(self.subsets) + columns - 1) // columns)
        width = 830 / columns
        row = min(57, 445 / rows)
        for i, subset in enumerate(self.subsets):
            x = 690 + (i // rows) * width
            y = 175 + (i % rows) * row
            selected = i in self.chosen
            active = i in (self.best, self.counting)
            accent = colors.GREEN if selected else colors.YELLOW if active else colors.BORDER
            self.rect(x, y, width - (5 if columns > 1 else 0), row - 5, colors.PANEL_DARK, accent, radius=5)
            self.centered_text(f"S{i + 1}", x + 32, y + (row - 5) / 2, 20, accent if selected or active else colors.TEXT, True)
            size = min(row - 11, (width - 140) / max(1, len(subset)) - 5, 40)
            for j, value in enumerate(subset):
                marked = i == self.best or (i == self.counting and value == self.current_element)
                color = colors.BORDER if value not in self.uncovered else colors.YELLOW if marked else colors.TEXT
                self._element(value, x + 72 + j * (size + 5), y + (row - 5 - size) / 2, size, color)
            count = "선택" if selected else str(self.tallies.get(i, "-"))
            self.centered_text(count, x + width - (34 if columns > 1 else 60), y + (row - 5) / 2,
                               18 if columns > 1 else 20, accent if selected or active else colors.TEXT, True)


class CitySetCoverVisualizer(SetCoverVisualizer):
    def _draw_universe(self):
        self.text("학교를 세울 지점", 80, 128, 24, colors.BLUE, True)
        self.text(f"아직 덮지 못한 지점: {len(self.uncovered)}개", 80, 175, 22)
        self.rect(80, 210, 560, 226, colors.PANEL_DARK, colors.BORDER, radius=5)
        points = {city: (110 + x * 5, 235 + y * 1.75)
                  for city, (x, y) in zip(self.data.universe, self.data.positions)}
        active = self.counting if self.counting is not None else self.best
        candidate = self.data.universe[active] if active is not None else None
        highlight = self.gains.get(self.best, set())
        selected = {self.data.universe[i] for i in self.chosen}
        radius_size = 10 if len(points) > 14 else 15
        for u, v in self.data.edges:
            other = v if u == candidate else u if v == candidate else None
            emphasized = other is not None and (other in highlight or other == self.current_element)
            pygame.draw.line(self.screen, colors.YELLOW if emphasized else colors.BORDER,
                             self.view.point(*points[u]), self.view.point(*points[v]),
                             max(1, self.view.length(3 if emphasized else 2)))
        for city, (x, y) in points.items():
            if city in selected:
                self.rect(x - radius_size - 4, y - radius_size, 2 * radius_size + 8, 2 * radius_size,
                          colors.GREEN, colors.GREEN, radius=4)
                self.centered_text(city, x, y, radius_size + 3, colors.BACKGROUND, True)
                continue
            active_city = city == candidate or city in highlight or city == self.current_element
            covered = city not in self.uncovered
            color = colors.YELLOW if active_city else colors.BORDER if covered else colors.TEXT
            fill = colors.BACKGROUND if covered else colors.PANEL
            center = self.view.point(x, y)
            radius = max(1, self.view.length(radius_size))
            pygame.draw.circle(self.screen, fill, center, radius)
            pygame.draw.circle(self.screen, color, center, radius, max(1, self.view.length(2)))
            self.centered_text(city, x, y, radius_size + 2, color, True)
