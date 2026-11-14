"""모든 정점 쌍의 최단 거리를 구한다. 음수 간선은 허용하며, 음수 사이클은 없다고 가정한다."""

from math import inf

import pyvisalgo as va


def floyd_warshall(count, edges, directed=False, vis=None):
    """거리 행렬과 다음 정점 행렬을 반환한다. 시각화가 중단되면 None을 반환한다."""
    # 처음에는 자기 자신으로 가는 거리만 알고 있습니다.
    dist = [[inf] * count for _ in range(count)]
    # next_hop[i][j]는 i에서 j로 갈 때 i 바로 다음에 방문하는 정점입니다.
    # 아직 알려진 경로가 없으면 None입니다.
    next_hop = [[None] * count for _ in range(count)]
    for i in range(count):
        dist[i][i] = 0
        # 자기 자신이 목적지라면 이동할 필요가 없으므로 i를 기록합니다.
        next_hop[i][i] = i

    # 직접 갈 수 있는 간선의 비용과 첫 방문 정점을 기록합니다.
    for u, v, weight in edges:
        # 방향 그래프의 간선은 u에서 v로만 갈 수 있는 단방향 간선입니다.
        if weight < dist[u][v]:
            dist[u][v] = weight
            next_hop[u][v] = v
        # 무방향 그래프일 때만 반대 방향(v에서 u)도 기록합니다.
        if not directed and weight < dist[v][u]:
            dist[v][u] = weight
            next_hop[v][u] = u

    if vis:
        vis.initialize(dist, next_hop)

    # k번째 바퀴를 마치면 0부터 k까지의 정점을 경유하는 경로를 고려한 상태입니다.
    # k를 바깥 루프에 두면 이전 단계의 모든 최단 거리를 구한 뒤 이번 단계에서 사용할 수 있습니다.
    for k in range(count):
        if vis:
            if vis.stopped():
                return None
            vis.begin_phase(k)

        # 모든 출발점 i와 도착점 j에 대해 k를 거치는 경로의 비용을 구합니다.
        for i in range(count):
            for j in range(count):
                if vis and vis.stopped():
                    return None
                via = dist[i][k] + dist[k][j]
                if vis:
                    vis.compare(i, j, k, via)
                    if vis.stopped():
                        return None
                if via < dist[i][j]:
                    dist[i][j] = via
                    # k가 바로 다음 정점이라는 보장은 없으므로 i에서 k로 가는 첫 정점을 씁니다.
                    next_hop[i][j] = next_hop[i][k]
                    if vis:
                        vis.update_distance()

        if vis:
            if vis.stopped():
                return None
            vis.end_phase()
    if vis and vis.stopped():
        return None
    return dist, next_hop


def floyd_warshall_without_vis(count, edges, directed=False):
    """각 칸에 (최단 거리, 경로의 다음 정점)이 들어 있는 행렬을 반환한다."""
    dist = [[(inf, None)] * count for _ in range(count)]
    for i in range(count):
        dist[i][i] = (0, i)

    for u, v, weight in edges:
        if weight < dist[u][v][0]:
            dist[u][v] = (weight, v)
        if not directed and weight < dist[v][u][0]:
            dist[v][u] = (weight, u)

    for k in range(count):
        for i in range(count):
            to_k, first_hop = dist[i][k]
            for j in range(count):
                via = to_k + dist[k][j][0]
                if via < dist[i][j][0]:
                    dist[i][j] = (via, first_hop)
    return dist


if __name__ == "__main__":
    vis = va.visualizer("floyd_warshall")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        result = floyd_warshall(len(data.vertices), data.edges, data.directed, vis)
        if result is not None:
            dist, _ = result
            for name, row in zip(data.vertices, dist):
                print(name, row)
            vis.finish()
        # 실행 중 Enter: 현재 k가 끝날 때까지 진행. 일시정지 또는 완료 상태에서 k 클릭: 단계 조회.
        # 행렬의 칸에 마우스를 올리면 표시 중인 단계의 경로를 확인할 수 있습니다.
        vis.wait()
