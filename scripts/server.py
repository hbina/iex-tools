from flask import Flask, render_template
import sqlite3

from cron_db import CronDb


app = Flask(__name__)


@app.route("/")
def index():
    cron_db = CronDb("/tmp/test.db")
    commands = cron_db.select_commands()[:1024]
    return render_template('index.html', commands=commands)


def run_server():
    app.run(host="0.0.0.0", port=7654, debug=True)


if __name__ == "__main__":
    run_server()
