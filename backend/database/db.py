"""
db.py
-----
SQLite database setup and connection helper for CareerCopilot AI.

Tables:
  users(id, username, password_hash, name, email, college, branch)
  resumes(id, user_id, resume_score, file_path, parsed_profile_json)
  reports(id, user_id, report_path)
  history(id, user_id, action, timestamp)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "careercopilot.db")


def get_connection():
    """Open a new SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all required tables if they don't already exist, and add any
    columns older databases may be missing (lightweight migration)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            name TEXT,
            email TEXT,
            college TEXT,
            branch TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            resume_score INTEGER,
            file_path TEXT,
            parsed_profile_json TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Lightweight migration for databases created by an older version of this app
    existing_user_cols = {row[1] for row in cur.execute("PRAGMA table_info(users)")}
    for col, ddl in [
        ("username", "ALTER TABLE users ADD COLUMN username TEXT"),
        ("password_hash", "ALTER TABLE users ADD COLUMN password_hash TEXT"),
        ("email", "ALTER TABLE users ADD COLUMN email TEXT"),
    ]:
        if col not in existing_user_cols:
            cur.execute(ddl)

    existing_resume_cols = {row[1] for row in cur.execute("PRAGMA table_info(resumes)")}
    if "parsed_profile_json" not in existing_resume_cols:
        cur.execute("ALTER TABLE resumes ADD COLUMN parsed_profile_json TEXT")

    conn.commit()
    conn.close()
