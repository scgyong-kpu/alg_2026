"""아직 덮지 못한 원소를 가장 많이 포함하는 집합부터 고른다."""

import pyvisalgo as va


def set_cover(universe, subsets, vis=None):
    pass


if __name__ == "__main__":
    vis = va.visualizer("set_cover")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        set_cover(data.universe, data.subsets, vis)
        vis.wait()
