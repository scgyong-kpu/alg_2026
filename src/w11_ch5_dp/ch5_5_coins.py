"""각 동전을 여러 번 사용해 목표 금액을 정확히 만드는 최소 동전 수를 구한다."""

from math import inf

import pyvisalgo as va


def coin_change(coins, amount, vis=None):
    # count[money]: 금액 money를 정확히 만드는 데 필요한 최소 동전 수.
    # 0은 동전 없이 만들 수 있고, 나머지는 아직 방법을 모르므로 inf로 둔다.
    count = [inf] * (amount + 1)
    count[0] = 0
    # 더 작은 금액의 조합에 추가한 동전은 조합을 찾은 뒤에 기록한다.
    last_coin = [None] * (amount + 1)
    if vis:
        vis.initialize(count, last_coin)
        if vis.stopped():
            return None

    # 이번 단계에서는 금액 1에 대해서만 최솟값을 구한다.
    for money in range(1, min(amount, 1) + 1):
        for coin in coins:
            # 남은 금액을 만드는 데 필요한 동전 수에 지금 동전 하나를 더한다.
            previous = money - coin
            candidate = count[previous] + 1 if previous >= 0 else inf
            if vis:
                vis.compare(money, coin, candidate)
                if vis.stopped():
                    return None
            # 동전 수가 줄어들 때만 새 조합을 기록한다.
            if candidate < count[money]:
                count[money] = candidate
                last_coin[money] = coin
                if vis:
                    vis.place()
                    if vis.stopped():
                        return None
        if vis:
            vis.end_amount(money)
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
