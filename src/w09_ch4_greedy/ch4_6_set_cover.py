"""아직 덮지 못한 원소를 가장 많이 포함하는 집합부터 고른다."""

import pyvisalgo as va


def set_cover(universe, subsets, vis=None):
    # uncovered: 아직 어느 후보도 덮지 않은 원소들의 집합입니다. 처음에는 전체 원소를 담습니다.
    uncovered = set(universe)
    # candidates: 입력 순서대로 보관한 후보 집합 목록입니다. 원본 subsets는 바꾸지 않습니다.
    candidates = [set(subset) for subset in subsets]
    # chosen에는 선택한 후보의 원래 인덱스를 순서대로 기록합니다.
    chosen = []
    # 후보를 제거해도 나머지 후보의 원래 번호는 바뀌지 않도록 인덱스만 관리합니다.
    available = list(range(len(candidates)))
    # 아직 덮지 못한 원소가 있는 동안 후보를 다시 평가합니다.
    while uncovered:
        if vis and vis.stopped():
            break
        # gains[index]: 후보 하나가 이번에 새로 덮을 원소들의 집합입니다.
        # 개수만 저장하지 않으므로 len()으로 셀 수도 있고, 어떤 원소를 셌는지도 표시할 수 있습니다.
        gains = {}
        # index는 0부터 시작하는 후보의 위치입니다. 화면에서 candidates[0]은 S1로 표시합니다.
        for index in available:
            subset = candidates[index]
            # 양쪽 집합에 모두 속한 원소만 남기면, 이 후보가 새로 덮는 원소를 얻습니다.
            gains[index] = subset & uncovered
        # max는 교집합 크기를 비교하되 크기가 아니라 후보 인덱스를 반환합니다.
        # 동률이면 먼저 나온 후보, 후보가 없으면 default인 None을 반환합니다.
        best = max(gains, key=lambda index: len(gains[index]), default=None)
        if vis and not vis.stopped():
            vis.compare(gains, best)
        # 후보가 없거나 최선의 후보도 새로 덮는 원소가 없으면 종료합니다.
        if best is None or not gains[best] or (vis and vis.stopped()):
            break

        chosen.append(best)
        available.remove(best)
        # 선택한 후보가 이번에 덮은 원소만 미포함 집합에서 제거합니다.
        uncovered -= gains[best]
        if vis:
            vis.select(best, uncovered)
    return chosen, uncovered


if __name__ == "__main__":
    vis = va.visualizer("set_cover")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        chosen, uncovered = set_cover(data.universe, data.subsets, vis)
        if not vis.stopped():
            print("선택:", [f"S{i + 1}" for i in chosen])
            print("아직 덮지 못한 원소:", sorted(uncovered))
            vis.finish(uncovered)
        vis.wait()
