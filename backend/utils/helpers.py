"""
helpers.py
----------
Small shared backend utilities.
"""


def log_action(conn, user_id: int, action: str):
    """Insert a row into the history table so /user_profile can show recent activity."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (user_id, action) VALUES (?, ?)",
        (user_id, action),
    )
    conn.commit()
