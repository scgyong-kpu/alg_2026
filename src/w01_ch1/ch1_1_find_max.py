import pyvisalgo as va


vis = va.visualizer("find_max")


def find_max(array):
    max_index = 0
    vis.update_max(max_index)

    for i in range(1, len(array)):
        vis.compare(i, max_index)
        if array[i] > array[max_index]:
            max_index = i
            vis.update_max(max_index)

    vis.finish(max_index)
    return array[max_index]


while va.running():
    data = va.Data(array=[1, 22, 41, 2, 492], file=__file__)

    vis.setup(data)
    print("다음에서 최대값 찾기:", data.array)
    print("최대값:", find_max(data.array))
    vis.wait()
