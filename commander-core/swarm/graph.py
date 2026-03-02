from langgraph.graph import StateGraph, END
from swarm.state import AgentState
from swarm.supervisor import supervisor_node
from swarm.agents.health_agent import health_coach_node
from swarm.agents.tech_agent import tech_lead_node
from swarm.agents.finance_agent import cfo_node
from swarm.agents.commander_agent import commander_agent_node

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("Commander", supervisor_node) # Renamed Supervisor to Commander
workflow.add_node("TechLeadAgent", tech_lead_node)
workflow.add_node("HealthCoachAgent", health_coach_node)
workflow.add_node("CFOAgent", cfo_node)
workflow.add_node("CommanderAgent", commander_agent_node) # Added CommanderAgent

# 3. Define the Router logic (The Edge that branches based on next_step)
def route_next_step(state: AgentState):
    """Read the 'next_step' flag set by Commander and return the node name."""
    next_step = state.get("next_step")
    # If the LLM spits out something weird, default to CommanderAgent
    if next_step in ["HealthCoachAgent", "TechLeadAgent", "CFOAgent", "CommanderAgent"]:
        return next_step
    return "CommanderAgent"

# 4. Add Edges (How they connect)
workflow.add_conditional_edges("Commander", route_next_step)
workflow.add_edge("TechLeadAgent", END)
workflow.add_edge("HealthCoachAgent", END)
workflow.add_edge("CFOAgent", END)
workflow.add_edge("CommanderAgent", END)

# 5. Set Entry Point
workflow.set_entry_point("Commander")

# 6. Compile Graph
swarm_engine = workflow.compile()
