import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class KnapsackDpVisualizer(BaseVisualizer):
    item_colors = (colors.YELLOW, colors.BLUE, colors.GREEN, colors.ORANGE,
                   (219, 153, 202), (120, 208, 208), (235, 147, 148))
    skip_fill = (30, 49, 68)
    take_fill = (58, 49, 31)

    def setup(self, data):
        self.hidden = getattr(self, "hidden", False)
        self.msg_clear()
        self.set_data_info(data)
        self.weights, self.values, self.capacity = data.weights, data.values, data.capacity
        self.weight_unit = getattr(data, "weight_unit", 1)
        self.original_capacity = getattr(data, "original_capacity", self.capacity)
        self.best = None
        self.shown = {}
        self.active = self.hovered = self.motion = None
        self.source = None
        self.trace_path = []
        self.selected = []
        self.tracing = self.finished = False

    def _running_hint(self):
        return super()._running_hint() + "  H: 설명"

    def _action_hint(self):
        return super()._action_hint() + "  H: 설명"

    def _draw_messages(self):
        if self.hidden:
            self.text(self.messages["hint"], 80, 852, 17, colors.TEXT_MUTED)
        else:
            super()._draw_messages()

    def _handle_key(self, key, mod=0):
        if key == pygame.K_h:
            self.hidden = not self.hidden
            self.hovered = None
            return
        if self.finished and key == pygame.K_RETURN:
            return
        if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_PERIOD, pygame.K_KP_PERIOD):
            self.hovered = None
        super()._handle_key(key, mod)

    def initialize(self, best):
        self.best = best
        self.msg_phase("초기값")
        self.msg_action("물건이 없거나 용량이 0이면 최대 가치는 0이다.")
        self.wait(650)
        bases = ([(0, w) for w in range(self.capacity + 1)]
                 + [(i, 0) for i in range(1, len(best))])
        for cell in bases:
            if self.stopped():
                return
            self.active = cell
            self.shown[cell] = (0, ())
            if not self.running_to_section and not self.is_max_speed():
                self.wait(160)
        self.active = None
        self.section_end()

    def compare(self, i, w, skip_value, take_value):
        self.active, self.source = (i, w), None
        self.msg_phase(f"물건 {i}번")
        self.msg_action(f"용량 {w}에서 물건 {i}번을 담을지 비교한다.")
        if take_value is None:
            self.msg_detail(f"무게 {self.weights[i - 1]} > 용량 {w}: 담을 수 없다.")
        else:
            self.msg_detail(f"안 담기: {skip_value}   |   담기: {take_value}")
        self.wait(850)

    def place(self, took):
        i, w = self.active
        self.source = (i - 1, w - self.weights[i - 1] if took else w)
        source_value, items = self.shown[self.source]
        if took:
            self.msg_action(f"물건 {i}번을 담아 가치 {self.best[i][w]}를 기록한다.")
        elif self.weights[i - 1] <= w and source_value == self.best[i - 1][w - self.weights[i - 1]] + self.values[i - 1]:
            self.msg_action(f"두 후보의 가치가 {source_value}로 같아 기존 선택을 유지한다.")
        else:
            self.msg_action(f"물건 {i}번은 담지 않고 기존 가치 {source_value}를 가져온다.")
        frames = max(2, round(26 / max(1, self.speed)))
        for frame in range(frames + 1):
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
            t = frame / frames
            self.motion = (source_value, items, i if took else None, t * t * (3 - 2 * t))
            self.wait(650 / frames)
        self.motion = None
        if self.stopped():
            return
        self.shown[self.active] = (self.best[i][w], items + (i,) if took else items)
        if not self.running_to_section and not self.is_max_speed():
            self.wait(310)
        if w == self.capacity:
            self.section_end()

    def trace(self, i, w, next_w, took):
        self.tracing = True
        self.active, self.source = (i, w), (i - 1, next_w)
        if not self.trace_path:
            self.trace_path.append(self.active)
        self.trace_path.append(self.source)
        if took:
            self.selected.insert(0, i)
        self.msg_phase("선택한 물건 복원")
        self.msg_action(f"물건 {i}번: " + ("담았다." if took else "담지 않았다."))
        self.msg_detail(f"K[{i}][{w}] → K[{i - 1}][{next_w}]")
        self.wait(850)

    def finish(self, maximum, selected):
        self.finished = True
        self.active = self.source = None
        self.selected = selected
        self.msg_phase("완료")
        total_weight = sum(self.weights[i - 1] for i in selected)
        self.msg_action(f"최대 가치 {maximum:,}  |  사용 용량 "
                        f"{total_weight * self.weight_unit}/{self.original_capacity}")
        self.msg_detail("선택한 물건: " + (", ".join(map(str, selected)) or "없음"))
        self.draw()

    def _cell(self, i, w):
        dx = min(145, 1310 / (self.capacity + 1))
        available = 585 if self.hidden else 365
        dy = min(84, available / (len(self.weights) + 1))
        return 208 + w * dx, 257 + i * dy, dx - 4, dy - 4

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = None
            if self.finished or (self.paused and not self.motion):
                for cell in self.shown:
                    if pygame.Rect(self.view.rect(*self._cell(*cell))).collidepoint(event.pos):
                        self.hovered = cell
                        break
        super().handle_event(event)

    def draw_content(self):
        self.text(self.title, 72, 40, 40, bold=True)
        if self.best is None:
            return
        focus = self.hovered or self.active
        self._draw_items(focus)
        self._draw_comparison(focus)
        for w in range(self.capacity + 1):
            x, _, width, _ = self._cell(0, w)
            ink = colors.ORANGE if focus and w == focus[1] else colors.TEXT_MUTED
            self.centered_text(w, x + width / 2, 238, 17, ink, True)
        self.text("물건 / 용량", 80, 225, 17, colors.TEXT_MUTED)
        for i in range(len(self.weights) + 1):
            _, y, _, height = self._cell(i, 0)
            self.text("물건 없음" if i == 0 else f"#{i}  {self.weights[i - 1]} / {self.values[i - 1]}",
                      85, y + height / 2 - 9, 17,
                      colors.ORANGE if focus and i == focus[0] else colors.TEXT_MUTED)
            for w in range(self.capacity + 1):
                cell = i, w
                fill, border = colors.PANEL_DARK, colors.BORDER
                if focus and focus[0] and focus[1] and (not self.tracing or self.hovered):
                    row, cap = focus
                    if cell == (row - 1, cap):
                        fill, border = self.skip_fill, colors.BLUE
                    elif cell == (row - 1, cap - self.weights[row - 1]):
                        fill, border = self.take_fill, colors.YELLOW
                if cell in self.trace_path:
                    fill, border = (29, 54, 42), colors.GREEN
                if cell == self.source:
                    border = colors.GREEN
                if cell == focus:
                    border = colors.ORANGE
                self._draw_cell(*self._cell(*cell), self.shown.get(cell), fill, border)
        if self.motion:
            self._draw_motion()

    def _draw_items(self, focus):
        for index, (weight, value) in enumerate(zip(self.weights, self.values), 1):
            x = 80 + (index - 1) * 171
            ink = self.item_colors[(index - 1) % len(self.item_colors)]
            border = (colors.GREEN if index in self.selected else colors.ORANGE
                      if focus and index == focus[0] else ink)
            self.rect(x, 108, 151, 42, colors.PANEL_DARK, border, radius=5)
            self.text(f"#{index}", x + 10, 116, 19, ink, True)
            label = (f"{weight * self.weight_unit}→{weight} / {value}"
                     if self.weight_unit > 1 else f"{weight} / {value}")
            self.text(label, x + 50, 118, 17)
        unit_label = (f"원래 무게 → 환산 무게 / 가치  |  1단위 = {self.weight_unit}"
                      if self.weight_unit > 1 else "무게 / 가치")
        self.text(unit_label, 82, 158, 15, colors.TEXT_MUTED)
        capacity = (f"{self.original_capacity} → {self.capacity}"
                    if self.weight_unit > 1 else str(self.capacity))
        self.right_text(f"배낭 용량 {capacity}", 1510, 115, 23, colors.TEXT, True)

    def _draw_comparison(self, focus):
        if not focus:
            if self.finished:
                value = self.best[-1][self.capacity]
                items = ", ".join(f"#{i}" for i in self.selected) or "없음"
                self.text(f"최대 가치 {value:,}   |   선택: {items}", 82, 186, 24, colors.GREEN, True)
            return
        i, w = focus
        if self.hovered and focus in self.shown:
            value, items = self.shown[focus]
            labels = ", ".join(f"#{item}" for item in items) or "없음"
            self.text(f"K[{i}][{w}] = {value:,}   |   선택: {labels}", 82, 186, 23, colors.ORANGE)
        elif self.tracing and self.source:
            a, b = self.source
            self.text(f"K[{i}][{w}] → K[{a}][{b}]", 82, 186, 24, colors.GREEN, True)
        elif i and w:
            weight, value = self.weights[i - 1], self.values[i - 1]
            self.text(f"안 담기: K[{i - 1}][{w}] = {self.best[i - 1][w]:,}", 82, 186, 23, colors.BLUE)
            remaining = w - weight
            if remaining >= 0:
                previous = self.best[i - 1][remaining]
                self.text(f"담기: K[{i - 1}][{remaining}] + {value} = {previous + value:,}",
                          590, 186, 23, colors.YELLOW)
            else:
                self.text(f"담기 불가: 무게 {weight} > 용량 {w}", 590, 186, 23, colors.TEXT_MUTED)

    def _draw_cell(self, x, y, width, height, result, fill, border):
        self.rect(x, y, width, height, fill, border, radius=3)
        if result is None:
            return
        value, items = result
        self.centered_text(f"{value:,}", x + width / 2, y + height * 0.32, 20, colors.TEXT, True)
        size = min(20, (width - 10) / max(1, len(items)), height * 0.32)
        for slot, item in enumerate(items):
            cx = x + width / 2 + (slot - (len(items) - 1) / 2) * size
            cy = y + height * 0.73
            ink = self.item_colors[(item - 1) % len(self.item_colors)]
            self.rect(cx - size * 0.37, cy - size * 0.37, size * 0.74, size * 0.74,
                      colors.PANEL, ink, radius=0)
            self.centered_text(item, cx, cy, min(13, size * 0.78), ink, True)

    def _draw_motion(self):
        value, items, added, t = self.motion
        x, y, width, height = self._cell(*self.source)
        end_x, end_y, _, _ = self._cell(*self.active)
        if added is not None and t >= 1:
            items += (added,)
            value += self.values[added - 1]
        self._draw_cell(x + (end_x - x) * t, y + (end_y - y) * t, width, height,
                        (value, items), colors.PANEL, colors.GREEN)
        if added is not None and 0.35 < t < 1:
            progress = (t - 0.35) / 0.65
            size = min(20, (width - 10) / (len(items) + 1), height * 0.32)
            start_x, start_y = 106 + (added - 1) * 171, 129
            target_x = end_x + width / 2 + len(items) * size / 2
            target_y = end_y + height * 0.73
            cx = start_x + (target_x - start_x) * progress
            cy = start_y + (target_y - start_y) * progress
            ink = self.item_colors[(added - 1) % len(self.item_colors)]
            self.rect(cx - 9, cy - 9, 18, 18, colors.PANEL, ink, radius=0)
            self.centered_text(added, cx, cy, 13, ink, True)
