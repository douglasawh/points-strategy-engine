# providers/hotels/hyatt.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import date
from ...engine.models import Trip, HotelNight, StayPlan, daterange

# --- Static metadata (sourced) ---

HYATT_META = {
    # Park Hyatt: reopened Dec 9, 2025; Cat 8; 35/40/45k — source: Hyatt newsroom & TPG. [4](https://newsroom.hyatt.com/120925-Park-Hyatt-Tokyo-Reopens-Following-19-Month-Renovation)[5](https://thepointsguy.com/news/park-hyatt-tokyo-with-points/)
    "Park Hyatt Tokyo": {
        "brand": "Park Hyatt",
        "program": "World of Hyatt",
        "category": 8,
        "award_points": [35000, 40000, 45000],  # off-peak, standard, peak
        "neighborhood": "Shinjuku",
    },
    # Andaz Tokyo: Category 8; standard ~40k; peak varies — source: TPG review. [6](https://thepointsguy.com/hotel/reviews/hyatt-andaz-tokyo-toranomon-hills/)
    "Andaz Tokyo Toranomon Hills": {
        "brand": "Andaz",
        "program": "World of Hyatt",
        "category": 8,
        "award_points": [35000, 40000, 45000],
        "neighborhood": "Minato (Toranomon)",
    }
}

@dataclass
class HyattCalendar:
    """date → points (None if unknown); is_peak heuristic if points==45000"""
    nightly_points: Dict[date, Optional[int]]

def load_calendar_from_fixture(hotel_name: str, start: date, end: date) -> HyattCalendar:
    """
    TEST-ONLY fixture with synthetic data for ~2 weeks pattern.
    Marked clearly as synthetic; do not use to make final bookings.
    """
    from datetime import timedelta
    off, std, peak = HYATT_META[hotel_name]["award_points"]
    nightly = {}
    d = start
    i = 0
    while d < end:
        # simple repeating pattern off/std/peak … purely for testing the allocator
        nightly[d] = [off, std, peak][i % 3]
        d += timedelta(days=1)
        i += 1
    return HyattCalendar(nightly)

def load_calendar_from_import(path: str) -> HyattCalendar:
    """
    Load a CSV/JSON you exported from Hyatt's points calendar:
    CSV columns: date, points
    JSON structure: { "YYYY-MM-DD": points }
    """
    import os, json, csv
    nightly = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Calendar file not found: {path}")
    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            for k, v in raw.items():
                nightly[date.fromisoformat(k)] = int(v) if v is not None else None
    else:
        with open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                nightly[date.fromisoformat(row["date"])] = int(row["points"]) if row["points"] else None
    return HyattCalendar(nightly)

def get_hotel_meta(hotel_name: str) -> Dict:
    if hotel_name not in HYATT_META:
        raise KeyError(f"Unknown Hyatt property: {hotel_name}")
    return HYATT_META[hotel_name]

def allocate_hyatt_stay(
    trip: Trip,
    start_hotel: str,
    alternates: List[str],
    calendars: Dict[str, HyattCalendar],
    prefer_single_hotel: bool = False
) -> StayPlan:
    """
    Decide whether to stay put at Park Hyatt or move nights to Andaz to save points.
    Strategy:
    1) Try to keep as many nights at start_hotel as possible.
    2) For nights priced 'peak' (e.g., 45k) at start_hotel, compare alternate's price.
       If the alternate is cheaper by >= 5k points that night, switch that night.
    3) If prefer_single_hotel=True, only switch if savings >= 10k per switched night.
    """
    if not trip.start_date or not trip.end_date:
        return StayPlan([])

    nights: List[HotelNight] = []
    main_cal = calendars.get(start_hotel)
    alt_calendars = {h: calendars[h] for h in alternates if h in calendars}

    for d in daterange(trip.start_date, trip.end_date):
        main_pts = main_cal.nightly_points.get(d) if main_cal else None
        chosen_hotel = start_hotel
        chosen_pts = main_pts
        chosen_is_peak = True if main_pts == 45000 else False

        # Compare alternates
        for alt_name, alt_cal in alt_calendars.items():
            alt_pts = alt_cal.nightly_points.get(d)
            if alt_pts is None or main_pts is None:
                continue
            threshold = 10000 if prefer_single_hotel else 5000
            if alt_pts + threshold <= main_pts:
                chosen_hotel = alt_name
                chosen_pts = alt_pts
                chosen_is_peak = True if alt_pts == 45000 else False
                break

        meta = get_hotel_meta(chosen_hotel)
        nights.append(HotelNight(
            date=d,
            hotel_name=chosen_hotel,
            program=meta["program"],
            points_price=chosen_pts,
            cash_price=None,   # You can add cash scraping/import later
            is_peak=chosen_is_peak,
            notes=""
        ))

    return StayPlan(nights)

def load_calendars_for_trip(
    trip: Trip,
    mode: str = "import",
    import_paths: Optional[Dict[str, str]] = None
) -> Dict[str, HyattCalendar]:
    """
    mode:
      - 'import': read your CSV/JSON exports (recommended)
      - 'fixture': synthetic test data (clearly marked)
      - 'live': (future) scrape Hyatt site (not implemented here)
    """
    calendars: Dict[str, HyattCalendar] = {}
    hotels = [trip.hotel_primary] + trip.hotel_alternates
    if mode == "import":
        if not import_paths:
            raise ValueError("import_paths required when calendar mode='import'")
        for h in hotels:
            calendars[h] = load_calendar_from_import(import_paths[h])
    elif mode == "fixture":
        if not trip.start_date or not trip.end_date:
            raise ValueError("Need dates to build fixture calendar")
        for h in hotels:
            calendars[h] = load_calendar_from_fixture(h, trip.start_date, trip.end_date)
    else:
        raise NotImplementedError("calendar mode 'live' is not implemented yet.")
    return calendars
