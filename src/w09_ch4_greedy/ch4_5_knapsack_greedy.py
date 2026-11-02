"""분할 가능한 배낭: 물건은 [무게, 가치]로 표현한다.

물건은 원하는 비율로 나눌 수 있고 그 비율만큼 가치를 얻습니다.
단위 무게당 가치가 높은 물건부터 담으면 같은 용량에서 얻는 가치가 최대입니다.
물건을 쪼갤 수 없는 0/1 배낭은 같은 탐욕 선택으로 최적해를 보장하지 않습니다.
정렬은 O(n log n), 단가 계산과 담기는 각각 O(n)이며 추가 공간은 O(n)입니다.
"""

import pyvisalgo as va


def knapsack(items, capacity):
    """원래 번호별 선택 무게 배열과 총가치를 반환한다. 입력 목록은 변경하지 않는다."""
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
            # 물건을 나누어도 단가가 유지되므로 남은 용량만큼만 담을 수 있습니다.
            # 원래 가치에 (담은 무게 / 원래 무게)를 곱한 만큼의 가치를 얻습니다.
            selected[index] = remaining
            total_value += value * (remaining / weight)
            vis.take(index, remaining)
            remaining = 0
            # 배낭이 가득 찼으므로 더 낮은 단가의 물건까지 볼 필요가 없습니다.
            break
    return selected, total_value


if __name__ == "__main__":
    vis = va.visualizer("knapsack_greedy")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        result = knapsack(data.items, data.capacity)
        # 중지한 부분 결과는 완성된 결과로 출력하지 않습니다.
        if not vis.stopped():
            selected, total_value = result
            for index, ((weight, value), amount) in enumerate(zip(data.items, selected)):
                earned = value * (amount / weight)
                print(f"#{index}: 무게 {amount:g}/{weight:g}, 얻은 가치 {earned:g}")
            print(f"총무게: {sum(selected):g}/{data.capacity:g}, 총가치: {total_value:g}")
            vis.finish()
        # 물건: [무게, 가치]. 높이는 같고 사각형의 가로 길이는 무게에 비례합니다.
        # R: 재실행, D: 다음 데이터, Space: 일시정지, .: 한 단계.
        # Enter: 다음 구간, 1~9: 속도, +/-: 글씨 크기, Esc: 종료.
        vis.wait()
