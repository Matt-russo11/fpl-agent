import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def get_ai_response(message: str, scout_data: dict, history: list) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not configured in the backend environment."
    
    # Initialize the Groq LLM (Llama 3 is extremely fast and capable)
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-70b-8192", 
        temperature=0.7
    )
    
    # Extract key data for the system prompt to keep it concise but informative
    target_gw = scout_data.get('target_gw', 'Unknown')
    bank = scout_data.get('bank', 0)
    
    # Format the current starting lineup
    current_lineup = scout_data.get('current_lineup', [])
    starters = [f"{p['name']} ({p.get('role_display', '')})" for p in current_lineup if p.get('status') == 'Starting']
    bench = [p['name'] for p in current_lineup if p.get('status') == 'Bench']
    
    # Format the AI action plans
    plans = scout_data.get('action_plans', [])
    plan_strs = []
    for i, plan in enumerate(plans):
        plan_strs.append(f"Plan {i+1}: {plan['explanation']} (Gain: +{plan['net_ep_gain']} EP)")
    plan_context = "\n".join(plan_strs) if plan_strs else "No urgent transfers recommended."
    
    system_prompt = f"""
    You are an expert Premier League Fantasy Football (FPL) Assistant.
    You are helping a manager optimize their team for {target_gw}.
    
    Current Bank Balance: £{bank}m
    
    Current Starting XI: {", ".join(starters)}
    Current Bench: {", ".join(bench)}
    
    Algorithm Suggested Transfer Plans:
    {plan_context}
    
    Guidelines:
    1. Answer the manager's question directly and concisely (keep it under 3-4 sentences if possible).
    2. Use the mathematical transfer plans to inform your advice, but you can also provide general FPL wisdom.
    3. Be conversational, analytical, and highly strategic. Use markdown for bolding player names.
    4. If the user asks about someone not in their squad, you can give general advice based on your vast knowledge of the Premier League.
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
