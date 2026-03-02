import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.2)

TECH_LEAD_PROMPT = """Du är The Tech Lead Agent. Din uppgift är att ha översikt på koden, deployment och arkitektur.
Om användaren ställer allmänna frågor, besvara dem tekniskt.
Din output visas under 'TECH LEAD AGENT' på the Commander Dashboard."""

async def tech_lead_node(state: AgentState) -> AgentState:
    """The Tech Lead specialized agent."""
    messages = state["messages"]
    
    system_message = SystemMessage(content=TECH_LEAD_PROMPT)
    response = await llm.ainvoke([system_message] + messages)
    
    return {
        "messages": [response],
        "active_dashboard_tab": "tech",
        "dashboard_data": {
            "system_status": "Online",
            "recent_commits": "Pending Sync"
        }
    }
