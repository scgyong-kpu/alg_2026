"""시간이 정해진 모든 작업을 가장 적은 기계에 배정한다."""

from heapq import heappop, heappush

import pyvisalgo as va


def schedule(jobs, vis=None):
    """작업은 [이름, 시작 시각, 종료 시각], 구간은 시작 포함·종료 미포함이다."""
    # ordered는 시작 시각으로 정렬한 새 목록입니다. 입력 jobs의 순서는 바꾸지 않습니다.
    ordered = sorted(jobs, key=lambda job: job[1])
    if vis:
        vis.order_jobs(ordered)
    # machines[i]는 기계 i에 배정한 작업 목록입니다.
    machines = []
    # ends: 각 기계의 (마지막 종료 시각, 기계 번호)를 저장하는 최소 힙입니다.
    ends = []
    for job in ordered:
        if vis and vis.stopped():
            break
        _, start, end = job
        # 가장 빨리 비는 기계도 아직 사용 중이라면 새 기계가 꼭 필요합니다.
        # 종료 시각과 시작 시각이 같으면 작업이 겹치지 않으므로 재사용합니다.
        reuse = bool(ends and ends[0][0] <= start)
        if reuse:
            _, machine = heappop(ends)
        else:
            machine = len(machines)
            machines.append([])
        machines[machine].append(job)
        heappush(ends, (end, machine))
        if vis:
            vis.place(job, machine, reuse)
    return machines


if __name__ == "__main__":
    vis = va.visualizer("job_sched")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        machines = schedule(data.jobs, vis)
        if not vis.stopped():
            for i, jobs in enumerate(machines, 1):
                print(f"기계 {i}:", jobs)
            vis.finish(len(machines))
        vis.wait()
