"""모든 정점 쌍의 최단 거리를 구하는 플로이드–워셜 알고리즘."""

from math import inf

import pyvisalgo as va


def floyd_warshall(count, edges, directed=False, vis=None):
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
    return dist, next_hop


if __name__ == "__main__":
    vis = va.visualizer("floyd_warshall")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        floyd_warshall(len(data.vertices), data.edges, data.directed, vis)
        vis.wait()
