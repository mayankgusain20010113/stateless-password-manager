import sqlite3

DB_NAME = "vault.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table: Stores username, hashed master password, and the salt used for key derivation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_salt BLOB NOT NULL
        )
    ''')
    
    # Vault entries: Stores encrypted data, nonce, and service name
    # Note: We do NOT store the key or master password here.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            encrypted_data BLOB NOT NULL,
            nonce BLOB NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password_hash, user_salt):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, user_salt) VALUES (?, ?, ?)",
            (username, password_hash, user_salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_entry(user_id, service_name, encrypted_data, nonce):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vault_entries (user_id, service_name, encrypted_data, nonce) VALUES (?, ?, ?, ?)",
        (user_id, service_name, encrypted_data, nonce)
    )
    conn.commit()
    conn.close()

def get_entries(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vault_entries WHERE user_id = ?", (user_id,))
    entries = cursor.fetchall()
    conn.close()
    return entries

def delete_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()