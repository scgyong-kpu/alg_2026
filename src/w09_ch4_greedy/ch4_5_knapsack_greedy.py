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

    # 단가만 key로 비교합니다. 단가가 같으면 Python의 안정 정렬로 입력 순서를 유지합니다.
    # 튜플 전체를 역순 정렬하면 번호까지 역순으로 비교하게 되므로 key를 지정합니다.
    ranked.sort(key=lambda item: item[0], reverse=True)
    vis.sort_items([index for _, index, _, _ in ranked])

    remaining = capacity
    total_value = 0
    # selected[index]는 원래 물건 index에서 담은 무게입니다. 아직 안 담았으면 0입니다.
    selected = [0] * len(items)
    for unit_value, index, weight, value in ranked:
        if vis.stopped():
            return
        if remaining <= 0:
            break
        if weight <= remaining:
            selected[index] = weight
            remaining -= weight
            total_value += value
            vis.take(index, weight)
        else:
            # 아직 분할은 구현하지 않았습니다. 들어가지 않는 물건에서 멈춥니다.
            # 이 중간 단계의 결과가 분할 배낭의 최적해라는 뜻은 아닙니다.
            break


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
