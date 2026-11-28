"""주어진 순서대로 물건을 통에 담는 빈 패킹 실습."""

from dataclasses import dataclass, field

import pyvisalgo as va

@dataclass
class Bin:
    free: int
    items: list[int] = field(default_factory=list)

    def add(self, size):
        self.items.append(size)
        self.free -= size


def pack(items, capacity, vis=None):
    bins = []
    if vis:
        vis.start(bins)
    for index, size in enumerate(items):
        if vis:
            vis.start_item(index)
            if vis.stopped():
                break
        new_bin = Bin(capacity)
        new_bin.add(size)
        bins.append(new_bin)
        if vis:
            vis.place_item(index, opened=True)
            if vis.stopped():
                break
    return bins


if __name__ == "__main__":
    vis = va.visualizer("bin_packing")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data, "Bin Packing")
        bins = pack(data.array, data.capacity, vis)
        if not vis.stopped():
            print(f"통 {len(bins)}개")
            vis.finish({"물건마다 새 통": len(bins)})
        vis.wait()
