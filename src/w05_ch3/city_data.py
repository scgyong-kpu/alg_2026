"""최근접 쌍 실습에서 사용할 도시 1,000개의 공통 자료를 읽는다."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class City:
    name: str
    x: int
    y: int
    index: int


def load_cities(city_ids):
    """공통 자료의 ID를 골라, 실행마다 독립적인 도시 객체를 만든다."""
    path = Path(__file__).parent / "data" / "cities.json"
    with path.open(encoding="utf-8") as source:
        records = json.load(source)
    # index는 현재 입력에서의 위치이며, 이후 x순 정렬 단계에서 다시 설정한다.
    return [City(records[i]["name"], records[i]["x"], records[i]["y"], index)
            for index, i in enumerate(city_ids)]


if __name__ == "__main__":
    # ID를 바꿔 공통 자료에서 원하는 도시를 골라 확인할 수 있습니다.
    city_ids = list(range(10))
    cities = load_cities(city_ids)
    print(f"불러온 도시: {len(cities)}개")
    for city in cities:
        print(f"#{city.index} {city.name}: ({city.x}, {city.y})")
