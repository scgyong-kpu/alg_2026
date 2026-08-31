import pyvisalgo as va


vis = va.visualizer("euler")


def build_adj_list(vertex_count, edges):
    adj_list = [[] for _ in range(vertex_count)]
    for u, v in edges:
        adj_list[u].append(v)
        adj_list[v].append(u)
    return adj_list


def remove_edge(adj_list, u, v):
    adj_list[u].remove(v)
    adj_list[v].remove(u)


def add_edge(adj_list, u, v):
    adj_list[u].append(v)
    adj_list[v].append(u)


def is_reachable(adj_list, current, target, visited=None):
    if visited is None:
        visited = set()

    visited.add(current)
    vis.dfs_enter(current)
    if current == target:
        vis.dfs_leave(current)
        return True

    for next_vertex in adj_list[current]:
        if next_vertex not in visited and is_reachable(adj_list, next_vertex, target, visited):
            vis.dfs_leave(current)
            return True

    vis.dfs_leave(current)
    return False


def can_use_edge(adj_list, current, next_vertex):
    if len(adj_list[current]) == 1:
        vis.only_edge(current, next_vertex)
        return True

    vis.start_test(current, next_vertex)
    remove_edge(adj_list, current, next_vertex)
    vis.hide_test_edge(current, next_vertex)
    connected = is_reachable(adj_list, current, next_vertex)
    add_edge(adj_list, current, next_vertex)
    vis.finish_test(current, next_vertex, connected)
    return connected


def find_euler_circuit(vertex_count, edges, start):
    adj_list = build_adj_list(vertex_count, edges)
    current = start
    circuit = [current]

    while any(adj_list):
        vis.mark_vertex(current)
        if len(adj_list[current]) == 0:
            vis.impossible()
            return None

        selected = None
        for next_vertex in adj_list[current][:]:
            if can_use_edge(adj_list, current, next_vertex):
                selected = next_vertex
                break

        if selected is None:
            vis.impossible()
            return None

        remove_edge(adj_list, current, selected)
        current = selected
        circuit.append(current)
        vis.use_edge(circuit[-2], circuit[-1], circuit)

    vis.finish(circuit)
    return circuit


def vertex_name(data, index):
    vertex = data.vertices[index]
    if isinstance(vertex, dict):
        return vertex.get("name", index)
    return vertex


while va.running():
    data = va.Data(
        vertices=["A", "B", "C", "D"],
        edges=[[0, 1], [1, 2], [2, 3], [3, 0]],
        start=0,
        file=__file__,
    )

    vis.setup(data)
    print("오일러 서킷을 찾을 그래프:", getattr(data, "name", ""))
    circuit = find_euler_circuit(len(data.vertices), data.edges, data.start)
    if circuit is not None:
        print("서킷:", " -> ".join(str(vertex_name(data, vertex)) for vertex in circuit))
    else:
        print("오일러 서킷을 만들 수 없다.")
    vis.wait()
