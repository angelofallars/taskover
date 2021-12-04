from functools import wraps
from sqlite3 import Row
from typing import Union

from flask import (render_template, redirect, url_for,
                   flash, g, request, Blueprint, session, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from taskover.db import get_db


bp = Blueprint("routes", __name__)


def get_task(task_id: int, user_id: int) -> Union[Row, None]:
    # Check if a task with that ID exists and is owned by the user
    task = get_db().execute(
                            """SELECT * FROM tasks
                               WHERE id = ? AND user_id = ?""",
                            (task_id, user_id)).fetchone()

    return task


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("routes.login"))
        else:
            return view(**kwargs)

    return wrapped_view


@bp.route("/")
def index():
    db = get_db()

    # Get the list of tasks for the user
    if g.user:
        tasks = db.execute("""SELECT id, title, body, is_completed
                              FROM tasks WHERE user_id = ?""",
                           (g.user["id"],)).fetchall()
    else:
        tasks = {}

    return render_template("index.html", tasks=tasks, css="index.css")


@bp.route("/tasks")
@login_required
def fetch_tasks():
    tasks = get_db().execute("""SELECT id, title, body, is_completed, task_order
                             FROM tasks WHERE user_id = ?""",
                             (g.user["id"],)).fetchall()

    # Convert SQLite row into dicts
    for i in range(len(tasks)):
        tasks[i] = dict(tasks[i])

        # Convert Pythonic prop names into JavaScript names
        tasks[i]["isCompleted"] = tasks[i]["is_completed"]
        del tasks[i]["is_completed"]
        tasks[i]["order"] = tasks[i]["task_order"]
        del tasks[i]["task_order"]

    return jsonify(tasks)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create_task():
    if request.method == "POST":
        # Get title and body
        title = request.form.get("title", "")
        body = request.form.get("body", "")
        db = get_db()
        error = None

        # Check if title content exists
        if not title:
            error = "Task must have a title."

        if not error:
            # Insert the task into database
            db.execute(
                       """INSERT INTO tasks (title, body, user_id, task_order)
                          VALUES (?, ?, ?,
                                  (SELECT COUNT(*) FROM tasks WHERE
                                   user_id = ?) + 1)
                          """,
                       (title, body, g.user["id"], g.user["id"]))
            db.commit()

            return redirect(url_for("routes.index"))

        else:
            flash(error)
            return redirect(url_for("routes.create_task"))

    else:
        return render_template("create.html")


@bp.route("/update", methods=("POST",))
@login_required
def update_task():
    db = get_db()
    task_id = request.form.get("id", None)
    update_db = request.form.get("update_db", "no")

    if not task_id:
        return "Bad request, no task ID", 400

    task = get_task(int(task_id), g.user["id"])

    if not task:
        return "You are forbidden from accessing that!", 403

    # Update form
    if update_db == "no":
        return render_template("update.html", task=task)

    # Update the database
    elif update_db == "yes":
        # Get title and body
        title = request.form.get("title", "")
        body = request.form.get("body", "")
        error = None

        # Check if title content exists
        if not title:
            error = "Task must have a title."

        if not error:
            # Update the task in the database
            db.execute(
                       """UPDATE tasks
                          SET title = ?,
                              body = ?
                          WHERE id = ?
                          """,
                       (title, body, task_id))
            db.commit()

            return redirect(url_for("routes.index"))

        else:
            flash(error)
            return redirect(url_for("routes.create_task"))


@bp.route("/delete", methods=("POST",))
@login_required
def delete_task():
    db = get_db()
    task_id = request.form.get("id", None)

    if not task_id:
        return "Bad request, no task ID", 400

    task = get_task(int(task_id), g.user["id"])

    if not task:
        return "You are forbidden from accessing that!", 403

    db.execute("""DELETE FROM tasks
                  WHERE id = ?""", (task_id,))
    # Shift all proceeding task counts by -1
    db.execute("""UPDATE tasks
                  SET task_order = task_order - 1
                  WHERE user_id = ? AND
                  task_order > ?""", (g.user["id"], task["task_order"]))
    db.commit()

    return redirect(url_for("routes.index"))


@bp.route("/mark_completion", methods=("POST",))
def toggle_task():
    # Toggle a task between done / not done
    db = get_db()
    task_id = request.form.get("id", None)

    if not task_id:
        return "Bad request, no task ID", 400

    task = get_task(int(task_id), g.user["id"])

    if not task:
        return "You are forbidden from accessing that!", 403

    new_status = 1 if task["is_completed"] == 0 else 0

    db.execute("""UPDATE tasks
                  SET is_completed = ?
                  WHERE id = ?""", (new_status, task_id))
    db.commit()

    return redirect(url_for("routes.index"))


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        error = None

        user = db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
                ).fetchone()

        if not user:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if not error:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("routes.index"))
        else:
            flash(error)
            return redirect(url_for("routes.login"))

    else:
        return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.index"))


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        # Check if username + password exists
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        username_already_exists = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,
                                                           )).fetchall()
        # Check if the user already exists
        if username_already_exists:
            error = "Username already exists."

        if not error:
            # Add new user to the database
            db.execute("INSERT INTO users (username, password)"
                       "VALUES (?, ?)",
                       (username, generate_password_hash(str(password))))
            db.commit()

            # Redirect users to the login page
            return redirect(url_for("routes.login"))

        else:
            flash(error)
            return redirect(url_for("routes.register"))

    else:
        return render_template("register.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
                ).fetchone()
