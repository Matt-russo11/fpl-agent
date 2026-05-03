import requests
import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

def get_trending_players(elements):
    """
    Scrapes r/FantasyPL and uses LLM to identify trending players.
    Matches extracted names against the official FPL elements list.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FPLAgent/1.0'}
    titles = []
    try:
        # Scrape FPL and Soccer to get a broad global sentiment
        for sub in ['FantasyPL', 'soccer']:
            res = requests.get(f'https://www.reddit.com/r/{sub}/hot.json?limit=15', headers=headers, timeout=5)
            data = res.json()
            titles.extend([post['data']['title'] for post in data['data']['children'] if not post['data']['stickied']])
    except Exception as e:
        print(f"Reddit scrape failed: {e}")
        return []
        
    titles_text = "\n".join(f"- {t}" for t in titles)
    
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.1, # Low temp for data extraction
    )
    
    prompt = f"""
    You are a data extraction assistant. Analyze these top posts from soccer and Fantasy Premier League communities:
    {titles_text}
    
    Identify any Premier League soccer players being actively hyped up, discussed as good transfers, or mentioned as essential (or players returning from injury).
    Assign each player a "hype_score" from 1 to 10 based on how strongly the community is praising them.
    Return ONLY a raw JSON array of objects with 'name', 'reason', and 'hype_score' (int).
    CRITICAL RULE: DO NOT hallucinate player positions (e.g. "in the midfield") or guess facts. Only summarize the exact words in the headline.
    Example: [{{"name": "Palmer", "reason": "Scored a hattrick in the cup", "hype_score": 9}}]
    If no one is clearly trending, return [].
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        extracted_data = json.loads(content)
    except Exception as e:
        print(f"LLM sentiment parse failed: {e}")
        return []
        
    trending = []
    # Match LLM names to official FPL names
    for item in extracted_data:
        llm_name = item.get('name', '').lower()
        reason = item.get('reason', '')
        if not llm_name: continue
        
        # Substring match against official names
        for pid, player in elements.items():
            fpl_name = player['web_name'].lower()
            first_name = player.get('first_name', '').lower()
            second_name = player.get('second_name', '').lower()
            
            if llm_name in fpl_name or fpl_name in llm_name or llm_name in second_name:
                trending.append({
                    'id': pid,
                    'name': player['web_name'],
                    'reason': reason,
                    'hype_score': item.get('hype_score', 5)
                })
                break # Matched this player
                
    return trending

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Mock elements for testing
    mock_els = {
        1: {'web_name': 'Haaland', 'first_name': 'Erling', 'second_name': 'Haaland'},
        2: {'web_name': 'Saka', 'first_name': 'Bukayo', 'second_name': 'Saka'},
        3: {'web_name': 'Isak', 'first_name': 'Alexander', 'second_name': 'Isak'},
        4: {'web_name': 'Palmer', 'first_name': 'Cole', 'second_name': 'Palmer'},
        5: {'web_name': 'Gordon', 'first_name': 'Anthony', 'second_name': 'Gordon'}
    }
    print(get_trending_players(mock_els))
