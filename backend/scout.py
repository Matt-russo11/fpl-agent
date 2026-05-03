import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
FPL_BASE_URL = "https://fantasy.premierleague.com/api"

def get_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def optimize_lineup(players):
    sorted_players = sorted(players, key=lambda x: x['ep_next'], reverse=True)
    
    gks = [p for p in sorted_players if p['element_type'] == 1]
    defs = [p for p in sorted_players if p['element_type'] == 2]
    mids = [p for p in sorted_players if p['element_type'] == 3]
    fwds = [p for p in sorted_players if p['element_type'] == 4]
    
    starting_xi = []
    
    if gks: starting_xi.append(gks.pop(0))
    for _ in range(min(3, len(defs))): starting_xi.append(defs.pop(0))
    for _ in range(min(2, len(mids))): starting_xi.append(mids.pop(0))
    for _ in range(min(1, len(fwds))): starting_xi.append(fwds.pop(0))
    
    remaining_outfielders = sorted(defs + mids + fwds, key=lambda x: x['ep_next'], reverse=True)
    
    for p in remaining_outfielders:
        if len(starting_xi) == 11: break
        current_def = len([s for s in starting_xi if s['element_type'] == 2])
        current_mid = len([s for s in starting_xi if s['element_type'] == 3])
        current_fwd = len([s for s in starting_xi if s['element_type'] == 4])
        
        if p['element_type'] == 2 and current_def >= 5: continue
        if p['element_type'] == 3 and current_mid >= 5: continue
        if p['element_type'] == 4 and current_fwd >= 3: continue
        starting_xi.append(p)
        
    starting_ids = set(s['id'] for s in starting_xi)
    bench_outfielders = [p for p in sorted_players if p['id'] not in starting_ids and p['element_type'] != 1]
    bench_gks = [p for p in sorted_players if p['id'] not in starting_ids and p['element_type'] == 1]
    bench = bench_gks + bench_outfielders
    
    starting_xi.sort(key=lambda x: x['ep_next'], reverse=True)
    if len(starting_xi) > 0:
        starting_xi[0]['is_captain'] = True
        starting_xi[0]['role_display'] = '(C)'
    if len(starting_xi) > 1:
        starting_xi[1]['is_vice_captain'] = True
        starting_xi[1]['role_display'] = '(VC)'
        
    for p in starting_xi[2:]:
        p['is_captain'] = False
        p['is_vice_captain'] = False
        p['role_display'] = ''
    for p in bench:
        p['is_captain'] = False
        p['is_vice_captain'] = False
        p['role_display'] = ''

    return starting_xi, bench

def is_fit(player):
    chance = player.get('chance_of_playing_next_round')
    return chance is None or chance == 100

def get_injury_warning(player):
    chance = player.get('chance_of_playing_next_round')
    if chance is not None and chance < 100:
        news = player.get('news', 'Doubtful')
        return f"{chance}% chance to play. {news}"
    return None

def get_league_intel(elements, teams):
    intel = {}
    
    # Pre-process
    team_dict = {t['id']: t['name'] for t in teams}
    
    # 1. Injury Ward (Top 15 most owned injured players)
    injured = [p for p in elements if p.get('chance_of_playing_next_round') is not None and p.get('chance_of_playing_next_round') < 100]
    injured.sort(key=lambda x: float(x.get('selected_by_percent', 0)), reverse=True)
    intel['injury_ward'] = [{
        'name': p['web_name'], 
        'team': team_dict.get(p['team']),
        'status': f"{p['chance_of_playing_next_round']}%",
        'news': p['news']
    } for p in injured]
    
    # 2. League Leaders (Top 5 for various stats)
    def top_5(sort_key, is_float=False):
        valid = [p for p in elements if p.get(sort_key)]
        try:
            valid.sort(key=lambda x: float(x[sort_key]) if is_float else int(x[sort_key]), reverse=True)
        except:
            valid.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
        return [{'name': p['web_name'], 'team': team_dict.get(p['team']), 'val': p[sort_key]} for p in valid[:5]]
    
    def top_5_custom(func):
        valid = [p for p in elements]
        valid.sort(key=lambda x: func(x), reverse=True)
        return [{'name': p['web_name'], 'team': team_dict.get(p['team']), 'val': func(p)} for p in valid[:5]]

    intel['leaders'] = {
        'assists': top_5('assists'),
        'goals_assists': top_5_custom(lambda p: int(p.get('goals_scored', 0)) + int(p.get('assists', 0))),
        'ict_index': top_5('ict_index', is_float=True),
        'xg': top_5('expected_goals', is_float=True),
        'xa': top_5('expected_assists', is_float=True),
        'tackles': top_5('tackles'),
        'saves': top_5('saves'),
        'minutes': top_5('minutes')
    }
    
    # 3. Team Set Pieces & Top Scorers
    team_intel = []
    for t in teams:
        tid = t['id']
        t_players = [p for p in elements if p['team'] == tid]
        
        # Top Scorer
        t_players.sort(key=lambda x: int(x.get('goals_scored', 0)), reverse=True)
        top_scorer = t_players[0]['web_name'] if t_players else "N/A"
        top_scorer_goals = t_players[0].get('goals_scored', 0) if t_players else 0
        
        # Top Assister
        t_players.sort(key=lambda x: int(x.get('assists', 0)), reverse=True)
        top_assister = t_players[0]['web_name'] if t_players else "N/A"
        top_assister_assists = t_players[0].get('assists', 0) if t_players else 0

        # Top Goals + Assists
        t_players.sort(key=lambda x: int(x.get('goals_scored', 0)) + int(x.get('assists', 0)), reverse=True)
        top_ga = t_players[0]['web_name'] if t_players else "N/A"
        top_ga_count = (int(t_players[0].get('goals_scored', 0)) + int(t_players[0].get('assists', 0))) if t_players else 0
        
        # Pen takers
        pens = [p for p in t_players if p.get('penalties_order') is not None]
        pens.sort(key=lambda x: x.get('penalties_order'))
        pen_takers = ", ".join(p['web_name'] for p in pens) if pens else "Unknown"
        
        # FK takers
        fks = [p for p in t_players if p.get('direct_freekicks_order') is not None]
        fks.sort(key=lambda x: x.get('direct_freekicks_order'))
        fk_takers = ", ".join(p['web_name'] for p in fks) if fks else "Unknown"
        
        team_intel.append({
            'team_name': t['name'],
            'top_scorer': f"{top_scorer} ({top_scorer_goals})",
            'top_assister': f"{top_assister} ({top_assister_assists})",
            'top_ga': f"{top_ga} ({top_ga_count})",
            'pens': pen_takers,
            'fks': fk_takers
        })
        
    intel['teams'] = team_intel
    return intel

def analyze_team(manager_id):
    if not manager_id:
        return {"error": "FPL_MANAGER_ID not set."}

    try:
        bootstrap = get_data(f"{FPL_BASE_URL}/bootstrap-static/")
        fixtures = get_data(f"{FPL_BASE_URL}/fixtures/?future=1")
    except Exception as e:
        return {"error": f"Error fetching global data: {e}"}

    elements_list = bootstrap['elements']
    elements = {e['id']: e for e in elements_list}
    
    current_gw = 1
    next_gw = 2
    for event in bootstrap.get('events', []):
        if event.get('is_current'): current_gw = event.get('id')
        if event.get('is_next'): next_gw = event.get('id')
            
    team_fixtures_next_gw = {team['id']: 0 for team in bootstrap['teams']}
    for f in fixtures:
        if f['event'] == next_gw:
            team_fixtures_next_gw[f['team_h']] += 1
            team_fixtures_next_gw[f['team_a']] += 1

    try:
        team_picks_data = get_data(f"{FPL_BASE_URL}/entry/{manager_id}/event/{current_gw}/picks/")
        history_data = get_data(f"{FPL_BASE_URL}/entry/{manager_id}/history/")
    except Exception as e:
        return {"error": f"Error fetching team data: {e}"}

    bank = team_picks_data.get('entry_history', {}).get('bank', 0)
    
    used_chips = [c['name'] for c in history_data.get('chips', [])]
    available_chips = []
    if '3xc' not in used_chips: available_chips.append('Triple Captain')
    if 'bboost' not in used_chips: available_chips.append('Bench Boost')
    if 'freehit' not in used_chips: available_chips.append('Free Hit')
    if used_chips.count('wildcard') < 2: available_chips.append('Wildcard')

    my_players = []
    for pick in team_picks_data.get('picks', []):
        pid = pick['element']
        player = elements[pid]
        ep_next = float(player.get('ep_next', 0) or 0)
        my_players.append({
            'id': pid,
            'name': player['web_name'],
            'element_type': player['element_type'],
            'now_cost': player['now_cost'],
            'ep_next': ep_next,
            'team_id': player['team'],
            'is_captain': False,
            'is_vice_captain': False,
            'role_display': '',
            'status': 'Bench',
            'injury_warning': get_injury_warning(player)
        })

    starting_xi, bench = optimize_lineup(my_players)
    for p in starting_xi: p['status'] = 'Starting'
    for p in bench: p['status'] = 'Bench'
    optimized_squad = starting_xi + bench

    chip_strategy = None
    bgw_count = sum(1 for p in my_players if team_fixtures_next_gw.get(p['team_id'], 0) == 0)
    bench_ep = sum(p['ep_next'] for p in bench)
    best_player = starting_xi[0] if starting_xi else None
    
    if 'Free Hit' in available_chips and bgw_count >= 4:
        chip_strategy = f"Use Free Hit. You have {bgw_count} players with a Blank Gameweek."
    elif 'Bench Boost' in available_chips and bench_ep > 12:
        chip_strategy = f"Use Bench Boost. Your bench has strong expected points ({bench_ep:.1f})."
    elif 'Triple Captain' in available_chips and best_player and best_player['ep_next'] > 7.5:
        chip_strategy = f"Use Triple Captain on {best_player['name']}. Extremely high expected points ({best_player['ep_next']})."
    elif 'Wildcard' in available_chips and sum(p['ep_next'] for p in my_players) < 35:
        chip_strategy = f"Use Wildcard. Overall team expected points are very low."
    else:
        chip_strategy = "Save your chips. No overwhelming advantage this Gameweek."

    my_players.sort(key=lambda x: x['ep_next'])
    worst_players = my_players[:2]
    action_plans = []
    
    for weak_player in worst_players[:1]:
        budget = weak_player['now_cost'] + bank
        valid_replacements = []
        for pid, p in elements.items():
            if not is_fit(p): continue
            if p['element_type'] == weak_player['element_type'] and p['now_cost'] <= budget:
                if any(mp['id'] == pid for mp in my_players): continue
                ep = float(p.get('ep_next', 0) or 0)
                if ep > weak_player['ep_next']:
                    valid_replacements.append((p, ep))
        valid_replacements.sort(key=lambda x: x[1], reverse=True)
        if valid_replacements:
            best_repl, repl_ep = valid_replacements[0]
            reason = f"Single Transfer. Upgrade using £{bank/10:.1f}m from bank. Expected Points jump from {weak_player['ep_next']} to {repl_ep}."
            if team_fixtures_next_gw.get(best_repl['team'], 0) > 1:
                reason += f" {best_repl['web_name']} has a Double Gameweek!"
            action_plans.append({
                'type': 'Single Transfer',
                'sell': [weak_player['name']],
                'buy': [best_repl['web_name']],
                'cost_diff': round((best_repl['now_cost'] - weak_player['now_cost'])/10, 1),
                'explanation': reason,
                'net_ep_gain': round(repl_ep - weak_player['ep_next'], 2)
            })

    if len(worst_players) == 2:
        wp1, wp2 = worst_players[0], worst_players[1]
        total_budget = wp1['now_cost'] + wp2['now_cost'] + bank
        cands1, cands2 = [], []
        for pid, p in elements.items():
            if not is_fit(p): continue
            if any(mp['id'] == pid for mp in my_players): continue
            ep = float(p.get('ep_next', 0) or 0)
            if p['element_type'] == wp1['element_type']: cands1.append((p, ep))
            if p['element_type'] == wp2['element_type']: cands2.append((p, ep))
        cands1.sort(key=lambda x: x[1], reverse=True)
        cands2.sort(key=lambda x: x[1], reverse=True)
        
        best_pair, best_pair_ep_gain = None, 0
        for r1, ep1 in cands1[:20]:
            for r2, ep2 in cands2[:20]:
                if r1['id'] == r2['id']: continue
                if r1['now_cost'] + r2['now_cost'] <= total_budget:
                    gain = (ep1 + ep2) - (wp1['ep_next'] + wp2['ep_next'])
                    if gain > best_pair_ep_gain:
                        best_pair_ep_gain = gain
                        best_pair = (r1, r2, ep1, ep2)
        if best_pair:
            r1, r2, ep1, ep2 = best_pair
            reason = f"Multi-Transfer Strategy. Downgrade one position to fund an upgrade using your bank. Total EP jump of {round(best_pair_ep_gain, 1)}."
            action_plans.append({
                'type': 'Double Transfer',
                'sell': [wp1['name'], wp2['name']],
                'buy': [r1['web_name'], r2['web_name']],
                'cost_diff': round(((r1['now_cost'] + r2['now_cost']) - (wp1['now_cost'] + wp2['now_cost']))/10, 1),
                'explanation': reason,
                'net_ep_gain': round(best_pair_ep_gain, 2)
            })
    action_plans.sort(key=lambda x: x['net_ep_gain'], reverse=True)
    
    intel = get_league_intel(elements_list, bootstrap['teams'])

    return {
        "manager_id": manager_id,
        "target_gw": next_gw,
        "bank": bank / 10,
        "available_chips": available_chips,
        "chip_strategy": chip_strategy,
        "action_plans": action_plans,
        "optimal_lineup": optimized_squad,
        "league_intel": intel
    }

if __name__ == "__main__":
    manager_id = os.getenv("FPL_MANAGER_ID") or "1147719"
    res = analyze_team(manager_id)
    print("Success")
