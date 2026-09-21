import perf


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


if __name__ == "__main__":
    perf.test(radix_sort_lsd, 1_000_000, measure_creation=True)
