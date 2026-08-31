import pyvisalgo as va


vis = va.visualizer("search_seq")


def search_seq(array, target):
    for i in range(len(array)):
        vis.compare(i)
        if array[i] == target:
            vis.found(i)
            return i

    vis.not_found()
    return -1


while va.running():
    data = va.Data(array=[17, 29, 12, 41, 33, 58, 24], target=41, file=__file__)

    vis.setup(data)
    print(f"찾을 값: {data.target}, 배열:", data.array)
    print("위치:", search_seq(data.array, data.target))
    vis.wait()
