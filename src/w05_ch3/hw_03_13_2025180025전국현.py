
"""실습 과제 13: Merge Sort, Quick Sort, Selection을 구현한다."""

import random


RANDOM_SEED = "EX_03"
ARRAY_SIZE = 30


def merge_sort(array):

    if len(array) <= 1:
        return
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    #right가 mid포함
    return merge(left, right)

 
def merge(left, right):
    result = []
    i = j = 0

    #리스트 두개를 비교해가면서 작은값들을 순서대로 추가
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # 남은 요소들 추가
    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1

    return result





def quick_sort(array, start, end):
    if start >= end:
        return

    pivot_index = partition(array, start, end)

    quick_sort(array, start, pivot_index - 1)
    quick_sort(array, pivot_index + 1, end)


def partition(arr, start, end):
    pivot = arr[end]
    left = start - 1   
    right = start     
    while right < end:
        if arr[right] <= pivot:
            left += 1
            arr[left], arr[right] = arr[right], arr[left]
        right += 1

    arr[left + 1], arr[end] = arr[end], arr[left + 1]
    return left + 1

def selection(array, n):
    if start == end:
        return arr[start]

    pivot_index = partition(arr, start, end)

    if k == pivot_index:
        return arr[pivot_index]
    elif k < pivot_index:
        return quickselect(arr, start, pivot_index - 1, k)
    else:
        return quickselect(arr, pivot_index + 1, end, k)


def make_random_array(randomizer):
    """1부터 99 사이의 값 ARRAY_SIZE 개를 가진 새 배열을 만든다."""
    return [randomizer.randint(1, 99) for _ in range(ARRAY_SIZE)]


if __name__ == "__main__":
    randomizer = random.Random(RANDOM_SEED)

    # 정렬 두 개는 서로 다른 무작위 배열을 사용한다.
    merge_data = make_random_array(randomizer)
    quick_data = make_random_array(randomizer)

    print("Merge Sort")
    print("정렬 전:", merge_data)
    merge_sort(merge_data)
    print("정렬 후:", merge_data)
    print()

    print("Quick Sort")
    print("정렬 전:", quick_data)
    quick_sort(quick_data)
    print("정렬 후:", quick_data)
    print()

    # Selection은 하나의 30개 배열에서 서로 다른 두 순위를 찾는다.
    selection_data = make_random_array(randomizer)
    first_n = randomizer.randint(10, 24)
    second_n = randomizer.randint(10, 24)

    print("Selection")
    print("배열:", selection_data)
    print(f"{first_n}번째로 작은 값은:", selection(selection_data, first_n))
    print(f"{second_n}번째로 작은 값은:", selection(selection_data, second_n))
