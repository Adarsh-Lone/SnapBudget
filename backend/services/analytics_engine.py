from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from models import Transaction, Account



def _transactions_to_dataframe(transactions: List[Transaction]) -> pd.DataFrame:
    rows = []
    for tx in transactions:
        rows.append(
            {
                "date": tx.transaction_date,
                "amount": float(tx.amount),
                "category": tx.category or "Other",
                "is_recurring": bool(tx.is_recurring),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["date", "amount", "category", "is_recurring"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df
=======
from services.behavior_engine import classify_behavior as classify_behavior_v2
from services.tx_utils import transactions_to_dataframe
>>>>>>> e8bc353 (Updated backend, frontend, analytics, alerts, and insights features)


def compute_core_metrics(
    user_id: int,
    transactions: List[Transaction],
    accounts: List[Account],
) -> Dict:
    df = transactions_to_dataframe(transactions)
    if df.empty:
        return {
            "avg_daily_spend": 0.0,
            "spending_volatility": 0.0,
            "burn_rate": 0.0,
            "survival_days": None,
            "current_month_spend": 0.0,
            "previous_month_spend": 0.0,
            "stress_date": None,

            "behavior_tag": "Stable Planner",

            "behavior_tag": "Balanced",

        }

    daily = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
    avg_daily_spend = float(daily.mean())
    spending_volatility = float(daily.std(ddof=0)) if len(daily) > 1 else 0.0

    today = date.today()
    last_30 = daily[daily.index >= (today - timedelta(days=30))]
    burn_rate = float(last_30.mean()) if not last_30.empty else avg_daily_spend

    total_balance = sum(float(ac.current_balance or 0) for ac in accounts)
    survival_days = None
    if burn_rate > 0:
        survival_days = total_balance / burn_rate

    first_day_current = today.replace(day=1)
    first_day_prev = (first_day_current - timedelta(days=1)).replace(day=1)
    end_prev = first_day_current - timedelta(days=1)

    current_month_spend = float(
        daily[(daily.index >= first_day_current) & (daily.index <= today)].sum()
    )
    previous_month_spend = float(
        daily[(daily.index >= first_day_prev) & (daily.index <= end_prev)].sum()
    )

    stress_date = None
    if survival_days is not None:
        stress_dt = today + timedelta(days=int(survival_days))
        stress_date = stress_dt.isoformat()


    behavior_tag = classify_behavior(df, avg_daily_spend, spending_volatility)

    # Improved behavior tags; still returns a single string field (API-compatible)
    behavior_tag = classify_behavior_v2(df).tag


    return {
        "avg_daily_spend": round(avg_daily_spend, 2),
        "spending_volatility": round(spending_volatility, 2),
        "burn_rate": round(burn_rate, 2),
        "survival_days": round(survival_days, 1) if survival_days is not None else None,
        "current_month_spend": round(current_month_spend, 2),
        "previous_month_spend": round(previous_month_spend, 2),
        "stress_date": stress_date,
        "behavior_tag": behavior_tag,
    }



def classify_behavior(
    df: pd.DataFrame, avg_daily_spend: float, spending_volatility: float
) -> str:
    if df.empty:
        return "Stable Planner"

    recurring_ratio = df["is_recurring"].mean()

    if recurring_ratio > 0.5:
        return "Subscription Heavy"

    if spending_volatility > avg_daily_spend * 0.8:
        return "Impulse Spender"

    if avg_daily_spend > 0 and recurring_ratio * avg_daily_spend > avg_daily_spend * 0.6:
        return "Risk Prone"

    return "Stable Planner"

