import sys
from random import Random


def random_values(count, seed="Hello", low=1, high=None):
    # seed를 고정하면 매번 같은 입력이 만들어집니다.
    # 성능 측정에서는 같은 입력을 여러 알고리즘에 넣어야 비교가 공정합니다.
    rng = Random(seed)
    high = high or count * 10
    return [rng.randint(low, high) for _ in range(count)]


def reversed_values(count):
    # 단순 교환 기반 정렬에서 가장 많은 이동이 필요한 입력입니다.
    return list(range(count, 0, -1))


def sorted_values(count):
    # 이미 정렬된 입력은 개선 버블 정렬과 삽입 정렬의 best case를 보여줍니다.
    return list(range(1, count + 1))


def nearly_sorted_values(count, seed="Hello", window=100):
    # 먼저 정렬된 데이터를 만든 뒤, 가까운 위치끼리 조금씩 섞습니다.
    # 값들이 대체로 제자리 근처에 남아 있어 nearly sorted 성격을 가집니다.
    values = sorted_values(count)
    if count <= 1:
        return values

    rng = Random(seed)
    window = max(1, min(window, count))

    for index in range(count):
        other = index + rng.randrange(window)
        if other >= count:
            other -= window
        values[index], values[other] = values[other], values[index]

    return values


def copy_case(values):
    # 성능 측정에서 같은 입력을 여러 정렬 함수에 넣을 때 원본 훼손을 막습니다.
    return list(values)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(random_values(count))
