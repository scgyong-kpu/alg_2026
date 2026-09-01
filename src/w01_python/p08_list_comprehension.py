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
