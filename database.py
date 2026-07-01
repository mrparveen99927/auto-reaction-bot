import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            access_id TEXT PRIMARY KEY,
            password TEXT,
            group_id INTEGER UNIQUE,
            expiry_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    conn.commit()
    conn.close()

def generate_user_credentials(access_id, password, days=30):
    conn = sqlite3.connect("bot_users.db")
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
    conn = sqlite3.connect("bot_users.db")
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
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE group_id = ? AND status = 'active'", (group_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        if datetime.now() < datetime.strptime(result, '%Y-%m-%d %H:%M:%S'):
            return True
    return False

def get_all_active_users():
    conn = sqlite3.connect("bot_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT access_id, password, expiry_date, group_id FROM users WHERE status = 'active'")
    rows = cursor.fetchall()
    conn.close()
    
    user_list = []
    for row in rows:
        access_id, password, expiry_date, group_id = row
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
        remaining = expiry - datetime.now()
        
        if remaining.total_seconds() > 0:
            days = remaining.days
            hours = remaining.seconds // 3600
            time_left = f"{days} दिन, {hours} घंटे"
            user_list.append({
                "id": access_id,
                "pass": password,
                "time": time_left,
                "group": group_id if group_id else "लिंक नहीं है"
            })
    return user_list

init_db()
