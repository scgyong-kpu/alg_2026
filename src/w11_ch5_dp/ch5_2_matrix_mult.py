"""왼쪽 행렬의 행과 오른쪽 행렬의 열을 곱해 결과 행렬을 구한다."""

import pyvisalgo as va


def matrix_mult(a, b, vis=None):
    pass


if __name__ == "__main__":
    vis = va.visualizer("matrix_mult")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        matrix_mult(data.a, data.b, vis)
        # Enter: 현재 결과 칸까지 계산. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
