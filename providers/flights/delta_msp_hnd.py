# providers/flights/delta_msp_hnd.py
from __future__ import annotations
from typing import List
from datetime import date
from ...engine.models import Trip, FlightOption

def get_msp_hnd_primary(trip: Trip) -> FlightOption:
    """
    Returns the daily MSP->HND nonstop (DL121) and return (DL120) as a single 'option'.
    Facts:
    - Operated daily today by Delta MSP T1 → HND T3; block ~12h45m (A350-900).
      Sources: public schedules & route maps. [2](https://www.flightsfrom.com/MSP-HND)[1](https://www.flightconnections.com/flights-from-msp-to-hnd)
    """
    return FlightOption(
        carrier="Delta Air Lines",
        flight_numbers=["DL121 (MSP→HND)", "DL120 (HND→MSP)"],
        cabin=trip.cabin_pref,
        nonstop=True,
        origin="MSP",
        destination="HND",
        depart_time_local="~11:30",  # indicative; exact time varies by date
        arrive_time_local="~15:20+1",
        duration_minutes=765
    )

def get_msp_hnd_fallbacks(trip: Trip) -> List[FlightOption]:
    """
    Provide a few one-stop logical fallbacks (SEA/DTW/LAX) using Delta/partners.
    We don't fetch live fares here—just structured options for the scorer.
    """
    hubs = [("SEA", "Delta"), ("DTW", "Delta"), ("LAX", "Delta")]
    options: List[FlightOption] = []
    for hub, carrier in hubs:
        options.append(FlightOption(
            carrier=f"{carrier} (via {hub})",
            flight_numbers=[f"MSP→{hub}", f"{hub}→HND"],
            cabin=trip.cabin_pref,
            nonstop=False,
            origin="MSP",
            destination="HND",
            duration_minutes=900
        ))
    return options

def propose_flights(trip: Trip) -> List[FlightOption]:
    """Return the primary nonstop if preferred, else include fallbacks."""
    options: List[FlightOption] = []
    primary = get_msp_hnd_primary(trip)
    if trip.prefer_nonstop:
        options.append(primary)
    # Always propose fallbacks for robustness:
    options.extend(get_msp_hnd_fallbacks(trip))
    return options
