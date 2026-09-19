import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("heap_sort")


def heapify(array, root, count):
    # 부모 index가 root이면 왼쪽 자식의 index는 2 * root + 1입니다.
    left = root * 2 + 1

    # 왼쪽 자식이 없으면 자식이 하나도 없는 leaf이므로 heapify를 끝냅니다.
    if left >= count:
        return

    # 지금 heapify하는 subtree의 root를 시각화에 표시합니다.
    vis.set_root(root)

    # 오른쪽 자식의 index는 2 * root + 2입니다.
    right = root * 2 + 2

    # 왼쪽 자식은 이미 존재하므로 우선 더 큰 자식의 후보로 정합니다.
    largest = left

    # 오른쪽 자식이 있을 때만 두 자식의 값을 비교합니다.
    if right < count:
        vis.compare(left, right)

        # 오른쪽 자식이 더 크면 부모와 비교할 후보를 오른쪽으로 바꿉니다.
        if array[right] > array[largest]:
            largest = right

    # largest에는 두 자식 중 더 큰 값의 index가 남습니다.
    # 이제 부모와 이 후보만 비교하면 heap 조건을 확인할 수 있습니다.
    vis.compare(root, largest)

    # 더 큰 자식이 부모보다 크면 max heap 조건이 깨진 상태입니다.
    if array[largest] > array[root]:
        # 시각화와 실제 배열에서 같은 두 값을 교환합니다.
        vis.swap(root, largest)
        array[root], array[largest] = array[largest], array[root]

        # 부모 값이 largest 위치로 내려갔으므로 그 subtree를 다시 heapify합니다.
        heapify(array, largest, count)


def heap_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 힙 정렬은 배열을 Max Heap으로 만든 뒤 최대값을 뒤로 보냅니다.
    count = len(array)

    # 배열 index를 완전 이진 트리의 부모와 자식 관계로 보여 줍니다.
    vis.build_tree()

    # heapify는 두 자식 subtree가 이미 heap이라는 전제에서 root까지 heap으로 만듭니다.
    # 따라서 자식이 없는 leaf에 가까운 작은 subtree부터 부모 방향으로 처리해야 합니다.
    if count > 1:
        # count // 2부터 마지막 index까지는 왼쪽 자식도 없는 leaf입니다.
        # 그 바로 앞 count // 2 - 1이 자식을 가진 마지막 부모입니다.
        # 마지막 부모부터 root #0까지 모든 부모 subtree를 heapify합니다.
        for root in range(count // 2 - 1, -1, -1):
            heapify(array, root, count)

    # 모든 부모 subtree가 heap 상태가 되었으므로 배열 전체가 Max Heap입니다.
    vis.finish_build_heap()

    # root의 최대값을 heap 마지막 원소와 바꿔 배열의 맨 뒤로 보냅니다.
    if count > 1:
        last = count - 1
        vis.swap(0, last)
        array[0], array[last] = array[last], array[0]

        # 마지막 원소는 최대값으로 확정되었으므로 heap 크기를 하나 줄입니다.
        vis.set_tree_size(last)

        # 마지막 원소가 root로 왔으므로 줄어든 heap에서 Max Heap 조건을 다시 회복합니다.
        if last > 1:
            heapify(array, 0, last)
        vis.finish_downheap()

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", heap_sort(array))
    # vis.finish()
    vis.wait()
