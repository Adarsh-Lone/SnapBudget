from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import pandas as pd


@dataclass(frozen=True)
class BehaviorResult:
    tag: str
    stats: Dict


def _safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return float(a) / float(b)


def classify_behavior(
    df: pd.DataFrame,
    monthly_limit: Optional[float] = None,
    current_month_spend: Optional[float] = None,
) -> BehaviorResult:
    """
    Tags requested:
      Saver, Overspender, Balanced, Weekend Spender, Subscription Heavy
    """
    if df is None or df.empty:
        return BehaviorResult(tag="Balanced", stats={"note": "no_transactions"})

    dff = df.copy()
    dff["day_of_week"] = dff["date"].dt.dayofweek  # Mon=0 .. Sun=6
    is_weekend = dff["day_of_week"].isin([5, 6])

    total_spend = float(dff["amount"].sum())
    weekend_spend = float(dff.loc[is_weekend, "amount"].sum())
    weekend_ratio = _safe_div(weekend_spend, total_spend)

    # Subscription heavy: use recurring flag and/or category label if present
    recurring_ratio = float(dff["is_recurring"].mean()) if len(dff) else 0.0
    sub_spend = float(
        dff.loc[dff["category"].str.lower().eq("subscriptions"), "amount"].sum()
    )
    subscription_ratio = _safe_div(sub_spend, total_spend)

    # Frequency: transactions per active day
    active_days = int(dff["date"].dt.date.nunique())
    tx_count = int(len(dff))
    tx_per_day = _safe_div(tx_count, max(active_days, 1))

    limit = float(monthly_limit or 0)
    month_spend = float(current_month_spend or 0)

    tag = "Balanced"
    if limit > 0 and month_spend > limit * 1.02:
        tag = "Overspender"
    elif recurring_ratio > 0.5 or subscription_ratio > 0.35:
        tag = "Subscription Heavy"
    elif weekend_ratio > 0.45 and tx_per_day >= 1.0:
        tag = "Weekend Spender"
    elif limit > 0 and month_spend < limit * 0.65:
        tag = "Saver"

    stats = {
        "total_spend": round(total_spend, 2),
        "weekend_ratio": round(weekend_ratio, 3),
        "subscription_ratio": round(subscription_ratio, 3),
        "recurring_ratio": round(recurring_ratio, 3),
        "tx_count": tx_count,
        "active_days": active_days,
        "tx_per_day": round(tx_per_day, 2),
        "monthly_limit": round(limit, 2),
        "current_month_spend": round(month_spend, 2),
    }
    return BehaviorResult(tag=tag, stats=stats)

