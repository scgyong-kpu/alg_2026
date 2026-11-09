"""시간이 정해진 모든 작업을 가장 적은 기계에 배정한다."""

import pyvisalgo as va


def schedule(jobs, vis=None):
    """작업은 [이름, 시작 시각, 종료 시각], 구간은 시작 포함·종료 미포함이다."""
    # ordered는 시작 시각으로 정렬한 새 목록입니다. 입력 jobs의 순서는 바꾸지 않습니다.
    ordered = sorted(jobs, key=lambda job: job[1])
    if vis:
        vis.order_jobs(ordered)


if __name__ == "__main__":
    vis = va.visualizer("job_sched")
    while va.running():
        data = va.next_data(__file__)
        vis.setup(data)
        schedule(data.jobs, vis)
        vis.wait()
