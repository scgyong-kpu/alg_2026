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

    # 이후 커밋에서 등장 횟수를 누적합으로 바꿉니다.
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", count_sort(array))
    vis.wait()
