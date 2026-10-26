"""Closest Pair 실습: 22개의 blank(번호)를 식, 조건 또는 제어문으로 바꾼다."""

from collections import namedtuple
from math import sqrt


City = namedtuple("City", "name x y")


def blank(number):
    """미완성 빈칸의 위치를 알린다. 이 함수 자체는 수정하지 않는다."""
    raise NotImplementedError(f"빈칸 {number:02d}을 채우세요.")


def point_distance(first, second):
    """두 도시 사이의 유클리드 거리를 반환한다."""
    horizontal = first.x - second.x
    vertical = first.y - second.y
    return sqrt(horizontal * horizontal + vertical *vertical)



def exhaustive_pair(points, lo, hi):
    """양 끝을 포함하는 points[lo..hi]의 최근접 쌍을 반환한다.

    반환값은 (첫 index, 둘째 index, 거리)이며, 두 도시 미만이면 None이다.
    index는 x순으로 정렬된 points 배열의 위치이다.
    """
    nearest = None
    # first_idx는 각 쌍에서 첫째로 고른 도시의 index이다.
    # 각 쌍을 한 번만 검사한다. 둘째 index는 첫째보다 뒤에서 고른다.
    # hi는 포함되는 끝이지만 range()의 끝은 포함되지 않는다는 점에 주의한다.
    for first_idx in range(lo, hi):
        for second_idx in range(first_idx +1, hi+1):
            trial = (first_idx, second_idx,
                     point_distance(points[first_idx], points[second_idx]))
            # 첫 쌍으로 초기화하고, 이후 더 가까운 쌍을 찾을 때만 갱신한다.
            if nearest is None or nearest > trial:
                nearest = trial
    return nearest


def find_nearest(points, lo, hi):
    """x순 points[lo..hi]의 최근접 쌍을 반환한다. 양 끝을 포함한다."""
    # points에는 도시 객체가 있고, vertical_order에는 정수 index만 있다.
    # index를 y순으로 정렬해도 points 자체의 순서는 바뀌지 않는다.
    # 최초 한 번 정렬한 목록을 재귀 호출에 나눠 전달한다.
    vertical_order = sorted(range(lo, hi + 1), key=lambda idx:points[idx].y)
    return solve_region(points, lo, hi, vertical_order)


def solve_region(points, lo, hi, vertical_order):
    """양 끝 포함 [lo, hi]와 해당 구간의 y순 index 목록을 받는다.

    vertical_order에는 이 구간의 index만 있고, 대응하는 y좌표는 증가순이다.
    재귀로 내려갈 때도 이 두 조건을 유지해야 한다.
    """
    size = hi - lo + 1
    if size < 2:
        return None
    # 두 점뿐이면 가능한 쌍이 하나이므로 반복문 없이 바로 반환한다.
    if size == 2:
        return (lo, hi, point_distance(points[lo], points[hi]))
    # 세 점이면 가능한 세 쌍을 완전 탐색한다. 더 나누지는 않는다.
    if size == 3:
        return exhaustive_pair(points, lo, hi)
    # divider는 왼쪽 구간의 마지막 index이다.
    # 왼쪽 [lo, divider], 오른쪽 [divider + 1, hi]는 각각 양 끝을 포함한다.
    # 두 구간에 빠지거나 중복되는 index가 없어야 한다.
    divider = (lo + hi) //2
    # 부모 목록의 순서를 유지하며 나누면 두 자식도 y순이다.
    # 같은 x좌표의 도시도 다른 편에 속할 수 있으므로 index로 나눈다.
    lower_order = [idx for idx in vertical_order if idx <= divider]
    upper_order = [idx for idx in vertical_order if idx > divider]
    # lower/upper는 x순 index 범위의 앞/뒤를 뜻한다. y의 아래/위가 아니다.
    # 왼쪽 재귀 호출은 함수 호출 식 전체를 작성한다.
    # 재귀 호출으로 왼쪽·오른쪽 구간의 최근접 쌍을 구한다.
    lower_pair = solve_region(points, lo, divider, lower_order)
    upper_pair = solve_region(points, divider + 1, hi, upper_order)

    # 두 결과 중 유효한( None 이 아닌) 쌍을 선택한다.
    if lower_pair is None:
        nearest = upper_pair
    elif upper_pair is None:
        nearest = lower_pair
    else:
        # 거리 같으면 왼쪽 결과를 유지한다.
        nearest = lower_pair if lower_pair[2] <= upper_pair[2] else upper_pair

    # 현재 최소 거리. None이면 무한대로 설정한다.
    margin = float('inf') if nearest is None else nearest[2]

    # 경계는 왼쪽 마지막 도시와 오른쪽 첫 도시의 x좌표 중간이다.
    boundary_x = (points[divider].x + points[divider + 1].x) / 2
    # 경계 근처에 있는 후보들을 모은다.
    band = [idx for idx in vertical_order if abs(points[idx].x - boundary_x) <= margin]
    for cursor in range(len(band)):
        first_idx = band[cursor]
        for next_cursor in range(cursor + 1, len(band)):
            second_idx = band[next_cursor]
            # y 차이만으로 더 가까울 수 없으면 이후 후보도 검사하지 않는다.
            if points[second_idx].y - points[first_idx].y > margin:
                break
            # 같은 편(두 도시가 같은 구간)인 경우 이미 재귀에서 처리됨.
            if (first_idx <= divider) == (second_idx <= divider):
                continue
            trial = (first_idx, second_idx, point_distance(points[first_idx], points[second_idx]))
            if trial[2] < margin:
                nearest = trial
                margin = trial[2]
    return nearest


DATASETS = [
    ("일반 도시 10개", [
        City("A", 42, 17), City("B", 8, 99), City("C", 23, 4),
        City("D", 75, 61), City("E", 30, 12), City("F", 64, 83),
        City("G", 12, 45), City("H", 90, 20), City("I", 51, 57),
        City("J", 5, 10),
    ]),
    ("분할 경계를 가로지르는 최근접 쌍", [
        City("A", 0, 0), City("B", 9, 10),
        City("C", 10, 10), City("D", 20, 0),
    ]),
    ("같은 x좌표를 가진 도시", [
        City("A", 5, 0), City("B", 5, 20), City("C", 5, 40),
        City("D", 5, 41), City("E", 5, 60), City("F", 5, 80),
    ]),
]


if __name__ == "__main__":
    for title, original in DATASETS:
        print(f"\n[{title}]")
        # 새 배열을 정렬하므로 제공된 원본 데이터의 순서는 바뀌지 않는다.
        points = sorted(original, key=lambda item: item.x)
        for index, city in enumerate(points):
            print(f"#{index} {city.name}: ({city.x}, {city.y})")

        result = find_nearest(points, 0, len(points) - 1)
        if result is None:
            print("두 도시가 없어 최근접 쌍을 만들 수 없습니다.")
        else:
            i, j, d = result
            print(f"최근접 쌍: #{i} {points[i].name} - #{j} {points[j].name}")
            print(f"최소거리: {d:.3f}")

            # 완전 탐색의 거리와 비교한다. 동률이면 선택된 쌍은 달라도 된다.
            reference = exhaustive_pair(points, 0, len(points) - 1)
            if reference is None:
                assert result is None and reference is None
            else:
                assert abs(result[2] - reference[2]) < 1e-6, "최소거리가 다릅니다."
                print("완전 탐색과 최소거리 일치")
