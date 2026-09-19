import perf


def heapify(array, root, count):
    # 부모 index가 root이면 왼쪽 자식의 index는 2 * root + 1입니다.
    left = root * 2 + 1

    # 왼쪽 자식이 없으면 자식이 하나도 없는 leaf이므로 heapify를 끝냅니다.
    if left >= count:
        return

    # 오른쪽 자식의 index는 2 * root + 2입니다.
    right = root * 2 + 2

    # 왼쪽 자식은 이미 존재하므로 우선 더 큰 자식의 후보로 정합니다.
    largest = left

    # 오른쪽 자식이 있을 때만 두 자식의 값을 비교합니다.
    if right < count:
        # 오른쪽 자식이 더 크면 부모와 비교할 후보를 오른쪽으로 바꿉니다.
        if array[right] > array[largest]:
            largest = right

    # largest에는 두 자식 중 더 큰 값의 index가 남습니다.
    # 이제 부모와 이 후보만 비교하면 heap 조건을 확인할 수 있습니다.
    # 더 큰 자식이 부모보다 크면 max heap 조건이 깨진 상태입니다.
    if array[largest] > array[root]:
        array[root], array[largest] = array[largest], array[root]

        # 부모 값이 largest 위치로 내려갔으므로 그 subtree를 다시 heapify합니다.
        heapify(array, largest, count)


def heap_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 힙 정렬은 배열을 Max Heap으로 만든 뒤 최대값을 뒤로 보냅니다.
    count = len(array)

    # heapify는 두 자식 subtree가 이미 heap이라는 전제에서 root까지 heap으로 만듭니다.
    # 따라서 자식이 없는 leaf에 가까운 작은 subtree부터 부모 방향으로 처리해야 합니다.
    if count > 1:
        # count // 2부터 마지막 index까지는 왼쪽 자식도 없는 leaf입니다.
        # 그 바로 앞 count // 2 - 1이 자식을 가진 마지막 부모입니다.
        # 마지막 부모부터 root #0까지 모든 부모 subtree를 heapify합니다.
        for root in range(count // 2 - 1, -1, -1):
            heapify(array, root, count)

    # heap 마지막 index를 하나씩 앞당기며 최대값을 정렬 완료 구간으로 보냅니다.
    for last in range(count - 1, 0, -1):
        # root의 최대값을 heap 마지막 원소와 바꿔 배열의 맨 뒤로 보냅니다.
        array[0], array[last] = array[last], array[0]

        # 마지막 원소가 root로 왔으므로 줄어든 heap에서 Max Heap 조건을 다시 회복합니다.
        if last > 1:
            heapify(array, 0, last)

    return array


if __name__ == "__main__":
    perf.test(heap_sort, 500000)

    # 실행 예:
    # python src/w03_ch6/ch6_5_heap_sort_performance.py
    # python src/w03_ch6/ch6_5_heap_sort_performance.py nearly
    # python src/w03_ch6/ch6_5_heap_sort_performance.py reversed


'''
Performance test results (seconds):
   Count   Random   Nearly Reversed
     100    0.000    0.000    0.000
    1000    0.001    0.001    0.001
    2000    0.002    0.002    0.001
    3000    0.003    0.003    0.002
    4000    0.004    0.004    0.004
    5000    0.005    0.005    0.004
    6000    0.006    0.006    0.005
    7000    0.007    0.007    0.006
    8000    0.009    0.008    0.007
    9000    0.010    0.009    0.008
   10000    0.011    0.011    0.010
   15000    0.018    0.017    0.015
   20000    0.024    0.023    0.021
   30000    0.037    0.036    0.033
   40000    0.051    0.049    0.045
   50000    0.065    0.062    0.057
  100000    0.144    0.133    0.122
  200000    0.322    0.281    0.264
  300000    0.519    0.436    0.411
  400000    0.745    0.596    0.562
  500000    0.983    0.754    0.719
'''
