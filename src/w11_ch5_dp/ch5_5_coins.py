"""각 동전을 여러 번 사용해 목표 금액을 정확히 만드는 최소 동전 수를 구한다."""

from math import inf

import pyvisalgo as va


def coin_change(coins, amount, vis=None):
    if (type(amount) is not int or amount < 0
            or any(type(coin) is not int or coin <= 0 for coin in coins)):
        raise ValueError("동전은 양의 정수, 목표 금액은 음이 아닌 정수여야 합니다.")

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

    # 동전의 값은 양수이므로 남은 금액의 최솟값을 먼저 구할 수 있도록 오름차순으로 계산한다.
    for money in range(1, amount + 1):
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

    selected = []
    if count[amount] != inf:
        money = amount
        while money > 0:
            # 기록된 동전을 빼면 이 동전을 추가하기 전의 금액으로 돌아간다.
            coin = last_coin[money]
            selected.append(coin)
            if vis:
                vis.trace(money, coin)
                if vis.stopped():
                    return None
            money -= coin
        selected.reverse()  # 역추적에서 찾은 순서를 실제로 더한 순서로 뒤집는다.
    return count[amount], selected


if __name__ == "__main__":
    vis = va.visualizer("coin_change")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        result = coin_change(data.coins, data.amount, vis)
        if result is not None:
            minimum, selected = result
            if minimum == inf:
                print("목표 금액을 만들 수 없습니다:", data.amount)
            else:
                print("최소 동전 수:", minimum, "선택 동전:", selected)
            vis.finish(minimum, selected)
        # Enter: 초기화, 현재 금액의 계산 또는 역추적이 끝날 때까지.
        # H: 설명. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
