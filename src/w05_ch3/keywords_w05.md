# Week 5: Divide and Conquer and Merge Sort (5주차: 분할 정복과 합병 정렬)

## Divide and Conquer (분할 정복)

- divide and conquer (분할 정복): 문제를 작은 부분 문제로 나누고, 각 결과를 결합하여 원래 문제를 해결하는 설계 방법
- divide (분할): 원래 문제를 더 작은 부분 문제로 나누는 단계
- conquer (정복): 부분 문제를 재귀적으로 해결하는 단계
- combine (결합): 부분 문제의 결과를 이용해 원래 문제의 답을 만드는 단계
- subproblem (부분 문제): 원래 문제와 같은 구조를 가지면서 입력 크기가 더 작은 문제
- recursion (재귀): 함수가 더 작은 문제를 처리하기 위해 자기 자신을 호출하는 방식
- base case (종료 조건): 더 나누지 않고 직접 답을 구하는 작은 문제
없으면 무한이 돈다.


- recursive case (재귀 단계): 문제를 나누고 재귀 호출로 처리하는 경우
- call stack (호출 스택): 아직 반환하지 않은 함수 호출의 실행 정보를 보관하는 구조
메모리 내놔라
원래 배열 크기만큼 메모리 사용

- recursion depth (재귀 깊이): 중첩된 재귀 호출의 깊이
절반에 가까운 크기일 수록 짧아짐.

- balanced division (균형 분할): 부분 문제의 크기가 비슷하도록 나누는 것
merge sort는 딱 절반, quicksort는 어디서 나눠질지 모름

- recurrence relation (점화식): 작은 문제의 비용으로 전체 문제의 비용을 나타내는 식. 합병 정렬은 `T(n) = 2T(n/2) + O(n)`

## Array Ranges (배열 구간)

- inclusive range (양 끝 포함 구간): `left..right`에서 두 끝 index를 모두 포함하는 범위
- range size (구간 크기): 양 끝 포함 구간의 원소 수는 `right - left + 1`
- midpoint (중간 index): `mid = (left + right) // 2`로 구한 분할 위치
- left subarray (왼쪽 부분 배열): `left..mid` 범위. `mid`를 포함함
- right subarray (오른쪽 부분 배열): `mid + 1..right` 범위. `mid`를 포함하지 않음
- half-open range (반열린 구간): 시작은 포함하고 끝은 제외하는 범위. Python의 `range(left, right + 1)`은 `right`까지 순회함
- off-by-one error (경계 한 칸 오류): 끝 포함 여부를 혼동하여 한 원소를 빠뜨리거나 범위를 벗어나는 오류

## Merge Sort (합병 정렬)
반 가르고 (중략) 병합

- merge sort (합병 정렬): 배열을 나누어 각각 정렬한 뒤 두 정렬된 구간을 병합하는 비교 정렬
- merge (병합): 이미 정렬된 두 구간의 앞 원소를 비교하며 하나의 정렬된 구간을 만드는 작업
- precondition (사전 조건): 병합을 시작할 때 양쪽 입력 구간이 각각 정렬되어 있어야 한다는 조건
- two-pointer technique (두 포인터 기법): 양쪽 구간에서 다음에 꺼낼 원소의 index를 각각 관리하는 방법
- output position (출력 위치): 병합 결과에서 다음 원소를 기록할 위치
- exhausted subarray (소진된 부분 배열): 모든 원소를 결과로 옮겨 더 비교할 원소가 없는 구간
- remaining elements (남은 원소): 한쪽이 소진된 뒤 다른 쪽에 남은 원소. 이미 정렬되어 있으므로 순서대로 옮기면 됨
- auxiliary array (보조 배열): 병합 결과나 원본 사본을 보관하는 추가 배열
- copy back (원본으로 복사): 보조 배열의 병합 결과를 원본 배열의 해당 구간으로 옮기는 작업
- stable merge (안정적인 병합): 값이 같을 때 왼쪽 구간의 원소를 먼저 선택하여 원래 순서를 유지하는 병합
- time complexity (시간 복잡도): 병합 한 번은 구간 크기에 비례하며, 전체 합병 정렬은 최악 `O(n log n)`
- auxiliary space (보조 공간): 일반적인 배열 합병 정렬은 `O(n)`의 보조 배열을 사용하며 재귀 스택은 `O(log n)`

## Merge Sort Improvements (합병 정렬 개선)

파이썬 레벨에서는 크게 의미 없지만, 다른 언어에서는 이득보는 경우 있음

- already ordered runs (이미 이어진 정렬 구간): 왼쪽 최댓값이 오른쪽 최솟값 이하라면 두 구간을 그대로 이어도 정렬된 상태
- merge skipping (병합 생략): `array[mid] <= array[mid + 1]`이면 불필요한 병합을 하지 않는 개선
- insertion sort cutoff (삽입 정렬 전환 기준): 작은 구간에서는 재귀 호출 대신 삽입 정렬을 사용하는 기준 크기
- hybrid sort (혼합 정렬): 큰 구간과 작은 구간에 서로 다른 정렬 알고리즘을 적용하는 방식
- slice assignment (슬라이스 대입): 한쪽이 소진된 뒤 남은 구간을 슬라이스로 한 번에 옮기는 방법
- buffer reuse (버퍼 재사용): 보조 배열을 처음에 한 번 준비하여 여러 병합에서 재사용하는 방법
- ping-pong merge (교대 버퍼 병합): 재귀 단계마다 읽는 배열과 쓰는 배열의 역할을 바꾸어 별도의 복사 작업을 줄이는 방식
삥 뽕

- constant factor (상수 계수): 같은 시간복잡도 안에서도 실제 실행시간을 달라지게 하는 연산 비용
- empirical measurement (실측): 개선 효과를 실제 실행으로 확인하는 것. Python에서는 슬라이싱과 반복문의 비용 때문에 다른 언어와 결과가 다를 수 있음
