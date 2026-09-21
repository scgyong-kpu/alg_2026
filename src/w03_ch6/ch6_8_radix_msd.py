import pyvisalgo as va


DATA_FILE = "data/radix_msd_words.json"

vis = va.visualizer("radix_msd_words")


def radix_sort_msd(words):
    # MSD 기수 정렬은 첫 글자부터 같은 글자 구간을 재귀적으로 정렬합니다.
    # 이후 커밋에서 현재 구간을 bucket으로 나누는 과정을 구현합니다.
    return words


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    words = list(data.array)

    vis.setup(data)
    print("정렬 전:", words)
    print("정렬 후:", radix_sort_msd(words))
    vis.wait()
