from math import pi

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class MatrixMultiplicationVisualizer(BaseVisualizer):
    def __init__(self, title="Matrix Multiplication", **kwargs):
        super().__init__(title, **kwargs)
        self.matrices = None

    def setup(self, data):
        self.msg_clear()
        self.set_data_info(data)
        self.matrices = None

    def start(self, a, b, c):
        self.matrices = a, b, c
        self.active = None
        self.completed = set()
        self.products = 0
        self.msg_phase("행렬 곱셈")
        self.msg_action("왼쪽 행과 오른쪽 열을 짝지어 결과 칸 하나를 계산한다.")
        self.msg_detail(f"A: {len(a)} × {len(a[0])}   B: {len(b)} × {len(b[0])}   C: {len(c)} × {len(c[0])}")
        self.wait(650)

    def accumulate(self, i, j, k):
        a, b, c = self.matrices
        self.active = i, j, k
        left, right, total = a[i][k], b[k][j], c[i][j]
        product = left * right
        self.products += 1
        self.msg_action(f"C[{i}][{j}] ← {total - product} + ({left}) × ({right}) = {total}")
        self.msg_detail(f"A의 {i}번 행과 B의 {j}번 열에서 {k}번 원소를 곱해 더한다.")
        self.msg_stats(f"곱셈 {self.products}회")
        self.wait(1000)
        if k == len(b) - 1 and not self.stopped():
            self.completed.add((i, j))
            self.section_end()

    def finish(self):
        self.active = None
        self.msg_phase("완료")
        self.msg_action("결과 행렬의 모든 칸을 계산했다.")
        self.msg_detail("")
        self.draw()

    def draw_content(self):
        self.text(self.title, 72, 45, 42, bold=True)
        if self.matrices is None:
            return
        widths = [len(m[0]) for m in self.matrices]
        height = max(map(len, self.matrices))
        cell = min(64, 1150 / sum(widths), 395 / height)
        gap = 94
        x = (1600 - (sum(widths) * cell + 2 * gap)) / 2
        center_y = 210 + height * cell / 2
        for index, (label, matrix, width) in enumerate(zip("ABC", self.matrices, widths)):
            y = center_y - len(matrix) * cell / 2
            self._draw_matrix(label, matrix, x, y, cell)
            x += width * cell
            if index < 2:
                self.centered_text("×="[index], x + gap / 2, center_y, 38, colors.TEXT_MUTED, True)
                x += gap

    def _draw_matrix(self, label, matrix, x, y, cell):
        rows, cols = len(matrix), len(matrix[0])
        accent = {"A": colors.BLUE, "B": colors.YELLOW, "C": colors.GREEN}[label]
        self.centered_text(f"{label}  ({rows} × {cols})", x + cols * cell / 2, y - 43, 23, accent, True)
        self._draw_parentheses(x, y, cols * cell, rows * cell, accent)
        for r, row in enumerate(matrix):
            for c, value in enumerate(row):
                ink = colors.TEXT
                outline = False
                if label == "C" and (r, c) in self.completed:
                    ink = colors.GREEN
                if self.active is not None:
                    i, j, k = self.active
                    if label == "A":
                        in_scope, outline = r == i, (r, c) == (i, k)
                    elif label == "B":
                        in_scope, outline = c == j, (r, c) == (k, j)
                    else:
                        in_scope = (r, c) == (i, j)
                    if in_scope:
                        ink = colors.ORANGE if outline or label == "C" else accent
                cx, cy = x + (c + 0.5) * cell, y + (r + 0.5) * cell
                if outline:
                    w, h = cell * 0.82, cell * 0.72
                    self.rect(cx - w / 2, cy - h / 2, w, h, colors.BACKGROUND, colors.ORANGE, radius=5)
                self.centered_text(value, cx, cy, min(26, cell * 0.36), ink, True)

    def _draw_parentheses(self, x, y, width, height, color):
        thickness = max(1, self.view.length(2))
        left = self.view.rect(x - 11, y, 34, height)
        right = self.view.rect(x + width - 23, y, 34, height)
        pygame.draw.arc(self.screen, color, left, pi / 2, 3 * pi / 2, thickness)
        pygame.draw.arc(self.screen, color, right, -pi / 2, pi / 2, thickness)
