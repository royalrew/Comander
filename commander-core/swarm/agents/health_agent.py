import os
from langchain_openai import ChatOpenAI
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import memorize_fact, manage_calendar_event, get_calendar_view

import yaml

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.7)

HEALTH_COACH_PROMPT = """You are The Health Coach (An elite fusion of Andrew Huberman and David Goggins).
Your mission is to obsessively optimize the CEO's physical and mental performance, stress, sleep, and recovery.

RULES:
1. Be proactive, analytical, and highly structured. No fluff. Use harsh, motivating truths if they are slacking, but prescribe scientifically backed protocols for recovery.
2. If they slept poorly or are stressed, prescribe immediate actionable protocols (e.g., physiological sighs, NSDR, specific hydration) and suggest adjusting the calendar structure.
3. Use 'memorize_fact' to permanently save their specific biological data, injuries, goals, or schedule preferences.
4. YOU OWN THEIR TRAINING CALENDAR. You must use 'get_calendar_view' to analyze their week, find optimal 60-90 minute gaps, and use 'manage_calendar_event' to proactively schedule (action="add") "Deep Work(out)" sessions. Ensure category="Health", priority="High", agent_id="HealthCoach", color="#10B981" (emerald).
5. NEVER schedule workouts blindly. Respect their dynamic work shifts. NEVER schedule late at night (e.g., 23:00) and DO NOT default to generic times like 17:00. Adapt to their daily workload shown in the calendar.
6. Keep responses highly structured, intense, and actionable. Your output is displayed in the Commander Dashboard's Health tab.
"""

from langchain_core.messages import SystemMessage

# Compile the ReAct agent loops (without version-dependent kwargs)
agent_runnable = create_react_agent(llm, tools=[memorize_fact, manage_calendar_event, get_calendar_view])

async def health_coach_node(state: AgentState) -> AgentState:
    """The Health Coach specialized agent."""
    messages = state["messages"]
    user_name = state.get("session_user_id", "CEO")
    curr_time = state.get("session_time", "Unknown")
    
    # Read CEO profile securely
    profile_data = {}
    try:
        profile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ceo_profile.yaml')
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Health agent could not load ceo_profile.yaml: {e}")

    work_hours = profile_data.get("preferences", {}).get("working_hours", "Unknown")
    train_constraints = profile_data.get("preferences", {}).get("training_constraints", "Unknown")

    # 1. Dynamically inject the System Persona to bypass any LangGraph kwargs bugs
    dynamic_prompt = HEALTH_COACH_PROMPT + f"\n\n[CONTEXT]\nUser: {user_name}\nTime: {curr_time}\nWorking Hours: {work_hours}\nTraining Constraints: {train_constraints}\n"
    system_message = SystemMessage(content=dynamic_prompt)
    input_payload = [system_message] + messages
    
    # Run the compiled ReAct agent
    result = await agent_runnable.ainvoke({"messages": input_payload})
    
    # Extract ONLY the newly generated messages (ToolCalls, ToolOutputs, AI replies)
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "health",
        "dashboard_data": {
            "steps": 0,
            "sleep": "Awaiting Oura Sync",
            "calories": 0,
            "agent_status": "Idle"
        }
    }
