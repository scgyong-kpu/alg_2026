"""물건을 쪼개지 않고, 각 물건을 최대 한 번 담아 가치를 최대화한다."""

import pyvisalgo as va


def knapsack(weights, values, capacity, vis=None):
    pass


if __name__ == "__main__":
    vis = va.visualizer("knapsack_dp")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        knapsack(data.weights, data.values, data.capacity, vis)
        # H: 설명 숨기기/표시. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
