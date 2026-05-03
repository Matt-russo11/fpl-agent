import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()

# Check teams for set piece takers
team = data['teams'][0]
print("Team keys:", team.keys())

# Check elements for goals scored
player = data['elements'][0]
print("Player keys:", player.keys())
