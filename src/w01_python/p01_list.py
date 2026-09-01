# Python 01. List
#
# 리스트(list)는 여러 값을 하나의 이름으로 묶어서 다루는 자료구조입니다.
# 알고리즘 수업에서는 입력 데이터, 중간 결과, 정렬 대상, DP 테이블의 한 줄 등을
# 리스트로 표현하는 일이 많습니다.


# 대괄호 안에 값을 나열하면 리스트가 됩니다.
# 리스트의 각 값은 원소(element)라고 부릅니다.
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# range(10)은 0부터 9까지의 정수 흐름을 나타냅니다.
# 출력해 보면 리스트처럼 모든 값이 펼쳐져 보이지는 않습니다.
indices = range(10)

print("-- list vs range --")
print(numbers)
print(indices)
print()


# 리스트와 range는 for loop에서 비슷하게 사용할 수 있습니다.
# for value in numbers는 numbers 안의 값을 앞에서부터 하나씩 꺼냅니다.
print("-- for loop over list --")
for value in numbers:
    print(value, end=" - ")
print("//")

# range도 반복문에서 값을 하나씩 만들어 줍니다.
# 큰 범위가 필요할 때는 실제 리스트를 미리 만들지 않는 range가 더 가볍습니다.
print("-- for loop over range --")
for value in indices:
    print(value, end=" - ")
print("//")
print()


# print()는 기본적으로 출력 뒤에 줄바꿈을 붙입니다.
# end 값을 지정하면 줄 끝에 무엇을 붙일지 바꿀 수 있습니다.
print("A", end=" ")
print("B", end=" ")
print("C")
print()


# len()은 원소의 개수를 알려줍니다.
# 인덱스가 0부터 시작하기 때문에 마지막 인덱스는 len(numbers) - 1입니다.
print("-- len of list / range --")
print(len(numbers))
print(len(indices))
print("first:", numbers[0])
print("last:", numbers[len(numbers) - 1])
print()


# range를 실제 리스트로 바꾸어 눈으로 확인하고 싶을 때는 list()를 사용합니다.
print("-- range to list --")
print(list(indices))
