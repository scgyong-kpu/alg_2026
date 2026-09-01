# Python 05. Class
#
# class는 관련 있는 데이터와 동작을 하나의 이름 아래 묶는 방법입니다.
# 시각화 도구, 게임 객체, 그래프의 정점처럼 "상태를 가진 대상"을 표현할 때 유용합니다.


class Student:
    pass


print("-- create objects --")

kim = Student()
lee = Student()

print(kim)
print(lee)
print("same object?", kim is lee)
