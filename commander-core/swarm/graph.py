from langgraph.graph import StateGraph, END
from swarm.state import AgentState
from swarm.supervisor import supervisor_node
from swarm.agents.tech_agent import tech_lead_node
from swarm.agents.health_agent import health_coach_node
from swarm.agents.finance_agent import cfo_node

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("TechLeadAgent", tech_lead_node)
workflow.add_node("HealthCoachAgent", health_coach_node)
workflow.add_node("CFOAgent", cfo_node)

# 3. Define the Router logic (The Edge that branches based on next_step)
def route_next_step(state: AgentState) -> str:
    """Read the 'next_step' flag set by Supervisor and return the node name."""
    next_step = state.get("next_step", "FINISH")
    if next_step == "FINISH":
        return END
    return next_step

# 4. Add Edges (How they connect)
# Every agent must return to the Supervisor after they do their job
workflow.add_conditional_edges("Supervisor", route_next_step)
workflow.add_edge("TechLeadAgent", "Supervisor")
workflow.add_edge("HealthCoachAgent", "Supervisor")
workflow.add_edge("CFOAgent", "Supervisor")

# 5. Set Entry Point
workflow.set_entry_point("Supervisor")

# 6. Compile Graph
swarm_engine = workflow.compile()
