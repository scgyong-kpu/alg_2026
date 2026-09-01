# Python 02-2. Dictionary Usage
#
# dictionary는 "어떤 값이 몇 번 나왔는가"를 기록하는 빈도표로 자주 사용합니다.
# 알고리즘 문제에서 문자 수, 단어 수, 방문 횟수, 간선 개수 등을 셀 때 같은 패턴을 씁니다.


words = [
    "apple",
    "algorithm",
    "banana",
    "binary",
    "cat",
    "code",
    "data",
]

counts = {}

for word in words:
    first_char = word[0]

    # first_char가 처음 나온 글자라면 먼저 0으로 초기화합니다.
    if first_char not in counts:
        counts[first_char] = 0

    # 이미 있던 글자든 방금 만든 글자든, 단어 하나를 발견했으므로 1 증가시킵니다.
    counts[first_char] += 1

print("-- count words by first character --")
print(counts)
print()


print("-- iteration order --")

# Python의 dictionary는 값을 넣은 순서를 기억합니다.
# 하지만 알고리즘 문제에서 출력 순서가 정해져 있다면, 그 요구에 맞게 정렬해야 합니다.
for first_char in counts:
    print(first_char, counts[first_char])
print()


print("-- sorted keys --")

# sorted()는 정렬된 새 리스트를 만들어 줍니다.
# dictionary 자체를 바꾸는 것이 아니라, 순회할 key 순서만 정렬해서 사용합니다.
for first_char in sorted(counts.keys()):
    print(first_char, counts[first_char])
print()


print("-- defaultdict --")

from collections import defaultdict

simple_counts = defaultdict(int)

for word in words:
    first_char = word[0]

    # defaultdict(int)는 없는 key를 처음 만났을 때 int()의 결과인 0을 준비합니다.
    # 그래서 if first_char not in counts 같은 초기화 코드를 줄일 수 있습니다.
    simple_counts[first_char] += 1

print(dict(simple_counts))
print()


print("-- items --")

# items()는 key와 value를 한 쌍으로 꺼냅니다.
for first_char, count in counts.items():
    print(first_char, "=>", count)
print()


print("-- nested dictionary as graph --")

# 그래프의 인접 리스트는 dictionary 안에 dictionary가 들어 있는 형태로 표현할 수 있습니다.
# graph[u][v]는 u에서 v로 가는 간선의 가중치라고 읽습니다.
graph = {
    "A": {"B": 3, "C": 5},
    "B": {"C": 1},
    "C": {"A": 2},
}

for u, adjs in graph.items():
    for v, weight in adjs.items():
        print(u, "->", v, "weight:", weight)
