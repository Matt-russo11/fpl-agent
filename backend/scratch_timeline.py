import requests
import json

def test_fixtures():
    fixtures = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
    bootstrap = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    
    teams = {t['id']: t['short_name'] for t in bootstrap['teams']}
    
    gw_matrix = {t_id: {} for t_id in teams.keys()}
    
    for f in fixtures:
        gw = f.get('event')
        if not gw: continue
        
        h_team = f['team_h']
        a_team = f['team_a']
        
        # Add to home team
        if gw not in gw_matrix[h_team]: gw_matrix[h_team][gw] = []
        gw_matrix[h_team][gw].append(f"vs {teams[a_team]} (H)")
        
        # Add to away team
        if gw not in gw_matrix[a_team]: gw_matrix[a_team][gw] = []
        gw_matrix[a_team][gw].append(f"vs {teams[h_team]} (A)")
        
    # Check Arsenal (id 1) for GWs 1-5
    print("Arsenal GW 1-5:")
    for gw in range(1, 6):
        print(f"GW{gw}: {gw_matrix[1].get(gw, ['BLANK'])}")

test_fixtures()
