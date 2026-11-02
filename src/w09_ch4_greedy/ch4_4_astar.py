"""목적지까지의 최단 경로: 먼저 Dijkstra의 누적 비용 기준으로 탐색한다."""
import math

from heapdict import heapdict

import pyvisalgo as va


def build_graph(count, edges):
    """무방향 간선 목록을 정점별 이웃과 가중치의 딕셔너리로 바꾼다."""
    # graph[u]는 u의 이웃을 key로, 연결 간선의 가중치를 value로 갖습니다.
    # 간선이 없는 정점도 빈 딕셔너리를 가지며, 정점 번호는 0부터 count-1입니다.
    graph = {u: {} for u in range(count)}
    for u, v, weight in edges:
        if not (0 <= u < count and 0 <= v < count) or u == v:
            raise ValueError("정점 범위와 자기 루프 여부를 확인하세요.")
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("간선 가중치는 유한한 음수가 아닌 수여야 합니다.")
        if v in graph[u] and graph[u][v] != weight:
            raise ValueError("같은 간선에 서로 다른 가중치를 지정할 수 없습니다.")
        # 무방향 간선 하나를 양쪽 정점의 이웃 정보에 모두 등록합니다.
        graph[u][v] = weight
        graph[v][u] = weight
    return graph


def astar(count, edges, start, goal):
    """목적지까지의 (경로, 실제 비용)을 반환한다. 경로가 없으면 ([], inf)이다."""
    if not (0 <= start < count and 0 <= goal < count):
        raise ValueError("시작점과 목적지가 정점 범위 안에 있어야 합니다.")
    # 정점 하나의 최단 거리를 확정할 때마다 그 정점에 연결된 이웃들을 검사합니다.
    # 전체 간선 목록 대신 graph[vertex].items()로 이웃과 가중치를 얻도록 준비합니다.
    graph = build_graph(count, edges)
    # completed는 시작점부터의 최단 거리를 확정한 정점들의 집합입니다.
    # 같은 정점을 다시 확정하거나 후보로 추가하지 않도록 소속 여부를 검사합니다.
    completed = set()
    # previous[v]는 최단 경로에서 v 바로 앞의 정점입니다. 역추적하면 경로를 복원합니다.
    # 거리만 저장하면 경로를 알 수 없으므로, 어떤 정점을 거쳐 왔는지도 함께 남깁니다.
    # 시작점과 도달할 수 없는 정점에는 이전 정점이 없어 None으로 둡니다.
    previous = [None] * count
    # heapdict: weights[vertex_to] = [시작점부터의 누적 거리, vertex_from]
    # 현재 후보 수 k에 대해 key 조회는 평균 O(1), 등록·갱신·최소 추출은 O(log k)입니다.
    # 같은 key에 새 value를 대입하면 해당 후보를 교체하고 힙의 위치도 조정합니다.
    # weights[vertex][0]을 직접 수정하면 이 조정이 일어나지 않으므로 피해야 합니다.
    weights = heapdict()
    weights[start] = [0, start]
    vis.add_candidate(start, 0, start, weights, starting=True)

    while weights:
        if vis.stopped():
            return [], float("inf")  # 중단한 결과를 도달 불가로 출력하지 않도록 실행부에서 구분합니다.
        # popitem()은 최소 value를 가진 (key, value)를 반환하면서 후보를 제거합니다.
        # 일반 dict.popitem()의 마지막 등록 항목 추출과는 의미가 다릅니다.
        vertex, (cost, origin) = weights.popitem()
        completed.add(vertex)
        if vertex != origin:
            previous[vertex] = origin
        vis.take_candidate(vertex, cost, origin, weights)

        # 목적지가 후보에 처음 등록되는 순간에는 더 저렴한 다른 경로가 남아 있을 수 있습니다.
        # 음수가 아닌 가중치에서 최소 누적 비용으로 꺼낸 이 시점에만 종료합니다.
        if vertex == goal:
            path = []
            current = goal
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
            return path, cost

        vis.show_neighbors(vertex, graph[vertex])
        # graph[vertex]의 key는 이웃 정점, value는 두 정점을 잇는 간선의 가중치입니다.
        # items()로 두 값을 함께 받아 현재 정점을 경유하는 경로의 도착점을 검사합니다.
        for neighbor, edge_cost in graph[vertex].items():
            if vis.stopped():
                return [], float("inf")
            vis.inspect_edge(vertex, neighbor, edge_cost)
            # 이미 최단 거리가 확정된 정점은 후보로 다시 등록하지 않습니다.
            if neighbor in completed:
                vis.ignore_inland(vertex, neighbor)
                continue
            # 현재 정점까지의 최단 거리에 다음 간선의 가중치를 더합니다.
            candidate_cost = cost + edge_cost
            # 결과로 보면 후보를 바꾸지 않거나, 새 비용과 출발점을 대입하거나 둘뿐입니다.
            # 새 후보 등록과 기존 후보 갱신은 같은 대입으로 처리할 수 있습니다.
            old_candidate = weights.get(neighbor)
            if old_candidate is None or candidate_cost < old_candidate[0]:
                # 새 리스트를 대입해야 heapdict가 새 비용에 맞춰 힙 위치도 갱신합니다.
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
    # 목적지 종료와 달리 후보 소진은 시작점에서 목적지까지의 경로가 없다는 뜻입니다.
    return [], float("inf")


if __name__ == "__main__":
    vis = va.visualizer("dijkstra")
    while va.running():
        data = va.next_data(__file__)
        start, goal = data.start, data.goal
        vis.setup(data, start)
        path, cost = astar(len(data.vertices), data.edges, start, goal)
        if not vis.stopped():
            print("시작점:", start, "목적지:", goal)
            print("최단 경로:", " -> ".join(map(str, path)) if path else "경로 없음")
            print("실제 비용:", cost)
            # 목적지에서 종료했으므로 아직 꺼내지 않은 정점을 도달 불가로 표시하지 않습니다.
            vis.msg_phase("목적지 탐색: 결과")
            vis.msg_action(f"목적지 #{goal}까지의 최단 비용: {cost}")
            vis.msg_detail("목적지를 발견한 때가 아니라 후보에서 꺼낸 때 종료한다.")
        # H: 설명 숨김, L: 배치 전환, 빈 곳 드래그: 이동, 휠: 확대/축소.
        # R: 재실행, D: 다음 데이터, Esc: 종료.
        vis.wait()
