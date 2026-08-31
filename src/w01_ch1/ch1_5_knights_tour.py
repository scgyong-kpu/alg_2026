import pyvisalgo as va


vis = va.visualizer("knights_tour")

OFFSETS = [
    (1, -2), (2, -1), (2, 1), (1, 2),
    (-1, 2), (-2, 1), (-2, -1), (-1, -2),
]


def can_move(board, x, y):
    size = len(board)
    return 0 <= x < size and 0 <= y < size and board[y][x] == 0


def backtrack_tour(size, start):
    board = [[0 for _ in range(size)] for _ in range(size)]
    attempts = 0

    def move(x, y, step):
        nonlocal attempts
        if vis.wants_answer():
            vis.show_answer()
            return "answer"
        if vis.stopped():
            return None

        board[y][x] = step
        vis.visit(x, y, step, attempts)
        if step == size * size:
            return True

        for direction, (dx, dy) in enumerate(OFFSETS):
            if vis.wants_answer():
                vis.show_answer()
                return "answer"
            if vis.stopped():
                return None
            attempts += 1
            vis.try_dir(x, y, direction, attempts)
            nx, ny = x + dx, y + dy
            if not can_move(board, nx, ny):
                continue

            result = move(nx, ny, step + 1)
            if result is None or result:
                return result

        board[y][x] = 0
        vis.step_back(x, y, step, attempts)
        return False

    result = move(start[0], start[1], 1)
    if result == "answer":
        pass
    elif result is None:
        vis.stopped_by_user()
    elif result:
        vis.finish()
    else:
        vis.fail()
    return result


def count_next_moves(board, x, y):
    count = 0
    for dx, dy in OFFSETS:
        if can_move(board, x + dx, y + dy):
            count += 1
    return count


def warnsdorff_tour(size, start):
    board = [[0 for _ in range(size)] for _ in range(size)]
    x, y = start
    attempts = 0

    for step in range(1, size * size + 1):
        if vis.wants_answer():
            vis.show_answer()
            return "answer"
        if vis.stopped():
            vis.stopped_by_user()
            return None

        board[y][x] = step
        vis.visit(x, y, step, attempts)
        if vis.wants_answer():
            vis.show_answer()
            return "answer"
        if step == size * size:
            vis.finish()
            return True

        candidates = []
        for direction, (dx, dy) in enumerate(OFFSETS):
            nx, ny = x + dx, y + dy
            attempts += 1
            if can_move(board, nx, ny):
                candidates.append((direction, nx, ny, count_next_moves(board, nx, ny)))

        if not candidates:
            vis.show_candidates(x, y, candidates, None, attempts)
            vis.fail()
            return False

        selected = min(candidates, key=lambda candidate: candidate[3])
        vis.show_candidates(x, y, candidates, None, attempts)
        if vis.wants_answer():
            vis.show_answer()
            return "answer"
        if vis.stopped():
            vis.stopped_by_user()
            return None
        vis.choose_candidate(x, y, candidates, selected, attempts)
        x, y = selected[1], selected[2]

    return False


while va.running():
    data = va.Data(size=5, start=[0, 0], method="backtrack", file=__file__)
    start = tuple(data.start)

    vis.setup(data)
    print(f"나이트 투어: {data.method}, {data.size}x{data.size}, 시작={start}")
    if data.method == "backtrack":
        result = backtrack_tour(data.size, start)
    else:
        result = warnsdorff_tour(data.size, start)

    if result is True:
        print("완료")
    elif result is False:
        print("실패")
    elif result == "answer":
        print("준비된 해답 표시")
    else:
        print("중단")
    vis.wait()
