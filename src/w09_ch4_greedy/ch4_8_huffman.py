"""문자 빈도가 가장 낮은 두 트리를 반복해서 합쳐 허프만 트리를 만든다."""

from collections import Counter

import pyvisalgo as va


def huffman(text, vis):
    """원문에서 문자마다 몇 번 등장하는지 센다."""
    # counts는 문자를 key로, 등장 횟수를 value로 갖는 Counter 객체입니다.
    # 공백·줄바꿈도 하나의 문자이며, 대문자와 소문자는 서로 다른 문자입니다.
    counts = Counter(text)
    vis.group(counts)


if __name__ == "__main__":
    vis = va.visualizer("huffman")
    while va.running():
        data = va.next_data(__file__)
        # text는 공백과 줄바꿈을 포함한 원문입니다.
        vis.setup(data)
        if not vis.stopped():
            huffman(data.text, vis)
        # R: 재실행, D: 다음 데이터, Space: 일시정지, .: 한 단계.
        # Enter: 다음 구간, 1~9: 속도, +/-: 글씨 크기, Esc: 종료.
        vis.wait()
