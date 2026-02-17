from __future__ import annotations
from .models import FlightOption, StayPlan

DEFAULT_WEIGHTS = {"nonstop_bonus": 40.0}

def score_flight(option: FlightOption, weights=DEFAULT_WEIGHTS) -> float:
    score = weights["nonstop_bonus"] if option.nonstop else 0.0
    option.score = score
    option.rationale = "Nonstop MSP↔HND (preferred)." if option.nonstop else "One-stop fallback."
    return score

def score_stay(stay: StayPlan, hyatt_cents_per_point: float = 2.0) -> float:
    points = stay.total_points()
    cash = stay.total_cash()
    if points and cash:
        est_value = points * hyatt_cents_per_point / 100.0
        return max(0.0, cash - est_value)
    return 0.0
