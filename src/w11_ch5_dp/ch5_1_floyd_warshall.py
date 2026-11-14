"""모든 정점 쌍의 최단 거리를 구하는 플로이드–워셜 알고리즘."""

import pyvisalgo as va


def floyd_warshall(count, edges, directed=False, vis=None):
    pass


if __name__ == "__main__":
    vis = va.visualizer("floyd_warshall")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        floyd_warshall(len(data.vertices), data.edges, data.directed, vis)
        vis.wait()
