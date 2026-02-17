from __future__ import annotations
from datetime import datetime
from .models import Recommendation

def render_markdown(rec: Recommendation) -> str:
    t = rec.trip
    when = f"{t.start_date} → {t.end_date}" if t.start_date and t.end_date else "(dates not set)"
    lines = []
    lines.append(f"# Tokyo Plan ({t.origin} → {t.destination})")
    lines.append(f"- **Dates**: {when}")
    lines.append(f"- **Cabin**: {t.cabin_pref} | **Prefer Nonstop**: {t.prefer_nonstop}")
    lines.append(f"- **Hotels**: start at **{t.hotel_primary}**, consider **{', '.join(t.hotel_alternates)}**\n")
    lines.append("## Flights")
    for f in rec.flights:
        lines.append(f"- **{f.carrier} {', '.join(f.flight_numbers)}** — {'Nonstop' if f.nonstop else '1-stop'}; "
                     f"Score: {f.score:.1f}. {f.rationale}")
    lines.append("\n**Flight references**")
    lines.append("- FlightsFrom MSP→HND: https://www.flightsfrom.com/MSP-HND")
    lines.append("- FlightConnections MSP→HND: https://www.flightconnections.com/flights-from-msp-to-hnd")
    lines.append("- MSP Nonstop map: https://www.mspairport.com/flights-airlines/nonstop-route-map\n")
    lines.append("## Hotels (night-by-night)")
    pts = 0
    for n in rec.stay.nights:
        peak = " (peak)" if n.is_peak else ""
        pp = f"{n.points_price:,} pts" if n.points_price is not None else "—"
        lines.append(f"- {n.date}: **{n.hotel_name}**{peak} — {pp}")
        if n.points_price: pts += n.points_price
    lines.append(f"\n**Total points**: {pts:,}\n")
    lines.append("**Hotel references**")
    lines.append("- Park Hyatt Tokyo (Reopened Dec 9, 2025; Cat 8 35k/40k/45k): https://newsroom.hyatt.com/120925-Park-Hyatt-Tokyo-Reopens-Following-19-Month-Renovation")
    lines.append("- Park Hyatt points context: https://thepointsguy.com/news/park-hyatt-tokyo-with-points/")
    lines.append("- Andaz Tokyo: https://www.hyatt.com/andaz/en-US/tyoaz-andaz-tokyo-toranomon-hills")
    lines.append("- Andaz review & points: https://thepointsguy.com/hotel/reviews/hyatt-andaz-tokyo-toranomon-hills/")
    lines.append(f"\n_Generated: {datetime.now().isoformat(timespec='minutes')}_")
    return "\n".join(lines)
