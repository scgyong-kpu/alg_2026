import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("bubble_sort")


def bubble_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # Python에서 리스트는 mutable 객체이므로, 함수 안에서 바꾼 내용이 호출한 쪽에도 보입니다.
    n = len(array)

    # 한 번의 pass가 끝날 때마다 가장 큰 값 하나가 오른쪽 끝으로 이동합니다.
    # sorted_index는 이번 pass에서 마지막으로 비교에 참여하는 위치입니다.
    for sorted_index in range(n - 1, 0, -1):
        pass_index = n - 1 - sorted_index
        vis.start_pass(pass_index, sorted_index + 1)

        # 이웃한 두 칸을 왼쪽에서 오른쪽으로 차례대로 비교합니다.
        for left in range(sorted_index):
            right = left + 1
            vis.compare(left, right)

            # 왼쪽 값이 더 크면 두 값을 바꿉니다.
            # 큰 값은 한 칸 오른쪽으로 이동하고, 작은 값은 한 칸 왼쪽으로 이동합니다.
            if array[left] > array[right]:
                vis.swap(left, right)
                array[left], array[right] = array[right], array[left]

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", bubble_sort(array))
    vis.finish()
    vis.wait()
