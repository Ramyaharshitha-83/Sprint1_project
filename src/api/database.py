import sqlite3

DB_PATH = "data/nifty100.db"


def get_connection():
    """
    Return SQLite database connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn