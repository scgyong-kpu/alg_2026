from math import factorial, inf, pi
from time import monotonic

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class ChainedMatrixVisualizer(BaseVisualizer):
    def setup(self, data):
        self.hidden = getattr(self, "hidden", False)
        self.msg_clear()
        self.set_data_info(data)
        self.sizes = data.sizes
        self.cost = self.split = None
        self.active = None
        self.updated = False
        self.completed = set()
        self.order = ""
        self.finished = False
        self.orders = None
        self.scroll = 0
        self.follow_tail = True
        self.hovered_order = None
        self.best_cost = inf
        self.layout = getattr(self, "layout", "table")
        self.layout_mix = 1.0 if self.layout == "pyramid" else 0.0
        self.layout_transition = None
        self.hovered_range = None
        self.reuse = None
        self.initialized_count = 0
        self.initializing = False
        self.initial_cell = None
        self.decision = None
        self.previous_cost = None
        self.previous_expression = ""

    def _running_hint(self):
        return super()._running_hint() + "  V: 표/역삼각형  휠: 목록  H: 설명"

    def _action_hint(self):
        return super()._action_hint() + "  V: 표/역삼각형  휠: 목록  H: 설명"

    def _visible_rows(self):
        return 12 if self.hidden else 7

    def _draw_messages(self):
        if self.hidden:
            self.text(self.messages["hint"], 80, 862, 17, colors.TEXT_MUTED)
        else:
            super()._draw_messages()

    def start_orders(self):
        self.orders = []
        self.total_orders = factorial(len(self.sizes) - 2)
        self.msg_phase("곱셈 실행 순서 전체")
        self.msg_action(f"행렬 {len(self.sizes) - 1}개: 곱셈 실행 순서 {self.total_orders:,}개")
        self.msg_detail("서로 다른 실행 순서가 같은 괄호 묶음을 만들 수도 있다.")

    def add_order(self, order, expression, cost):
        self.orders.append((order, expression, cost))
        self.best_cost = min(self.best_cost, cost)
        if self.follow_tail:
            self.scroll = max(0, len(self.orders) - self._visible_rows())
        self.msg_stats(f"{len(self.orders):,}/{self.total_orders:,}")
        self.msg_action(f"현재까지 최소 곱셈 횟수: {self.best_cost:,}")
        self.wait(1000)

    def finish_orders(self):
        self.finished = True
        self.msg_phase("전체 순서 나열 완료")
        self.msg_action(f"최소 곱셈 횟수: {self.best_cost:,}")
        self.section_end()
        self.draw()

    def handle_event(self, event):
        if self.orders is not None:
            if event.type == pygame.MOUSEWHEEL:
                self.follow_tail = False
                self.scroll = min(max(0, self.scroll - event.y * 3),
                                  max(0, len(self.orders) - self._visible_rows()))
                self.hovered_order = None
            elif event.type == pygame.MOUSEMOTION:
                self.hovered_order = None
                for row in range(self._visible_rows()):
                    index = self.scroll + row
                    if index >= len(self.orders):
                        break
                    rect = pygame.Rect(self.view.rect(80, 312 + row * 42, 1440, 42))
                    if rect.collidepoint(event.pos):
                        self.hovered_order = index
                        break
        elif (event.type == pygame.MOUSEMOTION and self.cost is not None
              and self.layout_transition is None and not self.reuse):
            self.hovered_range = None
            for left, right in self.completed:
                if pygame.Rect(self.view.rect(*self._range_rect(left, right))).collidepoint(event.pos):
                    self.hovered_range = left, right
                    break
        super().handle_event(event)

    def _handle_key(self, key, mod=0):
        if key == pygame.K_v and self.orders is None:
            mix = self._layout_frame()
            self.layout = "table" if self.layout == "pyramid" else "pyramid"
            target = 1.0 if self.layout == "pyramid" else 0.0
            self.layout_transition = (monotonic(), mix, target)
            self.hovered_range = None
            return
        if key == pygame.K_h:
            self.hidden = not self.hidden
            self.hovered_range = None
            if self.orders is not None:
                limit = max(0, len(self.orders) - self._visible_rows())
                self.scroll = limit if self.follow_tail else min(self.scroll, limit)
                self.hovered_order = None
            return
        if key == pygame.K_RETURN and self.finished:
            return
        super()._handle_key(key, mod)

    def start(self, sizes, cost, split):
        self.sizes, self.cost, self.split = sizes, cost, split
        self.orders = None
        self.initialized_count = 0
        self.initializing = True
        self.initial_cell = None
        self.msg_phase("초기값")
        self.msg_action("행렬 하나만 있는 구간의 곱셈 비용은 0이다.")
        self.msg_detail("대각선의 초기값을 차례로 기록한다.")
        self.wait(500)
        for i in range(len(cost)):
            if self.stopped():
                return
            self.initialized_count = i + 1
            self.initial_cell = i
            self.msg_action(f"C[{i}][{i}] = 0: A{i} 하나는 곱셈이 필요 없다.")
            self.wait(1000)
        self.initializing = False
        self.initial_cell = None
        self.section_end()

    def compare(self, left, right, mid, candidate):
        self.hovered_range = None
        self.active = left, right, mid, candidate
        self.updated = False
        self.decision = None
        self.previous_cost = self.cost[left][right]
        self.previous_expression = self._expression(left, right)
        self.reuse = (0, 0.0)
        self.msg_phase(f"길이 {right - left + 1}인 구간")
        a_range = f"A{left}" if left == mid else f"A{left}~A{mid}"
        b_range = f"A{right}" if mid + 1 == right else f"A{mid + 1}~A{right}"
        timing = "" if left == mid and mid + 1 == right else "마지막에 "
        self.msg_action(f"{a_range}와 {b_range}를 {timing}곱한다.")
        a, b = self.cost[left][mid], self.cost[mid + 1][right]
        x, y, z = self.sizes[left], self.sizes[mid + 1], self.sizes[right + 1]
        self.msg_detail(f"{a} + {b} + {x} × {y} × {z} = {candidate}")
        self.wait(500)
        for stage, duration in ((1, 850), (2, 850), (3, 650), (4, 850)):
            frames = max(1, round(36 / max(1, self.speed)))
            for frame in range(frames + 1):
                if self.stopped() or self.running_to_section or self.is_max_speed():
                    break
                t = frame / frames
                self.reuse = stage, t*t*(3-2*t)
                self.wait(duration / frames)
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
        self.reuse = (5, 1.0)
        if not self.stopped():
            self.wait(600)
        if not self.stopped() and candidate >= self.previous_cost:
            relation = "=" if candidate == self.previous_cost else ">"
            self.msg_action(f"후보 {candidate:,} {relation} 기존 {self.previous_cost:,}: 기존 값을 유지한다.")
            self._animate_candidate(False)
            if not self.stopped():
                self.wait(450)

    def update_cost(self):
        self.updated = True
        left, right, mid, candidate = self.active
        self.msg_action(f"cost[{left}][{right}] = {candidate}, 분할 위치 = {mid}")
        self._animate_candidate(True)
        self.wait(450)

    def _animate_candidate(self, accepted):
        for phase in range(1, 2 if accepted else 3):
            frames = max(1, round(36 / max(1, self.speed)))
            for frame in range(frames + 1):
                if self.stopped() or self.running_to_section or self.is_max_speed():
                    break
                t = frame / frames
                self.decision = (accepted, phase, t*t*(3-2*t))
                self.wait(750 / frames)
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
        self.decision = (accepted, 3, 1.0)

    def end_range(self):
        left, right, _, _ = self.active
        self.completed.add((left, right))
        self.section_end()
        self.reuse = None
        self.decision = None

    def finish(self, order):
        self.active = None
        self.reuse = None
        self.decision = None
        self.order = order
        self.finished = True
        self.msg_phase("완료")
        self.msg_action(f"최소 스칼라 곱셈 횟수: {self.cost[0][-1]}")
        self.msg_detail("저장한 분할 위치를 따라 최적 괄호 묶음을 복원했다.")
        self.draw()

    def draw_content(self):
        self.text("Chained Matrix Multiplication", 72, 40, 38, bold=True)
        if self.orders is not None:
            self._draw_orders()
            return
        focus = self._focus()
        self._draw_header(focus=focus)
        if self.cost is None:
            return
        if focus:
            left, right, mid, candidate = focus
            a, b = self.cost[left][mid], self.cost[mid + 1][right]
            x, y, z = self.sizes[left], self.sizes[mid + 1], self.sizes[right + 1]
            self._fitted_text(f"C[{left}][{mid}] + C[{mid + 1}][{right}] + {x}×{y}×{z}"
                              f" = {a:,} + {b:,} + {x*y*z:,} = {candidate:,}",
                              800, 305, 1400, 22, colors.TEXT)
            self.right_text(f"L={right-left+1}   [{left}..{right}]   k={mid}", 1520, 86, 18, colors.ORANGE)
        else:
            self.centered_text("구간별 최소 곱셈 횟수와 최적 괄호 묶음", 800, 305, 20, colors.TEXT_MUTED)
        self._draw_ranges(focus)
        if focus and self.reuse:
            self._draw_reuse(focus)

    def _focus(self):
        if self.hovered_range is not None:
            left, right = self.hovered_range
            mid = self.split[left][right]
            return left, right, mid, self.cost[left][right]
        return self.active

    def _expression(self, left, right):
        if left == right:
            return f"A{left}"
        mid = self.split[left][right]
        if mid is None:
            return ""
        return f"({self._expression(left, mid)}×{self._expression(mid + 1, right)})"

    def _fitted_text(self, text, cx, cy, width, size, color):
        while size > 10 and self.font(size).size(text)[0] > self.view.length(width):
            size -= 1
        while len(text) > 1 and self.font(size).size(text)[0] > self.view.length(width):
            text = text[:-2] + "…"
        self.centered_text(text, cx, cy, size, color)

    def _layout_frame(self):
        if self.layout_transition is None:
            return self.layout_mix
        started, initial, target = self.layout_transition
        progress = min(1.0, (monotonic() - started) / 0.95)
        eased = progress * progress * (3 - 2 * progress)
        self.layout_mix = initial + (target - initial) * eased
        if progress >= 1:
            self.layout_transition = None
        return self.layout_mix

    def _range_rect(self, left, right, mix=None):
        if mix is None:
            mix = self._layout_frame()
        count = len(self.sizes) - 1
        height = (480 if self.hidden else 280) / count
        width = 1400 / count
        table = 100 + right*width, 350 + left*height, width - 5, height - 4
        level = right - left
        cells = count - (right - left)
        # 구간이 길수록 셀은 조금 넓히되, 행 전체의 폭은 줄여 역삼각형을 만듭니다.
        width = min(600, 1400 / count * (1 + 0.45 * level / max(1, count - 1)))
        pyramid = (1600 - cells*width)/2 + left*width, 350 + level*height, width - 5, height - 4
        return tuple(a + (b-a)*mix for a, b in zip(table, pyramid))

    def _draw_ranges(self, focus):
        count = len(self.sizes) - 1
        mix = self._layout_frame()
        if self.layout == "table" and self.layout_transition is None:
            self.centered_text("i / j", 65, 333, 16, colors.TEXT_MUTED)
            for index in range(count):
                x, y, w, h = self._range_rect(index, index, mix)
                self.centered_text(index, x+w/2, 333, 17, colors.BLUE, True)
                self.centered_text(index, 77, y+h/2, 17, colors.YELLOW, True)
        for left in range(count):
            for right in range(left, count):
                x, y, w, h = self._range_rect(left, right, mix)
                border, fill = colors.BORDER, colors.PANEL_DARK
                known = ((left == right and left < self.initialized_count)
                         or (left, right) in self.completed)
                if left == right == self.initial_cell:
                    border = colors.ORANGE
                if self.active and (left, right) == self.active[:2]:
                    known = True
                if focus:
                    i, j, mid, _ = focus
                    if (left, right) == (i, j):
                        border, fill = colors.ORANGE, colors.PANEL
                        if self.decision:
                            border = colors.GREEN if self.decision[0] else colors.RED
                    elif (left, right) == (i, mid):
                        border, fill = colors.YELLOW, (53, 48, 30)
                    elif (left, right) == (mid + 1, j):
                        border, fill = colors.BLUE, (28, 45, 61)
                self.rect(x, y, w, h, fill, border, radius=3)
                value = self.cost[left][right]
                arriving = (self.decision and self.decision[0] and self.decision[1] < 3
                            and self.active and (left, right) == self.active[:2])
                if arriving:
                    value = self.previous_cost
                label = ("" if self.initializing else "—") if not known else "∞" if value == inf else f"{value:,}"
                self._fitted_text(label, x+w*0.33, y+h*0.3, w*0.6, min(25, h*0.33),
                                  colors.GREEN if known else colors.TEXT_MUTED)
                expression = self._expression(left, right) if known else f"A{left}" if left == right else f"A{left}..A{right}"
                if arriving:
                    expression = self.previous_expression
                self._fitted_text(expression, x+w*0.33, y+h*0.7, w*0.6, min(19, h*0.28), colors.TEXT)
                if known and value != inf:
                    self._result_shape(left, right, x+w*0.82, y+h*0.36,
                                       min(w*0.24, h*0.45), colors.TEXT_MUTED)
                    self._fitted_text(f"{self.sizes[left]}×{self.sizes[right+1]}",
                                      x+w*0.82, y+h*0.8, w*0.3, min(14,h*0.23), colors.TEXT_MUTED)

    def _draw_orders(self):
        selected = self.hovered_order
        if selected is None and self.orders:
            selected = len(self.orders) - 1
        order = self.orders[selected][0] if selected is not None else ()
        self._draw_header(order=order)
        if selected is not None:
            self.right_text(f"#{selected + 1} 실행 순서", 1490, 82, 17, colors.ORANGE)
        self._draw_order_rows(selected)

    def _header_matrix_limit(self):
        step = 1400 / (len(self.sizes) - 1)
        limit = min(100, step * 0.65)
        if self.orders is None and self.cost is not None:
            height = self._range_rect(0, 0)[3]
            limit = min(limit, height * 1.2)
        return limit

    def _draw_header(self, order=None, focus=None):
        count = len(self.sizes) - 1
        step = 1400 / count
        scale = self._header_matrix_limit() / max(self.sizes)
        if focus:
            left, right, mid, _ = focus
            self.rect(90 + left*step, 133, (right-left+1)*step, 105,
                      colors.BACKGROUND, colors.ORANGE, radius=0)
        for i in range(count):
            cx, cy = 90 + (i + 0.5) * step, 184
            width, height = self.sizes[i + 1] * scale, self.sizes[i] * scale
            accent = colors.BLUE if i % 2 == 0 else colors.YELLOW
            dimmed = False
            if focus:
                accent = colors.TEXT_MUTED
                if left <= i <= right:
                    accent = colors.YELLOW if i <= mid else colors.BLUE
                    if self.reuse:
                        stage, _ = self.reuse
                        dimmed = stage >= (1 if i <= mid else 2)
            if dimmed:
                accent = (65, 72, 82)
            self.centered_text(f"A{i}", cx, 108, 22, accent, True)
            self.rect(cx - width / 2, cy - height / 2, width, height,
                      colors.PANEL_DARK if dimmed else colors.PANEL, accent, radius=0)
            self.centered_text(f"{self.sizes[i]} × {self.sizes[i + 1]}", cx, 254, 18,
                               accent if dimmed else colors.TEXT)
            if i < count - 1 and order is not None:
                boundary_x = cx + step / 2
                pygame.draw.line(self.screen, colors.BORDER,
                                 self.view.point(boundary_x, 140),
                                 self.view.point(boundary_x, 230),
                                 max(1, self.view.length(1)))
                pygame.draw.circle(self.screen, colors.PANEL,
                                   self.view.point(boundary_x, 180), self.view.length(17))
                self.centered_text(i, boundary_x, 180, 18, colors.ORANGE, True)
                if order:
                    self.centered_text(f"{order.index(i) + 1}번째", boundary_x, 120, 15, colors.ORANGE)
            if focus and left <= i < right:
                ink = colors.ORANGE if i == mid else colors.YELLOW if i < mid else colors.BLUE
                if dimmed and i != mid:
                    ink = accent
                self.centered_text("×", cx + step/2, 184, 32 if i == mid else 23, ink, True)
        if focus and not self.reuse:
            for first, last, ink in ((left, mid, colors.YELLOW), (mid + 1, right, colors.BLUE)):
                if first < last:
                    self._group_parentheses(90 + first*step + 12, 130,
                                            (last-first+1)*step - 24, 108, ink)

    def _group_parentheses(self, x, y, width, height, color):
        thickness = max(1, self.view.length(2))
        pygame.draw.arc(self.screen, color, self.view.rect(x, y, 30, height),
                        pi/2, 3*pi/2, thickness)
        pygame.draw.arc(self.screen, color, self.view.rect(x + width - 30, y, 30, height),
                        -pi/2, pi/2, thickness)

    def _result_shape(self, left, right, cx, cy, maximum, color):
        scale = maximum / max(self.sizes)
        width, height = self.sizes[right+1]*scale, self.sizes[left]*scale
        self.rect(cx-width/2, cy-height/2, width, height, colors.PANEL, color, radius=0)

    def _draw_reuse(self, focus):
        left, right, mid, candidate = focus
        stage, t = self.reuse
        step = 1400 / (len(self.sizes)-1)
        positions = []
        for side, (first, last, ink) in enumerate(((left, mid, colors.YELLOW),
                                                  (mid+1, right, colors.BLUE)), 1):
            target = (90 + (first+last+1)*step/2, 184)
            positions.append(target)
            if stage < side:
                continue
            progress = t if stage == side else 1.0
            if first == last:
                source = target
            else:
                x, y, w, h = self._range_rect(first,last)
                source = x+w/2, y+h/2
            cx = source[0] + (target[0]-source[0])*progress
            cy = source[1] + (target[1]-source[1])*progress
            # 아래 원본 셀은 남기고 부분 결과의 복사본만 이동합니다.
            self._result_shape(first,last,cx,cy,self._header_matrix_limit(),ink)
            expression = self._expression(first,last)
            self._fitted_text(expression,cx,cy-72,max(100,(last-first+1)*step-30),20,ink)
            self.centered_text(f"{self.sizes[first]} × {self.sizes[last+1]}",cx,cy+68,18,ink)
            if stage < 4:
                self.centered_text(f"{self.cost[first][last]:,}",cx,cy+96,21,ink,True)
        multiply_x = 90+(mid+1)*step
        extra = self.sizes[left]*self.sizes[mid+1]*self.sizes[right+1]
        if stage >= 2:
            self.centered_text("×",multiply_x,184,32,colors.ORANGE,True)
        if stage == 3:
            self.centered_text(f"{extra:,}",multiply_x,280,24,colors.ORANGE,True)
            for px in ((positions[0][0]+multiply_x)/2, (positions[1][0]+multiply_x)/2):
                self.centered_text("+",px,280,24,colors.TEXT_MUTED)
        if stage == 4:
            values = (self.cost[left][mid], self.cost[mid+1][right], extra)
            sources = ((positions[0][0],280),(positions[1][0],280),(multiply_x,280))
            for value, source, ink in zip(values,sources,(colors.YELLOW,colors.BLUE,colors.ORANGE)):
                cx = source[0]+(800-source[0])*t
                cy = source[1]+(280-source[1])*t
                if t < 0.85:
                    self.centered_text(f"{value:,}",cx,cy,24,ink,True)
        if stage >= 5 or (stage == 4 and t >= 0.85):
            if self.decision is None:
                self.centered_text(f"{candidate:,}",800,280,28,colors.ORANGE,True)
            else:
                self._draw_candidate_motion(focus)

    def _draw_candidate_motion(self, focus):
        accepted, phase, t = self.decision
        if phase == 3:
            return
        left, right, _, candidate = focus
        x, y, w, h = self._range_rect(left, right)
        target = x+w*0.33, y+h*0.3
        if not accepted:
            target = target[0], y-8
        if phase == 1:
            cx, cy = 800+(target[0]-800)*t, 280+(target[1]-280)*t
            alpha = 255
        else:
            cx = target[0]+100*t
            cy = target[1]-(target[1]-max(110, target[1]-240))*t
            alpha = round(255*(1-t))
        ink = colors.GREEN if accepted else colors.ORANGE if phase == 1 else colors.RED
        size = 28+(min(25,h*0.33)-28)*t if accepted else 28
        image = self.font(size, True).render(f"{candidate:,}", True, ink)
        image.set_alpha(alpha)
        self.screen.blit(image, image.get_rect(center=self.view.point(cx,cy)))

    def _draw_order_rows(self, selected):
        self.text("#", 90, 285, 18, colors.TEXT_MUTED)
        self.text("경계 제거 순서", 155, 285, 18, colors.TEXT_MUTED)
        self.text("괄호 묶음", 455, 285, 18, colors.TEXT_MUTED)
        self.right_text("곱셈 횟수", 1480, 285, 18, colors.TEXT_MUTED)
        visible = self._visible_rows()
        for row, index in enumerate(range(self.scroll, min(len(self.orders), self.scroll + visible))):
            order, expression, cost = self.orders[index]
            y = 321 + row * 42
            if index == selected:
                self.rect(80, y - 6, 1410, 39, colors.PANEL, colors.BORDER, radius=0)
            ink = colors.GREEN if cost == self.best_cost else colors.TEXT
            self.text(index + 1, 90, y, 17, ink)
            sequence = " → ".join(map(str, order)) or "—"
            self.text(sequence, 155, y, 16, colors.TEXT_MUTED)
            self.text(expression, 455, y, 17, ink)
            self.right_text(f"{cost:,}", 1480, y, 19, ink, True)
        if len(self.orders) > visible:
            track = visible * 42
            thumb = max(20, track * visible / len(self.orders))
            offset = (track - thumb) * self.scroll / (len(self.orders) - visible)
            self.rect(1510, 312, 4, track, colors.PANEL, colors.PANEL, radius=0)
            self.rect(1510, 312 + offset, 4, thumb, colors.TEXT_MUTED, colors.TEXT_MUTED, radius=0)
