import enum
import logging
import sqlite3
import threading
import time
import typing
import uuid

SQLITE_LOCK = threading.Lock()


class CommandStatus(enum.Enum):
    Created = "created"
    Executing = "executing"
    Completed = "completed"
    Failed = "failed"


class GroupStatus(enum.Enum):
    Okay = "okay"
    Failed = "failed"


class RowCommand:
    def __init__(
            self,
            id_str: str,
            created_at: str,
            group_id: str,
            command_order: int,
            command: str,
            command_status: CommandStatus,
            group_status: GroupStatus,
    ):
        self.id_str = id_str
        self.created_at = created_at
        self.group_id = group_id
        self.command_order = command_order
        self.command_status = command_status
        self.group_status = group_status
        self.command = command


class RowLog:
    def __init__(
            self,
            id_str: str,
            command_id: str,
            created_at: str,
            command: str,
            return_code: int,
            stdout: str,
            stderr: str,
    ):
        self.id_str = id_str
        self.command_id = command_id
        self.created_at = created_at
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class RowCommandGroup:
    def __init__(
            self,
            id_str: str,
            created_at: str,
            group_status: CommandStatus,
    ):
        self.id_str = id_str
        self.created_at = created_at
        self.group_status = group_status


class CronDb:
    def __init__(self, database_path: str):
        self.connection = sqlite3.Connection(database_path)
        self.connection.set_trace_callback(logging.info)

    def init(self):
        cursor = self.connection.cursor()

        cursor.execute("""
CREATE TABLE IF NOT EXISTS "commands" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "group_id" TEXT NOT NULL,
    "command_order" INTEGER NOT NULL,
    "command" TEXT NOT NULL,
    "command_status" TEXT NOT NULL,
    "group_status" TEXT NOT NULL
);
""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS "logs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "command_id" TEXT NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "command" TEXT NOT NULL,
    "return_code" INTEGER NOT NULL,
    "stdout" TEXT NOT NULL,
    "stderr" TEXT NOT NULL,
    FOREIGN KEY ("command_id") REFERENCES commands('id')
);
""")

        self.connection.commit()

    def insert_commands(self, cmds: typing.List[str]):
        time.sleep(0.1)
        with SQLITE_LOCK:
            group_id = "group-" + str(uuid.uuid4())
            tuples = [
                (
                    "command-" + str(uuid.uuid4()),  #
                    group_id,  #
                    i,  #
                    cmds[i],  #
                    CommandStatus.Created.value,  #
                    GroupStatus.Okay.value,  #
                )
                for i in range(len(cmds))
            ]
            cursor = self.connection.cursor()
            cursor.executemany(
                """
INSERT INTO 
"commands" 
("id", "group_id", "command_order", "command", "command_status", "group_status") 
VALUES 
(?, ?, ?, ?, ?, ?);
""",
                tuples,
            )
            self.connection.commit()
            return [(t[0], t[3]) for t in tuples], group_id

    def select_commands(self) -> typing.List[RowCommand]:
        time.sleep(0.1)
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
SELECT 
"id", "created_at", "group_id", "command_order", "command", "command_status", "group_status"
FROM 
"commands";
    """)
            res = cursor.fetchall()
            # "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            # "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            # "group_id" TEXT NOT NULL,
            # "command_order" INTEGER NOT NULL,
            # "command" TEXT NOT NULL,
            # "command_status" TEXT NOT NULL,
            # "group_status" TEXT NOT NULL

            return [
                RowCommand(
                    t[0],
                    t[1],
                    t[2],
                    t[3],
                    t[4],
                    CommandStatus(t[5]),
                    GroupStatus(t[6]),
                )
                for t in res
            ]

    def update_command_completed(self, command_id: str):
        time.sleep(0.1)
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute(
                """
UPDATE 
"commands" 
SET 
"command_status" = ? 
WHERE 
"id" = ?;
""",
                (CommandStatus.Completed.value, command_id),
            )
            self.connection.commit()

    def update_command_failed(self, group_id: str, command_id: str):
        time.sleep(0.1)
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute(
                """
UPDATE 
"commands" 
SET 
"command_status" = ? 
WHERE 
"id" = ? AND "group_id" = ?;
""",
                (CommandStatus.Failed.value, command_id, group_id),
            )
            cursor.execute(
                """
UPDATE 
"commands" 
SET 
"group_status" = ? 
WHERE 
"group_id" = ?;
""",
                (GroupStatus.Failed.value, group_id),
            )
            self.connection.commit()

    def insert_log(self, command_id: str, command: str, return_code: int, stdout: str, stderr: str):
        time.sleep(0.1)
        with SQLITE_LOCK:
            log_id = "log-" + str(uuid.uuid4())
            cursor = self.connection.cursor()
            cursor.execute(
                """
INSERT INTO 
"logs" 
("id", "command_id", "command", "return_code", "stdout", "stderr") 
VALUES 
(?, ?, ?, ?, ?, ?);
""",
                (log_id, command_id, command, return_code, stdout, stderr),
            )
            self.connection.commit()

    def select_log(self, command_id: str) -> typing.Optional[RowLog]:
        time.sleep(0.1)
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute(
                """
SELECT 
"id", "command_id", "created_at", "command", "return_code", "stdout", "stderr"
FROM 
"logs"
WHERE
"command_id" = ?;
""",
                (command_id,),
            )
            res = cursor.fetchone()

            if res is None:
                return res

            return RowLog(res[0], res[1], res[2], res[3], res[4], res[5], res[6])
