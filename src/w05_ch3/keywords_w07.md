# Week 7: Closest Pair (7주차: 최근접 쌍)

## Geometry and Distance (기하와 거리)

- closest pair problem (최근접 쌍 문제): 평면의 점들 중 유클리드 거리가 가장 짧은 두 점을 찾는 문제
- point (점): 평면에서 `(x, y)` 좌표로 나타내는 위치
- coordinate (좌표): 점의 위치를 나타내는 수
- Euclidean distance (유클리드 거리): 두 점 사이의 직선거리. `sqrt(dx * dx + dy * dy)`

- squared distance (거리의 제곱): `dx * dx + dy * dy`. 음이 아닌 거리의 대소 관계를 제곱근 없이 비교할 때 사용할 수 있음

그냥 거리의 제곱만 구하는 경우가 많음. 어차피 비교하면 똑같잖아?

- brute force (완전 탐색): 가능한 모든 점 쌍을 검사하는 방법

무식하게 찾아봐라. 근데 확실하다.

- unordered pair (순서 없는 쌍): `(i, j)`와 `(j, i)`를 같은 쌍으로 봄. `i < j`인 경우만 검사하면 됨
- pair count (쌍의 수): 서로 다른 점 `n`개의 쌍은 `n(n - 1) / 2`개이며, 완전 탐색은 `O(n^2)`
- tie (동률): 최소거리가 같은 쌍이 여러 개인 경우. 기존 결과를 유지해도 최소거리 정답은 같음

## Recursive Division (재귀 분할)

- x-order (x좌표 순서): 도시 배열을 x좌표순으로 정렬한 순서. index 범위로 좌우를 나누는 기준
- inclusive bounds (양 끝 포함 경계): `[left, right]`의 양 끝을 모두 포함하며 크기는 `right - left + 1`
- midpoint index (중간 index): `mid = (left + right) // 2`. 왼쪽 구간의 마지막 index
- left and right subsets (좌우 부분 집합): index 기준 `[left, mid]`와 `[mid + 1, right]`
- base case (종료 조건): 수업 구현에서는 3개 이하의 점을 직접 완전 탐색하며, 두 점 미만이면 쌍이 없어 `None`을 반환함
- local closest pair (부분 구간의 최근접 쌍): 한 재귀 구간 내부에서 가장 가까운 두 점
- cross-boundary pair (경계를 가로지르는 쌍): 왼쪽 점 하나와 오른쪽 점 하나로 이루어진 쌍. 좌우 내부의 답만 비교해서는 놓칠 수 있음
- split line (분할선): 좌우를 나누는 세로선. 수업 구현에서는 `cities[mid].x`와 `cities[mid + 1].x`의 중간을 사용함
- index-based membership (index 기반 소속 판정): 같은 x좌표의 점도 다른 편에 배정될 수 있으므로 `index <= mid`인지로 소속을 판단하는 방법


## Strip Search (경계 띠 탐색)

- distance bound (거리 상한): 좌우 최근접 거리 중 작은 값 `d`. 전체 최소거리는 이 값보다 클 수 없음
- strip (경계 띠): 분할선에서 가로 거리 `d` 미만인 점들의 영역. 폭은 `2d`
- candidate filtering (후보 추리기): 더 가까운 경계 쌍의 두 점은 모두 strip에 있어야 한다는 성질로 검사 대상을 줄이는 작업
- y-order (y좌표 순서): strip 후보를 y좌표순으로 살펴보기 위한 순서
- vertical separation (세로 간격): 두 점의 y좌표 차이. 유클리드 거리는 이 차이보다 작을 수 없음

- early termination (조기 종료): y순 탐색 중 세로 간격이 현재 최소거리 이상이면 이후 후보도 더 가까울 수 없으므로 `break`하는 것


- same-side exclusion (같은 편 제외): 같은 편의 점 쌍은 재귀 결과에 반영되어 있으므로 경계 탐색에서 `continue`로 제외하는 것
- current minimum distance (현재 최소거리): 후보 검사 중 갱신되는 최소거리. 조기 종료에는 strip 진입 당시의 거리보다 이 값을 사용함
- packing argument (배치 개수 논증): 작은 영역 안에 서로 충분히 떨어진 점이 몇 개까지 들어갈 수 있는지로 후보 수를 제한하는 논증
- half-distance grid (절반 거리 격자): 한 변이 `d/2`인 정사각형. 대각선이 `d`보다 짧아 같은 편의 점 두 개가 한 칸에 있을 수 없음
- boundary-aligned grid (분할선 정렬 격자): 격자의 중앙 세로선을 분할선에 맞춘 4열 2행 격자. 각 칸을 한쪽 편에 속하도록 해 한 칸당 최대 한 점임을 설명함
- boundary ownership (경계 소속 규칙): 격자선 위의 점은 일관된 규칙으로 한 칸에만 배정하고, 분할선 위의 점은 index로 정해진 편을 따르게 하는 규칙
- constant-size neighborhood (상수 크기 이웃): y순 탐색에서 거리 `d` 이내에 확인할 후보 수가 상수로 제한되는 성질. strip 전체 탐색이 선형 시간이 되는 근거

이론상 격자당 한개 이상 들어갈 수 없음, 따라서 7n 정도 이내로 끝남.

## Presorting and Complexity (사전 정렬과 복잡도)

- presorting (사전 정렬): 재귀 전에 필요한 좌표순 목록을 준비하는 것
- index array (index 배열): 도시 객체를 옮기지 않고 그 객체의 배열 위치를 나열한 목록
- order preservation (순서 보존): 부모의 y순 목록을 순회하며 좌우로 나누면 각 자식의 목록도 y순으로 남는 성질
- local y-order (구간별 y순 목록): 현재 재귀 구간의 점만 포함하는 y순 index 목록. 전체 목록을 모든 호출에서 다시 훑는 방식과 구별함
- repeated strip sorting (strip 반복 정렬): 각 재귀 구간에서 strip을 y순으로 다시 정렬하는 방식. 전체 최악 시간복잡도는 `O(n log^2 n)`

근데 y좌표 정렬을 미리하면 O(n logn)

- linear partitioning (선형 분배): 현재 구간의 y순 목록을 index 기준으로 좌우에 나누는 작업. 두 번 훑어도 `O(n)`
- linear combine (선형 결합): 현재 구간에서 목록 분배, strip 수집과 제한된 후보 탐색을 크기에 비례하는 시간에 수행하는 것
- recurrence relation (점화식): 사전 정렬한 목록을 나누어 전달하면 `T(n) = 2T(n/2) + O(n)`
- optimal implementation (최적 차수 구현): 최초 정렬과 재귀 처리를 합쳐 `O(n log n)`에 동작하는 수업의 최종 구현

## Python Records (파이썬 레코드)

- named tuple (이름 있는 튜플): `collections.namedtuple`로 만드는 tuple 하위 클래스. 필드를 이름으로 읽을 수 있음
- field access (필드 접근): `point.x`, `point.y`처럼 항목의 의미를 드러내는 접근 방식
- immutability (불변성): namedtuple의 필드에 새 값을 대입할 수 없는 성질. 목록 안의 객체 순서를 바꾸는 것과는 별개임
- representation (표현 문자열): namedtuple은 필드 이름과 값을 보여주는 `__repr__`을 제공함
- value equality (값 동등성): namedtuple은 tuple의 비교를 상속하여 항목의 값으로 비교함. 서로 다른 namedtuple 타입이나 일반 tuple과도 값이 같으면 같다고 판단함
