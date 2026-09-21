import pyvisalgo as va


DATA_FILE = "data/count_sort.json"

vis = va.visualizer("count_sort")


def count_sort(array):
    # 계수 정렬은 값을 서로 비교하지 않고 각 값의 개수를 세어 정렬합니다.
    # 값 v를 counts[v]에 기록할 수 있도록 최댓값까지의 칸을 준비합니다.
    counts = [0] * (max(array) + 1)
    vis.init_counts(counts)

    # 배열을 왼쪽부터 한 번 훑으며, 값마다 대응하는 counts 칸을 증가시킵니다.
    for index, value in enumerate(array):
        counts[value] += 1
        vis.count_value(index, value, counts)

    # 이제 counts[v]에는 값 v가 입력 배열에 등장한 횟수가 기록되어 있습니다.
    vis.finish_counting()

    # 왼쪽 칸부터 차례로 더합니다.
    # 이렇게 누적하면 counts[v]는 값 v 이하 원소의 개수가 됩니다.
    vis.start_accumulate()
    for right in range(1, len(counts)):
        left = right - 1
        counts[right] += counts[left]
        vis.accumulate(left, right, counts)

    # 모든 누적합이 완성되면 counts는 결과 배열의 위치 정보가 됩니다.
    vis.finish_accumulate(counts)

    # 원본 배열과 같은 길이의 결과 배열을 비어 있는 칸으로 준비합니다.
    result = [None] * len(array)
    vis.init_result(result)

    # 같은 값을 가진 원소의 원래 순서를 보존하기 위해 뒤에서부터 읽습니다.
    for index in range(len(array) - 1, -1, -1):
        value = array[index]

        # counts[value]는 value 이하 원소의 개수이므로, 1을 줄이면 삽입 위치가 됩니다.
        counts[value] -= 1
        at = counts[value]
        result[at] = value
        vis.place_value(index, value, at, counts, result)

    # result에 완성된 오름차순 결과를 원본 배열에 반영합니다.
    array[:] = result
    vis.finish()
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", count_sort(array))
    vis.wait()
