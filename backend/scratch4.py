import os
import requests
from dotenv import load_dotenv

load_dotenv()
manager_id = os.getenv("FPL_MANAGER_ID") or "1147719"

# check history endpoint for transfers
url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/history/"
data = requests.get(url).json()

print(data['current'][-1]) # Look at the latest GW history
