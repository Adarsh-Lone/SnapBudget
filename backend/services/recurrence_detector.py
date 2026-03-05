from collections import Counter
from datetime import date
from typing import List

from models import Transaction


def mark_recurring_transactions(transactions: List[Transaction]) -> None:
    """
    Simple recurrence detection:
    - Group by merchant and amount
    - If at least 3 occurrences and roughly monthly (25-35 days apart), mark as recurring
    """
    by_key = {}
    for tx in transactions:
        key = (tx.merchant or "", float(tx.amount))
        by_key.setdefault(key, []).append(tx)

    for (merchant, amount), txs in by_key.items():
        if len(txs) < 3:
            continue
        txs.sort(key=lambda t: t.transaction_date)
        gaps = []
        for i in range(1, len(txs)):
            d1: date = txs[i - 1].transaction_date
            d2: date = txs[i].transaction_date
            gaps.append((d2 - d1).days)

        if not gaps:
            continue

        common_gap = Counter(gaps).most_common(1)[0][0]
        if 25 <= common_gap <= 35:
            for tx in txs:
                tx.is_recurring = True

