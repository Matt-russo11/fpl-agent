import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
teams = {t['id']: t['name'] for t in data['teams']}
jp = next(p for p in data['elements'] if "Pedro" in p['web_name'])
mav = next(p for p in data['elements'] if "Mavropanos" in p['web_name'])
print(f"Joao Pedro Team: {teams[jp['team']]}")
print(f"Mavropanos Team: {teams[mav['team']]}")

fixtures = requests.get('https://fantasy.premierleague.com/api/fixtures/?future=1').json()
next_gw = 36
print(f"Brighton GW{next_gw} fixtures:")
for f in fixtures:
    if f['event'] == next_gw and (f['team_h'] == jp['team'] or f['team_a'] == jp['team']):
        print(f"vs {teams[f['team_a']] if f['team_h'] == jp['team'] else teams[f['team_h']]}")
print(f"West Ham GW{next_gw} fixtures:")
for f in fixtures:
    if f['event'] == next_gw and (f['team_h'] == mav['team'] or f['team_a'] == mav['team']):
        print(f"vs {teams[f['team_a']] if f['team_h'] == mav['team'] else teams[f['team_h']]}")
