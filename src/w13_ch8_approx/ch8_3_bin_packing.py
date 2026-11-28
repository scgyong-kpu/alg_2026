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


def first_fit(size, bins, vis=None):
    """물건이 들어가는 첫 번째 통의 인덱스를 반환한다. 없으면 None을 반환한다."""
    for index, current_bin in enumerate(bins):
        if vis:
            vis.inspect_bin(index, current_bin.free)
            if vis.stopped():
                break
        if current_bin.free >= size:
            return index
    return None


def pack(items, capacity, vis=None):
    bins = []
    if vis:
        vis.start(bins)
    for index, size in enumerate(items):
        if vis:
            vis.start_item(index)
            if vis.stopped():
                break
        target = first_fit(size, bins, vis)  # 기존 통의 인덱스 또는 None
        if vis and vis.stopped():
            break
        if target is None:
            bin_index = len(bins)
            bins.append(Bin(capacity))
        else:
            bin_index = target
        bins[bin_index].add(size)
        if vis:
            vis.place_item(bin_index, target is None)
            if vis.stopped():
                break
    return bins


if __name__ == "__main__":
    vis = va.visualizer("bin_packing")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data, "First Fit")
        bins = pack(data.array, data.capacity, vis)
        if not vis.stopped():
            print(f"통 {len(bins)}개")
            vis.finish({"First Fit": len(bins)})
        vis.wait()
