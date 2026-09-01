# Python 02-1. Dictionary
#
# dictionary는 key로 value를 찾아가는 자료구조입니다.
# 알고리즘에서는 이름표가 붙은 데이터, 빈도표, 방문 여부, 그래프의 인접 리스트를
# 표현할 때 자주 사용합니다.


scores = {
    "Kim": 91,
    "Lee": 84,
    "Park": 77,
}

print("-- dictionary --")
print(scores)
print()


# 리스트는 숫자 인덱스로 값을 찾지만, dictionary는 key로 값을 찾습니다.
print("-- lookup by key --")
print("Kim:", scores["Kim"])
print("Lee:", scores["Lee"])
print()


# 이미 존재하는 key에 다시 값을 대입하면 value가 바뀝니다.
scores["Park"] = 88
print("-- update value --")
print(scores)
