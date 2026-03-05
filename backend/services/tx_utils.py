from typing import List

import pandas as pd

from models import Transaction


def transactions_to_dataframe(transactions: List[Transaction]) -> pd.DataFrame:
    """
    Helper used by multiple analytics engines to convert transactions into a
    pandas DataFrame with normalized columns.
    """
    rows = []
    for tx in transactions:
        rows.append(
            {
                "date": tx.transaction_date,
                "amount": float(tx.amount),
                "category": tx.category or "Other",
                "merchant": tx.merchant or "",
                "is_recurring": bool(tx.is_recurring),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=["date", "amount", "category", "merchant", "is_recurring"]
        )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df

