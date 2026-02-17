from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import date
from pte.engine.models import Trip, HotelNight, StayPlan, daterange

HYATT_META = {
    "Park Hyatt Tokyo": {
        "program": "World of Hyatt",
        "award_points": [35000, 40000, 45000],  # off/standard/peak
        "neighborhood": "Shinjuku",
    },
    "Andaz Tokyo Toranomon Hills": {
        "program": "World of Hyatt",
        "award_points": [35000, 40000, 45000],
        "neighborhood": "Minato (Toranomon)",
    }
}

@dataclass
class HyattCalendar:
    nightly_points: Dict[date, Optional[int]]

def load_calendar_from_import(path: str) -> HyattCalendar:
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

def load_calendar_from_fixture(hotel_name: str, start: date, end: date) -> HyattCalendar:
    from datetime import timedelta
    off, std, peak = HYATT_META[hotel_name]["award_points"]
    nightly = {}
    d = start
    i = 0
    while d < end:
        nightly[d] = [off, std, peak][i % 3]  # synthetic cycle for testing
        d += timedelta(days=1)
        i += 1
    return HyattCalendar(nightly)

def get_hotel_meta(hotel_name: str) -> Dict:
    return HYATT_META[hotel_name]

def allocate_hyatt_stay(trip: Trip, start_hotel: str, alternates: List[str],
                        calendars: Dict[str, HyattCalendar], prefer_single_hotel: bool=False) -> StayPlan:
    if not trip.start_date or not trip.end_date:
        return StayPlan([])
    nights: List[HotelNight] = []
    main_cal = calendars.get(start_hotel)
    alt_cals = {h: calendars[h] for h in alternates if h in calendars}
    for d in daterange(trip.start_date, trip.end_date):
        main_pts = main_cal.nightly_points.get(d) if main_cal else None
        chosen_hotel = start_hotel
        chosen_pts = main_pts
        chosen_is_peak = True if main_pts == 45000 else False
        for alt_name, alt_cal in alt_cals.items():
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
            date=d, hotel_name=chosen_hotel, program=meta["program"],
            points_price=chosen_pts, cash_price=None, is_peak=chosen_is_peak, notes=""
        ))
    return StayPlan(nights)

def load_calendars_for_trip(trip: Trip, mode: str="import", import_paths: Optional[Dict[str, str]]=None) -> Dict[str, HyattCalendar]:
    calendars: Dict[str, HyattCalendar] = {}
    hotels = [trip.hotel_primary] + trip.hotel_alternates
    if mode == "import":
        if not import_paths:
            raise ValueError("import_paths required for 'import' mode")
        for h in hotels:
            calendars[h] = load_calendar_from_import(import_paths[h])
    elif mode == "fixture":
        if not trip.start_date or not trip.end_date:
            raise ValueError("Need dates for fixture mode")
        for h in hotels:
            calendars[h] = load_calendar_from_fixture(h, trip.start_date, trip.end_date)
    else:
        raise NotImplementedError("live mode not implemented.")
    return calendars

