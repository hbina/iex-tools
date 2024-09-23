import os
import random
import subprocess
import threading
import time
import typing
from datetime import datetime as dt
from idlelib.undo import Command

from cron_converter import Cron

from backends.dag_container import DagContainer
from backends.dag_db import DagDb, CommandStatus


class DagCron:
    def __init__(
            self,
            database_path: str,
            dag_name: str,
            dag_container: DagContainer,
            cron_str: str,
            start_date: dt,
            end_date: typing.Optional[dt] = None,
    ):
        self.dag_name = dag_name
        self.cron_str = cron_str
        self.dag_container = dag_container

        self.cron = Cron(cron_str)
        self.start_date = start_date
        self.end_date = end_date
        self.schedule = self.cron.schedule(start_date)
        self.connection = DagDb(database_path)

    def next_dt(self) -> dt:
        return self.schedule.next()

    def run(self):
        time.sleep(random.random() * 2)
        while True:
            dt_next = self.schedule.next()
            dt_now = dt.now()
            if dt_now > dt_next:
                time_to_sleep = (dt_next - dt_now).total_seconds() / 10000
                if time_to_sleep > 0:
                    print(f"{self.dag_name} sleeping for {time_to_sleep} seconds from {dt_now} to {dt_next}")
                    time.sleep(time_to_sleep)

            cmds = self.dag_container.create_commands(dt_next)
            self.connection.insert_commands(cmds)


def __run_dag(database_path: str, dag_name: str, cron_str: str, dag_container: DagContainer):
    dag_cron = DagCron(
        database_path=database_path,
        dag_name=dag_name,
        cron_str=cron_str,
        dag_container=dag_container,
        start_date=dt.now()
    )
    dag_cron.run()


def __run_command(database_path: str):
    dag_db = DagDb(database_path)
    while True:
        cmds = dag_db.select_commands_status(CommandStatus.Created)
        for cmd in cmds:
            result = subprocess.run(cmd.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

            # Output of the command
            stdout_output = result.stdout
            stderr_output = result.stderr

            dag_db.update_command_completed(cmd.command)
            dag_db.insert_log(cmd.command, stdout_output, stderr_output)
        time.sleep(5)


def run_dag(database_path: str, dags: typing.List[typing.Tuple[str, str, typing.List[typing.Callable[[dt], str]]]]):
    threads = []
    for d in dags:
        dag_name, cron_str, dag = d

        thread = threading.Thread(target=__run_dag, args=(database_path, dag_name, cron_str, DagContainer(dag)))
        threads.append(thread)

    if True:
        thread = threading.Thread(target=__run_command, args=(database_path,))
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def __main():
    def task_1(dt_current: dt) -> str:
        return f"echo task_1 {dt_current.isoformat()}"

    def task_2(dt_current: dt) -> str:
        return f"echo task_2 {dt_current.isoformat()}"

    def task_3(dt_current: dt) -> str:
        return f"echo task_3 {dt_current.isoformat()}"

    def task_4(dt_current: dt) -> str:
        return f"echo task_4 {dt_current.isoformat()}"

    def task_5(dt_current: dt) -> str:
        return f"echo task_5 {dt_current.isoformat()}"

    dags = [
        ("DAG1", "*/2 * * * *", [task_1, task_2, task_3, task_4, task_5]),
        ("DAG2", "*/3 * * * *", [task_1, task_2, task_3, task_4, task_5]),
        ("DAG3", "*/7 * * * *", [task_1, task_2, task_3, task_4, task_5]),
        ("DAG4", "*/16 * * * *", [task_1, task_2, task_3, task_4, task_5]),
    ]
    run_dag("test.db", dags)


if __name__ == "__main__":
    __main()
