"""작업의 시간 위치를 유지하면서 기계 행으로 옮긴다."""

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class JobScheduleVisualizer(BaseVisualizer):
    palette = (colors.BLUE, colors.ORANGE, colors.GREEN, colors.RED, colors.YELLOW)
    first_machine_y = 205
    queue_y = 455

    def setup(self, data):
        self.msg_clear()
        self.set_data_info(data)
        self.jobs = list(data.jobs)
        self.by_name = {job[0]: i for i, job in enumerate(self.jobs)}
        self.first = min(job[1] for job in self.jobs)
        self.last = max(job[2] for job in self.jobs)
        self.unit = 1280 / (self.last - self.first)
        self.machine_row = min(48, 202 / len(self.jobs))
        self.queue_row = min(27, 160 / len(self.jobs))
        self.assigned = []
        self.motion = None
        self.overview = True
        self.sort_motion = None
        self.msg_phase("작업 준비")
        self.msg_action("각 작업은 시작 시각과 종료 시각이 정해져 있다.")
        self.wait(800)

    def order_jobs(self, ordered):
        self.msg_phase("시작 시각으로 정렬")
        self.msg_action("가장 이른 시작 시각의 작업부터 배정한다.")
        self.msg_detail("시간축에서 막대의 위치와 길이는 바꾸지 않고, 행의 순서만 바꾼다.")
        target_rows = {job[0]: i for i, job in enumerate(ordered)}
        for frame in range(37):
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
            t = frame / 36
            self.sort_motion = target_rows, t * t * (3 - 2 * t)
            self.wait(20)
        self.jobs = list(ordered)
        self.sort_motion = None
        self.wait(950)
        self.overview = False

    def place(self, job, machine, reuse):
        name, start, end = job
        self.msg_phase("기계 재사용" if reuse else "기계 추가")
        self.msg_action(f"{name} [{start}, {end}) → 기계 {machine + 1}")
        self.msg_detail("앞 작업이 시작 시각까지 끝났으므로 같은 기계에 배정한다." if reuse
                        else "시작 시각에 비어 있는 기계가 없으므로 새 기계를 추가한다.")
        for frame in range(25):
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
            t = frame / 24
            self.motion = (job, machine, t * t * (3 - 2 * t))
            self.wait(20)
        self.motion = None
        self.assigned.append((job, machine))
        self.wait(500)
        self.section_end()

    def finish(self, count):
        self.msg_phase("배정 완료")
        self.msg_action(f"모든 작업을 기계 {count}대에 배정했다.")
        self.msg_detail("새 기계를 추가한 순간에는 기존 기계가 모두 사용 중이었다.")
        self.draw()

    def _x(self, time):
        return 220 + (time - self.first) * self.unit

    def _block(self, job, y, height=36):
        name, start, end = job
        color = self.palette[self.by_name[name] % len(self.palette)]
        left, right = self._x(start), self._x(end)
        self.rect(left + 2, y - height / 2, right - left - 4, height, colors.PANEL, color, radius=4)
        self.centered_text(name, (left + right) / 2, y, min(21, int(height * 0.8)), color, True)

    def _draw_axis(self, y):
        for i in range(11):
            time = self.first + (self.last - self.first) * i / 10
            x = self._x(time)
            self.centered_text(f"{time:g}", x, y, 18, colors.TEXT_MUTED)
            pygame.draw.line(self.screen, colors.BORDER, self.view.point(x, y + 18),
                             self.view.point(x, 605), max(1, self.view.length(1)))

    def draw_content(self):
        if not hasattr(self, "jobs"):
            return
        self.text("Job Scheduling", 65, 35, 42, bold=True)
        self.text("작업 순서", 80, 110, 22, colors.BLUE, True)
        if self.overview:
            self._draw_axis(155)
            self.text("대기 작업", 80, self.queue_y - 13, 22, colors.BLUE, True)
            for i, job in enumerate(self.jobs):
                row = i
                if self.sort_motion is not None:
                    target_rows, t = self.sort_motion
                    row += (target_rows[job[0]] - i) * t
                self._block(job, self.queue_y + row * self.queue_row, self.queue_row - 4)
            return
        self.text(" → ".join(job[0] for job in self.jobs), 220, 110, 22)
        self._draw_axis(155)
        placed = {job[0] for job, _ in self.assigned}
        pending = [job for job in self.jobs if job[0] not in placed]
        self.text("대기 작업", 80, self.queue_y - 13, 22, colors.BLUE, True)
        for i, job in enumerate(pending):
            if i == 0 and self.motion:
                continue
            shift = self.motion[2] if self.motion else 0
            self._block(job, self.queue_y + (i - shift) * self.queue_row, self.queue_row - 4)
        count = max((i + 1 for _, i in self.assigned), default=0)
        if self.motion:
            count = max(count, self.motion[1] + 1)
        self.right_text(f"사용 기계: {count}대", 1510, 110, 22, colors.GREEN, True)
        for i in range(count):
            y = self.first_machine_y + i * self.machine_row
            label_size = min(22, int(self.machine_row - 4))
            self.text(f"기계 {i + 1}", 80, y - label_size / 2, label_size)
            height = self.machine_row - 2
            self.rect(220, y - height / 2, 1280, height, colors.PANEL_DARK, colors.BORDER, radius=4)
        for job, machine in self.assigned:
            self._block(job, self.first_machine_y + machine * self.machine_row, self.machine_row - 6)
        if self.motion:
            job, machine, t = self.motion
            target = self.first_machine_y + machine * self.machine_row
            height = (self.queue_row - 4) * (1 - t) + (self.machine_row - 6) * t
            self._block(job, self.queue_y + (target - self.queue_y) * t, height)
