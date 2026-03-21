"""Pydantic models for API request/response schemas."""
from __future__ import annotations
from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class FlightOptionSchema(BaseModel):
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


class HotelNightSchema(BaseModel):
    date: date
    hotel_name: str
    program: str
    points_price: Optional[int] = None
    cash_price: Optional[float] = None
    is_peak: Optional[bool] = None
    notes: str = ""


class StayPlanSchema(BaseModel):
    nights: List[HotelNightSchema] = []
    total_points: int = 0
    total_cash: float = 0.0


class SessionState(BaseModel):
    session_id: str
    origin: str = "MSP"
    destination: str = "HND"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prefer_nonstop: bool = True
    hotel_primary: str = "Park Hyatt Tokyo"
    hotel_alternates: List[str] = ["Andaz Tokyo Toranomon Hills"]


class CreateSessionResponse(BaseModel):
    session_id: str
    state: SessionState


class SetDatesRequest(BaseModel):
    start_date: date
    end_date: date


class SetDatesResponse(BaseModel):
    message: str
    state: SessionState


class SetHotelRequest(BaseModel):
    hotel: str


class SetHotelResponse(BaseModel):
    message: str
    state: SessionState


class SetNonstopRequest(BaseModel):
    prefer_nonstop: bool


class SetNonstopResponse(BaseModel):
    message: str
    state: SessionState


class GeneratePlanResponse(BaseModel):
    message: str
    markdown: str
    flights: List[FlightOptionSchema]
    stay: StayPlanSchema
    state: SessionState


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
