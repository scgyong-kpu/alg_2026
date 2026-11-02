"""Kruskal 알고리즘으로 최소 신장 트리를 만드는 실행 예제."""

import pyvisalgo as va


def getRoot(vertex):
    """부모를 따라 루트를 찾고, 돌아오면서 대표로 바로 연결한다."""
    vis.root_enter(vertex, roots)
    # 자기 자신을 가리키면 더 따라갈 부모가 없습니다.
    # 자기 자신을 반환하는 것이 재귀 호출의 종료 조건입니다.
    if roots[vertex] == vertex:
        vis.root_return(vertex, vertex, roots, is_root=True)
        return vertex
    # 루트가 아니면 부모 정점의 루트를 다시 묻습니다.
    # 예를 들어 3 -> 2 -> 1 -> 0이면 getRoot(0)에서 0을 반환하고,
    # 기다리던 getRoot(1), getRoot(2), getRoot(3)도 차례로 0을 반환합니다.
    root = getRoot(roots[vertex])
    # 이전 버전은 root를 반환하기만 해서 부모 사슬이 그대로 남았습니다.
    # 이제 재귀 호출에서 돌아올 때 최종 대표를 roots[vertex]에도 기록합니다.
    # 여기서 root는 바로 위 부모가 아니라, 재귀 탐색으로 찾은 최종 대표입니다.
    #
    # 예: roots = [0, 0, 1, 2]에서 getRoot(3)을 호출하면
    #     호출: 3 -> 2 -> 1 -> 0 (각 호출은 안쪽 호출의 결과를 기다립니다.)
    #     반환: 0을 받은 getRoot(1)이 roots[1] = 0을 기록합니다. (이미 0)
    #           그다음 getRoot(2)가 roots[2] = 0을 기록합니다. (1 -> 0)
    #           마지막 getRoot(3)이 roots[3] = 0을 기록합니다. (2 -> 0)
    #     결과: roots = [0, 0, 0, 0]
    # 따라서 다음 getRoot(3)은 3 -> 0으로 바로 가서 호출 단계가 줄어듭니다.
    # 이번 탐색에서는 기존 경로를 따라가야 하지만, 이후 탐색에 쓸 shortcut을 남깁니다.
    #
    # 같은 집합 안에서 최종 대표를 직접 가리키게 할 뿐 집합을 합치는 것은 아닙니다.
    # 대표와 MST 결과는 바뀌지 않으며, 실제 선택 간선 목록인 mst도 수정하지 않습니다.
    # 이렇게 지나온 경로의 부모 연결을 짧게 만드는 것이 경로 압축입니다.
    roots[vertex] = root
    vis.root_return(vertex, root, roots)
    return root


def union(root_u, root_v):
    """서로 다른 두 집합의 대표를 받아 하나의 집합으로 합친다."""
    # 일반 정점이 아니라 getRoot가 반환한 대표끼리 연결해야 합니다.
    # 대표가 아닌 정점의 부모만 바꾸면 기존 집합의 일부만 옮겨질 수 있습니다.
    # 작은 번호를 대표로 남기는 것은 집합을 관리하는 규칙일 뿐,
    # 간선의 가중치가 작거나 MST의 비용이 더 작다는 뜻은 아닙니다.
    if root_u < root_v:
        roots[root_v] = root_u
    else:
        roots[root_u] = root_v
    vis.union_roots(root_u, root_v, roots)


def kruskal(count, edges):
    """정점 수와 간선 목록을 받아 (선택한 간선 목록, 비용 합)을 반환한다."""
    global roots
    # 정점 번호는 0부터 count - 1까지입니다.
    # 각 간선 (u, v, weight)는 두 정점과 연결 비용을 나타냅니다.
    # 무방향 간선이므로 (v, u, weight)를 다시 저장하지 않습니다.
    # 아직 선택한 간선이 없으므로 빈 목록과 비용 0에서 시작합니다.
    # mst에는 선택한 간선을, total_cost에는 그 가중치 합을 저장합니다.
    mst = []
    total_cost = 0

    # 처음에는 간선을 선택하지 않았으므로 각 정점이 독립된 집합입니다.
    # 자기 자신을 가리키는 정점이 집합의 대표(루트)입니다.
    # 이후 getRoot와 union에서 함께 사용할 수 있도록 전역 배열로 준비합니다.
    # 이 부모 관계는 집합 관리용이며, 실제 선택 간선 목록인 mst와는 다릅니다.
    roots = [i for i in range(count)]
    vis.start(roots)

    # 간선의 세 번째 값인 weight를 기준으로 오름차순 정렬합니다.
    # sorted는 새 목록을 만들므로 원본 데이터의 간선 순서는 바뀌지 않습니다.
    # 같은 가중치를 가진 간선끼리는 원래 입력 순서가 유지됩니다.
    edges = sorted(edges, key=lambda edge: edge[2])
    vis.sort_edges(edges)

    # 가중치가 작은 순서대로 모든 후보를 검사합니다.
    # for문에서 각 간선의 두 끝점과 가중치를 나누어 받습니다.
    # 정점 n개의 사이클 없는 그래프는 간선이 최대 n-1개입니다.
    # 무조건 선택하는 대신 두 대표를 비교해 같은 집합의 간선은 제외합니다.
    # 제외한 후보도 검사 횟수에는 포함되므로, 앞의 count개만 보면 부족할 수 있습니다.
    # 선택한 간선이 count-1개가 되면 모든 정점이 연결되므로 검사를 끝냅니다.
    for u, v, weight in edges:
        if vis.stopped():
            break
        vis.begin_edge(u, v)
        # 현재 후보의 양 끝점이 각각 어느 집합에 속하는지 대표를 구합니다.
        # 이전에 선택한 간선에 따른 집합 합치기가 이 탐색 결과에 반영됩니다.
        root_u = getRoot(u)
        root_v = getRoot(v)
        vis.check_roots(u, v, root_u, root_v, roots)
        # 두 대표가 같으면 선택한 간선들로 이미 연결된 두 정점입니다.
        # 여기에 간선을 더하면 사이클이 생기므로 목록과 비용에 반영하지 않습니다.
        if root_u == root_v:
            vis.reject_edge(u, v, weight)
            continue
        # 선택한 간선은 두 끝점과 가중치를 함께 기록합니다.
        # 서로 다른 집합을 잇는 간선만 선택하고 비용을 누적합니다.
        mst.append((u, v, weight))
        # 선택을 확정한 간선의 가중치만 총비용에 더합니다.
        total_cost += weight
        vis.select_edge(u, v, weight, total_cost)
        # 간선을 확정한 뒤 두 집합을 합쳐 다음 간선의 사이클 검사에 반영합니다.
        # 이 호출이 없으면 이미 연결한 두 정점도 다른 집합으로 잘못 판단합니다.
        union(root_u, root_v)
        # 사이클 없이 정점 n개를 연결하는 트리의 간선은 n-1개입니다.
        # 검사 횟수가 아니라 실제 선택한 간선 수로 완료 여부를 판단합니다.
        # 이후의 후보는 더 검사하지 않아도 됩니다.
        if len(mst) == count - 1:
            break

    return mst, total_cost


if __name__ == "__main__":
    vis = va.visualizer("kruskal")
    while va.running():
        data = va.next_data(__file__)
        count = len(data.vertices)
        print("정점 수:", count)
        print("간선 목록:", data.edges)
        # positions는 그림을 배치하는 좌표일 뿐입니다.
        # Kruskal은 선의 화면상 길이가 아니라 weight를 비교합니다.
        vis.setup(data)
        mst, total_cost = kruskal(count, data.edges)
        if not vis.stopped():
            print("선택한 간선:", mst)
            # 사이클 없이 n-1개를 선택했다면 모든 정점을 연결한 MST입니다.
            # 후보가 소진되어도 개수가 부족하면 전체 그래프는 연결되지 않았습니다.
            if len(mst) == count - 1:
                print("최소 신장 트리 비용:", total_cost)
            else:
                print("전체 최소 신장 트리 없음: 그래프가 연결되어 있지 않습니다.")
                # 각 연결 요소 안에서 구한 MST들의 모음이 최소 신장 숲입니다.
                print("최소 신장 숲 비용:", total_cost)
            vis.finish_mst(count, mst, total_cost)
        # 정점 드래그: 배치 변경, 빈 곳 드래그: 화면 이동, 휠: 확대/축소.
        # H: 설명 숨김, L: 배치 전환, R: 재실행, D: 다음 데이터, Esc: 종료.
        vis.wait()
