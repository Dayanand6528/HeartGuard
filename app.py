import os
import re
import time
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, query_db, execute_db, get_driver_status
from chatbot_engine import get_bot_response

# Auto-load .env file if present
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
    except Exception as e:
        print(f"[ENV Warning] Could not load .env file: {e}")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'heartguard_secure_key_2026_x893k_protection_v2')

# Security Cookie & Session Hardening against Session Fixation & Hijacking
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# Brute-force Login Protection Tracker: { email: { "attempts": count, "lockout_until": timestamp } }
LOGIN_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes lockout

# Email Configuration Settings for Contact Form Dispatch
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'randomji5555@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', 'randomji5555@gmail.com')

def send_contact_email(sender_name, sender_email, subject, message_body):
    """Dispatches contact form submission as a self-notification email via SMTP."""
    target_dest = RECEIVER_EMAIL or 'randomji5555@gmail.com'
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"[SMTP Notice] SENDER_PASSWORD not set. Contact inquiry from {sender_email} saved to database only.")
        return False, "SENDER_PASSWORD not configured"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📌 Self Message: HeartGuard Inquiry from {sender_name} - {subject}"
        msg['From'] = f"HeartGuard Self-Notifier <{SENDER_EMAIL}>"
        msg['To'] = target_dest
        msg['Reply-To'] = sender_email

        text_content = f"""
📌 Self Message / HeartGuard System Notification

You received a new inquiry on your HeartGuard website:

• Visitor Name: {sender_name}
• Visitor Email: {sender_email}
• Subject: {subject}

Message Content:
{message_body}

---
Sent to yourself ({target_dest}) from HeartGuard System.
"""

        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; max-width: 600px; border: 1px solid #00f0ff; border-radius: 10px; background: #0a1128;">
            <h2 style="color: #00f0ff; margin-top: 0;">📌 Self Message: HeartGuard Inquiry</h2>
            <p style="color: #ffffff; font-size: 0.95rem;">You received a new inquiry on your website:</p>
            <div style="background: rgba(0, 240, 255, 0.08); padding: 15px; border-radius: 8px; border-left: 4px solid #00f0ff; margin: 15px 0;">
                <p style="color: #ffffff; margin: 0 0 8px 0;"><strong>👤 Visitor Name:</strong> {sender_name}</p>
                <p style="color: #ffffff; margin: 0 0 8px 0;"><strong>✉️ Visitor Email:</strong> <a href="mailto:{sender_email}" style="color: #00f0ff;">{sender_email}</a></p>
                <p style="color: #ffffff; margin: 0;"><strong>📝 Subject:</strong> {subject}</p>
            </div>
            <p style="color: #ffffff;"><strong>Message Content:</strong></p>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; color: #e2e8f0; white-space: pre-wrap; font-size: 0.95rem;">{message_body}</div>
            <hr style="border: 0; border-top: 1px solid #1f293d; margin-top: 20px;">
            <p style="font-size: 0.85em; color: #94a3b8;">This is a self-notification sent to {target_dest}. Click 'Reply' in your email client to respond directly to {sender_email}.</p>
        </div>
        """

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [target_dest], msg.as_string())

        print(f"[SMTP Self-Message Success] Email dispatched to {target_dest}")
        return True, "Self-message email sent successfully"
    except Exception as e:
        print(f"[SMTP Error] Failed to send email: {e}")
        return False, str(e)

# Initialize DB on start
init_db()

# Load ML Model & Scaler
MODEL_PATH = os.path.join('models', 'model.pkl')
SCALER_PATH = os.path.join('models', 'scaler.pkl')

ml_model = None
ml_scaler = None

def load_ml_resources():
    global ml_model, ml_scaler
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                ml_model = pickle.load(f)
            with open(SCALER_PATH, 'rb') as f:
                ml_scaler = pickle.load(f)
            print("[ML Engine] Model and Scaler loaded successfully.")
        except Exception as e:
            print(f"[ML Engine Error]: {e}")

load_ml_resources()

# Security Middleware: Inject Security Headers to block Clickjacking, XSS, and MIME-sniffing
@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com;"
    return response

# Helper decorator / session checks
def get_current_user():
    if 'user_id' in session:
        return query_db("SELECT id, name, email, role, phone FROM users WHERE id = %s", (session['user_id'],), fetchone=True)
    return None

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user(), db_status=get_driver_status())

# Page Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/technologies')
def technologies():
    return render_template('technologies.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash("Please fill in all required fields.", "danger")
        else:
            execute_db("""
                INSERT INTO contact_messages (name, email, subject, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, subject or 'General Inquiry', message))

            # Send real email notification via SMTP
            sent, info = send_contact_email(name, email, subject or 'General Inquiry', message)
            if sent:
                flash("Thank you! Your message has been sent successfully and emailed to our team.", "success")
            else:
                flash("Thank you! Your message has been saved successfully in our system.", "success")

            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/chatbot')
def dedicated_chatbot():
    return render_template('chatbot.html')

# Authentication Routes with Brute-Force & Identity Theft Safeguards
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        now = time.time()

        # Check if account is currently locked due to repeated failed login attempts
        user_attempts = LOGIN_ATTEMPTS.get(email, {})
        lockout_until = user_attempts.get('lockout_until', 0)

        if now < lockout_until:
            remaining_mins = int((lockout_until - now) / 60) + 1
            flash(f"🚨 Security Alert: Account temporarily locked due to repeated failed attempts to prevent Identity Theft. Try again in {remaining_mins} minutes.", "danger")
            return render_template('login.html')

        user = query_db("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)

        if user and check_password_hash(user['password'], password):
            # Reset failed attempts on success
            LOGIN_ATTEMPTS.pop(email, None)

            # Prevent Session Fixation attacks: regenerate session completely
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']

            flash(f"Welcome back, {user['name']}! Secure login verified as {user['role'].capitalize()}.", "success")
            return redirect(url_for('dashboard'))

        # Track failed attempt
        attempts = user_attempts.get('attempts', 0) + 1
        if attempts >= MAX_FAILED_ATTEMPTS:
            LOGIN_ATTEMPTS[email] = {'attempts': attempts, 'lockout_until': now + LOCKOUT_DURATION_SECONDS}
            flash("🚨 Security Lockout Triggered: 5 consecutive failed login attempts detected. Account locked for 15 minutes to prevent unauthorized access.", "danger")
        else:
            LOGIN_ATTEMPTS[email] = {'attempts': attempts, 'lockout_until': 0}
            remaining = MAX_FAILED_ATTEMPTS - attempts
            flash(f"Invalid email or password. {remaining} attempt(s) remaining before security lockout.", "danger")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'patient')
        phone = request.form.get('phone', '').strip()

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
        # Password Strength Policy Enforcement
        elif len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            flash("Security Requirement: Password must be at least 8 characters long and contain both letters and numbers to protect your identity.", "warning")
        else:
            existing = query_db("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
            if existing:
                flash("An account with this email already exists. Please login instead.", "warning")
            else:
                pw_hash = generate_password_hash(password)
                user_id = execute_db("""
                    INSERT INTO users (name, email, password, role, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, email, pw_hash, role, phone))

                # Prevent Session Fixation: clear prior session
                session.clear()
                session.permanent = True
                session['user_id'] = user_id
                session['user_name'] = name
                session['user_role'] = role

                flash(f"Account created securely! Welcome to HeartGuard, {name}.", "success")
                return redirect(url_for('dashboard'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out securely.", "info")
    return redirect(url_for('home'))

# Role-based Dashboard Router
@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        flash("Please login to access your dashboard.", "warning")
        return redirect(url_for('login'))

    role = user['role']
    if role == 'doctor':
        # Doctor views all patient records and filter options
        records = query_db("SELECT * FROM prediction_records ORDER BY created_at DESC")
        high_risk_count = sum(1 for r in records if r['prediction'] == 1)
        return render_template('dashboard_doctor.html', user=user, records=records, high_risk_count=high_risk_count)

    elif role == 'admin':
        # Admin views system metrics, all users, all predictions, contact messages
        users = query_db("SELECT id, name, email, role, phone, created_at FROM users ORDER BY created_at DESC")
        records = query_db("SELECT * FROM prediction_records ORDER BY created_at DESC")
        messages = query_db("SELECT * FROM contact_messages ORDER BY created_at DESC")
        chat_count = query_db("SELECT COUNT(*) as cnt FROM chat_logs", fetchone=True)

        return render_template('dashboard_admin.html',
                               user=user,
                               users=users,
                               records=records,
                               messages=messages,
                               chat_count=chat_count['cnt'] if chat_count else 0,
                               db_status=get_driver_status())

    else: # Patient
        # Patient views their own past prediction records
        records = query_db("SELECT * FROM prediction_records WHERE patient_id = %s ORDER BY created_at DESC", (user['id'],))
        return render_template('dashboard_patient.html', user=user, records=records)

# REST API Endpoints
@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json() or {}

    try:
        age = int(data.get('age', 50))
        sex = int(data.get('sex', 1))
        cp = int(data.get('cp', 0))
        trestbps = int(data.get('trestbps', 120))
        chol = int(data.get('chol', 200))
        fbs = int(data.get('fbs', 0))
        restecg = int(data.get('restecg', 0))
        thalach = int(data.get('thalach', 150))
        exang = int(data.get('exang', 0))
        oldpeak = float(data.get('oldpeak', 0.0))
        slope = int(data.get('slope', 1))
        ca = int(data.get('ca', 0))
        thal = int(data.get('thal', 2))

        # Check ML model availability
        if ml_model is None or ml_scaler is None:
            load_ml_resources()

        if ml_model is None or ml_scaler is None:
            # Emergency fallback model calculation if pickle file not generated yet
            risk_score = (
                (age > 55) * 1.5 + (cp > 0) * 2.5 + (trestbps > 140) * 1.5 +
                (chol > 240) * 1.2 + (thalach < 130) * 1.8 + (exang == 1) * 2.0 +
                (oldpeak > 1.5) * 2.0 + (ca > 0) * 2.0
            )
            prob = float(1 / (1 + np.exp(-(risk_score - 6.0))))
            prediction = 1 if prob >= 0.5 else 0
        else:
            import pandas as pd
            feature_cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            features_df = pd.DataFrame([[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]], columns=feature_cols)
            scaled_features = ml_scaler.transform(features_df)
            prob = float(ml_model.predict_proba(scaled_features)[0][1])
            prediction = int(ml_model.predict(scaled_features)[0])

        risk_percentage = round(prob * 100, 1)

        if risk_percentage >= 70:
            risk_level = "Critical High Risk"
        elif risk_percentage >= 45:
            risk_level = "Moderate High Risk"
        elif risk_percentage >= 25:
            risk_level = "Mild Risk"
        else:
            risk_level = "Low Risk"

        # Patient & Doctor Info
        user = get_current_user()
        patient_id = user['id'] if user else None
        patient_name = user['name'] if user else data.get('patient_name', 'Guest Patient')

        # Save to database
        record_id = execute_db("""
            INSERT INTO prediction_records
            (patient_id, patient_name, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, prediction, risk_percentage, risk_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, patient_name, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, prediction, risk_percentage, risk_level))

        # Recommendations list
        recommendations = []
        if trestbps >= 140:
            recommendations.append("Resting Blood Pressure is elevated. Reduce dietary sodium and monitor daily.")
        if chol >= 240:
            recommendations.append("Serum cholesterol is high. Limit saturated fats and consult a nutritionist for a lipid-lowering plan.")
        if thalach < 120 and age < 60:
            recommendations.append("Maximum achieved heart rate is relatively low. Cardiorespiratory endurance evaluation recommended.")
        if exang == 1:
            recommendations.append("Exercise induced angina detected. Avoid heavy exertion until cleared by a cardiologist.")
        if oldpeak >= 1.5:
            recommendations.append("ST depression noted on ECG. Diagnostic stress ECG or echocardiogram suggested.")
        if not recommendations:
            recommendations.append("Cardiovascular biomarkers are in healthy range. Maintain regular balanced diet and physical activity.")

        return jsonify({
            'success': True,
            'record_id': record_id,
            'patient_name': patient_name,
            'prediction': prediction,
            'risk_percentage': risk_percentage,
            'risk_level': risk_level,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'response': 'Please type a valid question.'})

    user = get_current_user()
    user_id = user['id'] if user else None

    bot_reply = get_bot_response(message)

    # Log chat
    try:
        execute_db("""
            INSERT INTO chat_logs (user_id, user_message, bot_response)
            VALUES (%s, %s, %s)
        """, (user_id, message, bot_reply))
    except Exception:
        pass

    return jsonify({'response': bot_reply})

@app.route('/api/doctor/notes', methods=['POST'])
def api_doctor_notes():
    user = get_current_user()
    if not user or user['role'] not in ['doctor', 'admin']:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

    data = request.get_json() or {}
    record_id = data.get('record_id')
    notes = data.get('notes', '').strip()

    if not record_id or not notes:
        return jsonify({'success': False, 'error': 'Missing record ID or consultation notes'}), 400

    execute_db("""
        UPDATE prediction_records
        SET doctor_notes = %s, doctor_name = %s
        WHERE id = %s
    """, (notes, user['name'], record_id))

    return jsonify({'success': True, 'message': 'Doctor clinical consultation note saved successfully.'})

@app.route('/api/admin/users/role', methods=['POST'])
def api_update_user_role():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Admin privileges required'}), 403

    data = request.get_json() or {}
    target_user_id = data.get('user_id')
    new_role = data.get('role')

    if new_role not in ['patient', 'doctor', 'admin']:
        return jsonify({'success': False, 'error': 'Invalid role specified'}), 400

    execute_db("UPDATE users SET role = %s WHERE id = %s", (new_role, target_user_id))
    return jsonify({'success': True, 'message': f'User role updated to {new_role}.'})

if __name__ == '__main__':
    print("Starting HeartGuard Flask Server with SMTP Email Integration & .env auto-loader...")
    app.run(host='0.0.0.0', port=5000, debug=True)
