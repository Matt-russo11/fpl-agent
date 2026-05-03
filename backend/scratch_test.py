import os
from scout import analyze_team
res = analyze_team("1147719")
if "error" in res:
    print("ERROR:", res["error"])
else:
    print("SUCCESS")
    print(res.get('trending_players'))
