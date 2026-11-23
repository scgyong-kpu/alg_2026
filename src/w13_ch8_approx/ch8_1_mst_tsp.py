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

현재 학생 코드는 heapdict의 이진 힙을 사용하므로 MST 단계가 O(m log n)이다.
거리 행렬 준비에는 간선 수와 관계없이 O(n^2) 시간과 공간을 사용한다.
이웃 차집합으로 왕복 순서를 만드는 단계와 리스트 중간 삭제로 중복을 없애는 단계도
각각 최악 O(n^2)이므로 전체 시간은 O(n^2 + m log n), 공간은 O(n^2)이다.
완전 그래프에서는 전체 시간이 O(n^2 log n)이고, m = O(n)이면 O(n^2)이다.

거리 행렬 준비를 제외해도 현재 순회와 중복 제거가 각각 최악 O(n^2)이므로
현재 구현은 O(n^2 + m log n)이다. 두 단계를 O(n)으로 개선하면 준비 비용 제외
전체가 O(m log n + n), 연결 그래프에서는 O(m log n)이 된다.
완전 그래프에서는 여전히 O(n^2 log n)이지만 m = O(n)이면 O(n log n)으로 줄어든다.
이 복잡도 비교에서는 시각화와 애니메이션 비용을 제외한다.

입력에 간선과 가중치가 이미 있으면 그것으로 MST와 방문 순서를 정할 수 있다.
MST를 고를 때는 가중치가 필요하지만, MST 이후의 순회와 중복 제거에는 거리가 필요 없다.
따라서 경로만 구한다면 전체 거리 행렬을 미리 계산할 필요가 없다.
총거리를 출력하려는 경우에도 결과 경로의 간선만 조회하면 된다. 없는 간선의 추정
거리는 그때 좌표로 계산하면 되며, n개 이동의 비용을 합산하는 데 O(n)이 걸린다.
단, 간선 목록 없이 좌표만 주어진 예제는 MST용 간선 가중치를 준비해야 한다.

Metric TSP는 완전 그래프와 삼각부등식을 전제로 한다. 희소 도로망을 도시 쌍의
최단거리로 완성해 적용한다면 그 최단거리 계산 비용도 별도로 포함해야 한다.
"""

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
    # 정점 n개와 간선 m개의 인접 목록을 만드는 데 O(n+m) 시간과 공간을 쓴다.
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


def make_walk(mst, distances, start=0):
    """MST의 각 간선을 양방향으로 한 번씩 지나는 왕복 방문 순서를 반환한다."""
    # 원본 mst는 보존하고, 순회에 사용할 가중치 없는 인접 목록을 여기서 만든다.
    tree = build_graph_without_weight(len(distances), mst)
    print("MST 인접 목록:", tree)
    vis.begin_walk(tree, start)
    # 이 인접 목록은 다시 쓰지 않으므로 복사하지 않고 tree에서 직접 지운다.
    # 정상적으로 순회를 마치면 tree의 모든 이웃 집합이 비어 있게 된다.
    visited = {start}
    walk = [start]
    current = start
    cost = 0
    while tree[current]:
        if vis.stopped():
            break
        # 남은 이웃 중 아직 방문하지 않은 도시가 있으면 그쪽으로 먼저 간다.
        # 없다면 트리에서는 되돌아갈 부모 방향 하나만 남아 있다.
        unvisited = tree[current] - visited
        # current -> neighbor만 지운다. 반대 방향은 돌아올 때 지운다.
        if unvisited:
            neighbor = unvisited.pop()
            # unvisited는 별도 집합이므로 원래 이웃 집합에서도 지운다.
            tree[current].remove(neighbor)
        else:
            neighbor = tree[current].pop()
        returning = neighbor in visited
        visited.add(neighbor)
        walk.append(neighbor)
        cost += distances[current][neighbor]
        vis.travel(current, neighbor, walk, tree, cost, returning=returning)
        current = neighbor
    # 시작점으로 돌아와 남은 방향이 없으면 끝난다. 이동은 2(n-1)번이다.
    # set 삭제는 평균 O(1)이지만 매번 차집합을 만들므로 전체는 최악 O(n^2)이다.
    return walk


def shortcut(walk):
    """왕복 방문 순서에서 중복 도시를 제외한다."""
    # 원래 왕복 순서는 보존하고 복사한 목록에서 중복 항목을 지운다.
    remaining = list(walk)
    visited = set()
    route = []
    index = 0
    vis.begin_shortcut(remaining)
    if len(walk) == 1:
        vis.shortcut_step(0, walk)
        return list(walk)
    # 마지막 시작점은 순회를 닫기 위한 것이므로 여기서는 검사하지 않는다.
    while index < len(remaining) - 1:
        if vis.stopped():
            break
        vertex = remaining[index]
        if vertex in visited:
            remaining.pop(index)
            vis.show_shortcut(vis.walk, index, remaining, route)
            # 다음 항목이 삭제한 자리로 당겨졌으므로 index를 증가시키지 않는다.
        else:
            visited.add(vertex)
            route.append(vertex)
            vis.shortcut_step(index, route)
            index += 1
    # 집합 조회는 평균 O(1)이지만 리스트 중간 삭제 때문에 전체는 최악 O(n^2)이다.
    return route


def tour_length(distances, route):
    """방문 순서에서 이웃한 도시 사이의 거리를 합산한다."""
    # 마지막에 시작점이 들어 있으면 그곳으로 돌아오는 거리도 합산된다.
    # 방문 순서 길이에 비례하는 시간이 걸린다.
    return sum(distances[u][v] for u, v in zip(route, route[1:]))


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
        walk = make_walk(mst, distances, start)
        if not vis.stopped():
            walk_cost = tour_length(distances, walk)
            print("왕복 방문 순서:", walk)
            print(f"왕복 거리: {walk_cost:,.2f}")
            vis.finish_walk(walk, walk_cost)
    if not vis.stopped():
        route = shortcut(walk)
        if not vis.stopped():
            print("처음 방문한 도시 순서:", route)
            # 도시를 한 번씩 방문한 뒤 시작점으로 돌아와 닫힌 순회를 만든다.
            route.append(start)
            vis.close_tour(route)
            if not vis.stopped():
                total_cost = tour_length(distances, route)
                print("TSP 근사 순회:", route)
                print(f"왕복 거리: {walk_cost:,.2f}")
                print(f"지름길 적용 후 거리: {total_cost:,.2f}")
                vis.finish_tour(route, total_cost)


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
