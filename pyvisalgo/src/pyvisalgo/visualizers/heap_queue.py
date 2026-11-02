"""실제 heapq 결과에 맞추어 up-heap과 down-heap의 원리를 연출한다."""

import copy
import math
import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class HeapQueueVisualizer(BaseVisualizer):
    def setup(self, data, array):
        self.msg_clear()
        self.set_data_info(data)
        self.values = copy.deepcopy(array)
        self.returned = []
        self.negated = getattr(data, "element_type", "int") == "negated"
        self.capacity = max(1, len(array) + len(data.pushes))
        self.motion = None
        self.operation = "heap = array.copy()"
        self.focus = None
        self.comparing = set()
        self.travel = None
        self.msg_phase("배열 준비")
        self.msg_action("아직 heapify하지 않은 배열이다.")
        self.msg_detail("부모와 자식을 연결해도 아직 최소 힙 조건을 만족하지 않을 수 있다.")
        self.draw()

    def heapify(self, array):
        self.operation = "heapq.heapify(heap)"
        self.msg_phase("heapify")
        self.msg_action("배열 전체를 최소 힙으로 바꾼다.")
        self.msg_detail("부모 ≤ 자식이지만, 배열 전체가 오름차순으로 정렬되는 것은 아니다.")
        self.wait(1300)
        self._transition(self.values, array)
        self._end_operation()

    def push(self, array, value):
        self.operation = f"heappush(heap, {value!r})"
        self.msg_phase("heappush")
        self.msg_action(f"{value!r}을 추가하고 최소 힙 조건을 유지한다.")
        self.msg_detail("마지막 칸에 넣은 뒤 부모와 비교하며 올라간다: up-heap.")
        before = copy.deepcopy(self.values) + [copy.deepcopy(value)]
        self.values = before
        self.focus = len(before) - 1
        self.wait(650)
        child = len(before) - 1
        while child > 0 and not self.stopped():
            parent = (child - 1) // 2
            self.comparing = {child, parent}
            self.msg_action(f"추가한 {self.values[child]!r}과 부모 {self.values[parent]!r}을 비교한다.")
            self.wait(650)
            if not self.values[child] < self.values[parent]:
                self.msg_detail("부모보다 작지 않으므로 여기서 멈춘다.")
                self.wait(650)
                break
            self.msg_detail("부모보다 작으므로 부모 쪽으로 한 단계 올라간다.")
            self._swap(child, parent, "up-heap ↑")
            child = parent
        self.values = copy.deepcopy(array)
        self._end_operation()

    def pop(self, array, value):
        self.operation = "value = heapq.heappop(heap)"
        self.msg_phase("heappop")
        interpreted = f" → 원래 값 {-value}" if self.negated else ""
        self.msg_action(f"루트의 최솟값 {value!r}{interpreted}을 꺼낸다.")
        self.msg_detail("남은 원소들로 최소 힙을 유지한다. 반환값은 오른쪽에 모은다.")
        self.focus = 0
        self.wait(700)
        # 루트만 반환하고, 마지막 원소를 빈 루트 자리로 옮긴다.
        before = copy.deepcopy(self.values)
        remaining = before[1:-1]
        replacement = [before[-1]] + remaining if len(before) > 1 else []
        mapping = {i: i for i in range(1, len(before) - 1)}
        if len(before) > 1:
            mapping[len(before) - 1] = 0
        self.msg_detail("마지막 원소가 루트의 빈자리를 채운다.")
        self._transition(before, replacement, popped=True, mapping=mapping)
        self.returned.append(copy.deepcopy(value))
        self.msg_stats(f"힙 {len(self.values)}개 / 반환 {len(self.returned)}개")
        parent = 0
        while 2 * parent + 1 < len(self.values) and not self.stopped():
            child = 2 * parent + 1
            right = child + 1
            self.comparing = {child}
            if right < len(self.values):
                self.comparing.add(right)
                self.msg_action(f"두 자식 {self.values[child]!r}, {self.values[right]!r} 중 작은 쪽을 고른다.")
                self.msg_detail("두 자식이 같으면 오른쪽 자식을 고른다.")
                self.wait(650)
                if not self.values[child] < self.values[right]:
                    child = right
            self.comparing = {parent, child}
            self.msg_action(f"부모 {self.values[parent]!r}과 작은 자식 {self.values[child]!r}을 비교한다.")
            self.msg_detail("작은 자식을 올리고, 루트를 채웠던 값은 자식 쪽으로 내려간다.")
            self.wait(650)
            if self.values[parent] < self.values[child]:
                self.msg_detail("부모가 더 작으므로 내려갈 필요가 없다.")
                self.wait(650)
                break
            # 동률일 때도 자식을 올리면 heapq의 결과 배열과 같은 배치가 된다.
            self._swap(parent, child, "down-heap ↓")
            parent = child
        self.values = copy.deepcopy(array)
        self._end_operation()

    def _swap(self, source, destination, label):
        before = copy.deepcopy(self.values)
        after = copy.deepcopy(before)
        after[source], after[destination] = after[destination], after[source]
        mapping = {i: i for i in range(len(before))}
        mapping[source], mapping[destination] = destination, source
        self.travel = (source, destination, label)
        try:
            self._transition(before, after, mapping=mapping)
        finally:
            self.travel = None

    def _end_operation(self):
        self.focus = None
        self.comparing = set()
        self.msg_stats(f"힙 {len(self.values)}개 / 반환 {len(self.returned)}개")
        self.wait(950)
        self.section_end()

    @staticmethod
    def match_positions(before, after, popped=False):
        # 리스트 원소는 hashable하지 않다. 작은 수업용 배열에서 동등 비교로 대응시킨다.
        # 중복값도 한 번만 소비하고, pop된 루트는 대응 대상에서 제외한다.
        unused = list(range(1 if popped else 0, len(before)))
        mapping = {}
        for destination, value in enumerate(after):
            source = next(i for i in unused if before[i] == value)
            unused.remove(source)
            mapping[source] = destination
        return mapping

    def _transition(self, before, after, popped=False, mapping=None):
        before, after = copy.deepcopy(before), copy.deepcopy(after)
        if mapping is None:
            mapping = self.match_positions(before, after, popped)
        self.motion = (before, after, mapping, popped, 0)
        try:
            for frame in range(46):
                if self.stopped() or self.running_to_section or self.is_max_speed():
                    break
                t = frame / 45
                self.motion = (before, after, mapping, popped, t * t * (3 - 2 * t))
                self.wait(24)
        finally:
            self.values = after
            self.motion = None
        self.draw()

    def _tree_position(self, index):
        level = (index + 1).bit_length() - 1
        slot = index - (2 ** level - 1)
        return 55 + (slot + 0.5) * 1110 / 2 ** level, 175 + level * 83

    def _array_position(self, index):
        width = min(130, 1460 / self.capacity)
        return 70 + (index + 0.5) * width, 566

    @staticmethod
    def _between(a, b, t):
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t

    def _label(self, value):
        return repr(value) if isinstance(value, (tuple, list)) else str(value)

    def _moving_position(self, source, target, t, tree=True):
        position = self._tree_position if tree else self._array_position
        a, b = position(source), position(target)
        x, y = self._between(a, b, t)
        if self.travel is not None and source != target:
            # 교환되는 두 원소가 같은 직선 위에서 겹치지 않게 반대쪽으로 비킨다.
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = (dx * dx + dy * dy) ** 0.5
            bend = math.sin(math.pi * t) * (75 if tree else 32)
            x -= dy / length * bend
            y += dx / length * bend
        return x, y

    def _value(self, value, x, y, width, color=colors.TEXT):
        label = self._label(value)
        size = 24 if isinstance(value, int) else 19
        while size > 10 and self.font(size, True).size(label)[0] > self.view.length(width):
            size -= 1
        self.centered_text(label, x, y, size=size, color=color, bold=True)
        if self.negated:
            self.centered_text(f"원래 {-value}", x, y + 22, size=13, color=colors.TEXT_MUTED)

    def _edges(self, values):
        for child in range(1, len(values)):
            parent = (child - 1) // 2
            color = colors.BORDER if values[parent] <= values[child] else colors.RED
            pygame.draw.line(self.screen, color, self.view.point(*self._tree_position(parent)),
                             self.view.point(*self._tree_position(child)), max(1, self.view.length(2)))

    def _node(self, value, index, position=None, active=False):
        x, y = position or self._tree_position(index)
        structured = isinstance(value, (list, tuple))
        width = 118 if structured else 68
        height = 64 if self.negated else 48
        self.rect(x - width / 2, y - 24, width, height, colors.PANEL,
                  colors.ORANGE if active else colors.BLUE, radius=6)
        self._value(value, x, y, width - 8)
        if position is None:
            self.centered_text(f"#{index}", x, y + height - 15, size=13, color=colors.TEXT_MUTED)

    def _draw_travel(self):
        if self.travel is None:
            return
        source, destination, label = self.travel
        a = self._tree_position(source)
        b = self._tree_position(destination)
        # 움직이는 원소와 겹치지 않도록 간선 옆에 방향 화살표를 표시한다.
        start = self._between(a, b, 0.25)
        end = self._between(a, b, 0.75)
        start = (start[0] + 42, start[1])
        end = (end[0] + 42, end[1])
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / length, dy / length
        pygame.draw.line(self.screen, colors.YELLOW, self.view.point(*start), self.view.point(*end), self.view.length(4))
        tip1 = (end[0] - ux * 16 - uy * 8, end[1] - uy * 16 + ux * 8)
        tip2 = (end[0] - ux * 16 + uy * 8, end[1] - uy * 16 - ux * 8)
        pygame.draw.polygon(self.screen, colors.YELLOW, [self.view.point(*p) for p in (end, tip1, tip2)])
        self.text(label, 900, 98, size=24, color=colors.YELLOW, bold=True)

    def draw_content(self):
        if not hasattr(self, "values"):
            return
        self.text("heapq", 65, 40, size=44, bold=True)
        subtitle = "음수로 저장하여 원래 값의 최댓값을 꺼낸다." if self.negated else "최소 힙: 부모 ≤ 자식 / 루트는 최솟값"
        self.text(subtitle, 65, 98, size=23, color=colors.TEXT_MUTED)
        self.text("호출", 1210, 150, size=22, color=colors.BLUE, bold=True)
        # 긴 튜플도 오른쪽 영역을 넘지 않도록 호출명을 두 줄로 분리한다.
        operation = self.operation.replace("heapq.", "")
        if len(operation) > 25:
            first, _, rest = operation.partition("(")
            self.text(first + "(", 1210, 188, size=18)
            self.text(rest, 1210, 215, size=17)
        else:
            self.text(operation, 1210, 188, size=18)
        self.text("반환값", 1210, 280, size=23, color=colors.GREEN, bold=True)
        for index, value in enumerate(self.returned):
            label = self._label(value)
            if self.negated:
                label += f" → {-value}"
            self.text(label, 1220, 323 + index * 43, size=21)
        self.text("heap 배열", 65, 510, size=22, color=colors.BLUE, bold=True)
        cell_width = min(130, 1460 / self.capacity)
        for index in range(self.capacity):
            x, y = self._array_position(index)
            self.rect(x - cell_width / 2 + 3, y - 27, cell_width - 6, 65 if self.negated else 52,
                      colors.PANEL_DARK, colors.BORDER, radius=4)
            self.centered_text(f"#{index}", x, 615, size=13, color=colors.TEXT_MUTED)
        if self.motion is None:
            self._edges(self.values)
            for index, value in enumerate(self.values):
                self._node(value, index, active=index == self.focus or index in self.comparing)
                self._value(value, *self._array_position(index), cell_width - 12)
        else:
            before, after, mapping, popped, t = self.motion
            self._edges(after)
            for source, target in mapping.items():
                self._node(before[source], source,
                           self._moving_position(source, target, t), source != target)
                self._value(before[source], *self._moving_position(source, target, t, tree=False),
                            cell_width - 12, colors.ORANGE if source != target else colors.TEXT)
            if popped:
                destination = (1320, 333 + len(self.returned) * 43)
                self._node(before[0], 0, self._between(self._tree_position(0), destination, t), True)
        self._draw_travel()
