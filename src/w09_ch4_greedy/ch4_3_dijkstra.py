"""Prim과 Dijkstra는 비슷한 후보 관리 구조를 사용하지만 구하려는 결과가 다르다.

Prim: 모든 정점을 연결하는 트리 중 간선 가중치의 합이 최소인 트리(MST)를 구한다.
Dijkstra: 주어진 시작점에서 각 정점까지의 최단 경로와 그 거리를 구한다.
MST에서도 두 점 사이의 경로를 찾을 수 있지만 그 경로가 최단이라는 보장은 없다.
Dijkstra의 경로들을 모으면 최단 경로 트리가 되지만 그 트리가 MST인 것은 아니다.

예를 들어 A-B=2, B-C=2, A-C=3이면 MST는 A-B와 B-C로 총비용 4이다.
그러나 A에서 C까지의 최단 경로는 A-C로 거리 3이다(A-B-C는 거리 4).
A에서 시작하는 최단 경로 트리는 A-B와 A-C이며 간선 가중치의 합은 5이다.
따라서 비용 계산 한 줄의 변화는 전체 연결 비용이 아닌 경로의 누적 거리를
최소화한다는 문제 목적의 차이에서 나온다. Dijkstra는 음수 가중치를 허용하지 않는다.
"""

from heapdict import heapdict

import pyvisalgo as va


def build_graph(count, edges):
    """무방향 간선 목록을 정점별 이웃과 가중치의 딕셔너리로 바꾼다."""
    # graph[u]는 u의 이웃을 key로, 연결 간선의 가중치를 value로 갖습니다.
    # 간선이 없는 정점도 빈 딕셔너리를 가지며, 정점 번호는 0부터 count-1입니다.
    graph = {u: {} for u in range(count)}
    for u, v, weight in edges:
        if weight < 0:
            raise ValueError("Dijkstra는 음수 가중치가 없는 그래프에서 사용합니다.")
        # 무방향 간선 하나를 양쪽 정점의 이웃 정보에 모두 등록합니다.
        graph[u][v] = weight
        graph[v][u] = weight
    return graph


def dijkstra(count, edges, start=0):
    """시작점에서 각 정점까지의 (최단 거리 배열, 이전 정점 배열)을 반환한다."""
    if not 0 <= start < count:
        raise ValueError("시작 정점 번호가 범위를 벗어났습니다.")
    # 정점 하나의 최단 거리를 확정할 때마다 그 정점에 연결된 이웃들을 검사합니다.
    # 전체 간선 목록 대신 graph[vertex].items()로 이웃과 가중치를 얻도록 준비합니다.
    graph = build_graph(count, edges)
    # completed는 시작점부터의 최단 거리를 확정한 정점들의 집합입니다.
    # 같은 정점을 다시 확정하거나 후보로 추가하지 않도록 소속 여부를 검사합니다.
    completed = set()
    # 확정 전의 거리는 무한대로 둡니다. 도달할 수 없는 정점은 끝까지 무한대입니다.
    distances = [float("inf")] * count
    # previous[v]는 최단 경로에서 v 바로 앞의 정점입니다. 역추적하면 경로를 복원합니다.
    # 거리만 저장하면 경로를 알 수 없으므로, 어떤 정점을 거쳐 왔는지도 함께 남깁니다.
    # 시작점과 도달할 수 없는 정점에는 이전 정점이 없어 None으로 둡니다.
    previous = [None] * count
    # heapdict: weights[vertex_to] = [시작점부터의 누적 거리, vertex_from]
    # 딕셔너리처럼 정점 번호를 key로 등록·조회하면서 value가 최소인 후보를 꺼냅니다.
    # value의 첫 항목인 비용부터 비교하고, 같으면 다음 항목인 출발점을 비교합니다.
    # value 전체가 같을 때 정점 번호나 등록 순서에 따른 추출 순서는 가정하지 않습니다.
    # 현재 후보 수 k에 대해 key 조회는 평균 O(1), 등록·갱신·최소 추출은 O(log k)입니다.
    # 같은 key에 새 value를 대입하면 해당 후보를 교체하고 힙의 위치도 조정합니다.
    # weights[vertex][0]을 직접 수정하면 이 조정이 일어나지 않으므로 피해야 합니다.
    # Prim과 달리 후보의 비용은 간선 하나가 아니라 시작점부터의 누적 거리입니다.
    weights = heapdict()
    # 시작점은 연결 간선 없이 출발하므로 비용 0, 출발점은 자기 자신으로 둡니다.
    # 이 항목은 실제 간선이 아니며, 시작점의 거리도 꺼내는 시점에 확정합니다.
    weights[start] = [0, start]
    vis.add_candidate(start, 0, start, weights, starting=True)
    # 후보가 남아 있는 동안 시작점부터의 누적 거리가 가장 작은 정점을 꺼냅니다.
    while weights:
        if vis.stopped():
            break
        # popitem()은 최소 value를 가진 (key, value)를 반환하면서 후보를 제거합니다.
        # 일반 dict.popitem()의 마지막 등록 항목 추출과는 의미가 다릅니다.
        # key는 정점 번호, value는 [누적 거리, 이전 정점]이므로 두 단계로 풀어 받습니다.
        vertex, (cost, origin) = weights.popitem()
        # 가중치가 0 이상이므로 최소 후보를 꺼낸 순간 그 거리가 최단 거리입니다.
        completed.add(vertex)
        distances[vertex] = cost
        if vertex != origin:
            previous[vertex] = origin
        # 정점이 확정되면 할 일:
        # 1. 최단 거리와 경로상의 이전 정점을 기록합니다. 거리들을 합산하지 않습니다.
        # 2. 주위 정점들에 대하여 다음을 수행합니다.
        #    - 이미 최단 거리가 확정된 정점이면 무시합니다.
        #    - 후보에 없으면 누적 거리와 이전 정점을 기록하여 새로 등록합니다.
        #    - 기존 후보보다 더 짧은 경로이면 거리와 이전 정점을 갱신합니다.
        #    - 기존 후보와 같거나 더 비싼 연결이면 기존 후보를 유지합니다.
        vis.take_candidate(vertex, cost, origin, weights)
        vis.show_neighbors(vertex, graph[vertex])
        # graph[vertex]의 key는 이웃 정점, value는 두 정점을 잇는 간선의 가중치입니다.
        # items()로 두 값을 함께 받아 현재 정점을 경유하는 경로의 도착점을 검사합니다.
        for neighbor, edge_cost in graph[vertex].items():
            if vis.stopped():
                break
            vis.inspect_edge(vertex, neighbor, edge_cost)
            # 이미 최단 거리가 확정된 정점은 후보로 다시 등록하지 않습니다.
            if neighbor in completed:
                vis.ignore_inland(vertex, neighbor)
                continue
            # Prim의 candidate_cost = edge_cost와 달라지는 핵심 한 줄입니다.
            # 현재 정점까지의 최단 거리에 다음 간선의 가중치를 더합니다.
            candidate_cost = cost + edge_cost
            # 결과로 보면 후보를 바꾸지 않거나, 새 비용과 출발점을 대입하거나 둘뿐입니다.
            # 새 후보 등록과 기존 후보 갱신은 같은 대입으로 처리할 수 있습니다.
            old_candidate = weights.get(neighbor)
            if old_candidate is None or candidate_cost < old_candidate[0]:
                # or는 왼쪽이 참이면 오른쪽을 평가하지 않습니다.
                # 따라서 후보가 없어 None인 경우에도 old_candidate[0]을 읽지 않습니다.
                # 새 리스트를 대입해야 heapdict가 힙의 위치도 다시 조정합니다.
                weights[neighbor] = [candidate_cost, vertex]
                # 아래 분기는 추가와 갱신을 서로 다른 애니메이션으로 표시하기 위한 것입니다.
                if old_candidate is None:
                    vis.add_candidate(neighbor, candidate_cost, vertex, weights)
                else:
                    vis.update_candidate(neighbor, *old_candidate,
                                         candidate_cost, vertex, weights)
            else:
                # 같거나 더 비싼 연결이면 아무것도 대입하지 않고 기존 후보를 유지합니다.
                vis.keep_candidate(neighbor, *old_candidate, candidate_cost, vertex)

    # 후보가 소진되면 시작점에서 도달할 수 있는 정점들의 탐색이 끝납니다.
    # 도달 불가 정점은 (거리 inf, 이전 정점 None)인 상태로 남습니다.
    return distances, previous


if __name__ == "__main__":
    vis = va.visualizer("dijkstra")
    while va.running():
        # Prim과 같은 무방향 그래프를 사용하되 누적 거리로 후보를 선택합니다.
        data = va.next_data(__file__, data_file="data/ch4_1_mst_kruskal.json")
        count = len(data.vertices)
        start = 0
        vis.setup(data, start)
        distances, previous = dijkstra(count, data.edges, start)
        # 사용자가 중간에 중지했다면 부분 결과를 최종 결과로 표시하지 않습니다.
        if not vis.stopped():
            print("시작점:", start, data.vertices[start])
            for vertex, distance in enumerate(distances):
                if distance == float("inf"):
                    print(f"#{vertex} {data.vertices[vertex]}: 도달 불가")
                    continue
                path = []
                current = vertex
                # 목적지에서 previous를 따라가면 시작점까지 역순으로 얻습니다.
                # 예: previous[C]=B, previous[B]=A이면 C, B, A 순서입니다.
                while current is not None:
                    path.append(current)
                    current = previous[current]
                path.reverse()  # 뒤집어 시작점 → 목적지의 실제 이동 순서로 출력합니다.
                print(f"#{vertex} {data.vertices[vertex]}: 거리 {distance}, 경로", " -> ".join(map(str, path)))
            vis.finish_paths()
        # H: 설명 숨김, L: 배치 전환, 정점 드래그: 배치, 빈 곳 드래그: 이동.
        # 휠: 그래프 확대/축소 또는 오른쪽 후보 배열 스크롤.
        # R: 재실행, D: 다음 데이터, Esc: 종료.
        vis.wait()
