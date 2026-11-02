"""분할 가능한 배낭: 물건은 [무게, 가치]로 표현한다."""

import pyvisalgo as va


def knapsack(items, capacity):
    """물건 목록과 배낭의 최대 무게를 받는다."""
    pass


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
