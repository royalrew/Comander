import os
from langchain_openai import ChatOpenAI
from swarm.state import AgentState
from langgraph.prebuilt import create_react_agent
from swarm.tools import (
    search_web,
    deep_scrape_url,
    memorize_fact
)
from langchain_core.messages import SystemMessage

# We use the Cortex model for deep reasoning during research
llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.3)

RESEARCH_AGENT_PROMPT = """You are The Research Agent (The Executor / Utföraren).
Your mission is to obsessively gather, analyze, and synthesize data from the deep web based on the Commander's or Controller's goals, without hallucinating.

RULES:
1. You act autonomously but safely. Always start by using `search_web` to find relevant URLs.
2. Once you find promising URLs, use `deep_scrape_url` to read their exact Markdown content.
3. NEVER guess or hallucinate facts. If the website does not contain the answer, say so or search again.
4. "The Critic" mindset: Before presenting data, double-check that you actually read it from a scraped source.
5. If the user or Controller gave you a specific abstract goal (e.g., "Find pricing for X"), summarize your findings clearly.
6. You ALWAYS reply in SVENSKA (Swedish). 
7. Use `memorize_fact` to permanently store critical competitive intelligence, pricing, or strategic data you find, so the Controller can use it later.
"""

# Compile the ReAct agent loops
agent_runnable = create_react_agent(
    llm,
    tools=[search_web, deep_scrape_url, memorize_fact],
)

async def research_agent_node(state: AgentState) -> AgentState:
    """The Research Agent (Utföraren)."""
    messages = state["messages"]

    system_message = SystemMessage(content=RESEARCH_AGENT_PROMPT)
    input_payload = [system_message] + messages
    
    # Run the compiled ReAct agent
    result = await agent_runnable.ainvoke({"messages": input_payload})
    
    # Extract ONLY the newly generated messages (ToolCalls, ToolOutputs, AI replies)
    new_messages = result["messages"][len(input_payload):]
    
    return {
        "messages": new_messages,
        "active_dashboard_tab": "tech",
        "dashboard_data": {
            "agent_status": "Idle",
            "last_action": "Web Research Completed"
        }
    }
