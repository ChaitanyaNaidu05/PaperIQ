import sqlite3
import json
import logging

DB_PATH = "data/paperiq.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
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
            salt TEXT,
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
    try:
        c.execute('ALTER TABLE analysis_history ADD COLUMN results_json TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE analysis_history ADD COLUMN file_path TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def create_user(username, email, password_hash, salt):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, salt)
        )
        conn.commit()
        logger.info(f"User created: {username}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"User creation failed - already exists: {username}")
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


def get_user_by_id(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def save_analysis(user_id, filename, sections_count, keywords, sections_data, results_data, file_path=None):
    conn = get_db_connection()
    c = conn.cursor()
    keywords_json = json.dumps(keywords)
    sections_json = json.dumps(sections_data)
    results_json = json.dumps(results_data)
    c.execute('''
        INSERT INTO analysis_history (user_id, filename, sections_count, keywords_json, sections_json, results_json, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, filename, sections_count, keywords_json, sections_json, results_json, file_path))
    conn.commit()
    conn.close()
    logger.info(f"Analysis saved: {filename} for user {user_id}")


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
