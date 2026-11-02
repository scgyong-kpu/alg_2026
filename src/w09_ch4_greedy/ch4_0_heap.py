"""최소 힙 연산과 부호 반전을 이용한 최댓값 추출을 실습한다."""

import heapq

import pyvisalgo as va


# Python 3.14부터 heapify_max, heappush_max, heappop_max도 공식 지원합니다.
# 이 예제는 Python 3.13에서도 실행하도록 최소 힙 API만 사용합니다.
if __name__ == "__main__":
    vis = va.visualizer("heap_queue")
    while va.running():
        data = va.next_data(__file__)
        heap = data.array.copy()
        pushes = data.pushes
        # 원소가 [비용, 이름] 배열이면 비용부터 비교하고, 같으면 이름을 비교합니다.
        # 예: [2, 'A'] < [2, 'B'] < [5, 'A']. 이름을 무시하는 것이 아닙니다.
        # 같은 위치에서 비교되는 항목들은 서로 비교 가능한 자료형이어야 합니다.
        if data.element_type == "negated":
            # a > b이면 -a < -b입니다. 큰 원래 값이 작은 저장값이 됩니다.
            # 초기 원소뿐 아니라 이후 추가할 원소도 같은 규칙으로 변환합니다.
            heap = [-value for value in heap]
            pushes = [-value for value in pushes]
        vis.setup(data, heap)
        print("준비:", heap)

        # heapify는 리스트 자체를 최소 힙으로 바꾸며, 반환값은 None입니다.
        # heap = heapq.heapify(heap)처럼 반환값을 대입하면 안 됩니다.
        # 모든 부모가 자식보다 작거나 같고, 루트 heap[0]에는 최솟값이 있습니다.
        # 형제 사이의 순서까지 정해지는 것은 아니므로 전체 정렬과는 다릅니다.
        heapq.heapify(heap)
        vis.heapify(heap)
        print("heapify:", heap)

        for value in pushes:
            if vis.stopped():
                break
            # 맨 뒤에 추가한 뒤 부모보다 작으면 위로 올립니다(up-heap).
            # 부모의 인덱스는 (child - 1) // 2이며, 루트까지 최대 O(log n)입니다.
            # append만 하면 힙 조건이 깨질 수 있으므로 heappush를 사용합니다.
            heapq.heappush(heap, value)
            vis.push(heap, value)
            print("push:", value, "→", heap)

        for _ in range(min(data.pop_count, len(heap))):
            if vis.stopped():
                break
            # 루트의 최솟값을 반환하며 리스트 길이가 하나 줄어듭니다.
            # 마지막 원소로 루트를 채운 뒤 작은 자식 쪽으로 내려갑니다(down-heap).
            # 최대 O(log n)이며, 빈 힙에서 호출하면 IndexError가 발생합니다.
            # heap[0]으로 읽기만 하는 것과 달리 실제로 원소를 제거합니다.
            value = heapq.heappop(heap)
            vis.pop(heap, value)
            if data.element_type == "negated":
                # 최소 저장값의 부호를 복원하면 원래 값의 최댓값입니다.
                print("pop 반환:", value, "원래 값:", -value, "남은 힙:", heap)
            else:
                print("pop 반환:", value, "남은 힙:", heap)

        # Space: 일시정지, .: 한 단계, Enter: 현재 연산까지 빠르게 진행.
        # R: 다시 실행, D: 다음 데이터, 1-9: 속도, +/-: 글씨, Esc: 종료.
        vis.wait()
