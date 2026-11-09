"""아직 덮지 못한 원소를 가장 많이 포함하는 집합부터 고른다."""

import pyvisalgo as va


def set_cover(universe, subsets, vis=None):
    # uncovered: 아직 어느 후보도 덮지 않은 원소들의 집합입니다. 처음에는 전체 원소를 담습니다.
    uncovered = set(universe)
    # candidates: 입력 순서대로 보관한 후보 집합 목록입니다. 원본 subsets는 바꾸지 않습니다.
    candidates = [set(subset) for subset in subsets]
    # gains[index]: 후보 하나가 이번에 새로 덮을 원소들의 집합입니다.
    # 개수만 저장하지 않으므로 len()으로 셀 수도 있고, 어떤 원소를 셌는지도 표시할 수 있습니다.
    gains = {}
    # 이번 단계에서는 첫 바퀴의 개수만 구합니다.
    # index는 0부터 시작하는 후보의 위치입니다. 화면에서 candidates[0]은 S1로 표시합니다.
    for index, subset in enumerate(candidates):
        # subset은 현재 후보 집합, new_elements는 그중 아직 덮지 않은 원소만 모으는 집합입니다.
        new_elements = set()
        for element in subset:
            if element in uncovered:
                new_elements.add(element)
        gains[index] = new_elements
    if vis and not vis.stopped():
        vis.compare(gains)


if __name__ == "__main__":
    vis = va.visualizer("set_cover")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        set_cover(data.universe, data.subsets, vis)
        vis.wait()
