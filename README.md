# 🫀 HeartGuard - Heart Attack Risk Detection & Medical Management System

**HeartGuard** is an advanced full-stack medical intelligence web application built with **Python Flask**, **Scikit-Learn Machine Learning**, **100% Offline SQLite Database**, and a **Dedicated Medical AI Assistant**.

---

## 🌟 Key Features

1. **Heart Attack Risk Calculator**:
   - Evaluates 14 clinical report parameters (Age, Sex, Chest Pain Type, Resting BP, Serum Cholesterol, Fasting Blood Sugar, Resting ECG, Max Heart Rate, Exercise Angina, ST Depression, ST Slope, Major Vessels, and Thalassemia).
   - Generates instant risk percentage scores and clinical risk stratification (Low Risk, Mild Risk, Moderate High Risk, Critical High Risk) with actionable recommendations.

2. **100% Offline SQLite Database**:
   - Uses Python's built-in `sqlite3` database engine (`heartguard.db`).
   - Requires **zero external database installation or setup** (no MySQL or XAMPP needed). Auto-creates schema and seeds default accounts on first run.

3. **Dedicated Medical AI Chatbot**:
   - Programmed strictly for medical, cardiology, clinical biomarker, and health questions.
   - **Strict Domain Boundary**: Automatically refuses non-medical requests (such as coding, sports, movies, or general trivia).
   - **Clean Text Output**: Displays clean, unformatted plain-text responses with zero asterisks (`*`).

4. **Contact Form Self-Message SMTP Integration**:
   - Automatically dispatches incoming contact form submissions as HTML **Self-Notifications** directly to `randomji5555@gmail.com`.
   - Includes 1-click **Reply-To** header so replying in your email client sends a response directly back to the visitor.

5. **Security & Identity Protection**:
   - **Brute-Force Lockout**: 5 failed login attempts trigger a 15-minute security lockout.
   - **Password Complexity**: Enforces a minimum of 8 characters with letters and numbers.
   - **Session Hardening**: HTTP-Only cookies, SameSite protections, and session fixation prevention.

6. **3-Role Access Portals**:
   - **Patient Portal**: Submit reports, view personal risk history, and read doctor consultation notes.
   - **Doctor Portal**: Triage patient records, filter high-risk cases, and save clinical consultation notes (clean numerical serial IDs without `#` symbols).
   - **Admin Portal**: Account role management (Patient/Doctor/Admin), system database status, and contact inquiry logs.

---

## 📁 Project Directory Structure

```
HeartGuard final year project/
├── app.py                  # Main Flask application server, REST APIs, & SMTP handler
├── database.py             # 100% Offline SQLite database manager & auto-seeder
├── chatbot_engine.py       # Offline Medical AI chatbot engine with strict domain bounds
├── train_model.py          # Machine Learning training script (Random Forest Classifier)
├── medical_db.json         # Medical knowledge reference dictionary
├── heartguard.db           # Local SQLite database file
├── schema.sql              # Clean SQLite DDL schema script
├── .env                    # Environment configuration (SMTP email credentials)
├── .env.example            # Environment template file
├── requirements.txt        # Python package dependencies
├── README.md               # Complete project documentation & guide
├── dataset/
│   └── heart.csv           # Kaggle UCI Heart Disease dataset
├── models/
│   ├── model.pkl           # Trained Random Forest model file
│   └── scaler.pkl          # Feature StandardScaler pickle file
├── static/
│   ├── css/
│   │   └── style.css       # Custom Glassmorphism medical CSS design system
│   └── js/
│       └── main.js         # Interactive client logic, AJAX handlers, & chatbot bindings
└── templates/
    ├── base.html           # Master layout header, navbar, floating chatbot, & footer
    ├── index.html          # Home page & Heart Attack Risk Calculator
    ├── about.html          # Clinical parameter dictionary & project mission
    ├── technologies.html   # System architecture & technology stack breakdown
    ├── contact.html        # Contact form & emergency hotline information
    ├── chatbot.html        # Dedicated Medical AI Console
    ├── login.html          # Secure login portal with role selector
    ├── signup.html         # User account registration form
    ├── dashboard_patient.html # Patient portal (personal risk history & notes)
    ├── dashboard_doctor.html  # Doctor portal (patient triage & advice editor)
    └── dashboard_admin.html   # Admin portal (user management & database logs)
```

---

## ⚡ Quick Setup & Installation

### Step 1: Install Python Dependencies
Open terminal or command prompt in the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Contact Email Settings (`.env`)
The project auto-loads settings from `.env`. Open or edit `.env` in the project root:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

SENDER_EMAIL=randomji5555@gmail.com
SENDER_PASSWORD=your_16_character_app_password
RECEIVER_EMAIL=randomji5555@gmail.com
```

*(For Gmail: Generate a 16-character App Password at [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and paste it into `SENDER_PASSWORD`).*

---

## 🚀 Running the Server

Start the HeartGuard server by running:
```bash
python app.py
```

Open your browser and navigate to: **`http://localhost:5000`**

---

## 🔐 Default Demo Accounts

| Role | Demo Email | Demo Password | Purpose |
|---|---|---|---|
| 🧑‍🦱 **Patient** | `patient@heartguard.com` | `patient123` | Submit health reports, view risk history & doctor notes |
| 🩺 **Doctor** | `doctor@heartguard.com` | `doctor123` | Patient triage dashboard, save consultation notes |
| 🛡️ **Admin** | `admin@heartguard.com` | `admin123` | System management, change user roles, view message logs |

---

## 🧪 Testing & Verification

Run the integration test suite to verify all routes, APIs, authentication, and database queries:
```bash
python test_app.py
```
