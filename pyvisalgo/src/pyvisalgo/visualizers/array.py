import math
import time

import pygame

from pyvisalgo.core import colors
from pyvisalgo.core.visualizer import BaseVisualizer


class FindMaxVisualizer(BaseVisualizer):
    def __init__(self, title="Find Max", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.max_index = None
        self.compare_index = None
        self.compare_count = 0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.max_index = None
        self.compare_index = None
        self.compare_count = 0
        self.msg_phase("최댓값 찾기")
        self.msg_action("배열을 준비한다.")
        self.msg_detail(f"{len(self.array)}개의 값을 왼쪽에서 오른쪽으로 확인한다.")
        self._update_stats()
        self.wait(700)

    def compare(self, index, max_index=None):
        self.compare_index = index
        if max_index is not None:
            self.max_index = max_index
        self.compare_count += 1
        self.msg_action(f"#{index}({self.array[index]}) 과 현재 최댓값 #{self.max_index}({self.array[self.max_index]}) 을 비교한다.")
        if self.array[index] > self.array[self.max_index]:
            self.msg_detail(f"{self.array[index]} 이 더 크므로 최댓값 후보를 바꾼다.")
        else:
            self.msg_detail(f"{self.array[self.max_index]} 이 더 크거나 같으므로 최댓값 후보를 유지한다.")
        self._update_stats()
        self.wait(900)

    def update_max(self, index):
        previous = self.max_index
        self.max_index = index
        self.compare_index = None
        if previous is None:
            self.msg_action(f"#{index}({self.array[index]}) 을 첫 최댓값 후보로 정한다.")
        else:
            self.msg_action(f"최댓값 후보를 #{previous}에서 #{index}({self.array[index]}) 로 바꾼다.")
        self.msg_detail("현재까지 확인한 값 중 가장 큰 값을 기억한다.")
        self._update_stats()
        self.wait(800)

    def finish(self, index):
        self.max_index = index
        self.compare_index = None
        self.msg_phase("완료")
        self.msg_action(f"최댓값은 #{index}({self.array[index]}) 이다.")
        self.msg_detail("모든 원소를 한 번씩 확인했으므로 탐색을 종료한다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("가장 큰 값을 저장해 두고, 나머지 값과 차례로 비교한다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count = len(self.array)
        gap = 18
        max_area_width = 1400
        box_width = min(120, (max_area_width - gap * (count - 1)) / count)
        box_height = 110
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 285

        for index, value in enumerate(self.array):
            x = start_x + index * (box_width + gap)
            fill = colors.PANEL
            border = colors.BORDER
            if index == self.max_index:
                fill = (35, 72, 52)
                border = colors.GREEN
            if index == self.compare_index:
                fill = (82, 55, 30)
                border = colors.ORANGE

            self.rect(x, top, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, top + box_height / 2, 34, colors.TEXT, True)
            self.centered_text(f"#{index}", x + box_width / 2, top + box_height + 36, 24, colors.TEXT_MUTED)

        if self.max_index is not None:
            max_x = start_x + self.max_index * (box_width + gap) + box_width / 2
            self.centered_text("현재 최댓값", max_x, top - 45, 24, colors.GREEN, True)

        if self.compare_index is not None:
            compare_x = start_x + self.compare_index * (box_width + gap) + box_width / 2
            self.centered_text("비교 중", compare_x, top + box_height + 78, 24, colors.ORANGE, True)

    def _draw_legend(self):
        self.rect(1020, 72, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("현재 최댓값 후보", 1066, 68, 24, colors.TEXT_MUTED)
        self.rect(1020, 112, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중인 원소", 1066, 108, 24, colors.TEXT_MUTED)

    def _update_stats(self):
        self.msg_stats(f"비교 {self.compare_count}회")


class SequentialSearchVisualizer(BaseVisualizer):
    def __init__(self, title="Sequential Search", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.target = None
        self.current_index = None
        self.found_index = None
        self.compare_count = 0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.target = data.target
        self.current_index = None
        self.found_index = None
        self.compare_count = 0
        self.msg_phase("순차 탐색")
        self.msg_action(f"찾을 값 {self.target} 을 왼쪽부터 차례로 찾는다.")
        self.msg_detail("각 원소를 목표값과 하나씩 비교한다.")
        self._update_stats()
        self.wait(700)

    def compare(self, index):
        self.current_index = index
        self.compare_count += 1
        self.msg_action(f"#{index}({self.array[index]}) 과 찾을 값 {self.target} 을 비교한다.")
        if self.array[index] == self.target:
            self.msg_detail("값이 같으므로 탐색에 성공한다.")
        else:
            self.msg_detail("값이 다르므로 다음 원소로 이동한다.")
        self._update_stats()
        self.wait(850)

    def found(self, index):
        self.found_index = index
        self.current_index = None
        self.msg_phase("완료")
        self.msg_action(f"{self.target} 은 #{index} 위치에 있다.")
        self.msg_detail("찾는 값을 발견했으므로 탐색을 종료한다.")
        self._update_stats()
        self.wait(1100)

    def not_found(self):
        self.current_index = None
        self.found_index = None
        self.msg_phase("완료")
        self.msg_action(f"{self.target} 을 찾지 못했다.")
        self.msg_detail("모든 원소를 확인했지만 같은 값이 없었다.")
        self._update_stats()
        self.wait(1100)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("목표값과 배열의 원소를 앞에서부터 하나씩 비교한다.", 72, 115, 26, colors.TEXT_MUTED)
        if self.target is not None:
            self.text(f"찾을 값: {self.target}", 72, 170, 30, colors.YELLOW, True)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count = len(self.array)
        gap = 18
        max_area_width = 1400
        box_width = min(120, (max_area_width - gap * (count - 1)) / count)
        box_height = 110
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 305

        for index, value in enumerate(self.array):
            x = start_x + index * (box_width + gap)
            fill = colors.PANEL
            border = colors.BORDER
            if index == self.current_index:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if index == self.found_index:
                fill = (35, 72, 52)
                border = colors.GREEN

            self.rect(x, top, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, top + box_height / 2, 34, colors.TEXT, True)
            self.centered_text(f"#{index}", x + box_width / 2, top + box_height + 36, 24, colors.TEXT_MUTED)

        if self.current_index is not None:
            current_x = start_x + self.current_index * (box_width + gap) + box_width / 2
            self.centered_text("비교 중", current_x, top - 45, 24, colors.ORANGE, True)

        if self.found_index is not None:
            found_x = start_x + self.found_index * (box_width + gap) + box_width / 2
            self.centered_text("발견", found_x, top - 45, 24, colors.GREEN, True)

    def _draw_legend(self):
        self.rect(1020, 72, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중인 원소", 1066, 68, 24, colors.TEXT_MUTED)
        self.rect(1020, 112, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("찾은 위치", 1066, 108, 24, colors.TEXT_MUTED)

    def _update_stats(self):
        self.msg_stats(f"비교 {self.compare_count}회")


class BinarySearchVisualizer(BaseVisualizer):
    def __init__(self, title="Binary Search", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.target = None
        self.left = None
        self.right = None
        self.mid = None
        self.found_index = None
        self.compare_count = 0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.target = data.target
        self.left = None
        self.right = None
        self.mid = None
        self.found_index = None
        self.compare_count = 0
        self.msg_phase("이진 탐색")
        self.msg_action(f"찾을 값 {self.target} 을 정렬된 배열에서 찾는다.")
        self.msg_detail("탐색 구간의 가운데 값을 비교하고, 절반을 제외한다.")
        self._update_stats()
        self.wait(700)

    def mark(self, left, right):
        self.left = left
        self.right = right
        self.mid = None
        self.msg_action(f"탐색 구간을 #{left}부터 #{right}까지로 정한다.")
        self.msg_detail("이 구간 안에 찾을 값이 있는지 확인한다.")
        self._update_stats()
        self.wait(750)

    def compare(self, mid):
        self.mid = mid
        self.compare_count += 1
        self.msg_action(f"가운데 #{mid}({self.array[mid]}) 과 찾을 값 {self.target} 을 비교한다.")
        if self.array[mid] == self.target:
            self.msg_detail("값이 같으므로 탐색에 성공한다.")
        elif self.array[mid] < self.target:
            self.msg_detail(f"{self.array[mid]} 이 더 작으므로 왼쪽 절반은 제외한다.")
        else:
            self.msg_detail(f"{self.array[mid]} 이 더 크므로 오른쪽 절반은 제외한다.")
        self._update_stats()
        self.wait(950)

    def found(self, index):
        self.found_index = index
        self.mid = None
        self.msg_phase("완료")
        self.msg_action(f"{self.target} 은 #{index} 위치에 있다.")
        self.msg_detail("찾는 값을 발견했으므로 탐색을 종료한다.")
        self._update_stats()
        self.wait(1100)

    def not_found(self):
        self.mid = None
        self.found_index = None
        self.msg_phase("완료")
        self.msg_action(f"{self.target} 을 찾지 못했다.")
        self.msg_detail("탐색 구간이 비었으므로 배열 안에 찾는 값이 없다.")
        self._update_stats()
        self.wait(1100)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("정렬된 배열에서 가운데 값을 비교하고 탐색 범위를 절반씩 줄인다.", 72, 115, 26, colors.TEXT_MUTED)
        if self.target is not None:
            self.text(f"찾을 값: {self.target}", 72, 170, 30, colors.YELLOW, True)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count = len(self.array)
        gap = max(4, min(14, 260 / max(1, count)))
        max_area_width = 1440
        box_width = min(96, (max_area_width - gap * (count - 1)) / count)
        box_height = 96
        value_size = max(12, min(30, box_width * 0.55))
        index_size = max(10, min(20, box_width * 0.45))
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 315

        for index, value in enumerate(self.array):
            x = start_x + index * (box_width + gap)
            fill = colors.PANEL
            border = colors.BORDER
            in_range = self.left is None or self.left <= index <= self.right
            if not in_range:
                fill = (22, 27, 34)
                border = (46, 54, 66)
            if index == self.mid:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if index == self.found_index:
                fill = (35, 72, 52)
                border = colors.GREEN

            self.rect(x, top, box_width, box_height, fill, border, 8)
            text_color = colors.TEXT if in_range or index == self.found_index else colors.TEXT_MUTED
            self.centered_text(value, x + box_width / 2, top + box_height / 2, value_size, text_color, True)
            self.centered_text(f"#{index}", x + box_width / 2, top + box_height + 32, index_size, colors.TEXT_MUTED)

        if self.left is not None and self.right is not None and self.left <= self.right:
            left_x = start_x + self.left * (box_width + gap) + box_width / 2
            right_x = start_x + self.right * (box_width + gap) + box_width / 2
            self.centered_text("L", left_x, top - 42, 24, colors.BLUE, True)
            self.centered_text("R", right_x, top - 42, 24, colors.BLUE, True)

        if self.mid is not None:
            mid_x = start_x + self.mid * (box_width + gap) + box_width / 2
            self.centered_text("M", mid_x, top - 76, 24, colors.ORANGE, True)

        if self.found_index is not None:
            found_x = start_x + self.found_index * (box_width + gap) + box_width / 2
            self.centered_text("발견", found_x, top - 76, 24, colors.GREEN, True)

    def _draw_legend(self):
        self.rect(1020, 72, 34, 24, colors.PANEL, colors.BORDER, 4)
        self.text("탐색 구간", 1066, 68, 24, colors.TEXT_MUTED)
        self.rect(1020, 112, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("가운데 원소", 1066, 108, 24, colors.TEXT_MUTED)
        self.rect(1020, 152, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("찾은 위치", 1066, 148, 24, colors.TEXT_MUTED)

    def _update_stats(self):
        self.msg_stats(f"비교 {self.compare_count}회")


class BubbleSortVisualizer(BaseVisualizer):
    def __init__(self, title="Bubble Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = None
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = len(self.array)
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0
        self.msg_phase("버블 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("이웃한 두 값을 비교해서 큰 값을 오른쪽으로 보낸다.")
        self._update_stats()
        self.wait(700)

    def start_pass(self, pass_index, sorted_from):
        self.pass_index = pass_index + 1
        self.pass_started = True
        self.sorted_from = sorted_from
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_action(f"{pass_index + 1}번째 반복을 시작한다.")
        self.msg_detail(f"#{sorted_from - 1} 위치까지 이웃한 두 값을 비교한다.")
        self._update_stats()
        self.wait(650)

    def compare(self, left, right):
        if left == 0 and not self.pass_started:
            self.pass_index += 1
            self.pass_started = True
        self.compare_pair = (left, right)
        self.swap_pair = None
        self.swap_progress = 0.0
        self.compare_count += 1
        self.msg_action(f"#{left}({self.array[left]}) 과 #{right}({self.array[right]}) 을 비교한다.")
        if self.array[left] > self.array[right]:
            self.msg_detail("왼쪽 값이 더 크므로 두 값을 교환한다.")
        else:
            self.msg_detail("왼쪽 값이 더 작거나 같으므로 그대로 둔다.")
        self._update_stats()
        self.wait(850)

    def swap(self, left, right):
        left_value = self.array[left]
        right_value = self.array[right]
        self.swap_pair = (left, right)
        self.compare_pair = None
        self.swap_count += 1
        self.msg_action(f"#{left} 과 #{right} 의 값을 교환한다.")
        self.msg_detail(f"{right_value} 이 왼쪽으로, {left_value} 이 오른쪽으로 이동한다.")
        self._update_stats()
        self._animate_swap(900)
        self.array[left], self.array[right] = self.array[right], self.array[left]
        self.swap_progress = 0.0
        self.draw()
        self.wait(250)

    def mark_sorted(self, index):
        self.sorted_from = index
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_action(f"#{index}부터 오른쪽은 정렬이 끝났다.")
        self.msg_detail("이번 반복에서 가장 큰 값이 정렬된 구간으로 이동했다.")
        self._update_stats()
        self.wait(750)
        self.pass_started = False
        self.section_end()

    def finish(self):
        self.sorted_from = 0
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("모든 원소가 작은 값부터 큰 값 순서로 놓였다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("이웃한 두 값을 비교하고 필요하면 교환하여 큰 값을 오른쪽으로 보낸다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count = len(self.array)
        gap = max(10, min(18, 220 / max(1, count)))
        max_area_width = 1440
        box_width = min(112, (max_area_width - gap * (count - 1)) / count)
        box_height = 110
        value_size = max(14, min(34, box_width * 0.52))
        index_size = max(10, min(22, box_width * 0.34))
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 305

        swapping = set(self.swap_pair or ())
        draw_order = [index for index in range(count) if index not in swapping]
        draw_order += [index for index in range(count) if index in swapping]

        for index in draw_order:
            value = self.array[index]
            slot_x = start_x + index * (box_width + gap)
            x = slot_x
            y = top
            if index in swapping:
                ox, oy = self._swap_offset(index, box_width + gap, box_height)
                x += ox
                y += oy
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT
            if self.sorted_from is not None and index >= self.sorted_from:
                fill = (35, 72, 52)
                border = colors.GREEN
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, text_color, True)
            self.centered_text(f"#{index}", slot_x + box_width / 2, top + box_height + 34, index_size, colors.TEXT_MUTED)

        if self.compare_pair is not None:
            self._pair_label("비교", self.compare_pair, start_x, box_width, gap, top, colors.ORANGE)
        if self.swap_pair is not None:
            self._pair_label("교환", self.swap_pair, start_x, box_width, gap, top, colors.BLUE)
        if self.sorted_from is not None and self.sorted_from < count:
            self._draw_sorted_region(start_x, box_width, gap, top, box_height, count)
            sorted_x = start_x + self.sorted_from * (box_width + gap) + box_width / 2
            self.centered_text("정렬 완료 구간", sorted_x, top - 46, 22, colors.GREEN, True)

    def _draw_sorted_region(self, start_x, box_width, gap, top, box_height, count):
        left = start_x + self.sorted_from * (box_width + gap)
        right = start_x + count * box_width + (count - 1) * gap
        margin = 8
        rect = self.view.rect(left - margin, top - margin, right - left + 2 * margin, box_height + 2 * margin)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(10),
        )

    def _pair_label(self, label, pair, start_x, box_width, gap, top, color):
        left, right = pair
        x1 = start_x + left * (box_width + gap) + box_width / 2
        x2 = start_x + right * (box_width + gap) + box_width / 2
        self.centered_text(label, (x1 + x2) / 2, top - 46, 24, color, True)

    def _swap_offset(self, index, step_width, box_height):
        if self.swap_pair is None:
            return 0, 0
        left, right = self.swap_pair
        if index == left:
            target = right
            vertical_sign = -1
        elif index == right:
            target = left
            vertical_sign = 1
        else:
            return 0, 0

        progress = self.swap_progress
        ox = (target - index) * step_width * progress
        arc = -2 * (progress - 0.5) ** 2 + 0.5
        oy = vertical_sign * box_height * arc
        return ox, oy

    def _animate_swap(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.swap_progress = 0.5
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.swap_progress = 0.5
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.swap_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.swap_progress >= 1.0:
                break
            self.clock.tick(60)

    def _draw_legend(self):
        self.rect(990, 72, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중", 1036, 68, 24, colors.TEXT_MUTED)
        self.rect(990, 112, 34, 24, (62, 66, 107), colors.BLUE, 4)
        self.text("교환한 원소", 1036, 108, 24, colors.TEXT_MUTED)
        self.rect(990, 152, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬 완료", 1036, 148, 24, colors.TEXT_MUTED)

    def _update_stats(self):
        self.msg_stats(f"반복 {self.pass_index}회\n비교 {self.compare_count}회\n교환 {self.swap_count}회")


class SelectionSortVisualizer(BubbleSortVisualizer):
    def __init__(self, title="Selection Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.sorted_until = -1
        self.min_index = None

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = None
        self.sorted_until = -1
        self.min_index = None
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0
        self.msg_phase("선택 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("아직 정렬되지 않은 구간에서 가장 작은 값을 찾아 앞쪽에 놓는다.")
        self._update_stats()
        self.wait(700)

    def select_min(self, index):
        self.min_index = index
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_action(f"#{index}({self.array[index]}) 을 현재 최솟값 후보로 둔다.")
        self.msg_detail("남은 원소들과 비교하면서 더 작은 값이 있는지 확인한다.")
        self._update_stats()
        self.wait(650)

    def selection(self, index):
        self.select_min(index)

    def compare(self, left, right):
        self.compare_pair = (left, right)
        self.swap_pair = None
        self.swap_progress = 0.0
        self.compare_count += 1
        self.msg_action(f"최솟값 후보 #{left}({self.array[left]}) 과 #{right}({self.array[right]}) 을 비교한다.")
        if self.array[left] > self.array[right]:
            self.msg_detail(f"#{right}의 값이 더 작으므로 최솟값 후보를 바꾼다.")
        else:
            self.msg_detail("현재 최솟값 후보를 그대로 유지한다.")
        self._update_stats()
        self.wait(850)

    def swap(self, left, right):
        if left == right:
            self.swap_pair = None
            self.compare_pair = None
            self.msg_action(f"#{left} 위치의 값이 이미 가장 작다.")
            self.msg_detail("교환하지 않고 이 위치를 확정한다.")
            self._update_stats()
            self.wait(650)
            return
        super().swap(left, right)

    def mark_sorted(self, index):
        self.sorted_until = index
        self.compare_pair = None
        self.swap_pair = None
        self.min_index = None
        self.swap_progress = 0.0
        self.pass_index = index + 1
        self.msg_action(f"#{index}까지 정렬이 끝났다.")
        self.msg_detail("이번 위치에는 남은 값 중 가장 작은 값이 놓였다.")
        self._update_stats()
        self.wait(750)
        self.section_end()

    def mark_done(self, index):
        self.mark_sorted(index)

    def finish(self):
        self.sorted_until = len(self.array) - 1
        self.compare_pair = None
        self.swap_pair = None
        self.min_index = None
        self.swap_progress = 0.0
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("각 위치에 들어갈 최솟값을 하나씩 선택했다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("남은 구간에서 가장 작은 값을 찾아 앞쪽 정렬 구간에 붙인다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count = len(self.array)
        gap = max(10, min(18, 220 / max(1, count)))
        max_area_width = 1440
        box_width = min(112, (max_area_width - gap * (count - 1)) / count)
        box_height = 110
        value_size = max(14, min(34, box_width * 0.52))
        index_size = max(10, min(22, box_width * 0.34))
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 305

        swapping = set(self.swap_pair or ())
        draw_order = [index for index in range(count) if index not in swapping]
        draw_order += [index for index in range(count) if index in swapping]

        for index in draw_order:
            value = self.array[index]
            slot_x = start_x + index * (box_width + gap)
            x = slot_x
            y = top
            if index in swapping:
                ox, oy = self._swap_offset(index, box_width + gap, box_height)
                x += ox
                y += oy

            fill = colors.PANEL
            border = colors.BORDER
            if index <= self.sorted_until:
                fill = (35, 72, 52)
                border = colors.GREEN
            if index == self.min_index:
                fill = (89, 39, 77)
                border = colors.RED
            if self.compare_pair is not None and index in self.compare_pair:
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT, True)
            self.centered_text(f"#{index}", slot_x + box_width / 2, top + box_height + 34, index_size, colors.TEXT_MUTED)

        if self.compare_pair is not None:
            self._comparison_label(self.compare_pair, start_x, box_width, gap, top, box_height, colors.ORANGE)
        if self.swap_pair is not None:
            self._pair_label("교환", self.swap_pair, start_x, box_width, gap, top, colors.BLUE)
        if self.min_index is not None:
            min_x = start_x + self.min_index * (box_width + gap) + box_width / 2
            self.centered_text("현재 최솟값", min_x, top - 46, 22, colors.RED, True)
        if self.sorted_until >= 0:
            self._draw_sorted_region(start_x, box_width, gap, top, box_height, count)

    def _draw_sorted_region(self, start_x, box_width, gap, top, box_height, count):
        right_index = min(self.sorted_until, count - 1)
        if right_index < 0:
            return
        margin = 8
        width = (right_index + 1) * box_width + right_index * gap
        rect = self.view.rect(start_x - margin, top - margin, width + 2 * margin, box_height + 2 * margin)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(10),
        )
        self.centered_text("정렬 완료 구간", start_x + width / 2, top + box_height + 74, 22, colors.GREEN, True)

    def _comparison_label(self, pair, start_x, box_width, gap, top, box_height, color):
        left, right = pair
        x1 = start_x + left * (box_width + gap) + box_width / 2
        x2 = start_x + right * (box_width + gap) + box_width / 2
        self.centered_text("비교", (x1 + x2) / 2, top + box_height + 78, 22, color, True)

    def _draw_legend(self):
        self.rect(910, 72, 34, 24, colors.PANEL, colors.ORANGE, 4)
        self.text("비교 중 테두리", 956, 68, 24, colors.TEXT_MUTED)
        self.rect(910, 112, 34, 24, (89, 39, 77), colors.RED, 4)
        self.text("현재 최솟값 후보", 956, 108, 24, colors.TEXT_MUTED)
        self.rect(1210, 72, 34, 24, (62, 66, 107), colors.BLUE, 4)
        self.text("교환", 1256, 68, 24, colors.TEXT_MUTED)
        self.rect(1210, 112, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬 완료", 1256, 108, 24, colors.TEXT_MUTED)


class InsertionSortVisualizer(BubbleSortVisualizer):
    def __init__(self, title="Insertion Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.sorted_until = 0
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.shift_pick = False
        self.unsettled_index = None
        self.pick_progress = 1.0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = None
        self.sorted_until = 0
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.shift_pick = False
        self.unsettled_index = None
        self.pick_progress = 1.0
        self.msg_phase("삽입 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("왼쪽의 정렬된 구간에 새 값을 알맞은 위치로 삽입한다.")
        self._update_stats()
        self.wait(700)

    def mark_end(self, index, pick=False):
        self.sorted_until = index
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.pass_index = index
        if pick:
            self.picked_from = index
            self.picked_value = self.array[index]
            self.hole_index = index
            self.unsettled_index = None
            self.pick_progress = 0.0
            self.msg_action(f"#{index}({self.picked_value}) 을 삽입할 값으로 빼 둔다.")
            self.msg_detail("왼쪽의 정렬된 구간에서 들어갈 위치를 찾는다.")
            self._update_stats()
            self._animate_pick(600)
            return
        else:
            self.picked_from = None
            self.picked_value = None
            self.hole_index = None
            self.unsettled_index = index
            self.pick_progress = 1.0
            self.msg_action(f"#{index}까지를 정렬된 구간으로 본다.")
            self.msg_detail("새 원소를 왼쪽 정렬 구간 안으로 이동시킨다.")
        self._update_stats()
        self.wait(750)

    def compare(self, left, right):
        self.compare_pair = (left, right)
        self.swap_pair = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.compare_count += 1
        if self.picked_value is None:
            right_value = self.array[right]
            self.msg_action(f"#{left}({self.array[left]}) 과 #{right}({right_value}) 을 비교한다.")
        else:
            right_value = self.picked_value if right == self.hole_index else self.array[right]
            self.msg_action(f"#{left}({self.array[left]}) 과 삽입할 값 {right_value} 을 비교한다.")
        will_move = self.array[left] > right_value
        restores_order = self.picked_value is None and self.unsettled_index is not None and not will_move
        if will_move:
            self.msg_detail("왼쪽 값이 더 크므로 오른쪽으로 이동시킨다.")
        else:
            self.msg_detail("왼쪽 값이 더 작거나 같으므로 이 자리 뒤에 삽입한다.")
        self._update_stats()
        self.wait(850)
        if restores_order:
            self._show_sorted_restored()

    def swap(self, left, right):
        super().swap(left, right)
        if self.picked_value is None:
            self.unsettled_index = left
            if left == 0:
                self._show_sorted_restored()

    def shift(self, source, target, pick=False):
        if pick and self.picked_from is not None:
            source = self.picked_from
        self.shift_pair = (source, target)
        self.shift_pick = pick
        self.compare_pair = None
        self.swap_pair = None
        self.shift_progress = 0.0
        self.swap_count += 1
        if pick:
            self.msg_action(f"빼 둔 값 {self.picked_value} 을 #{target} 위치에 삽입한다.")
            self.msg_detail("빈 자리에 값을 넣으면 이번 삽입이 끝난다.")
        else:
            self.msg_action(f"#{source}({self.array[source]}) 을 #{target} 위치로 한 칸 민다.")
            self.msg_detail("삽입할 값이 들어갈 빈 자리를 왼쪽으로 옮긴다.")
        self._update_stats()
        self._animate_shift(850)
        if pick:
            self.array[target] = self.picked_value
            self.picked_from = None
            self.picked_value = None
            self.hole_index = None
            self.pick_progress = 1.0
        else:
            self.array[target] = self.array[source]
            self.hole_index = source
        self.shift_pair = None
        self.shift_pick = False
        self.shift_progress = 0.0
        self.unsettled_index = None
        if pick:
            self._show_sorted_restored()
        else:
            self.draw()
            self.wait(250)

    def finish(self):
        self.sorted_until = len(self.array) - 1
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.unsettled_index = None
        self.pick_progress = 1.0
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("각 원소를 왼쪽의 정렬된 구간에 차례로 삽입했다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("왼쪽 정렬 구간에서 삽입 위치를 찾고, 큰 값들을 오른쪽으로 민다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count, start_x, top, box_width, box_height, gap = self._layout_metrics()
        value_size = max(14, min(34, box_width * 0.52))
        index_size = max(10, min(22, box_width * 0.34))

        moving = set(self.swap_pair or ())
        if self.shift_pair is not None and not self.shift_pick:
            moving = {self.shift_pair[0]}
        draw_order = [index for index in range(count) if index not in moving]
        draw_order += [index for index in range(count) if index in moving]

        for index in draw_order:
            if index == self.hole_index and not (self.shift_pair and index in moving):
                self._draw_hole(index, start_x, top, box_width, box_height, gap, value_size, index_size)
                continue

            value = self.array[index]
            slot_x = start_x + index * (box_width + gap)
            x = slot_x
            y = top
            if self.swap_pair is not None and index in moving:
                ox, oy = self._swap_offset(index, box_width + gap, box_height)
                x += ox
                y += oy
            elif self.shift_pair is not None and index in moving:
                if not self.shift_pick:
                    self._draw_ghost_card(value, slot_x, top, box_width, box_height, value_size)
                ox, oy = self._shift_offset(index, box_width + gap, box_height)
                x += ox
                y += oy

            fill = colors.PANEL
            border = colors.BORDER
            if index <= self.sorted_until:
                fill = (35, 72, 52)
                border = colors.GREEN
            if self._is_unsettled_region(index):
                border = colors.YELLOW
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE
            if self.shift_pair is not None and index in moving:
                fill = (62, 66, 107)
                border = colors.BLUE

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT, True)
            self.centered_text(f"#{index}", slot_x + box_width / 2, top + box_height + 34, index_size, colors.TEXT_MUTED)

        self._draw_picked_value(start_x, top, box_width, box_height, gap, value_size)

        if self.compare_pair is not None:
            self._pair_label("비교", self.compare_pair, start_x, box_width, gap, top, colors.ORANGE)
        if self.swap_pair is not None:
            self._pair_label("교환", self.swap_pair, start_x, box_width, gap, top, colors.BLUE)
        if self.shift_pair is not None:
            self._pair_label("이동", self.shift_pair, start_x, box_width, gap, top, colors.BLUE)
        if self.sorted_until >= 0:
            self._draw_sorted_region(start_x, box_width, gap, top, box_height, count)

    def _is_unsettled_region(self, index):
        return self.unsettled_index is not None and self.picked_value is None and 0 <= index <= self.sorted_until

    def _show_sorted_restored(self):
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.unsettled_index = None
        self.msg_action(f"#{self.sorted_until}까지 다시 정렬되었다.")
        self.msg_detail("방금 처리한 원소 때문에 깨졌던 구간이 정렬 상태로 돌아왔다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def _layout_metrics(self):
        count = len(self.array)
        gap = max(10, min(18, 220 / max(1, count)))
        max_area_width = 1440
        box_width = min(112, (max_area_width - gap * (count - 1)) / count)
        box_height = 110
        start_x = 800 - (box_width * count + gap * (count - 1)) / 2
        top = 330
        return count, start_x, top, box_width, box_height, gap

    def _draw_hole(self, index, start_x, top, box_width, box_height, gap, value_size, index_size):
        slot_x = start_x + index * (box_width + gap)
        self._draw_ghost_card(self.array[index], slot_x, top, box_width, box_height, value_size)
        self.centered_text(f"#{index}", slot_x + box_width / 2, top + box_height + 34, index_size, colors.TEXT_MUTED)

    def _draw_ghost_card(self, value, x, y, box_width, box_height, value_size):
        self.rect(x, y, box_width, box_height, (21, 25, 31), (61, 69, 82), 8)
        self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT_MUTED, True)

    def _draw_picked_value(self, start_x, top, box_width, box_height, gap, value_size):
        if self.picked_value is None or self.picked_from is None:
            return

        step_width = box_width + gap
        x = start_x + self.picked_from * step_width
        y = top - box_height * 0.95 * self.pick_progress
        if self.shift_pick and self.shift_pair is not None:
            _, target = self.shift_pair
            x += (target - self.picked_from) * step_width * self.shift_progress
            y = top - box_height * 0.95 * (1 - self.shift_progress)
        self.rect(x, y, box_width, box_height, (89, 39, 77), colors.RED, 8)
        self.centered_text(self.picked_value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT, True)

    def _draw_sorted_region(self, start_x, box_width, gap, top, box_height, count):
        right_index = min(self.sorted_until, count - 1)
        if right_index < 0:
            return
        margin = 8
        width = (right_index + 1) * box_width + right_index * gap
        rect = self.view.rect(start_x - margin, top - margin, width + 2 * margin, box_height + 2 * margin)
        broken = self.unsettled_index is not None and self.picked_value is None
        color = colors.YELLOW if broken else (88, 126, 101)
        label = "정렬이 깨진 구간" if broken else "정렬된 구간"
        pygame.draw.rect(
            self.screen,
            color,
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(10),
        )
        self.centered_text(label, start_x + width / 2, top + box_height + 74, 22, color, True)

    def _shift_offset(self, index, step_width, box_height):
        if self.shift_pair is None:
            return 0, 0
        source, target = self.shift_pair
        if self.shift_pick:
            if index != source:
                return 0, 0
            ox = (target - source) * step_width * self.shift_progress
            oy = -box_height * (1 - self.shift_progress)
            return ox, oy
        if index != source:
            return 0, 0
        return (target - source) * step_width * self.shift_progress, 0

    def _animate_pick(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.pick_progress = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.pick_progress = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.pick_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.pick_progress >= 1.0:
                break
            self.clock.tick(60)

        self.wait(250)

    def _animate_shift(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.shift_progress = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.shift_progress = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.shift_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.shift_progress >= 1.0:
                break
            self.clock.tick(60)

    def _draw_legend(self):
        self.rect(930, 72, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중", 976, 68, 24, colors.TEXT_MUTED)
        self.rect(930, 112, 34, 24, (62, 66, 107), colors.BLUE, 4)
        self.text("교환/이동", 976, 108, 24, colors.TEXT_MUTED)
        self.rect(930, 152, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬된 구간", 976, 148, 24, colors.TEXT_MUTED)
        self.rect(1210, 72, 34, 24, (89, 39, 77), colors.RED, 4)
        self.text("빼 둔 값", 1256, 68, 24, colors.TEXT_MUTED)


class ShellSortVisualizer(InsertionSortVisualizer):
    def __init__(self, title="Shell Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.current_gap = 1
        self.current_group = None
        self.previous_gap = None
        self.gap_progress = 1.0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = None
        self.sorted_until = 0
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.shift_pick = False
        self.unsettled_index = None
        self.pick_progress = 1.0
        self.current_gap = 1
        self.current_group = None
        self.previous_gap = None
        self.gap_progress = 1.0
        self.msg_phase("셸 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("gap 간격으로 나눈 부분 배열에 삽입 정렬을 적용한다.")
        self._update_stats()
        self.wait(700)

    def set_gap(self, gap):
        next_gap = max(1, int(gap))
        self.previous_gap = self.current_gap if self.current_gap != next_gap else None
        self.current_gap = max(1, int(gap))
        self.current_group = None
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.pick_progress = 1.0
        self.msg_phase(f"gap = {self.current_gap}")
        self.msg_action(f"gap을 {self.current_gap}로 정한다.")
        self.msg_detail(f"인덱스 차이가 {self.current_gap}인 원소들을 같은 부분 배열로 본다.")
        self._update_stats()
        if self.previous_gap is None:
            self.wait(900)
        else:
            self.gap_progress = 0.0
            self._animate_gap_change(900)
            self.previous_gap = None
            self.gap_progress = 1.0
            self.wait(250)

    def set_group(self, offset):
        self.current_group = int(offset)
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.msg_action(f"{self.current_group}번 부분 배열을 처리한다.")
        self.msg_detail(f"index % {self.current_gap} == {self.current_group}인 원소들만 삽입 정렬한다.")
        self._update_stats()
        self.wait(650)

    def finish_gap(self):
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.current_group = None
        self.msg_action(f"gap = {self.current_gap} 단계가 끝났다.")
        self.msg_detail("각 부분 배열이 gap 간격 기준으로 정렬되었다.")
        self._update_stats()
        self.wait(900)
        self.section_end()

    def mark_end(self, index, pick=False):
        new_group = index % self.current_gap
        if self.current_group != new_group:
            self.current_group = new_group
            self.compare_pair = None
            self.swap_pair = None
            self.shift_pair = None
            self.picked_from = None
            self.picked_value = None
            self.hole_index = None
            self.pick_progress = 1.0
            self.msg_action(f"{self.current_group}번 부분 배열로 이동한다.")
            self.msg_detail(f"index % {self.current_gap} == {self.current_group}인 원소들을 처리한다.")
            self._update_stats()
            self.wait(350)
        self.sorted_until = index
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.pass_index = index
        if pick:
            self.picked_from = index
            self.picked_value = self.array[index]
            self.hole_index = index
            self.unsettled_index = None
            self.pick_progress = 0.0
            self.msg_action(f"#{index}({self.picked_value}) 을 부분 배열에 삽입할 값으로 빼 둔다.")
            self.msg_detail(f"gap {self.current_gap}만큼 왼쪽의 값들과 비교한다.")
            self._update_stats()
            self._animate_pick(600)
            return

        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.unsettled_index = index
        self.pick_progress = 1.0
        self.msg_action(f"#{index}까지 현재 부분 배열의 정렬 구간으로 본다.")
        self.msg_detail("새 원소를 같은 부분 배열 안에서 알맞은 위치로 이동시킨다.")
        self._update_stats()
        self.wait(750)

    def compare(self, left, right):
        self.current_group = right % self.current_gap
        super().compare(left, right)

    def shift(self, source, target, pick=False):
        self.current_group = target % self.current_gap
        super().shift(source, target, pick)

    def finish(self):
        self.current_gap = 1
        self.current_group = None
        self.sorted_until = len(self.array) - 1
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.unsettled_index = None
        self.pick_progress = 1.0
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("gap을 1까지 줄여 전체 배열에 대한 삽입 정렬을 마쳤다.")
        self._update_stats()
        self.wait(1200)

    def _show_sorted_restored(self):
        self.compare_pair = None
        self.swap_pair = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.unsettled_index = None
        self.msg_action("현재 부분 배열에서 삽입이 끝났다.")
        self.msg_detail(f"gap {self.current_gap} 기준 부분 배열의 정렬 상태가 회복되었다.")
        self._update_stats()
        self.wait(800)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("gap 간격의 부분 배열을 삽입 정렬하고, gap을 줄여 마지막에는 전체를 정렬한다.", 72, 115, 26, colors.TEXT_MUTED)
        self.text(f"gap: {self.current_gap}", 72, 165, 28, colors.YELLOW, True)
        if self.current_group is not None:
            self.text(f"sub group: {self.current_group}", 210, 165, 28, colors.BLUE, True)
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count, start_x, top, box_width, box_height, slot_gap = self._layout_metrics()
        value_size = max(12, min(28, box_width * 0.48))
        index_size = max(9, min(16, box_width * 0.26))

        moving = set(self.swap_pair or ())
        if self.shift_pair is not None and not self.shift_pick:
            moving = {self.shift_pair[0]}
        draw_order = [index for index in range(count) if index not in moving]
        draw_order += [index for index in range(count) if index in moving]

        self._draw_group_guides(start_x, top, box_width, box_height, slot_gap, count)
        self._draw_interest_region(start_x, top, box_width, box_height, slot_gap)

        for index in draw_order:
            if index == self.hole_index and not (self.shift_pair and index in moving):
                self._draw_hole(index, start_x, top, box_width, box_height, slot_gap, value_size, index_size)
                continue

            value = self.array[index]
            slot_x, slot_y = self._slot_position(index, start_x, top, box_width, box_height, slot_gap)
            x = slot_x
            y = slot_y
            if self.swap_pair is not None and index in moving:
                ox, oy = self._swap_offset(index, box_width + slot_gap, box_height)
                x += ox
                y += oy
            elif self.shift_pair is not None and index in moving:
                if not self.shift_pick:
                    self._draw_ghost_card(value, slot_x, slot_y, box_width, box_height, value_size)
                ox, oy = self._shift_offset(index, box_width + slot_gap, box_height)
                x += ox
                y += oy

            active = self._is_active_group(index)
            fill = colors.PANEL if active else (17, 21, 27)
            border = colors.BORDER if active else (42, 51, 64)
            text_color = colors.TEXT if active else colors.TEXT_MUTED
            if self._is_sorted_index(index):
                fill = (35, 72, 52)
                border = colors.GREEN
            if self._is_unsettled_region(index):
                border = colors.YELLOW
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
                text_color = colors.TEXT
            if self.shift_pair is not None and index in moving:
                fill = (62, 66, 107)
                border = colors.BLUE
                text_color = colors.TEXT

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, text_color, True)
            self.centered_text(f"#{index}", slot_x + box_width / 2, slot_y + box_height + 18, index_size, colors.TEXT_MUTED)

        self._draw_picked_value(start_x, top, box_width, box_height, slot_gap, value_size)

        if self.compare_pair is not None:
            self._shell_pair_label("비교", self.compare_pair, start_x, top, box_width, box_height, slot_gap, colors.ORANGE)
        if self.shift_pair is not None:
            self._shell_pair_label("이동", self.shift_pair, start_x, top, box_width, box_height, slot_gap, colors.BLUE)
    def _layout_metrics(self):
        count = len(self.array)
        rows = max(1, min(self.current_gap, count))
        slot_gap = max(6, min(14, 180 / max(1, count)))
        max_area_width = 1380
        max_area_height = 320
        box_width = min(82, (max_area_width - slot_gap * max(0, count - 1)) / max(1, count))
        row_gap = min(42, max(16, (max_area_height - rows * 62) / max(1, rows - 1))) if rows > 1 else 0
        box_height = min(62, (max_area_height - row_gap * max(0, rows - 1)) / rows)
        start_x = 800 - (box_width * count + slot_gap * max(0, count - 1)) / 2
        top = 235
        return count, start_x, top, box_width, box_height, slot_gap

    def _slot_position(self, index, start_x, top, box_width, box_height, slot_gap):
        x = start_x + index * (box_width + slot_gap)
        y = self._row_y(index, self.current_gap, top)
        if self.previous_gap is not None and self.gap_progress < 1.0:
            old_y = self._row_y(index, self.previous_gap, top)
            y = old_y + (y - old_y) * self.gap_progress
        return x, y

    def _row_y(self, index, gap, top):
        rows = max(1, min(gap, len(self.array)))
        max_area_height = 320
        row_gap = min(42, max(16, (max_area_height - rows * 62) / max(1, rows - 1))) if rows > 1 else 0
        box_height = min(62, (max_area_height - row_gap * max(0, rows - 1)) / rows)
        return top + (index % gap) * (box_height + row_gap)

    def _draw_hole(self, index, start_x, top, box_width, box_height, slot_gap, value_size, index_size):
        slot_x, slot_y = self._slot_position(index, start_x, top, box_width, box_height, slot_gap)
        self._draw_ghost_card(self.array[index], slot_x, slot_y, box_width, box_height, value_size)
        self.centered_text(f"#{index}", slot_x + box_width / 2, slot_y + box_height + 18, index_size, colors.TEXT_MUTED)

    def _draw_picked_value(self, start_x, top, box_width, box_height, slot_gap, value_size):
        if self.picked_value is None or self.picked_from is None:
            return

        x, base_y = self._slot_position(self.picked_from, start_x, top, box_width, box_height, slot_gap)
        y = base_y - box_height * 0.9 * self.pick_progress
        if self.shift_pick and self.shift_pair is not None:
            _, target = self.shift_pair
            target_x, target_y = self._slot_position(target, start_x, top, box_width, box_height, slot_gap)
            x += (target_x - x) * self.shift_progress
            y = base_y - box_height * 0.9 * (1 - self.shift_progress) + (target_y - base_y) * self.shift_progress
        self.rect(x, y, box_width, box_height, (89, 39, 77), colors.RED, 8)
        self.centered_text(self.picked_value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT, True)

    def _shift_offset(self, index, step_width, box_height):
        if self.shift_pair is None:
            return 0, 0
        source, target = self.shift_pair
        if index != source:
            return 0, 0
        count, start_x, top, box_width, box_height, slot_gap = self._layout_metrics()
        source_x, source_y = self._slot_position(source, start_x, top, box_width, box_height, slot_gap)
        target_x, target_y = self._slot_position(target, start_x, top, box_width, box_height, slot_gap)
        if self.shift_pick:
            return 0, 0
        return (target_x - source_x) * self.shift_progress, (target_y - source_y) * self.shift_progress

    def _animate_gap_change(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.gap_progress = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.gap_progress = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.gap_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.gap_progress >= 1.0:
                break
            self.clock.tick(60)

    def _is_active_group(self, index):
        return self.current_group is None or index % self.current_gap == self.current_group

    def _is_sorted_index(self, index):
        if self.current_group is None:
            return False
        return index % self.current_gap == self.current_group and index <= self.sorted_until

    def _is_unsettled_region(self, index):
        return (
            self.unsettled_index is not None
            and self.picked_value is None
            and self.current_group is not None
            and index % self.current_gap == self.current_group
            and index <= self.sorted_until
        )

    def _draw_group_guides(self, start_x, top, box_width, box_height, slot_gap, count):
        rows = max(1, min(self.current_gap, count))
        for row in range(rows):
            first = row
            last = row + ((count - 1 - row) // self.current_gap) * self.current_gap
            if first >= count:
                continue
            x1, y = self._slot_position(first, start_x, top, box_width, box_height, slot_gap)
            x2, _ = self._slot_position(last, start_x, top, box_width, box_height, slot_gap)
            color = colors.BLUE if row == self.current_group else (42, 51, 64)
            pygame.draw.line(
                self.screen,
                color,
                self.view.point(x1 - 10, y + box_height / 2),
                self.view.point(x2 + box_width + 10, y + box_height / 2),
                self.view.length(1),
            )

    def _draw_interest_region(self, start_x, top, box_width, box_height, slot_gap):
        if self.current_group is None or self.sorted_until < 0:
            return

        last = self.sorted_until
        if last % self.current_gap != self.current_group:
            return

        first = self.current_group
        if first > last:
            return

        x1, y = self._slot_position(first, start_x, top, box_width, box_height, slot_gap)
        x2, _ = self._slot_position(last, start_x, top, box_width, box_height, slot_gap)
        margin_x = 10
        margin_y = 8
        rect = self.view.rect(
            x1 - margin_x,
            y - margin_y,
            x2 - x1 + box_width + 2 * margin_x,
            box_height + 2 * margin_y,
        )
        pygame.draw.rect(
            self.screen,
            (26, 40, 46),
            rect,
            border_radius=self.view.length(10),
        )
        pygame.draw.rect(
            self.screen,
            colors.GREEN,
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(10),
        )

    def _shell_pair_label(self, label, pair, start_x, top, box_width, box_height, slot_gap, color):
        left, right = pair
        x1, y1 = self._slot_position(left, start_x, top, box_width, box_height, slot_gap)
        x2, y2 = self._slot_position(right, start_x, top, box_width, box_height, slot_gap)
        self.centered_text(label, (x1 + x2 + box_width) / 2, min(y1, y2) - 24, 20, color, True)

    def _draw_sorted_region(self, start_x, box_width, gap, top, box_height, count):
        return

    def _draw_legend(self):
        self.rect(900, 72, 34, 24, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중", 946, 68, 24, colors.TEXT_MUTED)
        self.rect(900, 112, 34, 24, (62, 66, 107), colors.BLUE, 4)
        self.text("이동", 946, 108, 24, colors.TEXT_MUTED)
        self.rect(1160, 72, 34, 24, (89, 39, 77), colors.RED, 4)
        self.text("빼 둔 값", 1206, 68, 24, colors.TEXT_MUTED)
        self.rect(1160, 112, 34, 24, (35, 72, 52), colors.GREEN, 4)
        self.text("현재 부분 배열 정렬 구간", 1206, 108, 24, colors.TEXT_MUTED)


class BinaryTreeArrayVisualizer(BaseVisualizer):
    def __init__(self, title="Binary Tree in Array", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.mode = "complete"
        self.selected = None
        self.related = set()

    def setup(self, data, one_based=False):
        self.set_data_info(data)
        self.array = list(data.array)
        self.mode = "one_based" if one_based else "complete"
        self.selected = None
        self.related = set()
        if one_based:
            self.msg_phase("1-based index")
            self.msg_action("complete binary tree를 1-based index로 살펴본다.")
            self.msg_detail("root를 #1 로 두면 부모와 자식 공식이 단순해진다.")
        else:
            self.msg_phase("Complete Binary Tree")
            self.msg_action("배열을 complete binary tree로 해석한다.")
            self.msg_detail("위에서 아래로, 왼쪽에서 오른쪽으로 채우면 배열에 빈칸 없이 저장된다.")
        self._update_stats()
        self.wait(700)

    def show_complete_binary_tree(self):
        self.mode = "complete"
        self.selected = None
        self.related = set()
        self.msg_phase("Complete Binary Tree")
        self.msg_action("complete binary tree는 마지막 레벨을 왼쪽부터 채운다.")
        self.msg_detail("그래서 level-order 순서로 배열에 넣으면 빈 index가 생기지 않는다.")
        self._update_stats()
        self.wait(1000)
        self.section_end()

    def compare_index_systems(self, index=3):
        self.mode = "index"
        self.selected = self._valid_index(index)
        self.related = {self.selected}
        one_based = self.selected + 1
        self.msg_phase("0-based와 1-based")
        self.msg_action(f"0-based #{self.selected} 는 1-based #{one_based} 와 같은 노드이다.")
        self.msg_detail("1-based 공식이 더 단순하지만, Python list는 0-based index를 사용한다.")
        self._update_stats()
        self.wait(1100)
        self.section_end()

    def show_one_based_tree(self):
        self.mode = "one_based"
        self.selected = None
        self.related = set()
        self.msg_phase("1-based index")
        self.msg_action("root를 #1 로 두면 자식과 부모 공식이 단순해진다.")
        self.msg_detail("왼쪽 자식은 2*i, 오른쪽 자식은 2*i+1, 부모는 i//2 이다.")
        self._update_stats()
        self.wait(1000)
        self.section_end()

    def show_children_1based(self, index=3):
        self.mode = "one_based"
        internal = self._valid_index(index - 1)
        self.selected = internal
        left = index * 2
        right = index * 2 + 1
        self.related = {child - 1 for child in (left, right) if child <= len(self.array)}
        self.msg_phase("1-based 자식 index")
        self.msg_action(f"1-based #{index} 의 자식은 2*i, 2*i+1 로 찾는다.")
        if len(self.related) == 2:
            self.msg_detail(f"왼쪽 자식 #{left}, 오른쪽 자식 #{right} 이다.")
        elif len(self.related) == 1:
            self.msg_detail(f"왼쪽 자식 #{left} 만 있다.")
        else:
            self.msg_detail("자식이 없는 leaf node이다.")
        self._update_stats()
        self.wait(1100)
        self.section_end()

    def show_parent_1based(self, index=10):
        self.mode = "one_based"
        internal = self._valid_index(index - 1)
        self.selected = internal
        parent = index // 2 if index > 1 else None
        self.related = {parent - 1} if parent is not None else set()
        self.msg_phase("1-based 부모 index")
        if parent is None:
            self.msg_action("#1 은 root이므로 부모가 없다.")
            self.msg_detail("complete binary tree의 첫 노드이다.")
        else:
            self.msg_action(f"1-based #{index} 의 부모는 i//2 = #{parent} 이다.")
            self.msg_detail("공식은 단순하지만 Python list에서는 0-based로 다시 바꿔야 한다.")
        self._update_stats()
        self.wait(1100)
        self.section_end()

    def show_children(self, index=2, compare_bases=False):
        self.mode = "index" if compare_bases else "children"
        self.selected = self._valid_index(index)
        left = self.selected * 2 + 1
        right = self.selected * 2 + 2
        self.related = {child for child in (left, right) if child < len(self.array)}
        self.msg_phase("자식 index")
        if compare_bases:
            self.msg_action(f"같은 노드의 자식 index를 0-based와 1-based로 비교한다.")
        else:
            self.msg_action(f"0-based #{self.selected} 의 자식은 2*i+1, 2*i+2 로 찾는다.")
        if len(self.related) == 2:
            if compare_bases:
                self.msg_detail(f"0-based: #{left}, #{right} / 1-based: #{left + 1}, #{right + 1}")
            else:
                self.msg_detail(f"왼쪽 자식 #{left}, 오른쪽 자식 #{right} 이다.")
        elif len(self.related) == 1:
            self.msg_detail(f"왼쪽 자식 #{left} 만 있다.")
        else:
            self.msg_detail("자식이 없는 leaf node이다.")
        self._update_stats()
        self.wait(1100)
        self.section_end()

    def show_parent(self, index=9, compare_bases=False):
        self.mode = "index" if compare_bases else "parent"
        self.selected = self._valid_index(index)
        parent = (self.selected - 1) // 2 if self.selected > 0 else None
        self.related = {parent} if parent is not None else set()
        self.msg_phase("부모 index")
        if parent is None:
            self.msg_action("#0 은 root이므로 부모가 없다.")
            self.msg_detail("1-based에서는 #1 이 root이다.")
        else:
            self.msg_action(f"0-based #{self.selected} 의 부모는 (i-1)//2 = #{parent} 이다.")
            self.msg_detail(f"1-based로 보면 #{self.selected + 1} 의 부모는 i//2 = #{parent + 1} 이다.")
        self._update_stats()
        self.wait(1100)
        self.section_end()

    def finish(self):
        self.selected = None
        self.related = set()
        self.msg_phase("Heap Sort 준비")
        self.msg_action("heap은 complete binary tree를 배열로 저장해서 다룬다.")
        self.msg_detail("이제 배열 index 계산만으로 부모와 자식을 찾아 downheap을 할 수 있다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 34, 40, colors.TEXT, True)
        if self.mode == "index":
            self._draw_index_comparison()
        elif self.mode == "one_based":
            self._draw_one_based_tree_array()
        else:
            self._draw_tree_array()

    def _draw_tree_array(self):
        self.text("complete binary tree를 level-order 순서로 배열에 저장한다.", 72, 86, 22, colors.TEXT_MUTED)
        self._draw_formula_panel(70, 126, "Python list", "root = 0", "left = 2*i + 1", "right = 2*i + 2", "parent = (i-1)//2")
        self._draw_tree(800, 240, 1180, zero_based=True)
        self._draw_array()

    def _draw_index_comparison(self):
        self.text("같은 complete binary tree를 0-based / 1-based index로 비교한다.", 72, 86, 22, colors.TEXT_MUTED)
        self._draw_formula_panel(150, 126, "0-based", "root = 0", "left = 2*i + 1", "right = 2*i + 2", "parent = (i-1)//2")
        self._draw_formula_panel(930, 126, "1-based", "root = 1", "left = 2*i", "right = 2*i + 1", "parent = i//2")
        self._draw_tree(430, 250, 560, zero_based=True)
        self._draw_tree(1170, 250, 560, zero_based=False)
        self._draw_array()

    def _draw_one_based_tree_array(self):
        self.text("1-based index로 보면 complete binary tree의 부모/자식 공식이 단순해진다.", 72, 86, 22, colors.TEXT_MUTED)
        self._draw_formula_panel(70, 126, "1-based", "root = 1", "left = 2*i", "right = 2*i + 1", "parent = i//2")
        self._draw_tree(800, 240, 1180, zero_based=False)
        self._draw_array(zero_based=False)

    def _draw_formula_panel(self, x, y, title, *lines):
        self.rect(x, y, 520, 102, colors.PANEL_DARK, colors.BORDER, 8)
        self.text(title, x + 24, y + 16, 24, colors.BLUE, True)
        for offset, line in enumerate(lines):
            self.mono_text(line, x + 180, y + 14 + offset * 21, 18, colors.TEXT_MUTED)

    def _draw_tree(self, center_x, top, width, zero_based=True):
        label = "0-based index" if zero_based else "1-based index"
        self.centered_text(label, center_x, top - 52, 22, colors.TEXT, True)
        for index in range(len(self.array)):
            self._draw_tree_edge(center_x, top, width, index, index * 2 + 1)
            self._draw_tree_edge(center_x, top, width, index, index * 2 + 2)
        for index in range(len(self.array)):
            self._draw_tree_node(center_x, top, width, index, zero_based)

    def _draw_tree_edge(self, center_x, top, width, parent, child):
        if child >= len(self.array):
            return
        px, py = self._node_pos(center_x, top, width, parent)
        cx, cy = self._node_pos(center_x, top, width, child)
        color = colors.ORANGE if self._is_edge_related(parent, child) else colors.BORDER
        pygame.draw.line(self.screen, color, self.view.point(px, py), self.view.point(cx, cy), self.view.length(3))

    def _draw_tree_node(self, center_x, top, width, index, zero_based):
        x, y = self._node_pos(center_x, top, width, index)
        radius = 24
        fill = colors.PANEL
        border = colors.BORDER
        if index in self.related:
            fill = (82, 55, 30)
            border = colors.ORANGE
        if index == self.selected:
            fill = (35, 72, 52)
            border = colors.GREEN

        pygame.draw.circle(self.screen, fill, self.view.point(x, y), self.view.length(radius))
        pygame.draw.circle(self.screen, border, self.view.point(x, y), self.view.length(radius), width=self.view.length(2))
        label = index if zero_based else index + 1
        self.centered_text(label, x, y - 3, 22, colors.TEXT, True)
        self.centered_text(self.array[index], x, y + radius + 16, 13, colors.TEXT_MUTED)

    def _draw_array(self, zero_based=True):
        if not self.array:
            return
        count = len(self.array) if zero_based else len(self.array) + 1
        gap = max(6, min(14, 160 / max(1, count)))
        max_width = 1320
        box_width = min(70, (max_width - gap * max(0, count - 1)) / max(1, count))
        box_height = 48
        start_x = 800 - (box_width * count + gap * max(0, count - 1)) / 2
        top = 545
        title = "Python list: 0-based index" if zero_based else "개념 설명용 배열: 1-based index"
        self.centered_text(title, 800, top - 34, 22, colors.TEXT, True)
        for slot in range(count):
            if zero_based:
                index = slot
                value = self.array[index]
            else:
                index = slot - 1
                value = "" if slot == 0 else self.array[index]
            x = start_x + slot * (box_width + gap)
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT
            label_color = colors.TEXT_MUTED
            if not zero_based and slot == 0:
                fill = (33, 38, 45)
                border = colors.BORDER
                text_color = colors.TEXT_MUTED
                label_color = colors.ORANGE
            elif index in self.related:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if slot > 0 or zero_based:
                if index == self.selected:
                    fill = (35, 72, 52)
                    border = colors.GREEN
            self.rect(x, top, box_width, box_height, fill, border, 7)
            if zero_based or slot > 0:
                self.centered_text(value, x + box_width / 2, top + box_height / 2, 20, text_color, True)
            else:
                self.centered_text("사용 안 함", x + box_width / 2, top + box_height / 2, max(10, min(15, box_width * 0.25)), text_color, True)
            label = index if zero_based else slot
            self.centered_text(f"#{label}", x + box_width / 2, top + box_height + 18, 14, label_color)

    def _node_pos(self, center_x, top, width, index):
        level = int(math.log2(index + 1))
        first = 2**level - 1
        offset = index - first
        nodes = 2**level
        x = center_x - width / 2 + width * (offset + 0.5) / nodes
        y = top + level * 76
        return x, y

    def _is_edge_related(self, parent, child):
        if self.selected is None:
            return False
        return (parent == self.selected and child in self.related) or (child == self.selected and parent in self.related)

    def _valid_index(self, index):
        if not self.array:
            return 0
        return max(0, min(int(index), len(self.array) - 1))

    def _update_stats(self):
        self.msg_stats(f"원소 {len(self.array)}개")


class HeapSortVisualizer(BubbleSortVisualizer):
    def __init__(self, title="Heap Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.tree_size = 0
        self.root_index = None
        self.building_tree = False
        self.build_progress = 1.0
        self.show_tree = False

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.compare_pair = None
        self.swap_pair = None
        self.sorted_from = len(self.array)
        self.tree_size = len(self.array)
        self.root_index = None
        self.compare_count = 0
        self.swap_count = 0
        self.pass_index = 0
        self.pass_started = False
        self.swap_progress = 0.0
        self.building_tree = False
        self.build_progress = 1.0
        self.show_tree = False
        self.msg_phase("힙 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("배열을 완전 이진 트리로 보고 max heap을 만든다.")
        self._update_stats()
        self.wait(700)

    def build_tree(self):
        self.msg_phase("1단계: Max Heap 만들기")
        self.msg_action("배열을 완전 이진 트리 모양으로 배치한다.")
        self.msg_detail("부모 index i의 왼쪽 자식은 2i+1, 오른쪽 자식은 2i+2이다.")
        self._update_stats()
        self.show_tree = True
        self.building_tree = True
        self.build_progress = 0.0
        self._animate_build_tree(900)
        self.building_tree = False
        self.build_progress = 1.0
        self.wait(350)

    def set_root(self, root):
        if self.root_index is not None and self.root_index >= 0:
            self.compare_pair = None
            self.swap_pair = None
            self.swap_progress = 0.0
            if self._is_heap(self.root_index):
                self.msg_action(f"#{self.root_index} subtree가 heap 상태가 되었다.")
                self.msg_detail("파란 배경으로 heap 조건이 회복된 상태를 확인한다.")
            else:
                self.msg_action(f"#{self.root_index} subtree에 아직 heap 조건 위반이 있다.")
                self.msg_detail("빨간 배경으로 downheap이 더 필요함을 확인한다.")
            self._update_stats()
            self.wait(500)
        self.root_index = root
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        if root is None or root < 0:
            self.msg_action("heapify 대상을 해제한다.")
            self.msg_detail("현재 heap 영역 전체를 확인한다.")
        else:
            self.msg_action(f"#{root}({self.array[root]}) 를 root로 하는 subtree를 heapify한다.")
            self.msg_detail("subtree 테두리는 heap 조건 만족 여부를 나타낸다.")
        self._update_stats()
        self.wait(750)

    def finish_build_heap(self):
        self.root_index = 0 if self.tree_size > 0 else None
        self.compare_pair = None
        self.swap_pair = None
        self.msg_phase("2단계: 최대값 꺼내기")
        self.msg_action("Max Heap이 완성되었다.")
        self.msg_detail("이제 root의 최대값을 heap 끝으로 보내고 heap 크기를 줄인다.")
        self._update_stats()
        self.wait(1000)
        self.section_end()

    def finish_heapify(self, root):
        self.root_index = root
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_action(f"#{root} subtree를 heap 상태로 만들었다.")
        self.msg_detail("해당 subtree의 부모-자식 관계가 모두 heap 조건을 만족한다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def compare(self, left, right):
        self.compare_pair = (left, right)
        self.swap_pair = None
        self.swap_progress = 0.0
        self.compare_count += 1
        relation = self._compare_relation(left, right)
        self.msg_action(f"#{left}({self.array[left]}) 과 #{right}({self.array[right]}) 을 비교한다.")
        self.msg_detail(relation)
        self._update_stats()
        self.wait(850)

    def set_tree_size(self, size):
        self.tree_size = max(0, int(size))
        self.sorted_from = self.tree_size
        self.root_index = 0 if 1 < self.tree_size < len(self.array) else None
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        if self.tree_size < len(self.array):
            fixed = self.tree_size
            self.msg_action(f"#{fixed}({self.array[fixed]}) 를 heap에서 제외한다.")
            if self.root_index is None:
                self.msg_detail("방금 결정된 최대값은 정렬 완료 구간에 고정된다.")
            else:
                self.msg_detail("새 root 때문에 heap 조건이 깨졌는지 subtree 테두리로 확인한다.")
        else:
            self.msg_action("heap 영역을 설정한다.")
            self.msg_detail("아직 모든 원소가 heap 안에 있다.")
        self._update_stats()
        self.wait(900)

    def finish_downheap(self):
        self.root_index = 0 if self.tree_size > 0 else None
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_action("downheap으로 Max Heap을 회복했다.")
        self.msg_detail("이제 root에 현재 heap의 최대값이 있다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def finish(self):
        self.tree_size = 0
        self.sorted_from = 0
        self.root_index = None
        self.compare_pair = None
        self.swap_pair = None
        self.swap_progress = 0.0
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("최대값을 하나씩 뒤쪽 정렬 완료 구간으로 보냈다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 38, 42, colors.TEXT, True)
        self.text("배열을 max heap으로 만든 뒤, root의 최대값을 뒤로 보내며 heap 크기를 줄인다.", 72, 88, 22, colors.TEXT_MUTED)
        if self.show_tree or self.building_tree:
            self._draw_tree()
        self._draw_array()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count, start_x, top, box_width, box_height, gap = self._array_layout()
        value_size = max(12, min(28, box_width * 0.5))
        index_size = max(9, min(16, box_width * 0.3))

        swapping = set(self.swap_pair or ())
        draw_order = [index for index in range(count) if index not in swapping]
        draw_order += [index for index in range(count) if index in swapping]

        for index in draw_order:
            value = self.array[index]
            slot_x, slot_y = self._array_slot(index)
            x = slot_x
            y = slot_y
            if index in swapping:
                ox, oy = self._swap_offset(index, box_width + gap, box_height)
                x += ox
                y += oy

            fill = colors.PANEL
            border = colors.BORDER
            if index >= self.tree_size:
                fill = (35, 72, 52)
                border = colors.GREEN
            if index == self.root_index:
                border = colors.YELLOW
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, colors.TEXT, True)
            self.centered_text(f"#{index}", slot_x + box_width / 2, slot_y + box_height + 20, index_size, colors.TEXT_MUTED)

        if self.tree_size < count:
            self._draw_sorted_region(start_x, box_width, gap, top, box_height, count)

    def _draw_tree(self):
        if not self.array:
            return

        self._draw_root_boundary()
        for index in range(self.tree_size):
            self._draw_tree_edge(index, index * 2 + 1)
            self._draw_tree_edge(index, index * 2 + 2)
        for index in range(len(self.array)):
            self._draw_tree_node(index)

    def _draw_root_boundary(self):
        if self.root_index is None or self.root_index < 0 or self.root_index >= self.tree_size:
            return

        root = self.root_index
        nodes = self._subtree_nodes(root)
        if not nodes:
            return
        positions = [self._tree_node_pos(index, apply_swap=False) for index in nodes]
        xs = [pos[0] for pos in positions]
        ys = [pos[1] for pos in positions]
        radius = self._node_radius()
        margin = 18
        left = min(xs) - radius - margin
        top = min(ys) - radius - margin
        right = max(xs) + radius + margin
        bottom = max(ys) + radius + margin
        good = self._is_heap(root)
        fill = (31, 54, 75) if good else (58, 33, 35)
        border = (30, 96, 190) if good else (190, 30, 45)
        rect = self.view.rect(left, top, right - left, bottom - top)
        pygame.draw.rect(self.screen, fill, rect, border_radius=self.view.length(12))
        pygame.draw.rect(self.screen, border, rect, width=self.view.length(2), border_radius=self.view.length(12))
        pygame.draw.rect(self.screen, colors.YELLOW, rect, width=self.view.length(3), border_radius=self.view.length(12))

    def _draw_tree_edge(self, parent, child):
        if child >= self.tree_size:
            return

        px, py = self._tree_node_pos(parent, apply_swap=False)
        cx, cy = self._tree_node_pos(child, apply_swap=False)
        color = colors.GREEN if self.array[parent] >= self.array[child] else colors.RED
        pygame.draw.line(
            self.screen,
            color,
            self.view.point(px, py),
            self.view.point(cx, cy),
            self.view.length(4),
        )

    def _draw_tree_node(self, index):
        x, y = self._tree_node_pos(index)
        radius = self._node_radius()
        active = index < self.tree_size
        fill = colors.PANEL if active else (35, 72, 52)
        border = colors.BORDER if active else colors.GREEN
        text_color = colors.TEXT if active else colors.TEXT_MUTED
        if index == self.root_index:
            border = colors.YELLOW
        if self.compare_pair is not None and index in self.compare_pair:
            fill = (82, 55, 30)
            border = colors.ORANGE
            text_color = colors.TEXT
        if self.swap_pair is not None and index in self.swap_pair:
            fill = (62, 66, 107)
            border = colors.BLUE
            text_color = colors.TEXT

        rect = self.view.rect(x - radius, y - radius, radius * 2, radius * 2)
        pygame.draw.circle(self.screen, fill, self.view.point(x, y), self.view.length(radius))
        pygame.draw.circle(self.screen, border, self.view.point(x, y), self.view.length(radius), width=self.view.length(2))
        self.centered_text(self.array[index], x, y, max(12, radius * 0.72), text_color, True)
        self.centered_text(f"#{index}", x, y + radius + 18, 13, colors.TEXT_MUTED)

    def _tree_node_pos(self, index, apply_swap=True):
        if not self.array:
            return 0, 0

        level = int(math.log2(index + 1))
        first = 2**level - 1
        offset = index - first
        nodes_in_level = 2**level
        tree_left = 100
        tree_width = 1400
        tree_top = 158
        array_top = self._array_layout()[2]
        max_level = max(1, int(math.log2(max(1, len(self.array)))))
        row_height = max(46, min(76, (array_top - tree_top - 58) / max(1, max_level)))
        x = tree_left + tree_width * (offset + 0.5) / nodes_in_level
        y = tree_top + level * row_height

        if self.building_tree:
            ax, ay = self._array_slot_center(index)
            x = ax + (x - ax) * self.build_progress
            y = ay + (y - ay) * self.build_progress

        if apply_swap and self.swap_pair is not None and index in self.swap_pair:
            target = self.swap_pair[1] if index == self.swap_pair[0] else self.swap_pair[0]
            tx, ty = self._tree_node_pos(target, apply_swap=False)
            ox = (tx - x) * self.swap_progress
            oy = (ty - y) * self.swap_progress
            arc = -2 * (self.swap_progress - 0.5) ** 2 + 0.5
            oy -= arc * self._node_radius() * 1.3
            x += ox
            y += oy

        return x, y

    def _array_layout(self):
        count = len(self.array)
        gap = max(6, min(14, 180 / max(1, count)))
        max_area_width = 1380
        box_width = min(76, (max_area_width - gap * max(0, count - 1)) / max(1, count))
        box_height = 54
        start_x = 800 - (box_width * count + gap * max(0, count - 1)) / 2
        top = 535
        return count, start_x, top, box_width, box_height, gap

    def _array_slot(self, index):
        count, start_x, top, box_width, box_height, gap = self._array_layout()
        return start_x + index * (box_width + gap), top

    def _array_slot_center(self, index):
        count, start_x, top, box_width, box_height, gap = self._array_layout()
        return start_x + index * (box_width + gap) + box_width / 2, top + box_height / 2

    def _node_radius(self):
        return 25

    def _subtree_nodes(self, root):
        nodes = []
        stack = [root]
        while stack:
            index = stack.pop()
            if index >= self.tree_size:
                continue
            nodes.append(index)
            stack.append(index * 2 + 2)
            stack.append(index * 2 + 1)
        return nodes

    def _is_heap(self, root):
        if root >= self.tree_size:
            return True
        left = root * 2 + 1
        right = root * 2 + 2
        if left < self.tree_size:
            if self.array[root] < self.array[left] or not self._is_heap(left):
                return False
        if right < self.tree_size:
            if self.array[root] < self.array[right] or not self._is_heap(right):
                return False
        return True

    def _compare_relation(self, left, right):
        if left == 0 and right == self.tree_size - 1:
            return "root의 최대값을 heap 끝으로 보내기 위해 비교한다."
        if left > right:
            left, right = right, left
        parent = (right - 1) // 2
        if parent == left:
            if self.array[left] < self.array[right]:
                return "자식이 부모보다 크므로 교환이 필요하다."
            return "부모가 자식보다 크거나 같으므로 heap 조건을 만족한다."
        if (left - 1) // 2 == (right - 1) // 2:
            return "왼쪽/오른쪽 자식 중 더 큰 자식을 고른다."
        return "두 값을 비교한다."

    def _animate_build_tree(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.build_progress = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.build_progress = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.build_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.build_progress >= 1.0:
                break
            self.clock.tick(60)

    def _draw_sorted_region(self, start_x, box_width, gap, top, box_height, count):
        left = start_x + self.tree_size * (box_width + gap)
        right = start_x + count * box_width + (count - 1) * gap
        if right <= left:
            return
        margin = 7
        rect = self.view.rect(left - margin, top - margin, right - left + 2 * margin, box_height + 2 * margin)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(8),
        )
        self.centered_text("정렬 완료", (left + right) / 2, top - 26, 18, colors.GREEN, True)

    def _draw_legend(self):
        y = self._array_layout()[2] - 70
        self.text("표시", 200, y + 2, 18, colors.TEXT_MUTED, True)
        self.rect(280, y, 28, 20, (31, 54, 75), (30, 96, 190), 4)
        self.text("subtree heap", 320, y - 4, 18, colors.TEXT_MUTED)
        self.rect(520, y, 28, 20, colors.PANEL, (190, 30, 45), 4)
        self.text("heap 조건 위반", 560, y - 4, 18, colors.TEXT_MUTED)
        self.rect(780, y, 28, 20, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교", 820, y - 4, 18, colors.TEXT_MUTED)
        self.rect(920, y, 28, 20, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬 완료", 960, y - 4, 18, colors.TEXT_MUTED)

    def _update_stats(self):
        self.msg_stats(f"heap 크기 {self.tree_size}\n비교 {self.compare_count}회\n교환 {self.swap_count}회")


class CountSortVisualizer(BaseVisualizer):
    def __init__(self, title="Count Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.counts = []
        self.result = []
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.count_mode = "count"
        self.fly = None
        self.count_anim = None
        self.sum_anim = None
        self.scan_count = 0
        self.place_count = 0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.counts = []
        self.result = []
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.count_mode = "count"
        self.fly = None
        self.count_anim = None
        self.sum_anim = None
        self.scan_count = 0
        self.place_count = 0
        self.msg_phase("계수 정렬")
        self.msg_action("값의 종류가 많지 않은 정수 배열을 준비한다.")
        self.msg_detail("값을 직접 비교하지 않고, 각 값이 몇 번 나왔는지 센다.")
        self._update_stats()
        self.wait(700)

    def init_counts(self, counts):
        self.counts = list(counts)
        self.count_mode = "count"
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_phase("1단계: 개수 세기")
        self.msg_action("counts 배열을 0으로 초기화한다.")
        self.msg_detail("counts[v] 는 값 v가 지금까지 몇 번 나왔는지를 뜻한다.")
        self._update_stats()
        self.wait(900)

    def count_value(self, index, value, counts):
        new_counts = list(counts)
        old_counts = list(counts)
        old_counts[value] -= 1
        self.counts = old_counts
        self.current_array = index
        self.current_count = value
        self.current_count_pair = None
        self.current_result = None
        old_value = old_counts[value]
        new_value = new_counts[value]
        self.msg_action(f"array[{index}] 의 값 {value} 를 읽는다.")
        self.msg_detail(f"값 {value} 가 counts[{value}] 칸으로 날아가고, counts[{value}] 를 1 증가시킨다.")
        self.scan_count += 1
        self._update_stats()
        self._animate_fly(("array", index), ("count", value), str(value), 450)
        self.counts = new_counts
        self._animate_count(value, old_value, new_value, increasing=True, milliseconds=450)

    def count_item(self, index, item, key, counts):
        new_counts = list(counts)
        old_counts = list(counts)
        old_counts[key] -= 1
        self.counts = old_counts
        self.current_array = index
        self.current_count = key
        self.current_count_pair = None
        self.current_result = None
        old_value = old_counts[key]
        new_value = new_counts[key]
        self.msg_action(f"array[{index}] 의 {self._item_label(item)} 를 읽는다.")
        self.msg_detail(f"정렬 기준 {key} 를 사용해 counts[{key}] 를 1 증가시킨다.")
        self.scan_count += 1
        self._update_stats()
        self._animate_fly(("array", index), ("count", key), self._compact_label(item), 450)
        self.counts = new_counts
        self._animate_count(key, old_value, new_value, increasing=True, milliseconds=450)

    def finish_counting(self):
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_action("모든 원소를 세었다.")
        self.msg_detail("이제 counts 배열에는 각 값의 등장 횟수가 들어 있다.")
        self._update_stats()
        self.wait(900)
        self.section_end()

    def start_accumulate(self):
        self.count_mode = "accumulate"
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_phase("2단계: 누적합")
        self.msg_action("counts 배열을 누적합으로 바꾼다.")
        self.msg_detail("counts[i+1] += counts[i] 를 수행하면 위치 정보로 해석할 수 있다.")
        self._update_stats()
        self.wait(900)

    def accumulate(self, left, right, counts):
        old_counts = list(self.counts)
        new_counts = list(counts)
        left_value = old_counts[left]
        right_value = old_counts[right]
        result_value = new_counts[right]
        self.counts = old_counts
        self.current_count_pair = (left, right)
        self.current_count = right
        self.msg_action(f"counts[{right}] 에 counts[{left}] 를 더한다.")
        self.msg_detail(f"{left_value} + {right_value} = {result_value}; counts[{right}] 는 값 {right} 이하가 끝나는 위치 + 1 이 된다.")
        self._update_stats()
        self._animate_sum(left, right, left_value, right_value, result_value, milliseconds=900)
        self.counts = new_counts
        self.current_count_pair = None
        self.current_count = right
        self.wait(220)

    def finish_accumulate(self, counts):
        self.counts = list(counts)
        self.count_mode = "index"
        self.current_count = None
        self.current_count_pair = None
        self.msg_action("누적합 변환이 끝났다.")
        self.msg_detail("이제 counts[v] 는 값 v가 result에서 들어갈 다음 위치 + 1 로 해석한다.")
        self._update_stats()
        self.wait(1000)
        self.section_end()

    def init_result(self, result):
        self.result = list(result)
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.count_mode = "index"
        self.msg_phase("3단계: 결과 배열 채우기")
        self.msg_action("result 배열을 준비한다.")
        self.msg_detail("안정 정렬을 위해 원본 배열을 뒤에서부터 확인한다.")
        self._update_stats()
        self.wait(900)

    def place_value(self, index, value, at, counts, result):
        old_count = counts[value] + 1
        new_count = counts[value]
        self.current_array = index
        self.current_count = value
        self.current_count_pair = None
        self.current_result = at
        self.msg_action(f"뒤에서부터 array[{index}] 의 값 {value} 를 읽는다.")
        self.msg_detail(f"counts[{value}] 를 보고 result[{at}] 에 들어갈 위치를 정한다.")
        self._update_stats()
        self._animate_fly(("array", index), ("count", value), str(value), 450)

        self.counts = list(counts)
        self.msg_action(f"counts[{value}] 를 1 줄여 {at} 를 얻는다.")
        self.msg_detail(f"다음 값 {value} 는 result에서 그 앞쪽에 들어가게 된다.")
        self._update_stats()
        self._animate_count(value, old_count, new_count, increasing=False, milliseconds=450)

        self.msg_action(f"값 {value} 와 index {at} 를 result[{at}] 로 보낸다.")
        self.msg_detail(f"result[{at}] = {value}")
        self._update_stats()
        self._animate_fly(("count", value), ("result", at), f"{at}: {value}", 520)
        self.result = list(result)
        self.place_count += 1
        self.wait(250)

    def place_item(self, index, item, key, at, counts, result):
        old_count = counts[key] + 1
        new_count = counts[key]
        self.current_array = index
        self.current_count = key
        self.current_count_pair = None
        self.current_result = at
        self.msg_action(f"뒤에서부터 array[{index}] 의 {self._item_label(item)} 를 읽는다.")
        self.msg_detail(f"정렬 기준 {key} 로 counts[{key}] 를 보고 result[{at}] 위치를 정한다.")
        self._update_stats()
        self._animate_fly(("array", index), ("count", key), self._compact_label(item), 450)

        self.counts = list(counts)
        self.msg_action(f"counts[{key}] 를 1 줄여 {at} 를 얻는다.")
        self.msg_detail("같은 key의 원소를 뒤에서부터 배치하므로 원래 순서가 유지된다.")
        self._update_stats()
        self._animate_count(key, old_count, new_count, increasing=False, milliseconds=450)

        self.msg_action(f"index {at} 와 {self._item_label(item)} 를 result[{at}] 로 보낸다.")
        self.msg_detail(f"result[{at}] = {self._item_label(item)}")
        self._update_stats()
        self._animate_fly(("count", key), ("result", at), f"{at}: {self._compact_label(item)}", 520)
        self.result = list(result)
        self.place_count += 1
        self.wait(250)

    def finish(self):
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.fly = None
        self.count_anim = None
        self.sum_anim = None
        self.msg_phase("완료")
        self.msg_action("result 배열이 오름차순으로 채워졌다.")
        self.msg_detail("비교 대신 count 배열과 위치 정보를 이용해 정렬했다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 34, 40, colors.TEXT, True)
        self.text("값의 등장 횟수를 세고, 누적합을 위치 정보로 사용한다.", 72, 86, 22, colors.TEXT_MUTED)
        self._draw_array_row()
        self._draw_counts_row()
        self._draw_result_row()
        self._draw_sum_anim()
        self._draw_fly()

    def _draw_array_row(self):
        self._draw_row_title("array", 74, 148, "원본 배열")
        for index, value in enumerate(self.array):
            x, y, w, h = self._array_rect(index)
            fill = colors.PANEL
            border = colors.BORDER
            if index == self.current_array:
                fill = (82, 55, 30)
                border = colors.ORANGE
            self.rect(x, y, w, h, fill, border, 7)
            self._draw_item_label(value, x, y, w, h, colors.TEXT)
            if self._shows_grid_index(len(self.array), index):
                self.centered_text(f"#{index}", x + w / 2, y + h + 13, 11, colors.TEXT_MUTED)

    def _draw_counts_row(self):
        title = "counts: 개수" if self.count_mode == "count" else "counts: 끝 위치 + 1"
        self._draw_row_title("counts", 74, 326, title)
        for index, value in enumerate(self.counts):
            x, y, w, h = self._count_rect(index)
            fill = (28, 48, 56) if self.count_mode == "count" else (30, 51, 42)
            border = colors.BLUE if self.count_mode == "count" else colors.GREEN
            if self.current_count_pair is not None and index in self.current_count_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            elif index == self.current_count:
                fill = (82, 55, 30)
                border = colors.ORANGE
            self.rect(x, y, w, h, fill, border, 7)
            self._draw_count_value(index, value, x, y, w, h)
            self.centered_text(f"#{index}", x + w / 2, y - 16, 13, colors.TEXT_MUTED)

    def _draw_result_row(self):
        if not self.result:
            return
        self._draw_row_title("result", 74, 504, "결과 배열")
        for index, value in enumerate(self.result):
            x, y, w, h = self._result_rect(index)
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT if value is not None else colors.TEXT_MUTED
            if index == self.current_result:
                fill = (35, 72, 52)
                border = colors.GREEN
            self.rect(x, y, w, h, fill, border, 7)
            label = "" if value is None else value
            self._draw_item_label(label, x, y, w, h, text_color)
            if self._shows_grid_index(len(self.result), index):
                self.centered_text(f"#{index}", x + w / 2, y + h + 13, 11, colors.TEXT_MUTED)

    def _draw_formula(self):
        if self.count_mode == "count":
            lines = ["counts[v] += 1", "v = array[i]"]
        elif self.count_mode == "accumulate":
            lines = ["counts[i+1] += counts[i]", "counts[v] -> end + 1"]
        else:
            lines = ["at = counts[v] - 1", "counts[v] -= 1", "result[at] = v"]
        x, y = 1120, 122
        self.rect(x, y, 390, 112, colors.PANEL_DARK, colors.BORDER, 8)
        self.text("코드", x + 24, y + 18, 22, colors.BLUE, True)
        for row, line in enumerate(lines):
            self.mono_text(line, x + 118, y + 18 + row * 27, 18, colors.TEXT_MUTED)

    def _draw_row_title(self, name, x, y, detail):
        self.text(name, x, y, 24, colors.TEXT, True)
        self.text(detail, x + 110, y + 3, 18, colors.TEXT_MUTED)

    def _draw_count_value(self, index, value, x, y, w, h):
        if self.count_anim is None or self.count_anim["index"] != index:
            self.centered_text(value, x + w / 2, y + h / 2, self._card_text_size(w), colors.TEXT, True)
            return

        progress = self.count_anim["progress"]
        old_value = self.count_anim["old"]
        new_value = self.count_anim["new"]
        sign = -1 if self.count_anim["increasing"] else 1
        center_x = x + w / 2
        center_y = y + h / 2
        rect = self.view.rect(x, y, w, h)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(rect)
        self.centered_text(old_value, center_x, center_y + sign * h * progress, self._card_text_size(w), colors.TEXT_MUTED, True)
        self.centered_text(new_value, center_x, center_y + sign * h * (progress - 1), self._card_text_size(w), colors.TEXT, True)
        self.screen.set_clip(previous_clip)

    def _draw_fly(self):
        if self.fly is None:
            return
        sx, sy = self._center_for(self.fly["source"])
        tx, ty = self._center_for(self.fly["target"])
        progress = self.fly["progress"]
        x = sx + (tx - sx) * progress
        y = sy + (ty - sy) * progress
        y -= 36 * math.sin(math.pi * progress)
        label = self.fly["label"]
        width = max(48, 22 + len(label) * 11)
        self.rect(x - width / 2, y - 22, width, 44, (62, 66, 107), colors.YELLOW, 8)
        self.centered_text(label, x, y, 17, colors.TEXT, True)

    def _draw_sum_anim(self):
        if self.sum_anim is None:
            return

        progress = self.sum_anim["progress"]
        left = self.sum_anim["left"]
        right = self.sum_anim["right"]
        left_value = self.sum_anim["left_value"]
        right_value = self.sum_anim["right_value"]
        result_value = self.sum_anim["result_value"]

        left_center = self._center_for(("count", left))
        right_center = self._center_for(("count", right))
        formula_x = max(210, min(1390, (left_center[0] + right_center[0]) / 2))
        formula_y = min(left_center[1], right_center[1]) - 78
        left_term = (formula_x - 64, formula_y)
        right_term = (formula_x + 10, formula_y)
        result_term = (formula_x + 82, formula_y)

        if progress < 0.45:
            step = progress / 0.45
            self._draw_sum_badge(left_value, self._lerp_point(left_center, left_term, step), colors.ORANGE)
            self._draw_sum_badge(right_value, self._lerp_point(right_center, right_term, step), colors.BLUE)
            return

        self.rect(formula_x - 112, formula_y - 28, 260, 56, colors.PANEL_DARK, colors.BORDER, 8)
        self._draw_sum_formula(formula_x, formula_y, left_value, right_value, result_value)

        if progress < 0.68:
            return

        step = (progress - 0.68) / 0.32
        self._draw_sum_badge(
            result_value,
            self._lerp_point(result_term, right_center, step),
            colors.GREEN,
        )

    def _draw_sum_formula(self, center_x, center_y, left_value, right_value, result_value):
        self.mono_text(str(left_value), center_x - 78, center_y - 12, 22, colors.TEXT, True)
        self.mono_text("+", center_x - 31, center_y - 12, 22, colors.TEXT_MUTED, True)
        self.mono_text(str(right_value), center_x - 5, center_y - 12, 22, colors.TEXT, True)
        self.mono_text("=", center_x + 42, center_y - 12, 22, colors.TEXT_MUTED, True)
        self.mono_text(str(result_value), center_x + 72, center_y - 12, 22, colors.GREEN, True)

    def _draw_sum_badge(self, value, center, border):
        label = str(value)
        width = max(48, 22 + len(label) * 13)
        x, y = center
        self.rect(x - width / 2, y - 22, width, 44, (62, 66, 107), border, 8)
        self.centered_text(label, x, y, 19, colors.TEXT, True)

    def _lerp_point(self, start, end, progress):
        x = start[0] + (end[0] - start[0]) * progress
        y = start[1] + (end[1] - start[1]) * progress
        y -= 24 * math.sin(math.pi * progress)
        return x, y

    def _draw_item_label(self, item, x, y, w, h, color):
        if item == "":
            return
        name, key = self._item_parts(item)
        if key is None:
            self.centered_text(name, x + w / 2, y + h / 2, self._card_text_size(w), color, True)
            return
        self.centered_text(name, x + w / 2, y + h * 0.34, max(10, min(16, w * 0.28)), color, True)
        self.centered_text(key, x + w / 2, y + h * 0.69, max(10, min(17, w * 0.32)), colors.TEXT_MUTED, True)

    def _item_label(self, item):
        name, key = self._item_parts(item)
        if key is None:
            return name
        return f"{name}({key})"

    def _compact_label(self, item):
        name, key = self._item_parts(item)
        if key is None:
            return name
        return f"{name}/{key}"

    def _item_parts(self, item):
        if hasattr(item, "name") and hasattr(item, "age"):
            return str(item.name), str(item.age)
        if isinstance(item, dict) and "name" in item and "age" in item:
            return str(item["name"]), str(item["age"])
        return str(item), None

    def _array_rect(self, index):
        return self._grid_rect(len(self.array), 145, index)

    def _count_rect(self, index):
        return self._row_rect(max(1, len(self.counts)), 372, index, max_width=980, max_card=58)

    def _result_rect(self, index):
        return self._grid_rect(len(self.result), 455, index)

    def _grid_rect(self, count, top, index):
        columns = self._grid_columns(count)
        gap = 4 if count >= 80 else 6
        max_width = 1370
        width = min(58, (max_width - gap * max(0, columns - 1)) / max(1, columns))
        max_height = 34 if count >= 80 else 40 if count >= 40 else 48
        height = min(width, max_height)
        start_x = 800 - (width * columns + gap * max(0, columns - 1)) / 2
        col = index % columns
        row = index // columns
        return start_x + col * (width + gap), top + row * (height + gap), width, height

    def _grid_columns(self, count):
        return 20 if count < 80 else 30

    def _shows_grid_index(self, count, index):
        if count < 40:
            return True
        return index == self.current_array or index == self.current_result

    def _row_rect(self, count, top, index, max_width=1370, max_card=58):
        gap = max(5, min(12, 150 / max(1, count)))
        width = min(max_card, (max_width - gap * max(0, count - 1)) / max(1, count))
        height = 48
        start_x = 800 - (width * count + gap * max(0, count - 1)) / 2
        return start_x + index * (width + gap), top, width, height

    def _center_for(self, target):
        kind, index = target
        if kind == "array":
            x, y, w, h = self._array_rect(index)
        elif kind == "count":
            x, y, w, h = self._count_rect(index)
        else:
            x, y, w, h = self._result_rect(index)
        return x + w / 2, y + h / 2

    def _card_text_size(self, width):
        return max(13, min(24, width * 0.45))

    def _animate_fly(self, source, target, label, milliseconds):
        self.fly = {"source": source, "target": target, "label": label, "progress": 0.0}
        self._animate_state(self.fly, milliseconds)
        self.fly = None

    def _animate_count(self, index, old_value, new_value, increasing, milliseconds):
        self.count_anim = {
            "index": index,
            "old": old_value,
            "new": new_value,
            "increasing": increasing,
            "progress": 0.0,
        }
        self._animate_state(self.count_anim, milliseconds)
        self.count_anim = None

    def _animate_sum(self, left, right, left_value, right_value, result_value, milliseconds):
        self.sum_anim = {
            "left": left,
            "right": right,
            "left_value": left_value,
            "right_value": right_value,
            "result_value": result_value,
            "progress": 0.0,
        }
        self._animate_state(self.sum_anim, milliseconds)
        self.sum_anim = None

    def _animate_state(self, state, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            state["progress"] = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                state["progress"] = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            state["progress"] = min(1.0, active_elapsed / duration)
            self.draw()
            if state["progress"] >= 1.0:
                break
            self.clock.tick(60)

    def _update_stats(self):
        self.msg_stats(f"읽은 원소 {self.scan_count}개\n배치 {self.place_count}개")


class RadixLsdVisualizer(CountSortVisualizer):
    def __init__(self, title="Radix Sort: LSD", **kwargs):
        super().__init__(title, **kwargs)
        self.current_div = 1
        self.current_pass = 0
        self.total_passes = 0
        self.result_move_anim = None

    def setup(self, data):
        super().setup(data)
        self.current_div = 1
        self.current_pass = 0
        self.total_passes = 0
        self.result_move_anim = None
        self.msg_phase("LSD 기수 정렬")
        self.msg_action("가장 낮은 자리수부터 안정 정렬을 반복한다.")
        self.msg_detail("각 자리수 정렬은 0~9에 대한 계수 정렬로 수행한다.")
        self._update_stats()
        self.wait(700)

    def start_digit(self, pass_no, total_passes, div):
        self.current_pass = pass_no
        self.total_passes = total_passes
        self.current_div = div
        self.counts = []
        self.result = []
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_phase(f"{pass_no}/{total_passes}단계: {self._digit_name()} 자리")
        self.msg_action(f"각 수에서 {self._digit_name()} 자리 숫자를 읽는다.")
        self.msg_detail(f"digit = number // {div} % 10")
        self._update_stats()
        self.wait(900)

    def init_counts(self, counts):
        self.counts = list(counts)
        self.count_mode = "count"
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_action("0~9 digit을 담을 counts 배열을 0으로 초기화한다.")
        self.msg_detail(f"counts[d] 는 {self._digit_name()} 자리 숫자 d가 몇 번 나왔는지를 뜻한다.")
        self._update_stats()
        self.wait(800)

    def count_digit(self, index, number, digit, counts):
        new_counts = list(counts)
        old_counts = list(counts)
        old_counts[digit] -= 1
        self.counts = old_counts
        self.current_array = index
        self.current_count = digit
        self.current_count_pair = None
        self.current_result = None
        old_value = old_counts[digit]
        new_value = new_counts[digit]
        self.msg_action(f"array[{index}] = {number}, {self._digit_name()} 자리 digit은 {digit} 이다.")
        self.msg_detail(f"digit {digit} 이 counts[{digit}] 칸으로 날아가고, counts[{digit}] 를 1 증가시킨다.")
        self.scan_count += 1
        self._update_stats()
        self._animate_fly(("array", index), ("count", digit), str(digit), 450)
        self.counts = new_counts
        self._animate_count(digit, old_value, new_value, increasing=True, milliseconds=450)

    def finish_counting(self):
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_action(f"{self._digit_name()} 자리 digit을 모두 세었다.")
        self.msg_detail("이제 counts 배열에는 0~9 digit의 등장 횟수가 들어 있다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def place_digit(self, index, number, digit, at, counts, result):
        old_count = counts[digit] + 1
        new_count = counts[digit]
        self.current_array = index
        self.current_count = digit
        self.current_count_pair = None
        self.current_result = at
        self.msg_action(f"뒤에서부터 array[{index}] = {number} 를 읽는다.")
        self.msg_detail(f"{self._digit_name()} 자리 digit {digit} 로 result[{at}] 위치를 정한다.")
        self._update_stats()
        self._animate_fly(("array", index), ("count", digit), str(digit), 450)

        self.counts = list(counts)
        self.msg_action(f"counts[{digit}] 를 1 줄여 {at} 를 얻는다.")
        self.msg_detail("뒤에서부터 배치하므로 이전 자리수에서 만든 순서가 유지된다.")
        self._update_stats()
        self._animate_count(digit, old_count, new_count, increasing=False, milliseconds=450)

        self.msg_action(f"{number} 를 result[{at}] 로 보낸다.")
        self.msg_detail(f"result[{at}] = {number}")
        self._update_stats()
        self._animate_fly(("count", digit), ("result", at), str(number), 520)
        self.result = list(result)
        self.place_count += 1
        self.wait(230)

    def finish_result(self, result):
        self.result = list(result)
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_action(f"{self._digit_name()} 자리 기준으로 result 배열을 완성했다.")
        self.msg_detail("아직 다음 자리수 정렬을 위해 array로 복사하지는 않았다.")
        self._update_stats()
        self.wait(900)
        self.section_end()

    def result_to_array(self, result):
        self.result = list(result)
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.msg_action("result 배열을 다시 array로 복사한다.")
        self.msg_detail("다음 자리수 정렬은 이 배열을 기준으로 계속한다.")
        self._update_stats()
        self._animate_result_to_array(850)
        self.array = list(result)
        self.result = []
        self.wait(250)
        self.section_end()

    def finish(self):
        self.current_array = None
        self.current_count = None
        self.current_count_pair = None
        self.current_result = None
        self.fly = None
        self.count_anim = None
        self.sum_anim = None
        self.result_move_anim = None
        self.msg_phase("완료")
        self.msg_action("모든 자리수에 대해 안정 정렬을 마쳤다.")
        self.msg_detail("낮은 자리수부터 정렬했기 때문에 전체 숫자가 오름차순이 된다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 34, 40, colors.TEXT, True)
        self.text("낮은 자리수부터 각 digit에 대해 계수 정렬을 반복한다.", 72, 86, 22, colors.TEXT_MUTED)
        self.right_text(self._pass_status(), 1510, 42, 22, colors.BLUE, True)
        self._draw_array_row()
        self._draw_counts_row()
        self._draw_result_row()
        self._draw_sum_anim()
        self._draw_fly()

    def _draw_item_label(self, item, x, y, w, h, color):
        if item == "" or item is None:
            return
        try:
            number = int(item)
        except (TypeError, ValueError):
            super()._draw_item_label(item, x, y, w, h, color)
            return
        digit = number // self.current_div % 10
        number_size = max(11, min(20, w * 0.33))
        digit_size = max(10, min(16, w * 0.28))
        self.centered_text(number, x + w / 2, y + h * 0.38, number_size, color, True)
        self.centered_text(digit, x + w / 2, y + h * 0.72, digit_size, colors.ORANGE, True)

    def _result_rect(self, index):
        x, y, w, h = super()._result_rect(index)
        if self.result_move_anim is None:
            return x, y, w, h
        tx, ty, tw, th = super()._array_rect(index)
        progress = self.result_move_anim["progress"]
        return (
            x + (tx - x) * progress,
            y + (ty - y) * progress,
            w + (tw - w) * progress,
            h + (th - h) * progress,
        )

    def _digit_name(self):
        if self.current_div == 1:
            return "1의"
        if self.current_div == 10:
            return "10의"
        if self.current_div == 100:
            return "100의"
        return f"{self.current_div}의"

    def _pass_status(self):
        if self.total_passes == 0:
            return ""
        return f"{self.current_pass}/{self.total_passes}  {self._digit_name()} 자리"

    def _animate_result_to_array(self, milliseconds):
        self.result_move_anim = {"progress": 0.0}
        self._animate_state(self.result_move_anim, milliseconds)
        self.result_move_anim = None


class RadixMsdWordsVisualizer(CountSortVisualizer):
    def __init__(self, title="Radix Sort: MSD", **kwargs):
        super().__init__(title, **kwargs)
        self.set_message_layout("side")
        self.words = []
        self.temp = []
        self.left = 0
        self.right = -1
        self.depth = 0
        self.word_depths = []
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.result_move_anim = None
        self.stack = []
        self.word_scroll_offset = 0
        self.word_scroll_target = 0
        self.temp_scroll_offset = 0
        self.temp_scroll_target = 0
        self.layout_mode = "grid"
        self.layout_anim = None

    def setup(self, data):
        self.set_data_info(data)
        self.words = list(data.array)
        self.temp = [None] * len(self.words)
        self.counts = []
        self.left = 0
        self.right = len(self.words) - 1
        self.depth = 0
        self.word_depths = [0] * len(self.words)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.current_count_pair = None
        self.count_anim = None
        self.sum_anim = None
        self.fly = None
        self.result_move_anim = None
        self.stack = []
        self.word_scroll_offset = 0
        self.word_scroll_target = 0
        self.temp_scroll_offset = 0
        self.temp_scroll_target = 0
        self.layout_mode = "grid"
        self.layout_anim = None
        self.scan_count = 0
        self.place_count = 0
        self.msg_phase("MSD 기수 정렬")
        self.msg_action("정렬할 단어들을 준비한다.")
        self.msg_detail("처음에는 전체 단어를 한눈에 볼 수 있도록 grid로 배치한다.")
        self._update_stats()
        self.wait(900)

    def line_up(self):
        self.layout_mode = "grid"
        self.layout_anim = {"from": "grid", "to": "line", "progress": 0.0}
        self.word_scroll_offset = 0
        self.word_scroll_target = 0
        self.temp_scroll_offset = 0
        self.temp_scroll_target = 0
        self.msg_action("단어들을 1열 배열로 세운다.")
        self.msg_detail("이제 앞 글자부터 같은 글자 구간을 재귀적으로 정렬한다.")
        self._update_stats()
        self._animate_state(self.layout_anim, 900)
        self.layout_anim = None
        self.layout_mode = "line"
        self.wait(250)

    def push(self, left, right, depth):
        self.left = left
        self.right = right
        self.depth = depth
        self.stack.append((left, right, depth))
        for index in range(left, right + 1):
            self.word_depths[index] = max(self.word_depths[index], depth)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.current_count_pair = None
        self.msg_phase(f"depth {depth}: [{left}, {right}] 구간")
        self.msg_action(f"push [{left}, {right}], depth {depth}")
        self.msg_detail("스택 맨 위 구간의 단어들을 해당 depth 글자로 분류한다.")
        self._update_stats()
        self.wait(850)

    def init_counts(self, counts):
        self.counts = list(counts)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.current_count_pair = None
        self.msg_action("end, a~z bucket의 개수를 0으로 초기화한다.")
        self.msg_detail(f"각 단어의 {self.depth}번째 글자를 확인한다.")
        self._update_stats()
        self.wait(650)

    def scan(self, index, bucket, counts):
        new_counts = list(counts)
        old_counts = list(counts)
        old_counts[bucket] -= 1
        self.counts = old_counts
        self.active_word = index
        self.active_bucket = bucket
        self.active_result = None
        word = self.words[index]
        label = self._bucket_label(bucket)
        self.msg_action(f"#{index} {word}: depth {self.depth} 글자는 {label} 이다.")
        self.msg_detail(f"{label} bucket으로 보내고 counts[{label}] 를 1 증가시킨다.")
        self.scan_count += 1
        self._update_stats()
        self._animate_fly(("word", index), ("bucket", bucket), word, 430)
        self.counts = new_counts
        self._animate_count(bucket, old_counts[bucket], new_counts[bucket], increasing=True, milliseconds=380)

    def finish_counting(self):
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.msg_action("현재 구간의 모든 단어를 bucket별로 세었다.")
        self.msg_detail("counts를 누적합으로 바꾸면 각 bucket의 배치 위치를 알 수 있다.")
        self._update_stats()
        self.wait(750)
        self.section_end()

    def start_accumulate(self):
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.current_count_pair = None
        self.msg_action("bucket counts를 indexes로 바꾼다.")
        self.msg_detail("앞 bucket의 개수를 뒤 bucket에 누적한다.")
        self._update_stats()
        self.wait(650)

    def accumulate_bucket(self, left, right, counts):
        old_counts = list(self.counts)
        new_counts = list(counts)
        left_value = old_counts[left]
        right_value = old_counts[right]
        result_value = new_counts[right]
        self.counts = old_counts
        self.current_count_pair = (left, right)
        self.active_bucket = right
        self.msg_action(f"{self._bucket_label(right)} bucket에 이전 누적값을 더한다.")
        self.msg_detail(f"{left_value} + {right_value} = {result_value}")
        self._update_stats()
        self._animate_sum(left, right, left_value, right_value, result_value, milliseconds=700)
        self.counts = new_counts
        self.current_count_pair = None
        self.wait(180)

    def finish_accumulate(self, counts):
        self.counts = list(counts)
        self.active_bucket = None
        self.current_count_pair = None
        self.msg_action("bucket별 끝 위치 + 1 계산을 마쳤다.")
        self.msg_detail("이 값을 하나씩 줄여가며 temp 배열의 위치를 정한다.")
        self._update_stats()
        self.wait(750)
        self.section_end()

    def init_result(self, temp):
        self.temp = list(temp)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.msg_action("현재 구간을 담을 temp 배열을 준비한다.")
        self.msg_detail("안정 정렬을 위해 오른쪽 단어부터 배치한다.")
        self._update_stats()
        self.wait(650)

    def place(self, index, bucket, at, counts, temp):
        word = self.words[index]
        old_count = counts[bucket] + 1
        new_count = counts[bucket]
        self.active_word = index
        self.active_bucket = bucket
        self.active_result = at
        self.msg_action(f"뒤에서부터 #{index} {word} 를 읽는다.")
        self.msg_detail(f"{self._bucket_label(bucket)} bucket의 index로 temp[{at}] 위치를 정한다.")
        self._update_stats()
        self._animate_fly(("word", index), ("bucket", bucket), word, 400)

        self.counts = list(counts)
        self.msg_action(f"counts[{self._bucket_label(bucket)}] 를 1 줄여 {at - self.left} 를 얻는다.")
        self.msg_detail("같은 글자 안에서는 기존 순서가 유지된다.")
        self._update_stats()
        self._animate_count(bucket, old_count, new_count, increasing=False, milliseconds=360)

        self.msg_action(f"{word} 를 temp[{at}] 로 보낸다.")
        self.msg_detail(f"temp[{at}] = {word}")
        self._update_stats()
        self._animate_fly(("bucket", bucket), ("result", at), word, 460)
        self.temp = list(temp)
        self.place_count += 1
        self.wait(200)

    def finish_result(self, temp):
        self.temp = list(temp)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.msg_action("현재 depth 기준으로 temp 배열을 완성했다.")
        self.msg_detail("아직 원본 배열 구간으로 복사하지는 않았다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def copy_back(self, temp):
        self.temp = list(temp)
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.msg_action("temp의 현재 구간을 단어 배열로 복사한다.")
        self.msg_detail("같은 bucket 구간은 다음 depth에서 다시 정렬한다.")
        self._update_stats()
        self._animate_result_to_words(750)
        for index in range(self.left, self.right + 1):
            self.words[index] = temp[index]
        self.temp = [None] * len(self.words)
        self.wait(220)
        self.section_end()

    def pop(self):
        if self.stack:
            left, right, depth = self.stack.pop()
            self.left = left
            self.right = right
            self.depth = depth
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.msg_action(f"pop [{self.left}, {self.right}], depth {self.depth}")
        self.msg_detail("현재 구간 처리를 마치고 이전 재귀 구간으로 돌아간다.")
        self._update_stats()
        self.wait(550)
        self.section_end()

    def skip(self, left, right, depth):
        self.left = left
        self.right = right
        self.depth = depth
        self.msg_action(f"[{left}, {right}] 구간은 더 나눌 필요가 없다.")
        self.msg_detail("원소가 하나이거나 단어가 끝난 bucket이다.")
        self._update_stats()
        self.wait(420)

    def finish(self):
        self.left = 0
        self.right = len(self.words) - 1
        self.active_word = None
        self.active_bucket = None
        self.active_result = None
        self.fly = None
        self.count_anim = None
        self.sum_anim = None
        self.result_move_anim = None
        self.layout_mode = "line"
        self.msg_phase("완료")
        self.msg_action("모든 재귀 구간의 정렬을 마쳤다.")
        self.msg_detail("앞 글자부터 나누었으므로 문자열이 사전순으로 정렬되었다.")
        self._update_stats()
        self.wait(800)
        self.layout_anim = {"from": "line", "to": "grid", "progress": 0.0}
        self.msg_action("정렬된 단어들을 다시 grid 형태로 펼친다.")
        self.msg_detail("grid에서도 정렬된 순서는 왼쪽 위에서 오른쪽 아래로 이어진다.")
        self._update_stats()
        self._animate_state(self.layout_anim, 900)
        self.layout_anim = None
        self.layout_mode = "grid"
        self.word_scroll_offset = 0
        self.temp_scroll_offset = 0
        self.wait(900)

    def draw_content(self):
        if self._uses_line_layout():
            self._update_scroll_offsets()
        else:
            self.word_scroll_offset = 0
            self.temp_scroll_offset = 0
        self.text(self.title, 70, 34, 40, colors.TEXT, True)
        self.text("앞 글자로 나누고, 같은 글자 구간만 다음 글자로 재귀 정렬한다.", 72, 86, 22, colors.TEXT_MUTED)
        if self._uses_line_layout():
            self._draw_depth_guides()
        self._draw_words()
        if self._uses_line_layout():
            self._draw_buckets()
            self._draw_temp()
            self._draw_stack()
            self._draw_sum_anim()
            self._draw_fly()

    def _draw_words(self):
        self._draw_row_title("array", 74, 132, "단어 배열")
        for index, word in enumerate(self.words):
            x, y, w, h = self._word_rect(index)
            if not self._is_visible_row(y, h):
                continue
            fill = colors.PANEL
            border = colors.BORDER
            if self.left <= index <= self.right:
                border = colors.BLUE
            if index == self.active_word:
                fill = (82, 55, 30)
                border = colors.ORANGE
            self.rect(x, y, w, h, fill, border, 6)
            self.text(word, x + 8, y + 5, self._word_text_size(w), colors.TEXT, True)
            if self._uses_line_layout():
                self.text(self._char_info(word), x + w + 10, y + 6, 15, colors.ORANGE if self.left <= index <= self.right else colors.TEXT_MUTED)
                self.right_text(f"#{index}", x - 8, y + 7, 13, colors.TEXT_MUTED)

    def _draw_buckets(self):
        self._draw_row_title("bucket", 500, 132, "end, a~z")
        for bucket in range(27):
            x, y, w, h = self._bucket_rect(bucket)
            fill = (28, 48, 56)
            border = colors.BLUE
            if self.current_count_pair is not None and bucket in self.current_count_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            elif bucket == self.active_bucket:
                fill = (82, 55, 30)
                border = colors.ORANGE
            self.rect(x, y, w, h, fill, border, 4)
            self.text(self._bucket_label(bucket), x + 7, y + 3, 13, colors.TEXT_MUTED)
            value = self.counts[bucket] if bucket < len(self.counts) else 0
            self._draw_bucket_value(bucket, value, x + 58, y, 42, h)

    def _draw_temp(self):
        self._draw_row_title("temp", 680, 132, "재배치 결과")
        for index, word in enumerate(self.temp):
            if word is None and not (self.left <= index <= self.right):
                continue
            x, y, w, h = self._result_rect(index)
            if not self._is_visible_row(y, h):
                continue
            fill = colors.PANEL
            border = colors.BORDER
            if self.left <= index <= self.right:
                border = colors.GREEN
            if index == self.active_result:
                fill = (35, 72, 52)
                border = colors.GREEN
            self.rect(x, y, w, h, fill, border, 6)
            label = "" if word is None else word
            self.text(label, x + 10, y + 5, 18, colors.TEXT, True)
            self.right_text(f"#{index}", x - 8, y + 7, 13, colors.TEXT_MUTED)

    def _draw_stack(self):
        x, y = 1140, 600
        self.text("현재 구간", x, y, 20, colors.BLUE, True)
        self.mono_text(f"depth {self.depth}  [{self.left},{self.right}]", x, y + 30, 18, colors.TEXT, True)
        self.text("stack", x, y + 72, 20, colors.TEXT, True)
        recent = self.stack[-4:]
        for row, (left, right, depth) in enumerate(reversed(recent)):
            top = y + 106 + row * 32
            fill = (35, 72, 52) if row == 0 else colors.PANEL
            border = colors.GREEN if row == 0 else colors.BORDER
            self.rect(x, top, 330, 26, fill, border, 5)
            self.mono_text(f"d{depth} [{left},{right}]", x + 12, top + 5, 15, colors.TEXT, row == 0)

    def _draw_depth_guides(self):
        max_depth = min(max(self.word_depths or [0]), 4)
        if max_depth <= 0:
            return
        top = self._visible_top() - 8
        bottom = self._visible_bottom() + 8
        for depth in range(1, max_depth + 1):
            for base_x in (92, 720):
                x = base_x + depth * 18 - 8
                pygame.draw.line(
                    self.screen,
                    (45, 70, 86),
                    self.view.point(x, top),
                    self.view.point(x, bottom),
                    self.view.length(1),
                )
                self.mono_text(f"d{depth}", x + 4, top - 22, 12, colors.TEXT_MUTED)

    def _draw_bucket_value(self, bucket, value, x, y, w, h):
        if self.count_anim is None or self.count_anim["index"] != bucket:
            self.centered_text(value, x + w / 2, y + h / 2, 16, colors.TEXT, True)
            return
        progress = self.count_anim["progress"]
        old_value = self.count_anim["old"]
        new_value = self.count_anim["new"]
        sign = -1 if self.count_anim["increasing"] else 1
        rect = self.view.rect(x, y, w, h)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(rect)
        self.centered_text(old_value, x + w / 2, y + h / 2 + sign * h * progress, 16, colors.TEXT_MUTED, True)
        self.centered_text(new_value, x + w / 2, y + h / 2 + sign * h * (progress - 1), 16, colors.TEXT, True)
        self.screen.set_clip(previous_clip)

    def _draw_sum_anim(self):
        if self.sum_anim is None:
            return
        progress = self.sum_anim["progress"]
        left = self.sum_anim["left"]
        right = self.sum_anim["right"]
        left_value = self.sum_anim["left_value"]
        right_value = self.sum_anim["right_value"]
        result_value = self.sum_anim["result_value"]
        left_center = self._center_for(("bucket", left))
        right_center = self._center_for(("bucket", right))
        formula_x = 800
        formula_y = (left_center[1] + right_center[1]) / 2
        left_term = (formula_x - 64, formula_y)
        right_term = (formula_x + 10, formula_y)
        result_term = (formula_x + 82, formula_y)
        if progress < 0.45:
            step = progress / 0.45
            self._draw_sum_badge(left_value, self._lerp_point(left_center, left_term, step), colors.ORANGE)
            self._draw_sum_badge(right_value, self._lerp_point(right_center, right_term, step), colors.BLUE)
            return
        self.rect(formula_x - 112, formula_y - 28, 260, 56, colors.PANEL_DARK, colors.BORDER, 8)
        self._draw_sum_formula(formula_x, formula_y, left_value, right_value, result_value)
        if progress < 0.68:
            return
        step = (progress - 0.68) / 0.32
        self._draw_sum_badge(result_value, self._lerp_point(result_term, right_center, step), colors.GREEN)

    def _draw_fly(self):
        if self.fly is None:
            return
        sx, sy = self._center_for(self.fly["source"])
        tx, ty = self._center_for(self.fly["target"])
        progress = self.fly["progress"]
        x = sx + (tx - sx) * progress
        y = sy + (ty - sy) * progress
        y -= 30 * math.sin(math.pi * progress)
        label = self.fly["label"]
        width = max(72, 22 + len(label) * 10)
        self.rect(x - width / 2, y - 18, width, 36, (62, 66, 107), colors.YELLOW, 8)
        self.centered_text(label, x, y, 15, colors.TEXT, True)

    def _word_rect(self, index):
        if self.layout_anim is not None:
            source = self._layout_rect(index, self.layout_anim["from"])
            target = self._layout_rect(index, self.layout_anim["to"])
            return self._interpolate_rect(source, target, self.layout_anim["progress"])
        return self._layout_rect(index, self.layout_mode)

    def _layout_rect(self, index, mode):
        if mode == "grid":
            return self._grid_word_rect(index)
        return self._line_word_rect(index)

    def _line_word_rect(self, index):
        top = 170
        row_h = self._word_row_height()
        x = 92 + self._depth_indent(index)
        y = top + index * row_h - self.word_scroll_offset
        if self.result_move_anim is not None and self.left <= index <= self.right:
            sx, sy, sw, sh = self._result_rect(index)
            progress = self.result_move_anim["progress"]
            tx, ty, tw, th = x, y, 178, 28
            return sx + (tx - sx) * progress, sy + (ty - sy) * progress, sw + (tw - sw) * progress, sh + (th - sh) * progress
        return x, y, 178, 28

    def _grid_word_rect(self, index):
        columns = self._grid_columns_for_words()
        gap = 8 if columns <= 5 else 6
        width = min(176, (1000 - gap * (columns - 1)) / columns)
        height = 28
        left = 74
        top = 172
        col = index % columns
        row = index // columns
        return left + col * (width + gap), top + row * 34, width, height

    def _bucket_rect(self, bucket):
        return 500, 170 + bucket * 24, 105, 21

    def _result_rect(self, index):
        top = 170
        return 720 + self._depth_indent(index), top + index * self._word_row_height() - self.temp_scroll_offset, 178, 28

    def _word_row_height(self):
        return 34

    def _depth_indent(self, index):
        return min(self.word_depths[index], 4) * 18

    def _grid_columns_for_words(self):
        if len(self.words) <= 40:
            return 5
        return 7

    def _interpolate_rect(self, source, target, progress):
        return tuple(source[i] + (target[i] - source[i]) * progress for i in range(4))

    def _uses_line_layout(self):
        if self.layout_mode == "line":
            return True
        if self.layout_anim is None:
            return False
        return self.layout_anim["from"] == "line" or self.layout_anim["to"] == "line"

    def _word_text_size(self, width):
        return max(11, min(18, width * 0.12))

    def _target_scroll_offset(self, focus):
        if not self.words:
            return 0
        row_h = self._word_row_height()
        visible_height = self._visible_bottom() - self._visible_top()
        total_height = len(self.words) * row_h
        max_offset = max(0, total_height - visible_height)
        wanted = focus * row_h - visible_height * 0.45
        return max(0, min(max_offset, wanted))

    def _update_scroll_offsets(self):
        if self._current_range_fits():
            self.word_scroll_target = self._range_scroll_offset(self.word_scroll_offset)
            self.temp_scroll_target = self._range_scroll_offset(self.temp_scroll_offset)
        else:
            self.word_scroll_target = self._target_scroll_offset(self._word_focus_index())
            self.temp_scroll_target = self._target_scroll_offset(self._temp_focus_index())
        if self.is_max_speed() or self.running_to_section:
            self.word_scroll_offset = self.word_scroll_target
            self.temp_scroll_offset = self.temp_scroll_target
            return
        self.word_scroll_offset = self._approach_scroll(self.word_scroll_offset, self.word_scroll_target)
        self.temp_scroll_offset = self._approach_scroll(self.temp_scroll_offset, self.temp_scroll_target)

    def _approach_scroll(self, current, target):
        delta = target - current
        if abs(delta) < 0.5:
            return target
        return current + delta * 0.18

    def _word_focus_index(self):
        if self.active_word is not None:
            return self.active_word
        if self.left <= self.right:
            return (self.left + self.right) / 2
        return 0

    def _temp_focus_index(self):
        if self.active_result is not None:
            return self.active_result
        if self.left <= self.right:
            return (self.left + self.right) / 2
        return 0

    def _current_range_fits(self):
        if self.left > self.right:
            return True
        row_h = self._word_row_height()
        range_height = (self.right - self.left + 1) * row_h
        return range_height <= self._visible_bottom() - self._visible_top()

    def _range_scroll_offset(self, current_offset):
        row_h = self._word_row_height()
        visible_height = self._visible_bottom() - self._visible_top()
        total_height = len(self.words) * row_h
        max_offset = max(0, total_height - visible_height)
        range_top = self.left * row_h
        range_bottom = (self.right + 1) * row_h
        visible_top = current_offset
        visible_bottom = current_offset + visible_height
        margin = 18
        if range_top >= visible_top + margin and range_bottom <= visible_bottom - margin:
            return current_offset
        if range_top < visible_top + margin:
            wanted = range_top - margin
        else:
            wanted = range_bottom - visible_height + margin
        return max(0, min(max_offset, wanted))

    def _visible_top(self):
        return 170

    def _visible_bottom(self):
        return 760

    def _is_visible_row(self, y, height):
        return y + height >= self._visible_top() - 6 and y <= self._visible_bottom() + 6

    def _center_for(self, target):
        kind, index = target
        if kind == "word":
            x, y, w, h = self._word_rect(index)
        elif kind == "bucket":
            x, y, w, h = self._bucket_rect(index)
        else:
            x, y, w, h = self._result_rect(index)
        return x + w / 2, y + h / 2

    def _char_info(self, word):
        if self.depth >= len(word):
            return f"{self.depth}:end"
        return f"{self.depth}:{word[self.depth]}"

    def _bucket_label(self, bucket):
        if bucket == 0:
            return "end"
        return chr(ord("a") + bucket - 1)

    def _animate_result_to_words(self, milliseconds):
        self.result_move_anim = {"progress": 0.0}
        self._animate_state(self.result_move_anim, milliseconds)
        self.result_move_anim = None


class MergeSortVisualizer(BaseVisualizer):
    def __init__(self, title="Merge Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.stack = []
        self.active_range = None
        self.compare_pair = None
        self.merge_range = None
        self.merged = []
        self.merged_from = {}
        self.copy_range = None
        self.insertion_range = None
        self.shift_pair = None
        self.insert_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.insertion_sorted_until = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.push_animation = None
        self.copy_animation = None
        self.copy_back_animation = None
        self.anim_progress = 0.0
        self.merge_only = False
        self.exhausted_side = None
        self.compare_count = 0
        self.copy_count = 0

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.stack = []
        self.active_range = None
        self.compare_pair = None
        self.merge_range = None
        self.merged = []
        self.merged_from = {}
        self.copy_range = None
        self.insertion_range = None
        self.shift_pair = None
        self.insert_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.insertion_sorted_until = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.push_animation = None
        self.copy_animation = None
        self.copy_back_animation = None
        self.anim_progress = 0.0
        self.merge_only = False
        self.exhausted_side = None
        self.compare_count = 0
        self.copy_count = 0
        self.msg_phase("병합 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("배열을 반으로 나누고, 정렬된 두 부분 배열을 병합한다.")
        self._update_stats()
        self.wait(700)

    def push(self, left, right):
        self.stack.append({"left": left, "right": right, "mid": None})
        self.active_range = (left, right)
        self.compare_pair = None
        self.copy_range = None
        self.insertion_range = None
        self.push_animation = len(self.stack) - 1
        self.msg_action(f"부분 배열 #{left}..#{right} 을 정렬한다.")
        self.msg_detail("크기가 1이 될 때까지 반으로 나누어 생각한다.")
        self._update_stats()
        self._animate(550)
        self.push_animation = None

    def split(self, left, mid, right):
        if self.stack:
            self.stack[-1]["mid"] = mid
        self.active_range = (left, right)
        self.msg_action(f"#{left}..#{right} 을 #{left}..#{mid} 와 #{mid + 1}..#{right} 로 나눈다.")
        self.msg_detail("왼쪽 부분 배열과 오른쪽 부분 배열을 각각 정렬한다.")
        self._update_stats()
        self.wait(650)
        self.section_end()

    def prepare_merge(self, left, mid, right):
        self.stack = [{"left": left, "right": right, "mid": mid}]
        self.merge_only = True
        self.active_range = (left, right)
        self.compare_pair = None
        self.copy_range = None
        self.insertion_range = None
        self.msg_action(f"앞 절반 #{left}..#{mid}, 뒤 절반 #{mid + 1}..#{right} 은 이미 정렬되어 있다.")
        self.msg_detail("두 정렬된 부분 배열을 하나의 정렬된 배열로 합친다.")
        self._update_stats()
        self.wait(700)

    def single(self, index):
        self.active_range = (index, index)
        self.msg_action(f"#{index} 하나만 있는 부분 배열이다.")
        self.msg_detail("원소가 하나이면 이미 정렬되어 있다.")
        self._update_stats()
        self.wait(450)

    def pop(self):
        if self.stack:
            self.stack.pop()
        self.active_range = None if not self.stack else (self.stack[-1]["left"], self.stack[-1]["right"])

    def start_merge(self, left, mid, right):
        self.merge_range = (left, mid, right)
        self.active_range = (left, right)
        self.compare_pair = None
        self.copy_range = None
        self.exhausted_side = None
        self.merged = []
        self.merged_from = {}
        self.msg_action(f"#{left}..#{mid} 와 #{mid + 1}..#{right} 을 병합한다.")
        self.msg_detail("두 부분 배열의 앞쪽 값 중 작은 값을 임시 배열에 복사한다.")
        self._update_stats()
        self.wait(650)

    def compare(self, left, right):
        self.compare_pair = (left, right)
        self.compare_count += 1
        self.msg_action(f"#{left}({self.array[left]}) 과 #{right}({self.array[right]}) 을 비교한다.")
        if self.array[left] <= self.array[right]:
            self.msg_detail(f"{self.array[left]} 이 작거나 같으므로 왼쪽 값을 먼저 복사한다.")
        else:
            self.msg_detail(f"{self.array[right]} 이 더 작으므로 오른쪽 값을 먼저 복사한다.")
        self._update_stats()
        self.wait(750)

    def add_to_merged(self, source_index, merged):
        next_merged = list(merged)
        dest_offset = len(next_merged) - 1
        self.copy_animation = (source_index, dest_offset, next_merged[dest_offset])
        self.copy_count += 1
        self.msg_action(f"#{source_index}({self.array[source_index]}) 을 임시 배열에 복사한다.")
        self.msg_detail("원래 배열의 값은 그대로 두고, 정렬 결과를 임시 배열에 차례로 만든다.")
        self._update_stats()
        self._animate(650)
        self.merged = next_merged
        self.merged_from[dest_offset] = source_index
        self.copy_animation = None

    def exhausted(self, side):
        self.exhausted_side = side
        self.compare_pair = None
        if side == "left":
            self.msg_action("왼쪽 부분 배열이 모두 소진되었다.")
            self.msg_detail("이제 오른쪽에 남은 값들은 비교 없이 차례로 복사한다.")
        else:
            self.msg_action("오른쪽 부분 배열이 모두 소진되었다.")
            self.msg_detail("이제 왼쪽에 남은 값들은 비교 없이 차례로 복사한다.")
        self._update_stats()
        self.wait(700)

    def end_merge(self):
        self.compare_pair = None
        self.msg_action("임시 배열에 병합 결과가 완성되었다.")
        self.msg_detail("이제 임시 배열의 값을 원래 배열 구간으로 복사한다.")
        self._update_stats()
        self.wait(650)
        self.section_end()

    def copy_back(self, left, right, merged):
        self.copy_range = (left, right)
        self.copy_back_animation = (left, right, list(merged))
        self.msg_action(f"임시 배열을 원래 배열 #{left}..#{right} 에 복사한다.")
        self.msg_detail(f"부분 배열 #{left}..#{right} 의 정렬이 끝났다.")
        self._update_stats()
        self._animate(800)
        self.array[left : right + 1] = list(merged)
        self.merge_range = None
        self.merged = []
        self.merged_from = {}
        self.exhausted_side = None
        self.copy_range = None
        self.copy_back_animation = None
        if self.merge_only:
            self.stack = []
            self.merge_only = False
        self.section_end()

    def start_insertion(self, left, right):
        self.insertion_range = (left, right)
        self.insertion_sorted_until = left
        self.active_range = (left, right)
        self.compare_pair = None
        self.merge_range = None
        self.merged = []
        self.msg_action(f"작은 부분 배열 #{left}..#{right} 은 삽입 정렬로 처리한다.")
        self.msg_detail("작은 구간에서는 재귀를 더 나누지 않고 직접 정렬한다.")
        self._update_stats()
        self.wait(650)
        self.section_end()

    def mark_end(self, index, pick=False):
        self.compare_pair = None
        self.shift_pair = None
        self.insertion_sorted_until = index
        if pick:
            self.picked_from = index
            self.picked_value = self.array[index]
            self.hole_index = index
            self.pick_progress = 0.0
            self.msg_action(f"#{index}({self.picked_value}) 을 삽입할 값으로 빼 둔다.")
            self.msg_detail("왼쪽의 정렬된 구간에서 들어갈 위치를 찾는다.")
        else:
            self.pick_progress = 1.0
            self.msg_action(f"#{index}까지를 정렬된 구간으로 본다.")
            self.msg_detail("새 원소를 왼쪽 정렬 구간 안으로 이동시킨다.")
        self._update_stats()
        if pick:
            self._animate_insertion_pick(650)
        else:
            self.wait(650)

    def shift(self, left, right, pick=False):
        source = self.picked_from if pick and self.picked_from is not None else left
        self.shift_pair = (source, right)
        self.shift_pick = pick
        self.shift_progress = 0.0
        self.copy_count += 1
        if pick:
            self.msg_action(f"빼 둔 값 {self.picked_value} 을 #{right} 위치에 삽입한다.")
            self.msg_detail("빈 자리에 값을 넣으면 작은 부분 배열의 정렬이 회복된다.")
        else:
            self.msg_action(f"#{left}({self.array[left]}) 을 #{right} 위치로 한 칸 민다.")
            self.msg_detail("삽입할 값이 들어갈 빈 자리를 왼쪽으로 옮긴다.")
        self._update_stats()
        self._animate_insertion_shift(700)
        if pick:
            self.array[right] = self.picked_value
            self.picked_from = None
            self.picked_value = None
            self.hole_index = None
            self.pick_progress = 1.0
        else:
            self.array[right] = self.array[left]
            self.hole_index = left
        self.shift_pair = None
        self.shift_pick = False
        self.shift_progress = 0.0

    def insert(self, index, value):
        self.insert_index = index
        self.copy_count += 1
        self.msg_action(f"삽입할 값 {value} 을 #{index} 위치에 넣는다.")
        self.msg_detail("작은 부분 배열의 정렬 상태를 회복한다.")
        self._update_stats()
        self.wait(650)
        self.array[index] = value
        self.insert_index = None

    def finish_insertion(self, left, right):
        self.insertion_range = (left, right)
        self.msg_action(f"부분 배열 #{left}..#{right} 의 삽입 정렬이 끝났다.")
        self.msg_detail("정렬된 결과를 분리되기 전 부분 배열 자리로 복사한다.")
        self._update_stats()
        self.copy_range = (left, right)
        self.copy_back_animation = (left, right, self.array[left : right + 1])
        self._animate(800)
        self.copy_range = None
        self.copy_back_animation = None
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.section_end()

    def finish(self):
        self.active_range = None
        self.compare_pair = None
        self.merge_range = None
        self.insertion_range = None
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("모든 부분 배열을 병합하여 전체 배열을 정렬했다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("반으로 나눈 부분 배열을 정렬한 뒤, 임시 배열을 이용해 다시 합친다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_stack()
        self._draw_merge_guides()
        self._draw_merged()
        self._draw_copy_animation()
        self._draw_legend()

    def _draw_array(self):
        metrics = self._array_metrics()
        if metrics is None:
            return
        start_x, top, box_width, box_height, gap = metrics
        self.text("array", 78, top + 24, 22, colors.TEXT_MUTED, True)
        for index, value in enumerate(self.array):
            x = start_x + index * (box_width + gap)
            y = top
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT
            if self.active_range is not None and self.active_range[0] <= index <= self.active_range[1]:
                fill = (30, 47, 59)
                border = colors.BLUE
            if self.insertion_range is not None and self.insertion_range[0] <= index <= self.insertion_range[1]:
                fill = (41, 50, 35)
                border = colors.GREEN
            if self.hole_index == index:
                fill = (36, 39, 45)
                border = colors.TEXT_MUTED
                text_color = colors.TEXT_MUTED
            if self.copy_range is not None and self.copy_range[0] <= index <= self.copy_range[1]:
                fill = (35, 72, 52)
                border = colors.GREEN
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.shift_pair is not None and index in self.shift_pair:
                fill = (62, 66, 107)
                border = colors.BLUE
            if self.insert_index == index:
                fill = (65, 54, 29)
                border = colors.YELLOW
            self.rect(x, y, box_width, box_height, fill, border, 6)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, max(13, min(28, box_width * 0.55)), text_color, True)
            self.centered_text(f"#{index}", x + box_width / 2, top + box_height + 22, max(10, min(18, box_width * 0.38)), colors.TEXT_MUTED)

    def _draw_stack(self):
        metrics = self._array_metrics()
        if metrics is None:
            return
        start_x, _, box_width, _, gap = metrics
        row_height = 36
        for level, frame in enumerate(self.stack[:7]):
            top = self._stack_top(level)
            if self.push_animation == level:
                source_top = self._array_metrics()[1] if level == 0 else self._stack_top(level - 1)
                top = source_top + (top - source_top) * self.anim_progress
            left = frame["left"]
            right = frame["right"]
            mid = frame["mid"]
            label = "merge" if self.merge_only else f"depth {level + 1}"
            self.text(label, 78, top + 8, 18, colors.TEXT_MUTED)
            draw_order = list(range(left, right + 1))
            if level == len(self.stack) - 1 and self.shift_pair is not None and not self.shift_pick:
                source, _ = self.shift_pair
                draw_order = [index for index in draw_order if index != source] + [source]
            for index in draw_order:
                x = start_x + index * (box_width + gap)
                y = top
                fill = (28, 36, 45)
                border = colors.BORDER
                text_color = colors.TEXT
                if level == len(self.stack) - 1 and self.shift_pair is not None and not self.shift_pick and index == self.shift_pair[0]:
                    self.rect(x, top, box_width, row_height, (21, 25, 31), (61, 69, 82), 4)
                    self.centered_text(self.array[index], x + box_width / 2, top + row_height / 2, max(10, min(18, box_width * 0.42)), colors.TEXT_MUTED)
                    ox, oy = self._insertion_shift_offset(index, box_width + gap, row_height)
                    x += ox
                    y += oy
                if mid is not None:
                    if index <= mid:
                        fill = (42, 43, 29)
                        border = colors.YELLOW
                    else:
                        fill = (26, 45, 50)
                        border = colors.BLUE
                if (
                    self.insertion_range is not None
                    and level == len(self.stack) - 1
                    and self.insertion_range[0] <= index <= self.insertion_sorted_until
                ):
                    fill = (35, 72, 52)
                    border = colors.GREEN
                if self._is_exhausted_index(index):
                    fill = (28, 31, 36)
                    border = colors.TEXT_MUTED
                if self.compare_pair is not None and index in self.compare_pair and level == len(self.stack) - 1:
                    fill = (82, 55, 30)
                    border = colors.ORANGE
                if self.copy_range is not None and left <= index <= right and level == len(self.stack) - 1:
                    fill = (35, 72, 52)
                    border = colors.GREEN
                if self.hole_index == index and level == len(self.stack) - 1:
                    fill = (36, 39, 45)
                    border = colors.TEXT_MUTED
                    text_color = colors.TEXT_MUTED
                self.rect(x, y, box_width, row_height, fill, border, 4)
                self.centered_text(self.array[index], x + box_width / 2, y + row_height / 2, max(10, min(18, box_width * 0.42)), text_color)

        if self.picked_from is not None and self.picked_value is not None:
            x, y, box_width, row_height = self._stack_rect(self.picked_from)
            if self.shift_pick and self.shift_pair is not None:
                _, target = self.shift_pair
                target_x, target_y, _, _ = self._stack_rect(target)
                x += (target_x - x) * self.shift_progress
                y = y - row_height * 1.25 * (1 - self.shift_progress) + (target_y - y) * self.shift_progress
            else:
                y -= row_height * 1.25 * self.pick_progress
            self.rect(x, y, box_width, row_height, (89, 39, 77), colors.RED, 4)
            self.centered_text(self.picked_value, x + box_width / 2, y + row_height / 2, max(10, min(18, box_width * 0.42)), colors.TEXT, True)
        self._draw_insertion_sorted_region()

    def _draw_insertion_sorted_region(self):
        if self.insertion_range is None or self.insertion_sorted_until is None or not self.stack:
            return
        left, _ = self.insertion_range
        right = min(self.insertion_sorted_until, len(self.array) - 1)
        if right < left:
            return
        start_x, _, box_width, _, gap = self._array_metrics()
        top = self._stack_top(len(self.stack) - 1)
        row_height = 36
        x = start_x + left * (box_width + gap) - 6
        width = (right - left + 1) * box_width + (right - left) * gap + 12
        y = top - 6
        height = row_height + 12
        rect = self.view.rect(x, y, width, height)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(8),
        )
        self.centered_text("정렬된 구간", x + width / 2, top + row_height + 28, 18, (88, 126, 101), True)

    def _draw_merged(self):
        if self.merge_range is None and not self.merged:
            return
        metrics = self._array_metrics()
        if metrics is None:
            return
        start_x, _, box_width, box_height, gap = metrics
        left, _, _ = self.merge_range if self.merge_range else (0, 0, 0)
        top = self._merged_top()
        self.text("merged", 78, top + 24, 22, colors.TEXT_MUTED, True)
        for offset, value in enumerate(self.merged):
            if self.copy_back_animation is not None:
                continue
            x = start_x + (left + offset) * (box_width + gap)
            source = self.merged_from.get(offset)
            fill = (37, 43, 60)
            border = colors.BLUE
            if source is not None and self.merge_range is not None:
                _, mid, _ = self.merge_range
                if source <= mid:
                    fill = (61, 50, 34)
                    border = colors.YELLOW
                else:
                    fill = (31, 58, 62)
                    border = colors.BLUE
            self.rect(x, top, box_width, box_height, fill, border, 6)
            self.centered_text(value, x + box_width / 2, top + box_height / 2, max(13, min(28, box_width * 0.55)), colors.TEXT, True)

    def _draw_copy_animation(self):
        if self.copy_back_animation is not None:
            self._draw_copy_back_animation()
        if self.copy_animation is None or self.merge_range is None:
            return
        source_index, dest_offset, value = self.copy_animation
        left, mid, _ = self.merge_range
        sx, sy, box_width, row_height = self._stack_rect(source_index)
        dx, dy, _, _ = self._merged_rect(left + dest_offset)
        x = sx + (dx - sx) * self.anim_progress
        y = sy + (dy - sy) * self.anim_progress
        if source_index <= mid:
            fill = (61, 50, 34)
            border = colors.YELLOW
        else:
            fill = (31, 58, 62)
            border = colors.BLUE
        self.rect(x, y, box_width, row_height, fill, border, 6)
        self.centered_text(value, x + box_width / 2, y + row_height / 2, max(13, min(28, box_width * 0.55)), colors.TEXT, True)

    def _draw_merge_guides(self):
        if self.merge_range is None or not self.stack:
            return
        left, mid, right = self.merge_range
        self._dashed_range_rect(left, mid, colors.YELLOW)
        self._dashed_range_rect(mid + 1, right, colors.BLUE)
        self._dashed_separator(mid)
        if self.exhausted_side is not None:
            self._draw_exhausted_label()

    def _draw_copy_back_animation(self):
        left, right, merged = self.copy_back_animation
        for offset, value in enumerate(merged):
            if self.insertion_range is not None:
                source_x, source_y, box_width, box_height = self._stack_rect(left + offset)
            else:
                source_x, source_y, box_width, box_height = self._merged_rect(left + offset)
            target_x, target_y, _, target_height = self._copy_back_target_rect(left + offset)
            x = source_x + (target_x - source_x) * self.anim_progress
            y = source_y + (target_y - source_y) * self.anim_progress
            height = box_height + (target_height - box_height) * self.anim_progress
            self.rect(x, y, box_width, height, (35, 72, 52), colors.GREEN, 6)
            self.centered_text(value, x + box_width / 2, y + height / 2, max(13, min(28, box_width * 0.55)), colors.TEXT, True)

    def _draw_legend(self):
        self.rect(1010, 72, 30, 20, (42, 43, 29), colors.YELLOW, 4)
        self.text("왼쪽 부분 배열", 1052, 68, 21, colors.TEXT_MUTED)
        self.rect(1010, 108, 30, 20, (26, 45, 50), colors.BLUE, 4)
        self.text("오른쪽 부분 배열", 1052, 104, 21, colors.TEXT_MUTED)
        self.rect(1250, 72, 30, 20, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교", 1292, 68, 21, colors.TEXT_MUTED)
        self.rect(1250, 108, 30, 20, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬 완료 구간", 1292, 104, 21, colors.TEXT_MUTED)

    def _array_metrics(self):
        if not self.array:
            return None
        count = len(self.array)
        gap = max(4, min(12, 170 / max(1, count)))
        max_width = 1360
        box_width = min(72, (max_width - gap * (count - 1)) / count)
        box_height = 58
        start_x = 150 + (max_width - (box_width * count + gap * (count - 1))) / 2
        return start_x, 170, box_width, box_height, gap

    def _dashed_range_rect(self, left, right, color):
        if left > right:
            return
        start_x, _, box_width, _, gap = self._array_metrics()
        level = max(0, len(self.stack) - 1)
        top = self._stack_top(level)
        x = start_x + left * (box_width + gap) - 5
        y = top - 5
        width = (right - left + 1) * box_width + (right - left) * gap + 10
        height = 46
        self._dashed_line(x, y, x + width, y, color)
        self._dashed_line(x, y + height, x + width, y + height, color)
        self._dashed_line(x, y, x, y + height, color)
        self._dashed_line(x + width, y, x + width, y + height, color)

    def _dashed_separator(self, mid):
        start_x, _, box_width, _, gap = self._array_metrics()
        level = max(0, len(self.stack) - 1)
        x = start_x + (mid + 1) * (box_width + gap) - gap / 2
        y1 = self._stack_top(level) - 8
        y2 = self._stack_top(level) + 44
        self._dashed_line(x, y1, x, y2, colors.TEXT_MUTED, dash=5, space=5)

    def _draw_exhausted_label(self):
        left, mid, right = self.merge_range
        if self.exhausted_side == "left":
            first, last = left, mid
            label = "왼쪽 소진"
        else:
            first, last = mid + 1, right
            label = "오른쪽 소진"
        start_x, _, box_width, _, gap = self._array_metrics()
        x1 = start_x + first * (box_width + gap)
        x2 = start_x + last * (box_width + gap) + box_width
        self.centered_text(label, (x1 + x2) / 2, self._stack_top(len(self.stack) - 1) - 26, 20, colors.TEXT_MUTED, True)

    def _is_exhausted_index(self, index):
        if self.exhausted_side is None or self.merge_range is None:
            return False
        left, mid, right = self.merge_range
        if self.exhausted_side == "left":
            return left <= index <= mid
        return mid < index <= right

    def _dashed_line(self, x1, y1, x2, y2, color, dash=8, space=6):
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux = dx / length
        uy = dy / length
        distance = 0
        while distance < length:
            start = distance
            end = min(distance + dash, length)
            pygame.draw.line(
                self.screen,
                color,
                self.view.point(x1 + ux * start, y1 + uy * start),
                self.view.point(x1 + ux * end, y1 + uy * end),
                self.view.length(1),
            )
            distance += dash + space

    def _stack_top(self, level):
        return 242 + level * 56

    def _merged_top(self):
        level = max(0, len(self.stack) - 1)
        return self._stack_top(level) + 40

    def _stack_rect(self, index):
        start_x, _, box_width, _, gap = self._array_metrics()
        level = max(0, len(self.stack) - 1)
        x = start_x + index * (box_width + gap)
        return x, self._stack_top(level), box_width, 36

    def _copy_back_target_rect(self, index):
        start_x, array_top, box_width, box_height, gap = self._array_metrics()
        x = start_x + index * (box_width + gap)
        if len(self.stack) <= 1:
            return x, array_top, box_width, box_height
        level = len(self.stack) - 2
        return x, self._stack_top(level), box_width, 36

    def _merged_rect(self, index):
        start_x, _, box_width, _, gap = self._array_metrics()
        x = start_x + index * (box_width + gap)
        return x, self._merged_top(), box_width, 58

    def _insertion_shift_offset(self, index, step_width, row_height):
        if self.shift_pair is None:
            return 0, 0
        source, target = self.shift_pair
        if index != source:
            return 0, 0
        return (target - source) * step_width * self.shift_progress, 0

    def _animate_insertion_pick(self, milliseconds):
        self._animate_progress(milliseconds, "pick_progress")
        self.wait(200)

    def _animate_insertion_shift(self, milliseconds):
        self._animate_progress(milliseconds, "shift_progress")

    def _animate_progress(self, milliseconds, attr):
        if self.is_max_speed() or self.running_to_section:
            setattr(self, attr, 1.0)
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                setattr(self, attr, 1.0)
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            setattr(self, attr, min(1.0, active_elapsed / duration))
            self.draw()
            if getattr(self, attr) >= 1.0:
                break
            self.clock.tick(60)

    def _animate(self, milliseconds):
        if self.is_max_speed() or self.running_to_section:
            self.anim_progress = 1.0
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.anim_progress = 1.0
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            self.anim_progress = min(1.0, active_elapsed / duration)
            self.draw()
            if self.anim_progress >= 1.0:
                break
            self.clock.tick(60)
        self.anim_progress = 0.0

    def _update_stats(self):
        self.msg_stats(f"비교 {self.compare_count}회\n복사 {self.copy_count}회")


class MergeBattleVisualizer(MergeSortVisualizer):
    def __init__(self, title="Merge Battle", **kwargs):
        super().__init__(title, **kwargs)
        self.battle_pair = None
        self.battle_winner = None
        self.battle_phase = None

    def setup(self, data):
        super().setup(data)
        self.msg_phase("병합")
        self.msg_detail("양쪽 부분 배열에서 하나씩 비교하고, 작은 값부터 결과 줄에 선다.")

    def compare(self, left, right):
        self.compare_pair = (left, right)
        self.battle_pair = (left, right)
        self.battle_winner = None
        self.battle_phase = "meet"
        self.compare_count += 1
        self.msg_action(f"#{left}({self.array[left]}) 와 #{right}({self.array[right]}) 이 대결한다.")
        if self.array[left] <= self.array[right]:
            self.msg_detail(f"{self.array[left]} 이 더 작으므로 먼저 결과 줄에 선다.")
        else:
            self.msg_detail(f"{self.array[right]} 이 더 작으므로 먼저 결과 줄에 선다.")
        self._update_stats()
        self._animate(650)

    def add_to_merged(self, source_index, merged):
        next_merged = list(merged)
        dest_offset = len(next_merged) - 1
        self.battle_winner = source_index
        self.battle_phase = "settle"
        self.copy_animation = (source_index, dest_offset, next_merged[dest_offset])
        self.copy_count += 1
        self.msg_action(f"#{source_index}({self.array[source_index]}) 이 결과 줄로 이동한다.")
        self.msg_detail("상대 선수는 자기 자리로 돌아가고, 다음 선수가 대결을 준비한다.")
        self._update_stats()
        self._animate(700)
        self.merged = next_merged
        self.merged_from[dest_offset] = source_index
        self.copy_animation = None
        self.battle_pair = None
        self.battle_winner = None
        self.battle_phase = None

    def exhausted(self, side):
        self.battle_pair = None
        self.battle_winner = None
        self.battle_phase = None
        super().exhausted(side)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("양쪽 부분 배열에서 작은 값부터 결과 줄에 세운다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_stack()
        self._draw_merge_guides()
        self._draw_merged()
        self._draw_copy_animation()
        self._draw_legend()

    def _draw_stack(self):
        metrics = self._array_metrics()
        if metrics is None:
            return
        start_x, _, box_width, _, gap = metrics
        row_height = 36
        for level, frame in enumerate(self.stack[:7]):
            top = self._stack_top(level)
            left = frame["left"]
            right = frame["right"]
            mid = frame["mid"]
            label = "merge" if self.merge_only else f"depth {level + 1}"
            self.text(label, 78, top + 8, 18, colors.TEXT_MUTED)
            draw_order = list(range(left, right + 1))
            if level == len(self.stack) - 1 and self.battle_pair is not None and self.copy_animation is None:
                battle = [index for index in self.battle_pair if left <= index <= right]
                draw_order = [index for index in draw_order if index not in battle] + battle
            for index in draw_order:
                if level == len(self.stack) - 1 and self.battle_pair is not None and index in self.battle_pair and self.copy_animation is None:
                    x, y, width, height = self._battle_rect(index)
                else:
                    x = start_x + index * (box_width + gap)
                    y = top
                    width = box_width
                    height = row_height
                fill = (28, 36, 45)
                border = colors.BORDER
                if mid is not None:
                    if index <= mid:
                        fill = (42, 43, 29)
                        border = colors.YELLOW
                    else:
                        fill = (26, 45, 50)
                        border = colors.BLUE
                if self._is_exhausted_index(index):
                    fill = (28, 31, 36)
                    border = colors.TEXT_MUTED
                if self.compare_pair is not None and index in self.compare_pair and level == len(self.stack) - 1:
                    fill = (82, 55, 30)
                    border = colors.ORANGE
                if self.copy_range is not None and left <= index <= right and level == len(self.stack) - 1:
                    fill = (35, 72, 52)
                    border = colors.GREEN
                self.rect(x, y, width, height, fill, border, 4)
                self.centered_text(self.array[index], x + width / 2, y + height / 2, max(10, min(18, box_width * 0.42)), colors.TEXT)

    def _draw_copy_animation(self):
        if self.copy_back_animation is not None:
            self._draw_copy_back_animation()
        if self.copy_animation is None or self.merge_range is None:
            return
        source_index, dest_offset, value = self.copy_animation
        left, mid, _ = self.merge_range
        dx, dy, box_width, dest_height = self._merged_rect(left + dest_offset)
        if self.battle_pair is not None and source_index in self.battle_pair:
            sx, sy, _, height = self._battle_meet_rect(source_index)
        else:
            sx, sy, _, height = self._stack_rect(source_index)
        x = sx + (dx - sx) * self.anim_progress
        y = sy + (dy - sy) * self.anim_progress
        height = height + (dest_height - height) * self.anim_progress
        if source_index <= mid:
            fill = (61, 50, 34)
            border = colors.YELLOW
        else:
            fill = (31, 58, 62)
            border = colors.BLUE
        self.rect(x, y, box_width, height, fill, border, 6)
        self.centered_text(value, x + box_width / 2, y + height / 2, max(13, min(28, box_width * 0.55)), colors.TEXT, True)
        self._draw_returning_loser(source_index)

    def _draw_returning_loser(self, winner):
        if self.battle_pair is None:
            return
        loser = self.battle_pair[1] if winner == self.battle_pair[0] else self.battle_pair[0]
        value = self.array[loser]
        sx, sy, box_width, height = self._battle_meet_rect(loser)
        dx, dy, _, _ = super()._stack_rect(loser)
        x = sx + (dx - sx) * self.anim_progress
        y = sy + (dy - sy) * self.anim_progress
        fill = (42, 43, 29) if self._is_left_side(loser) else (26, 45, 50)
        border = colors.YELLOW if self._is_left_side(loser) else colors.BLUE
        self.rect(x, y, box_width, height, fill, border, 6)
        self.centered_text(value, x + box_width / 2, y + height / 2, max(13, min(28, box_width * 0.55)), colors.TEXT, True)

    def _stack_rect(self, index):
        if self.battle_pair is not None and index in self.battle_pair and self.copy_animation is None:
            return self._battle_rect(index)
        return super()._stack_rect(index)

    def _battle_rect(self, index):
        if self.battle_phase == "meet":
            return self._battle_meet_rect(index, self.anim_progress)
        if self.battle_phase == "settle":
            return self._battle_meet_rect(index, 1.0)
        return super()._stack_rect(index)

    def _battle_meet_rect(self, index, progress=1.0):
        sx, sy, box_width, height = super()._stack_rect(index)
        if self.battle_pair is None:
            return sx, sy, box_width, height
        left_index, right_index = self.battle_pair
        lx, _, _, _ = super()._stack_rect(left_index)
        rx, _, _, _ = super()._stack_rect(right_index)
        center = (lx + rx + box_width) / 2
        gap = box_width * 0.58
        if index == left_index:
            x = center - gap - box_width / 2
        else:
            x = center + gap - box_width / 2
        x = sx + (x - sx) * progress
        y = sy + height * 2.35 * progress
        return x, y, box_width, height

    def _is_left_side(self, index):
        if self.merge_range is None:
            return True
        _, mid, _ = self.merge_range
        return index <= mid


class QuickSortVisualizer(BaseVisualizer):
    def __init__(self, title="Quick Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.array = []
        self.stack = []
        self.active_range = None
        self.pivot_index = None
        self.pivot_value = None
        self.p_index = None
        self.q_index = None
        self.left_done = None
        self.right_done = None
        self.compare_index = None
        self.swap_pair = None
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.scan_progress = 0.0
        self.swap_progress = 0.0
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.fine_sections = False
        self.fixed = set()
        self.compare_count = 0
        self.swap_count = 0

    def set_fine_sections(self, enabled=True):
        self.fine_sections = enabled
        return self

    def setup(self, data):
        self.set_data_info(data)
        self.array = list(data.array)
        self.stack = []
        self.active_range = None
        self.pivot_index = None
        self.pivot_value = None
        self.p_index = None
        self.q_index = None
        self.left_done = None
        self.right_done = None
        self.compare_index = None
        self.swap_pair = None
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.scan_progress = 0.0
        self.swap_progress = 0.0
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.fixed = set()
        self.compare_count = 0
        self.swap_count = 0
        self.msg_phase("퀵 정렬")
        self.msg_action("배열을 준비한다.")
        self.msg_detail("pivot을 기준으로 작은 값은 왼쪽, 큰 값은 오른쪽으로 나눈다.")
        self._update_stats()
        self.wait(700)

    def push(self, left, right):
        self.stack.append({"left": left, "right": right, "pivot": None})
        self.active_range = (left, right)
        self.pivot_index = None
        self.pivot_value = None
        self.p_index = None
        self.q_index = None
        self.left_done = left
        self.right_done = right
        self.compare_index = None
        self.swap_pair = None
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.scan_progress = 0.0
        self.stack_anim_level = len(self.stack) - 1
        self.stack_anim_kind = "push"
        self.stack_anim_progress = 0.0
        self.msg_action(f"부분 배열 #{left}..#{right} 을 quick sort 한다.")
        self.msg_detail("이 구간에서 pivot을 하나 정해 partition을 수행한다.")
        self._update_stats()
        self._animate_progress(500, "stack_anim_progress")
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.wait(150)

    def pop(self):
        if self.stack:
            self.stack_anim_level = len(self.stack) - 1
            self.stack_anim_kind = "pop"
            self.stack_anim_progress = 0.0
            self._animate_progress(380, "stack_anim_progress")
        if self.stack:
            self.stack.pop()
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.active_range = None if not self.stack else (self.stack[-1]["left"], self.stack[-1]["right"])

    def set_pivot(self, index):
        self.pivot_index = index
        self.pivot_value = self.array[index]
        if self.stack:
            self.stack[-1]["pivot"] = index
        self.compare_index = None
        self.swap_pair = None
        self.msg_action(f"#{index}({self.pivot_value}) 을 pivot으로 정한다.")
        self.msg_detail("pivot보다 작은 값은 왼쪽으로, 큰 값은 오른쪽으로 보낸다.")
        self._update_stats()
        self.wait(700)
        self.section_end()

    def move_pivot_to_left(self, pivot_index, left):
        if pivot_index == left:
            self.msg_action(f"pivot이 이미 맨 왼쪽 #{left} 위치에 있다.")
            self.msg_detail("partition을 시작한다.")
            self._update_stats()
            self.wait(500)
            return
        self.swap(pivot_index, left, pivot=True)

    def set_p(self, index):
        self.p_index = index
        self.compare_index = None

    def set_q(self, index):
        self.q_index = index
        self.compare_index = None

    def compare_with_pivot(self, index):
        self.compare_index = index
        self.scan_index = index
        self.scan_direction = "p" if self.p_index == index else "q"
        if self.active_range is not None and self.scan_direction == "p":
            self.scan_start_index = max(self.active_range[0], index - 1)
        elif self.active_range is not None:
            self.scan_start_index = min(self.active_range[1], index + 1)
        else:
            self.scan_start_index = index
        self.scan_progress = 0.0
        self.compare_count += 1
        found_by_p = self.scan_direction == "p" and self.array[index] > self.pivot_value
        found_by_q = self.scan_direction == "q" and self.array[index] <= self.pivot_value
        if found_by_p:
            self.msg_action(f"p가 #{index}({self.array[index]}) 에서 멈춘다.")
            self.msg_detail(f"pivot {self.pivot_value} 보다 큰 값을 찾았다.")
        elif found_by_q:
            self.msg_action(f"q가 #{index}({self.array[index]}) 에서 멈춘다.")
            self.msg_detail(f"pivot {self.pivot_value} 보다 작거나 같은 값을 찾았다.")
        elif self.scan_direction == "p":
            self.msg_action("p가 오른쪽으로 이동하며 큰 값을 찾는다.")
            self.msg_detail(f"#{index}({self.array[index]}) 은 pivot 이하이므로 통과한다.")
        else:
            self.msg_action("q가 왼쪽으로 이동하며 작은 값을 찾는다.")
            self.msg_detail(f"#{index}({self.array[index]}) 은 pivot보다 크므로 통과한다.")
        self._update_stats()
        if found_by_p or found_by_q:
            self._animate_scan(650)
            if self.fine_sections:
                self.section_end()
        else:
            self._animate_scan(150)

    def compare_for_insertion(self, left, value):
        self.compare_index = left
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.compare_count += 1
        self.msg_action(f"#{left}({self.array[left]}) 과 삽입할 값 {value} 을 비교한다.")
        if self.array[left] > value:
            self.msg_detail("왼쪽 값이 더 크므로 오른쪽으로 이동시킨다.")
        else:
            self.msg_detail("왼쪽 값이 더 작거나 같으므로 이 자리 뒤에 삽입한다.")
        self._update_stats()
        self.wait(650)

    def accept_left(self, index):
        self.left_done = index
        self.compare_index = None
        self.msg_action("p가 오른쪽으로 이동하며 큰 값을 찾는다.")
        self.msg_detail(f"#{index}까지는 pivot 이하로 분류되었다.")
        self._update_stats()
        self.wait(120)

    def accept_right(self, index):
        self.right_done = index
        self.compare_index = None
        self.msg_action("q가 왼쪽으로 이동하며 작은 값을 찾는다.")
        self.msg_detail(f"#{index}부터는 pivot보다 큰 값으로 분류되었다.")
        self._update_stats()
        self.wait(120)

    def swap(self, left, right, pivot=False):
        if left == right:
            return
        self.swap_pair = (left, right)
        self.swap_progress = 0.0
        self.swap_count += 1
        if pivot:
            self.msg_action(f"pivot을 #{right} 위치로 옮긴다.")
            self.msg_detail("pivot의 최종 위치를 확정하기 위해 교환한다.")
        else:
            self.msg_action(f"#{left} 과 #{right} 의 값을 교환한다.")
            self.msg_detail("잘못된 쪽에 있던 두 값을 서로 바꾼다.")
        self._update_stats()
        self._animate_swap(850)
        self.array[left], self.array[right] = self.array[right], self.array[left]
        if self.pivot_index == left:
            self.pivot_index = right
        elif self.pivot_index == right:
            self.pivot_index = left
        self.swap_pair = None
        self.swap_progress = 0.0
        self.draw()
        self.wait(250)
        if self.fine_sections:
            self.section_end()

    def cross(self, p, q):
        self.p_index = p
        self.q_index = q
        self.msg_action(f"p={p}, q={q} 로 엇갈렸다.")
        self.msg_detail("더 이상 교환할 값이 없으므로 pivot의 자리를 확정한다.")
        self._update_stats()
        self.wait(700)

    def fix(self, index):
        self.fixed.add(index)
        self.pivot_index = index
        self.compare_index = None
        self.swap_pair = None
        if self.stack:
            self.stack[-1]["pivot"] = index
        self.msg_action(f"pivot #{index}({self.array[index]}) 의 위치가 확정되었다.")
        self.msg_detail("왼쪽은 pivot보다 작고, 오른쪽은 pivot보다 크다.")
        self._update_stats()
        self.wait(800)
        self.section_end()

    def single(self, index):
        self.fixed.add(index)
        self.active_range = (index, index)
        self.msg_action(f"#{index} 하나만 있으므로 위치가 확정되었다.")
        self.msg_detail("원소가 하나인 부분 배열은 이미 정렬되어 있다.")
        self._update_stats()
        self.wait(450)

    def start_insertion(self, left, right):
        self.insertion_range = (left, right)
        self.insertion_sorted_until = left
        self.active_range = (left, right)
        self.p_index = None
        self.q_index = None
        self.pivot_index = None
        self.compare_index = None
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.msg_action(f"작은 부분 배열 #{left}..#{right} 은 삽입 정렬로 처리한다.")
        self.msg_detail("작은 구간에서는 quick sort를 더 진행하지 않는다.")
        self._update_stats()
        self.wait(650)
        self.section_end()

    def mark_end(self, index, pick=False):
        self.compare_index = None
        self.shift_pair = None
        self.shift_progress = 0.0
        self.insertion_sorted_until = index
        if pick:
            self.picked_index = index
            self.picked_from = index
            self.picked_value = self.array[index]
            self.hole_index = index
            self.pick_progress = 0.0
            self.msg_action(f"#{index}({self.array[index]}) 을 삽입할 값으로 뺀다.")
            self.msg_detail("왼쪽의 작은 정렬 구간에서 들어갈 위치를 찾는다.")
        self._update_stats()
        if pick:
            self._animate_insertion_pick(650)
        else:
            self.wait(550)

    def shift(self, left, right, pick=False):
        source = self.picked_from if pick and self.picked_from is not None else left
        self.shift_pair = (source, right)
        self.shift_pick = pick
        self.shift_progress = 0.0
        if pick:
            self.msg_action(f"빼 둔 값을 #{right} 위치에 삽입한다.")
            self.msg_detail("작은 부분 배열의 정렬 상태를 회복한다.")
        else:
            self.msg_action(f"#{left}({self.array[left]}) 을 #{right} 위치로 민다.")
            self.msg_detail("삽입할 값이 들어갈 빈 자리를 만든다.")
        self._update_stats()
        self._animate_insertion_shift(700)
        if pick:
            if self.picked_value is not None:
                self.array[right] = self.picked_value
            self.picked_index = None
            self.picked_from = None
            self.picked_value = None
            self.hole_index = None
            self.pick_progress = 1.0
        else:
            self.array[right] = self.array[left]
            self.hole_index = left
        self.shift_pair = None
        self.shift_pick = False
        self.shift_progress = 0.0
        self.draw()
        self.wait(150)

    def finish_insertion(self, left, right):
        self.insertion_range = (left, right)
        self.insertion_sorted_until = right
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.fixed.update(range(left, right + 1))
        self.msg_action(f"부분 배열 #{left}..#{right} 의 삽입 정렬이 끝났다.")
        self.msg_detail("작은 구간이 정렬되었다.")
        self._update_stats()
        self.wait(700)
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.section_end()

    def finish_partition(self, index):
        self.active_range = (0, len(self.array) - 1)
        self.pivot_index = index
        self.p_index = None
        self.q_index = None
        self.left_done = index - 1
        self.right_done = index + 1
        self.compare_index = None
        self.swap_pair = None
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.scan_progress = 0.0
        self.swap_progress = 0.0
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.fixed = {index}
        self.msg_phase("pivot 위치")
        self.msg_action(f"#{index} 번째의 {self.array[index]} 은 위치가 확정되었다.")
        self.msg_detail("왼쪽에는 이 값 이하, 오른쪽에는 이 값보다 큰 값이 모였다.")
        self._update_stats()
        self.wait(1200)

    def finish(self):
        self.active_range = None
        self.pivot_index = None
        self.compare_index = None
        self.swap_pair = None
        self.scan_start_index = None
        self.scan_index = None
        self.scan_direction = None
        self.scan_progress = 0.0
        self.swap_progress = 0.0
        self.stack_anim_level = None
        self.stack_anim_kind = None
        self.stack_anim_progress = 0.0
        self.insertion_range = None
        self.insertion_sorted_until = None
        self.picked_index = None
        self.picked_from = None
        self.picked_value = None
        self.hole_index = None
        self.shift_pair = None
        self.shift_pick = False
        self.pick_progress = 1.0
        self.shift_progress = 0.0
        self.fixed = set(range(len(self.array)))
        self.msg_phase("완료")
        self.msg_action("배열이 오름차순으로 정렬되었다.")
        self.msg_detail("모든 pivot의 위치가 확정되었다.")
        self._update_stats()
        self.wait(1200)

    def draw_content(self):
        self.text(self.title, 70, 55, 46, colors.TEXT, True)
        self.text("pivot을 기준으로 작은 값과 큰 값을 나누고, 각 부분 배열을 다시 정렬한다.", 72, 115, 26, colors.TEXT_MUTED)
        self._draw_array()
        self._draw_stack()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return
        count, start_x, top, box_width, box_height, gap = self._layout_metrics()
        value_size = max(13, min(30, box_width * 0.52))
        index_size = max(10, min(18, box_width * 0.34))
        swapping = set(self.swap_pair or ())
        draw_order = [index for index in range(count) if index not in swapping]
        draw_order += [index for index in range(count) if index in swapping]
        for index in draw_order:
            value = self.array[index]
            x = start_x + index * (box_width + gap)
            y = top
            if index in swapping:
                ox, oy = self._swap_offset(index, box_width + gap, box_height)
                x += ox
                y += oy
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT
            if self.active_range is not None and self.active_range[0] <= index <= self.active_range[1]:
                fill = (30, 47, 59)
                border = colors.BLUE
            if self.insertion_range is not None and self.insertion_range[0] <= index <= self.insertion_range[1]:
                fill = (41, 50, 35)
                border = colors.GREEN
            if self.left_done is not None and self.active_range and self.active_range[0] < index <= self.left_done:
                fill = (42, 43, 29)
                border = colors.YELLOW
            if self.right_done is not None and self.active_range and self.right_done <= index <= self.active_range[1]:
                fill = (26, 45, 50)
                border = colors.BLUE
            if index == self.compare_index:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE
            if index in self.fixed:
                fill = (35, 72, 52)
                border = colors.GREEN
            self.rect(x, y, box_width, box_height, fill, border, 6)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, text_color, True)
            slot_x = start_x + index * (box_width + gap)
            self.centered_text(f"#{index}", slot_x + box_width / 2, top + box_height + 24, index_size, colors.TEXT_MUTED)

    def _draw_stack(self):
        if not self.stack:
            return
        _, start_x, _, box_width, _, gap = self._layout_metrics()
        row_height = 34
        visible_frames = self.stack[-8:]
        first_level = len(self.stack) - len(visible_frames)
        visible_last = len(visible_frames) - 1
        active_level = len(self.stack) - 1
        for visible_level, frame in enumerate(visible_frames):
            level = first_level + visible_level
            top = 300 + visible_level * 42
            if visible_level == visible_last and visible_level > 0:
                top += 22
            row_x_offset = 0
            if level == self.stack_anim_level:
                if self.stack_anim_kind == "push":
                    top -= 42 * (1.0 - self.stack_anim_progress)
                elif self.stack_anim_kind == "pop":
                    top -= 42 * self.stack_anim_progress
            left = frame["left"]
            right = frame["right"]
            pivot = frame["pivot"]
            self.text(f"depth {level + 1}", 78 + row_x_offset, top + 7, 17, colors.TEXT_MUTED)
            swapping = set(self.swap_pair or ()) if level == active_level else set()
            moving_shift = self.shift_pair[0] if level == active_level and self.shift_pair is not None and not self.shift_pick else None
            draw_order = [index for index in range(left, right + 1) if index not in swapping]
            draw_order += [index for index in range(left, right + 1) if index in swapping]
            if moving_shift is not None and left <= moving_shift <= right:
                draw_order = [index for index in draw_order if index != moving_shift] + [moving_shift]
            for index in draw_order:
                x = start_x + index * (box_width + gap) + row_x_offset
                y = top
                if index in swapping:
                    ox, oy = self._swap_offset(index, box_width + gap, row_height)
                    x += ox
                    y += oy
                fill = (28, 36, 45)
                border = colors.BORDER
                text_color = colors.TEXT
                if index == moving_shift:
                    self.rect(x, top, box_width, row_height, (21, 25, 31), (61, 69, 82), 4)
                    self.centered_text(self.array[index], x + box_width / 2, top + row_height / 2, max(10, min(16, box_width * 0.38)), colors.TEXT_MUTED)
                    ox, oy = self._insertion_shift_offset(index, box_width + gap)
                    x += ox
                    y += oy
                if pivot is not None:
                    if index == pivot:
                        fill = (89, 39, 77)
                        border = colors.RED
                    elif self.left_done is not None and left < index <= self.left_done:
                        fill = (42, 43, 29)
                        border = colors.YELLOW
                    elif self.right_done is not None and self.right_done <= index <= right:
                        fill = (26, 45, 50)
                        border = colors.BLUE
                if level == active_level:
                    if index == self.compare_index:
                        fill = (82, 55, 30)
                        border = colors.ORANGE
                    if self.swap_pair is not None and index in self.swap_pair:
                        fill = (62, 66, 107)
                        border = colors.BLUE
                    if (
                        self.insertion_range is not None
                        and self.insertion_sorted_until is not None
                        and self.insertion_range[0] <= index <= self.insertion_sorted_until
                    ):
                        fill = (35, 72, 52)
                        border = colors.GREEN
                    if self.hole_index == index:
                        fill = (36, 39, 45)
                        border = colors.TEXT_MUTED
                        text_color = colors.TEXT_MUTED
                    if self.shift_pair is not None and index in self.shift_pair:
                        fill = (62, 66, 107)
                        border = colors.BLUE
                self.rect(x, y, box_width, row_height, fill, border, 4)
                self.centered_text(self.array[index], x + box_width / 2, y + row_height / 2, max(10, min(16, box_width * 0.38)), text_color)
                if level == active_level:
                    label_y = top - 18
                    label_top = label_y - 10
                    if index == self.p_index:
                        slot_x = start_x + index * (box_width + gap)
                        self.text("p", slot_x + 2, label_top, 18, colors.YELLOW, True)
                    if index == self.q_index:
                        slot_x = start_x + index * (box_width + gap)
                        self.right_text("q", slot_x + box_width - 2, label_top, 18, colors.BLUE, True)
                    if index == self.pivot_index:
                        slot_x = start_x + index * (box_width + gap)
                        self.centered_text("pivot", slot_x + box_width / 2, label_y, 17, colors.RED, True)
            if level == active_level:
                self._draw_pivot_scan_marker(start_x, top, box_width, row_height, gap)
        self._draw_quick_insertion_pick()
        self._draw_quick_insertion_sorted_region()

    def _draw_legend(self):
        self.rect(1000, 72, 30, 20, (89, 39, 77), colors.RED, 4)
        self.text("pivot", 1042, 68, 21, colors.TEXT_MUTED)
        self.rect(1000, 108, 30, 20, (42, 43, 29), colors.YELLOW, 4)
        self.text("pivot 이하", 1042, 104, 21, colors.TEXT_MUTED)
        self.rect(1220, 108, 30, 20, (26, 45, 50), colors.BLUE, 4)
        self.text("pivot 이상", 1262, 104, 21, colors.TEXT_MUTED)
        self.rect(1220, 72, 30, 20, (35, 72, 52), colors.GREEN, 4)
        self.text("위치 확정", 1262, 68, 21, colors.TEXT_MUTED)

    def _draw_pivot_scan_marker(self, start_x, top, box_width, row_height, gap):
        if self.scan_index is None or self.pivot_value is None or not self.stack:
            return
        source = self.scan_start_index
        if source is None:
            source = self.pivot_index
        if source is None:
            source = self.stack[-1]["left"]
        source_x = start_x + source * (box_width + gap)
        target_x = start_x + self.scan_index * (box_width + gap)
        x = source_x + (target_x - source_x) * self.scan_progress
        y = top + row_height + 20
        self.rect(x, y, box_width, row_height, (89, 39, 77), colors.RED, 4)
        self.centered_text(self.pivot_value, x + box_width / 2, y + row_height / 2, max(10, min(16, box_width * 0.38)), colors.TEXT, True)
        label = "큰 값 찾기" if self.scan_direction == "p" else "작은 값 찾기"
        self.centered_text(label, x + box_width / 2, y + row_height + 18, 15, colors.TEXT_MUTED)

    def _draw_quick_insertion_pick(self):
        if self.picked_from is None or self.picked_value is None:
            return
        x, y, box_width, row_height = self._quick_stack_rect(self.picked_from)
        if self.shift_pick and self.shift_pair is not None:
            _, target = self.shift_pair
            target_x, target_y, _, _ = self._quick_stack_rect(target)
            x += (target_x - x) * self.shift_progress
            y = y - row_height * 1.25 * (1 - self.shift_progress) + (target_y - y) * self.shift_progress
        else:
            y -= row_height * 1.25 * self.pick_progress
        self.rect(x, y, box_width, row_height, (89, 39, 77), colors.RED, 4)
        self.centered_text(self.picked_value, x + box_width / 2, y + row_height / 2, max(10, min(16, box_width * 0.38)), colors.TEXT, True)

    def _draw_quick_insertion_sorted_region(self):
        if self.insertion_range is None or self.insertion_sorted_until is None or not self.stack:
            return
        left, _ = self.insertion_range
        right = min(self.insertion_sorted_until, len(self.array) - 1)
        if right < left:
            return
        _, start_x, _, box_width, _, gap = self._layout_metrics()
        _, top, _, row_height = self._quick_stack_rect(left)
        x = start_x + left * (box_width + gap) - 5
        width = (right - left + 1) * box_width + (right - left) * gap + 10
        rect = self.view.rect(x, top - 5, width, row_height + 10)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(8),
        )
        self.centered_text("정렬된 구간", x + width / 2, top + row_height + 24, 17, (88, 126, 101), True)

    def _quick_stack_rect(self, index):
        _, start_x, _, box_width, _, gap = self._layout_metrics()
        row_height = 34
        active_level = max(0, len(self.stack) - 1)
        first_level = max(0, len(self.stack) - 8)
        visible_level = active_level - first_level
        top = 300 + visible_level * 42
        if visible_level > 0:
            top += 22
        x = start_x + index * (box_width + gap)
        return x, top, box_width, row_height

    def _insertion_shift_offset(self, index, step_width):
        if self.shift_pair is None:
            return 0, 0
        source, target = self.shift_pair
        if index != source:
            return 0, 0
        return (target - source) * step_width * self.shift_progress, 0

    def _swap_offset(self, index, step_width, box_height):
        if self.swap_pair is None:
            return 0, 0
        left, right = self.swap_pair
        if index == left:
            target = right
            vertical_sign = -1
        elif index == right:
            target = left
            vertical_sign = 1
        else:
            return 0, 0

        progress = self.swap_progress
        ox = (target - index) * step_width * progress
        arc = -2 * (progress - 0.5) ** 2 + 0.5
        oy = vertical_sign * box_height * arc
        return ox, oy

    def _animate_scan(self, milliseconds):
        self._animate_progress(milliseconds, "scan_progress")
        self.wait(150)

    def _animate_swap(self, milliseconds):
        self._animate_progress(milliseconds, "swap_progress")

    def _animate_insertion_pick(self, milliseconds):
        self._animate_progress(milliseconds, "pick_progress")
        self.wait(150)

    def _animate_insertion_shift(self, milliseconds):
        self._animate_progress(milliseconds, "shift_progress")

    def _animate_progress(self, milliseconds, attr):
        if self.is_max_speed() or self.running_to_section:
            setattr(self, attr, 1.0 if attr != "swap_progress" else 0.5)
            self._handle_events()
            self.draw()
            return

        duration = max(0.001, milliseconds / 1000 / self.speed)
        active_elapsed = 0.0
        last_tick = time.monotonic()
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                setattr(self, attr, 1.0 if attr != "swap_progress" else 0.5)
                self.draw()
                break

            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = min(1 / 60, duration - active_elapsed)
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue

            active_elapsed += delta
            setattr(self, attr, min(1.0, active_elapsed / duration))
            self.draw()
            if getattr(self, attr) >= 1.0:
                break
            self.clock.tick(60)

    def _layout_metrics(self):
        count = len(self.array)
        gap = max(4, min(12, 170 / max(1, count)))
        max_width = 1360
        box_width = min(72, (max_width - gap * (count - 1)) / count)
        box_height = 58
        start_x = 150 + (max_width - (box_width * count + gap * (count - 1))) / 2
        top = 170
        return count, start_x, top, box_width, box_height, gap

    def _update_stats(self):
        self.msg_stats(f"비교 {self.compare_count}회\n교환 {self.swap_count}회")


class VerticalBubbleSortVisualizer(BubbleSortVisualizer):
    def __init__(self, title="Bubble Sort", **kwargs):
        super().__init__(title, **kwargs)
        self.set_message_layout("side")

    def draw_content(self):
        self.text(self.title, 35, 32, 42, colors.TEXT, True)
        self.right_text("이웃한 두 값을 비교하고 큰 값을 아래쪽으로 보낸다.", 1565, 38, 22, colors.TEXT_MUTED)
        self._draw_array()

    def _draw_messages(self):
        super()._draw_messages()
        self._draw_legend()

    def _draw_array(self):
        if not self.array:
            return

        count, left, top, box_width, box_height, gap = self._layout_metrics()
        value_size = max(14, min(28, box_height * 0.52))
        index_size = max(10, min(18, box_height * 0.34))

        swapping = set(self.swap_pair or ())
        draw_order = [index for index in range(count) if index not in swapping]
        draw_order += [index for index in range(count) if index in swapping]

        for index in draw_order:
            value = self.array[index]
            slot_y = top + index * (box_height + gap)
            x = left
            y = slot_y
            index_x = 240
            index_y = slot_y + box_height * 0.28
            if index in swapping:
                ox, oy = self._swap_offset(index, box_width, box_height + gap)
                x += ox
                y += oy
                index_x += ox
                index_y += oy
            fill = colors.PANEL
            border = colors.BORDER
            text_color = colors.TEXT
            if self.sorted_from is not None and index >= self.sorted_from:
                fill = (35, 72, 52)
                border = colors.GREEN
            if self.compare_pair is not None and index in self.compare_pair:
                fill = (82, 55, 30)
                border = colors.ORANGE
            if self.swap_pair is not None and index in self.swap_pair:
                fill = (62, 66, 107)
                border = colors.BLUE

            self.rect(x, y, box_width, box_height, fill, border, 8)
            self.text(f"#{index}", index_x, index_y, index_size, colors.TEXT_MUTED)
            self.centered_text(value, x + box_width / 2, y + box_height / 2, value_size, text_color, True)

        if self.compare_pair is not None:
            self._pair_label("비교", self.compare_pair, left, top, box_width, box_height, gap, colors.ORANGE)
        if self.swap_pair is not None:
            self._pair_label("교환", self.swap_pair, left, top, box_width, box_height, gap, colors.BLUE)
        if self.sorted_from is not None and self.sorted_from < count:
            self._draw_sorted_region(left, box_width, gap, top, box_height, count)
            sorted_y = top + self.sorted_from * (box_height + gap) + box_height / 2
            self.text("정렬 완료 구간", left + box_width + 24, sorted_y - 14, 20, colors.GREEN, True)

    def _draw_sorted_region(self, left, box_width, gap, top, box_height, count):
        region_top = top + self.sorted_from * (box_height + gap)
        bottom = top + count * box_height + (count - 1) * gap
        margin = 6
        rect = self.view.rect(left - margin, region_top - margin, box_width + 2 * margin, bottom - region_top + 2 * margin)
        pygame.draw.rect(
            self.screen,
            (88, 126, 101),
            rect,
            width=self.view.length(2),
            border_radius=self.view.length(10),
        )

    def _pair_label(self, label, pair, left, top, box_width, box_height, gap, color):
        upper, lower = pair
        step_height = box_height + gap
        y1 = top + upper * step_height + box_height / 2
        y2 = top + lower * step_height + box_height / 2
        self.text(label, left + box_width + 24, (y1 + y2) / 2 - 14, 22, color, True)

    def _layout_metrics(self):
        count = len(self.array)
        gap = max(6, min(12, 140 / max(1, count)))
        max_area_height = 720
        box_height = min(56, (max_area_height - gap * (count - 1)) / count)
        box_width = 270
        left = 360
        top = 95 + (max_area_height - (box_height * count + gap * (count - 1))) / 2
        return count, left, top, box_width, box_height, gap

    def _swap_offset(self, index, box_width, step_height):
        if self.swap_pair is None:
            return 0, 0
        upper, lower = self.swap_pair
        if index == upper:
            target = lower
            horizontal_sign = 1
        elif index == lower:
            target = upper
            horizontal_sign = -1
        else:
            return 0, 0

        progress = self.swap_progress
        oy = (target - index) * step_height * progress
        arc = -2 * (progress - 0.5) ** 2 + 0.5
        ox = horizontal_sign * box_width * 0.35 * arc
        return ox, oy

    def _draw_legend(self):
        self.text("표시", 1140, 640, 20, colors.TEXT_MUTED, True)
        self.rect(1140, 682, 28, 20, (82, 55, 30), colors.ORANGE, 4)
        self.text("비교 중", 1180, 678, 20, colors.TEXT_MUTED)
        self.rect(1140, 716, 28, 20, (62, 66, 107), colors.BLUE, 4)
        self.text("교환한 원소", 1180, 712, 20, colors.TEXT_MUTED)
        self.rect(1320, 716, 28, 20, (35, 72, 52), colors.GREEN, 4)
        self.text("정렬 완료", 1360, 712, 20, colors.TEXT_MUTED)
