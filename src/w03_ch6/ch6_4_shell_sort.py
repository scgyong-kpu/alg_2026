import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("shell_sort")


def shell_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 셸 정렬은 gap 간격으로 나눈 부분 배열에 삽입 정렬을 적용합니다.
    count = len(array)

    # gap 3으로 부분 배열을 정리한 뒤 gap 1로 전체 배열을 정렬합니다.
    for gap in [3, 1]:
      vis.set_gap(gap)

      for offset in range(gap):
        vis.set_group(offset)
        start = offset + gap
        while start < count:
            insert_value = array[start]
            insert_at = start
            vis.mark_end(start, pick=True)

            # gap만큼 왼쪽의 값과 비교하며 후보 값을 삽입할 위치를 찾습니다.
            while insert_at >= gap:
                left = insert_at - gap
                vis.compare(left, insert_at)
                if array[left] <= insert_value:
                    break
                vis.shift(left, insert_at)
                array[insert_at] = array[left]
                insert_at -= gap

            vis.shift(start, insert_at, pick=True)
            array[insert_at] = insert_value
            start += gap

      vis.finish_gap()

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", shell_sort(array))
    vis.finish()
    vis.wait()
