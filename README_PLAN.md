# Tokyo Planner (MSP → HND), Hyatt-first


Currently, this is not modularized, so this won't work. play.py was supposed to be plan.py. I will fix it eventually.

## Quick start
Create a venv, then run the CLI.

```bash
python -m pip install -r requirements.txt  # (if you add deps later)
python -m cli.plan --noninteractive --calendar-mode fixture --start "2027-11-20" --end "2027-12-02"
