# database.py
import sqlite3
from datetime import datetime, timedelta
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # यहाँ chat_id का नया कॉलम जोड़ा गया है ब्रॉडकास्ट के लिए
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        access_id TEXT PRIMARY KEY,
        password TEXT,
        group_id INTEGER UNIQUE,
        expiry_date TEXT,
        status TEXT DEFAULT 'active',
        chat_id INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def save_chat_id(access_id, chat_id):
    """यूजर की पर्सनल चैट आईडी अपडेट करने के लिए"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET chat_id = ? WHERE access_id = ?", (chat_id, access_id))
    conn.commit()
    conn.close()

def generate_user_credentials(access_id, password, days=30):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('''
        INSERT INTO users (access_id, password, expiry_date, status)
        VALUES (?, ?, ?, 'active')
        ON CONFLICT(access_id) DO UPDATE SET
        password=excluded.password,
        expiry_date=excluded.expiry_date,
        status='active'
        ''', (access_id, password, expiry))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def login_and_lock_group(access_id, password, group_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT expiry_date, group_id FROM users WHERE access_id = ? AND password = ? AND status = 'active'",
        (access_id, password)
    )
    result = cursor.fetchone()
    if not result:
        conn.close()
        return "invalid"
    
    expiry_date, locked_group = result
    if datetime.now() > datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S'):
        conn.close()
        return "expired"
    
    if locked_group is None:
        try:
            cursor.execute("UPDATE users SET group_id = ? WHERE access_id = ?", (group_id, access_id))
            conn.commit()
            conn.close()
            return "success"
        except sqlite3.IntegrityError:
            conn.close()
            return "group_already_used"
    elif locked_group == group_id:
        conn.close()
        return "success"
    else:
        conn.close()
        return "wrong_group"

def is_group_allowed(group_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE group_id = ? AND status = 'active'", (group_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        if datetime.now() < datetime.strptime(result, '%Y-%m-%d %H:%M:%S'):
            return True
    return False
    