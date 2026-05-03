import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
jp = next(p for p in data['elements'] if "Pedro" in p['web_name'])
print(f"Joao Pedro status: {jp['status']}, minutes: {jp['minutes']}")
