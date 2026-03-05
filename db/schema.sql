CREATE DATABASE IF NOT EXISTS snapbudget CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE snapbudget;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  bank_name VARCHAR(100),
  account_number_last4 VARCHAR(4),
  current_balance DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

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

-- USER PROFILE (1:1 with users; uses users.id as primary key)
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
