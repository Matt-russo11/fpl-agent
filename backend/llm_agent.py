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
        temperature=0.7
    )
    
    # Extract key data for the system prompt to keep it concise but informative
    target_gw = scout_data.get('target_gw', 'Unknown')
    bank = scout_data.get('bank', 0)
    
    # Format the current starting lineup with exact team names to prevent hallucinations
    current_lineup = scout_data.get('current_lineup', [])
    starters = [f"{p['name']} ({p.get('team_name', 'Unknown')}, {p.get('role_display', '').strip()})" for p in current_lineup if p.get('status') == 'Starting']
    bench = [f"{p['name']} ({p.get('team_name', 'Unknown')})" for p in current_lineup if p.get('status') == 'Bench']
    
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
    
    system_prompt = f"""
    You are an expert, brutally honest Premier League Fantasy Football (FPL) Assistant.
    You are helping a manager optimize their team for Gameweek {target_gw}.
    
    Current Bank Balance: £{bank}m
    
    Current Starting XI: {", ".join(starters)}
    Current Bench: {", ".join(bench)}
    
    Algorithm Suggested Transfer Plans:
    {plan_context}
    
    {fixture_context}
    
    CRITICAL BEHAVIOR GUIDELINES:
    1. NEVER hallucinate real-world facts. Use the exact team names provided in the starting XI array above.
    2. NEVER hallucinate fixtures. STRICTLY use the 'Upcoming Fixtures' data block above to answer any questions about schedules, Blank Gameweeks, or Double Gameweeks. If a gameweek says "BLANK", the team does not play.
    3. If the user asks a question that you cannot answer accurately using the provided data blocks, you MUST reply with exactly: "Sorry, I cannot answer that accurately right now." Do not attempt to guess or use outside knowledge.
    4. Be highly critical and opinionated. DO NOT act like a "yes-man". If the user suggests a transfer that contradicts the mathematical Algorithm Plans, explicitly tell them it is a bad idea.
    5. Make decisive, specific recommendations (e.g., "Sell X, Buy Y"). Avoid vague advice.
    6. Answer concisely (2-4 sentences max). Use markdown for bolding player names.
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
