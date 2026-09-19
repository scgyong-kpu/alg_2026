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
    # 다음 단계에서 array[root]와 array[largest]를 비교합니다.


def heap_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 힙 정렬은 배열을 Max Heap으로 만든 뒤 최대값을 뒤로 보냅니다.
    count = len(array)

    # 배열 index를 완전 이진 트리의 부모와 자식 관계로 보여 줍니다.
    vis.build_tree()

    # index 0을 root로 잡으면 왼쪽 자식의 index는 2 * root + 1입니다.
    root = 0
    heapify(array, root, count)

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", heap_sort(array))
    # vis.finish()
    vis.wait()
