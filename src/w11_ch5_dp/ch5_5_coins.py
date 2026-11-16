"""각 동전을 여러 번 사용해 목표 금액을 정확히 만드는 최소 동전 수를 구한다."""

import pyvisalgo as va


def coin_change(coins, amount, vis=None):
    pass


if __name__ == "__main__":
    vis = va.visualizer("coin_change")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        coin_change(data.coins, data.amount, vis)
        # H: 설명 숨기기/표시. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
