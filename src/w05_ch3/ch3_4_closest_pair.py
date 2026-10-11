from math import sqrt

import pyvisalgo as va

from city_data import load_cities


DATA_FILE = "data/closest_pair.json"
vis = va.visualizer("closest_pair")


def distance(first, second):
    """두 도시의 좌표로 유클리드 거리를 계산한다."""
    # 가로 차이와 세로 차이를 두 변으로 하는 직각삼각형의 빗변 길이입니다.
    dx = first.x - second.x
    dy = first.y - second.y
    return sqrt(dx * dx + dy * dy)


def brute_force(cities, left, right):
    """cities[left..right]의 최근접 쌍을 (index, index, 거리)로 반환한다.

    left와 right를 모두 포함하며, 도시가 두 개 미만이면 None을 반환한다.
    """
    best = None
    # i는 첫 도시, j는 그 뒤의 도시입니다. 같은 도시끼리 비교하지 않고,
    # (i, j)를 비교한 뒤 (j, i)를 다시 비교하지 않아 각 쌍을 한 번만 봅니다.
    for i in range(left, right):
        for j in range(i + 1, right + 1):
            if vis.stopped():
                return best
            d = distance(cities[i], cities[j])
            candidate = (i, j, d)
            if best is None:
                # 첫 쌍은 비교할 기존 결과가 없으므로 초기 최단 쌍으로 둡니다.
                best = candidate
                vis.compare(i, j)
                vis.closest(i, j, d)
            else:
                vis.compare_distances(best, candidate, prefer="smaller")
                # 선택은 학생 코드에서 수행합니다. 시각화는 그 과정을 보여줍니다.
                # 같은 거리라면 기존 쌍을 그대로 유지합니다.
                if d < best[2]:
                    best = candidate
        # Enter는 현재 i와 나머지 도시의 비교를 마친 구간까지 진행합니다.
        vis.section_end()
    return best


def closest_pair(cities, left, right):
    """x순 cities[left..right]에서 최근접 쌍을 찾는다. 양 끝을 포함한다."""
    # 도시 배열은 x순으로 두고, index 배열만 처음에 한 번 y순으로 만듭니다.
    # 별도 배열이므로 도시의 위치나 좌우 그룹 소속은 바뀌지 않습니다.
    y_order = sorted(range(left, right + 1), key=lambda i: cities[i].y)
    return closest_pair_range(cities, left, right, y_order)


def closest_pair_range(cities, left, right, y_order):
    """양 끝을 포함하는 [left, right]와 그 구간의 y순 index를 받는다."""
    count = right - left + 1
    # 도시가 하나 이하이면 두 도시로 이루어진 쌍이 없습니다.
    if count < 2:
        return None

    vis.push(left, right)
    try:
        vis.show_base_case(count)
        # 재귀 종료 조건: 2개는 1쌍, 3개는 3쌍만 검사하면 됩니다.
        # 더 나누지 않고 이미 만든 완전 탐색 함수를 그대로 사용합니다.
        if count <= 3:
            return brute_force(cities, left, right)

        # mid는 왼쪽 구간의 마지막 index입니다. 양 끝을 모두 포함하므로
        # 왼쪽은 [left, mid], 오른쪽은 [mid + 1, right]로 나눕니다.
        mid = (left + right) // 2
        vis.split(mid)
        # 부모의 y순 index를 앞에서부터 나누면 두 자식도 y순을 유지합니다.
        # x값이 아니라 index로 나눠 같은 x좌표의 도시도 정확히 배정합니다.
        left_y = [i for i in y_order if i <= mid]
        right_y = [i for i in y_order if i > mid]
        left_result = closest_pair_range(cities, left, mid, left_y)
        if vis.stopped():
            return None
        vis.show_left_result(left_result)
        right_result = closest_pair_range(cities, mid + 1, right, right_y)
        if vis.stopped():
            return None

        vis.show_results(left_result, right_result)
        # 같은 거리라면 왼쪽 결과를 유지합니다.
        if left_result[2] <= right_result[2]:
            best = left_result
        else:
            best = right_result

        # 경계는 왼쪽 마지막 도시와 오른쪽 첫 도시의 x좌표 중간입니다.
        # 양쪽 내부에서 찾은 거리 d보다 가까운 경계 쌍이 있다면,
        # 두 도시 모두 이 경계에서 가로 거리 d 미만에 있어야 합니다.
        split_x = (cities[mid].x + cities[mid + 1].x) / 2
        d = best[2]
        strip = [i for i in y_order
                 if abs(cities[i].x - split_x) < d]
        # y순 배열에서 후보만 골랐으므로 strip도 이미 y순입니다.
        # 각 구간에서 다시 정렬할 필요 없이 선형 시간에 후보를 모읍니다.
        # y정렬 전에도 모든 반대편 후보 쌍을 검사했으므로 정답은 같았습니다.
        # y정렬과 아래 조기 종료는 불필요한 거리 계산을 줄이는 개선입니다.
        # 예: "경계 근처에 좌우 8개씩 모인 도시 20개"의 최상위 strip에서
        # 거리 계산은 8 * 8 = 64회에서 7회로 감소합니다(약 89% 감소).
        # 이는 해당 구간의 거리 계산 횟수이며, 전체 실행시간의 배율은 아닙니다.
        # 모든 후보를 검사하는 이전 버전은 최악 O(n^2)입니다.
        # 직전 버전은 매 재귀 구간의 strip 정렬 때문에 O(n log^2 n)이었습니다.
        # 이 버전은 최초 y정렬 O(n log n) 이후, 각 구간에서 index 분배와
        # strip 수집 및 탐색을 O(n)에 수행합니다. T(n)=2T(n/2)+O(n)이므로
        # 전체 최악 시간복잡도는 O(n log n)입니다(시각화 연출 제외).
        vis.set_strip(strip, split_x, d)
        for p in range(len(strip)):
            i = strip[p]
            vis.scan(i)
            vis.show_grid(i)
            for q in range(p + 1, len(strip)):
                if vis.stopped():
                    return None
                j = strip[q]
                # 유클리드 거리는 y좌표 차이보다 작을 수 없습니다.
                # y순이므로 이후 후보의 y좌표 차이도 이보다 작지 않습니다.
                # 같은 편인지 확인하기 전에 검사해야 어느 편의 후보든
                # 더 가까운 쌍이 될 수 없는 순간 탐색을 멈출 수 있습니다.
                if cities[j].y - cities[i].y >= best[2]:
                    vis.stop_scan(i, j, best[2])
                    break
                # 같은 편의 쌍은 재귀 호출에서 이미 검사했습니다.
                # x좌표가 같아도 양쪽으로 나뉠 수 있으므로 index로 판별합니다.
                if (i <= mid) == (j <= mid):
                    continue
                vis.scan(i, j, best[2])
                candidate = (i, j, distance(cities[i], cities[j]))
                vis.compare_distances(best, candidate, prefer="smaller")
                if candidate[2] < best[2]:
                    best = candidate
            vis.section_end()
        vis.hide_grid()
        return best
    finally:
        # 반환하거나 실행을 중단해도 부모 구간의 시각화 상태로 돌아갑니다.
        vis.pop()


if __name__ == "__main__":
    while va.running():
        data = va.next_data(__file__, data_file=DATA_FILE)
        # 공통 도시 자료에서 이번 예제의 도시만 독립 객체로 가져옵니다.
        cities = load_cities(data.city_ids)
        data.cities = cities
        vis.setup(data)
        # 시각화 화면 조작:
        # - 그래프 위에서 마우스 휠을 돌리면 포인터 위치를 중심으로 확대/축소합니다.
        # - 마우스 왼쪽 버튼을 누른 채 드래그하면 평면을 이동합니다.
        # - 그래프 우상단의 화면 맞춤 버튼을 누르면 전체 도시를 다시 보여줍니다.
        # - H 키는 제목과 설명 패널을 숨기거나 표시합니다. 숨기면 그래프 영역이
        #   넓어지며, 다시 표시해도 확대 배율과 보고 있던 중심은 유지합니다.
        # - T 키는 최상위(depth 1) strip을 표시하는 지점까지 빠르게 진행합니다.
        #   계산은 생략하지 않고 중간 대기와 연출만 건너뛰며, 도착하면
        #   일반 속도로 돌아와 strip의 후보 쌍을 비교하는 과정을 보여줍니다.
        # 입력 순서로 화면을 준비한 뒤 x좌표 순으로 정렬합니다.
        # 좌표는 그대로이며, 배열에서의 순서와 index만 바뀝니다.
        # 정렬된 index 범위로 좌우 부분을 나눌 수 있습니다. 같은 x좌표의 도시도
        # 서로 다른 부분에 속할 수 있으므로, 편을 구분할 때에는 index를 씁니다.
        cities.sort(key=lambda city: city.x)
        for index, city in enumerate(cities):
            city.index = index
        vis.show_x_sort(cities)
        print(f"x좌표 순으로 정렬한 도시 {len(cities)}개:")
        for city in cities:
            print(f"#{city.index} {city.name}: ({city.x}, {city.y})")
        result = closest_pair(cities, 0, len(cities) - 1)
        if result is not None and not vis.stopped():
            first, second, d = result
            vis.closest(first, second, d)
            print(f"최근접 쌍: {cities[first].name} - {cities[second].name}, 거리: {d:.3f}")
            vis.finish()
        vis.wait()
