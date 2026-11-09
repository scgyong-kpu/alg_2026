"""문자 빈도가 가장 낮은 두 트리를 반복해서 합쳐 허프만 트리를 만든다."""

from collections import Counter
from heapq import heapify, heappop, heappush

import pyvisalgo as va


def huffman(text, vis):
    """최소 빈도 노드 두 개를 꺼내 빈도 합을 가진 부모에 연결한다."""
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
    # 첫 번째로 꺼낸 노드의 빈도와 고유 번호를 각각 받습니다.
    # heappop은 루트의 최소 항목을 제거하고, 남은 항목의 힙 조건도 유지합니다.
    if heap and not vis.stopped():
        first_count, first = heappop(heap)
        vis.pop(heap, first, 1)
    # 첫 노드를 제거한 뒤의 힙에서 다시 최솟값을 꺼냅니다.
    # 두 번째로 꺼낸 노드는 first와 다른 노드이며, 이후 새 부모의 다른 자식이 됩니다.
    if heap and not vis.stopped():
        second_count, second = heappop(heap)
        vis.pop(heap, second, 2)
        if not vis.stopped():
            # nodes의 번호는 0부터 연속이므로 현재 노드 수가 새 부모의 고유 번호입니다.
            parent = len(nodes)
            count = first_count + second_count
            # 내부 노드는 특정 문자를 뜻하지 않아 문자 자리에 None을 둡니다.
            # 자식 정보는 왼쪽·오른쪽 자식의 고유 번호를 담은 튜플입니다.
            nodes[parent] = (count, None, (first, second))
            vis.join(parent)
            if not vis.stopped():
                # 새 트리도 잎 노드와 같은 (빈도, 고유 번호) 형식으로 후보에 넣습니다.
                # 자식 정보는 nodes에 그대로 남아 있으므로 트리 전체가 유지됩니다.
                heappush(heap, (count, parent))
                vis.push(heap, parent)


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
