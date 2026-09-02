import os
import time
from importlib import resources

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from . import colors
from .config import load_config, save_config
from .view import View


FONT_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "malgun.ttf"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "malgunbd.ttf"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "gulim.ttc"),
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/NanumGothic_Coding.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

MONO_FONT_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "malgun.ttf"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "consola.ttf"),
    "/System/Library/Fonts/Menlo.ttc",
    "/Library/Fonts/NanumGothic_Coding.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
]

FONT_NAMES = [
    "malgungothic",
    "malgun gothic",
    "gulim",
    "gungsuh",
    "applesdgothicneo",
    "nanumgothiccoding",
    "nanumgothic",
    "notosanscjkkr",
    "notosanskr",
    "arialunicode",
]

MONO_FONT_NAMES = [
    "d2coding",
    "nanumgothiccoding",
    "malgungothic",
    "malgun gothic",
    "consolas",
    "menlo",
]

MAX_SPEED = 999999.0


class BaseVisualizer:
    def __init__(self, title="Algorithm Visualizer", width=None, height=None, config_path=None):
        self.config_path = config_path
        self.config = load_config(config_path)
        width = width or int(self.config["window"].get("width", 1280))
        height = height or int(self.config["window"].get("height", 720))

        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self._set_window_icon()
        self.clock = pygame.time.Clock()
        self.view = View(window_width=width, window_height=height)
        self.title = title
        self.closed = False
        self.requested_action = None
        self.paused = False
        self.step_requested = False
        self.running_to_section = False
        self.pause_after_section = False
        self.speed = float(self.config.get("speed", 1.0))
        self.font_scale = float(self.config["font"].get("scale", 1.0))
        self.font_path = self._find_font_path()
        self.mono_font_path = self._find_mono_font_path()
        self.font_cache = {}
        self.next_dataset_name = ""
        self.messages = {
            "phase": "",
            "action": "",
            "detail": "",
            "stats": "",
            "path": "",
            "dataset": "",
            "hint": "Space: 일시정지  .: 한 단계  Enter: 다음 구간  1-9: 속도  +/-: 글씨  Esc: 종료",
        }
        self.log_lines = []
        self.message_layout = "bottom"

    def set_message_layout(self, layout):
        if layout not in ("bottom", "side"):
            raise ValueError(f"unknown message layout: {layout}")
        self.message_layout = layout

    def msg_phase(self, text):
        self.messages["phase"] = str(text)

    def msg_action(self, text):
        self.messages["action"] = str(text)

    def msg_detail(self, text):
        self.messages["detail"] = str(text)

    def msg_stats(self, text):
        self.messages["stats"] = str(text)

    def msg_path(self, text):
        self.messages["path"] = str(text)

    def msg_dataset(self, text):
        self.messages["dataset"] = str(text)

    def set_data_info(self, data):
        self.running_to_section = False
        self.pause_after_section = False
        self.step_requested = False
        self.next_dataset_name = getattr(data, "_next_dataset_name", "")
        self.msg_dataset(self._data_label(data))
        self.msg_hint(self._running_hint())

    def msg_hint(self, text):
        self.messages["hint"] = str(text)

    def msg_log(self, text):
        self.log_lines.append(str(text))
        self.log_lines = self.log_lines[-1:]

    def msg_clear(self):
        for key in ("phase", "action", "detail", "stats", "path", "dataset"):
            self.messages[key] = ""
        self.log_lines.clear()

    def wait(self, milliseconds=None):
        if milliseconds is None:
            return self._wait_for_action()

        if self.closed:
            return

        if self.is_max_speed() or self.running_to_section:
            self._handle_events()
            self.draw()
            return

        target = time.monotonic() + milliseconds / 1000 / self.speed
        while not self.closed and self.requested_action is None:
            self._handle_events()
            if self.running_to_section or self.is_max_speed():
                self.draw()
                break
            self.draw()
            if self.paused:
                if self.step_requested:
                    self.step_requested = False
                    break
            elif time.monotonic() >= target:
                break
            self.clock.tick(60)

    def end(self):
        return self._wait_for_action()

    def stopped(self):
        return self.closed or self.requested_action is not None

    def can_show_answer(self):
        return False

    def wants_answer(self):
        return self.requested_action == "answer" and self.can_show_answer()

    def is_max_speed(self):
        return self.speed >= MAX_SPEED

    def section_end(self):
        if not self.running_to_section:
            return

        self.running_to_section = False
        self.paused = self.pause_after_section
        self.pause_after_section = False
        while self.paused and not self.closed and self.requested_action is None:
            self._handle_events()
            self.draw()
            if self.step_requested:
                self.step_requested = False
                break
            if self.running_to_section:
                self.paused = False
                break
            self.clock.tick(60)

    def _wait_for_action(self):
        self.running_to_section = False
        self.pause_after_section = False
        self.step_requested = False
        self.msg_hint(self._action_hint())
        while not self.closed and self.requested_action is None:
            self._handle_events()
            self.draw()
            self.clock.tick(60)
        self.save_config()
        action = self.requested_action or "quit"
        self.requested_action = None
        if action == "quit":
            pygame.quit()
        from .runner import set_action

        set_action(action)
        return action

    def draw(self):
        if self.requested_action is not None:
            return
        self.screen.fill(colors.BACKGROUND)
        self.draw_content()
        self._draw_messages()
        pygame.display.flip()

    def draw_content(self):
        pass

    def font(self, logical_size, bold=False):
        size = max(10, int(logical_size * self.view.scale * self.font_scale))
        key = (size, bold)
        if key not in self.font_cache:
            if self.font_path:
                font = pygame.font.Font(self.font_path, size)
                font.set_bold(bold)
            else:
                font = pygame.font.SysFont("arial", size, bold=bold)
            self.font_cache[key] = font
        return self.font_cache[key]

    def mono_font(self, logical_size, bold=False):
        size = max(10, int(logical_size * self.view.scale * self.font_scale))
        key = ("mono", size, bold)
        if key not in self.font_cache:
            if self.mono_font_path:
                font = pygame.font.Font(self.mono_font_path, size)
                font.set_bold(bold)
            else:
                font = pygame.font.SysFont("monospace", size, bold=bold)
            self.font_cache[key] = font
        return self.font_cache[key]

    def text(self, value, x, y, size=28, color=colors.TEXT, bold=False):
        rendered = self.font(size, bold).render(str(value), True, color)
        self.screen.blit(rendered, self.view.point(x, y))

    def mono_text(self, value, x, y, size=28, color=colors.TEXT, bold=False):
        rendered = self.mono_font(size, bold).render(str(value), True, color)
        self.screen.blit(rendered, self.view.point(x, y))

    def right_text(self, value, right, y, size=28, color=colors.TEXT, bold=False):
        rendered = self.font(size, bold).render(str(value), True, color)
        x, sy = self.view.point(right, y)
        rect = rendered.get_rect(topright=(x, sy))
        self.screen.blit(rendered, rect)

    def centered_text(self, value, cx, cy, size=28, color=colors.TEXT, bold=False):
        rendered = self.font(size, bold).render(str(value), True, color)
        rect = rendered.get_rect(center=self.view.point(cx, cy))
        self.screen.blit(rendered, rect)

    def rect(self, x, y, width, height, fill, border=colors.BORDER, radius=8):
        screen_rect = pygame.Rect(self.view.rect(x, y, width, height))
        pygame.draw.rect(self.screen, fill, screen_rect, border_radius=self.view.length(radius))
        pygame.draw.rect(
            self.screen,
            border,
            screen_rect,
            width=self.view.length(2),
            border_radius=self.view.length(radius),
        )

    def _draw_messages(self):
        if self.message_layout == "side":
            self._draw_messages_side()
            return

        self.rect(60, 640, 1480, 210, colors.PANEL_DARK, colors.BORDER, 10)
        y = 665
        if self.messages["phase"]:
            self.text(self.messages["phase"], 90, y, 26, colors.BLUE, True)
        if self.messages["dataset"]:
            self.text(self.messages["dataset"], 300, y + 2, 20, colors.TEXT_MUTED)
        if self.messages["stats"]:
            self.text(self.messages["stats"], 1180, y, 22, colors.TEXT_MUTED)
        y += 44
        if self.messages["path"]:
            self.text(self.messages["path"], 90, y, 22, colors.TEXT_MUTED)
            y += 34
        if self.messages["action"]:
            self.text(self.messages["action"], 90, y, 30, colors.TEXT, True)
            y += 46
        if self.messages["detail"]:
            self.text(self.messages["detail"], 90, y, 23, colors.TEXT_MUTED)
            y += 34
        for line in self.log_lines:
            self.text(line, 90, min(y, 795), 20, colors.TEXT_MUTED)
        self.text(self.messages["hint"], 90, 825, 18, colors.TEXT_MUTED)

    def _draw_messages_side(self):
        self.rect(1110, 70, 430, 780, colors.PANEL_DARK, colors.BORDER, 10)
        y = 100
        if self.messages["phase"]:
            y = self._draw_wrapped_text(self.messages["phase"], 1140, y, 360, 26, colors.BLUE, True, 34)
        if self.messages["dataset"]:
            y = self._draw_wrapped_text(self.messages["dataset"], 1140, y + 4, 360, 20, colors.TEXT_MUTED, False, 28)
        if self.messages["stats"]:
            y = self._draw_wrapped_text(self.messages["stats"], 1140, y + 10, 360, 22, colors.TEXT_MUTED, False, 30)
        if self.messages["path"]:
            y = self._draw_wrapped_text(self.messages["path"], 1140, y + 16, 360, 20, colors.TEXT_MUTED, False, 28)
        if self.messages["action"]:
            y = self._draw_wrapped_text(self.messages["action"], 1140, y + 28, 360, 28, colors.TEXT, True, 38)
        if self.messages["detail"]:
            y = self._draw_wrapped_text(self.messages["detail"], 1140, y + 22, 360, 22, colors.TEXT_MUTED, False, 32)
        for line in self.log_lines:
            y = self._draw_wrapped_text(line, 1140, y + 18, 360, 20, colors.TEXT_MUTED, False, 28)
        self._draw_wrapped_text(self.messages["hint"], 1140, 770, 360, 18, colors.TEXT_MUTED, False, 26)

    def _draw_wrapped_text(self, value, x, y, max_width, size, color=colors.TEXT, bold=False, line_height=30):
        text = str(value)
        font = self.font(size, bold)
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            line = ""
            for word in words:
                candidate = word if not line else f"{line} {word}"
                if font.size(candidate)[0] <= max_width * self.view.scale:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)

        for line in lines:
            self.text(line, x, y, size, color, bold)
            y += line_height
        return y

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closed = True
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.view.resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key, event.mod)

    def _handle_key(self, key, mod=0):
        if key == pygame.K_ESCAPE:
            self.closed = True
            self.requested_action = "quit"
        elif key == pygame.K_r:
            self.requested_action = "restart"
        elif key == pygame.K_d:
            self.requested_action = "next_data"
        elif key == pygame.K_a:
            if self.can_show_answer():
                self.requested_action = "answer"
            else:
                self.msg_log("준비된 해답 없음")
        elif key == pygame.K_SPACE:
            self.running_to_section = False
            self.pause_after_section = False
            self.paused = not self.paused
        elif key == pygame.K_RETURN:
            self._run_to_section()
        elif key in (pygame.K_PERIOD, getattr(pygame, "K_KP_PERIOD", None)):
            self._request_step()
        elif pygame.K_1 <= key <= pygame.K_8:
            self.speed = key - pygame.K_0
            self.msg_log(f"속도: {self.speed:g}x")
        elif key == pygame.K_9:
            self.speed = MAX_SPEED
            self.msg_log("속도: max")
        elif key == pygame.K_0:
            self.speed = 0.5
            self.msg_log("속도: 0.5x")
        elif key in (pygame.K_EQUALS, pygame.K_PLUS):
            self.font_scale = min(1.8, self.font_scale + 0.1)
            self.font_cache.clear()
            self.msg_log(f"글씨 배율: {self.font_scale:.1f}x")
        elif key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
            self.font_scale = max(0.7, self.font_scale - 0.1)
            self.font_cache.clear()
            self.msg_log(f"글씨 배율: {self.font_scale:.1f}x")

    def _request_step(self):
        if self.paused:
            self.step_requested = True
        else:
            self.paused = True
            self.step_requested = True

    def _run_to_section(self):
        self.pause_after_section = self.paused
        self.running_to_section = True
        self.paused = False
        self.step_requested = False
        self.msg_log("다음 구간까지 진행")

    def _data_label(self, data):
        name = getattr(data, "_dataset_name", "")
        index = getattr(data, "_dataset_index", None)
        count = getattr(data, "_dataset_count", None)
        if not name:
            return ""
        if index is not None and count:
            label = f"데이터 {index}/{count}: {name}"
        else:
            label = f"데이터: {name}"
        return label

    def _action_hint(self):
        if self.next_dataset_name:
            return f"R: 다시 실행  Esc: 종료  D: 다음 데이터({self.next_dataset_name})"
        return "R: 다시 실행  Esc: 종료  D: 다음 데이터"

    def _running_hint(self):
        if self.next_dataset_name:
            return f"Space: 일시정지  .: 한 단계  Enter: 다음 구간  D: 다음 데이터({self.next_dataset_name})  1-9: 속도  +/-: 글씨  Esc: 종료"
        return "Space: 일시정지  .: 한 단계  Enter: 다음 구간  D: 다음 데이터  1-9: 속도  +/-: 글씨  Esc: 종료"

    def _find_font_path(self):
        for path in FONT_CANDIDATES:
            if os.path.exists(path):
                return path
        for name in FONT_NAMES:
            path = pygame.font.match_font(name)
            if path:
                return path
        return None

    def _find_mono_font_path(self):
        for path in MONO_FONT_CANDIDATES:
            if os.path.exists(path):
                return path
        for name in MONO_FONT_NAMES:
            path = pygame.font.match_font(name)
            if path:
                return path
        return None

    def _set_window_icon(self):
        try:
            icon_ref = resources.files("pyvisalgo").joinpath("assets/tukorea.png")
            with resources.as_file(icon_ref) as icon_path:
                icon = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon)
        except (FileNotFoundError, ModuleNotFoundError, pygame.error):
            pass

    def save_config(self):
        width, height = self.screen.get_size()
        self.config["window"]["width"] = width
        self.config["window"]["height"] = height
        self.config["font"]["scale"] = self.font_scale
        self.config["speed"] = self.speed
        save_config(self.config, self.config_path)
