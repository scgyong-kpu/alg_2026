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


def next_fit(size, bins, vis=None):
    """마지막 통에 물건이 들어가면 그 인덱스를 반환한다. 아니면 None이다."""
    if not bins:
        return None
    index = len(bins) - 1
    free = bins[index].free
    if vis:
        vis.inspect_bin(index, free)
    if free >= size:
        return index
    return None


STRATEGY_FIRST_FIT, STRATEGY_NEXT_FIT = range(2)
STRATEGIES = [
    ("First Fit", first_fit),
    ("Next Fit", next_fit),
]


def pack(items, capacity, strategy_index, vis=None):
    _, select_bin = STRATEGIES[strategy_index]
    bins = []
    if vis:
        vis.start(bins)
    for index, size in enumerate(items):
        if vis:
            vis.start_item(index)
            if vis.stopped():
                break
        target = select_bin(size, bins, vis)  # 기존 통의 인덱스 또는 None
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
    strategy_index = STRATEGY_FIRST_FIT
    while va.running():
        data = va.next_data(__file__)
        strategy, _ = STRATEGIES[strategy_index]
        vis.setup(data, strategy)
        bins = pack(data.array, data.capacity, strategy_index, vis)
        if not vis.stopped():
            print(f"{strategy}: 통 {len(bins)}개")
            vis.finish({strategy: len(bins)})
        if vis.wait() == "next_strategy":
            strategy_index = (strategy_index + 1) % len(STRATEGIES)
