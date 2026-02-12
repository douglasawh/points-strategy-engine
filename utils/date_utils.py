# utils/date_utils.py
from __future__ import annotations
from datetime import datetime, date

def parse_date_or_none(s: str) -> date | None:
    """
    Try multiple human-friendly formats, else return None.
    """
    if not s:
        return None
    patterns = [
        "%Y-%m-%d",    # 2027-11-20
        "%b %d %Y",    # Nov 20 2027
        "%B %d %Y",    # November 20 2027
        "%m/%d/%Y",    # 11/20/2027
        "%m/%d/%y",    # 11/20/27
    ]
    for p in patterns:
        try:
            return datetime.strptime(s, p).date()
        except ValueError:
            continue
    return None

def validate_date_range(start: date | None, end: date | None) -> tuple[bool, str]:
    if not start or not end:
        return False, "Start and end dates are required."
    if end <= start:
        return False, "End date must be after start date."
    return True, ""
