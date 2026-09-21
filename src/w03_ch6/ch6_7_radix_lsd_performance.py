import perf
from sort_data import limited_random_values


LARGE_COUNTS = [10_000_000, 20_000_000, 50_000_000]


def digit_at(number, div):
    # div가 1이면 1의 자리, 10이면 10의 자리 digit을 얻습니다.
    return number // div % 10


def counting_sort_by_digit(array, div):
    # 한 자리수 digit을 기준으로 계수 정렬을 한 번 수행합니다.
    counts = [0] * 10
    for number in array:
        digit = digit_at(number, div)
        counts[digit] += 1

    for right in range(1, len(counts)):
        counts[right] += counts[right - 1]

    # 뒤에서부터 배치하면 같은 digit을 가진 수의 기존 순서가 유지됩니다.
    result = [0] * len(array)
    for index in range(len(array) - 1, -1, -1):
        number = array[index]
        digit = digit_at(number, div)
        counts[digit] -= 1
        result[counts[digit]] = number
    array[:] = result


def radix_sort_lsd(array):
    # 최대 자리수만큼 1, 10, 100, ... 순으로 안정 정렬을 반복합니다.
    total_passes = len(str(max(array)))
    div = 1
    for _ in range(total_passes):
        counting_sort_by_digit(array, div)
        div *= 10

    return array


def large_radix_lsd_values(count):
    # n / 100000 종류의 값만 사용해 대용량 배열의 값 범위를 제한합니다.
    # 예: 1천만 개는 0~99, 5천만 개는 0~499의 값으로 구성합니다.
    value_count = count // 100_000
    return limited_random_values(count, value_count)


if __name__ == "__main__":
    perf.test(radix_sort_lsd, 1_000_000, measure_creation=True)

    # 대용량 구간은 원본 배열 복사 없이 생성한 배열을 바로 정렬합니다.
    perf.test_generated(
        radix_sort_lsd,
        LARGE_COUNTS,
        large_radix_lsd_values,
        value_count_func=lambda count: count // 100_000,
    )


'''
Performance test results (seconds):
   Count     Create    Elapsed
     100      0.000      0.000
    1000      0.000      0.000
    2000      0.000      0.001
    3000      0.000      0.002
    4000      0.001      0.002
    5000      0.001      0.003
    6000      0.001      0.004
    7000      0.001      0.004
    8000      0.001      0.005
    9000      0.001      0.005
   10000      0.001      0.006
   15000      0.002      0.010
   20000      0.002      0.014
   30000      0.004      0.022
   40000      0.005      0.031
   50000      0.005      0.038
  100000      0.011      0.088
  200000      0.022      0.201
  300000      0.037      0.319
  400000      0.042      0.493
  500000      0.068      0.625
  750000      0.082      1.196
 1000000      0.137      1.799

Larger performance test results (seconds):
     Count   Values     Create    Elapsed
  10000000      100      1.021      2.365
  20000000      200      2.043      6.978
  50000000      500      5.233     20.142
'''
