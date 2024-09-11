import os
import time
import typing
import schedule
from datetime import datetime as dt
from flask import Flask
import sqlite3
from cron_converter import Cron

con = sqlite3.connect("tutorial.db")
app = Flask(__name__)

chart_html = open("chart.html").read()


def task_1(current_ts: dt) -> str:
    return f"echo task_1 {current_ts.isoformat()}"


def task_2(current_ts: dt) -> str:
    return f"echo task_2 {current_ts.isoformat()}"


def cmd_dag_solve(current_dt: dt, cmd_dag):
    solved_cmd_dag = []
    for cmd in cmd_dag:
        if isinstance(cmd, list):
            solved_cmd_dag.append(cmd_dag_solve(current_dt, cmd))
        else:
            solved_cmd_dag.append(cmd(current_dt))

    return solved_cmd_dag


def cmd_dag_run(cmd_dag) -> bool:
    for cmd in cmd_dag:
        if isinstance(cmd, list):
            cmd_dag_run(cmd)
        else:
            print(cmd)

    return True


class DagManager:
    def __init__(
            self,
            cmd_dag,
            cron: str,
            start_date: dt,
            end_date: typing.Optional[dt] = None,
    ):
        self.cmd_dag = cmd_dag
        self.cron = Cron(cron)
        self.start_date = start_date
        self.end_date = end_date
        self.schedule = self.cron.schedule(start_date)

    def next_dt(self) -> dt:
        return self.schedule.next()

    def run(self, current_dt: dt):
        solved_cmd_dag = cmd_dag_solve(current_dt, self.cmd_dag)
        print(solved_cmd_dag)
        cmd_dag_run(solved_cmd_dag)


DAG_1 = [task_1, [task_1, task_2], task_1]
DAG_2 = [task_1, task_2]
NOW = dt.now()

DAGS = {"DAG1": DagManager(DAG_1, cron="*/5 * * * *", start_date=NOW),
        "DAG2": DagManager(DAG_2, cron="*/1 * * * *", start_date=NOW)}


def run_dags(dags: typing.Dict[str, DagManager]):
    dag_last_run_dt: typing.Dict[str, dt] = dict()

    for k, v in dags.items():
        dag_last_run_dt[k] = v.next_dt()

    while True:
        next_dag_to_run = min(dag_last_run_dt.keys(), key=lambda x: dag_last_run_dt[x])
        dag_next_run_dt = dag_last_run_dt[next_dag_to_run]
        dag_last_run_dt[next_dag_to_run] = dags[next_dag_to_run].next_dt()
        yield next_dag_to_run, dag_next_run_dt, dags[next_dag_to_run]


if __name__ == '__main__':
    for t in run_dags(DAGS):
        dag_name, next_dt, dag_manager = t

        # # TODO(hanif): Add option to disable this to see what is going to happen
        # time_to_sleep = (next_dt - dt.now()).total_seconds()
        # if time_to_sleep > 0:
        #     print(f"sleeping for {time_to_sleep} seconds")
        #     time.sleep(time_to_sleep)

        print(dag_name, next_dt, dag_manager)

        dag_manager.run(next_dt)

# @app.route("/")
# def hello_world():
#     print(len(chart_html))
#     return chart_html
#
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=7654, debug=True)
