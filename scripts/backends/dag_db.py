import enum
import sqlite3
import threading
import typing
import uuid

SQLITE_LOCK = threading.Lock()


class CommandStatus(enum.Enum):
    Created = "created"
    Executing = "executing"
    Completed = "completed"
    Failed = "failed"


class RowCommand:
    def __init__(
            self,
            command: str,
            status: CommandStatus,
    ):
        self.command = command
        self.status = status


class DagDb:
    def __init__(self, database_path: str):
        self.connection = sqlite3.Connection(database_path)

        cursor = self.connection.cursor()

        cursor.execute("""
CREATE TABLE IF NOT EXISTS "commands" (
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "command" TEXT NOT NULL,
    "status" TEXT NOT NULL
);
""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS "logs" (
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "id" TEXT NOT NULL UNIQUE,
    "command" TEXT NOT NULL,
    "stdout" TEXT NOT NULL,
    "stderr" TEXT NOT NULL
);
""")

        self.connection.commit()

    def insert_commands(self, cmds: typing.List[str]):
        with SQLITE_LOCK:
            tuples = [(cmd, CommandStatus.Created.value) for cmd in cmds]
            cursor = self.connection.cursor()
            cursor.executemany("""
    INSERT INTO "commands" ("command", "status") VALUES (?, ?);
    """, tuples)
            self.connection.commit()

    def select_commands(self) -> typing.List[RowCommand]:
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
    SELECT "command", "status" FROM "commands";
    """)
            res = cursor.fetchall()
            return [RowCommand(x, CommandStatus(y)) for x, y in res]

    def select_commands_status(self, status: CommandStatus) -> typing.List[RowCommand]:
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
    SELECT "command", "status" FROM "commands" WHERE "status" = ?;
    """, (status.value,))
            res = cursor.fetchall()
            return [RowCommand(x, CommandStatus(y)) for x, y in res]

    def select_command(self, command: str) -> typing.Optional[RowCommand]:
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
    SELECT "command", "status" FROM "commands" where "command" = ?;
    """, (command,))
            res = cursor.fetchone()
            if res is None:
                return None
            x, y = res
            return RowCommand(x, CommandStatus(y))

    def update_command_completed(self, command: str):
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
    UPDATE "commands" SET "status" = ? WHERE "command" = ?;
    """, (CommandStatus.Completed.value, command))
            self.connection.commit()

    def insert_log(self, command: str, stdout: str, stderr: str):
        with SQLITE_LOCK:
            cursor = self.connection.cursor()
            cursor.execute("""
    INSERT INTO "logs" ("id", "command", "stdout", "stderr") VALUES (?, ?, ?, ?);
    """, (str(uuid.uuid4()), command, stdout, stderr))
            self.connection.commit()


def test_basic():
    db = DagDb(":memory:")
    db.insert_commands(["echo 1", "echo 2"])
    res = db.select_commands()

    expected = [RowCommand("echo 1", CommandStatus.Created), RowCommand("echo 2", CommandStatus.Created)]
    assert len(res) == len(expected)
    for i in range(len(res)):
        assert res[i].command == expected[i].command
        assert res[i].status == expected[i].status

    db.update_command_completed("echo 1")
    res = db.select_command("echo 1")
    assert res.command == "echo 1"
    assert res.status == CommandStatus.Completed

    res = db.select_command("echo 3")
    assert res is None
