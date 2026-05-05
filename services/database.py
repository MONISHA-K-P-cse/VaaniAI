import sqlite3
import os
import json
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vaani.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            phone TEXT,
            duration TEXT,
            is_active INTEGER,
            score INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            call_id TEXT,
            sender TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_call(call_id: str, customer_name: str, phone: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO calls (id, customer_name, phone, duration, is_active, score) VALUES (?, ?, ?, ?, ?, ?)',
              (call_id, customer_name, phone, "00:00", 1, 5)) # Default score 5
    conn.commit()
    conn.close()

def update_call_status(call_id: str, is_active: bool):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE calls SET is_active = ? WHERE id = ?', (1 if is_active else 0, call_id))
    conn.commit()
    conn.close()

def update_call_score(call_id: str, score: int):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE calls SET score = ? WHERE id = ?', (score, call_id))
    conn.commit()
    conn.close()

def add_message(call_id: str, msg_id: str, sender: str, text: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO messages (id, call_id, sender, text) VALUES (?, ?, ?, ?)',
              (msg_id, call_id, sender, text))
    conn.commit()
    conn.close()

def get_calls():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM calls ORDER BY is_active DESC, rowid DESC')
    rows = c.fetchall()
    conn.close()
    return [{"id": r["id"], "customerName": r["customer_name"], "phone": r["phone"], "duration": r["duration"], "isActive": bool(r["is_active"]), "score": r["score"]} for r in rows]

def get_messages(call_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE call_id = ? ORDER BY timestamp ASC', (call_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r["id"], "sender": r["sender"], "text": r["text"]} for r in rows]

def get_call_by_id(call_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM calls WHERE id = ?', (call_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "customerName": row["customer_name"], "phone": row["phone"], "duration": row["duration"], "isActive": bool(row["is_active"]), "score": row["score"]}
    return None
