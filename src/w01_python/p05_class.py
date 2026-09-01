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
print()


print("-- add attributes at runtime --")

# Python에서는 객체를 만든 뒤에도 속성을 붙일 수 있습니다.
kim.name = "Kim"
kim.score = 91

lee.name = "Lee"
lee.score = 84

print(kim.name, kim.score)
print(lee.name, lee.score)

# 하지만 이런 방식은 모든 객체가 같은 속성을 갖는다는 보장이 약합니다.
# 그래서 다음 단계에서는 생성자로 초기 상태를 보장합니다.
