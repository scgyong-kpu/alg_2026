"""같은 그래프에서 정점으로 정점 또는 간선을 덮는다."""

import pyvisalgo as va


# 탐욕 집합 커버의 근사비율은 H(d) 이하이며, H(d) <= 1 + ln(d)이다.
# d는 가장 큰 후보 집합의 크기이고, H(d) = 1 + 1/2 + ... + 1/d이다.
# 전체 원소가 n개라면 d <= n이므로 1 + ln(n)으로도 상한을 쓸 수 있다.
# 정점 → 정점에서는 후보가 자기 자신과 이웃을 덮으므로 d = 최대 차수 + 1이다.
# 정점 → 간선에서 d는 한 정점에 닿는 간선 수의 최댓값이며, m은 전체 간선 수이다.
# d <= m이므로 1 + ln(m)도 이 모드의 상한이다.
# 20정점 예제에서는 m = 33, d = 6이므로 H(d) = 2.45이다.
# 탐욕법은 14개, 최적해는 6개를 골라 실제 근사비율은 14/6 ≈ 2.33이다.
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


def make_subsets(universe, edges):
    neighbors = {city: {city} for city in universe}
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    return [neighbors[city] for city in universe]


def make_edge_subsets(vertices, edges):
    incident = {vertex: set() for vertex in vertices}
    for u, v in edges:
        edge = (u, v)
        incident[u].add(edge)
        incident[v].add(edge)
    return [incident[vertex] for vertex in vertices]


# 극대 매칭의 양 끝점으로 만든 정점 커버는 최적해 크기의 최대 2배이다.
# 매칭 간선이 k개이면 서로 끝점이 겹치지 않아 최적해도 최소 k개를 골라야 한다.
# 이 방법은 매칭의 양 끝점을 모두 골라 2k개를 사용한다.
# 간선 선택 순서에 따라 k는 달라질 수 있지만 2배 보장은 유지된다.
def maximal_matching(edges, vis=None):
    """입력 순서대로 끝점이 겹치지 않는 간선을 고른다."""
    matching = []
    matched_vertices = set()
    for u, v in edges:
        if vis and vis.stopped():
            break
        if u in matched_vertices or v in matched_vertices:
            continue
        edge = (u, v)
        matching.append(edge)
        matched_vertices.update(edge)
        if vis:
            vis.match_edge(edge)
    return matching


if __name__ == "__main__":
    vis = va.visualizer("cover_comparison")
    while va.running():
        data = va.next_data(__file__)
        data.vertices = data.universe
        if vis.cover_edges:
            data.universe = [tuple(edge) for edge in data.edges]
            data.subsets = make_edge_subsets(data.vertices, data.edges)
            # 기존 최적해는 정점을 덮는 경우에 해당한다.
            data.optimal_cover = None
        else:
            data.subsets = make_subsets(data.vertices, data.edges)
        vis.setup(data)
        if vis.mode == "matching":
            matching = maximal_matching(data.universe, vis)
            if not vis.stopped():
                print("매칭 간선:", matching)
                print("CCTV를 설치할 교차로:", [vertex for edge in matching for vertex in edge])
                vis.finish_matching()
        else:
            chosen, uncovered = set_cover(data.universe, data.subsets, vis)
            if not vis.stopped():
                install_label = "CCTV를 설치할 교차로" if vis.cover_edges else "학교를 세울 지점"
                print(f"{install_label}:", [data.vertices[i] for i in chosen])
                vis.finish(uncovered)
        action = vis.wait()
        if action == "toggle_cover":
            vis.mode = "vertices" if vis.cover_edges else "edges"
        elif action == "toggle_matching":
            vis.mode = "edges" if vis.mode == "matching" else "matching"
