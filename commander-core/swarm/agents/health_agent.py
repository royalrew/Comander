import os
from langchain_openai import ChatOpenAI
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import memorize_fact, manage_calendar_event, get_calendar_view

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.7)

HEALTH_COACH_PROMPT = """Du är The Health Coach (En vetenskaplig och empatisk elit-tränare).
Ditt jobb är att ansvara för CEO:ns fysiska och mentala prestationer, stressnivå, sömn och återhämtning.

REGLER:
1. Om användaren mår dåligt eller har sovit uselt – var stöttande! Gå inte direkt på strikta frågor. Möt dem där de är. Fråga hur du kan underlätta deras dag.
2. Lär känna dem över tid. Använd 'memorize_fact' FÖR ATT SPARA DET PERMANENT när de delar med sig av viktiga detaljer (t.ex. mål, skador, preferenser).
3. Du har tillgång till CEO:ns kalender. Använd 'get_calendar_view' för att se hur veckan ser ut.
4. Du KAN och SKA boka in träningspass eller återhämtning i kalendern via 'manage_calendar_event' om det behövs (kategori="Health", prioritet="High", agent_id="HealthCoach").
5. Håll svaren korta, mänskliga och insiktsfulla. Inte som ett formulär.
6. Din output visas under 'HEALTH AGENT' på the Commander Dashboard.
"""

from langchain_core.messages import SystemMessage

# Compile the ReAct agent loops (without version-dependent kwargs)
agent_runnable = create_react_agent(llm, tools=[memorize_fact, manage_calendar_event, get_calendar_view])

async def health_coach_node(state: AgentState) -> AgentState:
    """The Health Coach specialized agent."""
    messages = state["messages"]
    user_name = state.get("session_user_id", "CEO")
    curr_time = state.get("session_time", "Unknown")
    
    # 1. Dynamically inject the System Persona to bypass any LangGraph kwargs bugs
    dynamic_prompt = HEALTH_COACH_PROMPT + f"\n\n[CONTEXT]\nUser: {user_name}\nTime: {curr_time}\n"
    system_message = SystemMessage(content=dynamic_prompt)
    input_payload = [system_message] + messages
    
    # Run the compiled ReAct agent
    result = await agent_runnable.ainvoke({"messages": input_payload})
    
    # Extract ONLY the newly generated messages (ToolCalls, ToolOutputs, AI replies)
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "health",
        "dashboard_data": {
            "steps": 0,
            "sleep": "Awaiting Oura Sync",
            "calories": 0,
            "agent_status": "Idle"
        }
    }
