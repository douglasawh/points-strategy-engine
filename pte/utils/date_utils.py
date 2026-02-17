from __future__ import annotations
from datetime import datetime, date

def parse_date_or_none(s: str) -> date | None:
    if not s:
        return None
    patterns = ["%Y-%m-%d", "%b %d %Y", "%B %d %Y", "%m/%d/%Y", "%m/%d/%y"]
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

