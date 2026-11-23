"""MST를 왕복한 뒤 중복 방문을 제거하여 TSP 근사 순회를 만든다.

모든 도시 쌍을 직선거리로 연결한 예제에서는 삼각부등식이 성립한다.
즉 d(u, w) <= d(u, v) + d(v, w)이므로 중간 도시를 건너뛰어도 길어지지 않는다.

이때 최적 순회에서 간선 하나를 제거하면 신장 트리가 된다.
MST는 그 트리보다 비싸지 않으므로 MST 비용 <= 최적 순회 비용이다.
MST의 간선을 양방향으로 한 번씩 지나면 비용은 2 * MST 비용이고,
중복 방문을 건너뛴 결과는 그 이하이므로 최적 순회 비용의 2배 이내이다.
항상 최적해를 구한다는 뜻도, 결과가 꼭 최적해의 두 배라는 뜻도 아니다.

4장 MST 데이터는 원래 간선과 가중치를 보존하고 없는 연결만 좌표로 추정한다.
원래 가중치와 추정값을 섞으면 삼각부등식이 깨질 수 있어 위 보장을 단정할 수 없다.
또한 MST는 원래 입력 간선만으로 만들므로, 그 비용을 추정 간선까지 포함한
완전 그래프의 최적 순회에 대한 하한이라고 단정할 수도 없다.

MST 기반 TSP 근사 알고리즘의 시간복잡도
도시 수를 n, 간선 수를 m이라 하고 연결된 단순 무방향 그래프를 기준으로 비교한다.

MST 구현                         일반 그래프          완전 그래프
배열에서 최소 후보를 찾는 Prim    O(n^2)               O(n^2)
이진 힙으로 후보를 관리하는 Prim  O(m log n)           O(n^2 log n)
Kruskal                          O(m log m)           O(n^2 log n)

힙을 쓰는 Prim은 후보 등록과 갱신마다 O(log n)의 힙 조정이 필요하다.
완전 그래프에서는 m = n(n-1)/2 = O(n^2)이므로 O(n^2 log n)이 된다.
Kruskal은 간선 정렬 때문에 O(m log m)이며, 단순 그래프에서는 O(m log n)으로도 쓴다.
희소 그래프에는 힙 기반 Prim이, 간선 목록이 주어진 경우에는 Kruskal이 적합하다.
완전 그래프에서는 배열에서 최소 후보를 선형 탐색하는 Prim이 점근적으로 유리하다.
이는 인접 행렬을 썼기 때문이 아니라 힙 없이 최소 후보를 찾기 때문이다.

MST 이후의 왕복 순회와 중복 제거는 효율적으로 구현하면 O(n)에 할 수 있다.
따라서 완전 그래프의 MST를 배열 기반 Prim으로 구하면 전체를 O(n^2)에 구현할 수 있다.
이는 TSP의 최적해를 구하는 복잡도가 아니라 위 근사 알고리즘의 복잡도이다.

이 버전은 시각화 없이 실행하며 전체 거리 행렬을 만들지 않는다.
입력 간선의 가중치로 MST를 만든 뒤, 왕복 순회와 중복 제거를 각각 O(n)에 처리한다.
MST의 각 간선을 한 번 처리하고, 미방문 도시만 새 목록에 추가하므로 이 단계는 선형이다.
직전 수업용 버전의 이웃 차집합과 리스트 중간 삭제에 따른 O(n^2) 비용은 없다.

가중치 입력이 주어진 연결 그래프에서는 그래프 준비 O(n+m), Prim O(m log n),
왕복 순회와 중복 제거 O(n), 최종 경로 거리 합산 O(n)이므로 전체는 O(m log n)이다.
전체 저장 공간은 인접 목록과 간선 목록을 포함하여 O(n+m)이다.
m = O(n)이면 O(n log n)이며 완전 그래프에서는 O(n^2 log n)이다.
간선 목록 없이 좌표만 주어진 예제는 모든 도시 쌍의 간선 가중치를 O(n^2)에 준비한다.

경로만 정할 때 전체 거리 행렬은 필요 없다. MST 선택에는 입력 가중치를 사용하지만
MST 이후의 순회와 중복 제거는 거리 없이 동작한다. 총거리는 결과의 n개 이동만
조회하여 합산하고, 입력에 없는 간선만 좌표로 거리를 추정한다.
"""

import json
import math
from pathlib import Path

from heapdict import heapdict


def build_graph_with_weight(count, edges):
    """무방향 간선 목록을 가중치가 있는 인접 리스트로 바꾼다."""
    graph = {u: {} for u in range(count)}
    for u, v, weight in edges:
        graph[u][v] = weight
        graph[v][u] = weight
    return graph


def build_graph_without_weight(count, edges):
    """무방향 간선 목록을 가중치가 없는 이웃 집합으로 바꾼다."""
    graph = {u: set() for u in range(count)}
    for u, v, _ in edges:
        graph[u].add(v)
        graph[v].add(u)
    return graph


def prim(graph, start=0):
    """입력 가중치만 사용하여 (MST 간선 목록, 비용 합)을 반환한다."""
    completed = set()
    weights = heapdict()
    weights[start] = [0, start]
    mst = []
    total_cost = 0
    while weights:
        vertex, (cost, origin) = weights.popitem()
        completed.add(vertex)
        if vertex != origin:
            mst.append((origin, vertex, cost))
            total_cost += cost
        for neighbor, edge_cost in graph[vertex].items():
            if neighbor in completed:
                continue
            old_candidate = weights.get(neighbor)
            if old_candidate is None or edge_cost < old_candidate[0]:
                weights[neighbor] = [edge_cost, vertex]
    return mst, total_cost


def make_walk(mst, count, start=0):
    """MST의 각 간선을 두 번 지나는 왕복 순서를 O(n)에 만든다."""
    tree = build_graph_without_weight(count, mst)
    walk = [start]
    stack = [start]
    while stack:
        current = stack[-1]
        if tree[current]:
            neighbor = tree[current].pop()
            # 양방향을 함께 지워서 부모로 다시 내려가는 것을 막는다.
            # 부모로 돌아오는 이동은 스택에서 자식을 뺄 때 기록한다.
            tree[neighbor].remove(current)
            walk.append(neighbor)
            stack.append(neighbor)
        else:
            stack.pop()
            if stack:
                walk.append(stack[-1])
    # 각 집합 원소를 한 번씩 제거하므로 평균 O(n), 스택 공간은 O(n)이다.
    return walk


def shortcut(walk):
    """목록 중간을 삭제하지 않고 첫 방문만 추가하여 평균 O(n)에 처리한다."""
    visited = set()
    route = []
    for vertex in walk:
        if vertex not in visited:
            visited.add(vertex)
            route.append(vertex)
    return route


def tour_length(positions, graph, route):
    """결과 경로에 쓰인 간선의 비용만 조회하거나 추정하여 합산한다."""
    total = 0
    for u, v in zip(route, route[1:]):
        if u == v:
            continue
        if v in graph[u]:
            total += graph[u][v]
        else:
            total += math.dist(positions[u], positions[v])
    return total


def mst_tsp(positions, start=0, edges=None):
    """시각화와 전체 거리 행렬 없이 (순회 경로, 거리 합)을 반환한다."""
    count = len(positions)
    if count == 0 or not 0 <= start < count:
        raise ValueError("도시가 하나 이상 있어야 하며 시작점은 정점 범위 안이어야 한다.")
    if edges is None:
        edges = [(u, v, math.dist(positions[u], positions[v]))
                 for u in range(count) for v in range(u + 1, count)]
    graph = build_graph_with_weight(count, edges)
    mst, _ = prim(graph, start)
    if len(mst) != count - 1:
        raise ValueError("입력 그래프가 연결되지 않아 전체 MST를 만들 수 없다.")
    walk = make_walk(mst, count, start)
    route = shortcut(walk)
    route.append(start)
    return route, tour_length(positions, graph, route)


if __name__ == "__main__":
    path = Path(__file__).parent / "data/ch8_1_mst_tsp.json"
    for entry in json.loads(path.read_text(encoding="utf-8"))["datasets"]:
        data = entry["data"]
        positions = [point for _, point in data["pos_verts"]]
        route, total_cost = mst_tsp(positions, data["start"], data.get("edges"))
        print(entry["name"])
        print("TSP 근사 순회:", route)
        print(f"지름길 적용 후 거리: {total_cost:,.2f}")
