import perf


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


if __name__ == "__main__":
    perf.test(selection_sort, 50000)


'''
Performance test results:
   Count     Sel
     100   0.000
    1000   0.007
    2000   0.027
    3000   0.061
    4000   0.110
    5000   0.174
    6000   0.250
    7000   0.345
    8000   0.453
    9000   0.569
   10000   0.710
   15000   1.585
   20000   2.790
   30000   6.338
   40000  11.258
   50000  17.528
'''
