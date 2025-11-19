# db.py
import sqlite3
from typing import List, Tuple

DB = "randomizer.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        status TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def add_participant(user_id:int, username:str, first_name:str, status:str="member"):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO participants (user_id, username, first_name, status) VALUES (?, ?, ?, ?)",
                (user_id, username or "", first_name or "", status))
    conn.commit()
    conn.close()

def remove_participant(user_id:int):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM participants WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def list_participants() -> List[Tuple]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, first_name, joined_at FROM participants")
    rows = cur.fetchall()
    conn.close()
    return rows

def count_participants() -> int:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM participants")
    n = cur.fetchone()[0]
    conn.close()
    return n
