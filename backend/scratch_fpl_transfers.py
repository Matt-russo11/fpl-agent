import requests
res = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
elements = res['elements']
in_trans = sorted(elements, key=lambda x: x.get('transfers_in_event', 0), reverse=True)[:5]
out_trans = sorted(elements, key=lambda x: x.get('transfers_out_event', 0), reverse=True)[:5]

print("Transfers IN:")
for t in in_trans:
    print(t['web_name'], t.get('transfers_in_event', 0))

print("\nTransfers OUT:")
for t in out_trans:
    print(t['web_name'], t.get('transfers_out_event', 0))
