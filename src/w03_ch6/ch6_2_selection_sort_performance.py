def selection_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 선택 정렬은 아직 정렬되지 않은 구간에서 가장 작은 값을 찾아 앞쪽으로 옮깁니다.
    n = len(array)

    # 모든 위치에 대해 pass를 진행합니다.
    # left는 이번 pass에서 값을 확정할 위치입니다.
    for left in range(n):
        # 처음에는 left 위치의 값을 최솟값 후보로 둡니다.
        min_at = left

        # left 오른쪽의 아직 정렬되지 않은 값들을 끝까지 비교합니다.
        for right in range(left + 1, n):
            if array[min_at] > array[right]:
                min_at = right

        # 남은 구간에서 찾은 최솟값을 left 위치로 옮깁니다.
        array[left], array[min_at] = array[min_at], array[left]

    return array
