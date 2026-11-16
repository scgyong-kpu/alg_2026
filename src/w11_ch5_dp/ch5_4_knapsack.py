"""물건을 쪼개지 않고, 각 물건을 최대 한 번 담아 가치를 최대화한다."""

import pyvisalgo as va


def knapsack(weights, values, capacity, vis=None):
    count = len(weights)
    # best[i][w]: 물건 1번부터 i번까지 고려할 때, 용량 w에서 얻는 최대 가치.
    # 물건이 없거나(i=0) 용량이 0이면(w=0) 최대 가치는 0이다.
    best = [[0] * (capacity + 1) for _ in range(count + 1)]
    if vis:
        vis.initialize(best)
        if vis.stopped():
            return None

    # 이번 단계에서는 첫 번째 물건을 고려하는 행만 계산한다.
    for i in range(1, min(count, 1) + 1):
        weight, value = weights[i - 1], values[i - 1]
        for w in range(1, capacity + 1):
            skip_value = best[i - 1][w]
            take_value = None
            if weight <= w:
                # 물건을 담고 남은 용량도 이전 행에서 조회한다.
                take_value = best[i - 1][w - weight] + value
            if vis:
                vis.compare(i, w, skip_value, take_value)
                if vis.stopped():
                    return None

            # 동점이거나 담을 수 없으면 기존 값을 유지한다.
            took = take_value is not None and take_value > skip_value
            best[i][w] = take_value if took else skip_value
            if vis:
                vis.place(took)
                if vis.stopped():
                    return None
    return best


if __name__ == "__main__":
    vis = va.visualizer("knapsack_dp")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        knapsack(data.weights, data.values, data.capacity, vis)
        # Enter: 초기값 채우기 완료까지. H: 설명. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
