# Hibbard 수열: 2^k - 1 형태입니다.
HIBBARD_GAPS = [
    524287, 262143, 131071, 65535, 32767, 16383, 8191, 4095,
    2047, 1023, 511, 255, 127, 63, 31, 15, 7, 3, 1,
]

# Ciura 수열: 작은 배열의 평균 실행 시간을 대상으로 찾은 수열입니다.
CIURA_GAPS = [1750, 701, 301, 132, 57, 23, 10, 4, 1]

# Tokuda 수열: 큰 배열까지 확장해 성능을 측정하기에 적합한 수열입니다.
TOKUDA_GAPS = [
    776591, 345152, 153401, 68178, 30301, 13467, 5985, 2660,
    1182, 525, 233, 103, 46, 20, 9, 4, 1,
]


def gaps(count, gap_values):
    # 배열 길이의 절반보다 작은 첫 gap부터 마지막 gap 1까지 사용합니다.
    if count <= 7:
        return [1]

    limit = count // 2
    for index, gap in enumerate(gap_values):
        if gap < limit:
            return gap_values[index:]

    return [1]


def shell_sort(array, gap_values=TOKUDA_GAPS):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 셸 정렬은 gap 간격으로 나눈 부분 배열에 삽입 정렬을 적용합니다.
    count = len(array)

    # 배열 길이와 선택한 gap 수열에 맞는 gap을 큰 값부터 차례로 적용합니다.
    for gap in gaps(count, gap_values):
        for start in range(gap, count):
            insert_value = array[start]
            insert_at = start

            # gap만큼 왼쪽의 값과 비교하며 후보 값을 삽입할 위치를 찾습니다.
            while insert_at >= gap:
                left = insert_at - gap
                if array[left] <= insert_value:
                    break
                array[insert_at] = array[left]
                insert_at -= gap

            array[insert_at] = insert_value

    return array
