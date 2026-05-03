import requests

def test_fpl():
    res = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    elements = res['elements']
    
    # Find Joao Pedro
    for p in elements:
        if 'Pedro' in p['web_name']:
            print(f"Name: {p['web_name']}, EP: {p['ep_next']}, Chance: {p.get('chance_of_playing_next_round')}")
            
test_fpl()
