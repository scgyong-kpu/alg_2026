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
        min_value = array[left]

        # left 오른쪽의 아직 정렬되지 않은 값들을 끝까지 비교합니다.
        for right in range(left + 1, n):
            value = array[right]
            if min_value > value:
                min_at = right
                min_value = value

        # 남은 구간에서 찾은 최솟값을 left 위치로 옮깁니다.
        array[left], array[min_at] = array[min_at], array[left]

    return array


if __name__ == "__main__":
    perf.test(selection_sort, 50000)

    # 실행 예:
    # python src/w03_ch6/ch6_2_selection_sort_performance.py
    # python src/w03_ch6/ch6_2_selection_sort_performance.py nearly
    # python src/w03_ch6/ch6_2_selection_sort_performance.py sorted
    # python src/w03_ch6/ch6_2_selection_sort_performance.py reversed


'''
Performance test results:
   Count     Sel   SelNS
     100   0.000   0.000
    1000   0.007   0.008
    2000   0.026   0.026
    3000   0.056   0.056
    4000   0.102   0.099
    5000   0.160   0.155
    6000   0.232   0.224
    7000   0.316   0.307
    8000   0.415   0.401
    9000   0.524   0.507
   10000   0.646   0.630
   15000   1.454   1.411
   20000   2.591   2.489
   30000   5.786   5.586
   40000  10.354   9.931
   50000  16.385  15.541
'''
