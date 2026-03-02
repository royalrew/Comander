import os
from langchain_openai import ChatOpenAI
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import memorize_fact

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.7)

HEALTH_COACH_PROMPT = """Du är The Health Coach (En stenhård, vetenskaplig elit-tränare).
Ditt jobb är att ansvara för CEO:ns fysiska och mentala prestationer.

REGLER:
1. Om du inte vet deras exakta mål, utgå från att du inte vet något. Fråga dem!
2. Fråga strategiska frågor: Mål (hypertrofi, kondition)? Gym eller hemma? Dagar i veckan?
3. NÄR DU FÅR REDA PÅ CEO:ns MÅL ELLER FAKTA, MÅSTE DU GÖRA ETT ANROP TILL VERKTYGET 'memorize_fact' FÖR ATT SPARA DET PERMANENT!
4. Svara kort, koncist och med militärisk precision. Inget fluff.
5. Din output visas under 'HEALTH AGENT' på the Commander Dashboard.
"""

# Compile the ReAct agent loops
agent_runnable = create_react_agent(llm, tools=[memorize_fact], state_modifier=HEALTH_COACH_PROMPT)

async def health_coach_node(state: AgentState) -> AgentState:
    """The Health Coach specialized agent."""
    messages = state["messages"]
    
    # Run the compiled ReAct agent
    result = await agent_runnable.ainvoke({"messages": messages})
    
    # Extract ONLY the newly generated messages (ToolCalls, ToolOutputs, AI replies)
    new_messages = result["messages"][len(messages):]
    
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
