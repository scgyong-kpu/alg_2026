import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("insertion_sort")


def insertion_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 삽입 정렬은 왼쪽의 정렬된 구간에 새 값을 알맞은 위치로 끼워 넣습니다.
    n = len(array)

    # 먼저 두 번째 값을 왼쪽의 정렬된 구간에 삽입하는 과정을 살펴봅니다.
    right = 1
    if right < n:
        vis.mark_end(right)
        left = right - 1
        while left >= 0:
            moving = left + 1
            vis.compare(left, moving)
            if array[left] > array[moving]:
                vis.swap(left, moving)
                array[left], array[moving] = array[moving], array[left]
            left -= 1

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", insertion_sort(array))
    vis.finish()
    vis.wait()
