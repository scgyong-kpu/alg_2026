# Python 08. List Comprehension
#
# 리스트를 만드는 가장 직접적인 방법은 빈 리스트를 준비한 뒤 반복문에서 append하는 것입니다.
# list comprehension은 이 패턴을 더 짧게 표현하는 Python 문법입니다.


print("-- build list with loop --")

numbers = [1, 2, 3, 4, 5]
squares = []

for number in numbers:
    squares.append(number * number)

print("numbers:", numbers)
print("squares:", squares)
print()


print("-- list comprehension --")

# 위 반복문과 같은 일을 한 줄로 표현할 수 있습니다.
# 왼쪽 number * number가 새 리스트에 들어갈 값이고,
# 오른쪽 for number in numbers가 값을 하나씩 꺼내는 반복입니다.
squares2 = [number * number for number in numbers]

print("squares2:", squares2)
print()


print("-- map --")


def square(number):
    return number * number


# map은 numbers의 각 원소에 square 함수를 적용합니다.
mapped_squares = map(square, numbers)
print("mapped_squares:", mapped_squares)
print()


print("-- convert map to list --")

# map 객체는 필요할 때 값을 하나씩 꺼내는 iterator입니다.
# 전체 결과를 눈으로 보거나 여러 번 다루려면 list로 변환합니다.
mapped_squares = map(square, numbers)
print("list(mapped_squares):", list(mapped_squares))
