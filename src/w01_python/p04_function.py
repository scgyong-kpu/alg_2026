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
print()


print("-- local and global variables --")

message = "global message"


def show_scope():
    # 함수 안에서 만든 변수는 local variable입니다.
    # 함수 밖에 같은 이름이 있어도 별개의 이름으로 동작합니다.
    message = "local message"
    print("inside function:", message)


show_scope()
print("outside function:", message)
print()


print("-- positional and keyword arguments --")


def describe_student(name, score, passed=True):
    print("name:", name, "score:", score, "passed:", passed)


# positional argument는 순서대로 parameter에 들어갑니다.
describe_student("Park", 77)

# keyword argument는 이름으로 값을 전달합니다.
# 호출부만 읽어도 어떤 의미의 값인지 더 잘 보입니다.
describe_student(name="Choi", score=95, passed=True)
describe_student(score=62, name="Jung", passed=False)
