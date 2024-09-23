import typing
from datetime import datetime as dt


class DagContainer:
    def __init__(self, tasks: typing.List[typing.Callable[[dt], str]]):
        self.tasks = tasks

    def create_commands(self, current_dt: dt) -> typing.List[str]:
        result = []
        for n in self.tasks:
            result.append(n(current_dt))
        return result


def test_basic():
    def task_1(current_dt: dt) -> str:
        return f"echo 1 {current_dt.strftime('%y%m%d_%H%M')}"

    def task_2(current_dt: dt) -> str:
        return f"echo 2 {current_dt.strftime('%y%m%d_%H%M')}"

    def task_3(current_dt: dt) -> str:
        return f"echo 3 {current_dt.strftime('%y%m%d_%H%M')}"

    dag_container = DagContainer(tasks=[task_1, task_2, task_3])
    cmds = dag_container.create_commands(dt.now())
    for cmd in cmds:
        print(cmd)
