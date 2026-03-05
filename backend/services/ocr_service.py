"""
receipt_parser.py
-----------------
Drop-in replacement for the original parse_receipt_text / extract_text_from_image module.

Public API is identical to the original:
    extract_text_from_image(image_path) -> str
    parse_receipt_text(text, image_path=None) -> Dict

The original's output dict is preserved exactly:
    {
        "merchant":          str | None,
        "amount":            float | None,
        "transaction_date":  str  | None,   # ISO format: "YYYY-MM-DD"
        "raw_text":          str,
        "category":          str,           # NEW – bonus field
    }

Pass image_path to parse_receipt_text to enable the full v3 image-based
extraction (better total detection).  If only raw text is available the
function falls back to the original heuristic so nothing breaks.
"""

from __future__ import annotations

import re
import cv2
import numpy as np
import pytesseract

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from PIL import Image

# ── optional config shim (same as original) ──────────────────────
try:
    from config import config
    if config.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
except Exception:
    pass   # config not present – tesseract assumed to be on PATH


# ═════════════════════════════════════════════════════════════════
# SECTION 1 – IMAGE HELPERS  (v3 logic)
# ═════════════════════════════════════════════════════════════════

def _preprocess(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_text_from_image(image_path: str) -> str:
    """
    Public API – identical signature to original.
    Uses v3 preprocessing (2× upscale + OTSU) for better OCR quality.
    Falls back to PIL if cv2 is unavailable.
    """
    try:
        thresh = _preprocess(image_path)
        return pytesseract.image_to_string(thresh, config="--oem 3 --psm 6")
    except Exception:
        # Graceful fallback: plain PIL (original behaviour)
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)


# ═════════════════════════════════════════════════════════════════
# SECTION 2 – AMOUNT EXTRACTION  (v3 logic)
# ═════════════════════════════════════════════════════════════════

def _clean_amount(raw: str) -> float:
    raw = raw.strip().replace("$", "").replace(" ", "")
    if re.match(r"^\d{1,3}(\.\d{3})+,\d{2}$", raw):        # 1.234,56
        return float(raw.replace(".", "").replace(",", "."))
    if re.match(r"^\d{1,3}(,\d{3})*\.\d{2}$", raw):        # 1,234.56
        return float(raw.replace(",", ""))
    if re.match(r"^\d+,\d{2}$", raw):                       # 144,02
        return float(raw.replace(",", "."))
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return 0.0


def _find_amounts(line: str) -> list[float]:
    """Return all valid monetary amounts found in one line."""
    # Collapse OCR-split decimals: "38 .68" → "38.68"
    line = re.sub(r"(\d)\s+\.\s*(\d)", r"\1.\2", line)
    line = re.sub(r"\$\s+", "$", line)

    pattern = re.compile(r"(?<!\d)\$?(\d{1,4}[.,]\d{2})(?!\d)")
    results = [
        _clean_amount(m)
        for m in pattern.findall(line)
        if 0.01 < _clean_amount(m) < 10_000
    ]

    # Reconstructed-decimal fallback (handles "5.11" OCR'd as "5711")
    if not results:
        for nd in re.findall(r"(?<!\d)(\d{3,4})(?!\d)", line):
            val = float(nd[:-2] + "." + nd[-2:])
            if 0.01 < val < 10_000:
                results.append(val)

    return results


# --- skip / priority tables ---

_SKIP_WORDS = [
    "subtotal", "sub total", "sub-total", "net sales",
    "tax", "discount", "change due", "cash tend",
    "debit tend", "credit tend", "you saved", "savings",
    "reward", "points", "cash back", "tend", "cash $",
]

_TOTAL_PRIORITY: list[tuple[int, list[str]]] = [
    (10, ["grand total", "grand ttl"]),
    (9,  ["total due", "amount due", "balance due", "total amount"]),
    (8,  ["total:"]),
    (7,  ["total"]),
    (6,  ["net total"]),
    (5,  ["amount payable", "payable"]),
]


def _kw_present(line_lower: str, keyword: str) -> bool:
    return bool(re.search(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])", line_lower))


def _is_skip(line: str) -> bool:
    ll = line.lower()
    return any(_kw_present(ll, s) for s in _SKIP_WORDS)


def _line_priority(line: str) -> int:
    ll = line.lower()
    if _is_skip(ll):
        return -1
    for pri, keywords in _TOTAL_PRIORITY:
        if any(_kw_present(ll, kw) for kw in keywords):
            return pri
    return 0


def _extract_subtotal_and_discount(lines: list[str]) -> tuple[float, float]:
    subtotal = discount = 0.0
    for line in lines:
        ll = line.lower()
        amounts = _find_amounts(line)
        if not amounts:
            continue
        if "subtotal" in ll and subtotal == 0.0:
            subtotal = amounts[-1]
        if "discount" in ll and discount == 0.0:
            discount = amounts[-1]
    return subtotal, discount


def _extract_amount_from_lines(lines: list[str]) -> float:
    """Three-pass v3 total extractor."""

    # Pass 1 – keyword-priority search
    best_pri, best_val = -1, 0.0
    for i, line in enumerate(lines):
        pri = _line_priority(line)
        if pri <= 0:
            continue
        amounts = _find_amounts(line)
        if amounts:
            if pri > best_pri:
                best_pri, best_val = pri, amounts[-1]
            continue
        # Peek next non-empty, non-skip line
        for j in range(i + 1, min(i + 3, len(lines))):
            peek = lines[j].strip()
            if not peek:
                continue
            if _is_skip(peek):
                break
            peek_amounts = _find_amounts(peek)
            if peek_amounts and pri > best_pri:
                best_pri, best_val = pri, peek_amounts[-1]
            break

    if best_val > 0:
        return best_val

    # Pass 2 – last amount on any non-skip line
    last_valid = 0.0
    for line in lines:
        if _is_skip(line):
            continue
        for val in _find_amounts(line):
            if 0 < val < 9999:
                last_valid = val
    if last_valid > 0:
        return last_valid

    # Pass 3 – math reconstruction (OCR dropped decimal point)
    subtotal, discount = _extract_subtotal_and_discount(lines)
    expected = round(subtotal - discount, 2) if subtotal > 0 else None

    candidates: list[float] = []
    for i, line in enumerate(lines):
        if _line_priority(line) <= 0:
            continue
        candidates.extend(_find_amounts(line))
        for j in range(i + 1, min(i + 3, len(lines))):
            peek = lines[j].strip()
            if not peek:
                continue
            if _is_skip(peek):
                break
            candidates.extend(_find_amounts(peek))
            break

    if expected and candidates:
        best = min(candidates, key=lambda v: abs(v - expected))
        if abs(best - expected) < 0.50:
            return best

    valid = [v for v in candidates if 0 < v < 9999]
    return max(valid) if valid else 0.0


# ═════════════════════════════════════════════════════════════════
# SECTION 3 – MERCHANT EXTRACTION  (v3 logic)
# ═════════════════════════════════════════════════════════════════

_MERCHANT_NOISE = [
    "thank you", "receipt", "www.", "http", "store #", "store#",
    "open ", "tel:", "phone", "fax", "invoice", "feedback",
    "manager", "survey", "please", "always low", "save money",
    "supercenter", "give us", "scan with", "items sold",
    "see back", "win $", "market",
]

def _extract_merchant(lines: list[str]) -> Optional[str]:
    for line in lines[:12]:
        clean = line.strip()
        if len(clean) < 3:
            continue
        if not any(c.isalpha() for c in clean):
            continue
        lower = clean.lower()
        if any(noise in lower for noise in _MERCHANT_NOISE):
            continue
        if re.search(r"\d+\s+\w+\s+(ave|st|rd|blvd|dr|way|ln|pkwy|road|pico)", lower):
            continue
        if re.search(r"\b[A-Z]{2}\s+\d{5}\b", clean):
            continue
        if re.match(r"^[\d\s\-\*\#\(\)\.]+$", clean):
            continue
        return clean[:255]
    return None


# ═════════════════════════════════════════════════════════════════
# SECTION 4 – DATE EXTRACTION
# ═════════════════════════════════════════════════════════════════

_DATE_PATTERNS = [
    (r"\b(\d{2}/\d{2}/\d{4})\b", ["%m/%d/%Y", "%d/%m/%Y"]),
    (r"\b(\d{2}/\d{2}/\d{2})\b",  ["%m/%d/%y", "%d/%m/%y"]),
    (r"\b(\d{4}-\d{2}-\d{2})\b",  ["%Y-%m-%d"]),
    (r"\b(\d{2}-\d{2}-\d{4})\b",  ["%d-%m-%Y", "%m-%d-%Y"]),
]

def _extract_date(raw_text: str) -> Optional[str]:
    """Returns ISO date string 'YYYY-MM-DD' or None."""
    for pat, fmts in _DATE_PATTERNS:
        matches = re.findall(pat, raw_text)
        if not matches:
            continue
        for fmt in fmts:
            try:
                return datetime.strptime(matches[0], fmt).date().isoformat()
            except ValueError:
                continue
    return None


# ═════════════════════════════════════════════════════════════════
# SECTION 5 – CATEGORY LOOKUP
# ═════════════════════════════════════════════════════════════════

_CATEGORIES: dict[str, str] = {
    "walmart": "Shopping",   "wal-mart": "Shopping",  "wal*mart": "Shopping",
    "target":  "Shopping",   "costco":   "Shopping",
    "trader joe": "Groceries", "whole foods": "Groceries",
    "safeway":    "Groceries", "kroger":       "Groceries",
    "mcdonald":   "Food & Dining", "starbucks": "Food & Dining",
    "subway":     "Food & Dining",
    "cvs":        "Health & Pharmacy", "walgreen": "Health & Pharmacy",
    "shell":      "Gas & Fuel", "chevron": "Gas & Fuel", "exxon": "Gas & Fuel",
}

def _guess_category(merchant: Optional[str]) -> str:
    if not merchant:
        return "General"
    lower = merchant.lower()
    for key, cat in _CATEGORIES.items():
        if key in lower:
            return cat
    return "General"


# ═════════════════════════════════════════════════════════════════
# SECTION 6 – PUBLIC parse_receipt_text  (drop-in replacement)
# ═════════════════════════════════════════════════════════════════

def parse_receipt_text(
    text: str,
    image_path: Optional[str] = None,
) -> Dict[str, object]:
    """
    Parse a receipt and return a dict compatible with the original system.

    Parameters
    ----------
    text : str
        Raw OCR text (required – same as original).
    image_path : str, optional
        Path to the original image.  When supplied the function re-runs OCR
        with v3 preprocessing to get a cleaner text for amount extraction.
        If omitted the function works on `text` alone (original behaviour).

    Returns
    -------
    dict with keys:
        merchant          – str | None
        amount            – float | None
        transaction_date  – str | None  (ISO "YYYY-MM-DD")
        raw_text          – str
        category          – str         (bonus field)
    """

    # If we have the image, get a higher-quality OCR pass for amount logic
    working_text = text
    if image_path:
        try:
            working_text = extract_text_from_image(image_path)
        except Exception:
            pass   # fall back to whatever text was passed in

    lines = working_text.split("\n")

    merchant         = _extract_merchant(lines)
    transaction_date = _extract_date(working_text)
    raw_amount       = _extract_amount_from_lines(lines)
    category         = _guess_category(merchant)

    # Normalise amount to float | None  (matches original contract)
    try:
        amount = float(Decimal(str(raw_amount)).quantize(Decimal("0.01"))) if raw_amount else None
    except Exception:
        amount = None

    return {
        "merchant":         merchant,
        "amount":           amount,
        "transaction_date": transaction_date,
        "raw_text":         text,          # always the original text, not re-processed
        "category":         category,
    }