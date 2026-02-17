# pte/nlp/intent.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from datetime import date
from pte.utils.date_utils import parse_date_or_none

@dataclass
class Intent:
    name: str
    slots: Dict[str, Any]

# --- Helpers --------------------------------------------------------------

MONTHS = "(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
DATE_RX = re.compile(
    rf"(?P<m1>{MONTHS})\w*\s+(?P<d1>\d{{1,2}})\s*(?P<y1>\d{{2,4}})?"
    r"(?:\s*(?:to|-|through|thru|–)\s*)"
    rf"(?P<m2>{MONTHS})\w*\s+(?P<d2>\d{{1,2}})\s*(?P<y2>\d{{2,4}})?",
    re.IGNORECASE,
)

ISO_RANGE_RX = re.compile(
    r"(?P<s>\d{4}-\d{2}-\d{2})\s*(?:to|-|through|thru|–)\s*(?P<e>\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)

SINGLE_DATE_RX = re.compile(
    rf"(on|starting|start|begin)\s+(?P<m>{MONTHS})\w*\s+(?P<d>\d{{1,2}})\s*(?P<y>\d{{2,4}})?",
    re.IGNORECASE,
)

def _norm_year(y: Optional[str]) -> Optional[str]:
    if not y:
        return None
    y = y.strip()
    if len(y) == 2:
        return "20" + y
    return y

def extract_date_range(text: str) -> Tuple[Optional[date], Optional[date]]:
    """Find 'Nov 20 2027 to Dec 4 2027' or '2027-11-20 to 2027-12-04'."""
    # ISO first
    m = ISO_RANGE_RX.search(text)
    if m:
        s = parse_date_or_none(m.group("s"))
        e = parse_date_or_none(m.group("e"))
        return s, e
    # Natural language month names
    m = DATE_RX.search(text)
    if m:
        m1, d1, y1 = m.group("m1"), m.group("d1"), _norm_year(m.group("y1"))
        m2, d2, y2 = m.group("m2"), m.group("d2"), _norm_year(m.group("y2"))
        s = parse_date_or_none(f"{m1} {d1} {y1 or ''}".strip())
        e = parse_date_or_none(f"{m2} {d2} {y2 or ''}".strip())
        return s, e
    return None, None

def extract_single_date(text: str) -> Optional[date]:
    m = SINGLE_DATE_RX.search(text)
    if m:
        mon, d, y = m.group("m"), m.group("d"), _norm_year(m.group("y"))
        return parse_date_or_none(f"{mon} {d} {y or ''}".strip())
    return None

def yes_no(text: str, *keywords) -> Optional[bool]:
    """Return True/False if a keyword is negated/affirmed in text."""
    txt = text.lower()
    for k in keywords:
        if k in txt:
            # detect negation near the keyword
            window = 8
            idx = txt.find(k)
            left = txt[max(0, idx - window):idx]
            if "no " in left or "not " in left or "without " in left:
                return False
            return True
    return None

def mentions(text: str, *options) -> Optional[str]:
    txt = text.lower()
    for o in options:
        if o.lower() in txt:
            return o
    return None

# --- Intents -------------------------------------------------------------

def parse_query(text: str) -> Intent:
    """
    Very small, deterministic parser for our travel domain.
    Intents:
      - plan_trip
      - set_dates
      - set_nonstop
      - set_start_hotel
      - add_alternate_hotel
      - show_plan
      - help
      - reset
      - quit
    """
    t = text.strip()
    low = t.lower()
    if low in {"quit", "exit", "q"}:
        return Intent("quit", {})
    if low in {"help", "commands", "options"}:
        return Intent("help", {})

    # Dates
    s, e = extract_date_range(t)
    if s and e:
        return Intent("set_dates", {"start": s, "end": e})
    sd = extract_single_date(t)
    if sd:
        return Intent("set_dates", {"start": sd, "end": None})

    # Nonstop preference
    ns = yes_no(t, "nonstop", "direct", "no connections")
    if ns is not None:
        return Intent("set_nonstop", {"prefer_nonstop": ns})

    # Start hotel
    start_hotel = mentions(t, "Park Hyatt Tokyo", "Andaz Tokyo Toranomon Hills", "Park Hyatt", "Andaz Tokyo", "Andaz")
    if start_hotel:
        # normalize to canonical names
        if start_hotel.lower().startswith("park hyatt"):
            start_hotel = "Park Hyatt Tokyo"
        elif start_hotel.lower().startswith("andaz"):
            start_hotel = "Andaz Tokyo Toranomon Hills"
        return Intent("set_start_hotel", {"hotel": start_hotel})

    # Alternate hotel
    alt_flag = ("alternate" in low or "also consider" in low or "or andaz" in low or "or park hyatt" in low)
    if alt_flag:
        alt = mentions(t, "Park Hyatt Tokyo", "Andaz Tokyo Toranomon Hills", "Park Hyatt", "Andaz Tokyo", "Andaz")
        if alt:
            if alt.lower().startswith("park hyatt"):
                alt = "Park Hyatt Tokyo"
            elif alt.lower().startswith("andaz"):
                alt = "Andaz Tokyo Toranomon Hills"
            return Intent("add_alternate_hotel", {"hotel": alt})

    # Show/Plan
    if any(k in low for k in ["show plan", "generate plan", "make plan", "plan this", "save plan"]):
        return Intent("show_plan", {})

    # Default to high-level "plan_trip" intent
    return Intent("plan_trip", {})
