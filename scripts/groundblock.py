import heapq
import logging
import multiprocessing
import subprocess
import threading
import time
import typing
from datetime import datetime as dt
from cron_converter import Cron

from cron_db import CronDb, RowCommand


class CronJob:
    def __init__(self, name: str, cron: str, commands: typing.List[typing.Callable[[dt], str]], db_path: str, dry_run: bool):
        self.name = name
        self.cron = cron
        self.commands = commands
        self.db_path = db_path
        self.schedule = Cron(cron).schedule(start_date=dt.now())
        self.dry_run = dry_run

    def _run(self):
        cron_db = CronDb(self.db_path)
        while True:
            dt_next = self.schedule.next()

            if not self.dry_run:
                dt_now = dt.now()
                if dt_next > dt_now:
                    time_to_sleep = (dt_next - dt_now).total_seconds() / 1_000_000_000

                    if time_to_sleep > 0:
                        logging.info(f"{self.name} sleeping for {time_to_sleep} seconds from {dt_now} to {dt_next}")
                        time.sleep(time_to_sleep)

            cmds = [c(dt_next) for c in self.commands]
            group_id = cron_db.insert_commands(cmds)

            for cmd in cmds:
                logging.info(f"running '{cmd}'")
                if not self.dry_run:
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

                    # Output of the command
                    stdout_output = result.stdout
                    stderr_output = result.stderr

                    cron_db.insert_log(cmd, result.returncode, stdout_output, stderr_output)
                    if result.returncode == 0:
                        cron_db.update_command_completed(cmd)
                    else:
                        cron_db.update_command_failed(group_id, cmd)
                        break
            # print("ended")

    def run(self):
        try:
            self._run()
        except BaseException as e:
            print(e)


def run_cron(cron_job: CronJob):
    cron_job.run()


class GroundBlock:
    def __init__(self, db_path: str, dry_run: bool = False):
        self.db_path = db_path
        self.cron_jobs: typing.List[CronJob] = []
        self.dry_run = dry_run

        cron_db = CronDb(db_path)
        cron_db.init()

    def add(self, name: str, cron_str: str, commands: typing.List[typing.Callable[[dt], str]]):
        self.cron_jobs.append(CronJob(name, cron_str, commands, self.db_path, self.dry_run))

    def run(self):
        threads = []

        for cron_job in self.cron_jobs:
            thread = multiprocessing.Process(target=run_cron, args=(cron_job,))
            threads.append(thread)

        for t in threads:
            t.start()

        for t in threads:
            t.join()


def main():
    def task_1_1(dt_current: dt) -> str:
        return f"echo task_1_1 {dt_current.isoformat()}"

    def task_1_2(dt_current: dt) -> str:
        return f"echo task_1_2 {dt_current.isoformat()}"

    def task_1_3(dt_current: dt) -> str:
        return f"echo task_1_3 {dt_current.isoformat()}; sleep 4"

    def task_1_4(dt_current: dt) -> str:
        return f"echo task_1_4 {dt_current.isoformat()}"

    def task_1_5(dt_current: dt) -> str:
        return f"echo task_1_5 {dt_current.isoformat()}"

    def task_2_1(dt_current: dt) -> str:
        return f"echo task_2_1 {dt_current.isoformat()}"

    def task_2_2(dt_current: dt) -> str:
        return f"echo task_2_2 {dt_current.isoformat()}"

    def task_2_3(dt_current: dt) -> str:
        return f"echo task_2_3 {dt_current.isoformat()}"

    def task_2_4(dt_current: dt) -> str:
        return f"echo task_2_4 {dt_current.isoformat()}"

    def task_2_5(dt_current: dt) -> str:
        return f"echo task_2_5 {dt_current.isoformat()}"

    ground_block = GroundBlock("test.db")
    (ground_block.add("Cron1", "*/2 * * * *", [task_1_1, task_1_2, task_1_3, task_1_4, task_1_5]),)
    ground_block.add("Cron2", "*/3 * * * *", [task_2_1, task_2_2, task_2_3, task_2_4, task_2_5])
    ground_block.run()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(funcName)15s | %(message)s", level=logging.DEBUG)
    main()
