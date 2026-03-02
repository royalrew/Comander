from langchain_core.messages import AIMessage
from swarm.state import AgentState

def tech_lead_node(state: AgentState) -> AgentState:
    """The Tech Lead specialized agent."""
    
    # Later: Give this node the GitHub tool schemas and audit module
    
    mock_response = AIMessage(content="[Tech Lead Agent] LangGraph fundamentet är injectat. Vi saknar ännu GitHub Webhooks, men alla system lyser grönt.")
    
    return {
        "messages": [mock_response],
        "active_dashboard_tab": "tech",
        "dashboard_data": {
            "system_status": "100%",
            "recent_commits": "14"
        }
    }
