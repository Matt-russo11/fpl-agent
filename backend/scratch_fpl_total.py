import requests
res = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
print("Keys:", res.keys())
print("Total players:", res.get('total_players'))
