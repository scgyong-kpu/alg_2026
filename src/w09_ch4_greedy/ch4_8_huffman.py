"""문자 빈도가 가장 낮은 두 트리를 반복해서 합쳐 허프만 트리를 만든다."""

from collections import Counter
from heapq import heapify

import pyvisalgo as va


def huffman(text, vis):
    """문자별 빈도를 집계하고 각 문자를 잎 노드로 만들어 최소 힙을 구성한다."""
    # counts는 문자를 key로, 등장 횟수를 value로 갖는 Counter 객체입니다.
    # 공백·줄바꿈도 하나의 문자이며, 대문자와 소문자는 서로 다른 문자입니다.
    counts = Counter(text)
    vis.group(counts)
    # nodes는 고유 번호를 key로 갖는 노드 사전입니다.
    # 각 value는 (빈도, 문자, 자식 정보)이며, 잎에는 자식이 없어 None을 넣습니다.
    # 문자가 처음 등장한 순서대로 0부터 번호를 부여합니다.
    nodes = {i: (count, char, None) for i, (char, count) in enumerate(counts.items())}
    # 힙에는 노드 자체가 아니라 (빈도, 고유 번호)를 저장합니다.
    # 빈도가 같으면 고유 번호로 비교하므로, 자식 정보 등을 비교할 필요가 없습니다.
    heap = [(count, i) for i, (count, _, _) in nodes.items()]
    # heapify는 목록을 직접 최소 힙으로 바꿉니다. 목록 전체를 정렬하는 것은 아닙니다.
    heapify(heap)
    vis.make_heap(heap, nodes)


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
