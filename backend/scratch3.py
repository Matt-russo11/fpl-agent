import requests
data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
print("Expected Points Next:", data['elements'][0].get('ep_next'))
