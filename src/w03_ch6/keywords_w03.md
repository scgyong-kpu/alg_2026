# 3주차 정렬 기본 알고리즘

## 정렬

- sort
오름차순, 내림차순
- ascending order /asd
- descending order /dsd
sorted, sort 차이구분

- in-place sort
- comparison sort
비교정렬, 비교하지 않는 정렬

- stable sort
안정적인지아닌지 merge는 stable, quick은 아님.


- swap
바꿔잇

- pass
- sorted region
- unsorted region
- time complexity
- O(n^2)

## 버블 정렬
가장 쉽고
가장 오래걸리는 
수래기

인자값을 서로 바꿔서
- bubble sort
- adjacent comparison
- adjacent swap
- sorted suffix
- pass boundary
- swap flag
- early stop

- best case
n

- worst case
n^2

## 선택 정렬
은?근 빠르다.
교환횟수가 적어서
무작위 값 기준에서 n^2중에 대체로 가장 빠르다.

- selection sort
- minimum
- minimum index
- scan
- sorted prefix
- fixed swap count

## 삽입 정렬
정렬이 어느정도 된거에서 무식하게 빠르다.
개선하는 알고리즘 3개 다 학습
실전에서 사용되는 빠른 알고리즘

- insertion sort
- sorted prefix
- candidate value
- swap based insertion
- early break
- shift
- hole

## 셸 정렬
삽입정렬을 하긴 하는데
갭을 둬서 정렬을 한다.
뒤에나오는 heap정렬보다 빠르다? n이 작다 or 캐시 히트

- Shell sort
- gap
- gap sequence
- gapped insertion sort
- group
- index modulo gap
- gap reduction
- final gap
- partially sorted array
- adaptive behavior
