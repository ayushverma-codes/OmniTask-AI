import sqlite3
from pathlib import Path

DB_PATH = Path("artifact/chat_state.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            text TEXT,
            file_path TEXT
        )
        """)
        conn.commit()


def save_message(thread_id: str, text: str, file_path: str | None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (thread_id, text, file_path) VALUES (?, ?, ?)",
            (thread_id, text, file_path)
        )
        conn.commit()
