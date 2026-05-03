import os
import requests
from dotenv import load_dotenv

load_dotenv()
manager_id = os.getenv("FPL_MANAGER_ID") or "1147719"

team_picks_data = requests.get(f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/1/picks/").json()
for pick in team_picks_data.get('picks', []):
    print(pick)
