"""API route handlers for the Points Strategy Engine."""
from __future__ import annotations
import uuid
from typing import Dict
from fastapi import APIRouter, HTTPException

from pte.assistant.session import Session
from pte.engine.scorer import score_flight, score_stay
from pte.engine.render_markdown import render_markdown
from pte.engine.models import Recommendation
from pte.providers.flights.delta_msp_hnd import propose_flights
from pte.providers.hotels.hyatt import load_calendars_for_trip, allocate_hyatt_stay

from .schemas import (
    SessionState,
    CreateSessionResponse,
    SetDatesRequest,
    SetDatesResponse,
    SetHotelRequest,
    SetHotelResponse,
    SetNonstopRequest,
    SetNonstopResponse,
    GeneratePlanResponse,
    FlightOptionSchema,
    HotelNightSchema,
    StayPlanSchema,
)

router = APIRouter(prefix="/api")

# In-memory session store
sessions: Dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    """Get session by ID or raise 404."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return sessions[session_id]


def session_to_state(session_id: str, session: Session) -> SessionState:
    """Convert internal Session to API SessionState."""
    return SessionState(
        session_id=session_id,
        origin=session.origin,
        destination=session.destination,
        start_date=session.start_date,
        end_date=session.end_date,
        prefer_nonstop=session.prefer_nonstop,
        hotel_primary=session.hotel_primary,
        hotel_alternates=session.hotel_alternates,
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "points-strategy-engine"}


@router.post("/session", response_model=CreateSessionResponse)
async def create_session():
    """Create a new planning session."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session()
    return CreateSessionResponse(
        session_id=session_id,
        state=session_to_state(session_id, sessions[session_id]),
    )


@router.get("/session/{session_id}", response_model=SessionState)
async def get_session_state(session_id: str):
    """Get current session state."""
    session = get_session(session_id)
    return session_to_state(session_id, session)


@router.post("/session/{session_id}/dates", response_model=SetDatesResponse)
async def set_dates(session_id: str, request: SetDatesRequest):
    """Set trip dates."""
    session = get_session(session_id)
    message = session.set_dates(request.start_date, request.end_date)
    return SetDatesResponse(
        message=message,
        state=session_to_state(session_id, session),
    )


@router.post("/session/{session_id}/hotel", response_model=SetHotelResponse)
async def set_hotel(session_id: str, request: SetHotelRequest):
    """Set primary hotel."""
    session = get_session(session_id)
    message = session.set_start_hotel(request.hotel)
    return SetHotelResponse(
        message=message,
        state=session_to_state(session_id, session),
    )


@router.post("/session/{session_id}/nonstop", response_model=SetNonstopResponse)
async def set_nonstop(session_id: str, request: SetNonstopRequest):
    """Set nonstop preference."""
    session = get_session(session_id)
    message = session.set_nonstop(request.prefer_nonstop)
    return SetNonstopResponse(
        message=message,
        state=session_to_state(session_id, session),
    )


@router.post("/session/{session_id}/generate", response_model=GeneratePlanResponse)
async def generate_plan(session_id: str):
    """Generate the travel plan."""
    session = get_session(session_id)
    trip = session.to_trip()

    if not trip.start_date or not trip.end_date:
        raise HTTPException(
            status_code=400,
            detail="Please set both start and end dates first.",
        )

    # Generate flights
    flights = propose_flights(trip)
    for f in flights:
        score_flight(f)

    # Generate hotel stay
    calendars = load_calendars_for_trip(
        trip,
        mode=session.calendar_mode,
        import_paths=session.import_paths,
    )
    stay = allocate_hyatt_stay(
        trip,
        session.hotel_primary,
        session.hotel_alternates,
        calendars,
        session.prefer_single_hotel,
    )
    score_stay(stay)

    # Create recommendation and render markdown
    rec = Recommendation(trip=trip, flights=flights, stay=stay)
    markdown = render_markdown(rec)

    # Convert to API schemas
    flight_schemas = [
        FlightOptionSchema(
            carrier=f.carrier,
            flight_numbers=f.flight_numbers,
            cabin=f.cabin,
            nonstop=f.nonstop,
            origin=f.origin,
            destination=f.destination,
            depart_time_local=f.depart_time_local,
            arrive_time_local=f.arrive_time_local,
            duration_minutes=f.duration_minutes,
            score=f.score,
            rationale=f.rationale,
        )
        for f in flights
    ]

    hotel_schemas = [
        HotelNightSchema(
            date=n.date,
            hotel_name=n.hotel_name,
            program=n.program,
            points_price=n.points_price,
            cash_price=n.cash_price,
            is_peak=n.is_peak,
            notes=n.notes,
        )
        for n in stay.nights
    ]

    stay_schema = StayPlanSchema(
        nights=hotel_schemas,
        total_points=stay.total_points(),
        total_cash=stay.total_cash(),
    )

    return GeneratePlanResponse(
        message="Plan generated successfully",
        markdown=markdown,
        flights=flight_schemas,
        stay=stay_schema,
        state=session_to_state(session_id, session),
    )
