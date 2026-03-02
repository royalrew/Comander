from langchain_core.messages import AIMessage
from swarm.state import AgentState

def cfo_node(state: AgentState) -> AgentState:
    """The CFO specialized agent."""
    
    # Later: Connect to Stripe API and cfo_module.py
    
    mock_response = AIMessage(content="[CFO Agent] Inga kostsamme API-utsvävningar identifierade inatt. Budgeten ligger stabil.")
    
    return {
        "messages": [mock_response],
        "active_dashboard_tab": "finance",
        "dashboard_data": {
            "burn_rate": "$1.24",
            "mrr": "$0.00"
        }
    }
