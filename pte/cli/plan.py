from __future__ import annotations
import argparse, os
from getpass import getuser

from pte.utils.date_utils import parse_date_or_none, validate_date_range
from pte.engine.models import Trip, Recommendation
from pte.engine.scorer import score_flight, score_stay
from pte.engine.render_markdown import render_markdown
from pte.providers.flights.delta_msp_hnd import propose_flights
from pte.providers.hotels.hyatt import load_calendars_for_trip, allocate_hyatt_stay

def prompt_if_missing(args):
    start = parse_date_or_none(args.start)
    end   = parse_date_or_none(args.end)
    while (start is None or end is None) and not args.noninteractive:
        print("Enter trip dates (e.g., 2027-11-20). Leave blank to skip.")
        if start is None: start = parse_date_or_none(input("Start date: ").strip())
        if end   is None: end   = parse_date_or_none(input("End date: ").strip())
        if start and end:
            ok, msg = validate_date_range(start, end)
            if not ok: print("Error:", msg); start, end = None, None
    prefer_nonstop = args.nonstop
    if prefer_nonstop is None and not args.noninteractive:
        prefer_nonstop = input("Prefer nonstop? [Y/n]: ").strip().lower() != 'n'
    start_hotel = args.start_hotel or "Park Hyatt Tokyo"
    if not args.noninteractive:
        ans = input(f"Start at Park Hyatt Tokyo? [Y/n] (current: {start_hotel}): ").strip().lower()
        if ans == 'n': start_hotel = "Andaz Tokyo Toranomon Hills"
    alternates = args.alternates or (["Andaz Tokyo Toranomon Hills"] if start_hotel == "Park Hyatt Tokyo" else ["Park Hyatt Tokyo"])
    return start, end, bool(prefer_nonstop), start_hotel, alternates

def main():
    ap = argparse.ArgumentParser(description="Plan Tokyo (MSP→HND) with Hyatt strategy.")
    ap.add_argument("--origin", default="MSP")
    ap.add_argument("--destination", default="HND")
    ap.add_argument("--start", help="Start date (e.g., 2027-11-20)")
    ap.add_argument("--end", help="End date (e.g., 2027-12-04)")
    ap.add_argument("--nonstop", type=lambda s: s.lower() in ("1","true","y","yes"), default=None)
    ap.add_argument("--start-hotel", choices=["Park Hyatt Tokyo","Andaz Tokyo Toranomon Hills"])
    ap.add_argument("--alternates", nargs="*", help="Alternate hotels to consider")
    ap.add_argument("--calendar-mode", choices=["import","fixture"], default="fixture")
    ap.add_argument("--calendar-file", action="append", help="Repeatable: hotel_name=path (for import mode)")
    ap.add_argument("--prefer-single-hotel", action="store_true")
    ap.add_argument("--noninteractive", action="store_true")
    ap.add_argument("--out", default=f"out/tokyo-plan-{getuser()}.md")
    args = ap.parse_args()

    start, end, prefer_nonstop, start_hotel, alternates = prompt_if_missing(args)

    trip = Trip(origin=args.origin, destination=args.destination,
                start_date=start, end_date=end,
                prefer_nonstop=prefer_nonstop,
                hotel_primary=start_hotel, hotel_alternates=alternates)

    flights = propose_flights(trip)
    for f in flights: score_flight(f)

    import_paths = None
    if args.calendar_mode == "import":
        import_paths = {}
        for kv in args.calendar_file or []:
            if "=" not in kv: raise SystemExit("Use --calendar-file 'Hotel Name=path'")
            k, v = kv.split("=", 1); import_paths[k.strip()] = v.strip()

    calendars = load_calendars_for_trip(trip, mode=args.calendar_mode, import_paths=import_paths)
    stay = allocate_hyatt_stay(trip, start_hotel=start_hotel, alternates=alternates,
                               calendars=calendars, prefer_single_hotel=args.prefer_single_hotel)

    rec = Recommendation(trip=trip, flights=flights, stay=stay)
    _ = score_stay(stay)

    md = render_markdown(rec)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f: f.write(md)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
