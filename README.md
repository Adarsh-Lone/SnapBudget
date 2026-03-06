#VICSTA Hackathon-Grand finale
VIT College, Kondhwa Campus|5th-6th March 

Team Details

Team Name: DigiSurfurs

Members: 
  1. Gayatri Aiwale
  2. Aditya Ambhore
  3. Radhika Anchawale
  4. Adarsh Lone


Project

problem:

SnapBudget OCR
Most people stop using money trackers because manual entry is hard. Build a "Simple Money Tracker" that uses OCR to scan physical receipts and automatically categorizes spending with 99% accuracy.

Solution:

SnapBudget OCR is a smart financial management system that automatically tracks user expenses by extracting transaction data from receipts using OCR and parsing debit SMS messages. The system analyzes spending patterns using data analytics to detect unusual spending acceleration and predict potential financial stress before it occurs. By comparing previous and current spending rates, it forecasts how long a user’s balance will last and provides early alerts through an interactive dashboard. This eliminates manual expense tracking, improves financial awareness, and helps users make better budgeting decisions.

## SnapBudget OCR+ : Intelligent Passive Expense Tracker

SnapBudget OCR+ is a hackathon-ready MVP that passively tracks expenses from:
- **Receipt images** (JPG/PNG) using **Tesseract OCR**
- **Debit SMS text** using a simple rule-based parser

It stores transactions in **MySQL**, runs analytics (NumPy / Pandas), and exposes a **Flask REST API** plus a simple dashboard for demo purposes.

### Tech Stack
- **Backend**: Flask (Python)
- **DB**: MySQL
- **OCR**: Tesseract OCR via `pytesseract`
- **Analytics**: NumPy, Pandas
- **Frontend**: Minimal React dashboard (with a plain HTML fallback page)

---

## 1. Folder Structure

```text
snapbudget_OCR/
  backend/
    app.py
    config.py
    extensions.py
    models.py
    routes/
      __init__.py
      transactions.py
      analytics.py
    services/
      __init__.py
      ocr_service.py
      sms_parser.py
      categorizer.py
      recurrence_detector.py
      analytics_engine.py
    tests/
      __init__.py
      sample_data.py
  frontend/
    public/
      index.html
    src/
      index.js
      App.js
      components/
        Dashboard.js
        TransactionsTable.js
    package.json
  db/
    schema.sql
    seed.sql
  requirements.txt
```

---

## 2. Database Schema (MySQL)

The main entities are `users`, `accounts`, and `transactions`. See `db/schema.sql` for full DDL.

- **users**
  - `id`, `name`, `email`
- **accounts**
  - `id`, `user_id`, `bank_name`, `account_number_last4`, `current_balance`
- **transactions**
  - `id`, `user_id`, `account_id`, `source_type` (`RECEIPT` / `SMS`),
  - `raw_text`, `merchant`, `amount`, `currency`,
  - `transaction_date`, `category`, `is_recurring`, `created_at`

---

## 3. Running Locally

### 3.1 Prerequisites
- Python 3.10+ recommended
- Node.js 18+ (for React dashboard)
- MySQL 8+
- Tesseract OCR installed on system:
  - On Windows you can install from `https://github.com/UB-Mannheim/tesseract/wiki`
  - Note the Tesseract executable path (e.g. `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`)

### 3.2 Set up Python backend

```bash
cd C:\Users\kanch\OneDrive\Desktop\HACKATHON\snapbudget_OCR
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables (use PowerShell syntax):

```powershell
$env:FLASK_ENV = "development"
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_NAME = "snapbudget"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your_password"
# Optional: path to Tesseract binary on Windows
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 3.3 Set up MySQL

Create database and tables:

```bash
cd C:\Users\kanch\OneDrive\Desktop\HACKATHON\snapbudget_OCR\db
mysql -u root -p < schema.sql
mysql -u root -p snapbudget < seed.sql
```

### 3.4 Run backend API

```bash
cd C:\Users\kanch\OneDrive\Desktop\HACKATHON\snapbudget_OCR\backend
venv\Scripts\activate
python app.py
```

API will run at `http://localhost:5000`.

### 3.5 Run React dashboard (optional)

```bash
cd C:\Users\kanch\OneDrive\Desktop\HACKATHON\snapbudget_OCR\frontend
npm install
npm start
```

React dev server will be at `http://localhost:3000`, talking to backend at `http://localhost:5000`.

For a no-Node fallback, open `frontend/public/index.html` in a browser and interact with API via simple HTML.

---

## 4. API Overview

- **POST** `/api/transactions/upload-receipt`
  - Multipart upload with `file` (JPG/PNG).
  - Extracts `amount`, `date`, `merchant` via OCR and saves a transaction.
- **POST** `/api/transactions/parse-sms`
  - JSON body: `{ "text": "Your debit card 1234 used at AMAZON for INR 1,234.00 on 03-03-2026" }`
  - Parses amount, bank name, merchant, date.
- **GET** `/api/analytics/summary?user_id=1`
  - Returns snapshot: avg daily spend, volatility, burn rate, survival days, behavior tag.
- **GET** `/api/analytics/monthly-compare?user_id=1`
  - Compares current vs previous month.
- **GET** `/api/transactions?user_id=1`
  - List of recent transactions.

Detailed sample JSON responses are included in comments inside `routes/transactions.py` and `routes/analytics.py`.

---

## 5. Hackathon Demo Flow

1. Use `/api/transactions/parse-sms` with a few sample SMS strings (or the pre-seeded data).
2. Upload a sample receipt image using `/api/transactions/upload-receipt`.
3. Open the dashboard:
   - Show transactions table.
   - Show analytics summary (avg daily spend, volatility, burn rate, survival days).
   - Show behavior tag (Impulse Spender, Stable Planner, Subscription Heavy, Risk Prone).
4. Show how projecting same spending rate predicts a **financial stress date**.

This is intentionally simple, rule-based, and transparent to be hackathon-ready and easy to extend.