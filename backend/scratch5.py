import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
for p in data['elements']:
    if "Pedro" in p['web_name'] or "Mavropanos" in p['web_name']:
        print(f"{p['web_name']}: ep_next={p['ep_next']}, chance={p['chance_of_playing_next_round']}, news={p['news']}")
