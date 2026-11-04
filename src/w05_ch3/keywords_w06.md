# Week 6: Quick Sort and Selection (6주차: 퀵 정렬과 선택)

## Quick Sort (퀵 정렬)
partition, quick, quick
피벗을 어떤걸로 쓸건가?
겁나 중요하다. 피벗을 뭘 고를건지를 오래 고민하는게 더 이득되는 경우가 있음.

피벗 잘못선택하면 O(n^2)에 가까운 알고리즘이 될 수 있다.


- quick sort (퀵 정렬): pivot을 기준으로 배열을 분할한 뒤 양쪽 부분 배열을 재귀적으로 정렬하는 비교 정렬
- pivot (피벗): 원소들을 작은 쪽과 큰 쪽으로 나누는 기준값
- partition (분할): pivot과의 비교 결과에 따라 원소를 양쪽으로 재배치하는 작업. 양쪽 내부까지 정렬하는 것은 아님
- partition boundary (분할 경계): 분할 후 pivot이 놓이고 양쪽 구간이 갈리는 위치
- fixed position (확정된 위치): pivot이 전체 정렬 결과에서 들어갈 위치가 확정된 상태
- bidirectional scan (양방향 탐색): 왼쪽의 `p`는 오른쪽으로, 오른쪽의 `q`는 왼쪽으로 움직이며 교환할 원소를 찾는 방식
- misplaced element (잘못 배치된 원소): pivot 기준으로 반대쪽에 있어야 하는 원소
- pointer crossing (포인터 교차): `p >= q`가 되어 양쪽에서 더 교환할 원소를 찾는 과정을 끝내는 조건
- partition invariant (분할 불변식): 탐색이 진행되는 동안 이미 처리한 구간이 pivot과의 정해진 대소 관계를 유지한다는 성질
- equal keys (같은 키): pivot과 같은 값의 원소. 어느 쪽으로 보낼지는 구현의 비교 조건에 따라 달라짐
- recursive ranges (재귀 구간): pivot index를 `k`라 할 때 양 끝 포함 `[left, k - 1]`, `[k + 1, right]`. 확정된 pivot은 제외함
- balanced partition (균형 분할): pivot 양쪽 원소 수가 비슷한 분할
- unbalanced partition (불균형 분할): pivot이 한쪽 끝에 가까워 한 부분만 크게 남는 분할
- expected time complexity (기대 시간 복잡도): 무작위 pivot 등 적절한 가정에서 `O(n log n)`
- worst-case time complexity (최악 시간 복잡도): 불균형 분할이 반복되면 `O(n^2)`
- recursion stack space (재귀 스택 공간): 단순한 양쪽 재귀 구현은 균형 분할 시 `O(log n)`, 최악에는 `O(n)`
- unstable sort (불안정 정렬): 멀리 떨어진 원소 교환으로 같은 값의 원래 순서가 바뀔 수 있는 정렬

## Pivot Selection (피벗 선택)

- first-element pivot (첫 원소 피벗): 맨 왼쪽 값을 기준으로 선택하는 단순한 방식
- random pivot (무작위 피벗): 현재 구간에서 무작위로 pivot을 고르는 방식. 특정 입력 순서에 대한 의존을 줄임
- median (중앙값): 값의 크기순으로 나열했을 때 가운데에 있는 값
- median-of-three (세 값의 중앙값): 처음, 가운데, 마지막 등 세 후보의 중앙값을 pivot으로 선택하는 방법
- sampling (표본 추출): 전체 중앙값 대신 일부 원소를 살펴 pivot 후보를 정하는 방법
- Tukey's ninther (튜키의 나인서): 9개 표본을 세 묶음으로 나눈 뒤 각 묶음의 중앙값 3개 중 중앙값을 고르는 방법. 9개 전체의 정확한 중앙값과는 다를 수 있음
- sampling threshold (표본 선택 전환 기준): 큰 구간에서만 더 많은 표본을 사용하는 기준. 표본 선택 비용과 분할 품질의 균형을 고려함
- median of medians (중앙값들의 중앙값): 작은 묶음들의 중앙값을 모아 그 목록의 중앙값을 재귀적으로 선택하는 결정적 선택 기법. 단순히 중앙값을 몇 번 고르는 것과 구별함
- worst-case guarantee (최악 성능 보장): 알고리즘의 모든 입력에 대해 성립하는 비용 상한. median-of-three나 ninther만으로 퀵 정렬의 최악 `O(n log n)`이 보장되지는 않음

## Small Subarray Handling (작은 부분 배열 처리)

- cutoff threshold (중단 기준 크기): 작은 구간의 partition을 중단하는 기준
- local insertion sort (구간별 삽입 정렬): 작은 부분 배열마다 즉시 삽입 정렬하는 방식
- deferred insertion sort (지연 삽입 정렬): 작은 구간은 남겨 두고 큰 구간의 partition이 모두 끝난 뒤 전체 배열을 한 번 삽입 정렬하는 방식
- nearly sorted array (거의 정렬된 배열): 큰 구간의 순서가 정리되어 각 원소가 최종 위치에서 가까운 상태. 마지막 삽입 정렬의 이동 비용을 줄일 수 있음
- tuning (조정): threshold와 pivot 전략을 입력 특성 및 실행 환경에 맞춰 정하는 작업. 더 복잡한 전략이 항상 빠른 것은 아님

## Selection and Quickselect (선택과 퀵셀렉트)
다음은 어디서 찾아야되냐? 를 묻는다.
피벗을 랜덤하게 설정하면 반은 좋은 분할, 반은 나쁜 분할로 나뉠 것이기 때문에
시간은 O(nlog(n))

- selection problem (선택 문제): 전체를 정렬하지 않고 특정 순위의 값을 찾는 문제. Selection Sort와는 다른 문제
- order statistic (순서 통계량): 정렬했을 때 특정 위치에 오는 값
- rank (순위): 현재 구간에서 몇 번째로 작은 값인지 나타내는 번호. 수업 구현에서는 1부터 시작함
- quickselect (퀵셀렉트): partition 결과를 이용해 답이 있는 한쪽만 계속 탐색하는 선택 알고리즘
- pivot rank (피벗의 순위): 양 끝 포함 `[left, right]`에서 pivot index가 `k`이면 `k - left + 1`
- left-side selection (왼쪽 선택): 찾는 순위가 pivot 순위보다 작으면 왼쪽 구간에서 같은 순위를 찾음
- right-side selection (오른쪽 선택): 찾는 순위가 pivot 순위보다 크면 오른쪽에서 `찾던 순위 - pivot 순위`를 찾음
- discarded range (제외한 구간): 답이 없다는 사실이 확정되어 더 탐색하지 않는 부분
- rank adjustment (순위 조정): 앞에서 제외한 원소 수만큼 현재 구간의 목표 순위를 줄이는 작업
- partition reuse (분할 함수 재사용): Quick Sort와 Selection이 같은 partition 함수를 공유하고, 반환된 pivot 위치를 각자의 목적에 맞게 이용하는 것
- module import (모듈 가져오기): `import ch3_2_quick_sort as qs`처럼 다른 파일의 함수를 사용하는 방법
- main guard (직접 실행 구분): `if __name__ == "__main__":`로 실행 코드를 분리하여 import만 했을 때 실습 화면이나 메인 코드가 실행되지 않게 하는 장치
- expected linear time (기대 선형 시간): 무작위 pivot의 Quickselect는 기대 `O(n)`. 최악에는 `O(n^2)`까지 걸릴 수 있음
