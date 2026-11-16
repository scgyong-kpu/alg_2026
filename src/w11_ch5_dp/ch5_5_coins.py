"""각 동전을 여러 번 사용해 목표 금액을 정확히 만드는 최소 동전 수를 구한다."""

from math import inf

import pyvisalgo as va


def coin_change(coins, amount, vis=None):
    # count[money]: 금액 money를 정확히 만드는 데 필요한 최소 동전 수.
    # 0은 동전 없이 만들 수 있고, 나머지는 아직 방법을 모르므로 inf로 둔다.
    count = [inf] * (amount + 1)
    count[0] = 0
    # 마지막으로 더한 동전은 조합을 찾은 뒤에 기록한다.
    last_coin = [None] * (amount + 1)
    if vis:
        vis.initialize(count, last_coin)
        if vis.stopped():
            return None
    return count, last_coin


if __name__ == "__main__":
    vis = va.visualizer("coin_change")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        coin_change(data.coins, data.amount, vis)
        # H: 설명 숨기기/표시. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
