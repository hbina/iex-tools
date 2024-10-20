from flask import Flask, render_template
import sqlite3

from cron_db import CronDb

app = Flask(__name__)


@app.route("/")
def index():
    cron_db = CronDb("/tmp/test.db")
    commands = cron_db.select_commands()
    return render_template("index.html", commands=commands)


@app.route("/logs/<string:command_id>")
def log(command_id: str):
    cron_db = CronDb("/tmp/test.db")
    log_obj = cron_db.select_log(command_id)
    if log_obj is None :
        return render_template("cannot_find_log.html", command_id=command_id)
    return render_template("log.html", log_obj=log_obj)


def run_server():
    app.run(host="0.0.0.0", port=7654, debug=True)


if __name__ == "__main__":
    run_server()
