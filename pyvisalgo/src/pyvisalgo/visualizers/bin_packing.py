"""Show how each bin packing strategy inspects and fills bins."""

from colorsys import hls_to_rgb
from random import Random

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


SELECTION_REASONS = {
    "First Fit": "첫 적합",
    "Next Fit": "현재 통",
    "Best Fit": "가장 작은 여유",
    "Worst Fit": "가장 큰 여유",
}


class BinPackingVisualizer(BaseVisualizer):
    explanation_hidden = False
    comparison_page_size = 60
    capacity_label_width = 32

    def setup(self, data, strategy):
        if data is not getattr(self, "data", None):
            self.item_colors = self._pastel_colors(len(data.array))
        self.data = data
        self.items = data.array
        self.capacity = data.capacity
        self.strategy = strategy
        self.dataset_name = getattr(data, "_dataset_name", "")
        self.bins = []
        self.placed_items = []
        self.comparison_bins = None
        self.comparison_items = {}
        self.comparison_selected = {}
        self.comparison_opened = set()
        self.comparison_browse = False
        self.processed = 0
        self.current = None
        self.candidate_count = 0
        self.checking = None
        self.selected = None
        self.page = 0
        self.motion = None
        self.comparison_fade = None
        self.queue_motion = None
        self.status = f"{self.dataset_name} · 통 용량 {self.capacity}"

    @staticmethod
    def _pastel_colors(count):
        rng = Random()
        offset = rng.random()
        palette = []
        used_colors = set()
        for i in range(count):
            hue = (offset + i / count) % 1
            while True:
                rgb = hls_to_rgb(hue, rng.uniform(0.74, 0.82), rng.uniform(0.48, 0.66))
                color = tuple(round(channel * 255) for channel in rgb)
                if color not in used_colors:
                    break
                hue = rng.random()
            used_colors.add(color)
            palette.append(color)
        rng.shuffle(palette)
        return palette

    def start(self, bins):
        self.bins = bins
        self.wait(500)

    def start_comparison(self, bins):
        self.comparison_bins = bins
        self.comparison_items = {strategy: [] for strategy in bins}
        self.wait(500)

    def place_comparison(self, placements):
        size = self.items[self.current]
        self.comparison_selected = {}
        self.comparison_opened = set()
        for strategy, (index, opened) in placements.items():
            if opened:
                self.comparison_items[strategy].append([])
                self.comparison_opened.add(strategy)
            self.comparison_items[strategy][index].append(self.current)
            self.comparison_selected[strategy] = index
        self.page = max(self.comparison_selected.values()) // self.comparison_page_size
        self.comparison_browse = False
        self.status = f"물건 {size} · 각 전략이 선택한 통으로 이동 중"
        self._animate("comparison_fade", 250)
        self._animate("motion", 320)
        self.processed = self.current + 1
        self.current = None
        opened_count = len(self.comparison_opened)
        self.status = f"물건 {size} 배치 · {opened_count}개 전략에서 새 통을 열었다."
        self.wait(370)
        self.section_end()

    def start_item(self, index):
        self.current = index
        self.candidate_count = len(self.bins)
        self.checking = None
        self.selected = None
        self.status = f"크기 {self.items[index]}인 물건을 넣을 통을 찾는다."
        self._animate("queue_motion", 240)
        self.wait(120)

    def inspect_bin(self, index, free):
        if self.is_max_speed() or self.running_to_section:
            return
        self.checking = index
        self._show_bin(index)
        size = self.items[self.current]
        relation = "<" if free < size else "≥"
        self.status = f"통 {index + 1} 검사 · 남은 공간 {free} {relation} 물건 {size}"
        self.wait(240)

    def place_item(self, index, opened):
        size = self.items[self.current]
        if opened:
            self.placed_items.append([])
        self.placed_items[index].append(self.current)
        self.checking = None
        self.selected = index
        self._show_bin(index)
        free = self.bins[index].free
        decision = "새로 열기" if opened else SELECTION_REASONS[self.strategy]
        self.status = f"통 {index + 1} {decision} · 남은 공간 {free + size} → {free}"
        self._animate("motion", 360)
        self.processed = self.current + 1
        self.current = None
        self.wait(280)
        self.section_end()

    def _animate(self, attribute, duration):
        frames = max(2, min(12, round(duration * 0.06 / self.speed)))
        for frame in range(frames):
            if self.stopped() or self.is_max_speed() or self.running_to_section:
                break
            setattr(self, attribute, frame / frames)
            self.wait(duration / frames)
        setattr(self, attribute, None)

    def finish(self, results):
        self.checking = None
        self.status = "결과 · " + "  /  ".join(f"{name} {count}개" for name, count in results.items())
        self.draw()

    def _handle_key(self, key, mod=0):
        if key == pygame.K_h:
            if self.comparison_bins is None:
                old_columns = self._single_layouts()[-1][1]
                first_bin = self.page * old_columns
            self.explanation_hidden = not self.explanation_hidden
            if self.comparison_bins is None:
                columns = self._single_layouts()[-1][1]
                self.page = min(first_bin // columns, self._page_count() - 1)
                focused = self.checking if self.checking is not None else self.selected
                if focused is not None:
                    self._show_bin(focused)
        elif key == pygame.K_TAB:
            self.requested_action = "next_strategy"
        elif key == pygame.K_r and mod & pygame.KMOD_SHIFT:
            self.requested_action = "random_items"
        elif key == pygame.K_PAGEUP:
            self.comparison_browse = True
            self.page = max(0, self.page - 1)
        elif key == pygame.K_PAGEDOWN:
            self.comparison_browse = True
            self.page = min(self._page_count() - 1, self.page + 1)
        else:
            super()._handle_key(key, mod)

    def _page_count(self):
        if self.comparison_bins is not None:
            largest = max(map(len, self.comparison_bins.values()), default=0)
            return max(1, (largest + self.comparison_page_size - 1) // self.comparison_page_size)
        columns = self._single_layouts()[-1][1]
        overflow = max(0, len(self.bins) - columns * 3)
        return 1 + (overflow + columns - 1) // columns

    def _show_bin(self, index):
        columns = self._single_layouts()[-1][1]
        start = self.page * columns
        if index < start:
            self.page = index // columns
        elif index >= start + columns * 3:
            self.page = index // columns - 2

    def _single_layouts(self):
        bottom = 878 if self.explanation_hidden else 825
        available_height = bottom - 130
        label_space = 52
        full_height = available_height - label_space
        layouts = (
            (full_height, 1),
            (full_height * 0.75, 1),
            (available_height / 2 - label_space, 2),
            (available_height / 3 - label_space, 3),
        )
        result = []
        for height, row_count in layouts:
            gap = 4 if row_count == 1 else 2
            column_width = height / 10 + gap
            result.append((height, int(1490 // column_width), column_width, row_count))
        return result

    def _bin_rect(self, index):
        layouts = self._single_layouts()
        scroll_columns = layouts[-1][1]
        for height, columns, column_width, row_count in layouts:
            if len(self.bins) <= columns * row_count:
                break
        width = height / 10
        row, column = divmod(index - self.page * scroll_columns, columns)
        x = 55 + column * column_width + (column_width - width) / 2
        return x, 130 + row * (height + 52) + 26, width, height

    def _draw_item(self, index, x, y, width, height, alpha=255):
        if alpha == 0:
            return
        size = self.items[index]
        fill = self.item_colors[index]
        label_size = min(23, int(height * 0.75), int(width / max(1, len(str(size)))))
        if alpha < 255:
            left, top, pixel_width, pixel_height = self.view.rect(x, y, width, height)
            if pixel_width < 1 or pixel_height < 1:
                return
            tile = pygame.Surface((pixel_width, pixel_height), pygame.SRCALPHA)
            tile.fill(fill)
            pygame.draw.rect(tile, colors.BACKGROUND, tile.get_rect(), self.view.length(2))
            if label_size >= 7:
                label = self.font(label_size, True).render(str(size), True, colors.BACKGROUND)
                tile.blit(label, label.get_rect(center=tile.get_rect().center))
            tile.set_alpha(alpha)
            self.screen.blit(tile, (left, top))
            return
        self.rect(x, y, width, height, fill, colors.BACKGROUND, radius=0)
        if label_size >= 7:
            self.centered_text(size, x + width / 2, y + height / 2, label_size,
                               colors.BACKGROUND, True)

    def _draw_moving_item(self, x, y, width, height):
        t = self.motion
        self._draw_item(self.current, 712 + (x - 712) * t, 44 + (y - 44) * t,
                        64 + (width - 64) * t, 38 + (height - 38) * t)

    def _draw_queue(self):
        next_index = self.processed
        slide = 0 if self.queue_motion is None else 1 - self.queue_motion
        if self.current is not None:
            self.text("현재", 650, 52, 22, colors.TEXT_MUTED)
            if self.comparison_fade is not None:
                self._draw_item(self.current, 712, 44, 64, 38,
                                alpha=255 - round(255 * self.comparison_fade))
            elif self.motion is None:
                self._draw_item(self.current, 712 + 168 * slide, 44, 64 - 11 * slide, 38 - 3 * slide)
            next_index = self.current + 1
        if next_index < len(self.items):
            self.text("대기", 821, 52, 22, colors.TEXT_MUTED)
            for index in range(next_index, min(next_index + 8, len(self.items))):
                self._draw_item(index, 880 + (index - next_index + slide) * 62, 45, 53, 35)
            remaining = len(self.items) - next_index - 8
            if remaining > 0 and self.queue_motion is None:
                self.text(f"+{remaining}", 1381, 52, 20, colors.TEXT_MUTED)

    def draw_content(self):
        if not hasattr(self, "items"):
            return
        self.text(self.strategy, 55, 43, 39, bold=True)
        if self.comparison_bins is not None:
            self.text(f"{self.processed}/{len(self.items)} 처리", 300, 52, 24)
            self._draw_queue()
            self._draw_comparison()
            return
        self.text(f"{self.processed}/{len(self.items)} 처리 · 통 {len(self.bins)}개", 300, 52, 24)
        self._draw_queue()

        if self._page_count() > 1:
            self.right_text(f"통 페이지 {self.page + 1}/{self._page_count()} · PgUp/PgDn",
                            1545, 98, 18, colors.TEXT_MUTED)
        scroll_columns = self._single_layouts()[-1][1]
        start = self.page * scroll_columns
        end = min(start + scroll_columns * 3, len(self.bins))
        for index in range(start, end):
            bin = self.bins[index]
            x, y, width, height = self._bin_rect(index)
            accent = colors.YELLOW if index == self.checking else colors.GREEN if index == self.selected else colors.BORDER
            text_color = colors.TEXT_MUTED if accent == colors.BORDER else accent
            moving = index == self.selected and self.motion is not None
            free = bin.free + (bin.items[-1] if moving else 0)
            self.centered_text(index + 1, x + width / 2, y - 13, 18, text_color, True)
            center_x, free_y = x + width / 2, y + height + 13
            eligible = (
                self.current is not None
                and index < self.candidate_count
                and free >= self.items[self.current]
                and (self.strategy != "Next Fit" or index == self.candidate_count - 1)
            )
            width_label = min(self.capacity_label_width, width)
            font_size = min(16, max(8, int((width_label - 4) / (0.65 * len(str(free))))))
            if eligible:
                self.rect(center_x - width_label / 2, free_y - 11, width_label, 22,
                          colors.PANEL_DARK, colors.YELLOW, radius=4)
            self.centered_text(free, center_x, free_y, font_size, colors.YELLOW if eligible else text_color, True)
            self.rect(x, y, width, height, colors.PANEL_DARK, accent, radius=4)
            bottom = y + height - 3
            scale = (height - 6) / self.capacity
            items = self.placed_items[index]
            for item_index in items[:-1] if moving else items:
                item_height = self.items[item_index] * scale
                bottom -= item_height
                self._draw_item(item_index, x + 3, bottom, width - 6, item_height)

        if self.motion is not None and start <= self.selected < end:
            x, y, width, height = self._bin_rect(self.selected)
            size = self.items[self.current]
            free = self.bins[self.selected].free
            end_y = y + 3 + free * (height - 6) / self.capacity
            self._draw_moving_item(x + 3, end_y, width - 6, size * (height - 6) / self.capacity)

    def _draw_comparison(self):
        bottom = 878 if self.explanation_hidden else 825
        pane_width = 735
        pane_height = (bottom - 130 - 14) / 2
        columns = 20
        launch_space = 38
        destinations = []
        in_transit = self.comparison_fade is not None or self.motion is not None
        for panel, (strategy, bins) in enumerate(self.comparison_bins.items()):
            row, col = divmod(panel, 2)
            x = 55 + col * (pane_width + 20)
            y = 130 + row * (pane_height + 14)
            self.rect(x, y, pane_width, pane_height, colors.PANEL_DARK)
            bin_count = len(bins) - (in_transit and strategy in self.comparison_opened)
            self.text(f"{strategy} · 통 {bin_count}개", x + 14, y + 10, 22, bold=True)
            pages = max(1, (len(bins) + self.comparison_page_size - 1) // self.comparison_page_size)
            selected = self.comparison_selected.get(strategy)
            page = self.page if self.comparison_browse else (selected or 0) // self.comparison_page_size
            page = min(page, pages - 1)
            if self._page_count() > 1:
                self.right_text(f"{page + 1}/{pages} · PgUp/PgDn", x + pane_width - 14, y + 12, 17, colors.TEXT_MUTED)
            start = page * self.comparison_page_size
            end = min(start + self.comparison_page_size, len(bins))
            rows = max(1, (min(len(bins), self.comparison_page_size) + columns - 1) // columns)
            last_row, last_column = divmod(max(0, end - start - 1), columns)
            row_height = min(150, (pane_height - 50) / rows)
            bin_height = row_height - 25
            column_width = (pane_width - 28 - launch_space) / columns
            width = column_width - 3
            start_x = x + 14 + last_column * column_width + width + 6
            for index in range(start, end):
                bin_row, bin_col = divmod(index - start, columns)
                left = x + 14 + bin_col * column_width
                top = y + 48 + bin_row * row_height
                scale = (bin_height - 4) / self.capacity
                moving = index == selected and in_transit
                item_indices = self.comparison_items[strategy][index]
                free = bins[index].free
                accent = colors.GREEN if index == selected else colors.BORDER
                self.rect(left, top, width, bin_height, colors.BACKGROUND, accent, radius=3)
                if moving:
                    size = self.items[self.current]
                    item_width = width - 4
                    target_y = top + 2 + free * scale
                    start_y = target_y + (last_row - bin_row) * row_height
                    destinations.append((start_x, start_y, left + 2, target_y, item_width, size * scale))
                    free += size
                    item_indices = item_indices[:-1]
                self.centered_text(free, left + width / 2, top + bin_height + 10, 13,
                                   colors.GREEN if index == selected else colors.TEXT_MUTED)
                item_bottom = top + bin_height - 2
                for item_index in item_indices:
                    item_height = self.items[item_index] * scale
                    item_bottom -= item_height
                    self._draw_item(item_index, left + 2, item_bottom, width - 4, item_height)
        for start_x, start_y, target_x, target_y, width, height in destinations:
            if self.comparison_fade is not None:
                self._draw_item(self.current, start_x, start_y, width, height,
                                alpha=round(255 * self.comparison_fade))
            else:
                x = start_x + (target_x - start_x) * self.motion
                y = start_y + (target_y - start_y) * self.motion
                self._draw_item(self.current, x, y, width, height)

    def _draw_messages(self):
        if self.explanation_hidden:
            self.right_text("H: 설명", 1545, 52, 18, colors.TEXT_MUTED)
            return
        self.text(self.status, 55, 852, 20)
        self.right_text("Tab: 전략  D: 데이터  Shift+R: 무작위  H: 확대", 1545, 852, 18, colors.TEXT_MUTED)
