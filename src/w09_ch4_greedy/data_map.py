"""숫자 맵을 기존 A*가 사용하는 정점·간선 데이터로 변환한다."""

import math

import pyvisalgo as va


def map_to_graph(data):
    """map[row][col]에서 이동 가능한 칸만 정점으로 만든다. 입력은 바꾸지 않는다."""
    tiles = data.map
    if not tiles or not tiles[0] or any(len(row) != len(tiles[0]) for row in tiles):
        raise ValueError("map은 비어 있지 않은 직사각형 배열이어야 합니다.")
    allowed = {0, 1, 2, 3, 4, 11, 12, 13, 14}
    if any(type(tile) is not int or tile not in allowed for row in tiles for tile in row):
        raise ValueError("맵 값은 0, 1~4, 11~14 중 하나여야 합니다.")
    # 1 초원, 2 모래, 3 잔디, 4 나무블록: 이동 가능한 지형이며 비용 자체가 아닙니다.
    # 11 돌멩이, 12 나무, 13 석상, 14 뱀: 통과할 수 없는 장애물입니다.
    # 0(칸 없음)과 11~14(장애물)는 정점이나 간선을 만들지 않습니다.
    cells = [(col, row) for row, line in enumerate(tiles)
             for col, tile in enumerate(line) if 1 <= tile <= 4]
    indexes = {cell: index for index, cell in enumerate(cells)}
    start_cell, goal_cell = tuple(data.start_cell), tuple(data.goal_cell)
    if start_cell not in indexes or goal_cell not in indexes:
        raise ValueError("시작점과 목적지는 이동 가능한 칸이어야 합니다. 좌표는 [열, 행]입니다.")
    movement = getattr(data, "movement", {})
    diagonal = movement.get("diagonal", False)
    corner_cutting = movement.get("corner_cutting", False)
    straight_cost = movement.get("straight_cost", 10)
    diagonal_cost = movement.get("diagonal_cost", 14)
    if type(diagonal) is not bool or type(corner_cutting) is not bool:
        raise ValueError("diagonal과 corner_cutting은 true 또는 false여야 합니다.")
    if (type(straight_cost) not in (int, float) or not math.isfinite(straight_cost) or straight_cost <= 0 or
            type(diagonal_cost) not in (int, float) or not math.isfinite(diagonal_cost) or
            not straight_cost <= diagonal_cost <= 2 * straight_cost):
        raise ValueError("비용은 유한한 양수이며 직선 비용 <= 대각선 비용 <= 직선 비용의 2배여야 합니다.")
    heuristic = getattr(data, "heuristic", "octile" if diagonal else "manhattan")
    if heuristic not in {"manhattan", "octile", "euclidean", "zero"}:
        raise ValueError("지원하지 않는 휴리스틱입니다.")
    if diagonal and heuristic == "manhattan" and diagonal_cost < 2 * straight_cost:
        raise ValueError("저렴한 대각선 이동에서는 맨해튼 거리가 과대평가할 수 있습니다.")
    if diagonal and heuristic == "euclidean" and diagonal_cost < math.sqrt(2) * straight_cost:
        raise ValueError("이 대각선 비용에서는 유클리드 거리가 과대평가할 수 있습니다. octile을 사용하세요.")
    edges = []
    for index, (col, row) in enumerate(cells):
        # 오른쪽·아래쪽 간선만 만들고 build_graph에서 양방향으로 등록합니다.
        # 대각선은 데이터 옵션으로만 추가합니다. 기본은 상하좌우 이동입니다.
        for neighbor in [(col + 1, row), (col, row + 1)]:
            if neighbor in indexes:
                edges.append([index, indexes[neighbor], straight_cost])
        if diagonal:
            for dx in (-1, 1):
                neighbor = (col + dx, row + 1)
                if neighbor not in indexes:
                    continue
                # 양쪽 직교 칸이 모두 열려 있어야 장애물 모서리를 통과하지 않습니다.
                if not corner_cutting and ((col + dx, row) not in indexes or (col, row + 1) not in indexes):
                    continue
                edges.append([index, indexes[neighbor], diagonal_cost])
    coordinates = [[col * straight_cost, -row * straight_cost] for col, row in cells]
    # 데이터 이름과 다음 데이터 안내 등 runner의 메타데이터도 보존합니다.
    result = vars(data).copy()
    result.update(vertices=[f"({col},{row})" for col, row in cells],
                  coordinates=coordinates, positions=coordinates, edges=edges,
                  start=indexes[start_cell], goal=indexes[goal_cell],
                  heuristic=heuristic,
                  movement={"diagonal": diagonal, "straight_cost": straight_cost,
                            "diagonal_cost": diagonal_cost, "corner_cutting": corner_cutting},
                  grid={"rows": ["".join("." if 1 <= t <= 4 else " " if t == 0 else "#" for t in row)
                                 for row in tiles],
                        "tiles": tiles, "cells": cells, "step_cost": straight_cost})
    return va.Data(**result)


def map_heuristics(data):
    """이동 규칙에 맞는 추정값을 반환한다. 장애물을 무시한 비용의 하한이다."""
    goal_x, goal_y = data.grid["cells"][data.goal]
    straight = data.movement["straight_cost"]
    diagonal = data.movement["diagonal_cost"]
    values = []
    for x, y in data.grid["cells"]:
        dx, dy = abs(x - goal_x), abs(y - goal_y)
        if data.heuristic == "zero":
            h = 0
        elif data.heuristic == "manhattan":
            h = straight * (dx + dy)
        elif data.heuristic == "octile":
            # 가로·세로 공통 부분은 대각선으로, 나머지는 직선으로 이동하는 비용입니다.
            h = diagonal * min(dx, dy) + straight * abs(dx - dy)
        else:
            h = math.floor(straight * math.hypot(dx, dy))
        values.append(h)
    return values
