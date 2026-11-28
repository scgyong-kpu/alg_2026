"""주어진 순서대로 물건을 통에 담는 빈 패킹 실습."""

import pyvisalgo as va


def pack(items, capacity):
    pass


if __name__ == "__main__":
    vis = va.visualizer("bin_packing")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data, "Bin Packing")
        pack(data.array, data.capacity)
        vis.wait()
