import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.1)

CFO_PROMPT = """Du är The CFO Agent (Chief Financial Officer). Din roll är att övervaka kostnader, Stripe, intäkter och API-utgifter.
Var sparsam, ifrågasättande av utgifter och fokusera på ROI.
Din output visas under 'CFO AGENT' på the Commander Dashboard."""

async def cfo_node(state: AgentState) -> AgentState:
    """The CFO specialized agent."""
    messages = state["messages"]
    
    system_message = SystemMessage(content=CFO_PROMPT)
    response = await llm.ainvoke([system_message] + messages)
    
    return {
        "messages": [response],
        "active_dashboard_tab": "finance",
        "dashboard_data": {
            "burn_rate": "Calculating...",
            "mrr": "Awaiting Stripe"
        }
    }
