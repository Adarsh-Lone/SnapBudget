import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict


BANK_NAME_HINTS = [
    "HDFC",
    "ICICI",
    "SBI",
    "AXIS",
    "KOTAK",
    "YES BANK",
]


def parse_debit_sms(text: str) -> Dict[str, Optional[str]]:
    """
    Simple, rule-based debit SMS parser for Indian-style bank messages.
    Extracts amount, bank name, merchant, date.
    """
    normalized = text.upper()

    amt_pattern = re.compile(
        r"(INR|RS\.?)\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)"
    )
    amount = None
    m = amt_pattern.search(normalized)
    if m:
        amt_str = m.group(2).replace(",", "")
        try:
            amount = Decimal(amt_str)
        except Exception:
            amount = None

    bank_name = None
    for hint in BANK_NAME_HINTS:
        if hint in normalized:
            bank_name = hint
            break

    merch_pattern = re.compile(r"AT\s+([A-Z0-9\.\-\s]+)")
    merchant = None
    m2 = merch_pattern.search(normalized)
    if m2:
        merch_part = m2.group(1)
        merchant = merch_part.split(" ON ")[0].strip().rstrip(".")[:255]

    date_patterns = [
        r"ON\s+(\d{2}[/-]\d{2}[/-]\d{4})",
        r"ON\s+(\d{4}[/-]\d{2}[/-]\d{2})",
    ]
    date_str = None
    for pat in date_patterns:
        m3 = re.search(pat, normalized)
        if m3:
            date_str = m3.group(1)
            break

    parsed_date = None
    if date_str:
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue

    return {
        "amount": float(amount) if amount is not None else None,
        "currency": "INR",
        "bank_name": bank_name,
        "merchant": merchant,
        "transaction_date": parsed_date.isoformat() if parsed_date else None,
        "raw_text": text,
    }

