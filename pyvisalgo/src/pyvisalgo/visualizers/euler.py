from pyvisalgo.core import colors
from pyvisalgo.visualizers.graph import GraphVisualizer


class EulerCircuitVisualizer(GraphVisualizer):
    def __init__(self, title="Euler Circuit", **kwargs):
        super().__init__(title, **kwargs)
        self.start = 0
        self.current = None
        self.path = []
        self.used_edges = 0
        self.total_edges = 0
        self.dfs_stack = []
        self.dfs_edges = []
        self.test_edge = None

    def setup(self, data):
        super().setup(data)
        self.start = getattr(data, "start", 0)
        self.current = None
        self.path = []
        self.used_edges = 0
        self.total_edges = len(self.edges)
        self.dfs_stack = []
        self.dfs_edges = []
        self.test_edge = None
        self.msg_phase("오일러 서킷")
        self.msg_action(f"시작 정점 #{self.start}에서 출발한다.")
        self.msg_detail("모든 간선을 정확히 한 번씩 지나 다시 시작점으로 돌아온다.")
        self._update_path()
        self._update_stats()
        self.wait(1000)

    def mark_vertex(self, vertex):
        if self.current is not None:
            self.set_vertex_state(self.current, None)
        self.current = vertex
        self.set_vertex_state(vertex, "current")
        self.msg_action(f"현재 정점은 #{vertex}이다.")
        self.msg_detail("이 정점에서 다음에 사용할 간선을 고른다.")
        self._update_stats()
        self.wait(900)

    def only_edge(self, u, v):
        self._clear_test_edge()
        self.test_edge = self._edge_key(u, v)
        self.set_edge_state(u, v, "candidate")
        self.set_edge_label(u, v, "OK", colors.GREEN)
        self.set_vertex_state(v, "candidate")
        self.msg_action(f"#{u}에서 갈 수 있는 곳은 #{v}뿐이다.")
        self.msg_detail("선택지가 하나뿐이므로 이 간선을 사용한다.")
        self._update_stats()
        self.wait(1300)

    def start_test(self, u, v):
        self._clear_dfs_edges()
        self._clear_test_edge()
        self.test_edge = self._edge_key(u, v)
        self.set_edge_state(u, v, "candidate")
        self.set_edge_label(u, v, "?", colors.YELLOW)
        self.set_vertex_state(v, "candidate")
        self.msg_action(f"#{u}-#{v} 간선을 지금 사용해도 되는지 확인한다.")
        self.msg_detail("이 간선을 지운 뒤에도 두 정점이 연결되는지 살펴본다.")
        self._update_stats()
        self.wait(1200)

    def hide_test_edge(self, u, v):
        self.set_edge_state(u, v, "removed")
        self.msg_action(f"#{u}-#{v} 간선을 잠시 지운다.")
        self.msg_detail(f"DFS로 #{u}에서 #{v}까지 다른 길이 있는지 찾는다.")
        self._update_stats()
        self.wait(900)

    def finish_test(self, u, v, connected):
        self._clear_dfs_edges()
        self.set_edge_state(u, v, "candidate" if connected else "blocked")
        self.set_edge_label(u, v, "OK" if connected else "X", colors.GREEN if connected else colors.RED)
        self.set_vertex_state(v, "candidate" if connected else None)
        if connected:
            self.msg_action(f"#{u}-#{v} 간선을 사용해도 된다.")
            self.msg_detail(f"간선을 지워도 #{u}에서 #{v}까지 다른 길로 갈 수 있었다.")
        else:
            self.msg_action(f"#{u}-#{v} 간선은 나중에 사용한다.")
            self.msg_detail(f"#{u}에서 #{v}까지 다른 길이 없으므로 지금은 사용할 수 없다.")
        self._update_stats()
        self.wait(1300)

    def try_edge(self, u, v):
        self.start_test(u, v)
        self.hide_test_edge(u, v)

    def restore_edge(self, u, v, connected):
        self.finish_test(u, v, connected)

    def use_edge(self, u, v, path):
        self._clear_test_edge()
        self.set_edge_state(u, v, "used")
        self.set_vertex_state(u, "finished")
        self.set_vertex_state(v, "current")
        self.current = v
        self.path = list(path)
        self.used_edges += 1
        self.msg_action(f"#{u}-#{v} 간선을 사용한다.")
        self.msg_detail("사용한 간선은 다시 사용하지 않는다.")
        self._update_path()
        self._update_stats()
        self.wait(1000)

    def dfs_enter(self, vertex):
        self.dfs_stack.append(vertex)
        self.set_vertex_state(vertex, "visited")
        if len(self.dfs_stack) >= 2:
            u, v = self.dfs_stack[-2], self.dfs_stack[-1]
            self.dfs_edges.append(self._edge_key(u, v))
            self.set_edge_state(u, v, "dfs")
        self.msg_action(f"DFS로 #{vertex}에 도착했다.")
        self.msg_detail("후보 간선을 지운 상태에서도 목표 정점까지 갈 수 있는지 확인한다.")
        self.wait(550)

    def dfs_leave(self, vertex):
        if self.dfs_stack and self.dfs_stack[-1] == vertex:
            self.dfs_stack.pop()
        self.set_vertex_state(vertex, None)
        self.wait(250)

    def finish(self, path):
        self.path = list(path)
        self.current = None
        self.msg_phase("완료")
        self.msg_action("오일러 서킷을 완성했다.")
        self.msg_detail(self._path_text(path))
        self._update_path()
        self._update_stats()
        self.wait(1400)

    def impossible(self):
        self.msg_phase("불가능")
        self.msg_action("오일러 서킷을 만들 수 없다.")
        self.msg_detail("아직 사용하지 않은 간선이 남아 있지만 현재 경로를 더 이어 갈 수 없다.")
        self._update_path()
        self._update_stats()
        self.wait(1400)

    def draw_content(self):
        super().draw_content()
        self.right_text("간선을 하나씩 선택하되, 남은 그래프가 끊어지는 선택은 미룬다.", 1576, 28, 22, colors.TEXT_MUTED)

    def _path_text(self, path):
        return " -> ".join(f"#{vertex}" for vertex in path)

    def _update_stats(self):
        self.msg_stats(f"간선 {self.used_edges}/{self.total_edges}")

    def _update_path(self):
        if self.path:
            self.msg_path("경로: " + self._path_text(self.path))
        else:
            self.msg_path(f"경로: #{self.start}")

    def _clear_dfs_edges(self):
        for key in self.dfs_edges:
            if self.edge_states.get(key) == "dfs":
                self.edge_states.pop(key)
        self.dfs_edges = []

    def _clear_test_edge(self):
        if self.test_edge is None:
            return
        self.edge_labels.pop(self.test_edge, None)
        if self.edge_states.get(self.test_edge) in ("candidate", "blocked"):
            self.edge_states.pop(self.test_edge)
        self.test_edge = None
