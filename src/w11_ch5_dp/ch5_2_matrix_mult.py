"""왼쪽 행렬의 행과 오른쪽 행렬의 열을 곱해 결과 행렬을 구한다."""

import pyvisalgo as va


def matrix_mult(a, b, vis=None):
    if not a or not b or not b[0]:
        raise ValueError("비어 있지 않은 두 행렬이 필요합니다.")
    rows, common, cols = len(a), len(b), len(b[0])
    if any(len(row) != cols for row in b):
        raise ValueError("오른쪽 행렬의 모든 행은 길이가 같아야 합니다.")
    if any(len(row) != common for row in a):
        raise ValueError("왼쪽 행렬의 열 수와 오른쪽 행렬의 행 수가 같아야 합니다.")

    result = [[0] * cols for _ in range(rows)]
    if vis:
        vis.start(a, b, result)

    for i in range(rows):
        for j in range(cols):
            for k in range(common):
                if vis and vis.stopped():
                    return None
                result[i][j] += a[i][k] * b[k][j]
                if vis:
                    vis.accumulate(i, j, k)
    if vis and vis.stopped():
        return None
    return result


if __name__ == "__main__":
    vis = va.visualizer("matrix_mult")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        if matrix_mult(data.a, data.b, vis) is not None:
            vis.finish()
        # Enter: 현재 결과 칸까지 계산. D / Shift+D: 다음 / 이전 데이터.
        vis.wait()
