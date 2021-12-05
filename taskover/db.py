import sqlite3

import click
from flask import current_app
from flask.cli import with_appcontext


def get_db():
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row

    return db


def init_db():
    db = get_db()

    db.executescript(
                     "CREATE TABLE IF NOT EXISTS users ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "username TEXT UNIQUE NOT NULL,"
                     "password TEXT NOT NULL"
                     ");"
                     ""
                     "CREATE TABLE IF NOT EXISTS tasks ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_id INTEGER NOT NULL,"
                     "task_order INTEGER NOT NULL,"
                     "created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                     "title TEXT NOT NULL,"
                     "body TEXT NOT NULL,"
                     "is_completed INTEGER NOT NULL DEFAULT 0"
                     ");"
                     )
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)
