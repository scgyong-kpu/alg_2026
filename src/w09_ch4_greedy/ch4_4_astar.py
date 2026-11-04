"""A*: 목적지까지의 최단 경로를 휴리스틱으로 안내하며 찾는다.

Dijkstra는 g(시작점부터의 실제 비용)가 최소인 후보를 고릅니다.
A*는 f = g + h가 최소인 후보를 고릅니다. h는 목적지까지 남은 비용의 추정입니다.
이 파일은 일관적인 휴리스틱을 사용하여 꺼낸 정점을 다시 열지 않는 버전입니다.
목적지를 처음 발견했을 때가 아니라 최소 f 후보로 꺼냈을 때 종료해야 합니다.

화면에 그리는 위치 positions와 거리 계산용 좌표 coordinates는 구별합니다.
배치를 바꾸거나 정점을 드래그해도 입력 가중치와 휴리스틱은 변하지 않습니다.
실습 데이터의 간선 비용은 좌표 사이의 직선거리 이상인 정수로 준비했습니다.
따라서 목적지까지 직선거리를 내림한 정수 h는 실제 남은 비용을 넘지 않습니다.
직선거리의 삼각부등식과 정수 가중치에 의해 h(u) <= w(u,v) + h(v)도 만족합니다.
임의의 가중 그래프에서 화면상의 직선거리를 그대로 h로 쓰면 안 됩니다.
"""

import math

from heapdict import heapdict

import pyvisalgo as va


def straight_line_heuristics(coordinates, goal):
    """고정된 계산용 좌표에서 목적지까지의 직선거리를 내린 정수 배열을 만든다."""
    return [math.floor(math.dist(point, coordinates[goal])) for point in coordinates]


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


def validate_heuristics(graph, heuristics, goal):
    """닫힌 정점을 다시 열지 않는 구현의 전제인 일관성을 검사한다."""
    if len(heuristics) != len(graph):
        raise ValueError("휴리스틱은 정점마다 하나씩 필요합니다.")
    if any(not math.isfinite(h) or h < 0 for h in heuristics) or heuristics[goal] != 0:
        raise ValueError("h는 유한한 음수가 아닌 수이며 h(goal)은 0이어야 합니다.")
    for u, neighbors in graph.items():
        for v, weight in neighbors.items():
            if heuristics[u] > weight + heuristics[v]:
                raise ValueError("일관성 조건 h(u) <= w(u,v) + h(v)를 만족해야 합니다.")


def astar(count, edges, start, goal, heuristics):
    """목적지까지의 (경로, 실제 비용)을 반환한다. 경로가 없으면 ([], inf)이다."""
    if not (0 <= start < count and 0 <= goal < count):
        raise ValueError("시작점과 목적지가 정점 범위 안에 있어야 합니다.")
    # 정점 하나의 최단 거리를 확정할 때마다 그 정점에 연결된 이웃들을 검사합니다.
    # 전체 간선 목록 대신 graph[vertex].items()로 이웃과 가중치를 얻도록 준비합니다.
    graph = build_graph(count, edges)
    validate_heuristics(graph, heuristics, goal)
    # completed는 시작점부터의 최단 거리를 확정한 정점들의 집합입니다.
    # 같은 정점을 다시 확정하거나 후보로 추가하지 않도록 소속 여부를 검사합니다.
    completed = set()
    # previous[v]는 최단 경로에서 v 바로 앞의 정점입니다. 역추적하면 경로를 복원합니다.
    # 거리만 저장하면 경로를 알 수 없으므로, 어떤 정점을 거쳐 왔는지도 함께 남깁니다.
    # 시작점과 도달할 수 없는 정점에는 이전 정점이 없어 None으로 둡니다.
    previous = [None] * count
    # key는 도착 정점, value는 [f, g, 이전 정점]입니다.
    # heapdict는 value의 첫 항목 f로 우선 비교합니다. 동률이면 g, 이전 정점 순서입니다.
    # f가 같을 때 어느 정점을 먼저 선택하는지에 따라 탐색 수와 경로가 달라질 수 있습니다.
    # 현재 후보 수 k에 대해 key 조회는 평균 O(1), 등록·갱신·최소 추출은 O(log k)입니다.
    # 같은 key에 새 value를 대입하면 해당 후보를 교체하고 힙의 위치도 조정합니다.
    # weights[vertex][0]을 직접 수정하면 이 조정이 일어나지 않으므로 피해야 합니다.
    weights = heapdict()
    weights[start] = [heuristics[start], 0, start]
    vis.add_candidate(start, 0, start, weights, starting=True)

    while weights:
        if vis.stopped():
            return [], float("inf")  # 중단한 결과를 도달 불가로 출력하지 않도록 실행부에서 구분합니다.
        # popitem()은 최소 value를 가진 (key, value)를 반환하면서 후보를 제거합니다.
        # 일반 dict.popitem()의 마지막 등록 항목 추출과는 의미가 다릅니다.
        vertex, (priority, cost, origin) = weights.popitem()
        completed.add(vertex)
        if vertex != origin:
            previous[vertex] = origin
        vis.take_candidate(vertex, cost, origin, weights)

        # 목적지가 후보에 처음 등록되는 순간에는 더 저렴한 다른 경로가 남아 있을 수 있습니다.
        # 일관적인 h를 사용하여 최소 f로 꺼낸 이 시점에만 종료합니다.
        if vertex == goal:
            path = []
            current = goal
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
            return path, cost  # f가 아니라 실제 누적 비용 g를 반환합니다. 목적지에서는 h=0입니다.

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
            # g에는 실제 간선 비용만 더합니다. h를 경로 비용에 누적하면 안 됩니다.
            candidate_cost = cost + edge_cost
            # 결과로 보면 후보를 바꾸지 않거나, 새 비용과 출발점을 대입하거나 둘뿐입니다.
            # 새 후보 등록과 기존 후보 갱신은 같은 대입으로 처리할 수 있습니다.
            old_candidate = weights.get(neighbor)
            # 같은 정점의 h는 고정이지만, 갱신의 의미는 실제 비용 g의 개선입니다.
            if old_candidate is None or candidate_cost < old_candidate[1]:
                priority = candidate_cost + heuristics[neighbor]
                # 새 리스트를 대입해야 heapdict가 새 f에 맞춰 힙 위치도 갱신합니다.
                weights[neighbor] = [priority, candidate_cost, vertex]
                # 아래 분기는 추가와 갱신을 서로 다른 애니메이션으로 표시하기 위한 것입니다.
                if old_candidate is None:
                    vis.add_candidate(neighbor, candidate_cost, vertex, weights)
                else:
                    vis.update_candidate(neighbor, old_candidate[1], old_candidate[2],
                                         candidate_cost, vertex, weights)
            else:
                # 같거나 더 비싼 연결이면 아무것도 대입하지 않고 기존 후보를 유지합니다.
                vis.keep_candidate(neighbor, old_candidate[1], old_candidate[2], candidate_cost, vertex)
    # 목적지 종료와 달리 후보 소진은 시작점에서 목적지까지의 경로가 없다는 뜻입니다.
    return [], float("inf")


if __name__ == "__main__":
    from data_map import map_to_graph, map_heuristics

    vis = va.visualizer("astar")
    while va.running():
        data = va.next_data(__file__)
        if hasattr(data, "map"):
            # 숫자 맵에서 이동할 수 있는 정점과 간선을 만듭니다.
            data = map_to_graph(data)
            heuristics = map_heuristics(data)
        else:
            heuristics = straight_line_heuristics(data.coordinates, data.goal)
        start, goal = data.start, data.goal
        if not vis.use_heuristic:
            heuristics = [0] * len(data.vertices)  # 같은 목적지에서 끝나는 Dijkstra와 비교합니다.
        vis.setup(data, start, goal, heuristics)
        path, cost = astar(len(data.vertices), data.edges, start, goal, heuristics)
        if not vis.stopped():
            mode = "A*" if vis.use_heuristic else "h=0 (Dijkstra)"
            print(f"{mode}: #{start} {data.vertices[start]} -> #{goal} {data.vertices[goal]}")
            if path:
                print("최단 경로:", " -> ".join(f"#{v} {data.vertices[v]}" for v in path))
                print("실제 비용 g:", cost)
            else:
                print("도달 가능한 경로 없음")
            print("탐색한 정점 수:", len(vis.inland))
            vis.finish_search()
        # A: A*/h=0 비교 전환 후 재실행. 같은 그래프·시작점·목적지를 유지합니다.
        # M: 이미지 전용 / 정점 번호와 g(실제 비용)·h(추정)·f(우선순위) 표시 전환.
        # Space: 일시정지, .: 한 단계, Enter: 다음 동작까지 빠르게, 1-9: 속도.
        # H: 설명 숨김, L: 배치, 정점 드래그: 배치, 빈 곳 드래그: 이동, 휠: 확대/목록 스크롤.
        # 숫자 맵의 movement.diagonal로 대각선 허용 여부를 지정합니다.
        # 기본 비용은 직선 10, 대각선 14이며 corner_cutting=false는 모서리 통과를 막습니다.
        # heuristic은 직선 전용 manhattan, 대각선 허용 octile을 사용합니다.
        # 격자에서는 L과 정점 이동을 사용하지 않고 드래그로 지도 전체를 이동합니다.
        # 하단 탐색 정점에 마우스를 올리면 시작점부터 그 정점까지의 경로를 표시합니다.
        # R: 재실행, D: 다음 데이터, +/-: 글씨 크기, Esc: 종료.
        vis.wait()
