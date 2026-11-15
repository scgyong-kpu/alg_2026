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


def chained_matrix_mult(sizes, vis=None):
    """sizes[i], sizes[i+1]이 행렬 Ai의 행 수와 열 수다."""
    if len(sizes) < 2 or any(type(size) is not int or size <= 0 for size in sizes):
        raise ValueError("양의 정수로 된 행렬 차원이 두 개 이상 필요합니다.")
    count = len(sizes) - 1
    # cost[i][j]는 양 끝을 포함한 Ai..Aj의 최소 스칼라 곱셈 횟수입니다.
    # 대각선 cost[i][i]는 행렬 하나뿐이므로 곱셈이 필요 없어 0입니다.
    cost = [[0] * count for _ in range(count)]
    # split[i][j]에는 마지막 곱셈에서 왼쪽 구간의 끝 인덱스를 기록할 예정입니다.
    split = [[None] * count for _ in range(count)]
    if vis:
        vis.start(sizes, cost, split)
        if vis.stopped():
            return None

    # 짧은 구간의 결과를 재사용하며 전체 행렬 길이까지 계산합니다.
    for length in range(2, count + 1):
        for left in range(count - length + 1):
            right = left + length - 1  # 양 끝 포함: Aleft부터 Aright까지.
            cost[left][right] = inf
            for mid in range(left, right):
                if vis and vis.stopped():
                    return None
                # mid는 왼쪽에 포함: [left..mid]와 [mid+1..right].
                candidate = (cost[left][mid] + cost[mid + 1][right]
                             + sizes[left] * sizes[mid + 1] * sizes[right + 1])
                if vis:
                    vis.compare(left, right, mid, candidate)
                    if vis.stopped():
                        return None
                if candidate < cost[left][right]:
                    cost[left][right] = candidate
                    split[left][right] = mid
                    if vis:
                        vis.update_cost()
            if vis:
                vis.end_range()
    if vis and vis.stopped():
        return None
    return cost, split


def optimal_order(split, left, right):
    """양 끝을 포함한 구간의 최적 괄호 묶음을 저장된 분할 위치로 복원한다."""
    if left == right:
        return f"A{left}"
    # mid는 왼쪽 구간에 포함됩니다. 두 부분을 각각 복원한 뒤 괄호로 묶습니다.
    mid = split[left][right]
    return f"({optimal_order(split, left, mid)} × {optimal_order(split, mid + 1, right)})"


if __name__ == "__main__":
    vis = va.visualizer("chained_matrix_mult")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        result = chained_matrix_mult(data.sizes, vis)
        if result is not None:
            cost, split = result
            order = optimal_order(split, 0, len(data.sizes) - 2)
            print("최소 곱셈 횟수:", cost[0][-1])
            print("최적 괄호 묶음:", order)
            vis.finish(order)
        # Enter: 현재 구간까지 계산. V: 표/역삼각형. H: 설명.
        vis.wait()
