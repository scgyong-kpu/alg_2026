import perf


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


if __name__ == "__main__":
    perf.test(count_sort, 1_000_000)
