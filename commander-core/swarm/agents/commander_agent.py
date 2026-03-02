import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.5)

COMMANDER_PROMPT = """Du är The Commander, en state-of-the-art Enterprise GRC Agent och CTO för Sintari.
Svara kortfattat, mänskligt och professionellt. Denna nod hanterar allmänt prat, frågor som inte rör specifika agenter, eller otydliga inmatningar som 'Va?'.
Om användaren verkar förvirrad, fråga hur du kan hjälpa till."""

async def commander_agent_node(state: AgentState) -> AgentState:
    """The default fallback agent for general conversation."""
    messages = state["messages"]
    system_message = SystemMessage(content=COMMANDER_PROMPT)
    
    # Simple direct generation since it doesn't need tools right now.
    response = await llm.ainvoke([system_message] + messages)
    
    return {
        "messages": [response],
        "active_dashboard_tab": "overview",
        "dashboard_data": {
            "agent_status": "Idle"
        }
    }
