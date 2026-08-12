-- HeartGuard 100% Offline SQLite Database Schema
-- File: heartguard.db

-- 1. Users Table (Patients, Doctors, Admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'patient',
    phone TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Heart Attack Risk Prediction Records Table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. Contact Messages Table
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Chatbot Interaction Logs Table
CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
