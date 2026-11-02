"""분할 가능한 배낭: 같은 높이의 사각형을 무게에 비례하여 자르고 옮긴다."""

import math

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class FractionalKnapsackVisualizer(BaseVisualizer):
    palette = [colors.BLUE, colors.ORANGE, colors.GREEN, colors.RED,
               (173, 137, 213), colors.YELLOW, (73, 185, 185), (215, 145, 173)]

    def setup(self, data):
        self.msg_clear()
        self.set_data_info(data)
        self.items = [tuple(item) for item in data.items]
        self.capacity = data.capacity
        if (not math.isfinite(self.capacity) or self.capacity < 0 or not self.items or
                any(not math.isfinite(w) or w <= 0 or not math.isfinite(v) or v < 0
                    for w, v in self.items)):
            raise ValueError("용량은 0 이상, 무게는 양수, 가치는 0 이상인 유한한 수여야 합니다.")
        self.order = list(range(len(self.items)))
        self.ratios = {}
        self.selected = {}
        self.packed = []
        self.focus = None
        self.motion = None
        self.cut = None
        self.finished = False
        self.unit = (1440 - 18 * (len(self.items) - 1)) / max(
            sum(w for w, _ in self.items), self.capacity, 1)
        self.msg_phase("물건 준비")
        self.msg_action("물건의 무게와 가치를 확인한다.")
        self.msg_detail("높이는 모두 같고 가로 길이·면적은 무게에 비례한다. 물건은 나누어 담을 수 있다.")
        self.draw()
        self.wait(1000)
        self.section_end()

    def measure(self, index, ratio):
        self.focus = index
        self.ratios[index] = ratio
        weight, value = self.items[index]
        self.msg_phase("단위 무게당 가치")
        self.msg_action(f"#{index}: {value:g} ÷ {weight:g} = {ratio:g}")
        self.msg_detail("금액 자체가 아니라 무게 1당 얻는 가치를 계산한다.")
        self.wait(1000)
        self.section_end()

    def sort_items(self, order):
        order = list(order)
        if sorted(order) != list(range(len(self.items))):
            raise ValueError("정렬 순서는 모든 물건 번호의 순열이어야 합니다.")
        self.focus = None
        self.msg_phase("단가 내림차순 정렬")
        self.msg_action("단위 무게당 가치가 높은 물건부터 자리를 잡는다.")
        self.msg_detail("물건 번호와 색은 유지한다. 단가가 같으면 입력 순서를 유지한다.")
        before, after = self._positions(self.order), self._positions(order)
        self._animate({"kind": "sort", "before": before, "after": after})
        self.order = order
        self.wait(800)
        self.section_end()

    def take(self, index, amount):
        weight, value = self.items[index]
        remaining = self.capacity - sum(w for _, w in self.packed)
        if amount <= 0 or amount > weight or amount > remaining + 1e-9 or index in self.selected:
            raise ValueError("담는 무게와 남은 용량을 확인하세요.")
        self.focus = index
        partial = amount < weight
        self.cut = (index, amount) if partial else None
        self.msg_phase("일부 잘라 담기" if partial else "전체 담기")
        self.msg_action(f"#{index}에서 {amount:g} / {weight:g}만큼 담는다.")
        self.msg_detail(f"남은 용량 {remaining:g}, 담을 비율 {amount / weight:g}, 추가 가치 {value * amount / weight:g}")
        # 절단선을 먼저 보여 준 뒤 선택한 조각만 배낭으로 이동한다.
        self.wait(1100 if partial else 650)
        source = (self._positions(self.order)[index], 235)
        destination = (80 + sum(w for _, w in self.packed) * self.unit, 465)
        self._animate({"kind": "take", "index": index, "amount": amount,
                       "source": source, "destination": destination})
        self.selected[index] = amount
        self.packed.append((index, amount))
        self.cut = None
        self.wait(650)
        self.section_end()

    def finish(self):
        self.finished = True
        self.focus = None
        weight = sum(w for _, w in self.packed)
        value = sum(w * self.items[i][1] / self.items[i][0] for i, w in self.packed)
        self.msg_phase("분할 가능한 배낭: 결과")
        self.msg_action(f"총무게 {weight:g} / {self.capacity:g}, 총가치 {value:g}")
        self.msg_detail("단가가 높은 물건부터 담고, 마지막 물건도 같은 단가로 필요한 만큼만 나누어 담는다.")
        self.draw()

    def _animate(self, motion):
        self.motion = {**motion, "t": 0}
        try:
            for frame in range(51):
                if self.stopped() or self.running_to_section or self.is_max_speed():
                    break
                t = frame / 50
                self.motion["t"] = t * t * (3 - 2 * t)
                self.wait(22)
        finally:
            self.motion = None

    def _positions(self, order):
        x = 80
        result = {}
        for index in order:
            result[index] = x
            x += self.items[index][0] * self.unit + 18
        return result

    def _text_fit(self, label, x, y, width, size=25, color=colors.TEXT):
        while size > 10 and self.font(size, True).size(str(label))[0] > self.view.length(max(width - 8, 1)):
            size -= 1
        if self.font(size, True).size(str(label))[0] <= self.view.length(width):
            self.centered_text(label, x + width / 2, y, size, color, True)

    def _block(self, index, amount, x, y, muted=False, labels=False):
        weight, value = self.items[index]
        width = amount * self.unit
        color = self.palette[index % len(self.palette)]
        fill = tuple(int(c * (0.18 if muted else 0.42)) for c in color)
        self.rect(x, y, width, 100, fill, colors.BORDER if muted else color, radius=0)
        self._text_fit(f"{value * amount / weight:g}", x, y + 50, width,
                       color=colors.TEXT_MUTED if muted else colors.TEXT)
        if labels:
            self._text_fit(f"#{index}", x, y - 27, width, 20, color)
            self._text_fit(f"무게 {amount:g}", x, y + 125, width, 20)
            if index in self.ratios:
                self._text_fit(f"단가 {self.ratios[index]:g}", x, y - 63, width, 20, color)

    def draw_content(self):
        if not hasattr(self, "items"):
            return
        self.text("Fractional Knapsack", 70, 35, 44, bold=True)
        self.text("분할 가능한 배낭", 70, 95, 25, colors.TEXT_MUTED)
        self.right_text("면적 = 무게   |   내부 숫자 = 가치", 1520, 100, 22, colors.TEXT_MUTED)
        positions = self._positions(self.order)
        for index in self.order:
            x, y = positions[index], 235
            if self.motion and self.motion["kind"] == "sort":
                t = self.motion["t"]
                x = self.motion["before"][index] * (1 - t) + self.motion["after"][index] * t
                y += math.sin(math.pi * t) * (38 if index % 2 else -38)
            taken = self.selected.get(index, 0)
            if self.motion and self.motion["kind"] == "take" and self.motion["index"] == index:
                taken = self.motion["amount"]
            weight, _ = self.items[index]
            if taken < weight:
                self._block(index, weight - taken, x + taken * self.unit, y,
                            muted=index in self.selected, labels=True)
            if self.focus == index:
                pygame.draw.rect(self.screen, colors.YELLOW,
                                 self.view.rect(x - 4, y - 4, weight * self.unit + 8, 108),
                                 max(1, self.view.length(2)))
            if self.cut and self.cut[0] == index and self.motion is None:
                cx = x + self.cut[1] * self.unit
                pygame.draw.line(self.screen, colors.YELLOW, self.view.point(cx, y - 8),
                                 self.view.point(cx, y + 108), max(1, self.view.length(4)))
        self.text("배낭", 80, 410, 25, colors.BLUE, True)
        self.rect(80, 465, max(self.capacity * self.unit, 1), 100,
                  colors.PANEL_DARK, colors.BORDER, radius=0)
        x = 80
        for index, amount in self.packed:
            self._block(index, amount, x, 465)
            self._text_fit(f"#{index} · {amount:g}", x, 590, amount * self.unit, 20)
            x += amount * self.unit
        if self.motion and self.motion["kind"] == "take":
            m = self.motion
            t = m["t"]
            x = m["source"][0] * (1 - t) + m["destination"][0] * t
            y = m["source"][1] * (1 - t) + m["destination"][1] * t
            self._block(m["index"], m["amount"], x, y)
        used = sum(w for _, w in self.packed)
        total = sum(w * self.items[i][1] / self.items[i][0] for i, w in self.packed)
        self.right_text(f"남은 용량 {self.capacity - used:g}   |   누적 가치 {total:g}",
                        1520, 410, 25, colors.GREEN, True)
