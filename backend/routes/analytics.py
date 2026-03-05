from flask import Blueprint, jsonify, request

from models import Transaction, Account
from services.analytics_engine import compute_core_metrics
from extensions import db
from services.recurrence_detector import mark_recurring_transactions


bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@bp.route("/summary", methods=["GET"])
def summary():
    """
    Sample response:
    {
      "avg_daily_spend": 1234.5,
      "spending_volatility": 456.7,
      "burn_rate": 1100.0,
      "survival_days": 45.2,
      "current_month_spend": 20000.0,
      "previous_month_spend": 15000.0,
      "stress_date": "2026-05-01",
      "behavior_tag": "Impulse Spender"
    }
    """
    user_id = int(request.args.get("user_id", "1"))
    txs = Transaction.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    # update recurring flags in-place
    mark_recurring_transactions(txs)
    db.session.commit()

    metrics = compute_core_metrics(user_id, txs, accounts)
    return jsonify(metrics)


@bp.route("/monthly-compare", methods=["GET"])
def monthly_compare():
    user_id = int(request.args.get("user_id", "1"))
    txs = Transaction.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    metrics = compute_core_metrics(user_id, txs, accounts)
    return jsonify(
        {
            "current_month_spend": metrics["current_month_spend"],
            "previous_month_spend": metrics["previous_month_spend"],
            "delta": round(
                metrics["current_month_spend"] - metrics["previous_month_spend"], 2
            ),
            "stress_date": metrics["stress_date"],
        }
    )

