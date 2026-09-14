import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("selection_sort")


def selection_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 선택 정렬은 아직 정렬되지 않은 구간에서 가장 작은 값을 찾아 앞쪽으로 옮깁니다.
    n = len(array)

    # 먼저 한 번의 pass만 살펴봅니다.
    # left는 이번 pass에서 값을 확정할 위치입니다.
    for left in range(1):
        # 처음에는 left 위치의 값을 최솟값 후보로 둡니다.
        min_at = left
        vis.selection(min_at)

        # left 오른쪽의 아직 정렬되지 않은 값들을 끝까지 비교합니다.
        for right in range(left + 1, n):
            vis.compare(min_at, right)
            if array[min_at] > array[right]:
                min_at = right
                vis.selection(min_at)

        # 남은 구간에서 찾은 최솟값을 left 위치로 옮깁니다.
        vis.swap(left, min_at)
        array[left], array[min_at] = array[min_at], array[left]
        vis.mark_sorted(left)

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", selection_sort(array))
    # vis.finish() 
    vis.wait()
