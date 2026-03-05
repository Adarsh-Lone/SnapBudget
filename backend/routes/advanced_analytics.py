from flask import Blueprint, jsonify, request

from extensions import db
from models import Account, Profile, Transaction
from services.behavior_engine import classify_behavior
from services.graph_engine import compute_graph_datasets
from services.insights_engine import compute_insights
from services.prediction_engine import predict_financial_stress
from services.risk_engine import compute_risk_alerts
from services.tx_utils import transactions_to_dataframe


bp = Blueprint("advanced_analytics", __name__, url_prefix="/api")


def _load_core(user_id: int):
    txs = Transaction.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()
    profile = Profile.query.get(user_id)
    return txs, accounts, profile


@bp.route("/alerts", methods=["GET"])
def alerts():
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    alerts_list, ctx = compute_risk_alerts(user_id, txs, accounts, profile)
    return jsonify(
        {
            "alerts": alerts_list,
            "context": {
                "avg_daily_spend_30": ctx.avg_daily_spend_30,
                "burn_rate": ctx.burn_rate,
                "runway_days": ctx.runway_days,
                "current_month_spend": ctx.current_month_spend,
                "weekly_burn_rate_current": ctx.weekly_burn_rate_current,
                "weekly_burn_rate_previous": ctx.weekly_burn_rate_previous,
            },
        }
    )


@bp.route("/analytics/graphs", methods=["GET"])
def analytics_graphs():
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    currency = (profile.currency if profile and profile.currency else "INR")
    graphs = compute_graph_datasets(txs, accounts, currency=currency)
    return jsonify(graphs)


@bp.route("/analytics/trends", methods=["GET"])
def analytics_trends():
    """
    Returns daily and weekly trends plus burn-rate/survival for charts.

    Shape:
    {
      "daily": [...],      # from spending_last_30_days
      "weekly": [...],     # from weekly_spending_comparison
      "burn_rate": 1234.5,
      "survival_days": 42.3
    }
    """
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)

    currency = (profile.currency if profile and profile.currency else "INR")
    graphs = compute_graph_datasets(txs, accounts, currency=currency)
    alerts_list, ctx = compute_risk_alerts(user_id, txs, accounts, profile)

    return jsonify(
      {
        "daily": graphs.get("spending_last_30_days", []),
        "weekly": graphs.get("weekly_spending_comparison", []),
        "burn_rate": ctx.burn_rate,
        "survival_days": ctx.runway_days,
      }
    )


@bp.route("/analytics/categories", methods=["GET"])
def analytics_categories():
    """
    Returns category distribution suitable for pie charts.

    Shape:
    {
      "categories": [
        { "category": "Food", "amount": 1234.5 },
        ...
      ]
    }
    """
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    currency = (profile.currency if profile and profile.currency else "INR")
    graphs = compute_graph_datasets(txs, accounts, currency=currency)
    return jsonify({"categories": graphs.get("category_distribution", [])})


@bp.route("/behavior", methods=["GET"])
def behavior():
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    df = transactions_to_dataframe(txs)
    monthly_limit = float(profile.monthly_limit or 0) if profile else 0.0

    # derive current-month spend from df to keep behavior endpoint independent
    if df.empty:
        res = classify_behavior(df, monthly_limit=monthly_limit, current_month_spend=0.0)
    else:
        today = df["date"].dt.date.max()
        first_day_current = today.replace(day=1)
        daily = df.groupby(df["date"].dt.date)["amount"].sum()
        current_month_spend = float(
            daily[(daily.index >= first_day_current) & (daily.index <= today)].sum()
        )
        res = classify_behavior(
            df, monthly_limit=monthly_limit, current_month_spend=current_month_spend
        )

    return jsonify({"tag": res.tag, "stats": res.stats})


@bp.route("/predictions", methods=["GET"])
def predictions():
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    data = predict_financial_stress(txs, accounts, profile)
    return jsonify(data)


@bp.route("/insights", methods=["GET"])
def insights():
    user_id = int(request.args.get("user_id", "1"))
    txs, accounts, profile = _load_core(user_id)
    data = compute_insights(txs)
    return jsonify(data)

