from typing import TypedDict, Annotated, List, Union, Any, Dict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The shared central State (Memory) that flows through the LangGraph.
    """
    # 1. Message History (The dialog between User, Supervisor, and Sub-Agents)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 2. Generative UI Payload mapping for Next.js 
    active_dashboard_tab: str       # e.g. "health", "finance", "tech" (To highlight sidebar)
    dashboard_data: Dict[str, Any]  # The JSON object that AgentCard.tsx ingests

    # 3. Routing Flag
    next_step: str                  # Determines which node should execute next
    
    # Optional: Error tracking
    error: str
