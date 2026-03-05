import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from swarm.state import AgentState

llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.5)

from langgraph.prebuilt import create_react_agent
from swarm.tools import (
    recall_memories,
    memorize_fact,
    manage_calendar_event,
    get_calendar_view,
    bulk_add_calendar_events,
)

COMMANDER_PROMPT = """Du är The Commander, en state-of-the-art Enterprise GRC Agent och CTO för Sintari.
Svara kortfattat, mänskligt och professionellt. Denna nod hanterar allmänt prat, frågor som inte rör specifika agenter, eller otydliga inmatningar som 'Va?'.
Om användaren verkar förvirrad, fråga hur du kan hjälpa till. 

MINNESREGLER:
- Du HAR tillgång till verktyget 'memorize_fact'. När användaren berättar fakta om sig själv, sitt företag, sina preferenser eller viktiga mål (t.ex. 'Jag heter...', 'Jag bor...', 'Jag är VD', 'Jag hatar morgonmöten'), ska du ANVÄNDA 'memorize_fact' med en tydlig kategori (t.ex. 'Profile', 'Preference', 'Goal').
- Du HAR tillgång till verktyget 'recall_memories'. Om användaren frågar vad du har sparat om dem eller vad du kommer ihåg (t.ex. 'Vad vet du om mig?', 'Vad har du sparat om mig?'), ska du ALLTID först anropa 'recall_memories' innan du svarar.

KALENDER:
- Du HAR ÄVEN tillgång till kalendern via 'manage_calendar_event' och 'get_calendar_view'. Om användaren ber dig boka in allmänna möten, händelser eller påminnelser som inte är träningsrelaterade (vilket går till Health Coach), boka in dem direkt! Sätt category='General' och agent_id='Commander'.
- KRITISK REGEL: Om användaren ger dig FLER ÄN 2 events/arbetspass att lägga in, MÅSTE du anropa verktyget 'bulk_add_calendar_events' med en JSON-array. Du får INTE säga 'klart' utan att FAKTISKT anropa verktyget. Du MÅSTE se 'SUCCESS' i svaret från verktyget innan du bekräftar för användaren."""

# Compile the ReAct agent without static system prompts (we inject dynamically to bypass version issues)
agent_runnable = create_react_agent(
    llm,
    tools=[
        recall_memories,
        memorize_fact,
        manage_calendar_event,
        get_calendar_view,
        bulk_add_calendar_events,
    ],
)

async def commander_agent_node(state: AgentState) -> AgentState:
    """The default fallback agent for general conversation."""
    messages = state["messages"]
    user_name = state.get("session_user_id", "CEO")
    curr_time = state.get("session_time", "Unknown")
    
    dynamic_prompt = COMMANDER_PROMPT + f"\n\n[CONTEXT]\nUser: {user_name}\nTime: {curr_time}\n"
    system_message = SystemMessage(content=dynamic_prompt)
    
    input_payload = [system_message] + messages
    result = await agent_runnable.ainvoke({"messages": input_payload})
    
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "overview",
        "dashboard_data": {
            "agent_status": "Idle"
        }
    }
