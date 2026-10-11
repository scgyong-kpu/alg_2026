import math
import time

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class PlaneVisualizer(BaseVisualizer):
    """평면의 카메라만 조절한다. 데이터 좌표와 UI의 배율은 변경하지 않는다."""

    plane_rect = (70, 155, 1040, 390)
    fit_button = (1068, 163, 32, 32)

    def fit_plane(self, points):
        xs, ys = [p.x for p in points], [p.y for p in points]
        self.min_x, self.min_y = min(xs), min(ys)
        x, y, w, h = self.plane_rect
        width, height = w - 100, h - 90
        self.scale = min(width / max(1, max(xs) - min(xs)),
                         height / max(1, max(ys) - min(ys)))
        self.origin_x = x + w / 2 - (max(xs) - min(xs)) * self.scale / 2
        self.origin_y = y + h / 2 + (max(ys) - min(ys)) * self.scale / 2
        self.plane_fit = self.scale, self.origin_x, self.origin_y
        self.plane_zoom = 1.0
        self.plane_drag = None
        self.plane_motion_time = -math.inf
        self.plane_camera_animating = False
        self.plane_world = self.visible_world()

    def plane_screen_rect(self):
        return pygame.Rect(self.view.rect(*self.plane_rect))

    def _logical_mouse(self, position):
        return ((position[0] - self.view.origin_x) / self.view.scale,
                (position[1] - self.view.origin_y) / self.view.scale)

    def visible_world(self):
        x, y, w, h = self.plane_rect
        return (self.min_x + (x - self.origin_x) / self.scale,
                self.min_y + (self.origin_y - y - h) / self.scale,
                self.min_x + (x + w - self.origin_x) / self.scale,
                self.min_y + (self.origin_y - y) / self.scale)

    def reset_plane(self):
        self.scale, self.origin_x, self.origin_y = self.plane_fit
        self.plane_zoom = 1.0
        self.plane_drag = None
        self.plane_motion_time = time.monotonic()

    def _clamp_plane(self):
        x, y, w, h = self.plane_rect
        xmin, ymin, xmax, ymax = self.plane_world
        self.origin_x = min(x - (xmin - self.min_x) * self.scale,
                            max(x + w - (xmax - self.min_x) * self.scale, self.origin_x))
        self.origin_y = min(y + (ymax - self.min_y) * self.scale,
                            max(y + h + (ymin - self.min_y) * self.scale, self.origin_y))

    def ensure_visible(self, points, milliseconds=450):
        """필요한 점들이 보이도록 조정하되 자동으로 확대하지는 않는다."""
        points = list(points)
        if not points or self.stopped():
            return
        x, y, w, h = self.plane_rect
        margin = 20
        xmin, xmax = min(p.x for p in points), max(p.x for p in points)
        ymin, ymax = min(p.y for p in points), max(p.y for p in points)
        left = self.origin_x + (xmin - self.min_x) * self.scale
        right = self.origin_x + (xmax - self.min_x) * self.scale
        top = self.origin_y - (ymax - self.min_y) * self.scale
        bottom = self.origin_y - (ymin - self.min_y) * self.scale
        if x + margin <= left <= right <= x + w - margin and y + margin <= top <= bottom <= y + h - margin:
            return
        scale = max(self.plane_fit[0], min(self.scale,
                    (w - 2 * margin) / max(1, xmax - xmin),
                    (h - 2 * margin) / max(1, ymax - ymin)))
        ratio = scale / self.scale
        ox = x + w / 2 + (self.origin_x - x - w / 2) * ratio
        oy = y + h / 2 + (self.origin_y - y - h / 2) * ratio
        wxmin, wymin, wxmax, wymax = self.plane_world
        # 점을 포함하는 조건과 전체 영역 밖으로 이동하지 않는 조건을 함께 적용한다.
        min_ox = max(x + margin - (xmin - self.min_x) * scale,
                     x + w - (wxmax - self.min_x) * scale)
        max_ox = min(x + w - margin - (xmax - self.min_x) * scale,
                     x - (wxmin - self.min_x) * scale)
        min_oy = max(y + margin + (ymax - self.min_y) * scale,
                     y + h + (wymin - self.min_y) * scale)
        max_oy = min(y + h - margin + (ymin - self.min_y) * scale,
                     y + (wymax - self.min_y) * scale)
        target = scale, min(max_ox, max(min_ox, ox)), min(max_oy, max(min_oy, oy))
        start = self.scale, self.origin_x, self.origin_y
        elapsed = 0.0
        last_tick = time.monotonic()
        self.plane_camera_animating = True
        self.plane_drag = None
        try:
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
                progress = min(1.0, elapsed * 1000 / max(1, milliseconds))
                eased = progress * progress * (3 - 2 * progress)
                self.scale, self.origin_x, self.origin_y = (
                    a + (b - a) * eased for a, b in zip(start, target))
                self.plane_zoom = self.scale / self.plane_fit[0]
                self.plane_motion_time = now
                self.draw()
                if progress >= 1:
                    break
                self.clock.tick(60)
        finally:
            self.scale, self.origin_x, self.origin_y = target
            self.plane_zoom = scale / self.plane_fit[0]
            self._clamp_plane()
            self.plane_camera_animating = False
            self.plane_motion_time = time.monotonic()
        if not self.stopped():
            self.draw()

    def handle_event(self, event):
        if not hasattr(self, "plane_fit"):
            return
        if self.plane_camera_animating:
            return
        if event.type == pygame.WINDOWFOCUSLOST:
            self.plane_drag = None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.view.rect(*self.fit_button)).collidepoint(event.pos):
                self.reset_plane()
            elif self.plane_screen_rect().collidepoint(event.pos):
                self.plane_drag = self._logical_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.plane_drag = None
        elif event.type == pygame.MOUSEMOTION and self.plane_drag is not None:
            if not event.buttons[0]:
                self.plane_drag = None
                return
            x, y = self._logical_mouse(event.pos)
            self.origin_x += x - self.plane_drag[0]
            self.origin_y += y - self.plane_drag[1]
            self.plane_drag = x, y
            self._clamp_plane()
            self.plane_motion_time = time.monotonic()
        elif event.type == pygame.MOUSEWHEEL:
            position = pygame.mouse.get_pos()
            if not self.plane_screen_rect().collidepoint(position):
                return
            delta = getattr(event, "precise_y", event.y)
            if getattr(event, "flipped", False):
                delta = -delta
            zoom = min(16.0, max(1.0, self.plane_zoom * 1.15 ** max(-10, min(10, delta))))
            ratio = zoom / self.plane_zoom
            x, y = self._logical_mouse(position)
            self.origin_x = x + (self.origin_x - x) * ratio
            self.origin_y = y + (self.origin_y - y) * ratio
            self.scale *= ratio
            self.plane_zoom = zoom
            self._clamp_plane()
            self.plane_motion_time = time.monotonic()

    def draw_plane_controls(self):
        x, y, w, h = self.fit_button
        hover = pygame.Rect(self.view.rect(*self.fit_button)).collidepoint(pygame.mouse.get_pos())
        self.rect(x, y, w, h, colors.PANEL if hover else colors.BACKGROUND, radius=4)
        # 네 모서리의 괄호 모양으로 전체 보기 버튼을 표시한다.
        for cx, cy, sx, sy in ((x+7,y+7,1,1),(x+w-7,y+7,-1,1),
                              (x+7,y+h-7,1,-1),(x+w-7,y+h-7,-1,-1)):
            pygame.draw.lines(self.screen, colors.TEXT_MUTED, False,
                              [self.view.point(cx,cy+sy*6), self.view.point(cx,cy),
                               self.view.point(cx+sx*6,cy)], self.view.length(2))
        if hover:
            self.rect(x - 150, y + 4, 140, 28, colors.PANEL, radius=4)
            self.text("화면 맞춤", x - 140, y + 5, size=18)
        if self.plane_zoom <= 1.000001:
            return
        age = 0 if self.plane_drag is not None else time.monotonic() - self.plane_motion_time
        alpha = round(180 * max(0.0, min(1.0, (1.5 - age) / .6)))
        if not alpha:
            return
        xmin, ymin, xmax, ymax = self.plane_world
        vxmin, vymin, vxmax, vymax = self.visible_world()
        x, y, w, h = self.plane_rect
        layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        horizontal = (x + 8 + (vxmin - xmin) / (xmax - xmin) * (w - 16),
                      y + h - 7, (vxmax - vxmin) / (xmax - xmin) * (w - 16), 4)
        vertical = (x + w - 7, y + 8 + (ymax - vymax) / (ymax - ymin) * (h - 16),
                    4, (vymax - vymin) / (ymax - ymin) * (h - 16))
        for rect in (horizontal, vertical):
            pygame.draw.rect(layer, (*colors.TEXT_MUTED, alpha), self.view.rect(*rect),
                             border_radius=self.view.length(2))
        self.screen.blit(layer, (0, 0))
