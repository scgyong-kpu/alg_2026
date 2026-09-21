import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "radix_msd_e_to_o_words.json"
FIRST_CHAR = "e"
LAST_CHAR = "o"
BUCKET_COUNT = ord(LAST_CHAR) - ord(FIRST_CHAR) + 2


def bucket_at(word, depth):
    # 단어가 depth보다 짧으면 end bucket #0으로 보냅니다.
    if depth >= len(word):
        return 0

    # FIRST_CHAR~LAST_CHAR는 bucket #1부터 차례로 대응합니다.
    return ord(word[depth]) - ord(FIRST_CHAR) + 1


def radix_sort_msd_range(words, left, right, depth, result):
    # result는 최상위 호출에서 한 번만 만들고 모든 재귀 구간이 공유합니다.
    # 현재 구간을 복사한 뒤 다시 비우므로, 자식 구간이 같은 배열을 안전하게 씁니다.

    # end와 FIRST_CHAR~LAST_CHAR를 담을 bucket 개수를 모두 0으로 초기화합니다.
    counts = [0] * BUCKET_COUNT

    # 현재 구간의 단어만 읽어 depth 위치 글자 bucket의 개수를 셉니다.
    for index in range(left, right + 1):
        word = words[index]
        bucket = bucket_at(word, depth)
        counts[bucket] += 1

    # 각 bucket의 개수를 앞 bucket까지의 누적합으로 바꿉니다.
    # counts[bucket]은 그 bucket의 단어가 result에서 끝나는 다음 위치가 됩니다.
    for bucket in range(1, len(counts)):
        previous = bucket - 1
        counts[bucket] += counts[previous]
    bucket_ends = list(counts)

    # 이전 재귀 호출에서 남을 수 있는 현재 구간의 값을 비웁니다.
    for index in range(left, right + 1):
        result[index] = None

    # 뒤에서부터 읽으면 같은 bucket 안의 원래 순서가 유지됩니다.
    for index in range(right, left - 1, -1):
        word = words[index]
        bucket = bucket_at(word, depth)
        counts[bucket] -= 1
        at = left + counts[bucket]
        result[at] = word

    # 임시 배열의 현재 구간만 원래 배열에 반영합니다.
    words[left:right + 1] = result[left:right + 1]

    # 현재 구간의 복사가 끝났으므로, 작업 배열은 바로 재사용합니다.
    for index in range(left, right + 1):
        result[index] = None

    # end bucket은 단어가 끝난 경우이므로 더 내려가지 않습니다.
    # 같은 글자가 둘 이상인 bucket만 다음 depth에서 다시 정렬합니다.
    for bucket in range(1, len(bucket_ends)):
        child_left = left + bucket_ends[bucket - 1]
        child_right = left + bucket_ends[bucket] - 1
        if child_left < child_right:
            radix_sort_msd_range(words, child_left, child_right, depth + 1, result)


def radix_sort_msd(words):
    # 모든 재귀 구간이 공유할 임시 배열을 한 번만 준비합니다.
    result = [None] * len(words)

    # 첫 호출은 모든 단어를 포함하는 depth 0 구간을 처리합니다.
    radix_sort_msd_range(words, 0, len(words) - 1, 0, result)

    return words


def load_words():
    dataset = json.loads(DATA_FILE.read_text(encoding="utf-8"))["datasets"][0]
    return dataset["name"], list(dataset["data"]["array"])


def validate_words(words):
    # bucket_at()은 FIRST_CHAR~LAST_CHAR 범위의 문자만 인덱스로 바꿀 수 있습니다.
    for word in words:
        for char in word:
            if not FIRST_CHAR <= char <= LAST_CHAR:
                raise ValueError(
                    f"{word!r}에 범위 밖 문자 {char!r}가 있습니다: "
                    f"{FIRST_CHAR!r}~{LAST_CHAR!r}만 사용할 수 있습니다."
                )


def print_words(label, words):
    if len(words) <= 20:
        print(f"{label}: {', '.join(words)}")
        return

    print(f"{label}: {', '.join(words[:10])}, ...")
    print(f"{' ' * len(label)}  ... {', '.join(words[-4:])}")


if __name__ == "__main__":
    name, words = load_words()
    validate_words(words)
    expected = sorted(words)

    print(f"데이터: {name}")
    print(f"문자 범위: {FIRST_CHAR} ~ {LAST_CHAR}")
    print(f"단어 수: {len(words)}")
    print()
    print_words("정렬 전", words)

    radix_sort_msd(words)

    print()
    print_words("정렬 후", words)

    if words != expected:
        raise AssertionError("MSD 정렬 결과가 sorted(words)와 다릅니다.")
    print()
    print("검증: 입력 범위와 사전순 정렬 결과가 올바릅니다.")
