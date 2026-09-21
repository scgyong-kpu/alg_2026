import pyvisalgo as va


DATA_FILE = "data/count_sort.json"

vis = va.visualizer("count_sort")


def count_sort(array):
    # 계수 정렬은 값을 서로 비교하지 않고 각 값의 개수를 세어 정렬합니다.
    # 값 v를 counts[v]에 기록할 수 있도록 최댓값까지의 칸을 준비합니다.
    counts = [0] * (max(array) + 1)
    vis.init_counts(counts)

    # 이후 커밋에서 각 원소를 읽어 counts 배열의 값을 증가시킵니다.
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", count_sort(array))
    vis.wait()
