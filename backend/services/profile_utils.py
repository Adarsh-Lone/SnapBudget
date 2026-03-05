import json
from typing import Any, Dict, List, Optional


def parse_fixed_expenses(raw: Optional[str]) -> List[Dict[str, Any]]:
    if not raw:
        return []
    try:
        val = json.loads(raw)
        if isinstance(val, list):
            out: List[Dict[str, Any]] = []
            for item in val:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()[:120]
                try:
                    amount = float(item.get("amount") or 0)
                except Exception:
                    amount = 0.0
                if name:
                    out.append({"name": name, "amount": round(amount, 2)})
            return out
    except Exception:
        return []
    return []


def serialize_fixed_expenses(items: Any) -> Optional[str]:
    if items is None:
        return None
    if isinstance(items, str):
        # already JSON or user-provided string
        return items
    if not isinstance(items, list):
        return None
    cleaned: List[Dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        name = str(it.get("name") or "").strip()[:120]
        if not name:
            continue
        try:
            amount = float(it.get("amount") or 0)
        except Exception:
            amount = 0.0
        cleaned.append({"name": name, "amount": round(amount, 2)})
    return json.dumps(cleaned, ensure_ascii=False)


def fixed_expenses_total(items: List[Dict[str, Any]]) -> float:
    total = 0.0
    for it in items:
        try:
            total += float(it.get("amount") or 0)
        except Exception:
            continue
    return round(total, 2)

