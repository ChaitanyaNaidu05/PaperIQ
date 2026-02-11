import sqlite3
import datetime
import json

DB_NAME = "paperiq.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sections_count INTEGER,
            keywords_json TEXT,
            sections_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, email, password_hash, salt):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def save_analysis(user_id, filename, sections_count, keywords, sections_data):
    conn = get_db_connection()
    c = conn.cursor()
    
    keywords_json = json.dumps(keywords)
    sections_json = json.dumps(sections_data)
    
    c.execute('''
        INSERT INTO analysis_history (user_id, filename, sections_count, keywords_json, sections_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, filename, sections_count, keywords_json, sections_json))
    
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, filename, upload_time, sections_count, keywords_json 
        FROM analysis_history 
        WHERE user_id = ? 
        ORDER BY upload_time DESC
    ''', (user_id,))
    history = c.fetchall()
    conn.close()
    return history

def get_analysis_details(analysis_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM analysis_history WHERE id = ?', (analysis_id,))
    analysis = c.fetchone()
    conn.close()
    return analysis
