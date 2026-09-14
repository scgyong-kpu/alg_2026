import perf
from sort_data import nearly_sorted_values


def insertion_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 삽입 정렬은 왼쪽의 정렬된 구간에 새 값을 알맞은 위치로 끼워 넣습니다.
    n = len(array)

    # 두 번째 값부터 차례로 왼쪽의 정렬된 구간에 삽입합니다.
    right = 1
    while right < n:
        insert_value = array[right]
        insert_at = right

        # 삽입할 값보다 큰 값들은 오른쪽으로 한 칸씩 밀어냅니다.
        while insert_at > 0:
            left = insert_at - 1
            if array[left] <= insert_value:
                break
            array[insert_at] = array[left]
            insert_at -= 1

        # 밀어내기가 끝나면 비워진 위치에 후보 값을 넣습니다.
        array[insert_at] = insert_value
        right += 1

    return array


if __name__ == "__main__":
    # perf.test(insertion_sort, 50000)                               # Ins
    perf.test(insertion_sort, 50000, data_func=nearly_sorted_values) # InsNS


'''
Performance test results:
   Count     Ins   InsNS
     100   0.000   0.000
    1000   0.007   0.002
    2000   0.028   0.003
    3000   0.063   0.005
    4000   0.114   0.006
    5000   0.177   0.008
    6000   0.257   0.009
    7000   0.352   0.010
    8000   0.464   0.012
    9000   0.586   0.013
   10000   0.725   0.015
   15000   1.655   0.022
   20000   2.934   0.029
   30000   6.608   0.044
   40000  11.698   0.058
   50000  18.518   0.073
'''
