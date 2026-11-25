import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db"
)

if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "", 1)
else:
    DB_PATH = "./app.db"

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id
            ON messages(session_id)
        """)


def save_message(session_id, role, content, metadata=None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO messages
            (session_id, role, content, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            role,
            content,
            json.dumps(metadata) if metadata else None,
            datetime.now(timezone.utc).isoformat()
        ))


def get_messages(session_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT role, content, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,)).fetchall()

    messages = []

    for row in rows:
        message = {
            "role": row["role"],
            "content": row["content"]
        }

        if row["metadata"]:
            message["metadata"] = json.loads(row["metadata"])

        messages.append(message)

    return messages