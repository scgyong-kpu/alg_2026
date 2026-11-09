"""문자 빈도가 가장 낮은 두 트리를 반복해서 합쳐 허프만 트리를 만든다."""

from collections import Counter
from heapq import heapify, heappop, heappush

import pyvisalgo as va


def huffman(text, vis):
    """허프만 트리를 만들고 (노드 사전, 루트 번호)를 반환한다."""
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
    # 후보가 두 개 이상일 때만 두 번 꺼낼 수 있습니다.
    # 두 트리를 빼고 하나를 넣으므로, 매번 힙의 항목 수가 하나씩 줄어듭니다.
    while len(heap) > 1 and not vis.stopped():
        # 첫 번째로 꺼낸 노드의 빈도와 고유 번호를 각각 받습니다.
        # heappop은 루트의 최소 항목을 제거하고, 남은 항목의 힙 조건도 유지합니다.
        first_count, first = heappop(heap)
        vis.pop(heap, first, 1)
        if vis.stopped():
            return
        # 첫 노드를 제거한 뒤의 힙에서 다시 최솟값을 꺼냅니다.
        # 두 번째로 꺼낸 노드는 first와 다른 노드이며, 이후 새 부모의 다른 자식이 됩니다.
        second_count, second = heappop(heap)
        vis.pop(heap, second, 2)
        if vis.stopped():
            return
        # nodes의 번호는 0부터 연속이므로 현재 노드 수가 새 부모의 고유 번호입니다.
        parent = len(nodes)
        count = first_count + second_count
        # 내부 노드는 특정 문자를 뜻하지 않아 문자 자리에 None을 둡니다.
        # 자식 정보는 왼쪽·오른쪽 자식의 고유 번호를 담은 튜플입니다.
        nodes[parent] = (count, None, (first, second))
        vis.join(parent)
        if vis.stopped():
            return
        # 새 트리도 잎 노드와 같은 (빈도, 고유 번호) 형식으로 후보에 넣습니다.
        # 자식 정보는 nodes에 그대로 남아 있으므로 트리 전체가 유지됩니다.
        heappush(heap, (count, parent))
        vis.push(heap, parent)
    if heap and not vis.stopped():
        # 힙의 마지막 항목은 (전체 빈도, 루트 번호)입니다.
        # 루트 번호로 nodes를 조회하고 자식 번호를 따라가면 전체 트리를 얻습니다.
        root = heap[0][1]
        return nodes, root
    if not vis.stopped():
        return nodes, None  # 빈 원문에는 노드와 루트가 없습니다.


def make_codes(nodes, root):
    """트리를 순회하여 {문자: 비트 문자열} 코드표를 반환한다."""
    codes = {}

    def visit(node, prefix):
        # node는 현재 노드 번호, prefix는 루트부터 이 노드까지 읽은 비트입니다.
        _, char, children = nodes[node]
        if children is None:
            # 문자 종류가 하나뿐이면 루트 자체가 잎이어서 prefix가 빈 문자열입니다.
            # 이 경우에도 문자 수를 복원할 수 있도록 코드 0을 부여합니다.
            codes[char] = prefix or "0"
            return
        left, right = children
        visit(left, prefix + "0")
        visit(right, prefix + "1")

    if root is not None:
        visit(root, "")
    return codes


def encode(text, codes):
    """원문의 각 문자를 코드로 바꾸어 하나의 비트 문자열로 이어 붙인다."""
    # 여기서 0과 1은 설명용 문자열입니다. 실제 바이트로 압축하는 단계와 구별합니다.
    return "".join(codes[char] for char in text)


def decode(bits, nodes, root):
    """비트 문자열을 트리로 읽어 원문을 복원한다. 패딩을 제외한 비트만 받는다."""
    if root is None:
        if bits:
            raise ValueError("트리 없이 비트를 디코딩할 수 없습니다.")
        return ""
    # 루트 자체가 잎인 예외: 코드 0 하나가 문자 하나를 나타냅니다.
    if nodes[root][2] is None:
        if any(bit != "0" for bit in bits):
            raise ValueError("문자가 한 종류인 트리의 코드는 0입니다.")
        return nodes[root][1] * len(bits)

    letters = []  # 잎에 도착할 때마다 확정한 문자를 모읍니다.
    node = root  # 아직 읽고 있는 코드에 따라 현재 위치가 바뀝니다.
    for bit in bits:
        if bit not in "01":
            raise ValueError("비트 문자열에는 0과 1만 사용할 수 있습니다.")
        # 내부 노드의 자식 튜플은 (왼쪽 번호, 오른쪽 번호) 순서입니다.
        left, right = nodes[node][2]
        node = left if bit == "0" else right
        _, char, children = nodes[node]
        if children is None:
            letters.append(char)
            # 문자 하나를 읽었으므로 다음 비트는 다시 루트에서부터 해석합니다.
            node = root
    if node != root:
        raise ValueError("마지막 비트가 잎에 도착하기 전에 끝났습니다.")
    return "".join(letters)


if __name__ == "__main__":
    vis = va.visualizer("huffman")
    while va.running():
        data = va.next_data(__file__)
        # text는 공백과 줄바꿈을 포함한 원문입니다.
        vis.setup(data)
        if not vis.stopped():
            result = huffman(data.text, vis)
            if not vis.stopped():
                nodes, root = result
                codes = make_codes(nodes, root)
                bits = encode(data.text, codes)
                restored = decode(bits, nodes, root)
                print("코드표:", codes)
                print("인코딩:", bits)
                print("디코딩:", restored)
                print("원문과 일치:", restored == data.text)
                assert restored == data.text
                # 계산과 검증은 학생 코드에서 수행하고, 연출은 시각화에 맡깁니다.
                if root is not None:
                    vis.finish(root)
        # R: 재실행, D: 다음 데이터, Space: 일시정지, .: 한 단계.
        # Enter: 다음 구간, 1~9: 속도, +/-: 글씨 크기, Esc: 종료.
        # 트리 생성 중 Enter는 다음 부모 push까지 진행합니다.
        # 인코딩 중 첫 Enter는 가속, 두 번째는 남은 애니메이션 생략입니다.
        # Shift+Enter: 디코딩 시작으로 이동. 디코딩 중에는 일반 Enter처럼 동작합니다.
        vis.wait()
