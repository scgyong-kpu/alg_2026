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


def fitting_bins(size, bins, vis=None):
    candidates = []
    for index, current_bin in enumerate(bins):
        if vis:
            vis.inspect_bin(index, current_bin.free)
            if vis.stopped():
                break
        if current_bin.free >= size:
            candidates.append(index)
    return candidates


def best_fit(size, bins, vis=None):
    """물건이 들어가는 통 중 남은 공간이 가장 작은 통의 인덱스를 반환한다."""
    candidates = fitting_bins(size, bins, vis)
    if not candidates:
        return None

    # 첫 후보를 기준으로 나머지 후보의 남은 공간을 비교한다.
    best_index = candidates[0]
    for index in candidates[1:]:
        if bins[index].free < bins[best_index].free:
            best_index = index
    return best_index


def worst_fit(size, bins, vis=None):
    """물건이 들어가는 통 중 남은 공간이 가장 큰 통의 인덱스를 반환한다."""
    worst_index = None
    for index, current_bin in enumerate(bins):
        if vis:
            vis.inspect_bin(index, current_bin.free)
            if vis.stopped():
                return None
        if worst_index is None or current_bin.free > bins[worst_index].free:
            worst_index = index

    # 가장 여유 있는 통에도 들어가지 않으면 어느 통에도 들어가지 않는다.
    if worst_index is None or bins[worst_index].free < size:
        return None
    return worst_index


STRATEGY_FIRST_FIT, STRATEGY_NEXT_FIT, STRATEGY_BEST_FIT, STRATEGY_WORST_FIT = range(4)
STRATEGIES = [
    ("First Fit", first_fit),
    ("Next Fit", next_fit),
    ("Best Fit", best_fit),
    ("Worst Fit", worst_fit),
]
STRATEGY_COMPARE = len(STRATEGIES)


def place_in_bin(size, bins, capacity, select_bin, vis=None):
    target = select_bin(size, bins, vis)  # 기존 통의 인덱스 또는 None
    if vis and vis.stopped():
        return None
    if target is None:
        bin_index = len(bins)
        bins.append(Bin(capacity))
    else:
        bin_index = target
    bins[bin_index].add(size)
    return bin_index, target is None


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
        placement = place_in_bin(size, bins, capacity, select_bin, vis)
        if placement is None:
            break
        bin_index, is_new_bin = placement
        if vis:
            vis.place_item(bin_index, is_new_bin)
            if vis.stopped():
                break
    return bins


def compare_strategies(items, capacity, vis):
    bins_by_strategy = {name: [] for name, _ in STRATEGIES}
    vis.start_comparison(bins_by_strategy)
    for index, size in enumerate(items):
        vis.start_item(index)
        if vis.stopped():
            break

        # 같은 물건을 네 전략에 한 번씩 넣은 뒤 다음 물건으로 넘어간다.
        placements = {}
        for name, select_bin in STRATEGIES:
            placements[name] = place_in_bin(size, bins_by_strategy[name], capacity, select_bin)
        vis.place_comparison(placements)
        if vis.stopped():
            break
    return {name: len(bins) for name, bins in bins_by_strategy.items()}


if __name__ == "__main__":
    vis = va.visualizer("bin_packing")
    strategy_index = STRATEGY_FIRST_FIT
    while va.running():
        data = va.next_data(__file__)
        if strategy_index == STRATEGY_COMPARE:
            vis.setup(data, "동시 비교")
            counts = compare_strategies(data.array, data.capacity, vis)
        else:
            strategy, _ = STRATEGIES[strategy_index]
            vis.setup(data, strategy)
            bins = pack(data.array, data.capacity, strategy_index, vis)
            counts = {strategy: len(bins)}
        if not vis.stopped():
            for name, count in counts.items():
                print(f"{name}: 통 {count}개")
            vis.finish(counts)
        if vis.wait() == "next_strategy":
            strategy_index = (strategy_index + 1) % (len(STRATEGIES) + 1)
