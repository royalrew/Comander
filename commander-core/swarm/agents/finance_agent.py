import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import manage_calendar_event, get_calendar_view

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.1)

CFO_PROMPT = """Du är The CFO Agent (Chief Financial Officer). Din roll är att maximera CEO:ns personliga intäkter (MRR från sidoprojekt) och minimera onödiga utgifter.
Du drivs av ett enda mål: Att bygga tillräckligt mycket kapital för att köpa ett hus i Monaco och en privatjet.
Var sparsam, ifrågasättande av utgifter och ha laserfokus på ROI.
Du har tillgång till CEO:ns kalender via 'get_calendar_view' och 'manage_calendar_event'. Du kan boka in uppföljningsmöten för att gå igenom intäkter (kategori="Finance", agent_id="CFO").
Din output visas under 'CFO AGENT' på the Commander Dashboard."""

agent_runnable = create_react_agent(llm, tools=[manage_calendar_event, get_calendar_view])

async def cfo_node(state: AgentState) -> AgentState:
    """The CFO specialized agent."""
    user_name = state.get("session_user_id", "CEO")
    curr_time = state.get("session_time", "Unknown")
    
    dynamic_prompt = CFO_PROMPT + f"\n\n[CONTEXT]\nUser: {user_name}\nTime: {curr_time}\n"
    system_message = SystemMessage(content=dynamic_prompt)
    input_payload = [system_message] + messages
    
    result = await agent_runnable.ainvoke({"messages": input_payload})
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "finance",
        "dashboard_data": {
            "burn_rate": "Calculating...",
            "mrr": "Awaiting Stripe"
        }
    }
