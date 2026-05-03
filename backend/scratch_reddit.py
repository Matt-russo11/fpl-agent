import requests

def test_reddit():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FPLAgent/1.0'}
    try:
        res = requests.get('https://www.reddit.com/r/FantasyPL/hot.json?limit=15', headers=headers)
        data = res.json()
        titles = [post['data']['title'] for post in data['data']['children']]
        print("Scraped Reddit Titles:")
        for t in titles:
            print("-", t)
    except Exception as e:
        print("Error:", e)

test_reddit()
