-- CREATE DATABASE
CREATE DATABASE IF NOT EXISTS snapbudget 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE snapbudget;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ACCOUNTS TABLE
CREATE TABLE IF NOT EXISTS accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  bank_name VARCHAR(100),
  account_number_last4 VARCHAR(4),
  current_balance DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- TRANSACTIONS TABLE
CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  account_id INT NULL,
  source_type ENUM('RECEIPT','SMS') NOT NULL,
  raw_text TEXT,
  merchant VARCHAR(255),
  amount DECIMAL(15,2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'INR',
  transaction_date DATE NOT NULL,
  category VARCHAR(100),
  is_recurring TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_date (user_id, transaction_date),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- PROFILE TABLE (1:1 with users; uses users.id as primary key)
CREATE TABLE IF NOT EXISTS profile (
  id INT PRIMARY KEY,
  income DECIMAL(15,2) DEFAULT 0,
  fixed_expenses TEXT NULL, -- JSON string: [{"name":"Rent","amount":12000}, ...]
  monthly_limit DECIMAL(15,2) DEFAULT 0,
  savings_goal DECIMAL(15,2) DEFAULT 0,
  currency VARCHAR(10) DEFAULT 'INR',
  profile_picture_url VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (id) REFERENCES users(id)
);

-- =========================
-- SEED DATA
-- =========================

INSERT INTO users (name, email) VALUES
('Demo User', 'demo@snapbudget.local')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO accounts (user_id, bank_name, account_number_last4, current_balance)
VALUES
(1, 'HDFC Bank', '1234', 6000.00),
(1, 'ICICI Bank', '5678', 4000.00)
ON DUPLICATE KEY UPDATE current_balance = VALUES(current_balance);

INSERT INTO transactions
(user_id, account_id, source_type, raw_text, merchant, amount, currency, transaction_date, category, is_recurring)
VALUES
(1, 1, 'SMS',
'INR 799.00 spent on HDFC Bank CREDIT Card ending 1234 at NETFLIX.COM on 2026-02-01',
'NETFLIX', 799.00, 'INR', '2026-02-01', 'Subscriptions', 1),

(1, 1, 'SMS',
'INR 299.00 spent on HDFC Bank CREDIT Card ending 1234 at SPOTIFY on 2026-02-05',
'SPOTIFY', 299.00, 'INR', '2026-02-05', 'Subscriptions', 1),

(1, 1, 'SMS',
'INR 1349.50 spent on HDFC Bank CREDIT Card ending 1234 at BIGBAZAAR on 2026-02-10',
'BIGBAZAAR', 1349.50, 'INR', '2026-02-10', 'Groceries', 0),

-- previous week (for insights & burn-rate baseline)
(1, 1, 'SMS',
'INR 320.00 spent on HDFC Bank CREDIT Card ending 1234 at DOMINOS on 2026-02-24',
'DOMINOS', 320.00, 'INR', '2026-02-24', 'Food', 0),
(1, 1, 'SMS',
'INR 180.00 spent on HDFC Bank CREDIT Card ending 1234 at UBER on 2026-02-25',
'UBER', 180.00, 'INR', '2026-02-25', 'Transport', 0),

-- current week (higher spend, to trigger alerts/insights)
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 950.00 at ZOMATO on 2026-03-01',
'ZOMATO', 950.00, 'INR', '2026-03-01', 'Food', 0),

(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 1600.00 at AMAZON on 2026-03-02',
'AMAZON', 1600.00, 'INR', '2026-03-02', 'Shopping', 0),

(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 799.00 at NETFLIX.COM on 2026-03-02',
'NETFLIX', 799.00, 'INR', '2026-03-02', 'Subscriptions', 1),

(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 700.00 at ZOMATO on 2026-03-03',
'ZOMATO', 700.00, 'INR', '2026-03-03', 'Food', 0),

(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 650.00 at UBER on 2026-03-04',
'UBER', 650.00, 'INR', '2026-03-04', 'Transport', 0),

-- additional spread across last 30–45 days
(1, 1, 'SMS',
'INR 220.00 spent on HDFC Bank CREDIT Card ending 1234 at STARBUCKS on 2026-01-25',
'STARBUCKS', 220.00, 'INR', '2026-01-25', 'Food', 0),
(1, 1, 'SMS',
'INR 510.00 spent on HDFC Bank CREDIT Card ending 1234 at BIGBAZAAR on 2026-01-28',
'BIGBAZAAR', 510.00, 'INR', '2026-01-28', 'Groceries', 0),
(1, 1, 'SMS',
'INR 1199.00 spent on HDFC Bank CREDIT Card ending 1234 at SWIGGY on 2026-01-30',
'SWIGGY', 1199.00, 'INR', '2026-01-30', 'Food', 0),
(1, 1, 'SMS',
'INR 430.00 spent on HDFC Bank CREDIT Card ending 1234 at METRO on 2026-02-12',
'METRO', 430.00, 'INR', '2026-02-12', 'Groceries', 0),
(1, 1, 'SMS',
'INR 980.00 spent on HDFC Bank CREDIT Card ending 1234 at PVR on 2026-02-14',
'PVR', 980.00, 'INR', '2026-02-14', 'Entertainment', 0),
(1, 1, 'SMS',
'INR 360.00 spent on HDFC Bank CREDIT Card ending 1234 at BMTC on 2026-02-15',
'BMTC', 360.00, 'INR', '2026-02-15', 'Transport', 0),
(1, 1, 'SMS',
'INR 1500.00 spent on HDFC Bank CREDIT Card ending 1234 at RELIANCE DIGITAL on 2026-02-17',
'RELIANCE DIGITAL', 1500.00, 'INR', '2026-02-17', 'Shopping', 0),
(1, 1, 'SMS',
'INR 275.00 spent on HDFC Bank CREDIT Card ending 1234 at STARBUCKS on 2026-02-18',
'STARBUCKS', 275.00, 'INR', '2026-02-18', 'Food', 0),
(1, 1, 'SMS',
'INR 2100.00 spent on HDFC Bank CREDIT Card ending 1234 at TATASKY on 2026-02-20',
'TATASKY', 2100.00, 'INR', '2026-02-20', 'Utilities', 0),
(1, 1, 'SMS',
'INR 699.00 spent on HDFC Bank CREDIT Card ending 1234 at SPOTIFY on 2026-02-21',
'SPOTIFY', 699.00, 'INR', '2026-02-21', 'Entertainment', 1),
(1, 1, 'SMS',
'INR 350.00 spent on HDFC Bank CREDIT Card ending 1234 at METRO on 2026-02-22',
'METRO', 350.00, 'INR', '2026-02-22', 'Groceries', 0),
(1, 1, 'SMS',
'INR 450.00 spent on HDFC Bank CREDIT Card ending 1234 at BMTC on 2026-02-23',
'BMTC', 450.00, 'INR', '2026-02-23', 'Transport', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 300.00 at METRO on 2026-03-05',
'METRO', 300.00, 'INR', '2026-03-05', 'Groceries', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 1450.00 at CROMA on 2026-03-05',
'CROMA', 1450.00, 'INR', '2026-03-05', 'Shopping', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 399.00 at HOTSTAR on 2026-03-04',
'HOTSTAR', 399.00, 'INR', '2026-03-04', 'Entertainment', 1),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 520.00 at SWIGGY on 2026-03-02',
'SWIGGY', 520.00, 'INR', '2026-03-02', 'Food', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 780.00 at BMTC on 2026-03-03',
'BMTC', 780.00, 'INR', '2026-03-03', 'Transport', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 1899.00 at AMAZON on 2026-03-04',
'AMAZON', 1899.00, 'INR', '2026-03-04', 'Shopping', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 520.00 at STARBUCKS on 2026-03-01',
'STARBUCKS', 520.00, 'INR', '2026-03-01', 'Food', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 2300.00 at BESCOM on 2026-03-02',
'BESCOM', 2300.00, 'INR', '2026-03-02', 'Utilities', 0),

-- more realistic spread to reach 40–60 tx (last ~45 days)
(1, 1, 'SMS',
'INR 640.00 spent on HDFC Bank CREDIT Card ending 1234 at D-MART on 2026-01-21',
'D-MART', 640.00, 'INR', '2026-01-21', 'Groceries', 0),
(1, 1, 'SMS',
'INR 290.00 spent on HDFC Bank CREDIT Card ending 1234 at UBER on 2026-01-22',
'UBER', 290.00, 'INR', '2026-01-22', 'Transport', 0),
(1, 1, 'SMS',
'INR 850.00 spent on HDFC Bank CREDIT Card ending 1234 at ZOMATO on 2026-01-23',
'ZOMATO', 850.00, 'INR', '2026-01-23', 'Food', 0),
(1, 1, 'SMS',
'INR 1200.00 spent on HDFC Bank CREDIT Card ending 1234 at AJIO on 2026-01-24',
'AJIO', 1200.00, 'INR', '2026-01-24', 'Shopping', 0),
(1, 1, 'SMS',
'INR 410.00 spent on HDFC Bank CREDIT Card ending 1234 at BMTC on 2026-01-26',
'BMTC', 410.00, 'INR', '2026-01-26', 'Transport', 0),
(1, 1, 'SMS',
'INR 300.00 spent on HDFC Bank CREDIT Card ending 1234 at DUNZO on 2026-01-27',
'DUNZO', 300.00, 'INR', '2026-01-27', 'Utilities', 0),
(1, 1, 'SMS',
'INR 650.00 spent on HDFC Bank CREDIT Card ending 1234 at ZOMATO on 2026-01-29',
'ZOMATO', 650.00, 'INR', '2026-01-29', 'Food', 0),
(1, 1, 'SMS',
'INR 780.00 spent on HDFC Bank CREDIT Card ending 1234 at INOX on 2026-01-31',
'INOX', 780.00, 'INR', '2026-01-31', 'Entertainment', 0),
(1, 1, 'SMS',
'INR 520.00 spent on HDFC Bank CREDIT Card ending 1234 at D-MART on 2026-02-02',
'D-MART', 520.00, 'INR', '2026-02-02', 'Groceries', 0),
(1, 1, 'SMS',
'INR 260.00 spent on HDFC Bank CREDIT Card ending 1234 at UBER on 2026-02-03',
'UBER', 260.00, 'INR', '2026-02-03', 'Transport', 0),
(1, 1, 'SMS',
'INR 920.00 spent on HDFC Bank CREDIT Card ending 1234 at ZOMATO on 2026-02-04',
'ZOMATO', 920.00, 'INR', '2026-02-04', 'Food', 0),
(1, 1, 'SMS',
'INR 2400.00 spent on HDFC Bank CREDIT Card ending 1234 at ACT FIBERNET on 2026-02-06',
'ACT FIBERNET', 2400.00, 'INR', '2026-02-06', 'Utilities', 1),
(1, 1, 'SMS',
'INR 560.00 spent on HDFC Bank CREDIT Card ending 1234 at METRO on 2026-02-07',
'METRO', 560.00, 'INR', '2026-02-07', 'Groceries', 0),
(1, 1, 'SMS',
'INR 1450.00 spent on HDFC Bank CREDIT Card ending 1234 at MYNTRA on 2026-02-08',
'MYNTRA', 1450.00, 'INR', '2026-02-08', 'Shopping', 0),
(1, 1, 'SMS',
'INR 340.00 spent on HDFC Bank CREDIT Card ending 1234 at BMTC on 2026-02-09',
'BMTC', 340.00, 'INR', '2026-02-09', 'Transport', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 820.00 at ZOMATO on 2026-02-26',
'ZOMATO', 820.00, 'INR', '2026-02-26', 'Food', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 480.00 at METRO on 2026-02-27',
'METRO', 480.00, 'INR', '2026-02-27', 'Groceries', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 999.00 at BOOKMYSHOW on 2026-02-28',
'BOOKMYSHOW', 999.00, 'INR', '2026-02-28', 'Entertainment', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 3200.00 at AMAZON on 2026-03-03',
'AMAZON', 3200.00, 'INR', '2026-03-03', 'Shopping', 0),
(1, 2, 'SMS',
'Your a/c XX5678 is debited by INR 8200.00 at APPLE STORE on 2026-03-05',
'APPLE STORE', 8200.00, 'INR', '2026-03-05', 'Shopping', 0);

-- PROFILE SEED (safe if already exists)
INSERT INTO profile (id, income, fixed_expenses, monthly_limit, savings_goal, currency)
VALUES (
  1,
  80000.00,
  '[{"name":"Rent","amount":25000},{"name":"EMI","amount":12000},{"name":"Subscriptions","amount":1200}]',
  5000.00,
  15000.00,
  'INR'
)
ON DUPLICATE KEY UPDATE
  income = VALUES(income),
  fixed_expenses = VALUES(fixed_expenses),
  monthly_limit = VALUES(monthly_limit),
  savings_goal = VALUES(savings_goal),
  currency = VALUES(currency);