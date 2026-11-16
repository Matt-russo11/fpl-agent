"""
history_report.py - Run this to see what the database has learned so far:
    python history_report.py
It prints the results of each SQL query in database.py.
To save a fresh report first (needs internet):  python history_report.py --save
"""
import os
import sys
from dotenv import load_dotenv
import database

load_dotenv()
database.init_db()

if "--save" in sys.argv:
    from scout import analyze_team
    manager_id = os.getenv("FPL_MANAGER_ID")
    run_id = database.save_scout_report(analyze_team(manager_id))
    print("Saved new report." if run_id else "Today's report for this gameweek was already saved.")


def show(title, rows):
    print(f"\n=== {title} ===")
    if not rows:
        print("(no data yet)")
    for row in rows:
        print("  " + " | ".join(f"{k}: {v}" for k, v in row.items()))


print(f"Reports saved: {database.report_count()}")
show("Most shortlisted players", database.most_shortlisted_players())
show("Shortlist spots by team", database.team_averages())
show("Best value picks under 6.0m (latest report)", database.best_value_picks(6.0))
if len(sys.argv) > 1 and not sys.argv[-1].startswith("--"):
    show(f"History for '{sys.argv[-1]}'", database.player_history(sys.argv[-1]))
