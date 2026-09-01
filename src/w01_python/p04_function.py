# Python 04. Function
#
# 함수(function)는 반복해서 사용할 계산이나 동작에 이름을 붙이는 방법입니다.
# 알고리즘에서는 "한 단계의 판단"이나 "하나의 계산"을 함수로 분리하면 읽기 쉬워집니다.


def square(x):
    # parameter x는 함수가 일을 하기 위해 받는 입력입니다.
    return x * x


print("-- define and call function --")
print(square(3))
print(square(10))


def print_score(name, score):
    print(name, ":", score)


print_score("Kim", 91)
print_score("Lee", 84)
