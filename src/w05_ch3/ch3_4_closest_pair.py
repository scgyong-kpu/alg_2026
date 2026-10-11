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
        left_result = closest_pair(cities, left, mid)
        if vis.stopped():
            return None
        vis.show_left_result(left_result)
        right_result = closest_pair(cities, mid + 1, right)
        if vis.stopped():
            return None

        vis.show_results(left_result, right_result)
        # 같은 거리라면 왼쪽 결과를 유지합니다.
        # 아직 경계를 가로지르는 쌍을 검사하지 않았으므로 잠정 결과입니다.
        if left_result[2] <= right_result[2]:
            return left_result
        return right_result
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
            if len(cities) <= 3:
                print(f"최근접 쌍: {cities[first].name} - {cities[second].name}, 거리: {d:.3f}")
                vis.finish()
            else:
                print(f"부분 구간의 잠정 최근접 쌍: {cities[first].name} - {cities[second].name}, 거리: {d:.3f}")
                vis.msg_action("좌우 부분 구간의 결과 중 더 가까운 쌍을 선택했다.")
                vis.msg_detail("경계를 가로지르는 쌍은 아직 검사하지 않았다. 전체 최근접 쌍은 다음 단계에서 찾는다.")
                vis.draw()
        vis.wait()
