import sqlite3


def get_db():
    db = sqlite3.connect("mydatabase.db")
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
                     "author_id INTEGER NOT NULL,"
                     "created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                     "title TEXT NOT NULL,"
                     "body TEXT NOT NULL"
                     ");"
                     )
    db.commit()
