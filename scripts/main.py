from datetime import datetime as dt

from backends.dag_runner import DagCron, run_dag


def task_1(dt_current: dt) -> str:
    return f"echo task_1 {dt_current.isoformat()}"


def task_2(dt_current: dt) -> str:
    return f"echo task_2 {dt_current.isoformat()}"


sample_tasks = [task_1, task_2]

PIPELINES = [
    ("sample pipeline", "*/3 * * * *", [task_1]),
    ("DAG1", "*/5 * * * *", [task_1]),
]


def __main():
    run_dag("test.db", PIPELINES)


if __name__ == "__main__":
    __main()
