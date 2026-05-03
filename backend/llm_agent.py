import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def get_ai_response(message: str, scout_data: dict, history: list) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not configured in the backend environment."
    
    # Initialize the Groq LLM
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant", 
        temperature=0.7,
        max_tokens=800
    )
    
    # Extract key data for the system prompt to keep it concise but informative
    target_gw = scout_data.get('target_gw', 'Unknown')
    bank = scout_data.get('bank', 0)
    
    # Format the current starting lineup with exact team names, costs, and Social EP
    current_lineup = scout_data.get('current_lineup', [])
    starters = [f"{p['name']} ({p.get('team_name', 'Unknown')}, {p.get('role_display', '').strip()}) - £{p.get('now_cost', 0)/10}m - Social EP: {p.get('social_ep', p.get('ep_next', 0))}" for p in current_lineup if p.get('status') == 'Starting']
    bench = [f"{p['name']} ({p.get('team_name', 'Unknown')}) - £{p.get('now_cost', 0)/10}m - Social EP: {p.get('social_ep', p.get('ep_next', 0))}" for p in current_lineup if p.get('status') == 'Bench']
    
    # Format the AI action plans
    plans = scout_data.get('action_plans', [])
    plan_strs = []
    for i, plan in enumerate(plans):
        plan_strs.append(f"Plan {i+1}: {plan['explanation']} (Gain: +{plan['net_ep_gain']} EP)")
    plan_context = "\n".join(plan_strs) if plan_strs else "No urgent transfers recommended."
    
    # Format the Upcoming Fixtures (Next 4 Gameweeks)
    timeline = scout_data.get('season_timeline', {})
    fixture_context = "Upcoming Fixtures (Next 4 GWs):\n"
    if timeline:
        try:
            tgw = int(target_gw)
            for team, gws in timeline.items():
                team_fix = []
                for gw in range(tgw, min(tgw + 4, 39)):
                    # Handle both int and string keys just in case
                    fix = gws.get(str(gw)) or gws.get(gw) or []
                    if not fix:
                        team_fix.append(f"GW{gw}: BLANK")
                    elif len(fix) > 1:
                        team_fix.append(f"GW{gw}: DOUBLE ({', '.join(fix)})")
                    else:
                        team_fix.append(f"GW{gw}: {fix[0]}")
                fixture_context += f"- {team}: {' | '.join(team_fix)}\n"
        except Exception:
            fixture_context = "Fixture data unavailable."
    
    # Format the Market Intel
    intel = scout_data.get('league_intel', {})
    market_context = "Global Market Intel (Top Performers & Injuries):\n"
    if intel:
        leaders = intel.get('leaders', {})
        goals_assists = [f"{p['name']} ({p['val']})" for p in leaders.get('goals_assists', [])]
        ict = [f"{p['name']} ({p['val']})" for p in leaders.get('ict_index', [])]
        injuries = [f"{p['name']} ({p['status']})" for p in intel.get('injury_ward', [])[:5]]
        market_context += f"Top G+A: {', '.join(goals_assists)}\n"
        market_context += f"Top ICT Index: {', '.join(ict)}\n"
        market_context += f"Major Injuries: {', '.join(injuries)}\n"
    
    system_prompt = f"""
    You are an expert, brutally honest Premier League Fantasy Football (FPL) Assistant.
    You are helping a manager optimize their team for Gameweek {target_gw}.
    
    Current Bank Balance: £{bank}m
    
    Current Squad (Name (Team) - Cost - Expected Points):
    Starting XI: {", ".join(starters)}
    Bench: {", ".join(bench)}
    
    Algorithm Suggested Transfer Plans:
    {plan_context}
    
    {market_context}
    
    {fixture_context}
    
    FPL CHIP DEFINITIONS (STRICT RULES):
    - Bench Boost: Adds the points of the 4 bench players to the total score. Only use if the bench players have excellent fixtures (e.g. Double Gameweeks). Do NOT suggest it just because starters have good fixtures.
    - Triple Captain: Multiplies the captain's points by 3 instead of 2. Use on a premium player during a Double Gameweek.
    - Free Hit: Replaces the entire squad for ONE gameweek only. Perfect for navigating massive Blank Gameweeks.
    - Wildcard: Permanent unlimited transfers. Use when the squad is fundamentally broken long-term.
    
    CRITICAL BEHAVIOR GUIDELINES:
    1. NEVER hallucinate facts. Use the exact names, teams, and costs provided above.
    2. NEVER hallucinate fixtures. STRICTLY use the 'Upcoming Fixtures' data block.
    3. If asked an unanswerable question, reply exactly: "Sorry, I cannot answer that accurately right now."
    4. Be highly critical. If the user suggests a bad transfer, explicitly tell them. Use the Market Intel to suggest superior targets.
    5. STRICT TRANSFER MATH RULE: If you recommend a transfer, you MUST recommend a valid 1-for-1 or 2-for-2 swap. You MUST ensure the cost of the players being bought is less than or equal to the (cost of players sold + Current Bank Balance). Never recommend selling 3 and buying 2.
    6. DELIVERABLES: Always end your response with a clear, actionable insight block. Example: "ACTION: Sell [Player] and Buy [Player]."
    7. Answer concisely. Use markdown for bolding player names.
    """
    
    # Build message history
    messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg.get('role') == 'user':
            messages.append(HumanMessage(content=msg.get('content')))
        elif msg.get('role') == 'assistant':
            messages.append(AIMessage(content=msg.get('content')))
            
    # Add the current message
    messages.append(HumanMessage(content=message))
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"AI connection error: {str(e)}"
