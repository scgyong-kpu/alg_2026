# Week 4: Advanced Sorting (4주차: 고급 정렬)

## Heap Sort (힙 정렬)

- heap (힙): 완전 이진 트리 형태를 만족하는 자료 구조
- complete binary tree (완전 이진 트리): 마지막 level을 제외한 모든 level이 채워지고, 마지막 level은 왼쪽부터 채워진 트리
- array representation (배열 표현): 트리 노드를 배열 index로 표현하는 방법
- root (루트): index `0`에 있는 최상위 노드
- parent (부모 노드): 어떤 노드의 바로 위 노드
- child (자식 노드): 어떤 노드의 바로 아래 노드
- left child (왼쪽 자식): 부모 index `i`의 `2 * i + 1` 위치 노드
- right child (오른쪽 자식): 부모 index `i`의 `2 * i + 2` 위치 노드
- leaf (리프 노드): 자식이 없는 노드
- last parent (마지막 부모): `count // 2 - 1`에 있는, 자식을 가진 마지막 노드
- max heap (최대 힙): 모든 부모 값이 자식 값보다 크거나 같은 힙
- min heap (최소 힙): 모든 부모 값이 자식 값보다 작거나 같은 힙
- heap property (힙 조건): 부모와 자식 사이에 유지해야 하는 대소 관계
- subtree (부분 트리): 어떤 노드를 root로 하는 트리의 일부
- heapify (힙 만들기): 한 subtree가 힙 조건을 만족하도록 만드는 작업
- downheap (아래로 내리기): 부모를 더 큰 자식과 비교하며 아래로 보내는 heapify 방식
- sift-down (아래로 훑어 내리기): downheap의 다른 이름
- build heap (힙 만들기 단계): 마지막 부모부터 root까지 heapify해 전체 배열을 힙으로 만드는 과정
- extraction (최대값 꺼내기): root의 최대값을 heap 마지막 원소와 교환해 정렬 완료 구간으로 보내는 과정
- sorted suffix (정렬 완료 접미 구간): 배열 오른쪽에서 최대값부터 확정된 구간
- in-place sort (제자리 정렬): 추가 배열을 거의 사용하지 않고 원래 배열 안에서 정렬하는 방식
- unstable sort (불안정 정렬): 같은 값을 가진 원소의 원래 순서가 유지되지 않을 수 있는 정렬
- time complexity (시간 복잡도): build heap은 `O(n)`, 전체 Heap Sort는 `O(n log n)`

## Counting Sort (계수 정렬)

- counting sort (계수 정렬): 각 값이 나온 횟수를 세어 정렬하는 알고리즘
- non-comparison sort (비교하지 않는 정렬): 두 원소의 대소 비교만으로 순서를 정하지 않는 정렬
- key range (키 범위): 입력값이 가질 수 있는 최솟값부터 최댓값까지의 범위
- count array (계수 배열): 각 값의 등장 횟수를 저장하는 배열
- frequency (빈도): 어떤 값이 등장한 횟수
- offset (오프셋): 음수 또는 0이 아닌 최솟값을 배열 index로 바꾸기 위해 더하거나 빼는 값
- cumulative count (누적 계수): 현재 값 이하의 원소가 모두 몇 개인지 나타내는 계수
- prefix sum (접두 합): 앞 원소부터 차례로 더한 누적 합
- output array (출력 배열): 안정 정렬 결과를 만들기 위해 사용하는 별도 배열
- stable sort (안정 정렬): 같은 값을 가진 원소의 원래 순서를 유지하는 정렬
- time complexity (시간 복잡도): 입력 수가 `n`, 값의 범위가 `k`일 때 `O(n + k)`
- space complexity (공간 복잡도): 계수 배열과 출력 배열 때문에 `O(n + k)`
- small range (작은 값 범위): `k`가 `n`에 비해 충분히 작을 때 Counting Sort가 적합한 조건

## Radix Sort (기수 정렬)

- radix sort (기수 정렬): 수를 자릿수별로 나누어 여러 번 정렬하는 알고리즘
- radix (기수): 한 자릿수에 사용할 수 있는 값의 개수, 예를 들어 10진수의 radix는 10
- digit (자릿수): 일의 자리, 십의 자리처럼 수를 구성하는 한 자리
- digit extraction (자릿수 추출): 나눗셈과 나머지 연산으로 특정 자릿수를 얻는 작업
- bucket (버킷): 같은 자릿수 값을 가진 원소를 모으는 칸
- stable inner sort (안정적인 내부 정렬): 각 자릿수를 정렬할 때 이전 자릿수의 순서를 보존하는 정렬
- counting sort (계수 정렬): Radix Sort의 각 자릿수를 안정적으로 정렬할 때 자주 사용하는 알고리즘
- pass (반복 단계): 한 자릿수를 정렬하는 한 번의 처리
- maximum digits (최대 자릿수): 입력값 중 가장 큰 값이 가진 자릿수
- time complexity (시간 복잡도): 자릿수 개수가 `d`, radix가 `r`일 때 `O(d(n + r))`

### LSD Radix Sort (LSD 기수 정렬)

- least significant digit (최하위 자릿수): 일의 자리처럼 가장 작은 자릿수
- LSD radix sort (LSD 기수 정렬): 최하위 자릿수부터 높은 자릿수 방향으로 안정 정렬을 반복하는 방식
- stable pass (안정적인 반복): 낮은 자릿수에서 만든 순서를 높은 자릿수 정렬 뒤에도 유지하는 조건
- iterative processing (반복 처리): 모든 원소를 같은 자릿수 순서로 여러 번 처리하는 방식

### MSD Radix Sort (MSD 기수 정렬)

- most significant digit (최상위 자릿수): 가장 큰 자리값을 나타내는 자릿수
- MSD radix sort (MSD 기수 정렬): 최상위 자릿수부터 낮은 자릿수 방향으로 버킷을 나누는 방식
- recursive processing (재귀 처리): 같은 버킷에 들어간 원소만 다음 자릿수로 다시 나누는 방식
- partition (분할): 자릿수 값에 따라 원소를 여러 그룹으로 나누는 작업
- variable length key (길이가 다른 키): 문자열처럼 자릿수 또는 문자 수가 서로 다른 입력

## Comparison Sorting Lower Bound (비교 정렬의 하한)

- comparison sort (비교 정렬): 두 원소의 대소 비교 결과를 이용해 정렬하는 알고리즘
- comparison model (비교 모델): 알고리즘이 원소 비교만으로 정보를 얻는다고 가정하는 분석 모델
- decision tree (결정 트리): 비교 결과에 따라 다음 비교가 갈라지는 과정을 트리로 나타낸 것
- permutation (순열): `n`개 서로 다른 원소를 나열할 수 있는 모든 경우, 총 `n!`개
- leaf (리프): 결정 트리에서 하나의 최종 정렬 결과에 대응하는 끝 노드
- binary comparison (이진 비교): 두 원소 비교 결과가 작다 또는 크다의 두 갈래로 나뉘는 비교
- tree height (트리 높이): 최악의 경우에 필요한 비교 횟수
- lower bound (하한): 어떤 알고리즘도 이보다 적게 사용할 수 없는 최소 비용
- logarithm of permutations (순열 수의 로그): 모든 `n!`개 입력 순서를 구별하려면 결정 트리 높이가 최소 `log2(n!)`이어야 함
- Omega n log n (오메가 n log n): `log2(n!)`이 `Omega(n log n)`이므로 모든 비교 정렬의 최악 시간 하한도 `Omega(n log n)`이라는 결론
- merge sort (합병 정렬): 비교 정렬 하한에 맞는 `O(n log n)` 정렬 알고리즘
- heap sort (힙 정렬): 비교 정렬 하한에 맞는 `O(n log n)` 정렬 알고리즘
- quick sort (퀵 정렬): 평균적으로 `O(n log n)`이지만 최악에는 `O(n^2)`이 될 수 있는 비교 정렬
- escaping the lower bound (하한을 벗어남): Counting Sort와 Radix Sort는 값의 범위나 자릿수 정보를 사용하므로 비교 정렬 하한의 적용 대상이 아님
