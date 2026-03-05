from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    accounts = db.relationship("Account", backref="user", lazy=True)
    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bank_name = db.Column(db.String(100))
    account_number_last4 = db.Column(db.String(4))
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="account", lazy=True)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    source_type = db.Column(db.Enum("RECEIPT", "SMS", name="source_type_enum"), nullable=False)
    raw_text = db.Column(db.Text)
    merchant = db.Column(db.String(255))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(10), default="INR")
    transaction_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))
    is_recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Profile(db.Model):
    """
    1:1 with User. Uses users.id as the primary key.

    fixed_expenses is stored as a JSON string for portability:
      [{"name":"Rent","amount":25000}, {"name":"EMI","amount":12000}]
    """

    __tablename__ = "profile"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    income = db.Column(db.Numeric(15, 2), default=0)
    fixed_expenses = db.Column(db.Text, nullable=True)
    monthly_limit = db.Column(db.Numeric(15, 2), default=0)
    savings_goal = db.Column(db.Numeric(15, 2), default=0)
    currency = db.Column(db.String(10), default="INR")
    profile_picture_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)