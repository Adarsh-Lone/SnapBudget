import os
import tempfile
from datetime import date

from flask import Blueprint, jsonify, request

from extensions import db
from models import Transaction, Account, User
from services.ocr_service import extract_text_from_image, parse_receipt_text
from services.sms_parser import parse_debit_sms
from services.categorizer import auto_categorize


bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


@bp.route("", methods=["GET"])
def list_transactions():
    user_id = int(request.args.get("user_id", "1"))
    txs = (
        Transaction.query.filter_by(user_id=user_id)
        .order_by(Transaction.transaction_date.desc())
        .limit(100)
        .all()
    )
    data = []
    for tx in txs:
        data.append(
            {
                "id": tx.id,
                "source_type": tx.source_type,
                "merchant": tx.merchant,
                "amount": float(tx.amount),
                "currency": tx.currency,
                "transaction_date": tx.transaction_date.isoformat(),
                "category": tx.category,
                "is_recurring": bool(tx.is_recurring),
            }
        )
    return jsonify({"transactions": data})


@bp.route("/upload-receipt", methods=["POST"])
def upload_receipt():
    """
    Sample response:
    {
      "transaction": {
        "id": 10,
        "merchant": "BIGBAZAAR",
        "amount": 1349.5,
        "transaction_date": "2026-03-04",
        "category": "Groceries",
        "is_recurring": false
      },
      "parsed": { ...raw parsed fields... }
    }
    """
    user_id = int(request.form.get("user_id", "1"))
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(file.read())

        text = extract_text_from_image(temp_path)
        parsed = parse_receipt_text(text)

        merchant = parsed.get("merchant")
        amount = parsed.get("amount")
        tx_date_str = parsed.get("transaction_date")

        if amount is None:
            return jsonify({"error": "Could not extract amount from receipt"}), 422

        tx_date = date.today()
        if tx_date_str:
            try:
                tx_date = date.fromisoformat(tx_date_str)
            except ValueError:
                pass

        user = User.query.get(user_id)
        if not user:
            user = User(id=user_id, name="Demo User")
            db.session.add(user)
            db.session.flush()

        account = Account.query.filter_by(user_id=user_id).first()
        if not account:
            account = Account(user_id=user_id, bank_name="Unknown", account_number_last4="0000")
            db.session.add(account)
            db.session.flush()

        category = auto_categorize(merchant, parsed.get("raw_text") or "")

        tx = Transaction(
            user_id=user_id,
            account_id=account.id,
            source_type="RECEIPT",
            raw_text=parsed.get("raw_text") or "",
            merchant=merchant,
            amount=amount,
            currency="INR",
            transaction_date=tx_date,
            category=category,
        )
        db.session.add(tx)
        db.session.commit()

        return jsonify(
            {
                "transaction": {
                    "id": tx.id,
                    "merchant": tx.merchant,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "transaction_date": tx.transaction_date.isoformat(),
                    "category": tx.category,
                    "is_recurring": bool(tx.is_recurring),
                },
                "parsed": parsed,
            }
        )
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


@bp.route("/parse-sms", methods=["POST"])
def parse_sms():
    """
    Sample request:
    { "text": "Your a/c XX5678 is debited by INR 450.00 at ZOMATO on 2026-03-01" }

    Sample response:
    {
      "transaction": { ... },
      "parsed": { ... }
    }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    user_id = int(data.get("user_id", 1))

    if not text:
        return jsonify({"error": "Missing 'text'"}), 400

    parsed = parse_debit_sms(text)
    amount = parsed.get("amount")
    if amount is None:
        return jsonify({"error": "Could not parse amount"}), 422

    tx_date = date.today()
    if parsed.get("transaction_date"):
        try:
            tx_date = date.fromisoformat(parsed["transaction_date"])
        except ValueError:
            pass

    merchant = parsed.get("merchant")

    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, name="Demo User")
        db.session.add(user)
        db.session.flush()

    bank_name = parsed.get("bank_name") or "Unknown"
    account = Account.query.filter_by(user_id=user_id, bank_name=bank_name).first()
    if not account:
        account = Account(user_id=user_id, bank_name=bank_name, account_number_last4="0000")
        db.session.add(account)
        db.session.flush()

    category = auto_categorize(merchant, parsed.get("raw_text") or "")

    tx = Transaction(
        user_id=user_id,
        account_id=account.id,
        source_type="SMS",
        raw_text=parsed.get("raw_text") or "",
        merchant=merchant,
        amount=amount,
        currency=parsed.get("currency") or "INR",
        transaction_date=tx_date,
        category=category,
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify(
        {
            "transaction": {
                "id": tx.id,
                "merchant": tx.merchant,
                "amount": float(tx.amount),
                "currency": tx.currency,
                "transaction_date": tx.transaction_date.isoformat(),
                "category": tx.category,
                "is_recurring": bool(tx.is_recurring),
            },
            "parsed": parsed,
        }
    )

