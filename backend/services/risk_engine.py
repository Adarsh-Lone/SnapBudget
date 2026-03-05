from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from models import Account, Transaction
from services.profile_utils import fixed_expenses_total, parse_fixed_expenses
from services.tx_utils import transactions_to_dataframe


@dataclass(frozen=True)
class RiskContext:
    avg_daily_spend_30: float
    burn_rate: float
    runway_days: Optional[float]
    current_month_spend: float
    weekly_burn_rate_current: float
    weekly_burn_rate_previous: float


def _sum_balance(accounts: List[Account]) -> float:
    return float(sum(float(a.current_balance or 0) for a in accounts))


def _avg_daily_over_window(daily: pd.Series, start: date, days: int) -> float:
    """
    Average daily spend across a fixed-length window, counting missing days as zero.
    """
    if days <= 0:
        return 0.0
    total = float(daily[(daily.index >= start) & (daily.index < start + timedelta(days=days))].sum())
    return total / float(days)


def compute_risk_alerts(
    user_id: int,
    transactions: List[Transaction],
    accounts: List[Account],
    profile_row: Optional[object],  # models.Profile
) -> Tuple[List[Dict], RiskContext]:
    df = transactions_to_dataframe(transactions)
    if df.empty:
        ctx = RiskContext(
            avg_daily_spend_30=0.0,
            burn_rate=0.0,
            runway_days=None,
            current_month_spend=0.0,
            weekly_burn_rate_current=0.0,
            weekly_burn_rate_previous=0.0,
        )
        return [], ctx

    daily = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
    today = date.today()

    avg_daily_spend_30 = _avg_daily_over_window(daily, today - timedelta(days=30), 30)
    burn_rate = avg_daily_spend_30 * 30.0  # as requested

    total_balance = _sum_balance(accounts)
    runway_days = None
    if avg_daily_spend_30 > 0:
        runway_days = total_balance / avg_daily_spend_30

    first_day_current = today.replace(day=1)
    current_month_spend = float(daily[daily.index >= first_day_current].sum())

    # burn rate increasing WoW: compare last 7 days vs previous 7 days
    avg_daily_7_cur = _avg_daily_over_window(daily, today - timedelta(days=7), 7)
    avg_daily_7_prev = _avg_daily_over_window(daily, today - timedelta(days=14), 7)
    weekly_burn_rate_current = avg_daily_7_cur * 30.0
    weekly_burn_rate_previous = avg_daily_7_prev * 30.0

    monthly_limit = float(getattr(profile_row, "monthly_limit", 0) or 0)
    fixed_items = parse_fixed_expenses(getattr(profile_row, "fixed_expenses", None))
    fixed_total = fixed_expenses_total(fixed_items)

    alerts: List[Dict] = []

    if monthly_limit > 0 and current_month_spend > monthly_limit:
        alerts.append(
            {
                "type": "limit_exceeded",
                "severity": "critical",
                "message": f"You exceeded your monthly spending limit by {round(current_month_spend - monthly_limit, 2)}",
            }
        )

    if weekly_burn_rate_previous > 0 and weekly_burn_rate_current > weekly_burn_rate_previous * 1.10:
        pct = round(
            ((weekly_burn_rate_current - weekly_burn_rate_previous) / weekly_burn_rate_previous) * 100,
            1,
        )
        alerts.append(
            {
                "type": "burn_rate_increasing",
                "severity": "warning",
                "message": f"Your burn rate is up {pct}% week-over-week",
            }
        )

    if runway_days is not None and runway_days < 30:
        alerts.append(
            {
                "type": "financial_distress",
                "severity": "critical",
                "message": f"Your spending trend indicates risk in {int(max(runway_days, 0))} days",
            }
        )

    # unusually large transaction (last 30 days)
    try:
        start_30 = today - timedelta(days=30)
        recent = df[df["date"].dt.date >= start_30]
        if not recent.empty:
            amounts = recent["amount"].astype(float)
            mu = float(amounts.mean())
            sigma = float(amounts.std(ddof=0)) if len(amounts) > 1 else 0.0
            max_amt = float(amounts.max())
            # trigger if significantly above typical, or just clearly "big"
            big_threshold = max(5000.0, mu + 3.0 * sigma)
            if max_amt >= big_threshold:
                alerts.append(
                    {
                        "type": "unusually_large_transaction",
                        "severity": "warning",
                        "message": f"Unusually large transaction detected: ₹{round(max_amt, 2)} in the last 30 days",
                    }
                )
    except Exception:
        pass

    # extra signal: fixed expenses burden vs income (informational)
    income = float(getattr(profile_row, "income", 0) or 0)
    if income > 0 and fixed_total > income * 0.6:
        alerts.append(
            {
                "type": "fixed_expenses_high",
                "severity": "info",
                "message": "Fixed expenses are consuming a large portion of your income",
            }
        )

    ctx = RiskContext(
        avg_daily_spend_30=round(avg_daily_spend_30, 2),
        burn_rate=round(burn_rate, 2),
        runway_days=round(runway_days, 1) if runway_days is not None else None,
        current_month_spend=round(current_month_spend, 2),
        weekly_burn_rate_current=round(weekly_burn_rate_current, 2),
        weekly_burn_rate_previous=round(weekly_burn_rate_previous, 2),
    )
    return alerts, ctx

