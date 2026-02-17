from pte.nlp.intent import parse_query
from datetime import date

def test_parse_dates_range():
    i = parse_query("Nov 20 2027 to Dec 4 2027")
    assert i.name == "set_dates"
    assert i.slots["start"] == date(2027,11,20)
    assert i.slots["end"] == date(2027,12,4)

def test_nonstop_yes():
    i = parse_query("Prefer nonstop and direct flights")
    assert i.name == "set_nonstop" and i.slots["prefer_nonstop"] is True

def test_start_hotel():
    i = parse_query("Start at Park Hyatt")
    assert i.name == "set_start_hotel" and "Park Hyatt Tokyo" in i.slots["hotel"]
