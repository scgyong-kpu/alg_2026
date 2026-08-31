from dataclasses import dataclass


@dataclass
class View:
    logical_width: float = 1600.0
    logical_height: float = 900.0
    window_width: int = 1280
    window_height: int = 720
    scale: float = 1.0
    origin_x: float = 0.0
    origin_y: float = 0.0

    def __post_init__(self):
        self.resize(self.window_width, self.window_height)

    def resize(self, width, height):
        self.window_width = max(1, int(width))
        self.window_height = max(1, int(height))
        self.scale = min(
            self.window_width / self.logical_width,
            self.window_height / self.logical_height,
        )
        self.origin_x = (self.window_width - self.logical_width * self.scale) / 2
        self.origin_y = (self.window_height - self.logical_height * self.scale) / 2

    def point(self, x, y):
        return (
            int(round(self.origin_x + x * self.scale)),
            int(round(self.origin_y + y * self.scale)),
        )

    def rect(self, x, y, width, height):
        sx, sy = self.point(x, y)
        return (
            sx,
            sy,
            int(round(width * self.scale)),
            int(round(height * self.scale)),
        )

    def length(self, value):
        return max(1, int(round(value * self.scale)))
