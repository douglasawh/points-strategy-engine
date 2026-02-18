# pte/assistant/session.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date
from pte.engine.models import Trip, Recommendation
from pte.engine.scorer import score_flight, score_stay
from pte.engine.render_markdown import render_markdown
from pte.providers.flights.delta_msp_hnd import propose_flights
from pte.providers.hotels.hyatt import load_calendars_for_trip, allocate_hyatt_stay
from pte.utils.date_utils import validate_date_range

@dataclass
class Session:
    # Core trip state
    origin: str = "MSP"
    destination: str = "HND"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prefer_nonstop: bool = True
    hotel_primary: str = "Park Hyatt Tokyo"
    hotel_alternates: List[str] = field(default_factory=lambda: ["Andaz Tokyo Toranomon Hills"])
    prefer_single_hotel: bool = False

    # Provider config
    calendar_mode: str = "fixture"   # 'fixture' or 'import'
    import_paths: Optional[Dict[str, str]] = None

    # Last recommendation text
    last_markdown_path: Optional[str] = None

    def to_trip(self) -> Trip:
        return Trip(
            origin=self.origin, destination=self.destination,
            start_date=self.start_date, end_date=self.end_date,
            prefer_nonstop=self.prefer_nonstop,
            hotel_primary=self.hotel_primary, hotel_alternates=self.hotel_alternates
        )

    def set_dates(self, start: Optional[date], end: Optional[date]) -> str:
        if start and end:
            ok, msg = validate_date_range(start, end)
            if not ok:
                return f"❌ {msg}"
        self.start_date = start or self.start_date
        self.end_date = end or self.end_date
        return f"✅ Dates set: {self.start_date} → {self.end_date}"

    def set_nonstop(self, prefer: bool) -> str:
        self.prefer_nonstop = prefer
        return f"✅ Nonstop preference: {self.prefer_nonstop}"

    def set_start_hotel(self, hotel: str) -> str:
        self.hotel_primary = hotel
        # ensure alternates has the counterpart
        counterpart = "Andaz Tokyo Toranomon Hills" if hotel == "Park Hyatt Tokyo" else "Park Hyatt Tokyo"
        if counterpart not in self.hotel_alternates:
            self.hotel_alternates.append(counterpart)
        return f"✅ Start at: {self.hotel_primary} (alternates: {', '.join(self.hotel_alternates)})"

    def add_alternate(self, hotel: str) -> str:
        if hotel not in self.hotel_alternates and hotel != self.hotel_primary:
            self.hotel_alternates.append(hotel)
        return f"✅ Alternate added: {hotel} (now: {', '.join(self.hotel_alternates)})"

    def generate_plan(self, out_path: str) -> str:
        trip = self.to_trip()
        if not trip.start_date or not trip.end_date:
            return "❌ Please set both start and end dates first."

        # Flights
        flights = propose_flights(trip)
        for f in flights:
            score_flight(f)

        # Hotels
        calendars = load_calendars_for_trip(trip, mode=self.calendar_mode, import_paths=self.import_paths)
        stay = allocate_hyatt_stay(trip, self.hotel_primary, self.hotel_alternates, calendars, self.prefer_single_hotel)
        _ = score_stay(stay)

        rec = Recommendation(trip=trip, flights=flights, stay=stay)
        md = render_markdown(rec)
        import os
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        self.last_markdown_path = out_path
        return f"📝 Plan saved to: {out_path}"
