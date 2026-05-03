import os
import requests
from dotenv import load_dotenv

load_dotenv()

manager_id = os.getenv("FPL_MANAGER_ID")
if not manager_id: manager_id = "1147719"
url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/35/picks/"
data = requests.get(url).json()

print("Entry History Keys:", data.get('entry_history', {}).keys())
print("Bank:", data.get('entry_history', {}).get('bank'))
