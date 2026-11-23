"""MST를 왕복한 뒤 중복 방문을 제거하여 TSP 근사 순회를 만든다."""

import pyvisalgo as va


def build_distances(positions, edges=None):
    """입력 간선은 원래 가중치로, 없는 간선은 좌표 기반 추정값으로 채운다."""
    pass


def prim(distances, start=0, edges=None):
    """(MST 간선 목록, 비용 합)을 반환한다."""
    pass


def build_tree(count, mst):
    """MST 간선 목록을 양방향 인접 리스트로 바꾼다."""
    pass


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
    pass


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
