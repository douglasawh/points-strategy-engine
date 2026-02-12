# engine/scorer.py
from __future__ import annotations
from typing import Optional
from .models import FlightOption, StayPlan

DEFAULT_WEIGHTS = {
    "nonstop_bonus": 40.0,
    "time_quality": 10.0,      # placeholder for schedule fit (not used deeply here)
    "points_value": 30.0,
    "cash_value": 10.0,
    "loyalty_alignment": 10.0,
}

def score_flight(option: FlightOption, weights=DEFAULT_WEIGHTS) -> float:
    score = 0.0
    if option.nonstop:
        score += weights["nonstop_bonus"]  # DL121/DL120 MSP↔HND nonstop as primary. Sources: flightsfrom & flightconnections. [2](https://www.flightsfrom.com/MSP-HND)[1](https://www.flightconnections.com/flights-from-msp-to-hnd)
    # Time quality & duration could be mapped here if you ingest schedules.
    option.score = score
    option.rationale = "Nonstop bonus applied." if option.nonstop else "One-stop fallback."
    return score

def score_stay(stay: StayPlan, hyatt_cents_per_point: float = 2.0) -> float:
    """
    Convert the stay into a 'savings score' vs. hypothetical cash.
    If points/cash missing, do not count. This keeps the scorer honest when data is unknown.
    """
    points = stay.total_points()
    cash  = stay.total_cash()
    score = 0.0
    if points and cash:
        est_points_value = points * hyatt_cents_per_point / 100.0
        # Higher 'score' if the points save more vs. cash.
        score = max(0.0, cash - est_points_value)
    return score
