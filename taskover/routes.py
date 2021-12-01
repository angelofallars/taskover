from flask import render_template, redirect, flash, g, Blueprint
from taskover.db import get_db


bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    db = get_db()
    tasks = db.execute("SELECT title, body FROM tasks").fetchall()

    return render_template("index.html", tasks=tasks)


@bp.route("/login")
def login():
    pass


@bp.route("/logout")
def logout():
    pass


@bp.route("/register")
def register():
    pass
