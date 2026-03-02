from langchain_core.messages import AIMessage
from swarm.state import AgentState

def health_coach_node(state: AgentState) -> AgentState:
    """The Health Coach specialized agent."""
    
    # Later: Connect to Model Context Protocol (MCP) or Oura APIs here
    
    mock_response = AIMessage(content="[Health Coach Agent] Apple Health-metrics saknas via MCP, men jag ser inga varningsklockor. Se till att sova inatt.")
    
    # Output to the screen and generate the Dashboard JSON
    return {
        "messages": [mock_response],
        "active_dashboard_tab": "health",
        "dashboard_data": {
            "steps": 0,
            "sleep": "Unknown",
            "calories": 0
        }
    }
