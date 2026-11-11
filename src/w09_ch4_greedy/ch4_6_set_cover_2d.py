"""각 지점에 학교를 세우면 자기 자신과 바로 연결된 지점을 덮는다."""

import pyvisalgo as va

from ch4_6_set_cover import set_cover


def make_subsets(universe, edges):
    neighbors = {city: {city} for city in universe}
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    return [neighbors[city] for city in universe]


if __name__ == "__main__":
    vis = va.visualizer("set_cover_2d")
    while va.running():
        data = va.next_data(__file__)
        data.subsets = make_subsets(data.universe, data.edges)
        vis.setup(data)
        chosen, uncovered = set_cover(data.universe, data.subsets, vis)
        if not vis.stopped():
            print("학교를 세울 지점:", [data.universe[i] for i in chosen])
            vis.finish(uncovered)
        vis.wait()
