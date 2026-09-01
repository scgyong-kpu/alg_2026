# Python 02-3. Set
#
# set은 "포함되어 있는가?"가 중요한 값을 모아두는 자료구조입니다.
# 알고리즘에서는 visited, selected, remaining 같은 이름으로 자주 등장합니다.


print("-- remove duplicates --")

numbers = [3, 1, 2, 3, 2, 4, 1]
unique_numbers = set(numbers)

# set은 중복을 허용하지 않습니다.
# 단, list처럼 입력 순서를 보존하는 자료구조로 생각하면 안 됩니다.
print(numbers)
print(unique_numbers)
print()


print("-- add and membership test --")

visited = set()

visited.add("A")
visited.add("B")
visited.add("A")

print("visited:", visited)
print("A in visited:", "A" in visited)
print("C in visited:", "C" in visited)
print()


print("-- sorted set for stable output --")

# set의 핵심은 순서가 아니라 포함 여부입니다.
# 사람이 읽기 좋은 순서로 출력하고 싶으면 sorted()를 사용합니다.
for vertex in sorted(visited):
    print(vertex)
