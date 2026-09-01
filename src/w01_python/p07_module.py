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

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((250, 250, 250))
        pg.display.flip()

    pg.quit()


if RUN_PYGAME_DEMO:
    run_pygame_window()
