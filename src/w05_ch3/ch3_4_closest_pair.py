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


if __name__ == "__main__":
    while va.running():
        data = va.next_data(__file__, data_file=DATA_FILE)
        # 공통 도시 자료에서 이번 예제의 도시만 독립 객체로 가져옵니다.
        # 지금은 입력 순서 그대로 표시하며, x순 정렬은 이후 단계에서 구현합니다.
        cities = load_cities(data.city_ids)
        data.cities = cities
        print(f"도시 {len(cities)}개:")
        for city in cities:
            print(f"#{city.index} {city.name}: ({city.x}, {city.y})")
        vis.setup(data)
        # 시각화 화면 조작:
        # - 그래프 위에서 마우스 휠을 돌리면 포인터 위치를 중심으로 확대/축소합니다.
        # - 마우스 왼쪽 버튼을 누른 채 드래그하면 평면을 이동합니다.
        # - 그래프 우상단의 화면 맞춤 버튼을 누르면 전체 도시를 다시 보여줍니다.
        # - H 키는 제목과 설명 패널을 숨기거나 표시합니다. 숨기면 그래프 영역이
        #   넓어지며, 다시 표시해도 확대 배율과 보고 있던 중심은 유지합니다.
        # 모든 쌍을 검사하여 전체 입력의 최근접 쌍을 찾습니다.
        result = brute_force(cities, 0, len(cities) - 1)
        if result is not None and not vis.stopped():
            first, second, d = result
            print(f"최근접 쌍: {cities[first].name} - {cities[second].name}, 거리: {d:.3f}")
            vis.finish()
        vis.wait()
