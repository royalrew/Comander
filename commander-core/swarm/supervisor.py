import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from swarm.state import AgentState

# Supervisor uses the most capable model (Cortex)
llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.0)

SUPERVISOR_PROMPT = """You are THE COMMANDER. You are a strictly professional, high-end "Consigliere" and Enterprise Router.
Your job is to read the user's message and determine which specialized Sub-Agent should handle the request.

Available Sub-Agents:
- "TechLeadAgent": Handles all questions regarding code, Github, servers, deploying, system architecture, or software engineering.
- "HealthCoachAgent": Handles all questions regarding physical health, sleep, calories, working out, or mental recovery.
- "CFOAgent": Handles all questions regarding money, API costs, Stripe billing, finances, or budgets.
- "FINISH": If the user is just saying hello, or if the conversation is resolved, or if you should respond directly.

IMPORTANT INSTRUCTION: 
Respond ONLY with the EXACT name of the Sub-Agent or "FINISH". Do not output any other text or reasoning.
"""

def supervisor_node(state: AgentState) -> AgentState:
    """The Commander decides who should speak next."""
    messages = state["messages"]
    
    # Send the history to the LLM with the supervisor prompt
    system_message = SystemMessage(content=SUPERVISOR_PROMPT)
    response = llm.invoke([system_message] + messages)
    
    decision = response.content.strip().replace('"', '').replace("'", "")
    
    valid_agents = ["TechLeadAgent", "HealthCoachAgent", "CFOAgent", "FINISH"]
    if decision not in valid_agents:
        decision = "FINISH" # Fallback
        
    return {"next_step": decision}
