import sqlite3

DATABASE = 'users.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            bought_tokens INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def upsert_user(user_id: int, username: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, username) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username
    ''', (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_bought_tokens(user_id: int, amount: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET bought_tokens = bought_tokens + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()
