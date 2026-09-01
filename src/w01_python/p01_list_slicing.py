# Python 01-2. List Slicing
#
# slicing은 리스트의 일부 구간을 잘라 새 리스트처럼 사용하는 문법입니다.
# 분할 정복, 문자열 처리, 부분 배열을 다루는 코드에서 자주 만납니다.


letters = ["a", "b", "c", "d", "e", "f"]

print("-- original list --")
print(letters)
print()


print("-- basic slicing --")

# letters[start:end]는 start 위치부터 end 바로 앞까지 가져옵니다.
# end 위치의 원소는 포함하지 않습니다.
print("letters[1:4] =", letters[1:4])

# start를 생략하면 처음부터 가져옵니다.
print("letters[:3] =", letters[:3])

# end를 생략하면 끝까지 가져옵니다.
print("letters[3:] =", letters[3:])
print()


print("-- negative index --")

# 음수 인덱스는 뒤에서부터 셉니다.
# -1은 마지막 원소, -2는 마지막에서 두 번째 원소입니다.
print("letters[-1] =", letters[-1])
print("letters[-3:] =", letters[-3:])
