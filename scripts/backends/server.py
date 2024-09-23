import os
import time
import typing
import schedule
from datetime import datetime as dt
from flask import Flask
import sqlite3
from cron_converter import Cron

con = sqlite3.connect("../tutorial.db")
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "hello world"


def run_server():
    app.run(host="0.0.0.0", port=7654, debug=True)


if __name__ == "__main__":
    run_server()
