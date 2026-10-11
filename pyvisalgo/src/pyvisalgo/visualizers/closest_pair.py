import math
import time

import pygame

from ..core import colors
from .plane import PlaneVisualizer


class ClosestPairVisualizer(PlaneVisualizer):
    DEPTH_RECT_PADDING = 3
    plane_rect = (60, 100, 1480, 590)
    fit_button = (1500, 108, 32, 32)

    def setup(self, data):
        self.panel_hidden = getattr(self, "panel_hidden", False)
        self.plane_rect = (60, 20, 1480, 820) if self.panel_hidden else (60, 100, 1480, 590)
        self.cities = list(data.cities)
        self.best = None
        self.comparing = None
        self.comparisons = 0
        self.frames = []
        self.skip_to_top_strip = False
        self.top_strip_reached = False
        self.strip = None
        self.scanning = None
        self.grid_point = None
        self.distance_comparison = None
        self.distance_calculation = None
        self.x_sort = None
        self.set_data_info(data)
        self.fit_plane(self.cities)
        self.msg_phase("최근접 쌍")
        self.msg_action("도시를 평면에 배치한다.")
        self.msg_detail("같은 배율의 x, y 좌표에서 두 도시 사이의 거리를 비교한다.")
        self.msg_stats("거리 비교 0회")
        self.draw()

    def show_x_sort(self, sorted_cities):
        """x가 작은 도시부터 강조하며 새 index를 붙인다. 점은 이동하지 않는다."""
        original = list(self.cities)
        targets = {id(city): i for i, city in enumerate(sorted_cities)}
        if len(original) != len(sorted_cities) or set(targets) != {id(c) for c in original}:
            raise ValueError("정렬 전후에는 동일한 도시 객체가 있어야 합니다.")
        self.x_sort = {"targets": targets, "assigned": set(), "active": None}
        self.msg_action("정렬 전 입력 순서의 index를 확인한다.")
        self.msg_detail("점은 움직이지 않는다. 차례가 오기 전에는 입력 순서의 index를 유지한다.")
        try:
            self.ensure_visible(sorted_cities)
            self.wait(800)
            for index, city in enumerate(sorted_cities):
                if self.stopped():
                    break
                self.x_sort["active"] = id(city)
                self.x_sort["assigned"].add(id(city))
                self.msg_action(f"#{index} {city.name}: x = {city.x}")
                self.wait(160)
        finally:
            self.cities = list(sorted_cities)
            self.x_sort = None
        self.msg_action("x좌표 순 정렬을 마치고 index를 다시 설정한다.")
        self.msg_detail("#0부터 x좌표가 작은 순서로 번호를 붙인다. 도시의 좌표는 그대로이다.")
        self.wait(450)
        if not self.stopped():
            self.draw()

    def _point(self, index):
        p = self.cities[index]
        return (self.origin_x + (p.x - self.min_x) * self.scale,
                self.origin_y - (p.y - self.min_y) * self.scale)

    def _line(self, a, b, color, width=2):
        clip = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        pygame.draw.line(self.screen, color, self.view.point(*a),
                         self.view.point(*b), self.view.length(width))
        self.screen.set_clip(clip)

    def compare(self, first, second):
        self.distance_calculation = None
        self.comparing = (first, second)
        self.comparisons += 1
        a, b = self.cities[first], self.cities[second]
        self.msg_action(f"{a.name}과 {b.name}의 거리를 비교한다.")
        self.msg_stats(f"거리 비교 {self.comparisons}회")
        points = [a, b]
        if self.best:
            points.extend(self.cities[i] for i in self.best[:2])
        self.ensure_visible(points)
        self.wait(500)

    def show_distance(self, first, second, distance):
        """좌표, 좌표 차이, 제곱, 합, 제곱근을 순서대로 표시한다."""
        a, b = self.cities[first], self.cities[second]
        self.comparing = None
        self.distance_comparison = None
        self.best = None
        self.comparisons += 1
        self.distance_calculation = {"pair": (first, second, distance),
                                     "dx": a.x - b.x, "dy": a.y - b.y, "step": 0}
        self.msg_stats(f"거리 계산 {self.comparisons}회")
        descriptions = (
            ("두 도시의 좌표를 확인한다.", "좌표는 (x, y) 순서로 표시한다."),
            ("x좌표와 y좌표의 차이를 구한다.", "수평인 변의 길이는 |dx|, 수직인 변의 길이는 |dy|이다."),
            ("dx와 dy를 각각 제곱한다.", "좌표 차이가 음수여도 제곱하면 음수가 되지 않는다."),
            ("두 제곱을 더한다.", "피타고라스 정리에 따라 이 합은 거리의 제곱이다."),
            ("제곱근을 구해 두 점 사이의 거리를 얻는다.", "초록색 선이 직각삼각형의 빗변이다."),
        )
        for step, (action, detail) in enumerate(descriptions):
            if self.stopped():
                break
            self.distance_calculation["step"] = step
            self.msg_action(action)
            self.msg_detail(detail)
            self.wait(800)
        # Enter로 중간 단계를 건너뛰어도 마지막 식과 거리 표시는 같아야 한다.
        self.distance_calculation["step"] = 4
        self.best = (first, second, distance)
        if not self.stopped():
            self.draw()

    def _calculation_label(self, value, position, color):
        label = self.font(20, bold=True).render(value, True, color)
        rect = label.get_rect(center=self.view.point(*position))
        rect.clamp_ip(self.plane_screen_rect())
        padded = rect.inflate(self.view.length(12), self.view.length(8))
        background = pygame.Surface(padded.size, pygame.SRCALPHA)
        pygame.draw.rect(background, (*colors.BACKGROUND, 204), background.get_rect(),
                         border_radius=self.view.length(4))
        self.screen.blit(background, padded)
        self.screen.blit(label, rect)

    def _draw_distance_calculation(self):
        state = self.distance_calculation
        first, second, distance = state["pair"]
        a, b = self._point(first), self._point(second)
        corner = (a[0], b[1])
        dx, dy, step = state["dx"], state["dy"], state["step"]
        self.text("두 점의 좌표" if step == 0 else "거리 계산", 1160, 175, size=24, bold=True)
        for row, index in enumerate((first, second)):
            city = self.cities[index]
            self.text(f"#{index} {city.name}: ({city.x}, {city.y})",
                      1160, 220 + row * 34, size=19)
        if step == 0:
            return
        self._line(b, corner, colors.YELLOW, 3)
        self._line(corner, a, colors.BLUE, 3)
        self._calculation_label(f"|dx| = {abs(dx)}", ((b[0] + corner[0]) / 2, b[1] - 20), colors.YELLOW)
        self._calculation_label(f"|dy| = {abs(dy)}", (corner[0] + 70, (corner[1] + a[1]) / 2), colors.BLUE)
        # 직각 표시는 짧은 변보다 커지지 않도록 한다.
        size = min(12, abs(a[0] - b[0]) / 3, abs(a[1] - b[1]) / 3)
        if size > 0:
            sx = -1 if b[0] < corner[0] else 1
            sy = -1 if a[1] < corner[1] else 1
            inside = (corner[0] + sx * size, corner[1] + sy * size)
            self._line((inside[0], corner[1]), inside, colors.TEXT_MUTED)
            self._line(inside, (corner[0], inside[1]), colors.TEXT_MUTED)
        self.text(f"dx = {self.cities[first].x} - {self.cities[second].x} = {dx}", 1160, 310, size=19, color=colors.YELLOW)
        self.text(f"dy = {self.cities[first].y} - {self.cities[second].y} = {dy}", 1160, 344, size=19, color=colors.BLUE)
        if step >= 2:
            self.text(f"dx² = {dx * dx:,}", 1160, 395, size=22, color=colors.YELLOW)
            self.text(f"dy² = {dy * dy:,}", 1160, 429, size=22, color=colors.BLUE)
        total = dx * dx + dy * dy
        if step >= 3:
            self.text(f"dx² + dy² = {total:,}", 1160, 480, size=22)
        if step >= 4:
            self._line(a, b, colors.GREEN, 3)
            self._calculation_label(f"d = {distance:.3f}", ((a[0] + b[0]) / 2 - 55,
                                                           (a[1] + b[1]) / 2 - 25), colors.GREEN)
            self.text(f"sqrt({total:,})", 1160, 530, size=24)
            self.text(f"= {distance:.3f}", 1160, 565, size=28, color=colors.GREEN, bold=True)

    def closest(self, first, second, distance):
        self.best = (first, second, distance)
        self.comparing = None
        self.msg_action(f"최근접 거리: {distance:.3f}")
        self.wait(500)

    def compare_distances(self, current_pair, candidate_pair, prefer="smaller"):
        """두 (index, index, 거리) 쌍을 비교하고 선택된 쌍을 반환한다."""
        if prefer not in ("smaller", "larger"):
            raise ValueError("prefer는 smaller 또는 larger여야 합니다.")
        self.distance_calculation = None
        current, candidate = current_pair[2], candidate_pair[2]
        candidate_wins = candidate < current if prefer == "smaller" else candidate > current
        winner = candidate_pair if candidate_wins else current_pair
        self.comparing = None
        self.comparisons += 1
        self.distance_comparison = {"pairs": (current_pair, candidate_pair),
                                    "winner": int(candidate_wins), "progress": 0.0}
        self.msg_action("기존 쌍과 후보 쌍의 거리를 비교한다.")
        self.msg_detail("더 짧은 거리를 선택한다." if prefer == "smaller" else "더 긴 거리를 선택한다.")
        self.msg_stats(f"거리 비교 {self.comparisons}회")
        # 선택 결과는 진행률과 별개다. Enter, 최고속, 재시작에도 임시 표시를 정리한다.
        try:
            # 두 선의 끝점이 모두 보인 뒤 거리 숫자의 비교 연출을 시작한다.
            self.ensure_visible(self.cities[i] for pair in (current_pair, candidate_pair) for i in pair[:2])
            self.wait(750)
            self._animate_distance_comparison(1100)
        finally:
            self.best = winner
            self.distance_comparison = None
            self.comparing = None
        if current == candidate:
            self.msg_action(f"거리 {winner[2]:.3f}: 같은 거리이므로 기존 쌍을 유지한다.")
        else:
            self.msg_action(f"거리 {winner[2]:.3f}인 쌍을 선택한다.")
        if not self.stopped():
            self.draw()
        return winner

    def _animate_distance_comparison(self, milliseconds):
        elapsed = 0.0
        last_tick = time.monotonic()
        while not self.stopped():
            self._handle_events()
            if self.stopped() or self.is_max_speed() or self.running_to_section:
                break
            now = time.monotonic()
            delta = now - last_tick
            last_tick = now
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    delta = 1 / 60
                else:
                    self.draw()
                    self.clock.tick(60)
                    continue
            elapsed += delta * self.speed
            self.distance_comparison["progress"] = min(1.0, elapsed * 1000 / milliseconds)
            self.draw()
            if self.distance_comparison["progress"] >= 1.0:
                break
            self.clock.tick(60)

    def _draw_distance_pair(self, pair, color, occupied, alpha=255, pulse=1.0, ring=False):
        first, second, distance = pair
        a, b = self._point(first), self._point(second)
        layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        layer.set_clip(self.plane_screen_rect())
        pygame.draw.line(layer, (*color, alpha), self.view.point(*a),
                         self.view.point(*b), self.view.length(3))
        self.screen.blit(layer, (0, 0))
        layer.fill((0, 0, 0, 0))
        label = self.font(22, bold=True).render(f"{distance:.2f}", True, color)
        if pulse != 1.0:
            label = pygame.transform.smoothscale(label, (max(1, round(label.get_width() * pulse)),
                                                        max(1, round(label.get_height() * pulse))))
        label.set_alpha(alpha)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        nx, ny = (-(b[1] - a[1]) / length, (b[0] - a[0]) / length) if length else (0, -1)
        bounds = self.plane_screen_rect()
        for offset in (22, -22, 45, -45, 70, -70):
            rect = label.get_rect(center=self.view.point(mx + nx * offset, my + ny * offset))
            padded = rect.inflate(self.view.length(16), self.view.length(10))
            if bounds.contains(padded) and not any(padded.colliderect(r) for r in occupied):
                break
        else:
            rect = label.get_rect(center=self.view.point(mx, my))
            rect.clamp_ip(bounds)
            padded = rect.inflate(self.view.length(16), self.view.length(10))
        pygame.draw.rect(layer, (*colors.BACKGROUND, round(alpha * 0.8)), padded,
                         border_radius=self.view.length(4))
        layer.blit(label, rect)
        if ring:
            pygame.draw.ellipse(layer, (*color, alpha),
                                padded.inflate(self.view.length(8), self.view.length(8)),
                                self.view.length(2))
        self.screen.blit(layer, (0, 0))
        occupied.append(padded)

    def _draw_distance_comparison(self, occupied):
        state = self.distance_comparison
        progress = state["progress"]
        # 앞부분은 선택을 강조하고, 뒷부분은 탈락한 선과 숫자를 지운다.
        fade = max(0.0, (progress - 0.35) / 0.65)
        pulse = 1.0 + 0.16 * math.sin(math.pi * progress)
        for i, (pair, color) in enumerate(zip(state["pairs"], (colors.GREEN, colors.ORANGE))):
            chosen = i == state["winner"]
            self._draw_distance_pair(pair, color, occupied,
                                     alpha=255 if chosen else round(255 * (1 - fade)),
                                     pulse=pulse if chosen else 1.0,
                                     ring=chosen and progress > 0)
        current, candidate = (pair[2] for pair in state["pairs"])
        relation = "<" if current < candidate else ">" if current > candidate else "="
        if not self.panel_hidden:
            self.text(f"{current:.2f} {relation} {candidate:.2f}", 650, 42, size=22, bold=True)

    def finish(self):
        self.skip_to_top_strip = False
        self.comparing = None
        self.msg_action("최근접 쌍 탐색을 마쳤다.")
        self.draw()

    def push(self, left, right):
        """x순 배열의 [left, right]를 표시한다. 양 끝을 모두 포함한다."""
        self.frames.append({"left": left, "right": right, "mid": None,
                            "results": [], "best": self.best,
                            "strip": self.strip, "scanning": self.scanning,
                            "grid_point": self.grid_point})
        self.best = None
        self.distance_calculation = None
        self.comparing = None
        self.strip = None
        self.scanning = None
        self.grid_point = None
        self.msg_action(f"#{left} ~ #{right}에서 최근접 쌍을 찾는다.")
        self.msg_path(f"depth {len(self.frames)}")
        self.wait(500)

    def split(self, mid):
        """mid는 왼쪽 부분의 마지막 index이며, 오른쪽은 mid+1부터이다."""
        self.frames[-1]["mid"] = mid
        self.msg_action(f"#{mid}까지 왼쪽, #{mid + 1}부터 오른쪽으로 나눈다.")
        self.wait(500)
        self.section_end()

    def show_base_case(self, count):
        if count <= 3:
            self.msg_action(f"도시 {count}개: 완전 탐색으로 최근접 쌍을 찾는다.")
            self.msg_detail("3개 이하의 작은 구간은 더 나누지 않고 brute_force로 처리한다.")
        else:
            self.msg_action(f"도시 {count}개: 완전 탐색을 하지 않는다.")
            self.msg_detail("brute_force는 3개 이하에서만 사용한다. 이 구간은 분할 정복(D&C)으로 처리한다.")
        self.wait(600)

    def show_left_result(self, result):
        """완료한 왼쪽 결과를 부모 프레임에 보관해 오른쪽 탐색 중에도 표시한다."""
        self.frames[-1]["results"] = [result]
        self.msg_action("왼쪽 부분 구간의 탐색을 마쳤다.")
        self.msg_detail("왼쪽 결과를 표시해 둔 채 오른쪽 부분 구간을 탐색한다.")
        self.wait(600)

    def show_results(self, left_result, right_result):
        """각 결과는 (첫 index, 둘째 index, 거리), 쌍이 없으면 None이다."""
        self.frames[-1]["results"] = [left_result, right_result]
        candidates = [r for r in (left_result, right_result) if r is not None]
        self.best = min(candidates, key=lambda r: r[2]) if candidates else None
        self.comparing = None
        self.msg_action("좌우 부분에서 찾은 최근접 쌍을 비교한다.")
        self.wait(600)
        if left_result is not None and right_result is not None and not self.stopped():
            # 좌우 결과도 완전 탐색에서 사용한 두 선과 거리 숫자 비교로 보여줍니다.
            # 같은 거리이면 먼저 전달한 왼쪽 쌍을 유지합니다.
            self.compare_distances(left_result, right_result, prefer="smaller")
        self.section_end()

    def pop(self):
        frame = self.frames.pop()
        self.best = frame["best"]
        self.strip = frame["strip"]
        self.scanning = frame["scanning"]
        self.grid_point = frame["grid_point"]
        self.comparing = None
        self.msg_path(f"depth {len(self.frames)}")
        self.draw()

    def set_strip(self, indices, split_x, distance):
        """indices는 후보 index, distance는 strip 진입 시 좌우 결과의 최솟값이다."""
        self.strip = {"indices": list(indices), "x": split_x, "d": distance}
        self.scanning = None
        self.grid_point = None
        self.comparing = None
        if len(self.frames) == 1:
            self.top_strip_reached = True
            if self.skip_to_top_strip:
                self.skip_to_top_strip = False
                self.msg_log("depth 1 strip 도착")
        self.msg_action(f"경계에서 거리 {distance:.3f} 이내의 strip을 확인한다.")
        self.wait(2000)
        self.section_end()

    def scan(self, first, second=None, distance=None):
        self.scanning = (first, second, distance)
        if self.grid_point is not None:
            self.grid_point = first
        self.comparing = None
        self.msg_action(f"#{first}에서 다음 strip 후보를 확인한다.")
        if second is not None:
            # 같은 x좌표도 양쪽에 나뉠 수 있으므로 x값이 아니라 index로 판단한다.
            mid = self.frames[-1]["mid"]
            same_side = (first <= mid) == (second <= mid)
            self.msg_detail("같은 부분의 두 점은 이미 처리했으므로 제외한다." if same_side
                            else "반대 부분의 점이므로 거리 비교 후보이다.")
        else:
            self.msg_detail("후보 배열에서 현재 점 뒤에 있는 점들을 차례로 살펴본다.")
        self.wait(450)

    def stop_scan(self, first, second, distance):
        self.scanning = (first, second, distance)
        self.comparing = None
        self.msg_action("y좌표 차이가 현재 최근접 거리 이상이므로 탐색을 멈춘다.")
        self.msg_detail("이후 후보는 더 멀리 있으므로 거리 계산이 필요 없다.")
        self.wait(500)
        self.section_end()

    def show_grid(self, first):
        """분할 경계를 중앙에 두고 현재 최소거리로 4열 2행 격자를 표시한다."""
        if self.strip is None:
            raise ValueError("set_strip() 이후에 show_grid()를 호출해야 합니다.")
        self.grid_point = first
        self.msg_detail("현재 최소거리를 d로 두고 한 변 d/2인 8칸을 표시한다. 각 칸에는 최대 한 점이다.")
        self.wait(500)

    def hide_grid(self):
        self.grid_point = None
        self.draw()

    def _draw_grid(self):
        if self.grid_point is None or self.strip is None:
            return
        # strip 후보 범위는 진입 시 거리로 유지하되, 격자는 현재 최소거리로
        # 줄입니다. 거리 비교에서 best가 갱신되면 다음 그리기부터 반영됩니다.
        # p를 중심에 두면 경계를 가로지르는 칸이 생기므로 분할 경계를 중앙에 둔다.
        distance = self.best[2] if self.best is not None else self.strip["d"]
        d = distance * self.scale
        x = self.origin_x + (self.strip["x"] - self.min_x) * self.scale
        _, y = self._point(self.grid_point)
        for column in range(5):
            gx = x - d + column * d / 2
            self._line((gx, y), (gx, y - d), colors.TEXT_MUTED)
        for row in range(3):
            gy = y - row * d / 2
            self._line((x - d, gy), (x + d, gy), colors.TEXT_MUTED)

    def _draw_strip(self):
        if not self.strip:
            return
        x = self.origin_x + (self.strip["x"] - self.min_x) * self.scale
        d = self.strip["d"] * self.scale
        _, top, _, height = self.plane_rect
        self._outline((x - d, top, 2 * d, height), colors.ORANGE)
        self._line((x, top), (x, top + height), colors.TEXT_MUTED)
        mid = self.frames[-1]["mid"]
        for i in self.strip["indices"]:
            color = colors.YELLOW if i <= mid else colors.BLUE
            pygame.draw.circle(self.screen, color, self.view.point(*self._point(i)), self.view.length(9), self.view.length(2))
        if self.scanning:
            p, q, distance = self.scanning
            x, y = self._point(p)
            self.text("p", x - 20, y - 30, size=20, color=colors.ORANGE)
            if q is not None:
                xq, yq = self._point(q)
                self.text("q", xq - 20, yq - 30, size=20, color=colors.ORANGE)
            if distance is not None:
                cutoff = y - distance * self.scale
                self._line((x - d, cutoff), (x + d, cutoff), colors.RED)

    def _region(self, left, right):
        points = [self._point(i) for i in range(left, right + 1)]
        xs, ys = zip(*points)
        return min(xs) - 15, min(ys) - 20, max(xs) - min(xs) + 30, max(ys) - min(ys) + 40

    def _outline(self, region, color, fill=None):
        rect = region if isinstance(region, pygame.Rect) else pygame.Rect(self.view.rect(*region))
        clipped = rect.clip(self.plane_screen_rect())
        if fill and clipped.width and clipped.height:
            surface = pygame.Surface(clipped.size, pygame.SRCALPHA)
            surface.fill((*fill, 30))
            self.screen.blit(surface, clipped)
        clip = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        pygame.draw.rect(self.screen, color, rect, self.view.length(2))
        self.screen.set_clip(clip)

    def _frame_rect(self, left, right, depth):
        rect = pygame.Rect(self.view.rect(*self._region(left, right)))
        depth_difference = max(0, len(self.frames) - 1 - depth)
        padding = self.view.length(self.DEPTH_RECT_PADDING * depth_difference)
        rect.inflate_ip(2 * padding, 2 * padding)
        # 부모의 분할 경계를 넘어 확장하면 같은 깊이의 좌우 구간이
        # 겹칩니다. 모든 상위 경계에서 자기 편의 영역 안으로 제한합니다.
        for parent in self.frames[:depth]:
            mid = parent["mid"]
            if mid is None:
                continue
            boundary_x = (self._point(mid)[0] + self._point(mid + 1)[0]) / 2
            boundary = self.view.point(boundary_x, 0)[0]
            if right <= mid:
                rect.width = max(0, min(rect.right, boundary) - rect.left)
            elif left > mid:
                edge = max(rect.left, boundary)
                rect.width = max(0, rect.right - edge)
                rect.left = edge
        return rect

    def _draw_overlays(self):
        for depth, frame in enumerate(self.frames):
            left, right, mid = frame["left"], frame["right"], frame["mid"]
            self._outline(self._frame_rect(left, right, depth), colors.BORDER)
            if mid is not None:
                for side, (bounds, color) in enumerate(zip(
                        ((left, mid), (mid + 1, right)), (colors.YELLOW, colors.BLUE))):
                    result = frame["results"][side] if side < len(frame["results"]) else None
                    # 배경색은 현재 구간의 좌우 박스에만 적용합니다.
                    # 상위 구간은 완료 여부와 관계없이 양쪽 테두리를 유지합니다.
                    # 대기 중인 반대쪽도 표시하되, 배경색은 넣지 않습니다.
                    current = depth == len(self.frames) - 1
                    self._outline(self._frame_rect(*bounds, depth + 1),
                                  color if current else colors.BORDER,
                                  color if current else None)
                    if result:
                        self._line(self._point(result[0]), self._point(result[1]), color, 3)

    def _handle_key(self, key, mod=0):
        if key == pygame.K_t:
            if not self.top_strip_reached:
                self.skip_to_top_strip = True
                self.running_to_section = False
                self.pause_after_section = False
                self.paused = False
                self.step_requested = False
                self.msg_log("depth 1 strip까지 진행")
            else:
                self.msg_log("depth 1 strip에 이미 도착함")
        elif key == pygame.K_h:
            self.panel_hidden = not self.panel_hidden
            self.draw()
        else:
            super()._handle_key(key, mod)

    def is_max_speed(self):
        # 계산은 생략하지 않고, 최상위 strip 이전의 대기와 연출만 건너뜁니다.
        return getattr(self, "skip_to_top_strip", False) or super().is_max_speed()

    def _update_plane_layout(self):
        # 카메라 이동 연출 중에는 영역 변경을 미뤄 연출의 목표 좌표를 유지합니다.
        if self.plane_camera_animating:
            return
        width = 1040 if self.distance_calculation else 1480
        target = (60, 20, width, 820) if self.panel_hidden else (60, 100, width, 590)
        if target == self.plane_rect:
            return
        x, y, w, h = self.plane_rect
        center_x = self.min_x + (x + w / 2 - self.origin_x) / self.scale
        center_y = self.min_y + (self.origin_y - y - h / 2) / self.scale
        zoom = self.plane_zoom
        self.plane_rect = target
        self.fit_plane(self.cities)
        self.plane_zoom = zoom
        self.scale *= zoom
        x, y, w, h = target
        self.origin_x = x + w / 2 - (center_x - self.min_x) * self.scale
        self.origin_y = y + h / 2 + (center_y - self.min_y) * self.scale
        self._clamp_plane()

    def _draw_messages(self):
        if self.panel_hidden:
            self.text("H: 설명 표시", 60, 862, 18, colors.TEXT_MUTED)
            self.text("T: depth 1 strip", 650, 862, 18, colors.TEXT_MUTED)
            if self.distance_comparison:
                current, candidate = (pair[2] for pair in self.distance_comparison["pairs"])
                relation = "<" if current < candidate else ">" if current > candidate else "="
                self.text(f"{current:.2f} {relation} {candidate:.2f}",
                          300, 860, 22, colors.TEXT, True)
            return
        self.rect(60, 710, 1480, 140, colors.PANEL_DARK, colors.BORDER, 8)
        self.text(self.messages["phase"], 80, 723, 20, colors.BLUE, True)
        self.text(self.messages["dataset"], 360, 723, 18, colors.TEXT_MUTED)
        self.text(self.messages["stats"], 1000, 723, 18, colors.TEXT_MUTED)
        if self.log_lines:
            self.text(self.log_lines[-1], 1280, 723, 18, colors.TEXT_MUTED)
        self.text(self.messages["action"], 80, 751, 24, colors.TEXT, True)
        self.text(self.messages["detail"], 80, 787, 19, colors.TEXT_MUTED)
        if self.frames:
            path = " > ".join(f"depth {i + 1}: #{f['left']}~#{f['right']}"
                              for i, f in list(enumerate(self.frames))[-2:])
            self.text(path, 80, 819, 17, colors.TEXT_MUTED)
            results = self.frames[-1]["results"]
            labels = [f"{side}: {r[2]:.3f}" for side, r in
                      zip(("왼쪽", "오른쪽"), results) if r is not None]
            self.text(" / ".join(labels), 950, 819, 17, colors.TEXT_MUTED)
        self.text(self.messages["hint"] + "  H: 설명 숨김  T: depth 1 strip",
                  60, 862, 16, colors.TEXT_MUTED)

    def draw_content(self):
        if not hasattr(self, "cities"):
            return
        self._update_plane_layout()
        self.fit_button = (self.plane_rect[0] + self.plane_rect[2] - 40,
                           self.plane_rect[1] + 8, 32, 32)
        if not self.panel_hidden:
            self.text("Closest Pair", 60, 35, size=30, bold=True)
            self.text("비교", 1190, 42, size=18, color=colors.ORANGE)
            self.text("최근접 쌍", 1330, 42, size=18, color=colors.GREEN)
        self._draw_overlays()
        old_clip = self.screen.get_clip()
        self.screen.set_clip(self.plane_screen_rect())
        self._draw_strip()
        self._draw_grid()
        self.screen.set_clip(old_clip)
        if self.best and self.distance_comparison is None and self.distance_calculation is None:
            self._line(self._point(self.best[0]), self._point(self.best[1]), colors.GREEN, 3)
        if self.comparing:
            self._line(self._point(self.comparing[0]), self._point(self.comparing[1]), colors.ORANGE, 3)
        occupied = [pygame.Rect(self.view.rect(*self._point(i), 1, 1)).inflate(
                    self.view.length(16), self.view.length(16)) for i in range(len(self.cities))]
        label_bounds = self.plane_screen_rect()
        for i, city in enumerate(self.cities):
            x, y = self._point(i)
            if not label_bounds.collidepoint(self.view.point(x, y)):
                continue
            clip = self.screen.get_clip()
            self.screen.set_clip(label_bounds)
            color = colors.TEXT
            if self.x_sort:
                color = colors.GREEN if id(city) in self.x_sort["assigned"] else colors.TEXT_MUTED
                if id(city) == self.x_sort["active"]:
                    color = colors.YELLOW
                    pygame.draw.circle(self.screen, color, self.view.point(x, y),
                                       self.view.length(11), self.view.length(2))
            pygame.draw.circle(self.screen, color, self.view.point(x, y), self.view.length(5))
            self.screen.set_clip(clip)
            name = f"#{i} {city.name}"
            if self.x_sort:
                name = (f"#{self.x_sort['targets'][id(city)]} {city.name}"
                        if id(city) in self.x_sort["assigned"] else f"#{i} {city.name}")
            if self.distance_calculation and i in self.distance_calculation["pair"][:2]:
                name += f" ({city.x}, {city.y})"
            label = self.font(14).render(name, True, color)
            # 점과 앞서 배치한 이름을 피하며, 가까운 위치부터 후보를 확인한다.
            for offset_y in (-18, 8, -36, 26, -54, 44):
                for on_right in (True, False):
                    rect = label.get_rect()
                    sx, sy = self.view.point(x + (9 if on_right else -9), y + offset_y)
                    if on_right:
                        rect.topleft = sx, sy
                    else:
                        rect.topright = sx, sy
                    if label_bounds.contains(rect) and not any(rect.colliderect(r) for r in occupied):
                        self.screen.blit(label, rect)
                        occupied.append(rect.inflate(self.view.length(3), self.view.length(3)))
                        break
                else:
                    continue
                break
        if self.distance_calculation:
            self._draw_distance_calculation()
        elif self.distance_comparison:
            self._draw_distance_comparison(occupied)
        elif self.best:
            self._draw_distance_pair(self.best, colors.GREEN, occupied)
        self.draw_plane_controls()
