from flask import (render_template, redirect, url_for,
                   flash, g, request, Blueprint, session)
from werkzeug.security import generate_password_hash, check_password_hash
from taskover.db import get_db


bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    db = get_db()
    breakpoint()

    # Get the list of tasks for the user
    if g.user:
        tasks = db.execute("SELECT title, body FROM tasks WHERE author_id = ?",
                           (session["user_id"],)).fetchall()
    else:
        tasks = {}

    return render_template("index.html", tasks=tasks)


@bp.route("/create-task", methods=("GET", "POST"))
def create_task():
    pass


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
