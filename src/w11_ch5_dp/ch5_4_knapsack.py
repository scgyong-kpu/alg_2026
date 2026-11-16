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

    # 첫 번째 물건만 고려한다. 담을 수 있는 용량부터는 다음 단계에서 계산한다.
    for i in range(1, min(count, 1) + 1):
        weight = weights[i - 1]
        for w in range(1, capacity + 1):
            if weight <= w:
                break
            # 물건을 담을 수 없으면 이전 물건까지 고려한 최댓값을 그대로 쓴다.
            skip_value = best[i - 1][w]
            if vis:
                vis.compare(i, w, skip_value, None)
                if vis.stopped():
                    return None
            best[i][w] = skip_value
            if vis:
                vis.place(False)
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
