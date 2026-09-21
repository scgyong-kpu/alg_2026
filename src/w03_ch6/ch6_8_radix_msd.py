import pyvisalgo as va


DATA_FILE = "data/radix_msd_words.json"

vis = va.visualizer("radix_msd_words")


def radix_sort_msd(words):
    # MSD 기수 정렬은 첫 글자부터 같은 글자 구간을 재귀적으로 정렬합니다.
    # 단어를 1열 배열로 전환하면 재귀 구간의 범위를 위아래로 확인할 수 있습니다.
    vis.line_up()

    # 첫 호출은 모든 단어를 포함하는 depth 0 구간을 스택에 넣습니다.
    vis.push(0, len(words) - 1, 0)

    # 이후 커밋에서 이 구간의 첫 글자를 bucket으로 나눕니다.
    return words


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    words = list(data.array)

    vis.setup(data)
    print("정렬 전:", words)
    print("정렬 후:", radix_sort_msd(words))
    vis.wait()
