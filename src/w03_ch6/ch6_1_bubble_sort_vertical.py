import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("bubble_sort_vertical")


def bubble_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # Python에서 리스트는 mutable 객체이므로, 함수 안에서 바꾼 내용이 호출한 쪽에도 보입니다.
    n = len(array)

    # 한 번의 pass가 끝날 때마다 가장 큰 값 하나가 아래쪽 끝으로 이동합니다.
    # sorted_index는 이번 pass에서 마지막으로 비교에 참여하는 위치입니다.
    for sorted_index in range(n - 1, 0, -1):
        pass_index = n - 1 - sorted_index
        vis.start_pass(pass_index, sorted_index + 1)

        # 이웃한 두 칸을 위에서 아래로 차례대로 비교합니다.
        for upper in range(sorted_index):
            lower = upper + 1
            vis.compare(upper, lower)

            # 위쪽 값이 더 크면 두 값을 바꿉니다.
            # 큰 값은 한 칸 아래로 이동하고, 작은 값은 한 칸 위로 이동합니다.
            if array[upper] > array[lower]:
                vis.swap(upper, lower)
                array[upper], array[lower] = array[lower], array[upper]

        # 이번 pass에서 가장 큰 값이 sorted_index 위치까지 밀려났습니다.
        # 다음 pass에서는 이 위치의 아래쪽을 다시 비교하지 않아도 됩니다.
        vis.mark_sorted(sorted_index)

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", bubble_sort(array))
    vis.finish()
    vis.wait()
