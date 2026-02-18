# pte/cli/chat.py
from __future__ import annotations
import argparse
from getpass import getuser
from pte.nlp.intent import parse_query
from pte.assistant.session import Session

WELCOME = """\
Personal Travel Assistant — Chat Mode
Type natural language like:
  • "Plan Tokyo late 2027, nonstop, start at Park Hyatt, also consider Andaz"
  • "Nov 20 2027 to Dec 4 2027"
  • "prefer nonstop"
  • "start at Andaz"
  • "show plan"
  • "quit"

Tip: You can pass --calendar-mode import and --calendar-file "Hotel=path"
"""

def main():
    ap = argparse.ArgumentParser(description="Chat with your travel assistant.")
    ap.add_argument("--calendar-mode", choices=["fixture","import"], default="fixture")
    ap.add_argument("--calendar-file", action="append",
                    help='Repeatable: "Hotel Name=path" when using --calendar-mode import')
    ap.add_argument("--prefer-single-hotel", action="store_true")
    ap.add_argument("--out", default=f"out/tokyo-plan-{getuser()}.md")
    args = ap.parse_args()

    sess = Session(calendar_mode=args.calendar_mode, prefer_single_hotel=args.prefer_single_hotel, import_paths=None)
    if args.calendar_mode == "import":
        sess.import_paths = {}
        for kv in args.calendar_file or []:
            if "=" not in kv:
                raise SystemExit('Use --calendar-file "Hotel Name=path"')
            k, v = kv.split("=", 1)
            sess.import_paths[k.strip()] = v.strip()

    print(WELCOME)
    print(f"Calendar mode: {sess.calendar_mode}")
    if sess.import_paths:
        print(f"Imported calendars: {list(sess.import_paths.keys())}")

    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break
        if not text:
            continue
        intent = parse_query(text)

        if intent.name == "quit":
            print("bye!")
            break
        elif intent.name == "help":
            print(WELCOME)
        elif intent.name == "set_dates":
            print(sess.set_dates(intent.slots.get("start"), intent.slots.get("end")))
        elif intent.name == "set_nonstop":
            print(sess.set_nonstop(intent.slots["prefer_nonstop"]))
        elif intent.name == "set_start_hotel":
            print(sess.set_start_hotel(intent.slots["hotel"]))
        elif intent.name == "add_alternate_hotel":
            print(sess.add_alternate(intent.slots["hotel"]))
        elif intent.name in {"show_plan", "plan_trip"}:
            print(sess.generate_plan(args.out))
            if sess.last_markdown_path:
                print(f"(open {sess.last_markdown_path})")
        else:
            # Fallback: try to generate a plan
            print(sess.generate_plan(args.out))

if __name__ == "__main__":
    main()
