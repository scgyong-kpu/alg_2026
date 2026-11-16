"""물건을 쪼개지 않고, 각 물건을 최대 한 번 담아 가치를 최대화한다."""

from math import gcd

import pyvisalgo as va


def knapsack(weights, values, capacity, vis=None):
    count = len(weights)
    # best[i][w]: 물건 1번부터 i번까지 고려할 때, 용량 w에서 얻는 최대 가치.
    # 물건이 없거나(i=0) 용량이 0이면(w=0) 최대 가치는 0이다.
    best = [[0] * (capacity + 1) for _ in range(count + 1)]
    # take[i][w]: best[i][w]를 얻는 조합에 물건 i를 넣었는지 기록한다.
    take = [[False] * (capacity + 1) for _ in range(count + 1)]
    if vis:
        vis.initialize(best)
        if vis.stopped():
            return None

    # 이전 행을 모두 채운 뒤 다음 물건을 고려한다.
    for i in range(1, count + 1):
        weight, value = weights[i - 1], values[i - 1]
        for w in range(1, capacity + 1):
            skip_value = best[i - 1][w]
            take_value = None
            if weight <= w:
                # 이전 행을 조회해야 물건 i를 두 번 담지 않는다.
                take_value = best[i - 1][w - weight] + value
            if vis:
                vis.compare(i, w, skip_value, take_value)
                if vis.stopped():
                    return None

            # 동점이거나 담을 수 없으면 기존 값을 유지한다.
            took = take_value is not None and take_value > skip_value
            best[i][w] = take_value if took else skip_value
            take[i][w] = took
            if vis:
                vis.place(took)
                if vis.stopped():
                    return None

    selected = []
    w = capacity
    for i in range(count, 0, -1):
        # 물건을 담았으면 그 무게를 빼고, 어느 쪽이든 이전 행으로 간다.
        took = take[i][w]
        next_w = w
        if took:
            selected.append(i)
            next_w -= weights[i - 1]
        if vis:
            vis.trace(i, w, next_w, took)
            if vis.stopped():
                return None
        w = next_w
    selected.reverse()
    return best[count][capacity], selected


if __name__ == "__main__":
    vis = va.visualizer("knapsack_dp")
    while va.running():
        data = va.next_data(__file__)
        if getattr(data, "normalize_weights", False):
            # 모든 조합의 총무게는 공약수의 배수이므로 용량을 나눈 나머지는 버려도 된다.
            data.weight_unit = gcd(*data.weights) or 1
            data.original_capacity = data.capacity
            data.weights = [weight // data.weight_unit for weight in data.weights]
            data.capacity //= data.weight_unit
        vis.setup(data)
        result = knapsack(data.weights, data.values, data.capacity, vis)
        if result is not None:
            maximum, selected = result
            print("최대 가치:", maximum)
            print("선택 물건:", selected)
            vis.finish(maximum, selected)
        # Enter: 초기화, 현재 행 또는 역추적 완료까지. H: 설명. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
