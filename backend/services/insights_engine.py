from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

import pandas as pd

from models import Transaction
from services.tx_utils import transactions_to_dataframe


def compute_insights(transactions: List[Transaction]) -> Dict:
    """
    Examples:
      - "You spent 40% more on food this week"
      - "Your transport spending increased"
    """
    df = transactions_to_dataframe(transactions)
    today = date.today()

    if df.empty:
        return {"insights": []}

    df["day"] = df["date"].dt.date
    start_this_week = today - timedelta(days=today.weekday())
    start_last_week = start_this_week - timedelta(days=7)
    end_last_week = start_this_week - timedelta(days=1)

    this_week = df[(df["day"] >= start_this_week) & (df["day"] <= today)]
    last_week = df[(df["day"] >= start_last_week) & (df["day"] <= end_last_week)]

    if this_week.empty and last_week.empty:
        return {"insights": []}

    tw = this_week.groupby("category")["amount"].sum()
    lw = last_week.groupby("category")["amount"].sum()

    insights: List[Dict] = []
    categories = set(list(tw.index) + list(lw.index))
    for cat in categories:
        a = float(tw.get(cat, 0.0))
        b = float(lw.get(cat, 0.0))
        if b <= 0 and a <= 0:
            continue
        # ignore tiny categories
        if max(a, b) < 200:
            continue
        if b > 0 and a > b * 1.2:
            pct = round(((a - b) / b) * 100)
            insights.append(
                {
                    "type": "week_over_week_increase",
                    "category": cat,
                    "message": f"You spent {pct}% more on {cat} this week",
                    "severity": "warning" if pct >= 40 else "info",
                }
            )
        elif b > 0 and a < b * 0.75:
            pct = round(((b - a) / b) * 100)
            insights.append(
                {
                    "type": "week_over_week_decrease",
                    "category": cat,
                    "message": f"You spent {pct}% less on {cat} this week",
                    "severity": "info",
                }
            )

    insights.sort(key=lambda x: (x.get("severity") != "warning", x.get("category", "")))
    return {"insights": insights[:8]}

