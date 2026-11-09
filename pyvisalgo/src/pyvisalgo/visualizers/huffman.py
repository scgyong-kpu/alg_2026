"""허프만 코딩의 문자 집계와 최소 힙 연산을 그린다."""

import pygame

from ..core import colors
from ..core.visualizer import BaseVisualizer


class HuffmanVisualizer(BaseVisualizer):
    palette = (colors.BLUE, colors.ORANGE, colors.GREEN, colors.YELLOW,
               (205, 151, 227), (105, 204, 204), (237, 130, 150))

    def setup(self, data):
        # 이전 실행에서 저장된 공통 최대속도 설정도 허프만에서는 9배속으로 표시한다.
        if self.is_max_speed():
            self.speed = 9
        self.msg_clear()
        self.set_data_info(data)
        self.source = data.text
        symbols = len(set(self.source))
        self.dense = symbols > 20
        self.table_columns = max(10, (symbols + 2) // 3)
        # 한 데이터 안에서는 힙·합치기·이동 장면 모두 같은 축척을 사용한다.
        self.leaf_step = min(145, 1440 / max(symbols, 1))
        self.level_step = 18 if self.dense else 34 if symbols > 8 else 60
        self.counts = {}
        self.nodes = {}
        self.heap = []
        self.taken = []
        self.tree = None
        self.scene = "source"
        self.progress = 0
        self.motion = {}
        self.codes = []
        self.code_path = []
        self.extracted = set()
        self.flying_code = None
        self.encoding = None
        self.encoding_active = False
        self.encoding_fast = False
        self.msg_phase("원문")
        self.msg_action(f"원문에 문자가 {len(self.source)}개 있다.")
        self.wait(1800)
        self.section_end()

    @staticmethod
    def _symbol(char, compact=False):
        if compact and char == " ":
            return "·"
        return {" ": "공백", "\n": "줄바꿈", "\t": "탭"}.get(char, char)

    @staticmethod
    def _cell(index, columns, x, y, dx, dy):
        return x + index % columns * dx, y + index // columns * dy

    def _animate(self, scene):
        self.scene = scene
        self.progress = 0
        frame = 0
        while frame <= 36:
            if self.stopped() or self.running_to_section or self.is_max_speed():
                break
            t = frame / 36
            self.progress = t * t * (3 - 2 * t)
            self.wait(12 if self.encoding_fast else 24)
            frame += 18 if self.encoding_fast else 4 if self.speed == 9 else 1
        self.progress = 1

    def _handle_key(self, key, mod=0):
        if key == pygame.K_9:
            self.speed = 9
            self.msg_log("속도: 9x")
            return
        if key == pygame.K_RETURN and mod & pygame.KMOD_SHIFT:
            if not getattr(self, "scene", "").startswith("decode"):
                self.jump_to_decode = True
                self._run_to_section()
                return
        if key == pygame.K_RETURN and getattr(self, "encoding_active", False):
            if not self.encoding_fast:
                self.encoding_fast = True
                self.paused = False
                self.step_requested = False
                return
        super()._handle_key(key, mod)

    def wait(self, milliseconds=None):
        if milliseconds is not None and getattr(self, "jump_to_decode", False):
            self._handle_events()
            return
        return super().wait(milliseconds)

    def section_end(self):
        if not getattr(self, "jump_to_decode", False):
            super().section_end()

    def _encoding_wait(self, duration):
        if not (self.running_to_section or self.is_max_speed()):
            self.wait(0 if self.encoding_fast else duration)

    def _hold(self, duration=850):
        self.wait(duration)
        self.section_end()

    def group(self, counts):
        self.counts = counts
        self.char_index = {char: i for i, char in enumerate(counts)}
        self.msg_phase("문자별 빈도")
        self.msg_action("같은 글자를 한곳으로 모아 개수를 센다.")
        self.msg_detail("가운데 점(·)은 공백 문자이다. 공백도 다른 문자처럼 센다.")
        self._animate("group")
        self.scene = "table"
        self._hold()

    def _heap_positions(self, heap):
        return self._forest_positions([node for _, node in heap], 175, left=80)

    def _forest_positions(self, roots, top, left=None):
        # 각 트리에 잎 개수만큼 자리를 배정하여 가지가 옆 트리와 겹치지 않게 한다.
        layouts = [self._tree_positions(root, 0, top) for root in roots]
        widths = [max(x for x, _ in layout.values()) + self.leaf_step for layout in layouts]
        if left is None:
            left = 800 - sum(widths) / 2
        start = left + self.leaf_step / 2
        positions = {}
        for layout, width in zip(layouts, widths):
            positions.update({node: (x + start, y) for node, (x, y) in layout.items()})
            start += width
        return positions

    def _table_position(self, index):
        if self.dense:
            step = 1440 / self.table_columns
            return self._cell(index, self.table_columns, 80 + step / 2, 255, step, 130)
        return self._cell(index, 10, 145, 305, 145, 130)

    def make_heap(self, heap, nodes):
        self.nodes = nodes
        self.msg_phase("최소 힙 만들기")
        self.msg_action("문자별 빈도로 최소 힙을 만든다.")
        self.msg_detail("배열 전체가 정렬된 것은 아니다. 맨 앞이 최소 빈도이다.")
        self.motion = {node: (self._table_position(node), position)
                       for node, position in self._heap_positions(heap).items()}
        self._animate("heap_motion")
        self.heap = list(heap)
        self.scene = "heap"
        self.wait(850)

    def pop(self, heap, node, number):
        self.msg_phase(f"최솟값 꺼내기 {number}/2")
        self.msg_action(f"남은 힙에서 최소 빈도 {self.nodes[node][0]}을 꺼낸다.")
        self.msg_detail("첫 번째를 꺼낸 뒤의 힙에서 두 번째 최솟값을 고른다.")
        before, after = self._heap_positions(self.heap), self._heap_positions(heap)
        before.update(self._forest_positions(self.taken, 410))
        after.update(self._forest_positions([*self.taken, node], 410))
        self.motion = {i: (before[i], pos) for i, pos in after.items()}
        self._animate("heap_motion")
        self.heap = list(heap)
        self.taken.append(node)
        self.scene = "heap"
        self.wait(850)

    def join(self, parent):
        count, _, (left, right) = self.nodes[parent]
        before = self._forest_positions(self.taken, 410)
        after = self._forest_positions([parent], 350)
        before[parent] = (after[parent][0], 392)
        self.motion = {i: (before[i], pos) for i, pos in after.items()}
        self.tree = parent
        self.taken.clear()
        self.msg_phase("새 부모 만들기")
        self.msg_action(f"{self.nodes[left][0]} + {self.nodes[right][0]} = {count}")
        self.msg_detail("꺼낸 두 트리를 자식으로 연결하고 빈도 합을 부모에 기록한다.")
        self._animate("heap_motion")
        self.scene = "joined"
        self.wait(850)

    def push(self, heap, parent):
        self.msg_phase("부모를 힙에 넣기")
        self.msg_action(f"합친 트리의 빈도 {self.nodes[parent][0]}을 후보로 다시 넣는다.")
        before = self._heap_positions(self.heap)
        before.update(self._forest_positions([parent], 350))
        self.motion = {i: (before[i], pos) for i, pos in self._heap_positions(heap).items()}
        self._animate("heap_motion")
        self.heap = list(heap)
        self.scene = "heap"
        # 두 번의 pop과 부모 연결을 포함한 한 라운드를 push에서 마친다.
        self._hold()

    def finish(self, root):
        self.tree = root
        self.scene = "result"
        self.msg_phase("허프만 트리 완성")
        self.msg_action(f"힙에 트리 하나가 남았다. 루트 빈도: {self.nodes[root][0]}")
        self.msg_detail("왼쪽 간선은 0, 오른쪽 간선은 1이다. 루트에서 문자까지 따라가면 코드가 된다.")
        self.draw()
        self._hold(1000)
        codes = self._emit_codes(root)
        if codes and not self.stopped():
            self._encode_text(codes)
            if not self.stopped():
                self._hold(1300)
                self._decode_text(root)

    def _emit_codes(self, root):
        def leaves(node, path, bits):
            children = self.nodes[node][2]
            if children is None:
                yield path, bits or "0"
                return
            for bit, child in enumerate(children):
                yield from leaves(child, (*path, child), bits + str(bit))

        self.scene = "codes"
        self.msg_phase("문자별 코드 만들기")
        points = self._heap_positions(self.heap)
        codes = {}
        for path, bits in leaves(root, (root,), ""):
            for index, node in enumerate(path):
                if self.stopped():
                    return
                self.code_path = path[:index + 1]
                prefix = bits[:index]
                self.msg_action(f"지금까지 읽은 코드: {prefix}" if prefix else "루트부터 시작한다.")
                self.msg_detail("왼쪽 가지는 0, 오른쪽 가지는 1을 붙인다.")
                self.wait(120 if self.dense else 240)
            if self.stopped():
                return
            leaf = path[-1]
            count, char, _ = self.nodes[leaf]
            symbol = self._symbol(char)
            codes[char] = bits
            self.msg_action(f"{symbol}: 빈도 {count} → 코드 {bits}")
            self.msg_detail("잎에서 얻은 코드를 아래 표에 기록한다.")
            self.extracted.add(leaf)
            self.flying_code = (symbol, count, bits, points[leaf])
            self._animate("code_motion")
            self.codes.append((symbol, bits))
            self.flying_code = None
            self.scene = "codes"
            self._hold(240 if self.dense else 520)
        if not self.stopped():
            self.code_path = []
            self.msg_phase("허프만 코드 완성")
            self.msg_action(f"문자 {len(self.codes)}종의 코드를 만들었다.")
            self.msg_detail("한 문자의 코드가 다른 문자 코드의 접두사가 되지 않는다.")
            self.draw()
        return codes

    def _encode_text(self, codes):
        self._hold(850)
        self.encoding = {"index": 0, "pending": "", "bit_count": 0,
                         "selected": None, "part": "", "groups": [], "padding": 0}
        self.encoding_active = True
        state = self.encoding
        order = {char: i for i, char in enumerate(codes)}
        self.msg_phase("원문 인코딩")
        for index, char in enumerate(self.source):
            if self.stopped():
                return
            if self.running_to_section or self.is_max_speed():
                # 같은 비트를 이어 붙이되, 나머지 글자는 프레임을 그리지 않는다.
                tail = "".join(codes[c] for c in self.source[index:])
                state["pending"] += tail
                state["bit_count"] += len(tail)
                state["index"] = len(self.source)
                break
            part = codes[char]
            state.update(index=index, selected=order[char], part=part)
            self.scene = "encode"
            self.msg_action(f"{self._symbol(char)} → {part}")
            self.msg_detail(f"원문 {index + 1}/{len(self.source)}: 코드표에서 현재 문자의 코드를 찾는다.")
            self._encoding_wait(330)
            self._animate("encode_fly")
            self._animate("encode_scroll")
            state["pending"] += part
            state["bit_count"] += len(part)
            state.update(index=index + 1, selected=None, part="")
            self.scene = "encode"
            while len(state["pending"]) >= 8 and not self.stopped():
                self._pack_byte()
            self._encoding_wait(120)
        if self.stopped():
            return
        padding = -state["bit_count"] % 8
        state["padding"] = padding
        if padding:
            state["pending"] += "0" * padding
            if not (self.running_to_section or self.is_max_speed()):
                self.msg_action(f"마지막 바이트를 채우기 위해 0을 {padding}개 붙인다.")
                self._encoding_wait(550)
        if self.running_to_section or self.is_max_speed():
            pending = state["pending"]
            state["groups"].extend(pending[i:i + 8] for i in range(0, len(pending), 8))
            state["pending"] = ""
        while state["pending"] and not self.stopped():
            self._pack_byte()
        if self.stopped():
            return
        self.msg_phase("파일 저장 예시")
        self.msg_action(f"전체 {state['index']}자 → {state['bit_count']}비트 → {len(state['groups'])}바이트")
        self.msg_detail(f"패딩: 0을 {padding}개 추가. 실제 파일은 만들지 않는다.")
        self._animate("save")
        self.encoding_active = False
        self.encoding_fast = False
        self.draw()
        self.section_end()

    def _pack_byte(self):
        state = self.encoding
        group = state["pending"][:8]
        if not (self.running_to_section or self.is_max_speed()):
            self.msg_action(f"{group} → {int(group, 2):02X}")
            self.msg_detail("먼저 쌓인 8비트가 한 바이트가 된다.")
            self._animate("byte_drop")
        state["pending"] = state["pending"][8:]
        state["groups"].append(group)
        self.scene = "encode"

    def _decode_text(self, root):
        if getattr(self, "jump_to_decode", False):
            self.jump_to_decode = False
            self.running_to_section = False
            self.pause_after_section = False
        groups = self.encoding["groups"]
        length = self.encoding["bit_count"]
        points = self._tree_positions(root, 0, 0)
        width = max(x for x, _ in points.values())
        height = max(y for _, y in points.values())
        self.decoding = state = {
            "points": {i: (1160 + (x - width / 2) * min(1, 680 / max(1, width)),
                           170 + y * min(1, 360 / max(1, height)))
                       for i, (x, y) in points.items()},
            "byte": -1, "offset": 0, "word": "", "path": [root],
            "char": None, "output": [], "done": False,
        }
        self.scene = "decode"
        self.msg_phase("허프만 디코딩")
        self.msg_action("왼쪽 바이트부터 읽고 오른쪽 트리에서 문자를 찾는다.")
        self.msg_detail("0이면 왼쪽, 1이면 오른쪽. 잎에 도착하면 문자를 출력한다.")
        self.wait(900)
        node = root
        for index in range(length):
            if self.stopped():
                return
            byte, offset = divmod(index, 8)
            state.update(byte=byte, offset=offset)
            if offset == 0 and not self._decode_fast():
                self._animate("decode_byte")
            bit = groups[byte][offset]
            children = self.nodes[node][2]
            node = children[int(bit)] if children else node
            state["path"].append(node)
            state["word"] += bit
            if not self._decode_fast():
                self._animate("decode_bit")
            state["offset"] += 1
            char = self.nodes[node][1]
            if char is None:
                continue
            state["char"] = char
            if not self._decode_fast():
                self._animate("decode_leaf")
                self._animate("decode_output")
            state["output"].append(char)
            state.update(char=None, word="", path=[root])
            node = root
        if self.stopped():
            return
        state["done"] = True
        self.scene = "decode"
        self.msg_phase("디코딩 완료")
        self.msg_action(f"{length}비트에서 문자 {len(state['output'])}개를 복원했다.")
        matches = "".join(state["output"]) == self.source
        self.msg_detail("원문과 일치한다. 마지막 바이트의 패딩은 읽지 않았다." if matches else "원문과 일치하지 않는다.")
        self.draw()
        self.section_end()

    def _decode_fast(self):
        return self.running_to_section or self.is_max_speed()

    def _draw_decoding(self):
        state = self.decoding
        groups = self.encoding["groups"]
        byte, offset = state["byte"], state["offset"]
        self.text("입력 바이트", 80, 128, 22, colors.BLUE, True)
        start = byte if self.scene == "decode_byte" else byte + 1
        shift = 64 * self.progress if self.scene == "decode_byte" else 0
        for i, group in enumerate(groups[start:start + 10]):
            if i or self.scene != "decode_byte":
                self._code_card(f"{int(group, 2):02X}", 115 + i * 64 - shift, 175, 55)
        if byte >= 0 and not state["done"]:
            group = groups[byte]
            t = self.progress if self.scene == "decode_byte" else 1
            self.centered_text(f"{int(group, 2):02X}", 115 + 175 * t, 175 + 65 * t, 22, colors.GREEN, True)
            if self.scene != "decode_byte" or t > 0.5:
                for i, bit in enumerate(group):
                    consumed = i < offset or (self.scene == "decode_bit" and i == offset)
                    padding = byte * 8 + i >= self.encoding["bit_count"]
                    color = colors.BORDER if consumed or padding else colors.TEXT
                    self.centered_text(bit, 185 + 30 * i, 278, 25, color)
        self.text("현재 문자에 사용한 비트", 80, 326, 22, colors.BLUE, True)
        self.text("복원한 원문", 80, 477, 22, colors.BLUE, True)
        self.centered_text("".join(self._symbol(c, compact=True) if c != "\n" else "¶"
                                  for c in state["output"][-36:]),
                           400, 536, 21, colors.TEXT, True)
        points = state["points"]
        path = state["path"]
        traced = set(zip(path, path[1:]))
        for parent, (x, y) in points.items():
            for bit, child in enumerate(self.nodes[parent][2] or ()):
                cx, cy = points[child]
                active = (parent, child) in traced
                color = colors.YELLOW if active else colors.BORDER
                pygame.draw.line(self.screen, color, self.view.point(x, y),
                                 self.view.point(cx, cy), max(1, self.view.length(4 if active else 2)))
                if active:
                    self.centered_text(bit, (x + cx) / 2 + 5, (y + cy) / 2, 13, color, True)
        for node, (x, y) in points.items():
            char = self.nodes[node][1]
            color = colors.YELLOW if node in path and not state["done"] else colors.TEXT_MUTED
            if char is None:
                pygame.draw.circle(self.screen, color, self.view.point(x, y), max(1, self.view.length(3)))
            else:
                symbol = "¶" if char == "\n" else self._symbol(char, compact=True)
                self.centered_text(symbol, x, y, 14 if self.dense else 20, color, True)
        word = state["word"]
        if self.scene == "decode_bit":
            x = 185 + 30 * offset
            t = self.progress
            tx = 120 + (len(word) - 1) * 23
            self.centered_text(word[-1], x + (tx - x) * t, 278 + 100 * t, 24, colors.YELLOW, True)
            word = word[:-1]
        moving = self.scene == "decode_output"
        t = self.progress if moving else 0
        for i, bit in enumerate(word):
            self.centered_text(bit, 120 + i * 23 + 230 * t, 378 + 158 * t, 24, colors.YELLOW, True)
        if state["char"] is not None:
            symbol = self._symbol(state["char"], compact=True)
            target = 146 + len(word) * 23
            x, y = points[path[-1]]
            if self.scene == "decode_leaf":
                t = self.progress
                x, y = x + (target - x) * t, y + (378 - y) * t
            else:
                x, y = target + 230 * t, 378 + 158 * t
            self.centered_text(symbol, x, y, 27, colors.GREEN, True)

    def _draw_encoding(self):
        state = self.encoding
        self._draw_codes()
        self.text("원문", 80, 140, 22, colors.BLUE, True)
        self.text("Encoded", 80, 270, 22, colors.BLUE, True)
        self.rect(776, 166, 48, 55, colors.PANEL, colors.YELLOW, radius=4)
        scrolling = self.progress if self.scene == "encode_scroll" else 0
        index = state["index"]
        for i in range(max(0, index - 14), min(len(self.source), index + 15)):
            x = 800 + (i - index - scrolling) * 47
            symbol = {"\n": "¶", "\t": "⇥"}.get(self.source[i], self._symbol(self.source[i], compact=True))
            self.centered_text(symbol, x, 193, 23, colors.YELLOW if i == index else colors.TEXT, i == index)
        pending = state["pending"]
        bits = pending + (state["part"] if self.scene == "encode_scroll" else "")
        shift = len(state["part"]) * scrolling
        dropping = self.scene == "byte_drop"
        for i in range(8 if dropping else 0, len(bits)):
            x = 800 + (i - len(pending) - shift) * 22
            self.centered_text(bits[i], x, 322, 23, colors.GREEN if i >= len(pending) else colors.TEXT)
        pygame.draw.line(self.screen, colors.YELLOW, self.view.point(789, 298), self.view.point(789, 346),
                         max(1, self.view.length(2)))
        if self.scene == "encode_fly":
            x, y, width = self._code_position(state["selected"], len(self.codes))
            t = self.progress
            target = 800 + (len(state["part"]) - 1) * 11
            self._code_card(state["part"], x + (target - x) * t, y + (322 - y) * t, width, colors.YELLOW)
        self.text("16진수 바이트", 80, 389, 22, colors.BLUE, True)
        t = self.progress if dropping else 0
        for i, group in enumerate(reversed(state["groups"][-14:])):
            self.centered_text(f"{int(group, 2):02X}", 778 - (i + t) * 38, 404, 20, colors.GREEN, True)
        if state["groups"] and not dropping:
            self._draw_byte_bits(state["groups"][-1], 778, 368)
        if dropping:
            group = pending[:8]
            start = 800 + (3.5 - len(pending)) * 22
            x = start + (778 - start) * t
            y = 322 + (368 - 322) * t
            self._draw_byte_bits(group, x, y)
            if t >= 0.95:
                self.centered_text(f"{int(group, 2):02X}", 778, 404, 20, colors.GREEN, True)

    def _draw_byte_bits(self, group, x, y):
        for i, bit in enumerate(group):
            self.centered_text(bit, x + (i - 3.5) * 22, y, 23, colors.YELLOW, True)

    def _draw_bytes(self):
        groups = self.encoding["groups"]
        self.text("파일에 저장할 데이터", 80, 130, 23, colors.BLUE, True)
        self.text(f"전체 {len(groups)}바이트 · 처음 {min(16, len(groups))}바이트 표시", 80, 166, 19, colors.TEXT_MUTED)
        t = self.progress
        self.rect(1125, 225, 395, 210, colors.PANEL_DARK, colors.BLUE, radius=5)
        self.text("압축 파일", 1150, 248, 24, colors.BLUE, True)
        self.text(f"코드표 · 원래 길이 {self.encoding['bit_count']}비트", 1150, 290, 18)
        self.text(f"압축 데이터 {len(groups)}바이트", 1150, 330, 18)
        preview = " ".join(f"{int(group, 2):02X}" for group in groups[:8])
        self.text(preview, 1150, 378, 19, colors.GREEN, True)
        if t < 0.85:
            for index, group in enumerate(groups[:16]):
                x, y = self._cell(index, 8, 135, 255, 122, 90)
                self._code_card(f"{int(group, 2):02X}", x + (1320 - x) * t,
                                y + (391 - y) * t, 58)

    @staticmethod
    def _code_position(index, count):
        columns = min(15, max(8, count))
        pitch = 1440 / columns
        return 80 + (index % columns + 0.5) * pitch, 490 + index // columns * 48, pitch - 8

    def _draw_codes(self):
        self.text("문자별 허프만 코드", 80, 441, 22, colors.BLUE, True)
        pending = int(self.flying_code is not None)
        count = len(self.codes) + pending
        for index, (symbol, bits) in enumerate(self.codes):
            x, y, width = self._code_position(index, count)
            selected = self.encoding is not None and self.encoding["selected"] == index
            self._code_card(f"{symbol}:{bits}", x, y, width, colors.YELLOW if selected else colors.BLUE)
        if self.flying_code:
            symbol, frequency, bits, (x, y) = self.flying_code
            tx, ty, width = self._code_position(len(self.codes), count)
            t = self.progress
            label = f"{symbol}:{frequency}  {bits}" if t < 0.65 else f"{symbol}:{bits}"
            self._code_card(label, x + (tx - x) * t, y + (ty - y) * t,
                            width if t >= 0.65 else max(width, 145), colors.YELLOW)

    def _code_card(self, label, x, y, width, color=colors.BLUE):
        self.rect(x - width / 2, y - 17, width, 34, colors.PANEL, color, radius=4)
        size = 20
        while size > 10 and self.font(size, True).size(label)[0] > self.view.length(width - 6):
            size -= 1
        self.centered_text(label, x, y, size, colors.TEXT, True)

    def _node(self, node, x, y, active=False):
        count, char, _ = self.nodes[node]
        color = (colors.YELLOW if active else colors.TEXT_MUTED) if char is None else self.palette[node % len(self.palette)]
        if node in self.extracted:
            color = colors.BORDER
        elif active:
            color = colors.YELLOW
        width = min(110, self.leaf_step - (4 if self.dense else 12))
        height = 15 if self.dense else min(38, self.level_step - 8)
        self.rect(x - width / 2, y - height / 2, width, height, colors.PANEL, color, radius=4)
        label = f"{self._symbol(char)} : {count}" if char is not None else f"#{node} : {count}"
        if self.dense:
            symbol = {"\n": "¶", " ": "·"}.get(char, char)
            label = str(count) if char is None else f"{symbol}:{count}"
        self.centered_text(label, x, y, 10 if self.dense else 14 if height < 38 else 16, color, True)

    def _tree_positions(self, root, left, top):
        positions = {}
        leaf_count = 0

        def visit(node, depth):
            nonlocal leaf_count
            _, _, children = self.nodes[node]
            if children is None:
                x = leaf_count
                leaf_count += 1
            else:
                a, b = (visit(child, depth + 1) for child in children)
                x = (a + b) / 2
            positions[node] = (x, depth)
            return x

        visit(root, 0)
        # 밀집 배치에서도 루트 카드와 첫 자식 사이에 힙 경계가 들어갈 자리를 둔다.
        return {i: (left + x * self.leaf_step,
                    top + depth * self.level_step + (8 if self.dense and depth else 0))
                for i, (x, depth) in positions.items()}

    def _draw_forest(self, points, active=None):
        code_scene = self.scene in ("codes", "code_motion")
        traced = set(zip(self.code_path, self.code_path[1:])) if code_scene else set()
        for node, (x, y) in points.items():
            for bit, child in enumerate(self.nodes[node][2] or ()):
                cx, cy = points[child]
                highlighted = (node, child) in traced
                color = colors.YELLOW if highlighted else colors.BORDER
                pygame.draw.line(self.screen, color, self.view.point(x, y),
                                 self.view.point(cx, cy), max(1, self.view.length(4 if highlighted else 2)))
                if highlighted or (not self.dense and (code_scene or self.scene == "result")):
                    self.centered_text(bit, (x + cx) / 2 + 7, (y + cy) / 2,
                                       12 if self.dense else 16, colors.YELLOW if highlighted else colors.TEXT_MUTED)
        for node, (x, y) in points.items():
            self._node(node, x, y, node in self.code_path if code_scene else node == active)

    def _draw_heap_outline(self):
        points = self._heap_positions(self.heap)
        # 루트 카드와 배열 인덱스만 감싸고, 아래로 뻗는 가지는 포함하지 않는다.
        pygame.draw.rect(self.screen, colors.BLUE,
                         self.view.rect(80, 132, 1440, 58 if self.dense else 70),
                         width=max(1, self.view.length(2)), border_radius=self.view.length(5))
        self.text("최소 힙 배열", 80, 100, 21, colors.BLUE, True)
        self.right_text(f"힙에 남은 항목: {len(self.heap)}개", 1520, 100, 21, colors.BLUE, True)
        return points

    def draw_content(self):
        if not hasattr(self, "scene"):
            return
        self.text("Huffman Coding", 65, 35, 42, bold=True)
        if self.scene in ("decode", "decode_byte", "decode_bit", "decode_leaf", "decode_output"):
            self._draw_decoding()
            return
        if self.scene in ("encode", "encode_fly", "encode_scroll", "byte_drop"):
            self._draw_encoding()
            return
        if self.scene == "save":
            self._draw_bytes()
            return
        if self.scene in ("source", "group", "table"):
            if self.scene == "table":
                self.text("문자별 빈도표", 80, 165, 24, colors.BLUE, True)
                for char, index in self.char_index.items():
                    x, y = self._table_position(index)
                    color = self.palette[index % len(self.palette)]
                    width = min(124, 1440 / self.table_columns - 8)
                    self.rect(x - width / 2, y - 45, width, 90, colors.PANEL, color, radius=5)
                    self.centered_text(self._symbol(char), x, y - 20, 23, color, True)
                    self.centered_text(self.counts[char], x, y + 19, 24, bold=True)
                return
            occurrences = {}
            columns = max(38, (len(self.source) + 10) // 11)
            compact = columns > 38
            for i, char in enumerate(self.source):
                x, y = self._cell(i, columns, 80, 135, min(39, 1440 / columns), 43)
                if self.scene == "group":
                    index = self.char_index[char]
                    rank = occurrences.get(char, 0)
                    occurrences[char] = rank + 1
                    tx, ty = self._table_position(index)
                    if self.dense:
                        tx += (rank % 12 - 5.5) * (120 / self.table_columns)
                        ty += (rank // 12) * 4 - 48
                    elif compact:
                        tx += (rank % 12 - 5.5) * 10
                        ty += (rank // 12) * 10 - 105
                    else:
                        tx += (rank % 9 - 4) * 10
                        ty += (rank // 9) * 13 - 40
                    x += (tx - x) * self.progress
                    y += (ty - y) * self.progress
                    color = self.palette[index % len(self.palette)]
                else:
                    color = colors.TEXT
                if self.dense and self.scene == "group" and self.progress > 0.85:
                    pygame.draw.circle(self.screen, color, self.view.point(x, y), 1)
                else:
                    symbol = "¶" if self.dense and char == "\n" else self._symbol(char, compact=True)
                    self.centered_text(symbol, x, y, 10 if self.dense else 11 if compact else 16, color)
            return
        heap_points = self._draw_heap_outline()
        if self.scene == "heap_motion":
            t = self.progress
            points = {node: (x + (tx - x) * t, y + (ty - y) * t)
                      for node, ((x, y), (tx, ty)) in self.motion.items()}
            # 부모를 합치는 장면에는 힙에 남아 있는 다른 트리도 그대로 그린다.
            points = heap_points | points
            self._draw_forest(points, self.tree)
        else:
            points = heap_points
            for i, (_, node) in enumerate(self.heap):
                x, y = points[node]
                self.centered_text(f"[{i}]", x, y - 30, 14, colors.TEXT_MUTED)
            self._draw_forest(points, self.heap[0][1] if self.heap else None)
            roots = [self.tree] if self.scene == "joined" else self.taken
            top = 350 if self.scene == "joined" else 410
            self._draw_forest(self._forest_positions(roots, top), self.tree)
        if self.scene in ("codes", "code_motion"):
            self._draw_codes()
