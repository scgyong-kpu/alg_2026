import pygame

from pyvisalgo.core import colors
from pyvisalgo.core.visualizer import BaseVisualizer


DEFAULT_OFFSETS = [
    (1, -2), (2, -1), (2, 1), (1, 2),
    (-1, 2), (-2, 1), (-2, -1), (-1, -2),
]


class KnightsTourVisualizer(BaseVisualizer):
    def __init__(self, title="Knight's Tour", **kwargs):
        super().__init__(title, **kwargs)
        self.set_message_layout("side")
        self.size = 0
        self.method = ""
        self.board = []
        self.current = None
        self.trying = None
        self.candidates = []
        self.selected = None
        self.step = 0
        self.attempts = 0
        self.start = (0, 0)
        self.offsets = []
        self.path = []
        self.answer = []
        self.answer_attempt = None
        self.answer_method = ""
        self.showing_answer = False

    def setup(self, data):
        self.set_data_info(data)
        self.size = int(data.size)
        self.method = getattr(data, "method", "warnsdorff")
        self.start = tuple(getattr(data, "start", [0, 0]))
        self.offsets = [tuple(offset) for offset in getattr(data, "offsets", DEFAULT_OFFSETS)]
        self.answer, self.answer_attempt, self.answer_method = self._parse_answer(getattr(data, "answer", None))
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current = None
        self.trying = None
        self.candidates = []
        self.selected = None
        self.step = 0
        self.attempts = 0
        self.path = []
        self.showing_answer = False
        self.msg_phase("나이트 투어")
        self.msg_action(f"{self.size}x{self.size} 보드에서 시작한다.")
        self.msg_detail("나이트가 모든 칸을 한 번씩 방문하는 경로를 찾는다.")
        self._update_hint()
        self._update_stats()
        self.msg_path("")
        self.wait(700)

    def visit(self, x, y, step, attempts=0):
        self.showing_answer = False
        self.current = (x, y)
        self.trying = None
        self.candidates = []
        self.selected = None
        self.step = step
        self.attempts = attempts
        self.board[y][x] = step
        if len(self.path) >= step:
            self.path = self.path[: step - 1]
        self.path.append((x, y))
        self.msg_action(f"#{step}: ({x}, {y}) 칸을 방문한다.")
        self.msg_detail("방문한 칸은 다시 방문하지 않는다.")
        self._update_stats()
        self.wait(120)

    def try_dir(self, x, y, direction, attempts=0):
        self.showing_answer = False
        self.current = (x, y)
        self.trying = direction
        self.candidates = []
        self.selected = None
        self.attempts = attempts
        self.msg_action(f"({x}, {y})에서 {direction + 1}번째 방향을 시도한다.")
        self.msg_detail("시계 바늘처럼 현재 시도 중인 이동 방향을 표시한다.")
        self._update_stats()
        self.wait(60)

    def step_back(self, x, y, step, attempts=0):
        self.showing_answer = False
        self.current = (x, y)
        self.trying = None
        self.candidates = []
        self.selected = None
        self.step = step - 1
        self.attempts = attempts
        self.board[y][x] = 0
        if self.path and self.path[-1] == (x, y):
            self.path.pop()
        self.msg_action(f"({x}, {y})에서 되돌아간다.")
        self.msg_detail("이 칸 이후로는 경로를 완성할 수 없어 이전 칸으로 돌아간다.")
        self._update_stats()
        self.wait(90)

    def show_candidates(self, x, y, candidates, selected, attempts=0):
        self.showing_answer = False
        self.current = (x, y)
        self.trying = None
        self.candidates = list(candidates)
        self.selected = selected
        self.attempts = attempts
        if selected is None:
            self.msg_action(f"({x}, {y})에서 갈 수 있는 후보가 없다.")
            self.msg_detail("더 이상 진행할 수 없으므로 실패한다.")
        else:
            sx, sy = selected[1], selected[2]
            self.msg_action(f"후보 중 ({sx}, {sy}) 칸을 선택한다.")
            self.msg_detail("다음 후보 수가 가장 적은 칸을 먼저 방문한다.")
        self._update_stats()
        self.wait(650)

    def choose_candidate(self, x, y, candidates, selected, attempts=0):
        self.showing_answer = False
        self.current = (x, y)
        self.trying = None
        self.candidates = list(candidates)
        self.selected = selected
        self.attempts = attempts
        sx, sy = selected[1], selected[2]
        self.msg_action(f"({sx}, {sy}) 칸으로 이동하기로 결정한다.")
        self.msg_detail("후보 중 다음 이동 가능 칸 수가 가장 적은 곳을 선택한다.")
        self._update_stats()
        self.wait(650)

    def finish(self):
        self.trying = None
        self.candidates = []
        self.selected = None
        self.msg_phase("완료")
        self.msg_action("나이트 투어를 완성했다.")
        self.msg_detail("모든 칸을 정확히 한 번씩 방문했다.")
        self._update_stats()
        self.wait(1200)

    def show_answer(self):
        self.requested_action = None
        self.showing_answer = True
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.path = []
        for step, (x, y) in enumerate(self.answer, start=1):
            self.board[y][x] = step
            self.path.append((x, y))
        self.current = self.path[-1] if self.path else None
        self.trying = None
        self.candidates = []
        self.selected = None
        self.step = len(self.path)
        if self.answer_attempt is not None:
            self.attempts = self.answer_attempt
        self.msg_phase("준비된 해답")
        self.msg_action("완성된 나이트 투어 경로를 표시한다.")
        if self.answer_attempt is None:
            self.msg_detail(f"{self._method_label(self.answer_method)}로 준비한 해답이다.")
        else:
            self.msg_detail(f"{self._method_label(self.answer_method)} {self.answer_attempt}번째 시도에서 얻은 해답이다.")
        self._update_stats()
        self._update_hint()
        self.wait(1200)

    def fail(self):
        self.trying = None
        self.msg_phase("실패")
        self.msg_action("나이트 투어를 완성하지 못했다.")
        self.msg_detail("남은 후보가 없어 더 이상 진행할 수 없다.")
        self._update_stats()
        self.wait(1200)

    def stopped_by_user(self):
        self.msg_phase("중단")
        self.msg_action("다음 데이터로 넘어간다.")
        self.msg_detail("긴 backtracking 실행은 D를 눌러 건너뛸 수 있다.")
        self._update_stats()
        self.wait(300)

    def draw_content(self):
        self.text("Knight's Tour", 24, 18, 42, colors.TEXT, True)
        self.right_text("나이트가 모든 칸을 한 번씩 방문하는 경로를 찾는다.", 1576, 28, 22, colors.TEXT_MUTED)
        self._draw_board()

    def can_show_answer(self):
        return len(self.answer) == self.size * self.size

    def _parse_answer(self, answer):
        if isinstance(answer, dict):
            path = answer.get("path", [])
            attempt = answer.get("attempt")
            method = answer.get("method", "")
            return [tuple(point) for point in path], attempt, method
        if answer:
            return [tuple(point) for point in answer], None, ""
        return [], None, ""

    def _draw_board(self):
        if self.size <= 0:
            return
        left, top, right, bottom = 80, 110, 1040, 805
        board_size = min(right - left, bottom - top)
        cell = board_size / self.size
        origin_x = left + (right - left - board_size) / 2
        origin_y = top + (bottom - top - board_size) / 2

        for y in range(self.size):
            for x in range(self.size):
                self._draw_cell(origin_x, origin_y, cell, x, y, draw_value=False)

        self._draw_path(origin_x, origin_y, cell)
        self._draw_try_direction(origin_x, origin_y, cell)
        self._draw_candidates(origin_x, origin_y, cell)

        for y in range(self.size):
            for x in range(self.size):
                self._draw_cell_value(origin_x, origin_y, cell, x, y)

    def _draw_cell(self, origin_x, origin_y, cell, x, y, draw_value=True):
        value = self.board[y][x]
        base = colors.PANEL if (x + y) % 2 == 0 else colors.PANEL_DARK
        fill = base
        border = colors.BORDER
        if value > 0:
            age = max(0, min(8, self.step - value))
            shades = [
                (43, 96, 68),
                (40, 88, 64),
                (37, 80, 60),
                (34, 72, 56),
                (31, 64, 52),
                (29, 56, 48),
                (27, 50, 44),
                (25, 44, 40),
                (23, 38, 36),
            ]
            fill = shades[age]
            border = colors.GREEN
        if self.current == (x, y):
            fill = (82, 55, 30)
            border = colors.ORANGE

        px = origin_x + x * cell
        py = origin_y + y * cell
        self.rect(px, py, cell, cell, fill, border, 2)
        if value > 0 and draw_value:
            self._draw_cell_value(origin_x, origin_y, cell, x, y)

    def _draw_cell_value(self, origin_x, origin_y, cell, x, y):
        value = self.board[y][x]
        if value > 0:
            px = origin_x + x * cell
            py = origin_y + y * cell
            self.centered_text(value, px + cell / 2, py + cell / 2, max(12, min(30, cell * 0.38)), colors.TEXT, True)

    def _draw_path(self, origin_x, origin_y, cell):
        if len(self.path) < 2:
            return
        points = [
            self.view.point(origin_x + (x + 0.5) * cell, origin_y + (y + 0.5) * cell)
            for x, y in self.path
        ]
        if len(points) >= 2:
            pygame.draw.lines(self.screen, (132, 124, 70), False, points, self.view.length(2))
        if len(points) >= 2:
            pygame.draw.line(self.screen, (188, 123, 54), points[-2], points[-1], self.view.length(4))

    def _draw_try_direction(self, origin_x, origin_y, cell):
        if self.current is None or self.trying is None or not self.offsets:
            return
        x, y = self.current
        dx, dy = self.offsets[self.trying]
        cx = origin_x + (x + 0.5) * cell
        cy = origin_y + (y + 0.5) * cell
        ex = cx + dx * cell * 0.28
        ey = cy + dy * cell * 0.28
        pygame.draw.line(self.screen, colors.RED, self.view.point(cx, cy), self.view.point(ex, ey), self.view.length(4))
        pygame.draw.circle(self.screen, colors.RED, self.view.point(ex, ey), self.view.length(6))

    def _draw_candidates(self, origin_x, origin_y, cell):
        for direction, x, y, count in self.candidates:
            px = origin_x + x * cell
            py = origin_y + y * cell
            selected = self.selected is not None and direction == self.selected[0]
            deciding = self.selected is not None
            if deciding and not selected:
                fill = (37, 39, 35)
                border = (77, 78, 64)
                text_color = colors.TEXT_MUTED
            elif selected:
                fill = (82, 55, 30)
                border = colors.ORANGE
                text_color = colors.TEXT
            else:
                fill = (78, 68, 28)
                border = colors.YELLOW
                text_color = colors.TEXT
            margin = cell * 0.18
            self.rect(px + margin, py + margin, cell - 2 * margin, cell - 2 * margin, fill, border, 4)
            if selected:
                pygame.draw.circle(
                    self.screen,
                    colors.ORANGE,
                    self.view.point(px + cell / 2, py + cell / 2),
                    self.view.length(cell * 0.34),
                    self.view.length(4),
                )
            self.centered_text(count, px + cell / 2, py + cell / 2, max(12, min(26, cell * 0.34)), text_color, True)

    def _update_stats(self):
        lines = [
            f"방법: {self._method_label(self.method)}",
            f"크기: {self.size}x{self.size}",
            f"현재 단계: {self.step}",
        ]
        if self.showing_answer:
            if self.answer_method:
                lines.append(f"해답 방식: {self._method_label(self.answer_method)}")
            if self.answer_attempt is not None:
                lines.append(f"시도 횟수: {self.answer_attempt}")
        else:
            lines.append(f"시도 횟수: {self.attempts}")
        self.msg_stats("\n".join(lines))

    def _update_hint(self):
        if self.can_show_answer():
            self.msg_hint("A: 준비된 해답 보기  D: 다음 데이터  R: 다시 실행  Esc: 종료")
        else:
            self.msg_hint("D: 다음 데이터  R: 다시 실행  Esc: 종료")

    def _method_label(self, method):
        if method == "backtrack":
            return "Backtracking"
        if method == "warnsdorff":
            return "Warnsdorff"
        return method or "준비된 해답"
