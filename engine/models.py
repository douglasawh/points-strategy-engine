# engine/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple

# --- Core data models ---

@dataclass
class Trip:
    origin: str
    destination: str
    start_date: Optional[date]
    end_date: Optional[date]
    pax: int = 2
    cabin_pref: str = "business"
    prefer_nonstop: bool = True
    hotel_primary: str = "Park Hyatt Tokyo"
    hotel_alternates: List[str] = field(default_factory=lambda: ["Andaz Tokyo Toranomon Hills"])
    program_priority: List[str] = field(default_factory=lambda: ["World of Hyatt"])
    notes: str = ""

@dataclass
class FlightOption:
    carrier: str
    flight_numbers: List[str]
    cabin: str
    nonstop: bool
    origin: str
    destination: str
    depart_time_local: Optional[str] = None
    arrive_time_local: Optional[str] = None
    duration_minutes: Optional[int] = None
    score: float = 0.0
    rationale: str = ""

@dataclass
class HotelNight:
    date: date
    hotel_name: str
    program: str
    points_price: Optional[int]  # None if unknown
    cash_price: Optional[float]  # None if unknown
    is_peak: Optional[bool]
    notes: str = ""

@dataclass
class StayPlan:
    nights: List[HotelNight] = field(default_factory=list)

    def total_points(self) -> int:
        return sum(n.points_price for n in self.nights if n.points_price is not None)

    def total_cash(self) -> float:
        return sum(n.cash_price for n in self.nights if n.cash_price is not None)

@dataclass
class Recommendation:
    trip: Trip
    flights: List[FlightOption]
    stay: StayPlan
    summary: str = ""
    caveats: List[str] = field(default_factory=list)

# --- Utility helpers ---

def daterange(start: date, end: date):
    """Yield dates from start (inclusive) to end (exclusive)."""
    d = start
    while d < end:
        yield d
        from datetime import timedelta
        d += timedelta(days=1)
