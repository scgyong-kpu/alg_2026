import pyvisalgo as va


vis = va.visualizer("search_bin")


def search_bin(array, target):
    left = 0
    right = len(array) - 1

    while left <= right:
        vis.mark(left, right)
        mid = (left + right) // 2
        vis.compare(mid)

        if array[mid] == target:
            vis.found(mid)
            return mid

        if array[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    vis.not_found()
    return -1


while va.running():
    data = va.Data(
        array=[10, 20, 25, 35, 45, 55, 60, 75, 85, 90],
        target=85,
        file=__file__,
    )

    vis.setup(data)
    print(f"찾을 값: {data.target}, 정렬된 배열:", data.array)
    print("위치:", search_bin(data.array, data.target))
    vis.wait()
