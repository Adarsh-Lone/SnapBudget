USE snapbudget;

INSERT INTO users (name, email) VALUES
('Demo User', 'demo@snapbudget.local')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO accounts (user_id, bank_name, account_number_last4, current_balance)
VALUES
(1, 'HDFC Bank', '1234', 25000.00),
(1, 'ICICI Bank', '5678', 15000.00)
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
(1, 2, 'SMS',
 'Your a/c XX5678 is debited by INR 450.00 at ZOMATO on 2026-03-01',
 'ZOMATO', 450.00, 'INR', '2026-03-01', 'Food', 0),
(1, 2, 'SMS',
 'Your a/c XX5678 is debited by INR 1200.00 at AMAZON on 2026-03-02',
 'AMAZON', 1200.00, 'INR', '2026-03-02', 'Shopping', 0),
(1, 2, 'SMS',
 'Your a/c XX5678 is debited by INR 799.00 at NETFLIX.COM on 2026-03-02',
 'NETFLIX', 799.00, 'INR', '2026-03-02', 'Subscriptions', 1);

