import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("insertion_sort")


def insertion_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 삽입 정렬은 왼쪽의 정렬된 구간에 새 값을 알맞은 위치로 끼워 넣습니다.
    n = len(array)

    # 두 번째 값부터 차례로 왼쪽의 정렬된 구간에 삽입합니다.
    right = 1
    while right < n:
        insert_value = array[right]
        insert_at = right
        vis.mark_end(right, pick=True)

        # 삽입할 값보다 큰 값들은 오른쪽으로 한 칸씩 밀어냅니다.
        while insert_at > 0:
            left = insert_at - 1
            vis.compare(left, insert_at)
            if array[left] <= insert_value:
                break
            vis.shift(left, insert_at)
            array[insert_at] = array[left]
            insert_at -= 1

        # 밀어내기가 끝나면 비워진 위치에 후보 값을 넣습니다.
        vis.shift(right, insert_at, pick=True)
        array[insert_at] = insert_value
        right += 1

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", insertion_sort(array))
    vis.finish()
    vis.wait()
