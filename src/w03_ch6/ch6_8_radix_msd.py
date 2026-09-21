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

    # 현재 구간의 모든 단어를 읽어 depth 0 글자 bucket의 개수를 셉니다.
    for index, word in enumerate(words):
        bucket = bucket_at(word, 0)
        counts[bucket] += 1
        vis.scan(index, bucket, counts)
    vis.finish_counting()

    # 각 bucket의 개수를 앞 bucket까지의 누적합으로 바꿉니다.
    # counts[bucket]은 그 bucket의 단어가 result에서 끝나는 다음 위치가 됩니다.
    vis.start_accumulate()
    for bucket in range(1, len(counts)):
        previous = bucket - 1
        counts[bucket] += counts[previous]
        vis.accumulate_bucket(previous, bucket, counts)
    vis.finish_accumulate(counts)

    # bucket 순서대로 단어를 다시 놓을 임시 배열을 준비합니다.
    # 다음 커밋부터 counts의 누적합을 줄여가며 각 단어의 위치를 채웁니다.
    result = [None] * len(words)
    vis.init_result(result)

    # 뒤에서부터 읽으면 같은 bucket 안의 원래 순서가 유지됩니다.
    for index in range(len(words) - 1, -1, -1):
        word = words[index]
        bucket = bucket_at(word, 0)
        counts[bucket] -= 1
        at = counts[bucket]
        result[at] = word
        vis.place(index, bucket, at, counts, result)
    vis.finish_result(result)

    # 임시 배열의 첫 글자 기준 순서를 원래 배열에 반영합니다.
    words[:] = result
    vis.copy_back(result)

    # 배치 후 counts[bucket]은 그 bucket의 시작 인덱스가 됩니다.
    # e bucket은 e의 시작부터 f bucket 직전까지의 구간입니다.
    bucket = bucket_at("e", 0)
    left = counts[bucket]
    right = counts[bucket + 1] - 1
    if left < right:
        vis.push(left, right, 1)

        # e로 시작하는 단어의 둘째 글자를 세기 위한 새 counts 배열입니다.
        counts = [0] * 27
        vis.init_counts(counts)

        # 현재 e 구간만 순회하며 모든 단어의 둘째 글자 bucket을 셉니다.
        for index in range(left, right + 1):
            word = words[index]
            bucket = bucket_at(word, 1)
            counts[bucket] += 1
            vis.scan(index, bucket, counts)
        vis.finish_counting()

        # e 구간의 둘째 글자 bucket 개수를 누적합 인덱스로 바꿉니다.
        vis.start_accumulate()
        for bucket in range(1, len(counts)):
            previous = bucket - 1
            counts[bucket] += counts[previous]
            vis.accumulate_bucket(previous, bucket, counts)
        vis.finish_accumulate(counts)

        # result는 전체 길이로 만들고, e 구간 위치만 채웁니다.
        result = [None] * len(words)
        vis.init_result(result)

    return words


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    words = list(data.array)

    vis.setup(data)
    print("정렬 전:", words)
    print("정렬 후:", radix_sort_msd(words))
    vis.wait()
