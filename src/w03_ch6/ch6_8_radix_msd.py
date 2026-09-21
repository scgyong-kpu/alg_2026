import pyvisalgo as va


DATA_FILE = "data/radix_msd_words.json"

vis = va.visualizer("radix_msd_words")


def bucket_at(word, depth):
    # 단어가 depth보다 짧으면 end bucket #0으로 보냅니다.
    if depth >= len(word):
        return 0

    # a~z는 bucket #1~#26에 대응합니다.
    return ord(word[depth]) - ord("a") + 1


def radix_sort_msd(words):
    # MSD 기수 정렬은 첫 글자부터 같은 글자 구간을 재귀적으로 정렬합니다.
    # 단어를 1열 배열로 전환하면 재귀 구간의 범위를 위아래로 확인할 수 있습니다.
    vis.line_up()

    # 첫 호출은 모든 단어를 포함하는 depth 0 구간을 스택에 넣습니다.
    vis.push(0, len(words) - 1, 0)

    # end와 a~z를 담을 27개의 bucket 개수를 모두 0으로 초기화합니다.
    counts = [0] * 27
    vis.init_counts(counts)

    # 첫 단어의 depth 0 글자를 확인해 대응하는 bucket의 개수를 1 증가시킵니다.
    word = words[0]
    bucket = bucket_at(word, 0)
    counts[bucket] += 1
    vis.scan(0, bucket, counts)

    # 이후 커밋에서 현재 구간의 모든 단어를 같은 방식으로 셉니다.
    return words


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    words = list(data.array)

    vis.setup(data)
    print("정렬 전:", words)
    print("정렬 후:", radix_sort_msd(words))
    vis.wait()
