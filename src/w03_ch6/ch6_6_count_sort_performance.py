import perf
from sort_data import limited_random_values


LARGE_COUNTS = [10_000_000, 20_000_000, 50_000_000, 100_000_000]


def count_sort(array):
    # counts[v]에는 값 v의 등장 횟수를 기록합니다.
    counts = [0] * (max(array) + 1)
    for value in array:
        counts[value] += 1

    # 누적합으로 바꾸면 counts[v]는 값 v 이하 원소의 개수가 됩니다.
    for index in range(1, len(counts)):
        counts[index] += counts[index - 1]

    # 원본을 뒤에서부터 읽어 result에 배치하면 같은 값의 원래 순서가 유지됩니다.
    result = [0] * len(array)
    for index in range(len(array) - 1, -1, -1):
        value = array[index]
        counts[value] -= 1
        result[counts[value]] = value

    array[:] = result
    return array


def large_count_sort_values(count):
    # 1천만 개 이상은 n / 100000 종류의 값만 사용합니다.
    # 예: 1천만 개는 0~99, 1억 개는 0~999의 값으로 구성합니다.
    value_count = count // 100_000
    return limited_random_values(count, value_count)


if __name__ == "__main__":
    # 100만 개까지는 다른 정렬과 같은 random 데이터와 perf.test() 방식을 사용합니다.
    # Create 열은 random 입력 배열을 준비하는 데 걸린 시간입니다.
    perf.test(count_sort, 1_000_000, measure_creation=True)

    # 대용량 구간은 원본 배열 복사 없이 생성한 배열을 바로 정렬해 메모리 사용을 줄입니다.
    # Values 열은 사용할 서로 다른 값의 개수입니다.
    perf.test_generated(
        count_sort,
        LARGE_COUNTS,
        large_count_sort_values,
        value_count_func=lambda count: count // 100_000,
    )


'''
Performance test results (seconds):
   Count     Create    Elapsed
     100      0.001      0.000
    1000      0.000      0.000
    2000      0.000      0.001
    3000      0.000      0.001
    4000      0.001      0.002
    5000      0.001      0.002
    6000      0.001      0.003
    7000      0.001      0.003
    8000      0.001      0.003
    9000      0.001      0.003
   10000      0.001      0.005
   15000      0.002      0.006
   20000      0.004      0.019
   30000      0.005      0.014
   40000      0.005      0.020
   50000      0.005      0.024
  100000      0.010      0.061
  200000      0.021      0.132
  300000      0.036      0.194
  400000      0.043      0.268
  500000      0.067      0.332
  750000      0.080      0.522
 1000000      0.135      0.742

 Larger performance test results (seconds):
     Count   Values     Create    Elapsed
  10000000      100      1.024      0.552
  20000000      200      2.026      1.121
  50000000      500      5.163      3.785
 100000000     1000     10.080      6.898
'''
