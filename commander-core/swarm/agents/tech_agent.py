import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import manage_calendar_event, get_calendar_view

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.2)

TECH_LEAD_PROMPT = """Du är The Tech Lead Agent. Din uppgift är att skriva kod och bygga arkitektur som snabbt tar CEO:n mot sitt mål: Total ekonomisk frihet (Privatjet, Monaco).
Skapa inte komplicerad "Enterprise"-kod i onödan. Fokusera på att skeppa produkter snabbt, få ut dem på marknaden och generera intäkter (MRR).
Svara direkt och tekniskt.
Du har tillgång till CEO:ns kalender. Om CEO:n behöver fokustid för kodning, använd 'manage_calendar_event' för att blocka det (kategori="Tech", agent_id="TechLead").
Din output visas under 'TECH LEAD AGENT' på the Commander Dashboard."""

agent_runnable = create_react_agent(llm, tools=[manage_calendar_event, get_calendar_view])

async def tech_lead_node(state: AgentState) -> AgentState:
    """The Tech Lead specialized agent."""
    user_name = state.get("session_user_id", "CEO")
    curr_time = state.get("session_time", "Unknown")
    
    dynamic_prompt = TECH_LEAD_PROMPT + f"\n\n[CONTEXT]\nUser: {user_name}\nTime: {curr_time}\n"
    system_message = SystemMessage(content=dynamic_prompt)
    input_payload = [system_message] + messages
    
    result = await agent_runnable.ainvoke({"messages": input_payload})
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "tech",
        "dashboard_data": {
            "system_status": "Online",
            "recent_commits": "Pending Sync"
        }
    }
