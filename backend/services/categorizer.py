from typing import Optional


CATEGORY_RULES = {
    "NETFLIX": "Subscriptions",
    "SPOTIFY": "Subscriptions",
    "PRIME VIDEO": "Subscriptions",
    "SWIGGY": "Food",
    "ZOMATO": "Food",
    "UBER": "Transport",
    "OLA": "Transport",
    "AMAZON": "Shopping",
    "FLIPKART": "Shopping",
    "BIGBAZAAR": "Groceries",
    "DMART": "Groceries",
}


def auto_categorize(merchant: Optional[str], raw_text: str) -> str:
    if merchant:
        key = merchant.upper()
        for pattern, category in CATEGORY_RULES.items():
            if pattern in key:
                return category

    text_upper = raw_text.upper()
    for pattern, category in CATEGORY_RULES.items():
        if pattern in text_upper:
            return category

    return "Other"

