import pyvisalgo as va


DATA_FILE = "data/radix_msd_words.json"

vis = va.visualizer("radix_msd_words")


def bucket_at(word, depth):
    # 단어가 depth보다 짧으면 end bucket #0으로 보냅니다.
    if depth >= len(word):
        return 0

    # a~z는 bucket #1~#26에 대응합니다.
    return ord(word[depth]) - ord("a") + 1


def radix_sort_msd_range(words, left, right, depth, result):
    # result는 최상위 호출에서 한 번만 만들고 모든 재귀 구간이 공유합니다.
    # 현재 구간을 복사한 뒤 다시 비우므로, 자식 구간이 같은 배열을 안전하게 씁니다.

    # 현재 같은-prefix 구간을 depth 위치의 글자로 한 번 분류합니다.
    vis.push(left, right, depth)

    # end와 a~z를 담을 27개의 bucket 개수를 모두 0으로 초기화합니다.
    counts = [0] * 27
    vis.init_counts(counts)

    # 현재 구간의 단어만 읽어 depth 위치 글자 bucket의 개수를 셉니다.
    for index in range(left, right + 1):
        word = words[index]
        bucket = bucket_at(word, depth)
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
    bucket_ends = list(counts)

    # 이전 재귀 호출에서 남을 수 있는 현재 구간의 값을 비웁니다.
    for index in range(left, right + 1):
        result[index] = None
    vis.init_result(result)

    # 뒤에서부터 읽으면 같은 bucket 안의 원래 순서가 유지됩니다.
    for index in range(right, left - 1, -1):
        word = words[index]
        bucket = bucket_at(word, depth)
        counts[bucket] -= 1
        at = left + counts[bucket]
        result[at] = word
        vis.place(index, bucket, at, counts, result)
    vis.finish_result(result)

    # 임시 배열의 현재 구간만 원래 배열에 반영합니다.
    words[left:right + 1] = result[left:right + 1]
    vis.copy_back(result)

    # copy_back()은 시각화할 값의 사본을 보관했으므로, 작업 배열은 바로 재사용합니다.
    for index in range(left, right + 1):
        result[index] = None

    # end bucket은 단어가 끝난 경우이므로 더 내려가지 않습니다.
    # 같은 글자가 둘 이상인 bucket만 다음 depth에서 다시 정렬합니다.
    for bucket in range(1, len(bucket_ends)):
        child_left = left + bucket_ends[bucket - 1]
        child_right = left + bucket_ends[bucket] - 1
        if child_left < child_right:
            radix_sort_msd_range(words, child_left, child_right, depth + 1, result)
    vis.pop()


def radix_sort_msd(words):
    # MSD 기수 정렬은 첫 글자부터 같은 글자 구간을 재귀적으로 정렬합니다.
    # 단어를 1열 배열로 전환하면 재귀 구간의 범위를 위아래로 확인할 수 있습니다.
    vis.line_up()

    # 모든 재귀 구간이 공유할 임시 배열을 한 번만 준비합니다.
    result = [None] * len(words)

    # 첫 호출은 모든 단어를 포함하는 depth 0 구간을 처리합니다.
    radix_sort_msd_range(words, 0, len(words) - 1, 0, result)
    vis.finish()

    return words


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    words = list(data.array)

    vis.setup(data)
    print("정렬 전:", words)
    print("정렬 후:", radix_sort_msd(words))
    vis.wait()
