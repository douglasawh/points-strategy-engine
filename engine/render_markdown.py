# engine/render_markdown.py
from __future__ import annotations
from datetime import datetime
from .models import Recommendation

def render_markdown(rec: Recommendation) -> str:
    t = rec.trip
    lines = []
    lines.append(f"# Tokyo Plan ({t.origin} → {t.destination})")
    when = f"{t.start_date} → {t.end_date}" if t.start_date and t.end_date else "Dates: (not set)"
    lines.append(f"- **Dates**: {when}")
    lines.append(f"- **Pax**: {t.pax} | **Cabin**: {t.cabin_pref} | **Prefer Nonstop**: {t.prefer_nonstop}")
    lines.append(f"- **Hotel Pref**: start at **{t.hotel_primary}**, consider **{', '.join(t.hotel_alternates)}**")
    lines.append("")
    lines.append("## Flights")
    for f in rec.flights:
        lines.append(f"- **{f.carrier} {', '.join(f.flight_numbers)}** — "
                     f"{'Nonstop' if f.nonstop else '1-stop'}; "
                     f"Score: {f.score:.1f}. {f.rationale}")
    lines.append("")
    lines.append("**Source notes**: MSP↔HND daily nonstop and terminals validated via published schedules and airport route maps. "
                 "(See schedules on FlightsFrom & FlightConnections; MSP nonstop map.) "
                 "[FlightsFrom](https://www.flightsfrom.com/MSP-HND), [FlightConnections](https://www.flightconnections.com/flights-from-msp-to-hnd), [MSP Route Map](https://www.mspairport.com/flights-airlines/nonstop-route-map)")
    lines.append("")
    lines.append("## Hotels (night-by-night)")
    total_pts = 0
    total_cash = 0.0
    for n in rec.stay.nights:
        pp = f"{n.points_price:,} pts" if n.points_price is not None else "—"
        cp = f"${n.cash_price:,.0f}" if n.cash_price is not None else "—"
        peak = " (peak)" if n.is_peak else ""
        lines.append(f"- {n.date}: **{n.hotel_name}**{peak} — {pp} / {cp}")
        if n.points_price: total_pts += n.points_price
        if n.cash_price: total_cash += n.cash_price

    lines.append("")
    lines.append(f"**Totals**: {total_pts:,} points; cash data total ${total_cash:,.0f} (if provided)")
    lines.append("")
    lines.append("**Hyatt references**: Park Hyatt Tokyo (reopened Dec 9, 2025; Category 8, 35k/40k/45k) and Andaz Tokyo (Category 8). "
                 "See: Hyatt newsroom & TPG Andaz review. "
                 "[Hyatt Newsroom](https://newsroom.hyatt.com/120925-Park-Hyatt-Tokyo-Reopens-Following-19-Month-Renovation), [TPG Andaz Review](https://thepointsguy.com/hotel/reviews/hyatt-andaz-tokyo-toranomon-hills/)")
    if rec.caveats:
        lines.append("\n## Caveats")
        for c in rec.caveats:
            lines.append(f"- {c}")
    lines.append(f"\n_Generated: {datetime.now().isoformat(timespec='minutes')}_")
    return "\n".join(lines)
