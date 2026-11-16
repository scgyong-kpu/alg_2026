from math import inf

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class CoinChangeVisualizer(BaseVisualizer):
    coin_colors = (colors.YELLOW, colors.BLUE, colors.GREEN, colors.ORANGE,
                   (219, 153, 202), (120, 208, 208))

    def setup(self, data):
        self.hidden = getattr(self, "hidden", False)
        self.msg_clear()
        self.set_data_info(data)
        self.coins, self.amount = data.coins, data.amount
        self.coin_inks = {coin: self.coin_colors[i % len(self.coin_colors)]
                          for i, coin in enumerate(self.coins)}
        self.count = self.last_coin = None
        self.active = self.source = self.coin = self.motion = self.hovered = None
        self.candidate = self.previous_count = None
        self.completed = set()
        self.trace_path = []
        self.selected = []
        self.finished = False

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
        if key == pygame.K_RETURN and self.finished:
            return
        if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_PERIOD, pygame.K_KP_PERIOD):
            self.hovered = None
        super()._handle_key(key, mod)

    def initialize(self, count, last_coin):
        self.count, self.last_coin = count, last_coin
        self.active = 0
        self.completed.add(0)
        self.msg_phase("초기값")
        self.msg_action("금액 0은 동전 0개로 만들 수 있다.")
        self.msg_detail("나머지 금액은 아직 방법을 찾지 못해 ∞로 둔다.")
        self.wait(850)
        self.section_end()

    @staticmethod
    def _number(value):
        return "∞" if value == inf else str(value)

    def compare(self, money, coin, candidate):
        self.active, self.coin = money, coin
        self.source = money - coin if money >= coin else None
        self.previous_count, self.candidate = self.count[money], candidate
        self.previous_coins = self._combination(money) if candidate < self.previous_count else []
        self.msg_phase(f"금액 {money}")
        self.msg_action(f"동전 {coin}을 마지막에 더하는 경우를 확인한다.")
        if self.source is None:
            detail = f"{coin} > {money}: 이 동전은 사용할 수 없다."
        elif candidate == inf:
            detail = f"남은 금액 {self.source}을 만들 수 없다."
        elif candidate < self.previous_count:
            detail = f"{candidate} < {self._number(self.previous_count)}: 더 적은 동전으로 만들 수 있다."
        else:
            detail = f"{candidate} ≥ {self.previous_count}: 기존 조합을 유지한다."
        self.msg_detail(detail)
        self.wait(850 if candidate < self.previous_count else 550)

    def place(self):
        self.msg_action(f"금액 {self.source}의 조합에 동전 {self.coin}을 하나 더한다.")
        self.msg_detail(f"금액 {self.active}의 최소 동전 수를 {self.count[self.active]}로 갱신한다.")
        source_coins = self._combination(self.source)
        frames = max(2, round(26 / max(1, self.speed)))
        for frame in range(frames + 1):
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
            t = frame / frames
            self.motion = source_coins, t * t * (3 - 2 * t)
            self.wait(650 / frames)
        self.motion = None
        if not self.stopped() and not self.running_to_section and not self.is_max_speed():
            self.wait(300)

    def end_amount(self, money):
        self.active = money
        self.source = self.coin = self.candidate = None
        self.completed.add(money)
        self.msg_action(f"금액 {money}의 최소 동전 수: {self._number(self.count[money])}")
        self.msg_detail("")
        if not self.running_to_section and not self.is_max_speed():
            self.wait(280)
        self.section_end()

    def trace(self, money, coin):
        self.active, self.source, self.coin = money, money - coin, coin
        self.candidate = None
        if not self.trace_path:
            self.trace_path.append(money)
        self.trace_path.append(self.source)
        self.selected.insert(0, coin)
        self.msg_phase("동전 조합 복원")
        self.msg_action(f"마지막 동전 {coin}을 선택하고 금액 {self.source}로 이동한다.")
        self.msg_detail(f"{money} - {coin} = {self.source}")
        self.wait(850)

    def finish(self, count, selected):
        self.active = self.source = self.coin = self.candidate = None
        self.selected = selected
        self.finished = True
        self.msg_phase("완료")
        if count == inf:
            self.msg_action(f"목표 금액 {self.amount}을 정확히 만들 수 없다.")
            self.msg_detail("")
        else:
            self.msg_action(f"목표 금액 {self.amount}  |  최소 동전 {count}개")
            self.msg_detail("선택 동전: " + (" + ".join(map(str, selected)) or "없음"))
        self.draw()

    def _combination(self, money):
        if self.count[money] == inf:
            return []
        result = []
        while money:
            coin = self.last_coin[money]
            result.append(coin)
            money -= coin
        return result[::-1]

    def _cell(self, money):
        columns = min(12, self.amount + 1)
        rows = self.amount // columns + 1
        row, col = divmod(money, columns)
        dx = min(160, 1440 / columns)
        dy = min(180, (565 if self.hidden else 360) / rows)
        return 80 + col * dx, 254 + row * dy, dx - 5, dy - 5

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = None
            if self.finished or (self.paused and self.motion is None):
                for money in self.completed:
                    if pygame.Rect(self.view.rect(*self._cell(money))).collidepoint(event.pos):
                        self.hovered = money
                        break
        super().handle_event(event)

    def draw_content(self):
        self.text(self.title, 72, 40, 40, bold=True)
        if self.count is None:
            return
        for i, coin in enumerate(self.coins):
            x = 104 + i * 65
            active = coin == self.coin
            self._draw_coin(coin, x, 131, 23, active)
            if active:
                pygame.draw.line(self.screen, self.coin_inks[coin],
                                 self.view.point(x - 17, 162), self.view.point(x + 17, 162),
                                 self.view.length(3))
        self.right_text(f"목표 금액 {self.amount}", 1510, 112, 24, colors.TEXT, True)
        self._draw_summary()
        for money in range(self.amount + 1):
            border, fill = colors.BORDER, colors.PANEL_DARK
            if money in self.trace_path:
                border, fill = colors.GREEN, (29, 54, 42)
            if money == self.source:
                border, fill = colors.BLUE, (30, 49, 68)
            if money == self.active:
                border = colors.ORANGE
            if money == self.hovered or (self.finished and money == self.amount):
                border = colors.YELLOW
            if money == self.active and self.motion is not None:
                number, coins = self.previous_count, self.previous_coins
            else:
                number, coins = self.count[money], self._combination(money)
            self._draw_cell(money, *self._cell(money), number, coins, fill, border)
        if self.motion is not None:
            self._draw_motion()

    def _draw_summary(self):
        if self.hovered is not None:
            money = self.hovered
            coins = self._combination(money)
            suffix = " + ".join(map(str, coins)) if coins else (
                "만들 수 없음" if self.count[money] == inf else "동전 없음")
            line = f"C[{money}] = {self._number(self.count[money])}   |   {suffix}"
        elif self.candidate is not None:
            if self.source is None:
                line = f"{self.coin} > {self.active}"
            else:
                line = (f"C[{self.active} - {self.coin}] + 1 = {self._number(self.candidate)}"
                        f"   |   기존 C[{self.active}] = {self._number(self.previous_count)}")
        elif self.trace_path and not self.finished:
            line = f"{self.active} → {self.source}   |   선택: " + " + ".join(map(str, self.selected))
        elif self.finished:
            count = self.count[self.amount]
            line = ("정확히 만들 수 없음" if count == inf
                    else f"최소 {count}개   |   " + (" + ".join(map(str, self.selected)) or "동전 없음"))
        else:
            line = "C[금액] = 최소 동전 수"
        self.text(line, 82, 185, 23, colors.TEXT)

    def _draw_coin(self, coin, x, y, radius, active=False):
        center = self.view.point(x, y)
        radius_px = self.view.length(radius)
        ink = self.coin_inks[coin]
        pygame.draw.circle(self.screen, colors.PANEL, center, radius_px)
        pygame.draw.circle(self.screen, ink, center, radius_px, self.view.length(2 if active else 1))
        self.centered_text(coin, x, y, radius * 0.9, ink, True)

    def _draw_cell(self, money, x, y, w, h, number, coins, fill, border):
        self.rect(x, y, w, h, fill, border, radius=4)
        if money is not None:
            self.centered_text(money, x + w / 2, y + 15, 16, colors.TEXT_MUTED)
        ink = colors.TEXT_MUTED if number == inf else colors.TEXT
        self.centered_text(self._number(number), x + w / 2, y + 42, 24, ink, True)
        for i, coin in enumerate(coins[:7]):
            self._draw_coin(coin, *self._coin_slot(x, y, w, h, i))
        if len(coins) > 7:
            cx, cy, _ = self._coin_slot(x, y, w, h, 7)
            self.centered_text(f"+{len(coins) - 7}", cx, cy, 12, colors.TEXT_MUTED)

    @staticmethod
    def _coin_slot(x, y, w, h, index):
        radius = min(12, (w - 10) / 9, (h - 56) / 5)
        return (x + w / 2 + (index % 4 - 1.5) * 2.15 * radius,
                y + 64 + index // 4 * 2.15 * radius, radius)

    def _draw_motion(self):
        coins, t = self.motion
        x, y, w, h = self._cell(self.source)
        end_x, end_y, _, _ = self._cell(self.active)
        displayed = coins + [self.coin] if t == 1 else coins
        self._draw_cell(None, x + (end_x - x) * t, y + (end_y - y) * t,
                        w, h, len(displayed), displayed, colors.PANEL, colors.GREEN)
        if 0.25 < t < 1:
            f = (t - 0.25) / 0.75
            start_x = 104 + self.coins.index(self.coin) * 65
            target_x, target_y, radius = self._coin_slot(end_x, end_y, w, h, min(7, len(coins)))
            self._draw_coin(self.coin, start_x + (target_x - start_x) * f,
                            131 + (target_y - 131) * f, 23 + (radius - 23) * f, True)
