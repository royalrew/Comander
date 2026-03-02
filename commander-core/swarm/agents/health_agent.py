import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.7)

HEALTH_COACH_PROMPT = """Du är The Health Coach (En stenhård, vetenskaplig elit-tränare).
Ditt jobb är att ansvara för CEO:ns fysiska och mentala prestationer.

REGLER:
1. Om användaren säger att de vill börja träna eller frågar om råd: GE INTE bara tips direkt.
2. Om du inte vet deras exakta mål, utgå från att du inte vet något. Fråga dem!
3. Fråga strategiska frågor: "Vilket är det primära målet (viktnedgång, hypertrofi, kondition)? Vill du träna på gym eller hemma? Hur många dagar i veckan?"
4. Svara kort, koncist och med militärisk precision. Inget fluff.
5. Din output visas under 'HEALTH AGENT' på the Commander Dashboard.
"""

async def health_coach_node(state: AgentState) -> AgentState:
    """The Health Coach specialized agent."""
    messages = state["messages"]
    
    # 1. Ge agenten sin identitet
    system_message = SystemMessage(content=HEALTH_COACH_PROMPT)
    
    # 2. Låt agenten tänka baserat på konversationen
    response = await llm.ainvoke([system_message] + messages)
    
    # 3. Output till UI:n
    return {
        "messages": [response],
        "active_dashboard_tab": "health",
        "dashboard_data": {
            "steps": 0,
            "sleep": "Awaiting Oura Sync",
            "calories": 0,
            "agent_status": "Interviewing CEO"
        }
    }
