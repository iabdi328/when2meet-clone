import sqlite3
import os
from flask import g

DB_NAME = "schedule.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row

        try:
            g.db.execute("SELECT 1 FROM users LIMIT 1")
        except sqlite3.OperationalError:
            sql_path = os.path.join(os.path.dirname(__file__), "users.sql")
            with open(sql_path, "r") as f:
                g.db.executescript(f.read())
                g.db.commit()
                
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
