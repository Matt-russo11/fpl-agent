import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
for k, v in data['elements'][0].items():
    if 'expected' in k:
        print(f"{k}: {v}")
