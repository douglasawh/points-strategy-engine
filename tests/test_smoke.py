from datetime import date
from pte.utils.date_utils import parse_date_or_none, validate_date_range
from pte.engine.models import Trip
from pte.providers.hotels.hyatt import load_calendar_from_fixture, allocate_hyatt_stay

def test_parse_and_validate_dates():
    assert parse_date_or_none("2027-11-20") == date(2027,11,20)
    assert parse_date_or_none("Dec 4 2027") == date(2027,12,4)
    ok, msg = validate_date_range(date(2027,11,20), date(2027,12,4))
    assert ok and msg == ""

def test_allocator_runs():
    trip = Trip(origin="MSP", destination="HND",
                start_date=date(2027,11,20), end_date=date(2027,11,23))
    ph = load_calendar_from_fixture("Park Hyatt Tokyo", trip.start_date, trip.end_date)
    az = load_calendar_from_fixture("Andaz Tokyo Toranomon Hills", trip.start_date, trip.end_date)
    calendars = {"Park Hyatt Tokyo": ph, "Andaz Tokyo Toranomon Hills": az}
    stay = allocate_hyatt_stay(trip, "Park Hyatt Tokyo", ["Andaz Tokyo Toranomon Hills"], calendars)
    assert len(stay.nights) == 3
