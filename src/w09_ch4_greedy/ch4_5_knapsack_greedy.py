"""분할 가능한 배낭: 물건은 [무게, 가치]로 표현한다."""

import pyvisalgo as va


def knapsack(items, capacity):
    """물건 목록과 배낭의 최대 무게를 받는다."""
    # 무게는 양수, 가치는 0 이상, 용량은 0 이상인 데이터를 사용합니다.
    # 정렬할 정보는 (단가, 원래 번호, 무게, 가치)로 모읍니다.
    # 원래 번호를 남겨야 정렬한 뒤에도 어떤 물건을 골랐는지 알 수 있습니다.
    ranked = []
    for index, (weight, value) in enumerate(items):
        if vis.stopped():
            return
        unit_value = value / weight
        ranked.append((unit_value, index, weight, value))
        vis.measure(index, unit_value)


if __name__ == "__main__":
    vis = va.visualizer("knapsack_greedy")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        knapsack(data.items, data.capacity)
        # 물건: [무게, 가치]. 높이는 같고 사각형의 가로 길이는 무게에 비례합니다.
        # R: 재실행, D: 다음 데이터, Space: 일시정지, .: 한 단계.
        # Enter: 다음 구간, 1~9: 속도, +/-: 글씨 크기, Esc: 종료.
        vis.wait()
