import os
import sqlite3
from werkzeug.security import generate_password_hash

SQLITE_FILE = os.path.join(os.path.dirname(__file__), 'heartguard.db')
CURRENT_DRIVER = "SQLite (100% Offline)"

def get_db():
    conn = sqlite3.connect(SQLITE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print(f"[Database] Initializing 100% Offline SQLite database at: {SQLITE_FILE}")
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient',
            phone TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Prediction Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER DEFAULT NULL,
            patient_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex INTEGER NOT NULL,
            cp INTEGER NOT NULL,
            trestbps INTEGER NOT NULL,
            chol INTEGER NOT NULL,
            fbs INTEGER NOT NULL,
            restecg INTEGER NOT NULL,
            thalach INTEGER NOT NULL,
            exang INTEGER NOT NULL,
            oldpeak REAL NOT NULL,
            slope INTEGER NOT NULL,
            ca INTEGER NOT NULL,
            thal INTEGER NOT NULL,
            prediction INTEGER NOT NULL,
            risk_percentage REAL NOT NULL,
            risk_level TEXT NOT NULL,
            doctor_notes TEXT DEFAULT NULL,
            doctor_name TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Contact Messages Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Chat Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

    seed_default_users()

def seed_default_users():
    admin_pw = generate_password_hash('admin123')
    doctor_pw = generate_password_hash('doctor123')
    patient_pw = generate_password_hash('patient123')

    users_to_seed = [
        ('System Administrator', 'admin@heartguard.com', admin_pw, 'admin', '+18005550199'),
        ('Dr. Sarah Jenkins MD', 'doctor@heartguard.com', doctor_pw, 'doctor', '+18005550188'),
        ('John Doe', 'patient@heartguard.com', patient_pw, 'patient', '+18005550177')
    ]

    for name, email, pw, role, phone in users_to_seed:
        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
        if not existing:
            execute_db("""
                INSERT INTO users (name, email, password, role, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, pw, role, phone))

def execute_db(query, params=()):
    conn = get_db()
    try:
        cursor = conn.cursor()
        clean_query = query.replace('%s', '?')
        cursor.execute(clean_query, params)
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id
    except Exception as e:
        err_msg = str(e).lower()
        if "no such table" in err_msg:
            print("[Database] Table missing detected, initializing SQLite database...")
            init_db()
            conn = get_db()
            cursor = conn.cursor()
            clean_query = query.replace('%s', '?')
            cursor.execute(clean_query, params)
            conn.commit()
            inserted_id = cursor.lastrowid
            conn.close()
            return inserted_id
        print(f"[SQLite Execute Error]: {e}")
        if conn:
            conn.close()
        raise e

def query_db(query, params=(), fetchone=False):
    conn = get_db()
    try:
        cursor = conn.cursor()
        clean_query = query.replace('%s', '?')
        cursor.execute(clean_query, params)
        raw_res = cursor.fetchone() if fetchone else cursor.fetchall()
        conn.close()
        if raw_res is None:
            return None
        if fetchone:
            return dict(raw_res)
        return [dict(r) for r in raw_res]
    except Exception as e:
        err_msg = str(e).lower()
        if "no such table" in err_msg:
            print("[Database] Table missing detected, initializing SQLite database...")
            init_db()
            conn = get_db()
            cursor = conn.cursor()
            clean_query = query.replace('%s', '?')
            cursor.execute(clean_query, params)
            raw_res = cursor.fetchone() if fetchone else cursor.fetchall()
            conn.close()
            if raw_res is None:
                return None
            if fetchone:
                return dict(raw_res)
            return [dict(r) for r in raw_res]

        print(f"[SQLite Query Error]: {e}")
        if conn:
            conn.close()
        return None if fetchone else []

def get_driver_status():
    return CURRENT_DRIVER
