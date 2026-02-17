from __future__ import annotations
from typing import List
from pte.engine.models import Trip, FlightOption

def get_msp_hnd_primary(trip: Trip) -> FlightOption:
    return FlightOption(
        carrier="Delta Air Lines",
        flight_numbers=["DL121 (MSP→HND)", "DL120 (HND→MSP)"],
        cabin=trip.cabin_pref,
        nonstop=True,
        origin="MSP",
        destination="HND",
        depart_time_local="~11:30",
        arrive_time_local="~15:20+1",
        duration_minutes=765
    )

def get_msp_hnd_fallbacks(trip: Trip) -> List[FlightOption]:
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
    options: List[FlightOption] = []
    primary = get_msp_hnd_primary(trip)
    if trip.prefer_nonstop:
        options.append(primary)
    options.extend(get_msp_hnd_fallbacks(trip))
    return options
