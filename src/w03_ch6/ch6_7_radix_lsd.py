import pyvisalgo as va


DATA_FILE = "data/radix_lsd.json"

vis = va.visualizer("radix_lsd")


def digit_at(number, div):
    # div가 1이면 1의 자리, 10이면 10의 자리 digit을 얻습니다.
    return number // div % 10


def counting_sort_by_digit(array, div, pass_no, total_passes):
    # 한 자리수 digit을 기준으로 계수 정렬을 한 번 수행합니다.
    vis.start_digit(pass_no, total_passes, div)

    # 0부터 9까지 가능한 digit의 등장 횟수를 셉니다.
    counts = [0] * 10
    vis.init_counts(counts)
    for index, number in enumerate(array):
        digit = digit_at(number, div)
        counts[digit] += 1
        vis.count_digit(index, number, digit, counts)
    vis.finish_counting()

    # counts[digit]를 digit 이하 원소의 개수로 바꿔 result의 위치 정보로 사용합니다.
    vis.start_accumulate()
    for right in range(1, len(counts)):
        left = right - 1
        counts[right] += counts[left]
        vis.accumulate(left, right, counts)
    vis.finish_accumulate(counts)

    # 뒤에서부터 배치하면 같은 1의 자리 digit을 가진 수의 기존 순서가 유지됩니다.
    result = [None] * len(array)
    vis.init_result(result)
    for index in range(len(array) - 1, -1, -1):
        number = array[index]
        digit = digit_at(number, div)
        counts[digit] -= 1
        at = counts[digit]
        result[at] = number
        vis.place_digit(index, number, digit, at, counts, result)
    vis.finish_result(result)
    vis.result_to_array(result)
    array[:] = result


def radix_sort_lsd(array):
    # 최대 자리수만큼 1, 10, 100, ... 순으로 안정 정렬을 반복합니다.
    total_passes = len(str(max(array)))
    div = 1
    for pass_no in range(1, total_passes + 1):
        counting_sort_by_digit(array, div, pass_no, total_passes)
        div *= 10

    vis.finish()
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", radix_sort_lsd(array))
    vis.wait()
