"""행렬의 순서는 유지하고 괄호 묶음을 바꾸어 스칼라 곱셈 횟수를 최소화한다."""

from math import inf
from itertools import permutations

import pyvisalgo as va


def multiplication_orders(sizes, vis=None):
    """원래 행렬 사이의 경계를 없애는 순서를 모두 나열한다."""
    if len(sizes) < 2 or any(type(size) is not int or size <= 0 for size in sizes):
        raise ValueError("양의 정수로 된 행렬 차원이 두 개 이상 필요합니다.")
    count = len(sizes) - 1
    best_cost, best_order = inf, ""
    if vis:
        vis.start_orders()
    # 경계 i는 Ai와 Ai+1 사이. 경계를 없애는 순서가 곱셈 실행 순서입니다.
    # permutations(range(3))은 (0,1,2), (0,2,1), ... 처럼 3!개의 순열을 하나씩 반환합니다.
    # 행렬 자체의 순서는 바꾸지 않습니다. 행렬 n개 사이의 경계 n-1개를 나열합니다.
    for order in permutations(range(count - 1)):
        if vis and vis.stopped():
            return None
        groups = [(i, i, f"A{i}") for i in range(count)]
        total = 0
        for boundary in order:
            index = next(i for i, group in enumerate(groups) if group[1] == boundary)
            left, mid, a = groups[index]
            _, right, b = groups[index + 1]
            total += sizes[left] * sizes[mid + 1] * sizes[right + 1]
            groups[index:index + 2] = [(left, right, f"({a} × {b})")]
        expression = groups[0][2]
        if total < best_cost:
            best_cost, best_order = total, expression
        if vis:
            vis.add_order(order, expression, total)
    if vis and vis.stopped():
        return None
    return best_cost, best_order


if __name__ == "__main__":
    vis = va.visualizer("chained_matrix_mult")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        result = multiplication_orders(data.sizes, vis)
        if result is not None:
            cost, order = result
            print("최소 곱셈 횟수:", cost)
            print("최적 괄호 묶음:", order)
            vis.finish_orders()
        # Enter: 나머지 실행 순서까지 나열. 휠: 목록 스크롤. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
