"""MST를 왕복한 뒤 중복 방문을 제거하여 TSP 근사 순회를 만든다."""

import math

from heapdict import heapdict

import pyvisalgo as va


def build_distances(positions, edges=None):
    """입력 간선은 원래 가중치로, 없는 간선은 좌표 기반 추정값으로 채운다."""
    # distances[u][v]는 도시 u에서 v로 이동할 비용이다. 자기 자신까지는 0이다.
    # 없는 간선은 나중에 중복 방문을 건너뛸 때 사용할 수 있도록 직선거리로 추정한다.
    # 계산값은 반올림하지 않고, 화면과 출력에서만 소수 자릿수를 줄인다.
    distances = [[math.dist(a, b) for b in positions] for a in positions]
    if edges is not None:
        for u, v, weight in edges:
            # 무방향 입력 간선은 원래 가중치를 양방향에 그대로 기록한다.
            distances[u][v] = distances[v][u] = weight
    return distances


def build_graph_with_weight(count, edges):
    """무방향 간선 목록을 가중치가 있는 인접 리스트로 바꾼다."""
    # graph[u]는 이웃 v를 key로, 연결 비용을 value로 갖는 딕셔너리이다.
    graph = {u: {} for u in range(count)}
    for u, v, weight in edges:
        graph[u][v] = weight
        graph[v][u] = weight
    return graph


def build_graph_without_weight(count, edges):
    """무방향 간선 목록을 가중치가 없는 이웃 집합으로 바꾼다."""
    # Prim은 연결 비용이 필요했지만 MST를 순회할 때는 이웃 번호만 있으면 된다.
    # graph[u]는 u와 연결된 정점 번호의 set이다. 가중치는 저장하지 않는다.
    graph = {u: set() for u in range(count)}
    for u, v, _ in edges:
        graph[u].add(v)
        graph[v].add(u)
    # set은 순서를 보장하지 않으므로 이후의 방문 순서는 달라질 수 있다.
    return graph


def prim(distances, start=0, edges=None):
    """(MST 간선 목록, 비용 합)을 반환한다."""
    # MST는 입력 간선만 사용한다. 없는 간선의 추정값을 후보에 추가하지 않는다.
    # 간선 목록이 없는 도시 배치 예제만 모든 쌍의 직선거리로 연결한다.
    count = len(distances)
    if edges is None:
        edges = [(u, v, distances[u][v])
                 for u in range(count) for v in range(u + 1, count)]
    graph = build_graph_with_weight(count, edges)

    # Prim에서 배운 것처럼 weights[정점] = [최소 연결 비용, 출발 정점]이다.
    completed = set()
    weights = heapdict()
    weights[start] = [0, start]
    mst = []
    total_cost = 0
    vis.add_candidate(start, 0, start, weights, starting=True)
    while weights:
        if vis.stopped():
            break
        vertex, (cost, origin) = weights.popitem()
        completed.add(vertex)
        if vertex != origin:
            mst.append((origin, vertex, cost))
            total_cost += cost
        vis.take_candidate(vertex, cost, origin, weights, total_cost)
        neighbors = graph[vertex]
        vis.show_neighbors(vertex, neighbors)
        for neighbor, edge_cost in neighbors.items():
            if vis.stopped():
                break
            vis.inspect_edge(vertex, neighbor, edge_cost)
            if neighbor in completed:
                vis.ignore_inland(vertex, neighbor)
                continue
            # 시작점부터의 누적 거리가 아니라 연결할 간선 하나의 비용을 비교한다.
            old_candidate = weights.get(neighbor)
            if old_candidate is None or edge_cost < old_candidate[0]:
                weights[neighbor] = [edge_cost, vertex]
                if old_candidate is None:
                    vis.add_candidate(neighbor, edge_cost, vertex, weights)
                else:
                    vis.update_candidate(neighbor, *old_candidate, edge_cost, vertex, weights)
            else:
                vis.keep_candidate(neighbor, *old_candidate, edge_cost, vertex)
    return mst, total_cost


def make_walk(tree, distances, start=0):
    """MST의 각 간선을 양방향으로 한 번씩 지나는 왕복 방문 순서를 반환한다."""
    pass


def shortcut(walk):
    """왕복 방문 순서에서 중복 도시를 제외한다."""
    pass


def tour_length(distances, route):
    """방문 순서에서 이웃한 도시 사이의 거리를 합산한다."""
    pass


def mst_tsp(positions, start=0, edges=None):
    """MST 구성, 왕복 순회, 중복 제거를 차례로 실행한다."""
    distances = build_distances(positions, edges)
    mst, mst_cost = prim(distances, start, edges)
    if not vis.stopped():
        print("MST 간선:", mst)
        print(f"MST 비용: {mst_cost:,.2f}")
        vis.finish_mst(len(positions), mst, mst_cost)
        if len(mst) != len(positions) - 1:
            vis.msg_action("입력 그래프가 연결되지 않아 전체 MST를 만들 수 없다.")
            return
    if not vis.stopped():
        # 같은 간선 목록 형식이지만 이번에는 MST 간선만 넣고 가중치는 제외한다.
        tree = build_graph_without_weight(len(positions), mst)
        print("MST 인접 목록:", tree)
        vis.begin_walk(tree, start)


if __name__ == "__main__":
    vis = va.visualizer("mst_tsp")
    while va.running():
        data = va.next_data(__file__)
        start = data.start
        edges = getattr(data, "edges", None)
        vis.setup(data, start)
        vis.msg_action("도시 좌표, 입력 간선과 시작점을 준비한다.")
        vis.msg_detail("아직 MST나 방문 순서를 구하지 않은 상태이다.")
        mst_tsp(data.positions, start, edges)
        # H: 설명 숨김/표시, E: 전체 간선 표시.
        # 휠: 확대/축소 또는 목록 스크롤, 드래그: 평면 이동, 모서리 버튼: 화면 맞춤.
        # Enter: 다음 동작까지, Shift+Enter: MST 완성까지 진행한 뒤 일시정지.
        # D/Shift+D: 다음/이전 데이터, R: 재실행, Esc: 종료.
        vis.wait()
