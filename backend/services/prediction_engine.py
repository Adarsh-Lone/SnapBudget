from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from models import Account, Transaction
from services.profile_utils import fixed_expenses_total, parse_fixed_expenses
from services.tx_utils import transactions_to_dataframe


def _sum_balance(accounts: List[Account]) -> float:
    return float(sum(float(a.current_balance or 0) for a in accounts))


def _confidence_from_daily(daily: pd.Series) -> float:
    if daily is None or daily.empty:
        return 0.0
    mu = float(daily.mean())
    if mu <= 0:
        return 0.2
    sigma = float(daily.std(ddof=0)) if len(daily) > 1 else 0.0
    # normalize volatility into [0,1]
    score = 1.0 - min(1.0, sigma / (mu * 2.0))
    return float(max(0.05, min(0.95, score)))


def predict_financial_stress(
    transactions: List[Transaction],
    accounts: List[Account],
    profile_row: Optional[object],  # models.Profile
) -> Dict:
    """
    Improve stress prediction using:
      current_balance - projected_expense
    Returns:
      financial_stress_date, confidence_score
    """
    df = transactions_to_dataframe(transactions)
    today = date.today()
    balance = _sum_balance(accounts)

    if df.empty:
        return {
            "financial_stress_date": None,
            "confidence_score": 0.0,
            "projected_daily_expense": 0.0,
            "current_balance": round(balance, 2),
        }

    df["day"] = df["date"].dt.date
    daily = df.groupby("day")["amount"].sum().sort_index()

    # projected variable expense = avg daily spend over last 30 days (including zeros)
    start_30 = today - timedelta(days=30)
    total_30 = float(daily[daily.index >= start_30].sum())
    projected_daily = total_30 / 30.0

    fixed_items = parse_fixed_expenses(getattr(profile_row, "fixed_expenses", None))
    monthly_fixed = fixed_expenses_total(fixed_items)

    # simulate depletion up to 365 days
    if projected_daily <= 0 and monthly_fixed <= 0:
        return {
            "financial_stress_date": None,
            "confidence_score": round(_confidence_from_daily(daily), 3),
            "projected_daily_expense": 0.0,
            "current_balance": round(balance, 2),
        }

    bal = float(balance)
    stress_date = None
    for i in range(0, 366):
        d = today + timedelta(days=i)
        # variable expense
        bal -= projected_daily
        # fixed monthly expenses on the 1st (starting next month, and also today if today is 1st)
        if d.day == 1:
            bal -= monthly_fixed
        if bal <= 0:
            stress_date = d.isoformat()
            break

    confidence = _confidence_from_daily(daily)
    return {
        "financial_stress_date": stress_date,
        "confidence_score": round(confidence, 3),
        "projected_daily_expense": round(projected_daily, 2),
        "projected_monthly_fixed_expense": round(monthly_fixed, 2),
        "current_balance": round(balance, 2),
    }

