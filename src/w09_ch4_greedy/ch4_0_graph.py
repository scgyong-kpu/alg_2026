"""MST 전에 그래프의 세 가지 표현을 비교하는 실행 예제."""

import pyvisalgo as va


def adjacency_matrix(count, edges):
    """matrix[u][v]에 가중치를 저장한다. None은 간선이 없다는 뜻이다."""
    # 각 행은 별도의 리스트여야 합니다. [[None] * count] * count는
    # 같은 행을 공유하므로 한 칸을 수정할 때 다른 행도 바뀌게 됩니다.
    matrix = [[None for _ in range(count)] for _ in range(count)]
    for u, v, weight in edges:
        # 무방향 그래프이므로 반대 방향에도 같은 가중치를 기록합니다.
        matrix[u][v] = weight
        matrix[v][u] = weight
    return matrix


def adjacency_list(count, edges):
    """graph[u]에 정점 u와 연결된 이웃: 가중치를 저장한다."""
    # 고립된 정점도 빈 딕셔너리를 가집니다. 연결된 간선이 없다고
    # 정점 자체가 그래프에서 사라지는 것은 아닙니다.
    graph = {u: {} for u in range(count)}
    for u, v, weight in edges:
        graph[u][v] = weight
        graph[v][u] = weight
    return graph


if __name__ == "__main__":
    vis = va.visualizer("graph_representation")
    while va.running():
        data = va.next_data(__file__)
        edges = data.edges
        matrix = adjacency_matrix(len(data.vertices), edges)
        graph = adjacency_list(len(data.vertices), edges)
        print("Edge List:", edges)
        print("Adjacency Matrix:")
        for row in matrix:
            print(row)
        print("Adjacency List:")
        for u, neighbors in graph.items():
            print(u, neighbors)
        # vertices와 edges가 그래프 데이터입니다. positions는 그림의 배치일 뿐,
        # 간선 가중치나 알고리즘의 답을 결정하지 않습니다.
        vis.setup(data)
        for representation in ("edge_list", "adj_matrix", "adj_list"):
            if vis.stopped():
                break
            vis.set_representation(representation)
            for u, v, weight in data.edges:
                if vis.stopped():
                    break
                vis.show_edge(u, v)
            if representation != "edge_list":
                for u in range(len(data.vertices)):
                    if vis.stopped():
                        break
                    vis.show_vertex(u)
            # Enter는 현재 표현의 설명을 마치고 다음 표현으로 진행합니다.
            vis.section_end()
        # Tab: 세 표현 전환, L: 지정/원형/섞은 배치, H: 설명 숨김.
        # 정점 드래그는 배치 변경, 빈 곳 드래그는 화면 이동, 휠은 확대/축소입니다.
        # 오른쪽 패널 위에서는 휠로 행을 이동합니다. R: 재실행, D: 다음 데이터.
        if not vis.stopped():
            vis.active = None
            vis.selected_vertex = None
            vis.msg_action("배치만 바꾸어도 같은 그래프다.")
            vis.msg_detail("정점 번호, 연결 관계, 가중치는 그대로 유지된다.")
        vis.wait()
