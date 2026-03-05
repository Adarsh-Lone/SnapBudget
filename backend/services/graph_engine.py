from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Optional

import pandas as pd

from models import Account, Transaction
from services.tx_utils import transactions_to_dataframe


def _sum_balance(accounts: List[Account]) -> float:
    return float(sum(float(a.current_balance or 0) for a in accounts))


def compute_graph_datasets(
    transactions: List[Transaction],
    accounts: List[Account],
    currency: str = "INR",
) -> Dict:
    df = transactions_to_dataframe(transactions)
    today = date.today()

    if df.empty:
        return {
            "currency": currency,
            "spending_last_30_days": [],
            "category_distribution": [],
            "weekly_spending_comparison": [],
            "burn_rate_trend": [],
            "survival_forecast": [],
        }

    # Daily spend (last 30 days)
    df["day"] = df["date"].dt.date
    daily = df.groupby("day")["amount"].sum().sort_index()

    days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    spending_last_30 = [
        {"date": d.isoformat(), "amount": round(float(daily.get(d, 0.0)), 2)} for d in days
    ]

    # Category distribution (last 30 days)
    start_30 = today - timedelta(days=30)
    df30 = df[df["day"] >= start_30]
    cat = (
        df30.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(12)
    )
    category_distribution = [
        {"category": str(idx), "amount": round(float(val), 2)} for idx, val in cat.items()
    ]

    # Weekly spending comparison (last 8 weeks)
    df["week_start"] = (df["date"] - pd.to_timedelta(df["date"].dt.dayofweek, unit="D")).dt.date
    weekly = df.groupby("week_start")["amount"].sum().sort_index()
    week_starts = [today - timedelta(days=today.weekday()) - timedelta(weeks=i) for i in range(7, -1, -1)]
    weekly_spending = [
        {
            "week_start": ws.isoformat(),
            "amount": round(float(weekly.get(ws, 0.0)), 2),
        }
        for ws in week_starts
    ]

    # Burn rate trend (weekly burn = avg_daily_week * 30)
    burn_rate_trend = []
    for ws in week_starts:
        total = float(weekly.get(ws, 0.0))
        avg_daily_week = total / 7.0
        burn_rate_trend.append(
            {"week_start": ws.isoformat(), "burn_rate": round(avg_daily_week * 30.0, 2)}
        )

    # Survival forecast: projected balance over next 60 days using avg daily spend (last 30 days)
    total_30 = float(df30["amount"].sum()) if not df30.empty else float(df["amount"].sum())
    avg_daily_30 = total_30 / 30.0
    balance0 = _sum_balance(accounts)

    forecast = []
    for i in range(0, 61):
        d = today + timedelta(days=i)
        projected_balance = balance0 - avg_daily_30 * i
        survival_remaining = None
        if avg_daily_30 > 0:
            survival_remaining = max(0.0, projected_balance / avg_daily_30)
        forecast.append(
            {
                "date": d.isoformat(),
                "projected_balance": round(projected_balance, 2),
                "survival_days_remaining": round(survival_remaining, 1)
                if survival_remaining is not None
                else None,
            }
        )

    return {
        "currency": currency,
        "spending_last_30_days": spending_last_30,
        "category_distribution": category_distribution,
        "weekly_spending_comparison": weekly_spending,
        "burn_rate_trend": burn_rate_trend,
        "survival_forecast": forecast,
    }

