import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from swarm.state import AgentState

# Supervisor uses the most capable model (Cortex)
llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.0)

SUPERVISOR_PROMPT = """You are the Commander. Route conversations to specialized sub-agents.
Available Sub-Agents:
- HealthCoachAgent: For fitness, sleep, metrics, physical goals.
- TechLeadAgent: For coding, software architecture, technical planning.
- CFOAgent: For finance, subscriptions, Stripe data.
- CommanderAgent: For general conversation, chitchat, or unclassified queries (like "ok", "va?", "tack").

Respond ONLY with the EXACT name of the Sub-Agent. Do not output any other text or reasoning.
"""

async def supervisor_node(state: AgentState) -> AgentState:
    """The Commander decides who should speak next."""
    messages = state["messages"]
    
    # Send the history to the LLM with the supervisor prompt
    system_message = SystemMessage(content=SUPERVISOR_PROMPT)
    response = await llm.ainvoke([system_message] + messages)
    
    decision = response.content.strip().replace('"', '').replace("'", "")
    
    valid_agents = ["TechLeadAgent", "HealthCoachAgent", "CFOAgent", "FINISH"]
    if decision not in valid_agents:
        decision = "FINISH" # Fallback
        
    return {"next_step": decision}
