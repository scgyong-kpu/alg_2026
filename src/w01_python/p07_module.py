# Python 07. Module
#
# 모듈(module)은 이미 만들어진 코드 묶음입니다.
# 모든 것을 직접 구현하지 않고 표준 라이브러리나 외부 패키지를 가져와 사용할 수 있습니다.


import math


print("-- math module --")

# math.sqrt()는 제곱근을 계산합니다.
print("sqrt(16):", math.sqrt(16))

# math.pi처럼 모듈 안에 준비된 상수도 사용할 수 있습니다.
print("pi:", math.pi)
print()


print("-- degree and radian --")

degree = 90
radian = math.radians(degree)

# Python의 삼각함수는 degree가 아니라 radian을 입력으로 받습니다.
print("degree:", degree)
print("radian:", radian)
print("sin(90 degrees):", math.sin(radian))
print("back to degree:", math.degrees(radian))
print()


print("-- rotate point --")


def rotate_point(x, y, degree):
    theta = math.radians(degree)
    rotated_x = x * math.cos(theta) - y * math.sin(theta)
    rotated_y = x * math.sin(theta) + y * math.cos(theta)
    return rotated_x, rotated_y


point = (1, 0)
rotated = rotate_point(point[0], point[1], 90)

print("before:", point)
print("after 90 degree rotation:", rotated)
print()


print("-- pygame window demo is prepared below --")


RUN_PYGAME_DEMO = False


def run_pygame_window():
    # pygame은 표준 라이브러리가 아니라 requirements.txt로 설치하는 외부 패키지입니다.
    # import를 함수 안에 두면, 이 함수를 실행할 때만 pygame이 필요합니다.
    import pygame as pg

    pg.init()
    screen = pg.display.set_mode((640, 480))
    pg.display.set_caption("Python Module Demo")

    demo_points = [(-120, -60), (0, 0), (120, 80)]

    def to_screen(x, y):
        width, height = screen.get_size()
        center_x = width // 2
        center_y = height // 2
        return center_x + x, center_y - y

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((250, 250, 250))

        width, height = screen.get_size()
        center_x = width // 2
        center_y = height // 2

        # 화면 좌표계는 왼쪽 위가 (0, 0)이고, y값은 아래로 갈수록 커집니다.
        # 수학 좌표계처럼 생각하려면 이 차이를 항상 의식해야 합니다.
        pg.draw.line(screen, (180, 180, 180), (0, center_y), (width, center_y), 1)
        pg.draw.line(screen, (180, 180, 180), (center_x, 0), (center_x, height), 1)

        # 수학 좌표의 y는 위로 갈수록 커진다고 생각하지만, 화면 y는 아래로 커집니다.
        # 그래서 to_screen()에서 y를 빼는 방식으로 변환합니다.
        for x, y in demo_points:
            pg.draw.circle(screen, (37, 99, 235), to_screen(x, y), 6)

        # 선은 두 점 사이의 관계를 보여줄 때 사용합니다.
        # 그래프 알고리즘에서는 정점 사이의 간선을 그릴 때 같은 생각을 씁니다.
        for i in range(len(demo_points) - 1):
            start = to_screen(demo_points[i][0], demo_points[i][1])
            end = to_screen(demo_points[i + 1][0], demo_points[i + 1][1])
            pg.draw.line(screen, (217, 119, 6), start, end, 3)

        pg.display.flip()

    pg.quit()


if RUN_PYGAME_DEMO:
    run_pygame_window()
