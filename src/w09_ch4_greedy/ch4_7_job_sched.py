"""시간이 정해진 모든 작업을 가장 적은 기계에 배정한다."""

import pyvisalgo as va


def schedule(jobs, vis=None):
    """작업은 [이름, 시작 시각, 종료 시각], 구간은 시작 포함·종료 미포함이다."""
    # ordered는 시작 시각으로 정렬한 새 목록입니다. 입력 jobs의 순서는 바꾸지 않습니다.
    ordered = sorted(jobs, key=lambda job: job[1])
    if vis:
        vis.order_jobs(ordered)
    # machines[i]는 기계 i에 배정한 작업 목록입니다.
    machines = []
    for job in ordered:
        if vis and vis.stopped():
            break
        # 아직 기계 재사용은 구현하지 않았으므로 작업마다 새 기계를 만듭니다.
        machine = len(machines)
        machines.append([job])
        if vis:
            vis.place(job, machine, False)


if __name__ == "__main__":
    vis = va.visualizer("job_sched")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        schedule(data.jobs, vis)
        vis.wait()
