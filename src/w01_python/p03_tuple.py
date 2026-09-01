# Python 03. Tuple
#
# tuple은 여러 값을 하나로 묶는 자료구조입니다.
# 리스트와 비슷하게 순서가 있지만, 만들어진 뒤에는 내부 값을 바꿀 수 없습니다.


print("-- create tuple --")

# 쉼표로 값을 나열하면 tuple이 됩니다.
# 괄호는 생략할 수 있지만, 수업 예제에서는 읽기 쉽게 괄호를 자주 사용합니다.
point = (10, 20)
record = 1, "Kim", 91

print(point)
print(record)
print()


print("-- unpacking --")

# tuple의 각 위치를 변수 이름에 나누어 담을 수 있습니다.
x, y = point
number, name, score = record

print("x:", x)
print("y:", y)
print("name:", name)
print("score:", score)
print()


print("-- tuple is immutable, list is mutable --")

tuple_point = (100, 200)
list_point = [100, 200]

# tuple은 내부 값을 바꿀 수 없습니다.
# tuple_point[1] = 250
try:
    tuple_point[1] = 250
except TypeError as error:
    print("tuple update error:", error)

# list는 내부 값을 바꿀 수 있습니다.
list_point[1] = 250

print("tuple_point:", tuple_point)
print("list_point:", list_point)
