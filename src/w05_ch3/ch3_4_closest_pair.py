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
        # 먼저 입력의 첫 두 도시만 비교합니다. 전체 쌍 탐색은 다음 단계입니다.
        d = distance(cities[0], cities[1])
        print(f"{cities[0].name} - {cities[1].name} 거리: {d:.3f}")
        vis.show_distance(0, 1, d)
        vis.wait()
